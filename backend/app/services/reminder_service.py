import uuid
from datetime import datetime, timezone, timedelta
from typing import List, Optional
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select, desc, asc, func
from app.models.user import User
from app.models.document import Document
from app.models.reminder import Reminder
from app.schemas.reminder import (
    ActionableDateResponse,
    ActionableDatesListResponse,
    ReminderCreateRequest,
    ReminderUpdateRequest,
    ReminderResponse,
    ReminderSummaryResponse,
    ProcessDueRemindersResponse,
)
from app.services.date_extractor import date_extractor

class ReminderService:
    def scan_document_actionable_dates(
        self,
        db: Session,
        user: User,
        document_id: uuid.UUID
    ) -> ActionableDatesListResponse:
        stmt = select(Document).where(
            Document.id == document_id,
            Document.user_id == user.id
        )
        doc = db.execute(stmt).scalar_one_or_none()
        if not doc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found"
            )

        if doc.status not in ("PROCESSED", "READY"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Document must be processed before scanning for actionable dates"
            )

        candidates = date_extractor.extract_from_document_content(
            extracted_text=doc.extracted_text,
            extracted_metadata=doc.extracted_metadata
        )

        cand_responses = [
            ActionableDateResponse(
                date=c.date,
                type=c.type,
                title=c.title,
                source_text=c.source_text,
                page=c.page,
                section=c.section,
                confidence=c.confidence
            )
            for c in candidates
        ]

        return ActionableDatesListResponse(
            document_id=doc.id,
            document_filename=doc.original_filename,
            candidates_count=len(cand_responses),
            candidates=cand_responses
        )

    def create_reminder(
        self,
        db: Session,
        user: User,
        request: ReminderCreateRequest
    ) -> ReminderResponse:
        doc_filename = None
        if request.document_id:
            doc_stmt = select(Document).where(
                Document.id == request.document_id,
                Document.user_id == user.id
            )
            doc = db.execute(doc_stmt).scalar_one_or_none()
            if not doc:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Linked document not found or does not belong to user"
                )
            doc_filename = doc.original_filename

        due_at = request.due_at
        if due_at.tzinfo is None:
            due_at = due_at.replace(tzinfo=timezone.utc)

        if request.lead_time_days is not None:
            remind_at = due_at - timedelta(days=request.lead_time_days)
        elif request.remind_at is not None:
            remind_at = request.remind_at
            if remind_at.tzinfo is None:
                remind_at = remind_at.replace(tzinfo=timezone.utc)
        else:
            remind_at = due_at

        reminder = Reminder(
            id=uuid.uuid4(),
            user_id=user.id,
            document_id=request.document_id,
            title=request.title.strip(),
            description=request.description.strip() if request.description else None,
            reminder_type=request.reminder_type.upper().strip() if request.reminder_type else "CUSTOM",
            due_at=due_at,
            remind_at=remind_at,
            status="PENDING",
            source_text=request.source_text,
            source_page=request.source_page,
            source_section=request.source_section
        )

        db.add(reminder)
        db.commit()
        db.refresh(reminder)

        return ReminderResponse(
            id=reminder.id,
            user_id=reminder.user_id,
            document_id=reminder.document_id,
            document_filename=doc_filename,
            title=reminder.title,
            description=reminder.description,
            reminder_type=reminder.reminder_type,
            due_at=reminder.due_at,
            remind_at=reminder.remind_at,
            status=reminder.status,
            source_text=reminder.source_text,
            source_page=reminder.source_page,
            source_section=reminder.source_section,
            created_at=reminder.created_at,
            updated_at=reminder.updated_at,
            completed_at=reminder.completed_at
        )

    def list_reminders(
        self,
        db: Session,
        user: User,
        status_filter: Optional[str] = None,
        reminder_type: Optional[str] = None,
        document_id: Optional[uuid.UUID] = None,
        upcoming: Optional[bool] = None,
        overdue: Optional[bool] = None
    ) -> List[ReminderResponse]:
        now = datetime.now(timezone.utc)
        stmt = (
            select(Reminder, Document.original_filename)
            .outerjoin(Document, Reminder.document_id == Document.id)
            .where(Reminder.user_id == user.id)
        )

        if status_filter:
            stmt = stmt.where(Reminder.status == status_filter.upper())

        if reminder_type and reminder_type != "ALL":
            stmt = stmt.where(Reminder.reminder_type == reminder_type.upper())

        if document_id:
            stmt = stmt.where(Reminder.document_id == document_id)

        if upcoming is True:
            stmt = stmt.where(
                Reminder.due_at >= now,
                Reminder.status.in_(["PENDING", "DUE"])
            )

        if overdue is True:
            stmt = stmt.where(
                Reminder.due_at < now,
                Reminder.status.in_(["PENDING", "DUE"])
            )

        stmt = stmt.order_by(asc(Reminder.due_at))
        results = db.execute(stmt).all()

        reminders = []
        for rem, doc_name in results:
            reminders.append(
                ReminderResponse(
                    id=rem.id,
                    user_id=rem.user_id,
                    document_id=rem.document_id,
                    document_filename=doc_name,
                    title=rem.title,
                    description=rem.description,
                    reminder_type=rem.reminder_type,
                    due_at=rem.due_at,
                    remind_at=rem.remind_at,
                    status=rem.status,
                    source_text=rem.source_text,
                    source_page=rem.source_page,
                    source_section=rem.source_section,
                    created_at=rem.created_at,
                    updated_at=rem.updated_at,
                    completed_at=rem.completed_at
                )
            )
        return reminders

    def get_reminder_by_id(
        self,
        db: Session,
        user: User,
        reminder_id: uuid.UUID
    ) -> ReminderResponse:
        stmt = (
            select(Reminder, Document.original_filename)
            .outerjoin(Document, Reminder.document_id == Document.id)
            .where(
                Reminder.id == reminder_id,
                Reminder.user_id == user.id
            )
        )
        res = db.execute(stmt).first()
        if not res:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Reminder not found"
            )

        rem, doc_name = res
        return ReminderResponse(
            id=rem.id,
            user_id=rem.user_id,
            document_id=rem.document_id,
            document_filename=doc_name,
            title=rem.title,
            description=rem.description,
            reminder_type=rem.reminder_type,
            due_at=rem.due_at,
            remind_at=rem.remind_at,
            status=rem.status,
            source_text=rem.source_text,
            source_page=rem.source_page,
            source_section=rem.source_section,
            created_at=rem.created_at,
            updated_at=rem.updated_at,
            completed_at=rem.completed_at
        )

    def update_reminder(
        self,
        db: Session,
        user: User,
        reminder_id: uuid.UUID,
        request: ReminderUpdateRequest
    ) -> ReminderResponse:
        stmt = select(Reminder).where(
            Reminder.id == reminder_id,
            Reminder.user_id == user.id
        )
        rem = db.execute(stmt).scalar_one_or_none()
        if not rem:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Reminder not found"
            )

        if request.title is not None:
            rem.title = request.title.strip()
        if request.description is not None:
            rem.description = request.description.strip() if request.description else None
        if request.reminder_type is not None:
            rem.reminder_type = request.reminder_type.upper().strip()
        if request.due_at is not None:
            due_at = request.due_at
            if due_at.tzinfo is None:
                due_at = due_at.replace(tzinfo=timezone.utc)
            rem.due_at = due_at
        if request.remind_at is not None:
            remind_at = request.remind_at
            if remind_at.tzinfo is None:
                remind_at = remind_at.replace(tzinfo=timezone.utc)
            rem.remind_at = remind_at
        if request.status is not None:
            st = request.status.upper().strip()
            rem.status = st
            if st == "COMPLETED" and not rem.completed_at:
                rem.completed_at = datetime.now(timezone.utc)
            elif st != "COMPLETED":
                rem.completed_at = None

        rem.updated_at = func.now()
        db.commit()
        db.refresh(rem)

        doc_name = None
        if rem.document_id:
            doc = db.execute(select(Document.original_filename).where(Document.id == rem.document_id)).scalar_one_or_none()
            doc_name = doc

        return ReminderResponse(
            id=rem.id,
            user_id=rem.user_id,
            document_id=rem.document_id,
            document_filename=doc_name,
            title=rem.title,
            description=rem.description,
            reminder_type=rem.reminder_type,
            due_at=rem.due_at,
            remind_at=rem.remind_at,
            status=rem.status,
            source_text=rem.source_text,
            source_page=rem.source_page,
            source_section=rem.source_section,
            created_at=rem.created_at,
            updated_at=rem.updated_at,
            completed_at=rem.completed_at
        )

    def complete_reminder(
        self,
        db: Session,
        user: User,
        reminder_id: uuid.UUID
    ) -> ReminderResponse:
        stmt = select(Reminder).where(
            Reminder.id == reminder_id,
            Reminder.user_id == user.id
        )
        rem = db.execute(stmt).scalar_one_or_none()
        if not rem:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Reminder not found"
            )

        rem.status = "COMPLETED"
        rem.completed_at = datetime.now(timezone.utc)
        rem.updated_at = func.now()
        db.commit()
        db.refresh(rem)

        doc_name = None
        if rem.document_id:
            doc = db.execute(select(Document.original_filename).where(Document.id == rem.document_id)).scalar_one_or_none()
            doc_name = doc

        return ReminderResponse(
            id=rem.id,
            user_id=rem.user_id,
            document_id=rem.document_id,
            document_filename=doc_name,
            title=rem.title,
            description=rem.description,
            reminder_type=rem.reminder_type,
            due_at=rem.due_at,
            remind_at=rem.remind_at,
            status=rem.status,
            source_text=rem.source_text,
            source_page=rem.source_page,
            source_section=rem.source_section,
            created_at=rem.created_at,
            updated_at=rem.updated_at,
            completed_at=rem.completed_at
        )

    def delete_reminder(
        self,
        db: Session,
        user: User,
        reminder_id: uuid.UUID
    ) -> None:
        stmt = select(Reminder).where(
            Reminder.id == reminder_id,
            Reminder.user_id == user.id
        )
        rem = db.execute(stmt).scalar_one_or_none()
        if not rem:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Reminder not found"
            )

        db.delete(rem)
        db.commit()

    def get_reminders_summary(
        self,
        db: Session,
        user: User
    ) -> ReminderSummaryResponse:
        now = datetime.now(timezone.utc)
        user_rems_stmt = (
            select(Reminder, Document.original_filename)
            .outerjoin(Document, Reminder.document_id == Document.id)
            .where(Reminder.user_id == user.id)
            .order_by(asc(Reminder.due_at))
        )
        all_rems = db.execute(user_rems_stmt).all()

        total_pending = 0
        due_count = 0
        overdue_count = 0
        upcoming_count = 0
        completed_count = 0
        expiry_count = 0
        warranty_count = 0
        renewal_count = 0
        next_rem_obj = None

        for rem, doc_name in all_rems:
            st = rem.status
            rt = rem.reminder_type
            due = rem.due_at
            if due is not None and due.tzinfo is None:
                due = due.replace(tzinfo=timezone.utc)

            if st == "PENDING":
                total_pending += 1
            if st == "DUE":
                due_count += 1
            if st == "COMPLETED":
                completed_count += 1

            if st in ("PENDING", "DUE") and due is not None:
                if due < now:
                    overdue_count += 1
                else:
                    upcoming_count += 1

                if rt == "EXPIRY":
                    expiry_count += 1
                elif rt == "WARRANTY":
                    warranty_count += 1
                elif rt == "RENEWAL":
                    renewal_count += 1

                if next_rem_obj is None and due >= now:
                    next_rem_obj = ReminderResponse(
                        id=rem.id,
                        user_id=rem.user_id,
                        document_id=rem.document_id,
                        document_filename=doc_name,
                        title=rem.title,
                        description=rem.description,
                        reminder_type=rem.reminder_type,
                        due_at=rem.due_at,
                        remind_at=rem.remind_at,
                        status=rem.status,
                        source_text=rem.source_text,
                        source_page=rem.source_page,
                        source_section=rem.source_section,
                        created_at=rem.created_at,
                        updated_at=rem.updated_at,
                        completed_at=rem.completed_at
                    )

        if next_rem_obj is None and all_rems:
            for rem, doc_name in all_rems:
                if rem.status in ("PENDING", "DUE"):
                    next_rem_obj = ReminderResponse(
                        id=rem.id,
                        user_id=rem.user_id,
                        document_id=rem.document_id,
                        document_filename=doc_name,
                        title=rem.title,
                        description=rem.description,
                        reminder_type=rem.reminder_type,
                        due_at=rem.due_at,
                        remind_at=rem.remind_at,
                        status=rem.status,
                        source_text=rem.source_text,
                        source_page=rem.source_page,
                        source_section=rem.source_section,
                        created_at=rem.created_at,
                        updated_at=rem.updated_at,
                        completed_at=rem.completed_at
                    )
                    break

        return ReminderSummaryResponse(
            total_pending=total_pending,
            due_count=due_count,
            overdue_count=overdue_count,
            upcoming_count=upcoming_count,
            completed_count=completed_count,
            expiry_count=expiry_count,
            warranty_count=warranty_count,
            renewal_count=renewal_count,
            next_reminder=next_rem_obj
        )

    def process_due_reminders(
        self,
        db: Session,
        user: User
    ) -> ProcessDueRemindersResponse:
        now = datetime.now(timezone.utc)
        stmt = select(Reminder).where(
            Reminder.user_id == user.id,
            Reminder.status == "PENDING",
            Reminder.remind_at <= now
        )
        due_rems = list(db.execute(stmt).scalars().all())

        for rem in due_rems:
            rem.status = "DUE"
            rem.updated_at = func.now()

        if due_rems:
            db.commit()

        return ProcessDueRemindersResponse(
            processed_count=len(due_rems),
            transitioned_due_count=len(due_rems),
            evaluated_at=now
        )

reminder_service = ReminderService()

import uuid
from typing import Optional, List
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.user import User
from app.api.deps import get_current_user
from app.schemas.reminder import (
    ReminderCreateRequest,
    ReminderUpdateRequest,
    ReminderResponse,
    ReminderSummaryResponse,
    ProcessDueRemindersResponse,
)
from app.services.reminder_service import reminder_service

router = APIRouter()

@router.post("", response_model=ReminderResponse, status_code=status.HTTP_201_CREATED)
def create_reminder(
    request: ReminderCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ReminderResponse:
    return reminder_service.create_reminder(db=db, user=current_user, request=request)

@router.get("/summary", response_model=ReminderSummaryResponse)
def get_reminders_summary(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ReminderSummaryResponse:
    return reminder_service.get_reminders_summary(db=db, user=current_user)

@router.post("/process-due", response_model=ProcessDueRemindersResponse)
def process_due_reminders(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ProcessDueRemindersResponse:
    return reminder_service.process_due_reminders(db=db, user=current_user)

@router.get("", response_model=List[ReminderResponse])
def list_reminders(
    status: Optional[str] = Query(None),
    reminder_type: Optional[str] = Query(None),
    document_id: Optional[uuid.UUID] = Query(None),
    upcoming: Optional[bool] = Query(None),
    overdue: Optional[bool] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> List[ReminderResponse]:
    return reminder_service.list_reminders(
        db=db,
        user=current_user,
        status_filter=status,
        reminder_type=reminder_type,
        document_id=document_id,
        upcoming=upcoming,
        overdue=overdue,
    )

@router.get("/{reminder_id}", response_model=ReminderResponse)
def get_reminder(
    reminder_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ReminderResponse:
    return reminder_service.get_reminder_by_id(db=db, user=current_user, reminder_id=reminder_id)

@router.patch("/{reminder_id}", response_model=ReminderResponse)
def update_reminder(
    reminder_id: uuid.UUID,
    request: ReminderUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ReminderResponse:
    return reminder_service.update_reminder(
        db=db,
        user=current_user,
        reminder_id=reminder_id,
        request=request,
    )

@router.post("/{reminder_id}/complete", response_model=ReminderResponse)
def complete_reminder(
    reminder_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ReminderResponse:
    return reminder_service.complete_reminder(db=db, user=current_user, reminder_id=reminder_id)

@router.delete("/{reminder_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_reminder(
    reminder_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    reminder_service.delete_reminder(db=db, user=current_user, reminder_id=reminder_id)

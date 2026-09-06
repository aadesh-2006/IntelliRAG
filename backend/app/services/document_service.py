import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import select, desc
from fastapi import UploadFile, HTTPException, status
from app.models.document import Document
from app.models.user import User
from app.services.storage_service import storage_service
from app.services.document_processing.pipeline import document_pipeline
from app.services.notification_service import notification_service
from app.config import settings

def validate_file_extension(filename: str) -> None:
    ext = filename.split(".")[-1].lower() if "." in filename else ""
    if ext not in settings.ALLOWED_EXTENSIONS:
        allowed = ", ".join(settings.ALLOWED_EXTENSIONS)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file extension '{ext}'. Allowed extensions are: {allowed}"
        )

def create_document(
    db: Session,
    user: User,
    file: UploadFile,
    document_type: str = "GENERAL_DOCUMENT"
) -> Document:
    original_filename = file.filename or "untitled"
    validate_file_extension(original_filename)

    file_type = file.content_type or "application/octet-stream"
    unique_filename, file_path, file_size = storage_service.save_file(file)

    document = Document(
        user_id=user.id,
        filename=unique_filename,
        original_filename=original_filename,
        file_type=file_type,
        file_path=file_path,
        file_size=file_size,
        status="UPLOADED",
        document_type=document_type,
    )
    db.add(document)
    db.commit()
    db.refresh(document)

    try:
        notification_service.create_notification(
            db=db,
            user_id=user.id,
            notification_type="DOCUMENT_UPLOADED",
            title="Document Uploaded",
            message=f"Document uploaded: {original_filename}",
            severity="INFO",
            related_document_id=document.id,
            event_key=f"doc_uploaded_{document.id}"
        )
    except Exception:
        pass

    return document

def list_documents(
    db: Session,
    user_id: uuid.UUID,
    skip: int = 0,
    limit: int = 100,
    document_type: Optional[str] = None
) -> List[Document]:
    stmt = select(Document).where(Document.user_id == user_id)
    if document_type:
        stmt = stmt.where(Document.document_type == document_type)
    stmt = stmt.order_by(desc(Document.created_at)).offset(skip).limit(limit)
    return list(db.execute(stmt).scalars().all())

def get_document_by_id(
    db: Session,
    document_id: uuid.UUID,
    user_id: uuid.UUID
) -> Optional[Document]:
    stmt = select(Document).where(Document.id == document_id, Document.user_id == user_id)
    return db.execute(stmt).scalar_one_or_none()

def delete_document(
    db: Session,
    document_id: uuid.UUID,
    user_id: uuid.UUID
) -> bool:
    document = get_document_by_id(db, document_id, user_id)
    if not document:
        return False
    storage_service.delete_file(document.file_path)
    db.delete(document)
    db.commit()
    return True

def process_document_by_id(
    db: Session,
    document_id: uuid.UUID,
    user_id: uuid.UUID
) -> Document:
    document = get_document_by_id(db, document_id, user_id)
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )

    document.status = "PROCESSING"
    document.processing_error = None
    db.commit()
    db.refresh(document)

    try:
        file_path = Path(document.file_path)
        extracted = document_pipeline.process_document(
            file_path=file_path,
            document_id=str(document.id),
            document_type=document.document_type
        )
        document.status = "PROCESSED"
        document.processed_at = datetime.now(timezone.utc)
        document.processing_error = None
        document.extracted_text = extracted.full_text
        document.extracted_metadata = extracted.model_dump(mode="json")
        db.commit()
        db.refresh(document)

        try:
            notification_service.create_notification(
                db=db,
                user_id=user_id,
                notification_type="DOCUMENT_PROCESSED",
                title="Document Processed",
                message=f"Document processed successfully: {document.original_filename}",
                severity="SUCCESS",
                related_document_id=document.id,
                event_key=f"doc_processed_{document.id}"
            )
        except Exception:
            pass

        return document
    except Exception as exc:
        document.status = "FAILED"
        document.processed_at = datetime.now(timezone.utc)
        document.processing_error = str(exc)
        db.commit()
        db.refresh(document)

        try:
            notification_service.create_notification(
                db=db,
                user_id=user_id,
                notification_type="DOCUMENT_FAILED",
                title="Document Processing Failed",
                message=f"Document processing failed: {document.original_filename}",
                severity="ERROR",
                related_document_id=document.id,
                event_key=f"doc_failed_{document.id}"
            )
        except Exception:
            pass

        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Document processing failed: {str(exc)}"
        )
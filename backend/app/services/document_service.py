import uuid
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import select, desc
from fastapi import UploadFile, HTTPException, status
from app.models.document import Document
from app.models.user import User
from app.services.storage_service import storage_service
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
import uuid
from typing import Optional
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, status, Query
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.user import User
from app.api.deps import get_current_user
from app.schemas.document import DocumentResponse, DocumentListResponse
from app.services.document_service import (
    create_document,
    list_documents,
    get_document_by_id,
    delete_document,
)
from app.services.storage_service import storage_service

router = APIRouter()

@router.post("/upload", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
def upload_document(
    file: UploadFile = File(...),
    document_type: str = Form("GENERAL_DOCUMENT"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> DocumentResponse:
    document = create_document(
        db=db,
        user=current_user,
        file=file,
        document_type=document_type
    )
    return DocumentResponse.model_validate(document)

@router.get("", response_model=DocumentListResponse)
def get_documents(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    document_type: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> DocumentListResponse:
    docs = list_documents(
        db=db,
        user_id=current_user.id,
        skip=skip,
        limit=limit,
        document_type=document_type
    )
    return DocumentListResponse(
        items=[DocumentResponse.model_validate(d) for d in docs],
        total=len(docs)
    )

@router.get("/{document_id}", response_model=DocumentResponse)
def get_document(
    document_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> DocumentResponse:
    document = get_document_by_id(db, document_id, current_user.id)
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    return DocumentResponse.model_validate(document)

@router.get("/{document_id}/download")
def download_document(
    document_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> FileResponse:
    document = get_document_by_id(db, document_id, current_user.id)
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    file_path = storage_service.get_file_path(document.file_path)
    return FileResponse(
        path=str(file_path),
        filename=document.original_filename,
        media_type=document.file_type
    )

@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_document(
    document_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    success = delete_document(db, document_id, current_user.id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
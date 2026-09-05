import uuid
from typing import List
from sqlalchemy.orm import Session
from sqlalchemy import select, delete, asc
from fastapi import HTTPException, status
from app.models.document import Document
from app.models.document_chunk import DocumentChunk
from app.services.document_service import get_document_by_id
from app.services.chunking_service import chunking_service
from app.services.embedding_service import embedding_service

def generate_and_store_chunks(
    db: Session,
    document_id: uuid.UUID,
    user_id: uuid.UUID
) -> List[DocumentChunk]:
    document = get_document_by_id(db, document_id, user_id)
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )

    if document.status not in ["PROCESSED", "READY", "INDEXED", "FAILED"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot generate embeddings for document in '{document.status}' state. Document must be in PROCESSED state."
        )

    document.status = "EMBEDDING"
    document.processing_error = None
    db.commit()
    db.refresh(document)

    try:
        db.execute(delete(DocumentChunk).where(DocumentChunk.document_id == document.id))
        db.commit()

        generated_chunks = chunking_service.chunk_document(document)

        if not generated_chunks:
            document.status = "READY"
            db.commit()
            db.refresh(document)
            return []

        texts = [c.content for c in generated_chunks]
        embeddings = embedding_service.embed_batch(texts)

        chunk_records: List[DocumentChunk] = []
        for i, c in enumerate(generated_chunks):
            chunk_uuid = uuid.UUID(c.chunk_id) if isinstance(c.chunk_id, str) else c.chunk_id
            rec = DocumentChunk(
                id=chunk_uuid,
                document_id=document.id,
                chunk_index=c.chunk_index,
                content=c.content,
                chunk_metadata=c.metadata,
                embedding=embeddings[i]
            )
            chunk_records.append(rec)

        db.add_all(chunk_records)
        document.status = "READY"
        db.commit()
        db.refresh(document)
        return chunk_records

    except Exception as exc:
        document.status = "FAILED"
        document.processing_error = f"Embedding generation failed: {str(exc)}"
        db.commit()
        db.refresh(document)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate chunks and embeddings: {str(exc)}"
        )

def list_document_chunks(
    db: Session,
    document_id: uuid.UUID,
    user_id: uuid.UUID
) -> List[DocumentChunk]:
    document = get_document_by_id(db, document_id, user_id)
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )

    stmt = select(DocumentChunk).where(
        DocumentChunk.document_id == document.id
    ).order_by(asc(DocumentChunk.chunk_index))
    
    return list(db.execute(stmt).scalars().all())

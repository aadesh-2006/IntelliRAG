import uuid
from typing import Dict
from sqlalchemy.orm import Session
from sqlalchemy import select, func, desc
from app.models.document import Document
from app.models.document_chunk import DocumentChunk
from app.schemas.dashboard import DashboardStatsResponse
from app.schemas.document import DocumentResponse

class DashboardService:
    def get_user_stats(self, db: Session, user_id: uuid.UUID) -> DashboardStatsResponse:
        docs_stmt = (
            select(Document)
            .where(Document.user_id == user_id)
            .order_by(desc(Document.created_at))
        )
        user_docs = list(db.execute(docs_stmt).scalars().all())

        total_docs = len(user_docs)
        total_storage = sum(d.file_size for d in user_docs)

        status_counts: Dict[str, int] = {
            "UPLOADED": 0,
            "PROCESSING": 0,
            "PROCESSED": 0,
            "EMBEDDING": 0,
            "READY": 0,
            "FAILED": 0,
        }
        type_counts: Dict[str, int] = {}
        file_type_counts: Dict[str, int] = {}

        for doc in user_docs:
            st = doc.status.upper() if doc.status else "UPLOADED"
            status_counts[st] = status_counts.get(st, 0) + 1

            dt = doc.document_type or "GENERAL_DOCUMENT"
            type_counts[dt] = type_counts.get(dt, 0) + 1

            ft = doc.file_type or "unknown"
            file_type_counts[ft] = file_type_counts.get(ft, 0) + 1

        chunks_count_stmt = (
            select(func.count(DocumentChunk.id))
            .join(Document, DocumentChunk.document_id == Document.id)
            .where(Document.user_id == user_id)
        )
        total_chunks = db.execute(chunks_count_stmt).scalar() or 0

        recent_docs = [DocumentResponse.model_validate(d) for d in user_docs[:5]]

        return DashboardStatsResponse(
            total_documents=total_docs,
            processed_documents=status_counts.get("PROCESSED", 0),
            processing_documents=status_counts.get("PROCESSING", 0),
            failed_documents=status_counts.get("FAILED", 0),
            ready_documents=status_counts.get("READY", 0),
            uploaded_documents=status_counts.get("UPLOADED", 0),
            embedding_documents=status_counts.get("EMBEDDING", 0),
            total_chunks=total_chunks,
            total_storage_bytes=total_storage,
            documents_by_status=status_counts,
            documents_by_type=type_counts,
            documents_by_file_type=file_type_counts,
            recent_documents=recent_docs
        )

dashboard_service = DashboardService()

from typing import Dict, List
from pydantic import BaseModel
from app.schemas.document import DocumentResponse

class DashboardStatsResponse(BaseModel):
    total_documents: int
    processed_documents: int
    processing_documents: int
    failed_documents: int
    ready_documents: int
    uploaded_documents: int
    embedding_documents: int
    total_chunks: int
    total_storage_bytes: int
    documents_by_status: Dict[str, int]
    documents_by_type: Dict[str, int]
    documents_by_file_type: Dict[str, int]
    recent_documents: List[DocumentResponse]

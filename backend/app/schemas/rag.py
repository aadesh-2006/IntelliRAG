import uuid
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class Citation(BaseModel):
    citation_id: int
    document_id: uuid.UUID
    document_filename: str
    page_number: Optional[int] = None
    section: Optional[str] = None
    chunk_id: uuid.UUID
    chunk_index: int
    similarity_score: float
    content_snippet: str

    model_config = {
        "from_attributes": True,
        "populate_by_name": True
    }

class RAGQueryRequest(BaseModel):
    query: str = Field(..., min_length=1)
    top_k: int = Field(default=5, ge=1, le=50)
    similarity_threshold: Optional[float] = Field(default=0.25, ge=0.0, le=1.0)
    document_ids: Optional[List[uuid.UUID]] = None
    document_type: Optional[str] = None

class RAGQueryResponse(BaseModel):
    query: str
    answer: str
    citations: List[Citation]
    retrieved_chunks_count: int
    has_sufficient_context: bool
    model_info: Dict[str, Any]

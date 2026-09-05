import uuid
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class SearchQueryRequest(BaseModel):
    query: str = Field(..., min_length=1)
    top_k: int = Field(default=5, ge=1, le=50)
    similarity_threshold: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    document_ids: Optional[List[uuid.UUID]] = Field(default=None)
    document_type: Optional[str] = Field(default=None)

class RetrievedChunk(BaseModel):
    id: uuid.UUID
    document_id: uuid.UUID
    document_filename: str
    document_type: str
    chunk_index: int
    content: str
    similarity_score: float
    distance: float
    metadata: Optional[Dict[str, Any]] = None

    model_config = {
        "from_attributes": True,
        "populate_by_name": True
    }

class SearchQueryResponse(BaseModel):
    query: str
    total_results: int
    top_k: int
    similarity_threshold: Optional[float] = None
    results: List[RetrievedChunk]

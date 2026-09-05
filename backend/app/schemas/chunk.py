import uuid
from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class ChunkResponse(BaseModel):
    id: uuid.UUID
    document_id: uuid.UUID
    chunk_index: int
    content: str
    metadata: Optional[Dict[str, Any]] = Field(default=None, alias="chunk_metadata")
    created_at: datetime

    model_config = {
        "from_attributes": True,
        "populate_by_name": True
    }

class ChunkListResponse(BaseModel):
    items: List[ChunkResponse]
    total: int
    document_id: uuid.UUID
    status: str
    embedding_dimension: int

class EmbedTriggerResponse(BaseModel):
    document_id: uuid.UUID
    status: str
    total_chunks: int
    message: str

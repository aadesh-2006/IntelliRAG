import uuid
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel

class DocumentResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    filename: str
    original_filename: str
    file_type: str
    file_size: int
    status: str
    document_type: str
    processed_at: Optional[datetime] = None
    processing_error: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True
    }

class DocumentListResponse(BaseModel):
    items: List[DocumentResponse]
    total: int
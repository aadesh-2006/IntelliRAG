import uuid
from datetime import datetime
from typing import List
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
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True
    }

class DocumentListResponse(BaseModel):
    items: List[DocumentResponse]
    total: int
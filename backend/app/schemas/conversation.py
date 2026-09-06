import uuid
from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from app.schemas.rag import Citation

class ConversationCreateRequest(BaseModel):
    title: Optional[str] = Field(default=None, max_length=255)

class ConversationUpdateRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)

class ConversationMessageResponse(BaseModel):
    id: uuid.UUID
    conversation_id: uuid.UUID
    role: str
    content: str
    citations: Optional[List[Citation]] = None
    grounding_metadata: Optional[Dict[str, Any]] = None
    is_sufficient_context: bool = True
    created_at: datetime

    model_config = {
        "from_attributes": True
    }

class ConversationResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    title: str
    created_at: datetime
    updated_at: datetime
    message_count: int = 0

    model_config = {
        "from_attributes": True
    }

class ConversationDetailResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    title: str
    created_at: datetime
    updated_at: datetime
    messages: List[ConversationMessageResponse] = []

    model_config = {
        "from_attributes": True
    }

class SendMessageRequest(BaseModel):
    content: str = Field(..., min_length=1)
    document_ids: Optional[List[uuid.UUID]] = None
    document_type: Optional[str] = None
    top_k: int = Field(default=5, ge=1, le=50)
    similarity_threshold: Optional[float] = Field(default=0.25, ge=0.0, le=1.0)

class SendMessageResponse(BaseModel):
    user_message: ConversationMessageResponse
    assistant_message: ConversationMessageResponse

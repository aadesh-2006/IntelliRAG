import uuid
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field

class ActionableDateResponse(BaseModel):
    date: datetime
    type: str
    title: str
    source_text: str
    page: Optional[int] = None
    section: Optional[str] = None
    confidence: float

    model_config = {
        "from_attributes": True
    }

class ActionableDatesListResponse(BaseModel):
    document_id: uuid.UUID
    document_filename: str
    candidates_count: int
    candidates: List[ActionableDateResponse]

class ReminderCreateRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    reminder_type: str = Field(default="CUSTOM")
    due_at: datetime
    remind_at: Optional[datetime] = None
    lead_time_days: Optional[int] = Field(default=None, ge=0, le=365)
    document_id: Optional[uuid.UUID] = None
    source_text: Optional[str] = None
    source_page: Optional[int] = None
    source_section: Optional[str] = None

class ReminderUpdateRequest(BaseModel):
    title: Optional[str] = Field(default=None, min_length=1, max_length=255)
    description: Optional[str] = None
    reminder_type: Optional[str] = None
    due_at: Optional[datetime] = None
    remind_at: Optional[datetime] = None
    status: Optional[str] = None

class ReminderResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    document_id: Optional[uuid.UUID] = None
    document_filename: Optional[str] = None
    title: str
    description: Optional[str] = None
    reminder_type: str
    due_at: datetime
    remind_at: datetime
    status: str
    source_text: Optional[str] = None
    source_page: Optional[int] = None
    source_section: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime] = None

    model_config = {
        "from_attributes": True
    }

class ReminderSummaryResponse(BaseModel):
    total_pending: int
    due_count: int
    overdue_count: int
    upcoming_count: int
    completed_count: int
    expiry_count: int
    warranty_count: int
    renewal_count: int
    next_reminder: Optional[ReminderResponse] = None

class ProcessDueRemindersResponse(BaseModel):
    processed_count: int
    transitioned_due_count: int
    evaluated_at: datetime

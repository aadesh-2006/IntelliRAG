import uuid
from datetime import datetime
from typing import List, Optional, Any, Dict
from pydantic import BaseModel, Field

class NotificationResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    notification_type: str
    title: str
    message: str
    channel: str
    status: str
    severity: str
    related_document_id: Optional[uuid.UUID] = None
    related_reminder_id: Optional[uuid.UUID] = None
    related_conversation_id: Optional[uuid.UUID] = None
    payload_metadata: Optional[Dict[str, Any]] = None
    retry_count: int
    created_at: datetime
    sent_at: Optional[datetime] = None
    read_at: Optional[datetime] = None
    failed_at: Optional[datetime] = None
    failure_reason: Optional[str] = None

    model_config = {
        "from_attributes": True
    }

class NotificationListResponse(BaseModel):
    items: List[NotificationResponse]
    total: int
    unread_count: int

class UnreadCountResponse(BaseModel):
    unread_count: int

class NotificationPreferenceResponse(BaseModel):
    in_app_enabled: bool
    email_enabled: bool
    webhook_enabled: bool
    document_event_notifications: bool
    reminder_notifications: bool
    query_alert_notifications: bool
    email_address: Optional[str] = None
    webhook_url: Optional[str] = None
    has_webhook_secret: bool
    updated_at: datetime

    model_config = {
        "from_attributes": True
    }

class NotificationPreferenceUpdateRequest(BaseModel):
    in_app_enabled: Optional[bool] = None
    email_enabled: Optional[bool] = None
    webhook_enabled: Optional[bool] = None
    document_event_notifications: Optional[bool] = None
    reminder_notifications: Optional[bool] = None
    query_alert_notifications: Optional[bool] = None
    email_address: Optional[str] = Field(default=None, max_length=255)
    webhook_url: Optional[str] = Field(default=None, max_length=512)
    webhook_secret: Optional[str] = Field(default=None, max_length=255)

class NotificationProcessResponse(BaseModel):
    processed_count: int
    delivered_count: int
    failed_count: int
    evaluated_at: datetime

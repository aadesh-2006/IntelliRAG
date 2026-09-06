import uuid
from datetime import datetime
from typing import Optional, Any, Dict, TYPE_CHECKING
from sqlalchemy import String, DateTime, ForeignKey, Text, Integer, Boolean, JSON, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.document import Document
    from app.models.reminder import Reminder
    from app.models.conversation import Conversation

class Notification(Base):
    __tablename__ = "notifications"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    notification_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True
    )
    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )
    message: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )
    channel: Mapped[str] = mapped_column(
        String(50),
        default="IN_APP",
        nullable=False,
        index=True
    )
    status: Mapped[str] = mapped_column(
        String(50),
        default="PENDING",
        nullable=False,
        index=True
    )
    severity: Mapped[str] = mapped_column(
        String(50),
        default="INFO",
        nullable=False
    )
    related_document_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("documents.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )
    related_reminder_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("reminders.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )
    related_conversation_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("conversations.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )
    event_key: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
        index=True
    )
    payload_metadata: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSON,
        nullable=True
    )
    retry_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        index=True
    )
    sent_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )
    read_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        index=True
    )
    failed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )
    failure_reason: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True
    )

    user: Mapped["User"] = relationship(
        "User",
        back_populates="notifications"
    )
    document: Mapped[Optional["Document"]] = relationship(
        "Document"
    )
    reminder: Mapped[Optional["Reminder"]] = relationship(
        "Reminder"
    )
    conversation: Mapped[Optional["Conversation"]] = relationship(
        "Conversation"
    )

class NotificationPreference(Base):
    __tablename__ = "notification_preferences"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True
    )
    in_app_enabled: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False
    )
    email_enabled: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False
    )
    webhook_enabled: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False
    )
    document_event_notifications: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False
    )
    reminder_notifications: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False
    )
    query_alert_notifications: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False
    )
    email_address: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True
    )
    webhook_url: Mapped[Optional[str]] = mapped_column(
        String(512),
        nullable=True
    )
    webhook_secret: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )

    user: Mapped["User"] = relationship(
        "User",
        back_populates="notification_preference"
    )

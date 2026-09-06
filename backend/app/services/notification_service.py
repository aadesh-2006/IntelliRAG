import uuid
from datetime import datetime, timezone
from typing import List, Optional, Any, Dict
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select, desc, func, and_
from app.config import settings
from app.models.user import User
from app.models.notification import Notification, NotificationPreference
from app.schemas.notification import (
    NotificationResponse,
    NotificationListResponse,
    NotificationPreferenceResponse,
    NotificationPreferenceUpdateRequest,
    NotificationProcessResponse,
)
from app.services.notifications.in_app_channel import InAppNotificationChannel
from app.services.notifications.email_channel import EmailNotificationChannel
from app.services.notifications.webhook_channel import WebhookNotificationChannel

class NotificationService:
    def __init__(self):
        self.in_app_channel = InAppNotificationChannel()
        self.email_channel = EmailNotificationChannel()
        self.webhook_channel = WebhookNotificationChannel()

    def get_or_create_preferences(
        self,
        db: Session,
        user_id: uuid.UUID
    ) -> NotificationPreference:
        stmt = select(NotificationPreference).where(NotificationPreference.user_id == user_id)
        pref = db.execute(stmt).scalar_one_or_none()
        if not pref:
            pref = NotificationPreference(
                id=uuid.uuid4(),
                user_id=user_id,
                in_app_enabled=True,
                email_enabled=False,
                webhook_enabled=False,
                document_event_notifications=True,
                reminder_notifications=True,
                query_alert_notifications=True
            )
            db.add(pref)
            db.commit()
            db.refresh(pref)
        return pref

    def get_preferences_response(
        self,
        db: Session,
        user: User
    ) -> NotificationPreferenceResponse:
        pref = self.get_or_create_preferences(db, user.id)
        return NotificationPreferenceResponse(
            in_app_enabled=pref.in_app_enabled,
            email_enabled=pref.email_enabled,
            webhook_enabled=pref.webhook_enabled,
            document_event_notifications=pref.document_event_notifications,
            reminder_notifications=pref.reminder_notifications,
            query_alert_notifications=pref.query_alert_notifications,
            email_address=pref.email_address,
            webhook_url=pref.webhook_url,
            has_webhook_secret=bool(pref.webhook_secret),
            updated_at=pref.updated_at
        )

    def update_preferences(
        self,
        db: Session,
        user: User,
        request: NotificationPreferenceUpdateRequest
    ) -> NotificationPreferenceResponse:
        pref = self.get_or_create_preferences(db, user.id)

        if request.in_app_enabled is not None:
            pref.in_app_enabled = request.in_app_enabled
        if request.email_enabled is not None:
            pref.email_enabled = request.email_enabled
        if request.webhook_enabled is not None:
            pref.webhook_enabled = request.webhook_enabled
        if request.document_event_notifications is not None:
            pref.document_event_notifications = request.document_event_notifications
        if request.reminder_notifications is not None:
            pref.reminder_notifications = request.reminder_notifications
        if request.query_alert_notifications is not None:
            pref.query_alert_notifications = request.query_alert_notifications
        if request.email_address is not None:
            pref.email_address = request.email_address.strip() if request.email_address else None
        if request.webhook_url is not None:
            pref.webhook_url = request.webhook_url.strip() if request.webhook_url else None
        if request.webhook_secret is not None:
            pref.webhook_secret = request.webhook_secret.strip() if request.webhook_secret else None

        pref.updated_at = func.now()
        db.commit()
        db.refresh(pref)

        return NotificationPreferenceResponse(
            in_app_enabled=pref.in_app_enabled,
            email_enabled=pref.email_enabled,
            webhook_enabled=pref.webhook_enabled,
            document_event_notifications=pref.document_event_notifications,
            reminder_notifications=pref.reminder_notifications,
            query_alert_notifications=pref.query_alert_notifications,
            email_address=pref.email_address,
            webhook_url=pref.webhook_url,
            has_webhook_secret=bool(pref.webhook_secret),
            updated_at=pref.updated_at
        )

    def create_notification(
        self,
        db: Session,
        user_id: uuid.UUID,
        notification_type: str,
        title: str,
        message: str,
        severity: str = "INFO",
        related_document_id: Optional[uuid.UUID] = None,
        related_reminder_id: Optional[uuid.UUID] = None,
        related_conversation_id: Optional[uuid.UUID] = None,
        event_key: Optional[str] = None,
        payload_metadata: Optional[Dict[str, Any]] = None
    ) -> List[Notification]:
        if event_key:
            stmt = select(Notification).where(
                Notification.user_id == user_id,
                Notification.event_key.like(f"{event_key}%")
            )
            existing = db.execute(stmt).first()
            if existing:
                return []

        pref = self.get_or_create_preferences(db, user_id)

        if notification_type.startswith("DOCUMENT_") and not pref.document_event_notifications:
            return []
        if notification_type.startswith("REMINDER_") and not pref.reminder_notifications:
            return []
        if notification_type.startswith("QUERY_") and not pref.query_alert_notifications:
            return []

        channels = []
        if pref.in_app_enabled:
            channels.append("IN_APP")
        if pref.email_enabled and pref.email_address:
            channels.append("EMAIL")
        if pref.webhook_enabled and pref.webhook_url:
            channels.append("WEBHOOK")

        if not channels:
            channels = ["IN_APP"]

        created_notifs = []
        now = datetime.now(timezone.utc)

        for ch in channels:
            notif = Notification(
                id=uuid.uuid4(),
                user_id=user_id,
                notification_type=notification_type,
                title=title,
                message=message,
                channel=ch,
                status="PENDING",
                severity=severity,
                related_document_id=related_document_id,
                related_reminder_id=related_reminder_id,
                related_conversation_id=related_conversation_id,
                event_key=f"{event_key}_{ch}" if event_key else None,
                payload_metadata=payload_metadata,
                retry_count=0,
                created_at=now
            )

            if ch == "IN_APP":
                success, err = self.in_app_channel.send(notif, pref)
            elif ch == "EMAIL":
                success, err = self.email_channel.send(notif, pref)
            elif ch == "WEBHOOK":
                success, err = self.webhook_channel.send(notif, pref)
            else:
                success, err = False, f"Unknown notification channel {ch}"

            if success:
                notif.status = "SENT"
                notif.sent_at = now
            else:
                notif.status = "FAILED"
                notif.failed_at = now
                notif.failure_reason = err

            db.add(notif)
            created_notifs.append(notif)

        db.commit()
        for n in created_notifs:
            db.refresh(n)

        return created_notifs

    def list_notifications(
        self,
        db: Session,
        user: User,
        unread: Optional[bool] = None,
        notification_type: Optional[str] = None,
        severity: Optional[str] = None,
        channel: Optional[str] = None,
        skip: int = 0,
        limit: int = 50
    ) -> NotificationListResponse:
        base_filter = [Notification.user_id == user.id]

        if unread is True:
            base_filter.append(Notification.read_at.is_(None))
        elif unread is False:
            base_filter.append(Notification.read_at.is_not(None))

        if notification_type and notification_type != "ALL":
            base_filter.append(Notification.notification_type == notification_type)

        if severity and severity != "ALL":
            base_filter.append(Notification.severity == severity)

        if channel and channel != "ALL":
            base_filter.append(Notification.channel == channel)

        count_stmt = select(func.count(Notification.id)).where(and_(*base_filter))
        total = db.execute(count_stmt).scalar() or 0

        unread_stmt = select(func.count(Notification.id)).where(
            Notification.user_id == user.id,
            Notification.read_at.is_(None)
        )
        unread_count = db.execute(unread_stmt).scalar() or 0

        query_stmt = (
            select(Notification)
            .where(and_(*base_filter))
            .order_by(desc(Notification.created_at))
            .offset(skip)
            .limit(limit)
        )
        notifs = db.execute(query_stmt).scalars().all()

        return NotificationListResponse(
            items=[NotificationResponse.model_validate(n) for n in notifs],
            total=total,
            unread_count=unread_count
        )

    def get_unread_count(
        self,
        db: Session,
        user: User
    ) -> int:
        unread_stmt = select(func.count(Notification.id)).where(
            Notification.user_id == user.id,
            Notification.read_at.is_(None)
        )
        return db.execute(unread_stmt).scalar() or 0

    def mark_as_read(
        self,
        db: Session,
        user: User,
        notification_id: uuid.UUID
    ) -> NotificationResponse:
        stmt = select(Notification).where(
            Notification.id == notification_id,
            Notification.user_id == user.id
        )
        notif = db.execute(stmt).scalar_one_or_none()
        if not notif:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Notification not found"
            )

        if not notif.read_at:
            notif.read_at = datetime.now(timezone.utc)
            if notif.status == "SENT":
                notif.status = "READ"
            db.commit()
            db.refresh(notif)

        return NotificationResponse.model_validate(notif)

    def mark_all_as_read(
        self,
        db: Session,
        user: User
    ) -> int:
        now = datetime.now(timezone.utc)
        stmt = select(Notification).where(
            Notification.user_id == user.id,
            Notification.read_at.is_(None)
        )
        unread_notifs = db.execute(stmt).scalars().all()
        count = len(unread_notifs)

        for n in unread_notifs:
            n.read_at = now
            if n.status == "SENT":
                n.status = "READ"

        if count > 0:
            db.commit()

        return count

    def delete_notification(
        self,
        db: Session,
        user: User,
        notification_id: uuid.UUID
    ) -> None:
        stmt = select(Notification).where(
            Notification.id == notification_id,
            Notification.user_id == user.id
        )
        notif = db.execute(stmt).scalar_one_or_none()
        if not notif:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Notification not found"
            )

        db.delete(notif)
        db.commit()

    def process_pending_notifications(
        self,
        db: Session,
        user: User
    ) -> NotificationProcessResponse:
        pref = self.get_or_create_preferences(db, user.id)
        stmt = select(Notification).where(
            Notification.user_id == user.id,
            Notification.status == "FAILED",
            Notification.retry_count < settings.NOTIFICATION_MAX_RETRIES
        )
        retryable_notifs = list(db.execute(stmt).scalars().all())

        delivered = 0
        failed = 0
        now = datetime.now(timezone.utc)

        for notif in retryable_notifs:
            notif.retry_count += 1
            if notif.channel == "EMAIL":
                success, err = self.email_channel.send(notif, pref)
            elif notif.channel == "WEBHOOK":
                success, err = self.webhook_channel.send(notif, pref)
            else:
                success, err = True, None

            if success:
                notif.status = "SENT"
                notif.sent_at = now
                notif.failure_reason = None
                delivered += 1
            else:
                notif.status = "FAILED"
                notif.failed_at = now
                notif.failure_reason = err
                failed += 1

        if retryable_notifs:
            db.commit()

        return NotificationProcessResponse(
            processed_count=len(retryable_notifs),
            delivered_count=delivered,
            failed_count=failed,
            evaluated_at=now
        )

notification_service = NotificationService()

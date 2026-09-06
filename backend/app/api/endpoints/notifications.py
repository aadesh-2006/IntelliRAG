import uuid
from typing import Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.user import User
from app.api.deps import get_current_user
from app.schemas.notification import (
    NotificationResponse,
    NotificationListResponse,
    UnreadCountResponse,
    NotificationPreferenceResponse,
    NotificationPreferenceUpdateRequest,
    NotificationProcessResponse,
)
from app.services.notification_service import notification_service

router = APIRouter()

@router.get("", response_model=NotificationListResponse)
def list_notifications(
    unread: Optional[bool] = Query(None),
    notification_type: Optional[str] = Query(None),
    severity: Optional[str] = Query(None),
    channel: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> NotificationListResponse:
    return notification_service.list_notifications(
        db=db,
        user=current_user,
        unread=unread,
        notification_type=notification_type,
        severity=severity,
        channel=channel,
        skip=skip,
        limit=limit
    )

@router.get("/unread-count", response_model=UnreadCountResponse)
def get_unread_count(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> UnreadCountResponse:
    count = notification_service.get_unread_count(db=db, user=current_user)
    return UnreadCountResponse(unread_count=count)

@router.patch("/{notification_id}/read", response_model=NotificationResponse)
def mark_notification_read(
    notification_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> NotificationResponse:
    return notification_service.mark_as_read(
        db=db,
        user=current_user,
        notification_id=notification_id
    )

@router.post("/mark-all-read", response_model=UnreadCountResponse)
def mark_all_notifications_read(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> UnreadCountResponse:
    read_count = notification_service.mark_all_as_read(db=db, user=current_user)
    return UnreadCountResponse(unread_count=0)

@router.delete("/{notification_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_notification(
    notification_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    notification_service.delete_notification(
        db=db,
        user=current_user,
        notification_id=notification_id
    )

@router.post("/process-pending", response_model=NotificationProcessResponse)
def process_pending_notifications(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> NotificationProcessResponse:
    return notification_service.process_pending_notifications(
        db=db,
        user=current_user
    )

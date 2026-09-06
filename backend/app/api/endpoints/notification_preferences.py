from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.user import User
from app.api.deps import get_current_user
from app.schemas.notification import (
    NotificationPreferenceResponse,
    NotificationPreferenceUpdateRequest,
)
from app.services.notification_service import notification_service

router = APIRouter()

@router.get("", response_model=NotificationPreferenceResponse)
def get_notification_preferences(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> NotificationPreferenceResponse:
    return notification_service.get_preferences_response(
        db=db,
        user=current_user
    )

@router.patch("", response_model=NotificationPreferenceResponse)
def update_notification_preferences(
    request: NotificationPreferenceUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> NotificationPreferenceResponse:
    return notification_service.update_preferences(
        db=db,
        user=current_user,
        request=request
    )

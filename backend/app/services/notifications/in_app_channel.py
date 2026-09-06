from typing import Tuple, Optional
from app.models.notification import Notification, NotificationPreference
from app.services.notifications.base import BaseNotificationChannel

class InAppNotificationChannel(BaseNotificationChannel):
    def send(
        self,
        notification: Notification,
        preference: NotificationPreference
    ) -> Tuple[bool, Optional[str]]:
        if not preference.in_app_enabled:
            return False, "In-app notifications disabled in user preferences"
        return True, None

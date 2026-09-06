from abc import ABC, abstractmethod
from typing import Tuple, Optional
from app.models.notification import Notification, NotificationPreference

class BaseNotificationChannel(ABC):
    @abstractmethod
    def send(
        self,
        notification: Notification,
        preference: NotificationPreference
    ) -> Tuple[bool, Optional[str]]:
        pass

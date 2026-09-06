import json
import hmac
import hashlib
from urllib.parse import urlparse
from typing import Tuple, Optional
import httpx
from app.config import settings
from app.models.notification import Notification, NotificationPreference
from app.services.notifications.base import BaseNotificationChannel

class WebhookNotificationChannel(BaseNotificationChannel):
    def validate_webhook_url(self, url_str: str) -> bool:
        if not url_str or not url_str.strip():
            return False
        parsed = urlparse(url_str.strip())
        if parsed.scheme not in ("http", "https"):
            return False
        if not parsed.netloc:
            return False
        return True

    def send(
        self,
        notification: Notification,
        preference: NotificationPreference
    ) -> Tuple[bool, Optional[str]]:
        if not preference.webhook_enabled:
            return False, "Webhook notifications disabled in user preferences"

        url = preference.webhook_url
        if not url:
            return False, "No webhook URL configured in user preferences"

        if not self.validate_webhook_url(url):
            return False, "Invalid or unsafe webhook URL scheme"

        payload = {
            "event": notification.notification_type,
            "notification_id": str(notification.id),
            "title": notification.title,
            "message": notification.message,
            "severity": notification.severity,
            "channel": "WEBHOOK",
            "created_at": notification.created_at.isoformat() if notification.created_at else "",
            "related_document_id": str(notification.related_document_id) if notification.related_document_id else None,
            "related_reminder_id": str(notification.related_reminder_id) if notification.related_reminder_id else None,
            "related_conversation_id": str(notification.related_conversation_id) if notification.related_conversation_id else None,
            "metadata": notification.payload_metadata or {}
        }

        body_bytes = json.dumps(payload, sort_keys=True).encode("utf-8")
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "IntelliRAG-Webhook-Delivery/1.0"
        }

        if preference.webhook_secret:
            sig = hmac.new(
                preference.webhook_secret.encode("utf-8"),
                body_bytes,
                hashlib.sha256
            ).hexdigest()
            headers["X-IntelliRAG-Signature"] = f"sha256={sig}"

        try:
            with httpx.Client(timeout=settings.WEBHOOK_TIMEOUT_SECONDS, follow_redirects=False) as client:
                response = client.post(url, content=body_bytes, headers=headers)
                if 200 <= response.status_code < 300:
                    return True, None
                return False, f"Webhook server returned status {response.status_code}"
        except httpx.TimeoutException:
            return False, "Webhook request timed out"
        except Exception as e:
            return False, f"Webhook delivery error: {str(e)}"

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Tuple, Optional
from app.config import settings
from app.models.notification import Notification, NotificationPreference
from app.services.notifications.base import BaseNotificationChannel

class EmailNotificationChannel(BaseNotificationChannel):
    def send(
        self,
        notification: Notification,
        preference: NotificationPreference
    ) -> Tuple[bool, Optional[str]]:
        if not preference.email_enabled:
            return False, "Email notifications disabled in user preferences"

        recipient = preference.email_address
        if not recipient:
            return False, "No recipient email address configured in user preferences"

        if not settings.NOTIFICATION_EMAIL_ENABLED and not settings.SMTP_HOST:
            return True, None

        if not settings.SMTP_HOST:
            return False, "SMTP server not configured"

        try:
            msg = MIMEMultipart()
            msg["From"] = settings.SMTP_FROM
            msg["To"] = recipient
            msg["Subject"] = f"[IntelliRAG] {notification.title}"

            body = (
                f"{notification.title}\n\n"
                f"{notification.message}\n\n"
                f"Type: {notification.notification_type}\n"
                f"Severity: {notification.severity}\n"
                f"Timestamp: {notification.created_at.isoformat() if notification.created_at else ''}\n\n"
                f"-- \nIntelliRAG Notification Engine"
            )
            msg.attach(MIMEText(body, "plain"))

            with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT, timeout=5) as server:
                if settings.SMTP_USERNAME and settings.SMTP_PASSWORD:
                    server.starttls()
                    server.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
                server.send_message(msg)

            return True, None
        except Exception as e:
            return False, f"Failed to deliver email: {str(e)}"

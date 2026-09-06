import uuid
import pytest
from unittest.mock import patch, MagicMock
from httpx import Response
from datetime import datetime, timezone

from app.models.notification import (
    Notification,
    NotificationPreference,
)
from app.models.user import User
from app.services.notifications.email_channel import EmailNotificationChannel
from app.services.notifications.webhook_channel import WebhookNotificationChannel
from app.services.notification_service import NotificationService
from tests.test_documents import create_test_user


def test_email_channel_unconfigured():
    with patch("app.services.notifications.email_channel.settings") as mock_settings:
        mock_settings.NOTIFICATION_EMAIL_ENABLED = True
        mock_settings.SMTP_HOST = None
        channel = EmailNotificationChannel()
        notif = Notification(
            id=uuid.uuid4(),
            title="Test",
            message="Test msg",
            notification_type="TEST",
            severity="INFO",
        )
        pref = NotificationPreference(
            email_enabled=True,
            email_address="test@example.com",
        )
        success, error = channel.send(notif, pref)
        assert success is False
        assert "not configured" in error.lower()


def test_email_channel_disabled_in_pref():
    channel = EmailNotificationChannel()
    notif = Notification(id=uuid.uuid4(), title="Test", message="Test")
    pref = NotificationPreference(email_enabled=False)
    success, error = channel.send(notif, pref)
    assert success is False
    assert "disabled" in error.lower()


def test_email_channel_send_success():
    with patch("app.services.notifications.email_channel.settings") as mock_settings, \
         patch("smtplib.SMTP") as mock_smtp:
        mock_settings.NOTIFICATION_EMAIL_ENABLED = True
        mock_settings.SMTP_HOST = "smtp.example.com"
        mock_settings.SMTP_PORT = 587
        mock_settings.SMTP_USERNAME = "user"
        mock_settings.SMTP_PASSWORD = "pwd"
        mock_settings.SMTP_FROM = "noreply@intellirag.ai"

        smtp_instance = MagicMock()
        mock_smtp.return_value.__enter__.return_value = smtp_instance

        channel = EmailNotificationChannel()
        notif = Notification(
            id=uuid.uuid4(),
            title="Due Reminder",
            message="Your reminder is due.",
            notification_type="REMINDER_DUE",
            severity="WARNING",
            created_at=datetime.now(timezone.utc),
        )
        pref = NotificationPreference(
            email_enabled=True,
            email_address="client@example.com",
        )
        success, error = channel.send(notif, pref)
        assert success is True
        assert error is None
        smtp_instance.starttls.assert_called_once()
        smtp_instance.login.assert_called_once_with("user", "pwd")
        smtp_instance.send_message.assert_called_once()


def test_webhook_channel_invalid_url():
    channel = WebhookNotificationChannel()
    notif = Notification(id=uuid.uuid4(), title="Test", message="Test", notification_type="TEST")
    pref = NotificationPreference(
        webhook_enabled=True,
        webhook_url="ftp://malicious.com/hook",
    )
    success, error = channel.send(notif, pref)
    assert success is False
    assert "scheme" in error.lower()


def test_webhook_channel_success():
    channel = WebhookNotificationChannel()
    mock_resp = Response(status_code=200, json={"received": True})

    notif = Notification(
        id=uuid.uuid4(),
        title="Doc Processed",
        message="Doc #123 processed",
        notification_type="DOCUMENT_PROCESSED",
        severity="INFO",
        created_at=datetime.now(timezone.utc),
    )
    pref = NotificationPreference(
        webhook_enabled=True,
        webhook_url="https://api.example.com/webhook",
        webhook_secret="supersecret",
    )

    with patch("httpx.Client.post", return_value=mock_resp) as mock_post:
        success, error = channel.send(notif, pref)
        assert success is True
        assert error is None
        assert mock_post.called
        headers = mock_post.call_args[1]["headers"]
        assert "X-IntelliRAG-Signature" in headers
        sig = headers["X-IntelliRAG-Signature"]
        assert sig.startswith("sha256=")


def test_get_or_create_preferences(db_session):
    user, _ = create_test_user("notif_pref_user@intellirag.ai")
    service = NotificationService()
    prefs = service.get_or_create_preferences(db_session, user.id)
    assert prefs.user_id == user.id
    assert prefs.in_app_enabled is True
    assert prefs.email_enabled is False
    assert prefs.webhook_enabled is False
    assert prefs.document_event_notifications is True


def test_preferences_api_get_and_patch(client):
    user, token = create_test_user("notif_api_pref@intellirag.ai")
    auth_headers = {"Authorization": f"Bearer {token}"}

    get_res = client.get("/api/notification-preferences", headers=auth_headers)
    assert get_res.status_code == 200
    data = get_res.json()
    assert data["in_app_enabled"] is True
    assert data["has_webhook_secret"] is False

    patch_res = client.patch(
        "/api/notification-preferences",
        headers=auth_headers,
        json={
            "email_enabled": True,
            "email_address": "alerts@example.com",
            "webhook_enabled": True,
            "webhook_url": "https://hooks.example.com/alerts",
            "webhook_secret": "my-secret-key",
            "document_event_notifications": False,
        },
    )
    assert patch_res.status_code == 200
    updated = patch_res.json()
    assert updated["email_enabled"] is True
    assert updated["email_address"] == "alerts@example.com"
    assert updated["webhook_enabled"] is True
    assert updated["webhook_url"] == "https://hooks.example.com/alerts"
    assert updated["has_webhook_secret"] is True
    assert updated["document_event_notifications"] is False
    assert "webhook_secret" not in updated


def test_create_and_list_notifications(db_session):
    user, _ = create_test_user("notif_create_user@intellirag.ai")
    service = NotificationService()
    created = service.create_notification(
        db=db_session,
        user_id=user.id,
        notification_type="DOCUMENT_PROCESSED",
        title="Document Processed",
        message="Invoice #101 has been processed.",
        severity="INFO",
        payload_metadata={"doc_id": "1"},
        event_key="doc-proc-1",
    )
    assert len(created) == 1
    notif = created[0]
    assert notif.title == "Document Processed"
    assert notif.status == "SENT"
    assert notif.read_at is None

    dup = service.create_notification(
        db=db_session,
        user_id=user.id,
        notification_type="DOCUMENT_PROCESSED",
        title="Duplicate doc",
        message="Duplicate msg",
        event_key="doc-proc-1",
    )
    assert len(dup) == 0


def test_notifications_api_lifecycle(client, db_session):
    user, token = create_test_user("notif_lifecycle_user@intellirag.ai")
    auth_headers = {"Authorization": f"Bearer {token}"}

    service = NotificationService()
    service.create_notification(
        db=db_session,
        user_id=user.id,
        notification_type="DOCUMENT_UPLOADED",
        title="Doc 1",
        message="Doc 1 uploaded",
        severity="INFO",
    )
    service.create_notification(
        db=db_session,
        user_id=user.id,
        notification_type="REMINDER_DUE",
        title="Reminder 1",
        message="Reminder 1 is due",
        severity="WARNING",
    )

    count_res = client.get("/api/notifications/unread-count", headers=auth_headers)
    assert count_res.status_code == 200
    assert count_res.json()["unread_count"] >= 2

    list_res = client.get("/api/notifications", headers=auth_headers)
    assert list_res.status_code == 200
    items = list_res.json()["items"]
    assert len(items) >= 2
    target_id = items[0]["id"]

    read_res = client.patch(f"/api/notifications/{target_id}/read", headers=auth_headers)
    assert read_res.status_code == 200
    assert read_res.json()["read_at"] is not None

    mark_all_res = client.post("/api/notifications/mark-all-read", headers=auth_headers)
    assert mark_all_res.status_code == 200
    assert "unread_count" in mark_all_res.json()

    count_res2 = client.get("/api/notifications/unread-count", headers=auth_headers)
    assert count_res2.json()["unread_count"] == 0

    del_res = client.delete(f"/api/notifications/{target_id}", headers=auth_headers)
    assert del_res.status_code == 204


def test_user_isolation(client, db_session):
    user1, token1 = create_test_user("notif_iso1@intellirag.ai")
    user2, token2 = create_test_user("notif_iso2@intellirag.ai")
    auth_headers2 = {"Authorization": f"Bearer {token2}"}

    service = NotificationService()
    created = service.create_notification(
        db=db_session,
        user_id=user1.id,
        notification_type="REMINDER_DUE",
        title="User1 Secret Notif",
        message="Private data",
    )
    notif_id = created[0].id

    list_u2 = client.get("/api/notifications", headers=auth_headers2)
    assert list_u2.status_code == 200
    ids_u2 = [n["id"] for n in list_u2.json()["items"]]
    assert str(notif_id) not in ids_u2

    del_forbidden = client.delete(f"/api/notifications/{notif_id}", headers=auth_headers2)
    assert del_forbidden.status_code == 404

    read_forbidden = client.patch(f"/api/notifications/{notif_id}/read", headers=auth_headers2)
    assert read_forbidden.status_code == 404


def test_process_pending_notifications(client, db_session):
    user, token = create_test_user("notif_pending@intellirag.ai")
    auth_headers = {"Authorization": f"Bearer {token}"}

    pref = NotificationService().get_or_create_preferences(db_session, user.id)
    pref.email_enabled = True
    pref.email_address = "user@example.com"
    db_session.commit()

    with patch("smtplib.SMTP") as mock_smtp, \
         patch("app.services.notifications.email_channel.settings") as mock_settings:
        mock_settings.NOTIFICATION_EMAIL_ENABLED = True
        mock_settings.SMTP_HOST = "smtp.example.com"
        mock_settings.SMTP_PORT = 587
        mock_settings.SMTP_USERNAME = "user"
        mock_settings.SMTP_PASSWORD = "pwd"
        mock_settings.SMTP_FROM = "noreply@intellirag.ai"
        mock_smtp.return_value.__enter__.return_value = MagicMock()

        notif = Notification(
            user_id=user.id,
            notification_type="REMINDER_DUE",
            title="Pending Email",
            message="Needs delivery",
            channel="EMAIL",
            status="FAILED",
            retry_count=0,
        )
        db_session.add(notif)
        db_session.commit()

        proc_res = client.post("/api/notifications/process-pending", headers=auth_headers)
        assert proc_res.status_code == 200
        data = proc_res.json()
        assert data["processed_count"] >= 1
        assert data["delivered_count"] >= 1

        db_session.refresh(notif)
        assert notif.status == "SENT"

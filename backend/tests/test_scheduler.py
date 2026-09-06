import sys
import os
import uuid
from datetime import datetime, timezone, timedelta
from unittest.mock import patch, MagicMock

root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
for p in (root_dir, backend_dir):
    if p not in sys.path:
        sys.path.insert(0, p)

import pytest
from sqlalchemy import select
from app.config import settings
from app.models.user import User
from app.models.document import Document
from app.models.reminder import Reminder
from app.models.notification import Notification, NotificationPreference
from app.services.reminder_service import reminder_service
from app.services.date_extractor import date_extractor
from app.core.scheduler import AppScheduler, app_scheduler

def test_scheduler_start_and_shutdown():
    scheduler = AppScheduler()
    assert scheduler.is_running is False

    scheduler.start()
    assert scheduler.is_running is True
    assert scheduler.scheduler is not None
    assert len(scheduler.scheduler.get_jobs()) == 2

    scheduler.shutdown(wait=False)
    assert scheduler.is_running is False
    assert scheduler.scheduler is None

def test_scheduler_idempotent_start():
    scheduler = AppScheduler()
    scheduler.start()
    assert scheduler.is_running is True

    scheduler.start()
    assert scheduler.is_running is True
    assert len(scheduler.scheduler.get_jobs()) == 2

    scheduler.shutdown(wait=False)

def test_scheduler_disabled_when_config_false():
    scheduler = AppScheduler()
    with patch.object(settings, "SCHEDULER_ENABLED", False):
        scheduler.start()
        assert scheduler.is_running is False
        assert scheduler.scheduler is None

def test_process_all_due_reminders_multi_user(db_session):
    u1 = User(id=uuid.uuid4(), email="sch_u1@test.com", password_hash="hash")
    u2 = User(id=uuid.uuid4(), email="sch_u2@test.com", password_hash="hash")
    db_session.add_all([u1, u2])
    db_session.commit()

    now = datetime.now(timezone.utc)
    past = now - timedelta(hours=2)
    future = now + timedelta(days=5)

    rem1 = Reminder(
        id=uuid.uuid4(),
        user_id=u1.id,
        title="U1 Due Reminder",
        due_at=future,
        remind_at=past,
        status="PENDING",
        reminder_type="WARRANTY"
    )
    rem2 = Reminder(
        id=uuid.uuid4(),
        user_id=u2.id,
        title="U2 Due Reminder",
        due_at=future,
        remind_at=past,
        status="PENDING",
        reminder_type="EXPIRY"
    )
    rem3 = Reminder(
        id=uuid.uuid4(),
        user_id=u1.id,
        title="U1 Future Reminder",
        due_at=future,
        remind_at=future,
        status="PENDING",
        reminder_type="RENEWAL"
    )
    db_session.add_all([rem1, rem2, rem3])
    db_session.commit()

    res = reminder_service.process_all_due_reminders(db=db_session)
    assert res.processed_count == 2
    assert res.transitioned_due_count == 2

    db_session.refresh(rem1)
    db_session.refresh(rem2)
    db_session.refresh(rem3)

    assert rem1.status == "DUE"
    assert rem2.status == "DUE"
    assert rem3.status == "PENDING"

    notifs_u1 = db_session.execute(select(Notification).where(Notification.user_id == u1.id)).scalars().all()
    notifs_u2 = db_session.execute(select(Notification).where(Notification.user_id == u2.id)).scalars().all()

    assert len(notifs_u1) >= 1
    assert len(notifs_u2) >= 1
    assert any("U1 Due Reminder" in n.title for n in notifs_u1)
    assert any("U2 Due Reminder" in n.title for n in notifs_u2)

def test_scheduler_run_due_reminders_job(db_session):
    u = User(id=uuid.uuid4(), email="sch_job_user@test.com", password_hash="hash")
    db_session.add(u)
    db_session.commit()

    now = datetime.now(timezone.utc)
    past = now - timedelta(hours=1)
    future = now + timedelta(days=2)

    rem = Reminder(
        id=uuid.uuid4(),
        user_id=u.id,
        title="Job Executed Reminder",
        due_at=future,
        remind_at=past,
        status="PENDING"
    )
    db_session.add(rem)
    db_session.commit()

    with patch("app.core.scheduler.SessionLocal", return_value=db_session):
        with patch.object(db_session, "close", MagicMock()):
            app_scheduler.run_due_reminders_job()

    db_session.refresh(rem)
    assert rem.status == "DUE"

def test_e2e_extracted_date_to_reminder_to_scheduler_to_email(db_session):
    u = User(id=uuid.uuid4(), email="e2e_sched_user@test.com", password_hash="hash")
    pref = NotificationPreference(
        id=uuid.uuid4(),
        user_id=u.id,
        in_app_enabled=True,
        email_enabled=True,
        email_address="e2e_sched_user@test.com",
        reminder_notifications=True
    )
    db_session.add_all([u, pref])
    db_session.commit()

    doc_text = "APEX POLICY 2025\nExpiration Date: 2025-05-15\nAnnual Premium: $1,200.00"
    candidates = date_extractor.extract_from_document_content(doc_text, {})
    assert len(candidates) >= 1
    exp_cand = candidates[0]

    now = datetime.now(timezone.utc)
    past_remind = now - timedelta(minutes=30)
    future_due = now + timedelta(days=10)

    rem = Reminder(
        id=uuid.uuid4(),
        user_id=u.id,
        title=f"Actionable Reminder: {exp_cand.type}",
        due_at=future_due,
        remind_at=past_remind,
        status="PENDING",
        reminder_type=exp_cand.type,
        source_text=exp_cand.source_text
    )
    db_session.add(rem)
    db_session.commit()

    with patch("app.services.notifications.email_channel.smtplib.SMTP") as mock_smtp:
        mock_instance = MagicMock()
        mock_smtp.return_value.__enter__.return_value = mock_instance

        with patch.object(settings, "NOTIFICATION_EMAIL_ENABLED", True):
            with patch.object(settings, "SMTP_HOST", "smtp.test.com"):
                with patch("app.core.scheduler.SessionLocal", return_value=db_session):
                    with patch.object(db_session, "close", MagicMock()):
                        app_scheduler.run_due_reminders_job()

    db_session.refresh(rem)
    assert rem.status == "DUE"

    notifs = db_session.execute(
        select(Notification).where(Notification.user_id == u.id)
    ).scalars().all()

    email_notif = next((n for n in notifs if n.channel == "EMAIL"), None)
    assert email_notif is not None
    assert email_notif.status == "SENT"

def test_scheduler_job_failure_does_not_crash():
    scheduler = AppScheduler()
    with patch("app.core.scheduler.SessionLocal", side_effect=Exception("Database connection failure")):
        scheduler.run_due_reminders_job()
        scheduler.run_pending_notifications_retry_job()

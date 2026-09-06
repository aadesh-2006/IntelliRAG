import logging
from typing import Optional
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from app.config import settings
from app.db.session import SessionLocal
from app.services.reminder_service import reminder_service
from app.services.notification_service import notification_service

logger = logging.getLogger(__name__)

class AppScheduler:
    def __init__(self):
        self._scheduler: Optional[BackgroundScheduler] = None

    @property
    def scheduler(self) -> Optional[BackgroundScheduler]:
        return self._scheduler

    @property
    def is_running(self) -> bool:
        return self._scheduler is not None and self._scheduler.running

    def start(self) -> None:
        if not settings.SCHEDULER_ENABLED:
            return
        if self._scheduler is not None and self._scheduler.running:
            return

        self._scheduler = BackgroundScheduler(daemon=True)
        self._scheduler.add_job(
            func=self.run_due_reminders_job,
            trigger=IntervalTrigger(seconds=settings.REMINDER_CHECK_INTERVAL_SECONDS),
            id="process_due_reminders_job",
            name="Process due reminders and dispatch notifications",
            replace_existing=True
        )
        self._scheduler.add_job(
            func=self.run_pending_notifications_retry_job,
            trigger=IntervalTrigger(seconds=settings.NOTIFICATION_RETRY_INTERVAL_SECONDS),
            id="process_pending_notifications_job",
            name="Retry failed notifications",
            replace_existing=True
        )
        try:
            self._scheduler.start()
        except Exception as e:
            logger.error(f"Failed to start APScheduler: {e}")

    def shutdown(self, wait: bool = False) -> None:
        if self._scheduler is not None and self._scheduler.running:
            try:
                self._scheduler.shutdown(wait=wait)
            except Exception as e:
                logger.error(f"Error shutting down scheduler: {e}")
            finally:
                self._scheduler = None

    def run_due_reminders_job(self) -> None:
        db = None
        try:
            db = SessionLocal()
            reminder_service.process_all_due_reminders(db=db)
        except Exception as e:
            logger.error(f"Error in due reminders scheduler job: {e}")
        finally:
            if db is not None:
                try:
                    db.close()
                except Exception:
                    pass

    def run_pending_notifications_retry_job(self) -> None:
        db = None
        try:
            db = SessionLocal()
            from app.models.user import User
            from sqlalchemy import select
            users = db.execute(select(User)).scalars().all()
            for u in users:
                try:
                    notification_service.process_pending_notifications(db=db, user=u)
                except Exception:
                    pass
        except Exception as e:
            logger.error(f"Error in pending notifications retry scheduler job: {e}")
        finally:
            if db is not None:
                try:
                    db.close()
                except Exception:
                    pass

app_scheduler = AppScheduler()

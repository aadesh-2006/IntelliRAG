from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

revision: str = "007_add_notification_models"
down_revision: Union[str, None] = "006_add_reminder_models"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    op.create_table(
        "notification_preferences",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("user_id", UUID(as_uuid=True), nullable=False),
        sa.Column("in_app_enabled", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("email_enabled", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("webhook_enabled", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("document_event_notifications", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("reminder_notifications", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("query_alert_notifications", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("email_address", sa.String(length=255), nullable=True),
        sa.Column("webhook_url", sa.String(length=512), nullable=True),
        sa.Column("webhook_secret", sa.String(length=255), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
    )
    op.create_index(op.f("ix_notification_preferences_user_id"), "notification_preferences", ["user_id"], unique=True)

    op.create_table(
        "notifications",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("user_id", UUID(as_uuid=True), nullable=False),
        sa.Column("notification_type", sa.String(length=50), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("channel", sa.String(length=50), nullable=False, server_default="IN_APP"),
        sa.Column("status", sa.String(length=50), nullable=False, server_default="PENDING"),
        sa.Column("severity", sa.String(length=50), nullable=False, server_default="INFO"),
        sa.Column("related_document_id", UUID(as_uuid=True), nullable=True),
        sa.Column("related_reminder_id", UUID(as_uuid=True), nullable=True),
        sa.Column("related_conversation_id", UUID(as_uuid=True), nullable=True),
        sa.Column("event_key", sa.String(length=255), nullable=True),
        sa.Column("payload_metadata", sa.JSON(), nullable=True),
        sa.Column("retry_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("sent_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("read_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("failed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("failure_reason", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["related_document_id"], ["documents.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["related_reminder_id"], ["reminders.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["related_conversation_id"], ["conversations.id"], ondelete="SET NULL"),
    )
    op.create_index(op.f("ix_notifications_user_id"), "notifications", ["user_id"], unique=False)
    op.create_index(op.f("ix_notifications_notification_type"), "notifications", ["notification_type"], unique=False)
    op.create_index(op.f("ix_notifications_channel"), "notifications", ["channel"], unique=False)
    op.create_index(op.f("ix_notifications_status"), "notifications", ["status"], unique=False)
    op.create_index(op.f("ix_notifications_event_key"), "notifications", ["event_key"], unique=False)
    op.create_index(op.f("ix_notifications_created_at"), "notifications", ["created_at"], unique=False)
    op.create_index(op.f("ix_notifications_read_at"), "notifications", ["read_at"], unique=False)
    op.create_index(op.f("ix_notifications_related_document_id"), "notifications", ["related_document_id"], unique=False)
    op.create_index(op.f("ix_notifications_related_reminder_id"), "notifications", ["related_reminder_id"], unique=False)
    op.create_index(op.f("ix_notifications_related_conversation_id"), "notifications", ["related_conversation_id"], unique=False)

def downgrade() -> None:
    op.drop_index(op.f("ix_notifications_related_conversation_id"), table_name="notifications")
    op.drop_index(op.f("ix_notifications_related_reminder_id"), table_name="notifications")
    op.drop_index(op.f("ix_notifications_related_document_id"), table_name="notifications")
    op.drop_index(op.f("ix_notifications_read_at"), table_name="notifications")
    op.drop_index(op.f("ix_notifications_created_at"), table_name="notifications")
    op.drop_index(op.f("ix_notifications_event_key"), table_name="notifications")
    op.drop_index(op.f("ix_notifications_status"), table_name="notifications")
    op.drop_index(op.f("ix_notifications_channel"), table_name="notifications")
    op.drop_index(op.f("ix_notifications_notification_type"), table_name="notifications")
    op.drop_index(op.f("ix_notifications_user_id"), table_name="notifications")
    op.drop_table("notifications")

    op.drop_index(op.f("ix_notification_preferences_user_id"), table_name="notification_preferences")
    op.drop_table("notification_preferences")

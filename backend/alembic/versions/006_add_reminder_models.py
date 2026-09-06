from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

revision: str = "006_add_reminder_models"
down_revision: Union[str, None] = "005_add_conversation_models"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    op.create_table(
        "reminders",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("user_id", UUID(as_uuid=True), nullable=False),
        sa.Column("document_id", UUID(as_uuid=True), nullable=True),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("reminder_type", sa.String(length=50), nullable=False, server_default="CUSTOM"),
        sa.Column("due_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("remind_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("status", sa.String(length=50), nullable=False, server_default="PENDING"),
        sa.Column("source_text", sa.Text(), nullable=True),
        sa.Column("source_page", sa.Integer(), nullable=True),
        sa.Column("source_section", sa.String(length=255), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["document_id"], ["documents.id"], ondelete="SET NULL"),
    )
    op.create_index(op.f("ix_reminders_user_id"), "reminders", ["user_id"], unique=False)
    op.create_index(op.f("ix_reminders_document_id"), "reminders", ["document_id"], unique=False)
    op.create_index(op.f("ix_reminders_reminder_type"), "reminders", ["reminder_type"], unique=False)
    op.create_index(op.f("ix_reminders_due_at"), "reminders", ["due_at"], unique=False)
    op.create_index(op.f("ix_reminders_remind_at"), "reminders", ["remind_at"], unique=False)
    op.create_index(op.f("ix_reminders_status"), "reminders", ["status"], unique=False)

def downgrade() -> None:
    op.drop_index(op.f("ix_reminders_status"), table_name="reminders")
    op.drop_index(op.f("ix_reminders_remind_at"), table_name="reminders")
    op.drop_index(op.f("ix_reminders_due_at"), table_name="reminders")
    op.drop_index(op.f("ix_reminders_reminder_type"), table_name="reminders")
    op.drop_index(op.f("ix_reminders_document_id"), table_name="reminders")
    op.drop_index(op.f("ix_reminders_user_id"), table_name="reminders")
    op.drop_table("reminders")

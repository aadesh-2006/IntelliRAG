from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

revision: str = "008_add_cricket_models"
down_revision: Union[str, None] = "007_add_notification_models"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    op.create_table(
        "cricket_matches",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("document_id", UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", UUID(as_uuid=True), nullable=False),
        sa.Column("team_1", sa.String(length=100), nullable=False),
        sa.Column("team_2", sa.String(length=100), nullable=False),
        sa.Column("venue", sa.String(length=255), nullable=True),
        sa.Column("city", sa.String(length=100), nullable=True),
        sa.Column("match_date", sa.String(length=50), nullable=True),
        sa.Column("tournament", sa.String(length=255), nullable=True),
        sa.Column("match_number", sa.String(length=50), nullable=True),
        sa.Column("format", sa.String(length=50), nullable=True),
        sa.Column("toss_winner", sa.String(length=100), nullable=True),
        sa.Column("toss_decision", sa.String(length=50), nullable=True),
        sa.Column("winner", sa.String(length=100), nullable=True),
        sa.Column("result_text", sa.String(length=255), nullable=True),
        sa.Column("player_of_match", sa.String(length=100), nullable=True),
        sa.Column("raw_metadata", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["document_id"], ["documents.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
    )
    op.create_index(op.f("ix_cricket_matches_document_id"), "cricket_matches", ["document_id"], unique=True)
    op.create_index(op.f("ix_cricket_matches_user_id"), "cricket_matches", ["user_id"], unique=False)

    op.create_table(
        "cricket_innings",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("match_id", UUID(as_uuid=True), nullable=False),
        sa.Column("innings_number", sa.Integer(), nullable=False),
        sa.Column("team", sa.String(length=100), nullable=False),
        sa.Column("total_runs", sa.Integer(), nullable=False),
        sa.Column("wickets", sa.Integer(), nullable=False),
        sa.Column("overs", sa.Float(), nullable=False),
        sa.Column("run_rate", sa.Float(), nullable=True),
        sa.Column("extras_wides", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("extras_no_balls", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("extras_byes", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("extras_leg_byes", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("extras_penalty", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("extras_total", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("raw_metadata", sa.JSON(), nullable=True),
        sa.ForeignKeyConstraint(["match_id"], ["cricket_matches.id"], ondelete="CASCADE"),
    )
    op.create_index(op.f("ix_cricket_innings_match_id"), "cricket_innings", ["match_id"], unique=False)

    op.create_table(
        "cricket_batting_performances",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("innings_id", UUID(as_uuid=True), nullable=False),
        sa.Column("player_name", sa.String(length=150), nullable=False),
        sa.Column("runs", sa.Integer(), nullable=False),
        sa.Column("balls", sa.Integer(), nullable=False),
        sa.Column("fours", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("sixes", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("strike_rate", sa.Float(), nullable=True),
        sa.Column("dismissal", sa.String(length=255), nullable=True),
        sa.Column("batting_position", sa.Integer(), nullable=True),
        sa.Column("source_page", sa.Integer(), nullable=True),
        sa.Column("source_text", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(["innings_id"], ["cricket_innings.id"], ondelete="CASCADE"),
    )
    op.create_index(op.f("ix_cricket_batting_performances_innings_id"), "cricket_batting_performances", ["innings_id"], unique=False)
    op.create_index(op.f("ix_cricket_batting_performances_player_name"), "cricket_batting_performances", ["player_name"], unique=False)

    op.create_table(
        "cricket_bowling_performances",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("innings_id", UUID(as_uuid=True), nullable=False),
        sa.Column("player_name", sa.String(length=150), nullable=False),
        sa.Column("overs", sa.Float(), nullable=False),
        sa.Column("maidens", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("runs_conceded", sa.Integer(), nullable=False),
        sa.Column("wickets", sa.Integer(), nullable=False),
        sa.Column("economy", sa.Float(), nullable=True),
        sa.Column("wides", sa.Integer(), nullable=True),
        sa.Column("no_balls", sa.Integer(), nullable=True),
        sa.Column("source_page", sa.Integer(), nullable=True),
        sa.Column("source_text", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(["innings_id"], ["cricket_innings.id"], ondelete="CASCADE"),
    )
    op.create_index(op.f("ix_cricket_bowling_performances_innings_id"), "cricket_bowling_performances", ["innings_id"], unique=False)
    op.create_index(op.f("ix_cricket_bowling_performances_player_name"), "cricket_bowling_performances", ["player_name"], unique=False)

def downgrade() -> None:
    op.drop_table("cricket_bowling_performances")
    op.drop_table("cricket_batting_performances")
    op.drop_table("cricket_innings")
    op.drop_table("cricket_matches")

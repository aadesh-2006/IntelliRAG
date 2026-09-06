import os
import uuid
from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker
from alembic.config import Config
from alembic.script import ScriptDirectory
from app.config import settings
from app.db.base import Base
from app.db.session import get_db, SessionLocal
from app.models.user import User
from app.models.document import Document
from app.models.document_chunk import DocumentChunk
from app.models.conversation import Conversation, ConversationMessage
from app.models.reminder import Reminder
from app.models.notification import Notification, NotificationPreference
from app.models.cricket import (
    CricketMatch,
    CricketInnings,
    CricketBattingPerformance,
    CricketBowlingPerformance,
)

def test_settings_database_configuration():
    assert settings.DATABASE_URL is not None
    assert "postgresql" in settings.DATABASE_URL or "sqlite" in settings.DATABASE_URL
    assert settings.VECTOR_DIMENSION == 768
    assert settings.DB_POOL_SIZE > 0
    assert settings.DB_MAX_OVERFLOW >= 0

def test_models_metadata_registration():
    table_names = Base.metadata.tables.keys()
    assert "users" in table_names
    assert "documents" in table_names
    assert "document_chunks" in table_names
    assert "conversations" in table_names
    assert "conversation_messages" in table_names
    assert "cricket_matches" in table_names
    assert "cricket_innings" in table_names
    assert "cricket_batting_performances" in table_names
    assert "cricket_bowling_performances" in table_names
    assert "reminders" in table_names
    assert "notifications" in table_names
    assert "notification_preferences" in table_names

def test_user_model_instantiation():
    user = User(
        email="test@intellirag.ai",
        password_hash="hashed_secret_string"
    )
    assert user.email == "test@intellirag.ai"
    assert user.password_hash == "hashed_secret_string"
    assert hasattr(user, "documents")
    assert hasattr(user, "conversations")
    assert hasattr(user, "reminders")
    assert hasattr(user, "notifications")
    assert hasattr(user, "notification_preference")

def test_document_model_instantiation():
    user_id = uuid.uuid4()
    doc = Document(
        user_id=user_id,
        filename="report.pdf",
        original_filename="Annual_Report_2026.pdf",
        file_type="application/pdf",
        file_path="/storage/documents/report.pdf",
        file_size=1048576,
        status="UPLOADED",
        document_type="GENERAL_DOCUMENT",
    )
    assert doc.filename == "report.pdf"
    assert doc.file_size == 1048576
    assert doc.status == "UPLOADED"
    assert doc.document_type == "GENERAL_DOCUMENT"
    assert hasattr(doc, "chunks")
    assert hasattr(doc, "user")
    assert hasattr(doc, "reminders")

def test_document_chunk_model_instantiation():
    doc_id = uuid.uuid4()
    chunk = DocumentChunk(
        document_id=doc_id,
        chunk_index=0,
        content="IntelliRAG document chunk sample content.",
        chunk_metadata={"page": 1, "section": "Introduction"},
    )
    assert chunk.document_id == doc_id
    assert chunk.chunk_index == 0
    assert chunk.content == "IntelliRAG document chunk sample content."
    assert chunk.chunk_metadata == {"page": 1, "section": "Introduction"}
    assert hasattr(chunk, "document")
    assert hasattr(chunk, "embedding")

def test_reminder_model_instantiation():
    user_id = uuid.uuid4()
    doc_id = uuid.uuid4()
    rem = Reminder(
        user_id=user_id,
        document_id=doc_id,
        title="Warranty Renewal",
        description="Renew hardware warranty",
        reminder_type="WARRANTY",
        due_at="2026-12-31T00:00:00Z",
        remind_at="2026-12-24T00:00:00Z",
        status="PENDING",
        source_text="Warranty expires on Dec 31, 2026"
    )
    assert rem.user_id == user_id
    assert rem.document_id == doc_id
    assert rem.title == "Warranty Renewal"
    assert rem.reminder_type == "WARRANTY"
    assert rem.status == "PENDING"
    assert hasattr(rem, "user")
    assert hasattr(rem, "document")

def test_notification_model_instantiation():
    user_id = uuid.uuid4()
    notif = Notification(
        user_id=user_id,
        notification_type="DOCUMENT_PROCESSED",
        title="Doc Processed",
        message="Document processing succeeded",
        channel="IN_APP",
        status="SENT",
        severity="SUCCESS"
    )
    assert notif.user_id == user_id
    assert notif.notification_type == "DOCUMENT_PROCESSED"
    assert notif.channel == "IN_APP"
    assert notif.status == "SENT"
    assert hasattr(notif, "user")

def test_notification_preference_model_instantiation():
    user_id = uuid.uuid4()
    pref = NotificationPreference(
        user_id=user_id,
        in_app_enabled=True,
        email_enabled=True,
        webhook_enabled=True,
        email_address="user@intellirag.ai",
        webhook_url="https://example.com/webhook",
        webhook_secret="secret123"
    )
    assert pref.user_id == user_id
    assert pref.email_address == "user@intellirag.ai"
    assert pref.webhook_url == "https://example.com/webhook"
    assert hasattr(pref, "user")

def test_conversation_model_instantiation():
    user_id = uuid.uuid4()
    conv = Conversation(
        user_id=user_id,
        title="Q3 Strategy Analysis"
    )
    assert conv.user_id == user_id
    assert conv.title == "Q3 Strategy Analysis"
    assert hasattr(conv, "user")
    assert hasattr(conv, "messages")

def test_conversation_message_model_instantiation():
    conv_id = uuid.uuid4()
    msg = ConversationMessage(
        conversation_id=conv_id,
        role="assistant",
        content="Grounding confirmed in Q3 report.",
        citations=[{"citation_id": 1, "document_filename": "Q3.pdf"}],
        grounding_metadata={"retrieved_sources": 1, "highest_similarity": 0.88},
        is_sufficient_context=True
    )
    assert msg.conversation_id == conv_id
    assert msg.role == "assistant"
    assert msg.content == "Grounding confirmed in Q3 report."
    assert msg.is_sufficient_context is True
    assert msg.citations == [{"citation_id": 1, "document_filename": "Q3.pdf"}]
    assert hasattr(msg, "conversation")

def test_cricket_models_instantiation():
    user_id = uuid.uuid4()
    doc_id = uuid.uuid4()
    match = CricketMatch(
        document_id=doc_id,
        user_id=user_id,
        team_1="India",
        team_2="Australia",
        format="T20",
        venue="MCG",
        winner="India",
        result_text="India won by 5 wickets"
    )
    assert match.team_1 == "India"
    assert match.winner == "India"
    assert hasattr(match, "innings")
    assert hasattr(match, "user")
    assert hasattr(match, "document")

    innings = CricketInnings(
        match_id=match.id,
        innings_number=1,
        team="Australia",
        total_runs=185,
        wickets=6,
        overs=20.0,
        extras_total=12
    )
    assert innings.total_runs == 185
    assert innings.overs == 20.0
    assert hasattr(innings, "batting_performances")
    assert hasattr(innings, "bowling_performances")

    bat = CricketBattingPerformance(
        innings_id=innings.id,
        player_name="David Warner",
        runs=56,
        balls=38,
        fours=6,
        sixes=2,
        strike_rate=147.37,
        dismissal="c Kohli b Bumrah"
    )
    assert bat.player_name == "David Warner"
    assert bat.runs == 56

    bowl = CricketBowlingPerformance(
        innings_id=innings.id,
        player_name="Jasprit Bumrah",
        overs=4.0,
        maidens=0,
        runs_conceded=24,
        wickets=3,
        economy=6.0
    )
    assert bowl.player_name == "Jasprit Bumrah"
    assert bowl.wickets == 3

def test_get_db_generator():
    db_gen = get_db()
    db_session = next(db_gen)
    assert db_session is not None
    try:
        next(db_gen)
    except StopIteration:
        pass

def test_alembic_configuration():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    alembic_ini_path = os.path.join(base_dir, "alembic.ini")
    alembic_cfg = Config(alembic_ini_path)
    alembic_cfg.set_main_option("script_location", os.path.join(base_dir, "alembic"))
    script = ScriptDirectory.from_config(alembic_cfg)
    revisions = list(script.walk_revisions())
    assert len(revisions) >= 8
    head_rev = revisions[0]
    assert head_rev.revision == "008_add_cricket_models"
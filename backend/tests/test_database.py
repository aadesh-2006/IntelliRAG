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

def test_user_model_instantiation():
    user = User(
        email="test@intellirag.ai",
        password_hash="hashed_secret_string"
    )
    assert user.email == "test@intellirag.ai"
    assert user.password_hash == "hashed_secret_string"
    assert hasattr(user, "documents")
    assert hasattr(user, "conversations")

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
    assert len(revisions) >= 5
    head_rev = revisions[0]
    assert head_rev.revision == "005_add_conversation_models"
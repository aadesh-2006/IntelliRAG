from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = "004_add_vector_indexes"
down_revision: Union[str, None] = "003_add_document_processing_fields"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    try:
        op.execute("CREATE INDEX IF NOT EXISTS ix_document_chunks_embedding_cosine ON document_chunks USING hnsw (embedding vector_cosine_ops)")
    except Exception:
        pass

def downgrade() -> None:
    try:
        op.execute("DROP INDEX IF EXISTS ix_document_chunks_embedding_cosine")
    except Exception:
        pass

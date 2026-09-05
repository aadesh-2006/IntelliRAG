from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = "003_add_document_processing_fields"
down_revision: Union[str, None] = "002_add_user_password_hash"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    op.add_column("documents", sa.Column("processed_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("documents", sa.Column("processing_error", sa.Text(), nullable=True))
    op.add_column("documents", sa.Column("extracted_text", sa.Text(), nullable=True))
    op.add_column("documents", sa.Column("extracted_metadata", sa.JSON(), nullable=True))

def downgrade() -> None:
    op.drop_column("documents", "extracted_metadata")
    op.drop_column("documents", "extracted_text")
    op.drop_column("documents", "processing_error")
    op.drop_column("documents", "processed_at")

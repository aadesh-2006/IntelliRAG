from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = "002_add_user_password_hash"
down_revision: Union[str, None] = "001_initial_schema"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    op.add_column("users", sa.Column("password_hash", sa.String(length=255), nullable=False, server_default=""))

def downgrade() -> None:
    op.drop_column("users", "password_hash")
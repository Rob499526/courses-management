"""Add created_at to users

Revision ID: e2a186dbb039
Revises: 
Create Date: 2025-06-12 19:11:34.587949

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e2a186dbb039'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.add_column('users', sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')))


def downgrade():
    op.drop_column('users', 'created_at')
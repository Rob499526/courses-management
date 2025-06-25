"""Add created_at to user_course

Revision ID: 6b0b5f001af5
Revises: e2a186dbb039
Create Date: 2025-06-23 19:33:55.686149

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6b0b5f001af5'
down_revision: Union[str, None] = 'e2a186dbb039'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.add_column('user_course',
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False)
    )

def downgrade():
    op.drop_column('user_course', 'created_at')
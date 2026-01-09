"""add signed contract fields

Revision ID: 6f4888e0729a
Revises: d78a82d6b74b
Create Date: 2026-01-07 20:01:37.331551
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '6f4888e0729a'
down_revision = 'd78a82d6b74b'
branch_labels = None
depends_on = None


def upgrade():
    # ✅ SQLite-safe change
    op.add_column(
        'application',
        sa.Column('signed_ip', sa.String(length=45), nullable=True)
    )


def downgrade():
    op.drop_column('application', 'signed_ip')

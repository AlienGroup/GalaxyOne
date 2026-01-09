"""add loan finance tracking

Revision ID: 178479c34dd8
Revises: 6f4888e0729a
Create Date: 2026-01-08
"""

from alembic import op
import sqlalchemy as sa

revision = '178479c34dd8'
down_revision = '6f4888e0729a'
branch_labels = None
depends_on = None


def upgrade():
    # ✅ Create loan finance tracking table
    op.create_table(
        'loan_finance',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('application_id', sa.Integer(), sa.ForeignKey('application.id'), nullable=False),
        sa.Column('principal', sa.Float(), nullable=False),
        sa.Column('interest', sa.Float(), nullable=False),
        sa.Column('total_payable', sa.Float(), nullable=False),
        sa.Column('amount_paid', sa.Float(), default=0),
        sa.Column('status', sa.String(20), default='Pending'),  # Pending | Released | Settled | Defaulted
        sa.Column('date_released', sa.DateTime()),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now())
    )


def downgrade():
    op.drop_table('loan_finance')


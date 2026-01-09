"""Make application address fields required

Revision ID: 8e835789384f
Revises: e4057d8ed4f2
Create Date: 2025-10-03 11:03:07.813864

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import text


# revision identifiers, used by Alembic.
revision = '8e835789384f'
down_revision = 'e4057d8ed4f2'
branch_labels = None
depends_on = None


def upgrade():
    # For SQLite, we need to handle NOT NULL constraints differently
    conn = op.get_bind()
    
    # First, update any NULL values to empty strings for required fields
    conn.execute(text("UPDATE application SET address_line1 = '' WHERE address_line1 IS NULL"))
    conn.execute(text("UPDATE application SET city = '' WHERE city IS NULL"))
    conn.execute(text("UPDATE application SET postal_code = '' WHERE postal_code IS NULL"))
    conn.execute(text("UPDATE application SET country = '' WHERE country IS NULL"))
    
    # Use batch_alter_table for SQLite compatibility
    with op.batch_alter_table('application') as batch_op:
        batch_op.alter_column('address_line1',
                   existing_type=sa.VARCHAR(length=100),
                   nullable=False)
        batch_op.alter_column('city',
                   existing_type=sa.VARCHAR(length=50),
                   nullable=False)
        batch_op.alter_column('postal_code',
                   existing_type=sa.VARCHAR(length=10),
                   nullable=False)
        batch_op.alter_column('country',
                   existing_type=sa.VARCHAR(length=50),
                   nullable=False)


def downgrade():
    # Use batch_alter_table for SQLite compatibility
    with op.batch_alter_table('application') as batch_op:
        batch_op.alter_column('country',
                   existing_type=sa.VARCHAR(length=50),
                   nullable=True)
        batch_op.alter_column('postal_code',
                   existing_type=sa.VARCHAR(length=10),
                   nullable=True)
        batch_op.alter_column('city',
                   existing_type=sa.VARCHAR(length=50),
                   nullable=True)
        batch_op.alter_column('address_line1',
                   existing_type=sa.VARCHAR(length=100),
                   nullable=True)
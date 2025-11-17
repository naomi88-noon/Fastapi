"""Add phone_number column to users table

Revision ID: 01_add_phone_number
Revises: 
Create Date: 2025-11-03 12:00:00.000000
"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '01_add_phone_number'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Add 'phone_number' column to 'users' table
    op.add_column('users', sa.Column('phone_number', sa.String(length=20), nullable=True))


def downgrade():
    # Remove 'phone_number' column (if rollback)
    op.drop_column('users', 'phone_number')
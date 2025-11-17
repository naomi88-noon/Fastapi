"""Add owner_id column to todo table"""

from alembic import op
import sqlalchemy as sa

revision = '02_add_owner_id_to_todo'
down_revision = '01_add_phone_number'  # put your previous migration ID
branch_labels = None
depends_on = None

def upgrade():
    op.add_column('todo', sa.Column('owner_id', sa.Integer(), nullable=True))
    op.create_foreign_key('fk_todo_owner', 'todo', 'users', ['owner_id'], ['id'])

def downgrade():
    op.drop_constraint('fk_todo_owner', 'todo', type_='foreignkey')
    op.drop_column('todo', 'owner_id')
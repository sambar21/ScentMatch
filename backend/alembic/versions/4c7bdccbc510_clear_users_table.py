"""clear_users_table

Revision ID: 4c7bdccbc510
Revises: b04fc1803860
Create Date: 2025-09-26 19:45:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '4c7bdccbc510'
down_revision = 'b04fc1803860'
branch_labels = None
depends_on = None

def upgrade() -> None:
    op.execute("DELETE FROM users")

def downgrade() -> None:
    pass
"""Introduce user admin column

Revision ID: 299678a8d216
Revises:
Create Date: 2016-10-04 14:27:06.598503

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '299678a8d216'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('user', sa.Column('is_admin', sa.Boolean))


def downgrade():
    op.drop_column('user', 'is_admin')

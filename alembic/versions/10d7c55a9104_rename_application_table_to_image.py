"""Rename Application table to Image

Revision ID: 10d7c55a9104
Revises:
Create Date: 2017-05-10 18:51:00.876105

"""
from alembic import op
import sqlalchemy as sa
from remoteappmanager.db import orm

# revision identifiers, used by Alembic.
revision = '10d7c55a9104'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Joy. sqlite does not support column renaming, so we need to
    # create and copy.
    connection = op.get_bind()

    ImageTable = orm.Image.__table__

    Application = sa.Table(
        'application',
        sa.MetaData(),
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('image', sa.Unicode()),
    )

    TmpAccounting = sa.Table(
        'tmpaccounting',
        sa.MetaData(),
        sa.Column('id', sa.String(32), primary_key=True),
        sa.Column('user_id', sa.Integer),
        sa.Column('image_id', sa.Integer),
        sa.Column('application_policy_id', sa.Integer)
        )

    OldAccounting = sa.Table(
        'accounting',
        sa.MetaData(),
        sa.Column('id', sa.String(32), primary_key=True),
        sa.Column('user_id', sa.Integer),
        sa.Column('application_id', sa.Integer),
        sa.Column('application_policy_id', sa.Integer)
        )

    NewAccounting = orm.Accounting.__table__

    ImageTable.create(connection)
    with connection.begin():
        for row in connection.execute(Application.select()):
            d = {"id": row[0], "name": row[1]}
            connection.execute(ImageTable.insert(), id=row[0], name=row[1])

    # Wait to delete the table, or the cascading will destroy the content of
    # the accounting.

    TmpAccounting.create(connection)

    with connection.begin():
        for row in connection.execute(OldAccounting.select()):
            connection.execute(TmpAccounting.insert(),
                               id=row[0],
                               user_id=row[1],
                               image_id=row[2],
                               application_policy_id=row[3])

    op.drop_table("accounting")

    NewAccounting.create(connection)

    with connection.begin():
        for row in connection.execute(TmpAccounting.select()):
            d = {
                "id": row[0],
                "user_id": row[1],
                "image_id": row[2],
                "application_policy_id": row[3]
                }
            connection.execute(NewAccounting.insert(), **d)

    op.drop_table('application')
    op.drop_table('tmpaccounting')


def downgrade():
    raise Exception("cannot downgrade")

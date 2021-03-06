"""empty message

Revision ID: 7b5139f2b9f5
Revises: 68ee37e507e5
Create Date: 2021-07-18 01:13:54.323307

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7b5139f2b9f5'
down_revision = '68ee37e507e5'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('student', schema=None) as batch_op:
        batch_op.add_column(sa.Column('index', sa.Integer(), nullable=False))
        batch_op.alter_column('test_room_id',
               existing_type=sa.VARCHAR(),
               nullable=True)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('student', schema=None) as batch_op:
        batch_op.alter_column('test_room_id',
               existing_type=sa.VARCHAR(),
               nullable=False)
        batch_op.drop_column('index')

    # ### end Alembic commands ###

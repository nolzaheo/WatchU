"""empty message

Revision ID: ae4651fccb72
Revises: 4431291f0ee4
Create Date: 2021-07-18 01:54:03.049994

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ae4651fccb72'
down_revision = '4431291f0ee4'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('log', schema=None) as batch_op:
        batch_op.alter_column('test_room_id',
               existing_type=sa.VARCHAR(),
               nullable=False)
        batch_op.alter_column('student_id',
               existing_type=sa.INTEGER(),
               nullable=False)

    with op.batch_alter_table('student', schema=None) as batch_op:
        batch_op.alter_column('test_room_id',
               existing_type=sa.VARCHAR(),
               nullable=False)

    with op.batch_alter_table('test_room', schema=None) as batch_op:
        batch_op.alter_column('professor_id',
               existing_type=sa.INTEGER(),
               nullable=False)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('test_room', schema=None) as batch_op:
        batch_op.alter_column('professor_id',
               existing_type=sa.INTEGER(),
               nullable=True)

    with op.batch_alter_table('student', schema=None) as batch_op:
        batch_op.alter_column('test_room_id',
               existing_type=sa.VARCHAR(),
               nullable=True)

    with op.batch_alter_table('log', schema=None) as batch_op:
        batch_op.alter_column('student_id',
               existing_type=sa.INTEGER(),
               nullable=True)
        batch_op.alter_column('test_room_id',
               existing_type=sa.VARCHAR(),
               nullable=True)

    # ### end Alembic commands ###
"""empty message

Revision ID: 58d5af4ffb0c
Revises: f4f7f32518dd
Create Date: 2021-08-14 11:56:35.439412

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '58d5af4ffb0c'
down_revision = 'f4f7f32518dd'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('test_room', schema=None) as batch_op:
        batch_op.alter_column('title',
               existing_type=sa.VARCHAR(),
               nullable=False)
        batch_op.alter_column('state',
               existing_type=sa.VARCHAR(),
               nullable=False)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('test_room', schema=None) as batch_op:
        batch_op.alter_column('state',
               existing_type=sa.VARCHAR(),
               nullable=True)
        batch_op.alter_column('title',
               existing_type=sa.VARCHAR(),
               nullable=True)

    # ### end Alembic commands ###
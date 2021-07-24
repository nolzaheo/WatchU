"""empty message

Revision ID: 0f1dea1026d8
Revises: bab28d93d304
Create Date: 2021-07-18 02:28:46.426011

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0f1dea1026d8'
down_revision = 'bab28d93d304'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('log', schema=None) as batch_op:
        batch_op.add_column(sa.Column('test_room_id', sa.String(), nullable=False))
        batch_op.create_foreign_key(batch_op.f('fk_log_test_room_id_test_room'), 'test_room', ['test_room_id'], ['id'], ondelete='CASCADE')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('log', schema=None) as batch_op:
        batch_op.drop_constraint(batch_op.f('fk_log_test_room_id_test_room'), type_='foreignkey')
        batch_op.drop_column('test_room_id')

    # ### end Alembic commands ###

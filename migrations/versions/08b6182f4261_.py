"""empty message

Revision ID: 08b6182f4261
Revises: 427675801f21
Create Date: 2024-10-24 08:34:20.257553

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '08b6182f4261'
down_revision = '427675801f21'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('reserva', schema=None) as batch_op:
        batch_op.add_column(sa.Column('user_id', sa.Integer(), nullable=False))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('reserva', schema=None) as batch_op:
        batch_op.drop_column('user_id')

    # ### end Alembic commands ###
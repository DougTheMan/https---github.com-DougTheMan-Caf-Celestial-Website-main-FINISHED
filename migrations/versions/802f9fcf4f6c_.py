"""empty message

Revision ID: 802f9fcf4f6c
Revises: bed5cfa52873
Create Date: 2024-09-21 12:59:31.706772

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '802f9fcf4f6c'
down_revision = 'bed5cfa52873'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('reserva', schema=None) as batch_op:
        batch_op.add_column(sa.Column('data', sa.Date(), nullable=False))
        batch_op.drop_column('disponibilidade')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('reserva', schema=None) as batch_op:
        batch_op.add_column(sa.Column('disponibilidade', sa.INTEGER(), nullable=False))
        batch_op.drop_column('data')

    # ### end Alembic commands ###
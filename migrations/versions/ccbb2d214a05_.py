"""empty message

Revision ID: ccbb2d214a05
Revises: 613f3086a46f
Create Date: 2024-10-31 14:01:26.383096

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ccbb2d214a05'
down_revision = '613f3086a46f'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('registro', schema=None) as batch_op:
        batch_op.drop_column('forma_de_entrega')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('registro', schema=None) as batch_op:
        batch_op.add_column(sa.Column('forma_de_entrega', sa.VARCHAR(length=20), nullable=False))

    # ### end Alembic commands ###
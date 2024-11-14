"""empty message

Revision ID: 37096ae3a8cd
Revises: 920c8a8f7f2b
Create Date: 2024-09-21 12:07:00.613632

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '37096ae3a8cd'
down_revision = '920c8a8f7f2b'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('review',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('descricao', sa.String(length=500), nullable=False),
    sa.Column('estrela', sa.Integer(), nullable=False),
    sa.Column('Itens_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['Itens_id'], ['itens.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.drop_table('reviews')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('reviews',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('descricao', sa.VARCHAR(), nullable=False),
    sa.Column('estrela', sa.INTEGER(), nullable=False),
    sa.Column('id_itens', sa.INTEGER(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.drop_table('review')
    # ### end Alembic commands ###
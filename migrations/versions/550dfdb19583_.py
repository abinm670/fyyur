"""empty message

Revision ID: 550dfdb19583
Revises: 4ecab8fd50f7
Create Date: 2020-06-01 18:35:21.633627

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '550dfdb19583'
down_revision = '4ecab8fd50f7'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('venues', sa.Column('seeking_talent', sa.Boolean(), server_default='false', nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('venues', 'seeking_talent')
    # ### end Alembic commands ###

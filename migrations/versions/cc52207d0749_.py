"""empty message

Revision ID: cc52207d0749
Revises: 550dfdb19583
Create Date: 2020-06-04 04:36:58.984397

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'cc52207d0749'
down_revision = '550dfdb19583'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('venues', sa.Column('website', sa.String(length=500), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('venues', 'website')
    # ### end Alembic commands ###
"""camera start date

Revision ID: 7d2977404e00
Revises: 67073be45d5c
Create Date: 2018-04-30 07:52:56.161324

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7d2977404e00'
down_revision = '67073be45d5c'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('chat', sa.Column('start_date', sa.DateTime(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('chat', 'start_date')
    # ### end Alembic commands ###

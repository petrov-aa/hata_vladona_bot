"""remove image path column

Revision ID: 1a071de26fbe
Revises: aef5cec32956
Create Date: 2018-05-14 02:07:44.107528

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '1a071de26fbe'
down_revision = 'aef5cec32956'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('image', 'path')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('image', sa.Column('path', mysql.VARCHAR(collation='utf8_unicode_ci', length=255), nullable=True))
    # ### end Alembic commands ###

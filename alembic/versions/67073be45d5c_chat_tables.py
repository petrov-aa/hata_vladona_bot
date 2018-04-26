"""chat tables

Revision ID: 67073be45d5c
Revises: b7695a538c96
Create Date: 2018-04-26 23:31:52.676212

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '67073be45d5c'
down_revision = 'b7695a538c96'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('camera',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=50), nullable=True),
    sa.Column('url_base', sa.String(length=255), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('chat',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('camera_id', sa.Integer(), nullable=True),
    sa.Column('state', sa.String(length=50), nullable=True),
    sa.ForeignKeyConstraint(['camera_id'], ['camera.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.add_column('gif', sa.Column('camera_id', sa.Integer(), nullable=True))
    op.create_foreign_key(None, 'gif', 'camera', ['camera_id'], ['id'])
    op.add_column('image', sa.Column('camera_id', sa.Integer(), nullable=True))
    op.create_foreign_key(None, 'image', 'camera', ['camera_id'], ['id'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'image', type_='foreignkey')
    op.drop_column('image', 'camera_id')
    op.drop_constraint(None, 'gif', type_='foreignkey')
    op.drop_column('gif', 'camera_id')
    op.drop_table('chat')
    op.drop_table('camera')
    # ### end Alembic commands ###

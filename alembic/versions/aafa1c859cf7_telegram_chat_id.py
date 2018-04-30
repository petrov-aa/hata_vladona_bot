"""telegram chat id

Revision ID: aafa1c859cf7
Revises: 8eeca44b494b
Create Date: 2018-04-30 08:58:25.188678

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'aafa1c859cf7'
down_revision = '8eeca44b494b'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('chat', sa.Column('telegram_chat_id', sa.String(length=32), nullable=True))
    op.create_index(op.f('ix_chat_telegram_chat_id'), 'chat', ['telegram_chat_id'], unique=True)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_chat_telegram_chat_id'), table_name='chat')
    op.drop_column('chat', 'telegram_chat_id')
    # ### end Alembic commands ###

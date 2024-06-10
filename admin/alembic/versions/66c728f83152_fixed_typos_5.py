"""Fixed typos_5!

Revision ID: 66c728f83152
Revises: fc1cd35d5008
Create Date: 2023-11-22 11:33:09.672591

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlalchemy_utils


# revision identifiers, used by Alembic.
revision: str = '66c728f83152'
down_revision: Union[str, None] = 'fc1cd35d5008'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users_subscribes', sa.Column('client_user_subscribe_id', sa.Integer(), nullable=True, comment='Идентификатор абонемента пользователя в системе клиента'))
    op.drop_column('users_subscribes', 'client_subscribe_id')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users_subscribes', sa.Column('client_subscribe_id', sa.INTEGER(), autoincrement=False, nullable=True, comment='Идентификатор абонемента пользователя в системе клиента'))
    op.drop_column('users_subscribes', 'client_user_subscribe_id')
    # ### end Alembic commands ###

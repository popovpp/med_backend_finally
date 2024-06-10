"""Fixed typos_2!

Revision ID: a0940c183480
Revises: 2e9bbfe071c2
Create Date: 2023-11-21 16:04:07.088164

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlalchemy_utils


# revision identifiers, used by Alembic.
revision: str = 'a0940c183480'
down_revision: Union[str, None] = '2e9bbfe071c2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('financial_types', sa.Column('client_financial_type_id', sa.Integer(), nullable=True, comment='Идентификатор финансового типа в системе клиента'))
    op.drop_column('financial_types', 'client_shifr_id')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('financial_types', sa.Column('client_shifr_id', sa.INTEGER(), autoincrement=False, nullable=True, comment='Идентификатор финансового типа в системе клиента'))
    op.drop_column('financial_types', 'client_financial_type_id')
    # ### end Alembic commands ###

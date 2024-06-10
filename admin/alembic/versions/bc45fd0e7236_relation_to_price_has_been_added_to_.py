"""Relation to price has been added to service

Revision ID: bc45fd0e7236
Revises: 259fbb622a53
Create Date: 2023-10-27 18:05:14.410891

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlalchemy_utils


# revision identifiers, used by Alembic.
revision: str = 'bc45fd0e7236'
down_revision: Union[str, None] = '259fbb622a53'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('services', sa.Column('price_id', sa.Integer(), nullable=True, comment='Идентификатор прайса услуги'))
    op.create_foreign_key(None, 'services', 'prices', ['price_id'], ['id'])
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'services', type_='foreignkey')
    op.drop_column('services', 'price_id')
    # ### end Alembic commands ###

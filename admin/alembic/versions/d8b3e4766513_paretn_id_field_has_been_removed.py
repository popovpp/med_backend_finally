"""Paretn_id field has been removed!

Revision ID: d8b3e4766513
Revises: ebdb45f328f2
Create Date: 2023-11-11 19:12:59.366132

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlalchemy_utils


# revision identifiers, used by Alembic.
revision: str = 'd8b3e4766513'
down_revision: Union[str, None] = 'ebdb45f328f2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('nodes_parent_id_fkey', 'nodes', type_='foreignkey')
    op.drop_column('nodes', 'parent_id')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('nodes', sa.Column('parent_id', sa.INTEGER(), autoincrement=False, nullable=True, comment='Идентификатор родителя'))
    op.create_foreign_key('nodes_parent_id_fkey', 'nodes', 'nodes', ['parent_id'], ['id'])
    # ### end Alembic commands ###

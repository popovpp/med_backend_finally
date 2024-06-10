"""string to ltree has been done_3!

Revision ID: d2534ccb1114
Revises: c19bac568382
Create Date: 2023-11-11 23:10:35.805154

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlalchemy_utils


# revision identifiers, used by Alembic.
revision: str = 'd2534ccb1114'
down_revision: Union[str, None] = 'c19bac568382'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_index(op.f('ix_nodes_path'), 'nodes', ['path'], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_nodes_path'), table_name='nodes')
    # ### end Alembic commands ###

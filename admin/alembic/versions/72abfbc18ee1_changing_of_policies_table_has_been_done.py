"""Changing of policies table has been done!

Revision ID: 72abfbc18ee1
Revises: ceb10bf0e4ba
Create Date: 2024-02-21 23:36:31.125575

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlalchemy_utils


# revision identifiers, used by Alembic.
revision: str = '72abfbc18ee1'
down_revision: Union[str, None] = 'ceb10bf0e4ba'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    pass
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    pass
    # ### end Alembic commands ###

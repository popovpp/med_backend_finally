"""merge 415a848dac8a and 1b141fcd362b

Revision ID: 04c8c8379d4d
Revises: 415a848dac8a, 1b141fcd362b
Create Date: 2024-01-23 17:26:23.955717

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlalchemy_utils


# revision identifiers, used by Alembic.
revision: str = '04c8c8379d4d'
down_revision: Union[str, None] = ('415a848dac8a', '1b141fcd362b')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass

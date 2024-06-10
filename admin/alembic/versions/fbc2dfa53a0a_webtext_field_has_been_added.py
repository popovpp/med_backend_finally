"""webtext field has been added!

Revision ID: fbc2dfa53a0a
Revises: f15d80f477be
Create Date: 2023-11-13 10:09:52.338811

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlalchemy_utils


# revision identifiers, used by Alembic.
revision: str = 'fbc2dfa53a0a'
down_revision: Union[str, None] = 'f15d80f477be'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('services_groups', sa.Column('webtext', sa.String(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('services_groups', 'webtext')
    # ### end Alembic commands ###

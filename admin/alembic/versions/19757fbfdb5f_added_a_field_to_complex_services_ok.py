"""Added a field to complex_services. Ok!

Revision ID: 19757fbfdb5f
Revises: 19a318f52ccf
Create Date: 2023-12-15 17:43:44.378613

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlalchemy_utils


# revision identifiers, used by Alembic.
revision: str = '19757fbfdb5f'
down_revision: Union[str, None] = '19a318f52ccf'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('complex_services', sa.Column('client_id', sa.Integer(), nullable=True, comment='Идентификатор услуги в системе Клиента'))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('complex_services', 'client_id')
    # ### end Alembic commands ###

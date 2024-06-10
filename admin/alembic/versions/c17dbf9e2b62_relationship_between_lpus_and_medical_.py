"""relationship between lpus and medical_centers has been added

Revision ID: c17dbf9e2b62
Revises: 0b06b91ea746
Create Date: 2024-02-19 10:31:17.825812

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlalchemy_utils


# revision identifiers, used by Alembic.
revision: str = 'c17dbf9e2b62'
down_revision: Union[str, None] = '0b06b91ea746'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('medical_centers', sa.Column('lpu_id', sa.Integer(), nullable=True, comment='Идентификатор города'))
    op.create_foreign_key(None, 'medical_centers', 'lpus', ['lpu_id'], ['id'])
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'medical_centers', type_='foreignkey')
    op.drop_column('medical_centers', 'lpu_id')
    # ### end Alembic commands ###

"""is_active field was added ok!

Revision ID: 091c7927a951
Revises: aed3a12c12a9
Create Date: 2023-09-26 16:59:54.731781

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlalchemy_utils


# revision identifiers, used by Alembic.
revision: str = '091c7927a951'
down_revision: Union[str, None] = 'aed3a12c12a9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('cities', sa.Column('is_active', sa.Boolean(), nullable=True))
    op.add_column('doctors', sa.Column('is_active', sa.Boolean(), nullable=True))
    op.add_column('doctors_services', sa.Column('is_active', sa.Boolean(), nullable=True))
    op.add_column('mcenters_mdepartments', sa.Column('is_active', sa.Boolean(), nullable=True))
    op.add_column('medical_centers', sa.Column('is_active', sa.Boolean(), nullable=True))
    op.add_column('medical_departments', sa.Column('is_active', sa.Boolean(), nullable=True))
    op.add_column('medical_specialities', sa.Column('is_active', sa.Boolean(), nullable=True))
    op.add_column('services', sa.Column('is_active', sa.Boolean(), nullable=True))
    op.add_column('services_directions', sa.Column('is_active', sa.Boolean(), nullable=True))
    op.add_column('services_types', sa.Column('is_active', sa.Boolean(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('services_types', 'is_active')
    op.drop_column('services_directions', 'is_active')
    op.drop_column('services', 'is_active')
    op.drop_column('medical_specialities', 'is_active')
    op.drop_column('medical_departments', 'is_active')
    op.drop_column('medical_centers', 'is_active')
    op.drop_column('mcenters_mdepartments', 'is_active')
    op.drop_column('doctors_services', 'is_active')
    op.drop_column('doctors', 'is_active')
    op.drop_column('cities', 'is_active')
    # ### end Alembic commands ###

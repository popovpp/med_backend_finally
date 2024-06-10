"""Removed not needed tables!

Revision ID: 2c034c923941
Revises: f519fed9125d
Create Date: 2023-11-16 15:12:28.292909

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlalchemy_utils


# revision identifiers, used by Alembic.
revision: str = '2c034c923941'
down_revision: Union[str, None] = 'f519fed9125d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index('ix_user_relatives_id', table_name='user_relatives')
    op.drop_table('user_relatives')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('user_relatives',
    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('user_id', sa.INTEGER(), autoincrement=False, nullable=False, comment='идентификатор потльзователя'),
    sa.Column('user_relative_id', sa.INTEGER(), autoincrement=False, nullable=False, comment='Идентификатор родственника пользователя'),
    sa.Column('relationship_degree_id', sa.INTEGER(), autoincrement=False, nullable=False, comment='Идентификатор степени родства'),
    sa.Column('is_legal_agent', sa.BOOLEAN(), autoincrement=False, nullable=True, comment='Флаг является законным представителем / не является законным представителем'),
    sa.ForeignKeyConstraint(['relationship_degree_id'], ['relationship_degreeses.id'], name='user_relatives_relationship_degree_id_fkey'),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], name='user_relatives_user_id_fkey'),
    sa.ForeignKeyConstraint(['user_relative_id'], ['users.id'], name='user_relatives_user_relative_id_fkey'),
    sa.PrimaryKeyConstraint('id', name='user_relatives_pkey'),
    comment='Таблица "Родственники пользователя"'
    )
    op.create_index('ix_user_relatives_id', 'user_relatives', ['id'], unique=False)
    # ### end Alembic commands ###

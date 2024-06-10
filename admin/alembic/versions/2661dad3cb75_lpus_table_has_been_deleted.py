"""lpus table has been deleted

Revision ID: 2661dad3cb75
Revises: d67b19f3fefa
Create Date: 2024-02-19 10:26:29.203673

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlalchemy_utils
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '2661dad3cb75'
down_revision: Union[str, None] = 'd67b19f3fefa'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index('ix_lpus_id', table_name='lpus')
    op.drop_table('lpus')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('lpus',
    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('client_id', sa.BIGINT(), autoincrement=False, nullable=True, comment='Идентификатор записи в системе клиента'),
    sa.Column('name', sa.VARCHAR(length=200), autoincrement=False, nullable=False, comment='Наименование ЛПУ'),
    sa.Column('description', sa.TEXT(), autoincrement=False, nullable=True, comment='Описание ЛПУ'),
    sa.Column('start_date', postgresql.TIMESTAMP(), autoincrement=False, nullable=True, comment='Дата и время начала использования'),
    sa.Column('end_date', postgresql.TIMESTAMP(), autoincrement=False, nullable=True, comment='Дата и время окончания использования'),
    sa.Column('is_active', sa.BOOLEAN(), autoincrement=False, nullable=True, comment='Флаг активно/неактивно'),
    sa.PrimaryKeyConstraint('id', name='lpus_pkey'),
    comment='Таблица "Лечебныо-профилактические учреждения"'
    )
    op.create_index('ix_lpus_id', 'lpus', ['id'], unique=False)
    # ### end Alembic commands ###

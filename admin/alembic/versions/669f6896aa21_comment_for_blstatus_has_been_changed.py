"""comment for blstatus has been changed!

Revision ID: 669f6896aa21
Revises: 30b84ff72f9d
Create Date: 2024-01-30 13:30:41.292861

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlalchemy_utils


# revision identifiers, used by Alembic.
revision: str = '669f6896aa21'
down_revision: Union[str, None] = '30b84ff72f9d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('access_tickets', 'bl_status',
               existing_type=sa.INTEGER(),
               comment='Статус номерка: 0 - блокирован для выдачи в регистратуре,                                  1 - активный, 2 - выдан пациенту, 3 - зарезервирован;',
               existing_comment='Длительность услуги в минутах',
               existing_nullable=True)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('access_tickets', 'bl_status',
               existing_type=sa.INTEGER(),
               comment='Длительность услуги в минутах',
               existing_comment='Статус номерка: 0 - блокирован для выдачи в регистратуре,                                  1 - активный, 2 - выдан пациенту, 3 - зарезервирован;',
               existing_nullable=True)
    # ### end Alembic commands ###

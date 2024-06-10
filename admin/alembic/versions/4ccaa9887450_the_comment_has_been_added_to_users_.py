"""The comment has been added to users_services_carts!

Revision ID: 4ccaa9887450
Revises: d9c12c87c0c6
Create Date: 2024-04-13 08:11:32.472217

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlalchemy_utils


# revision identifiers, used by Alembic.
revision: str = '4ccaa9887450'
down_revision: Union[str, None] = 'd9c12c87c0c6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('users_services_carts', 'service_status',
               existing_type=sa.INTEGER(),
               comment='Статус услуги: 0 / 3 - назначена, 1 - выполнена, 2 - отменена, для service_group.client_id == 86137 : 100 - запрос на получение документа отправлен,',
               existing_comment='Статус услуги: 0 / 3 - назначена, 1 - выполнена, 2 - отменена',
               existing_nullable=True)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('users_services_carts', 'service_status',
               existing_type=sa.INTEGER(),
               comment='Статус услуги: 0 / 3 - назначена, 1 - выполнена, 2 - отменена',
               existing_comment='Статус услуги: 0 / 3 - назначена, 1 - выполнена, 2 - отменена,             для service_group.client_id == 86137 : 100 - запрос на получение документа отправлен,',
               existing_nullable=True)
    # ### end Alembic commands ###

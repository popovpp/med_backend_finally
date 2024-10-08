"""initpro_payments_receipts and email to medical_centers have been added!

Revision ID: 0177e7593595
Revises: 706f1223fa63
Create Date: 2024-04-03 14:55:51.043160

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlalchemy_utils


# revision identifiers, used by Alembic.
revision: str = '0177e7593595'
down_revision: Union[str, None] = '706f1223fa63'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('initpro_payments_receipts',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('initpro_payment_method', sa.String(length=15), nullable=False, comment='Признак способа расчёта в системе Инитпро'),
    sa.Column('paykeeper_id', sa.Integer(), nullable=False, comment='Идентификатор подтвержденного в системе PayKeeper платежа'),
    sa.Column('initpro_payment_type', sa.String(length=1), nullable=False, comment='Вид оплаты в системе Инитпро'),
    sa.Column('timestamp', sa.DateTime(), nullable=False, comment='Дата и время возникновения текущего статуса'),
    sa.Column('uuid', sa.String(length=36), nullable=True, comment='Идентификатор документа в системе Инитпро'),
    sa.Column('status', sa.String(length=20), nullable=True, comment='Статус регистрации документа в системе Инитпро'),
    sa.Column('error_id', sa.String(length=50), nullable=True, comment='Идентификатор ошибки в системе Инитпро'),
    sa.Column('error_code', sa.Integer(), nullable=True, comment='Код ошибки в системе Инитпро'),
    sa.Column('error_text', sa.String(), nullable=True, comment='Сообщение об ошибке в системе Инитпро'),
    sa.Column('error_type', sa.String(length=20), nullable=True, comment='Тип ошибки в системе Инитпро'),
    sa.Column('payload_total', sa.String(), nullable=True, comment='Параметр total в системе Инитпро'),
    sa.Column('payload_fns_site', sa.String(), nullable=True, comment='Параметр fns_site в системе Инитпро'),
    sa.Column('payload_fn_number', sa.String(), nullable=True, comment='Параметр fn_number в системе Инитпро'),
    sa.Column('payload_shifr_number', sa.String(), nullable=True, comment='Параметр shifr_number в системе Инитпро'),
    sa.Column('payload_receipt_datetime', sa.DateTime(), nullable=True, comment='Параметр receipt_datetime в системе Инитпро'),
    sa.Column('payload_fiscal_receipt_number', sa.String(), nullable=True, comment='Параметр receipt_number в системе Инитпро'),
    sa.Column('payload_fiscal_document_number', sa.String(), nullable=True, comment='Параметр fiscal_document_number в системе Инитпро'),
    sa.Column('payload_ecr_registration_number', sa.String(), nullable=True, comment='Параметр ecr_registration_number в системе Инитпро'),
    sa.Column('payload_fiscal_document_attribute', sa.String(), nullable=True, comment='Параметр fiscal_document_attribute в системе Инитпро'),
    sa.Column('payload_group_code', sa.String(), nullable=True, comment='Параметр group_code в системе Инитпро'),
    sa.Column('payload_daemon_code', sa.String(), nullable=True, comment='Параметр daemon_code в системе Инитпро'),
    sa.Column('payload_device_code', sa.String(), nullable=True, comment='Параметр device_code в системе Инитпро'),
    sa.Column('payload_warnings', sa.String(), nullable=True, comment='Параметр warnings в системе Инитпро'),
    sa.Column('payload_external_id', sa.String(), nullable=True, comment='Параметр external_id в системе Инитпро'),
    sa.Column('payload_callback_url', sa.String(), nullable=True, comment='Параметр callback_ur в системе Инитпро'),
    sa.PrimaryKeyConstraint('id'),
    comment='Таблица "Регистрация документа в онлайн кассе Инитпро"'
    )
    op.create_index(op.f('ix_initpro_payments_receipts_id'), 'initpro_payments_receipts', ['id'], unique=False)
    op.add_column('medical_centers', sa.Column('email', sa.String(length=200), nullable=True, comment='Электронная почта пользователя'))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('medical_centers', 'email')
    op.drop_index(op.f('ix_initpro_payments_receipts_id'), table_name='initpro_payments_receipts')
    op.drop_table('initpro_payments_receipts')
    # ### end Alembic commands ###

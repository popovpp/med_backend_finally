"""Removed not needed tables!

Revision ID: 940ac4b55ed4
Revises: e9d035ada2ac
Create Date: 2023-11-16 14:48:43.337543

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlalchemy_utils
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '940ac4b55ed4'
down_revision: Union[str, None] = 'e9d035ada2ac'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index('ix_documents_types_id', table_name='documents_types')
    op.drop_table('documents_types')
    op.drop_index('ix_doctors_services_id', table_name='doctors_services')
    op.drop_table('doctors_services')
    op.drop_index('ix_users_payments_id', table_name='users_payments')
    op.drop_table('users_payments')
    op.drop_index('ix_users_subscriptions_items_id', table_name='users_subscriptions_items')
    op.drop_table('users_subscriptions_items')
    op.drop_index('ix_users_subscriptions_id', table_name='users_subscriptions')
    op.drop_table('users_subscriptions')
    op.drop_index('ix_users_carts_id', table_name='users_carts')
    op.drop_table('users_carts')
    op.drop_constraint('services_price_id_fkey', 'services', type_='foreignkey')
    op.drop_column('services', 'price_id')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('services', sa.Column('price_id', sa.INTEGER(), autoincrement=False, nullable=True, comment='Идентификатор прайса услуги'))
    op.create_foreign_key('services_price_id_fkey', 'services', 'prices', ['price_id'], ['id'])
    op.create_table('users_carts',
    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('user_id', sa.INTEGER(), autoincrement=False, nullable=False, comment='Идентификатор пользователя'),
    sa.Column('service_id', sa.INTEGER(), autoincrement=False, nullable=False, comment='Идентификатор услуги'),
    sa.Column('doctor_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('price', sa.DOUBLE_PRECISION(precision=53), autoincrement=False, nullable=False, comment='Цена услуги'),
    sa.Column('discount', sa.INTEGER(), autoincrement=False, nullable=True, comment='Скидка на услугу'),
    sa.Column('amount_to_pay', sa.DOUBLE_PRECISION(precision=53), autoincrement=False, nullable=False, comment='Итоговая стоимость услуги к оплате'),
    sa.Column('needed_datetime', postgresql.TIMESTAMP(), autoincrement=False, nullable=True, comment='Желаемые для пользователя дата и время получения услуги'),
    sa.ForeignKeyConstraint(['doctor_id'], ['doctors.id'], name='users_carts_doctor_id_fkey'),
    sa.ForeignKeyConstraint(['service_id'], ['services.id'], name='users_carts_service_id_fkey'),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], name='users_carts_user_id_fkey'),
    sa.PrimaryKeyConstraint('id', name='users_carts_pkey'),
    comment='Таблица "Корзина пользователя"'
    )
    op.create_index('ix_users_carts_id', 'users_carts', ['id'], unique=False)
    op.create_table('users_subscriptions',
    sa.Column('id', sa.INTEGER(), server_default=sa.text("nextval('users_subscriptions_id_seq'::regclass)"), autoincrement=True, nullable=False),
    sa.Column('client_subscription_id', sa.INTEGER(), autoincrement=False, nullable=True, comment='Идентификатор абонемента пользователя в системе Клиента'),
    sa.Column('user_id', sa.INTEGER(), autoincrement=False, nullable=False, comment='Идентификатор пользователя'),
    sa.Column('description', sa.TEXT(), autoincrement=False, nullable=True, comment='Описание'),
    sa.Column('is_paid', sa.BOOLEAN(), autoincrement=False, nullable=True, comment='Флаг оплачен/не оплачен'),
    sa.Column('price', sa.DOUBLE_PRECISION(precision=53), autoincrement=False, nullable=False, comment='Цена абонемента'),
    sa.Column('common_discount', sa.INTEGER(), autoincrement=False, nullable=True, comment='Общая скидка на абонемент'),
    sa.Column('paid_amount', sa.DOUBLE_PRECISION(precision=53), autoincrement=False, nullable=False, comment='Опламенная сумма абонемента'),
    sa.Column('current_amount', sa.DOUBLE_PRECISION(precision=53), autoincrement=False, nullable=False, comment='Текущая неоплаченная сумма абонемента'),
    sa.Column('is_active', sa.BOOLEAN(), autoincrement=False, nullable=True, comment='Флаг активности абонемента - активный/не активный'),
    sa.Column('amount', sa.DOUBLE_PRECISION(precision=53), autoincrement=False, nullable=False, comment='Итоговая стоимость абонемента'),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], name='users_subscriptions_user_id_fkey'),
    sa.PrimaryKeyConstraint('id', name='users_subscriptions_pkey'),
    comment='Таблица "Абонементы пользователя"',
    postgresql_ignore_search_path=False
    )
    op.create_index('ix_users_subscriptions_id', 'users_subscriptions', ['id'], unique=False)
    op.create_table('users_subscriptions_items',
    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('user_subscription_id', sa.INTEGER(), autoincrement=False, nullable=False, comment='Идентификатор подписки пользователя'),
    sa.Column('service_id', sa.INTEGER(), autoincrement=False, nullable=False, comment='Идентификатор услуги'),
    sa.Column('price', sa.DOUBLE_PRECISION(precision=53), autoincrement=False, nullable=False, comment='Цена услуги'),
    sa.Column('discount', sa.INTEGER(), autoincrement=False, nullable=True, comment='Скидка на услугу'),
    sa.Column('amount', sa.DOUBLE_PRECISION(precision=53), autoincrement=False, nullable=False, comment='Итоговая стоимость услуги'),
    sa.Column('is_paid', sa.BOOLEAN(), autoincrement=False, nullable=True, comment='Флаг оплачена/не оплачена'),
    sa.Column('is_got', sa.BOOLEAN(), autoincrement=False, nullable=True, comment='Флаг получена/не получена'),
    sa.Column('is_active', sa.BOOLEAN(), autoincrement=False, nullable=True, comment='Флаг активности услуги - активная/не активная'),
    sa.ForeignKeyConstraint(['service_id'], ['services.id'], name='users_subscriptions_items_service_id_fkey'),
    sa.ForeignKeyConstraint(['user_subscription_id'], ['users_subscriptions.id'], name='users_subscriptions_items_user_subscription_id_fkey'),
    sa.PrimaryKeyConstraint('id', name='users_subscriptions_items_pkey'),
    comment='Таблица "Услуги в абонементе пользователя (состав абонемента пользователя)"'
    )
    op.create_index('ix_users_subscriptions_items_id', 'users_subscriptions_items', ['id'], unique=False)
    op.create_table('users_payments',
    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('payment_system_id', sa.INTEGER(), autoincrement=False, nullable=False, comment='Идентификатор платежной системы'),
    sa.Column('user_id', sa.INTEGER(), autoincrement=False, nullable=False, comment='Идентификатор пользователя'),
    sa.Column('service_id', sa.INTEGER(), autoincrement=False, nullable=False, comment='Идентификатор услуги'),
    sa.Column('doctor_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('payment_date', postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
    sa.Column('price', sa.DOUBLE_PRECISION(precision=53), autoincrement=False, nullable=False, comment='Цена услуги'),
    sa.Column('discount', sa.INTEGER(), autoincrement=False, nullable=True, comment='Скидка на услугу'),
    sa.Column('amount_to_pay', sa.DOUBLE_PRECISION(precision=53), autoincrement=False, nullable=False, comment='Итоговая стоимость услуги к оплате'),
    sa.Column('payment_amount', sa.DOUBLE_PRECISION(precision=53), autoincrement=False, nullable=False, comment='Оплаченная сумма'),
    sa.Column('payment_status', sa.INTEGER(), autoincrement=False, nullable=False, comment='Статус платежа'),
    sa.Column('payment_transaction_id', sa.INTEGER(), autoincrement=False, nullable=True, comment='Идентификатор платежя в платежной системе'),
    sa.ForeignKeyConstraint(['doctor_id'], ['doctors.id'], name='users_payments_doctor_id_fkey'),
    sa.ForeignKeyConstraint(['payment_system_id'], ['payments_systems.id'], name='users_payments_payment_system_id_fkey'),
    sa.ForeignKeyConstraint(['service_id'], ['services.id'], name='users_payments_service_id_fkey'),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], name='users_payments_user_id_fkey'),
    sa.PrimaryKeyConstraint('id', name='users_payments_pkey'),
    comment='Таблица "Платежи пользователя"'
    )
    op.create_index('ix_users_payments_id', 'users_payments', ['id'], unique=False)
    op.create_table('doctors_services',
    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('doctor_id', sa.INTEGER(), autoincrement=False, nullable=False, comment='Идентификатор доктора'),
    sa.Column('service_id', sa.INTEGER(), autoincrement=False, nullable=False, comment='Идентификатор услуги'),
    sa.Column('is_active', sa.BOOLEAN(), autoincrement=False, nullable=True, comment='Флаг активна/не активна'),
    sa.ForeignKeyConstraint(['doctor_id'], ['doctors.id'], name='doctors_services_doctor_id_fkey'),
    sa.ForeignKeyConstraint(['service_id'], ['services.id'], name='doctors_services_service_id_fkey'),
    sa.PrimaryKeyConstraint('id', name='doctors_services_pkey'),
    comment='Таблица-справочник "Услуги, оказываемые врачами"'
    )
    op.create_index('ix_doctors_services_id', 'doctors_services', ['id'], unique=False)
    op.create_table('documents_types',
    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('client_document_type_id', sa.INTEGER(), autoincrement=False, nullable=True, comment='Идентификатор типа документа в системе Клиента'),
    sa.Column('name', sa.VARCHAR(length=200), autoincrement=False, nullable=False, comment='Наименование документа'),
    sa.Column('description', sa.TEXT(), autoincrement=False, nullable=True, comment='Описание документа'),
    sa.Column('document_params', postgresql.JSON(astext_type=sa.Text()), autoincrement=False, nullable=True, comment='Обязательные параметры документа при его запросе'),
    sa.Column('is_online_allowed', sa.BOOLEAN(), autoincrement=False, nullable=True, comment='Флаг разрешен/неразрешен онлайн просмотр документа'),
    sa.Column('is_active', sa.BOOLEAN(), autoincrement=False, nullable=True, comment='Флаг активен/не активен'),
    sa.PrimaryKeyConstraint('id', name='documents_types_pkey'),
    sa.UniqueConstraint('name', name='documents_types_name_key'),
    comment='Таблица "Типы документов"'
    )
    op.create_index('ix_documents_types_id', 'documents_types', ['id'], unique=False)
    # ### end Alembic commands ###

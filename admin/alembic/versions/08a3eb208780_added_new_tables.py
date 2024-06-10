"""Added new tables

Revision ID: 08a3eb208780
Revises: fcc60905f490
Create Date: 2023-11-16 14:07:45.329760

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlalchemy_utils


# revision identifiers, used by Alembic.
revision: str = '08a3eb208780'
down_revision: Union[str, None] = 'fcc60905f490'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('doctor_statuses_types',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('client_dcategory_id', sa.Integer(), nullable=True, comment='Идентификатор типа статуса в системе клиента'),
    sa.Column('name', sa.String(length=100), nullable=False, comment='Наименование типа статуса'),
    sa.Column('description', sa.Text(), nullable=True, comment='Описание типа статуса'),
    sa.Column('is_active', sa.Boolean(), nullable=True, comment='Флаг активно/неактивно'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name'),
    comment='Таблица-справочник "Типы статусов доктора"'
    )
    op.create_index(op.f('ix_doctor_statuses_types_id'), 'doctor_statuses_types', ['id'], unique=False)
    op.create_table('doctors_categories',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('client_dcategory_id', sa.Integer(), nullable=True, comment='Идентификатор категории в системе клиента'),
    sa.Column('name', sa.String(length=100), nullable=False, comment='Наименование категории'),
    sa.Column('description', sa.Text(), nullable=True, comment='Описание категории'),
    sa.Column('is_active', sa.Boolean(), nullable=True, comment='Флаг активно/неактивно'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name'),
    comment='Таблица-справочник "Категории докторов"'
    )
    op.create_index(op.f('ix_doctors_categories_id'), 'doctors_categories', ['id'], unique=False)
    op.create_table('medical_positions',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('client_doctor_speciality_id', sa.Integer(), nullable=True, comment='Идентификатор должности в системе клиента'),
    sa.Column('view_name', sa.String(length=200), nullable=False, comment='Отображаемое наименование должности'),
    sa.Column('search_name', sa.String(length=200), nullable=False, comment='Поисковое наименование должности'),
    sa.Column('view_description', sa.Text(), nullable=True, comment='Отображаемое описание должности'),
    sa.Column('search_description', sa.Text(), nullable=True, comment='Поисковое описание должности'),
    sa.Column('is_active', sa.Boolean(), nullable=True, comment='Флаг активна/не активна'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('view_name'),
    comment='Таблица-справочник "Должности врачей"'
    )
    op.create_index(op.f('ix_medical_positions_id'), 'medical_positions', ['id'], unique=False)
    op.create_table('patients_types',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('client_patient_type_id', sa.Integer(), nullable=True, comment='Идентификатор типа пациента в системе клиента'),
    sa.Column('name', sa.String(length=100), nullable=False, comment='Наименование типа пациента'),
    sa.Column('description', sa.Text(), nullable=True, comment='Описание типа пациента'),
    sa.Column('is_active', sa.Boolean(), nullable=True, comment='Флаг активно/неактивно'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name'),
    comment='Таблица-справочник "Типы пациентов"'
    )
    op.create_index(op.f('ix_patients_types_id'), 'patients_types', ['id'], unique=False)
    op.create_table('staff_types',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('client_dcategory_id', sa.Integer(), nullable=True, comment='Идентификатор типа персонала в системе клиента'),
    sa.Column('name', sa.String(length=100), nullable=False, comment='Наименование типа персонала'),
    sa.Column('description', sa.Text(), nullable=True, comment='Описание типа персонала'),
    sa.Column('is_active', sa.Boolean(), nullable=True, comment='Флаг активно/неактивно'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name'),
    comment='Таблица-справочник "Типы персонала"'
    )
    op.create_index(op.f('ix_staff_types_id'), 'staff_types', ['id'], unique=False)
    op.create_table('doctors_medical_centers',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('client_doctor_mcenter_id', sa.Integer(), nullable=True, comment='Идентификатор доктора в медцентре в системе клиента'),
    sa.Column('doctor_id', sa.Integer(), nullable=False, comment='Идентификатор доктора'),
    sa.Column('medical_speciality_id', sa.Integer(), nullable=False, comment='Идентификатор медицинской специальности доктора'),
    sa.Column('medical_center_id', sa.Integer(), nullable=False, comment='Идентификатор медицинского центра'),
    sa.Column('medical_position_id', sa.Integer(), nullable=False, comment='Идентификатор должности доктора'),
    sa.Column('staff_type_id', sa.Integer(), nullable=False, comment='Идентификатор типа персонала'),
    sa.Column('show_in_lk', sa.Boolean(), nullable=True, comment='Флаг показывать/не показывать в личном кабинете'),
    sa.Column('minimal_age', sa.Integer(), nullable=False, comment='Минимальный возраст пациента'),
    sa.Column('maximal_age', sa.Integer(), nullable=False, comment='Максимальный возраст пациента'),
    sa.Column('is_active', sa.Boolean(), nullable=True, comment='Флаг активно/неактивно'),
    sa.ForeignKeyConstraint(['doctor_id'], ['doctors.id'], ),
    sa.ForeignKeyConstraint(['medical_center_id'], ['medical_centers.id'], ),
    sa.ForeignKeyConstraint(['medical_position_id'], ['medical_positions.id'], ),
    sa.ForeignKeyConstraint(['medical_speciality_id'], ['medical_specialities.id'], ),
    sa.ForeignKeyConstraint(['staff_type_id'], ['staff_types.id'], ),
    sa.PrimaryKeyConstraint('id'),
    comment='Таблица-справочник "Доктора в медцентрах"'
    )
    op.create_index(op.f('ix_doctors_medical_centers_id'), 'doctors_medical_centers', ['id'], unique=False)
    op.create_table('doctors_statuses',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('doctor_id', sa.Integer(), nullable=False, comment='Идентификатор доктора'),
    sa.Column('status_type_id', sa.Integer(), nullable=False, comment='Идентификатор типа статуса доктора'),
    sa.Column('start_date', sa.DateTime(), nullable=False, comment='Начальная дата периода действия статуса'),
    sa.Column('end_date', sa.DateTime(), nullable=False, comment='Конечная дата периода действия статуса'),
    sa.ForeignKeyConstraint(['doctor_id'], ['doctors.id'], ),
    sa.ForeignKeyConstraint(['status_type_id'], ['doctor_statuses_types.id'], ),
    sa.PrimaryKeyConstraint('id'),
    comment='Таблица "Статусы докторов"'
    )
    op.create_index(op.f('ix_doctors_statuses_id'), 'doctors_statuses', ['id'], unique=False)
    op.create_table('doctors_patients_types',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('client_dpatient_type_id', sa.Integer(), nullable=True, comment='Идентификатор типа пауцента для данного доктора в системе клиента'),
    sa.Column('doctor_medical_center_id', sa.Integer(), nullable=False, comment='Идентификатор типа статуса доктора'),
    sa.Column('patient_type_id', sa.Integer(), nullable=False, comment='Идентификатор типа пациента'),
    sa.Column('start_date', sa.DateTime(), nullable=False, comment='Начальная дата периода действия разрешения работать с данным питом пациента'),
    sa.Column('end_date', sa.DateTime(), nullable=False, comment='Конечная дата периода действия разрешения работать с данным питом пациента'),
    sa.Column('is_active', sa.Boolean(), nullable=True, comment='Флаг активно/неактивно'),
    sa.ForeignKeyConstraint(['doctor_medical_center_id'], ['doctors_medical_centers.id'], ),
    sa.ForeignKeyConstraint(['patient_type_id'], ['patients_types.id'], ),
    sa.PrimaryKeyConstraint('id'),
    comment='Таблица "Разрешенные доктору типы пациентов"'
    )
    op.create_index(op.f('ix_doctors_patients_types_id'), 'doctors_patients_types', ['id'], unique=False)
    op.drop_constraint('doctors_medical_department_id_fkey', 'doctors', type_='foreignkey')
    op.drop_column('doctors', 'medical_department_id')
    op.drop_constraint('prices_medical_department_id_fkey', 'prices', type_='foreignkey')
    op.drop_column('prices', 'medical_department_id')
    op.drop_index('ix_mcenters_mdepartments_id', table_name='mcenters_mdepartments')
    op.drop_table('mcenters_mdepartments')
    op.drop_index('ix_medical_departments_id', table_name='medical_departments')
    op.drop_table('medical_departments')
    op.add_column('doctors', sa.Column('first_name', sa.String(length=100), nullable=False, comment='Имя доктора'))
    op.add_column('doctors', sa.Column('last_name', sa.String(length=100), nullable=False, comment='Фамилия доктора'))
    op.add_column('doctors', sa.Column('patronymic', sa.String(length=100), nullable=True, comment='Отчество доктора (если есть)'))
    op.add_column('doctors', sa.Column('birth_date', sa.Date(), nullable=True, comment='Дата рождения доктора'))
    op.add_column('doctors', sa.Column('doctor_category_id', sa.Integer(), nullable=True, comment='Идентификатор категории доктора'))
    op.add_column('doctors', sa.Column('private_phone', sa.String(length=25), nullable=True, comment='Личный телефон доктора'))
    op.add_column('doctors', sa.Column('work_phone', sa.String(length=25), nullable=True, comment='Рабочий телефон доктора'))
    op.add_column('doctors', sa.Column('email', sa.String(length=200), nullable=True, comment='Электронная почта доктора'))
    op.add_column('doctors', sa.Column('common_experience', sa.Integer(), nullable=True, comment='Общий медицинский стаж доктора'))
    op.create_unique_constraint(None, 'doctors', ['private_phone'])
    op.drop_constraint('doctors_medical_center_id_fkey', 'doctors', type_='foreignkey')
    op.create_foreign_key(None, 'doctors', 'doctors_categories', ['doctor_category_id'], ['id'])
    op.drop_column('doctors', 'fio')
    op.drop_column('doctors', 'description')
    op.drop_column('doctors', 'medical_center_id')
    op.alter_column('medical_centers', 'city_id',
               existing_type=sa.INTEGER(),
               nullable=False,
               existing_comment='Идентификатор города')
    op.add_column('medical_specialities', sa.Column('view_name', sa.String(length=200), nullable=False, comment='Отображаемое наименование специальности'))
    op.add_column('medical_specialities', sa.Column('search_name', sa.String(length=200), nullable=False, comment='Поисковое наименование специальности'))
    op.add_column('medical_specialities', sa.Column('view_description', sa.Text(), nullable=True, comment='Отображаемое описание специальности'))
    op.add_column('medical_specialities', sa.Column('search_description', sa.Text(), nullable=True, comment='Поисковое описание специальности'))
    op.drop_constraint('medical_specialities_name_key', 'medical_specialities', type_='unique')
    op.create_unique_constraint(None, 'medical_specialities', ['view_name'])
    op.drop_column('medical_specialities', 'description')
    op.drop_column('medical_specialities', 'name')
    op.alter_column('users', 'email',
               existing_type=sa.VARCHAR(length=100),
               type_=sa.String(length=200),
               existing_comment='Электронная почта пользователя',
               existing_nullable=True)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('users', 'email',
               existing_type=sa.String(length=200),
               type_=sa.VARCHAR(length=100),
               existing_comment='Электронная почта пользователя',
               existing_nullable=True)
    op.add_column('prices', sa.Column('medical_department_id', sa.INTEGER(), autoincrement=False, nullable=True, comment='Идентификатор департамента'))
    op.create_foreign_key('prices_medical_department_id_fkey', 'prices', 'medical_departments', ['medical_department_id'], ['id'])
    op.add_column('medical_specialities', sa.Column('name', sa.VARCHAR(length=200), autoincrement=False, nullable=False, comment='Наименование специальности'))
    op.add_column('medical_specialities', sa.Column('description', sa.TEXT(), autoincrement=False, nullable=True, comment='Описание специальности'))
    op.drop_constraint(None, 'medical_specialities', type_='unique')
    op.create_unique_constraint('medical_specialities_name_key', 'medical_specialities', ['name'])
    op.drop_column('medical_specialities', 'search_description')
    op.drop_column('medical_specialities', 'view_description')
    op.drop_column('medical_specialities', 'search_name')
    op.drop_column('medical_specialities', 'view_name')
    op.alter_column('medical_centers', 'city_id',
               existing_type=sa.INTEGER(),
               nullable=True,
               existing_comment='Идентификатор города')
    op.add_column('doctors', sa.Column('medical_center_id', sa.INTEGER(), autoincrement=False, nullable=False, comment='Идентификатор медицинского центра'))
    op.add_column('doctors', sa.Column('description', sa.TEXT(), autoincrement=False, nullable=True, comment='Описание доктора'))
    op.add_column('doctors', sa.Column('fio', sa.VARCHAR(length=300), autoincrement=False, nullable=False, comment='ФИО доктора'))
    op.add_column('doctors', sa.Column('medical_department_id', sa.INTEGER(), autoincrement=False, nullable=True, comment='Идентификатор медицинского департемента'))
    op.drop_constraint(None, 'doctors', type_='foreignkey')
    op.create_foreign_key('doctors_medical_department_id_fkey', 'doctors', 'medical_departments', ['medical_department_id'], ['id'])
    op.create_foreign_key('doctors_medical_center_id_fkey', 'doctors', 'medical_centers', ['medical_center_id'], ['id'])
    op.drop_constraint(None, 'doctors', type_='unique')
    op.drop_column('doctors', 'common_experience')
    op.drop_column('doctors', 'email')
    op.drop_column('doctors', 'work_phone')
    op.drop_column('doctors', 'private_phone')
    op.drop_column('doctors', 'doctor_category_id')
    op.drop_column('doctors', 'birth_date')
    op.drop_column('doctors', 'patronymic')
    op.drop_column('doctors', 'last_name')
    op.drop_column('doctors', 'first_name')
    op.create_table('medical_departments',
    sa.Column('id', sa.INTEGER(), server_default=sa.text("nextval('medical_departments_id_seq'::regclass)"), autoincrement=True, nullable=False),
    sa.Column('client_department_id', sa.INTEGER(), autoincrement=False, nullable=True, comment='Идентификатор департамента в системе клиента'),
    sa.Column('name', sa.VARCHAR(length=200), autoincrement=False, nullable=False, comment='Наименование департамента'),
    sa.Column('description', sa.TEXT(), autoincrement=False, nullable=True, comment='Описание департамента'),
    sa.Column('is_active', sa.BOOLEAN(), autoincrement=False, nullable=True, comment='Флаг активен/не активен'),
    sa.PrimaryKeyConstraint('id', name='medical_departments_pkey'),
    sa.UniqueConstraint('name', name='medical_departments_name_key'),
    comment='Таблица-справочник "Медицинские департаменты"',
    postgresql_ignore_search_path=False
    )
    op.create_index('ix_medical_departments_id', 'medical_departments', ['id'], unique=False)
    op.create_table('mcenters_mdepartments',
    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('medical_center_id', sa.INTEGER(), autoincrement=False, nullable=False, comment='Идентификатор медицинского центра'),
    sa.Column('medical_department_id', sa.INTEGER(), autoincrement=False, nullable=False, comment='Идентификатор медицинского депртамент'),
    sa.Column('description', sa.TEXT(), autoincrement=False, nullable=True, comment='Описание конкретного департамента в конкретном медицинском центре'),
    sa.Column('is_active', sa.BOOLEAN(), autoincrement=False, nullable=True, comment='Флаг активен/не активен'),
    sa.ForeignKeyConstraint(['medical_center_id'], ['medical_centers.id'], name='mcenters_mdepartments_medical_center_id_fkey'),
    sa.ForeignKeyConstraint(['medical_department_id'], ['medical_departments.id'], name='mcenters_mdepartments_medical_department_id_fkey'),
    sa.PrimaryKeyConstraint('id', name='mcenters_mdepartments_pkey'),
    comment='Таблица-справочник "Департаменты медицинских центров"'
    )
    op.create_index('ix_mcenters_mdepartments_id', 'mcenters_mdepartments', ['id'], unique=False)
    op.drop_index(op.f('ix_doctors_patients_types_id'), table_name='doctors_patients_types')
    op.drop_table('doctors_patients_types')
    op.drop_index(op.f('ix_doctors_statuses_id'), table_name='doctors_statuses')
    op.drop_table('doctors_statuses')
    op.drop_index(op.f('ix_doctors_medical_centers_id'), table_name='doctors_medical_centers')
    op.drop_table('doctors_medical_centers')
    op.drop_index(op.f('ix_staff_types_id'), table_name='staff_types')
    op.drop_table('staff_types')
    op.drop_index(op.f('ix_patients_types_id'), table_name='patients_types')
    op.drop_table('patients_types')
    op.drop_index(op.f('ix_medical_positions_id'), table_name='medical_positions')
    op.drop_table('medical_positions')
    op.drop_index(op.f('ix_doctors_categories_id'), table_name='doctors_categories')
    op.drop_table('doctors_categories')
    op.drop_index(op.f('ix_doctor_statuses_types_id'), table_name='doctor_statuses_types')
    op.drop_table('doctor_statuses_types')
    # ### end Alembic commands ###

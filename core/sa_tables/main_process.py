from datetime import datetime
from sqlalchemy import (Column, String, Integer, ForeignKey, Float, Text, Boolean, DateTime,
                        Sequence, Date, BigInteger, Index, func)
from sqlalchemy.orm import relationship, backref

from ..config.db import Base
from core.sa_tables.accounts import UserTable, LpuTable, MedicalCenterTable


id_seq = Sequence('nodes_id_seq')


class BaseNameDescriptionTable(Base):

    __abstract__ = True

    id = Column(Integer,
                primary_key=True,
                index=True)
    name = Column(String(200), nullable=False,
                  comment='Наименование')
    description = Column(Text, nullable=True,
                         comment='Описание')
    is_active = Column(Boolean, default=True,
                       comment='Флаг активно/неактивно')


class ServiceGroupTable(Base):
    """Модель ServiceGroup утвержденная"""

    __tablename__ = 'services_groups'
    __table_args__ = {
        'comment': 'Таблица-справочник "Прейскурант услуг". Содержит древовидную струтктуру'
    }

    id = Column(Integer, id_seq, primary_key=True)
    client_id = Column(BigInteger, nullable=True, index=True, unique=True,
                       comment='Идентификатор узла прейкуранта в системе клиента')
    name = Column(String(200), nullable=False,
                  comment='Наименование узла прейскуранта')
    view_name = Column(String, nullable=True,
                       comment='Отображаемое наименование узла прейскуранта')
    description = Column(Text, nullable=True,
                         comment='Описание узла прейскуранта')
    path = Column(String, nullable=False, index=True,
                  comment='путь в дереве, начиная от корня вида "ud.id.id...id", где id идентификатор узла в таблице services_groups. Самая правая метка в path - это id самого узла. Перед ним - id родителя.')
    client_service_group_code = Column(String(100), nullable=True,
                                       comment='Код раздела прейскуранта для нужд администрирования')
    level_sorting_code = Column(Integer, nullable=True,
                                comment='Числовой код для произвольно сортировки узла в рамках уровня, в котором узел расположен')
    is_active = Column(Boolean, default=True,
                       comment='Флаг активный/не активный')


    def __str__(self):
        return self.name

    def __repr__(self):
        return 'ServiceGroupTable({})'.format(self.name)


class MedicalSpecialityTable(Base):
    """Модель MedicalSpeciality утвержденная"""

    __tablename__ = "medical_specialities"
    __table_args__ = {
        'comment': 'Таблица-справочник "Специальности врачей"'
    }

    id = Column(Integer,
                primary_key=True,
                index=True)
    client_id = Column(BigInteger, nullable=True, index=True, unique=True,
                       comment='Идентификатор специальности в системе клиента')
    view_name = Column(String(200), nullable=False,
                       comment='Отображаемое наименование специальности')
    search_name = Column(String(200), nullable=False,
                         comment='Поисковое наименование специальности')
    view_description = Column(Text, nullable=True,
                              comment='Отображаемое описание специальности')
    search_description = Column(Text, nullable=True,
                                comment='Поисковое описание специальности')
    is_active = Column(Boolean, default=True,
                       comment='Флаг активна/не активна')


class MedicalPositionTable(Base):
    """Модель MedicalPosition утвержденная"""

    __tablename__ = "medical_positions"
    __table_args__ = {
        'comment': 'Таблица-справочник "Должности врачей"'
    }

    id = Column(Integer,
                primary_key=True,
                index=True)
    client_id = Column(BigInteger, nullable=True, index=True, unique=True,
                       comment='Идентификатор должности в системе клиента')
    view_name = Column(String(200), nullable=False,
                       comment='Отображаемое наименование должности')
    search_name = Column(String(200), nullable=False,
                         comment='Поисковое наименование должности')
    view_description = Column(Text, nullable=True,
                              comment='Отображаемое описание должности')
    search_description = Column(Text, nullable=True,
                                comment='Поисковое описание должности')
    is_active = Column(Boolean, default=True,
                       comment='Флаг активна/не активна')


class StaffTypeTable(Base):
    """Модель StaffType утвержденная"""

    __tablename__ = "staff_types"
    __table_args__ = {
        'comment': 'Таблица-справочник "Типы персонала"'
    }

    id = Column(Integer,
                primary_key=True,
                index=True)
    client_id = Column(BigInteger, nullable=True, index=True, unique=True,
                       comment='Идентификатор типа персонала в системе клиента')
    name = Column(String(100), nullable=False, unique=True,
                  comment='Наименование типа персонала')
    description = Column(Text, nullable=True,
                         comment='Описание типа персонала')
    is_active = Column(Boolean, default=True,
                       comment='Флаг активно/неактивно')


class DoctorCategoryTable(Base):
    """Модель DoctorCategory утвержденная"""

    __tablename__ = "doctors_categories"
    __table_args__ = {
        'comment': 'Таблица-справочник "Категории докторов"'
    }

    id = Column(Integer,
                primary_key=True,
                index=True)
    client_id = Column(BigInteger, nullable=True, index=True, unique=True,
                       comment='Идентификатор категории в системе клиента')
    name = Column(String(100), nullable=False, unique=True,
                  comment='Наименование категории')
    description = Column(Text, nullable=True,
                         comment='Описание категории')
    is_active = Column(Boolean, default=True,
                       comment='Флаг активно/неактивно')


class DoctorTable(Base):
    """Модель Doctor утвержденная"""

    __tablename__ = "doctors"
    __table_args__ = {
        'comment': 'Таблица-справочник "Врачи"'
    }

    id = Column(Integer,
                primary_key=True,
                index=True)
    client_id = Column(BigInteger, nullable=True, index=True, unique=True,
                       comment='Идентификатор доктора в системе клиента')
    first_name = Column(String(100), nullable=False,
                        comment='Имя доктора')
    last_name = Column(String(100), nullable=False,
                       comment='Фамилия доктора')
    patronymic = Column(String(100), nullable=True,
                        comment='Отчество доктора (если есть)')
    birth_date = Column(Date, nullable=True,
                        comment='Дата рождения доктора')
    photo = Column(String(200), nullable=True,
                   comment='Фотография доктора')
    doctor_category_id = Column(Integer, ForeignKey('doctors_categories.id'), nullable=True,
                                comment='Идентификатор категории доктора')
    private_phone = Column(String(25), nullable=True,
                           comment='Личный телефон доктора')
    work_phone = Column(String(25), nullable=True,
                        comment='Рабочий телефон доктора')
    email = Column(String(200), nullable=True,
                   comment='Электронная почта доктора')
    common_experience = Column(Integer, nullable=True,
                               comment='Общий медицинский стаж доктора')
    is_active = Column(Boolean, default=True,
                       comment='Флаг активен/не активен')

    doctor_category = relationship('DoctorCategoryTable', lazy='joined')

    def fio(self):
        """Получение ФИО доктора"""
        doctor_fio = ''
        if self.last_name:
            self.last_name = self.last_name.capitalize()
            doctor_fio += f'{self.last_name} '
        if self.first_name:
            self.first_name = self.first_name.capitalize()
            doctor_fio += f'{self.first_name} '
        if self.patronymic:
            self.patronymic = self.patronymic.capitalize()
            doctor_fio += f'{self.patronymic}'
        return doctor_fio.strip()



class DoctorStatusTypeTable(Base):
    """Модель DoctorStatusType утвержденная"""

    __tablename__ = "doctor_statuses_types"
    __table_args__ = {
        'comment': 'Таблица-справочник "Типы статусов доктора"'
    }

    id = Column(Integer,
                primary_key=True,
                index=True)
    client_id = Column(BigInteger, nullable=True, index=True, unique=True,
                       comment='Идентификатор типа статуса в системе клиента')
    name = Column(String(100), nullable=False, unique=True,
                  comment='Наименование типа статуса')
    description = Column(Text, nullable=True,
                         comment='Описание типа статуса')
    is_active = Column(Boolean, default=True,
                       comment='Флаг активно/неактивно')


class DoctorStatusTable(Base):
    """Модель DoctorStatus утвержденная"""

    __tablename__ = "doctors_statuses"
    __table_args__ = {
        'comment': 'Таблица "Статусы докторов"'
    }

    id = Column(Integer,
                primary_key=True,
                index=True)
    doctor_id = Column(Integer, ForeignKey('doctors.id'), nullable=False,
                       comment='Идентификатор доктора')
    status_type_id = Column(Integer, ForeignKey('doctor_statuses_types.id'), nullable=False,
                            comment='Идентификатор типа статуса доктора')
    start_date = Column(DateTime, nullable=False,
                        comment='Начальная дата периода действия статуса')
    end_date = Column(DateTime, nullable=False,
                      comment='Конечная дата периода действия статуса')

    doctor = relationship('DoctorTable', lazy='joined')
    status_type = relationship('DoctorStatusTypeTable', lazy='joined')


class PatientTypeTable(Base):
    """Модель PatientType утвержденная"""

    __tablename__ = "patients_types"
    __table_args__ = {
        'comment': 'Таблица-справочник "Типы пациентов"'
    }

    id = Column(Integer,
                primary_key=True,
                index=True)
    client_id = Column(BigInteger, nullable=True, index=True, unique=True,
                       comment='Идентификатор типа пациента в системе клиента')
    name = Column(String(100), nullable=False, unique=True,
                  comment='Наименование типа пациента')
    description = Column(Text, nullable=True,
                         comment='Описание типа пациента')
    is_active = Column(Boolean, default=True,
                       comment='Флаг активно/неактивно')


class DoctorMedicalCenterTable(Base):
    """Модель DoctorMedicalCenter утвержденная"""

    __tablename__ = "doctors_medical_centers"
    __table_args__ = {
        'comment': 'Таблица-справочник "Доктора в медцентрах"'
    }

    id = Column(Integer,
                primary_key=True,
                index=True)
    client_id = Column(BigInteger, nullable=True, index=True, unique=True,
                       comment='Идентификатор доктора в медцентре в системе клиента')
    doctor_id = Column(Integer, ForeignKey('doctors.id'), nullable=False,
                                   comment='Идентификатор доктора')
    medical_speciality_id = Column(Integer, ForeignKey('medical_specialities.id'), nullable=False,
                                   comment='Идентификатор медицинской специальности доктора')
    medical_center_id = Column(Integer, ForeignKey('medical_centers.id'), nullable=False,
                               comment='Идентификатор медицинского центра')
    medical_position_id = Column(Integer, ForeignKey('medical_positions.id'), nullable=False,
                                 comment='Идентификатор должности доктора')
    staff_type_id = Column(Integer, ForeignKey('staff_types.id'), nullable=False,
                           comment='Идентификатор типа персонала')
    show_in_lk = Column(Boolean, default=True,
                        comment='Флаг показывать/не показывать в личном кабинете')
    minimal_age = Column(Integer, nullable=False,
                         comment='Минимальный возраст пациента')
    maximal_age = Column(Integer, nullable=False,
                         comment='Максимальный возраст пациента')
    is_active = Column(Boolean, default=True,
                       comment='Флаг активно/неактивно')

    doctor = relationship('DoctorTable', lazy='joined')
    medical_speciality = relationship('MedicalSpecialityTable', lazy='joined')
    medical_center = relationship('MedicalCenterTable', lazy='joined')
    medical_position = relationship('MedicalPositionTable', lazy='joined')
    staff_type = relationship('StaffTypeTable', lazy='joined')

    def __str__(self):
        return f'{self.doctor.last_name} {self.doctor.first_name} {self.doctor.patronymic}'


class DoctorPatientTypeTable(Base):
    """Модель DoctorPatientType утвержденная"""

    __tablename__ = "doctors_patients_types"
    __table_args__ = {
        'comment': 'Таблица "Разрешенные доктору типы пациентов"'
    }

    id = Column(Integer,
                primary_key=True,
                index=True)
    client_id = Column(BigInteger, nullable=True, index=True, unique=True,
                       comment='Идентификатор типа пауцента для данного доктора в системе клиента')
    doctor_medical_center_id = Column(Integer, ForeignKey('doctors_medical_centers.id'), nullable=False,
                                      comment='Идентификатор типа статуса доктора')
    patient_type_id = Column(Integer, ForeignKey('patients_types.id'), nullable=False,
                                                  comment='Идентификатор типа пациента')
    start_date = Column(DateTime, nullable=False,
                        comment='Начальная дата периода действия разрешения работать с данным типом пациента')
    end_date = Column(DateTime, nullable=False,
                      comment='Конечная дата периода действия разрешения работать с данным типом пациента')
    is_active = Column(Boolean, default=True,
                       comment='Флаг активно/неактивно')

    doctor_medical_center = relationship('DoctorMedicalCenterTable', lazy='joined')
    patient_type = relationship('PatientTypeTable', lazy='joined')


class ServiceTypeTable(Base):
    """Модель ServiceType утвержденная"""

    __tablename__ = "services_types"
    __table_args__ = {
        'comment': 'Таблица-справочник "Типы услуг"'
    }

    id = Column(Integer,
                primary_key=True,
                index=True)
    client_id = Column(BigInteger, nullable=True, index=True, unique=True,
                       comment='Идентификатор типа услуги на стороне клиента')
    name = Column(String(200), nullable=False, unique=True,
                  comment='Наименование типа услуг')
    description = Column(Text, nullable=True,
                         comment='Описание типа.')
    is_active = Column(Boolean, default=True,
                       comment='Флаг активна/не активна')


class ServiceTable(Base):
    """Модель Service утвержденная"""

    __tablename__ = "services"
    __table_args__ = {
        'comment': 'Таблица-справочник "Услуги"'
    }

    id = Column(Integer,
                primary_key=True,
                index=True)
    client_id = Column(BigInteger, nullable=True, index=True, unique=True,
                       comment='Идентификатор услуги в системе Клиента')
    service_type_id = Column(Integer, ForeignKey('services_types.id'), nullable=False,
                             comment='Идентификатор типа услуги')
    service_group_id = Column(Integer, ForeignKey('services_groups.id'), nullable=False,
                              comment='Идентификатор группы прейскуранта')
    name_for_staff = Column(String(512), nullable=False,
                            comment='Наименование услуги для персонала')
    name_for_mz = Column(String(512), nullable=False,
                         comment='Наименование услуги для минздрава')
    name_for_lk = Column(String(512), nullable=False,
                         comment='Наименование услуги для личного кабинета')
    full_description = Column(Text, nullable=True,
                              comment='Полное описание')
    applied_method = Column(Text, nullable=True,
                            comment='Применяемый метод')
    preparation_rules = Column(Text, nullable=True,
                               comment='Правила подготовки')
    short_description = Column(String(500), nullable=True,
                               comment='Короткое описание')
    comment = Column(Text, nullable=True,
                     comment='Комментарий')
    mz_code = Column(String(50), nullable=True,
                     comment='Код минздрава')
    execution_time = Column(Integer, nullable=True,
                            comment='Время выполнения в целых минутах')
    nurses_execution_time = Column(Integer, nullable=True,
                                   comment='Время выполнения младшим медицинским персоналом в целых минутах')
    minimal_age = Column(Integer, nullable=True,
                         comment='Минимальный возраст пациента')
    maximal_age = Column(Integer, nullable=True,
                         comment='Максимальный возраст пациента')
    gender = Column(String(1), nullable=True,
                    comment='Пол пользователя')
    is_urgent = Column(Boolean, nullable=True,
                       comment='Флаг срочная/не срочная')
    is_for_home_only = Column(Boolean, nullable=True,
                       comment='Флаг домашняя/недомашняя')
    selected_service_notification = Column(Text, nullable=True,
                                           comment='Текст уведомления при выбранной услуге')
    is_complex_service = Column(Boolean, nullable=True,
                                comment='Флаг комплексная/некомплексная')
    client_service_code = Column(String(100), nullable=True,
                                 comment='Буквенноцифровой код услуги в системе клиента')
    is_active = Column(Boolean, default=True,
                       comment='Флаг активна/не активна')
    is_plan_checking = Column(Boolean, default=True,
                              comment='Флаг проверять планируемые/не проверять планируемые')
    checking_interval = Column(Integer, nullable=True,
                               comment='Интервал проверки +- checking_interval дней')

    service_type = relationship('ServiceTypeTable', lazy='joined')
    service_group = relationship('ServiceGroupTable', lazy='joined')

    def __str__(self):
        return self.name_for_lk


class DoctorMspecialityTable(Base):
    """Модель DoctorMspeciality - врачи со специальностями, утвержденная"""

    __tablename__ = 'docrors_mspecialities'
    __table_args__ = {
        'comment': 'Таблица-справочник "Врачи со специальностями"'
    }

    id = Column(Integer,
                primary_key=True,
                index=True)
    doctor_id = Column(Integer, ForeignKey('doctors.id'), nullable=False,
                       comment='Идентификатор доктора')
    mspeciality_id = Column(Integer, ForeignKey('medical_specialities.id'), nullable=False,
                            comment='Идентификатор медицинской специальности')
    is_active = Column(Boolean, default=True,
                       comment='Флаг активна/не активна')

    doctor = relationship('DoctorTable', lazy='joined')
    mspeciality = relationship(MedicalSpecialityTable, lazy='joined')


class ServiceMedicalSpecialityTable(Base):
    """Модель ServiceMedicalSpeciality утвержденная"""

    __tablename__ = 'services_mspecialities'
    __table_args__ = {
        'comment': 'Таблица-справочник "Услуги со специальностями"'
    }

    id = Column(Integer,
                primary_key=True,
                index=True)
    client_id = Column(BigInteger, nullable=True, index=True, unique=True,
                       comment='Идентификатор услуги в системе Клиента')
    service_id = Column(Integer, ForeignKey('services.id'), nullable=False,
                        comment='Идентификатор услуги')
    medical_speciality_id = Column(Integer, ForeignKey('medical_specialities.id'), nullable=False,
                                   comment='Идентификатор медицинской специальности')
    is_active = Column(Boolean, default=True,
                       comment='Флаг активна/не активна')

    service = relationship('ServiceTable', lazy='joined')
    medical_speciality = relationship('MedicalSpecialityTable', lazy='joined')


class ComplexServiceTable(Base):
    """Модель ComplexService утвержденная"""

    __tablename__ = 'complex_services'
    __table_args__ = {
        'comment': 'Таблица "Комплексные услуги"'
    }

    id = Column(Integer,
                primary_key=True,
                index=True)
    client_id = Column(BigInteger, nullable=True, index=True, unique=True,
                       comment='Идентификатор услуги в системе Клиента')
    service_id = Column(Integer, ForeignKey('services.id'), nullable=False,
                        comment='Идентификатор услуги')
    description = Column(Text, nullable=True,
                         comment='Описание комплексной услуги')
    is_active = Column(Boolean, default=True,
                       comment='Флаг активна/не активна')

    service = relationship('ServiceTable', lazy='joined')


class ComplexServiceItemTable(Base):
    """Модель ComplexServiceItem утвержденная"""

    __tablename__ = 'complex_services_items'
    __table_args__ = {
        'comment': 'Таблица "Элементы комплексных услуг"'
    }

    id = Column(Integer,
                primary_key=True,
                index=True)
    complex_service_id = Column(Integer, ForeignKey('complex_services.id'), nullable=False,
                                comment='Идентификатор услуги')
    service_id = Column(Integer, ForeignKey('services.id'), nullable=False,
                        comment='Идентификатор услуги')
    comment = Column(Text, nullable=True,
                     comment='Комментарий')
    price = Column(Float, nullable=True,
                   comment='Цена элемента комплексной услуги')
    quantity = Column(Integer, nullable=False, default=1,
                      comment='Количество входящей услуги')
    coefficient_to_price = Column(Float, nullable=True, default=1.0,
                                  comment='Цена элемента комплексной услуги')
    is_active = Column(Boolean, default=True,
                       comment='Флаг активна/не активна')

    complex_service = relationship('ComplexServiceTable', lazy='joined')
    service = relationship('ServiceTable', lazy='joined')


class FinancialTypeTable(BaseNameDescriptionTable):
    """Модель FinancialType - финансовый тип. Утвержденная"""

    __tablename__ = 'financial_types'
    __table_args__ = {
        'comment': 'Таблица "Финансовые типы"'
    }

    client_id = Column(BigInteger, nullable=True, index=True, unique=True,
                       comment='Идентификатор финансового типа в системе клиента')
    name = Column(String(200), nullable=False, unique=True,
                  comment='Наименование финансового типа')


class ShifrTable(Base):
    """Модель Shifr - шифр. Утвержденная"""

    __tablename__ = 'shifrs'
    __table_args__ = {
        'comment': 'Таблица "Шифры"'
    }

    id = Column(Integer,
                primary_key=True,
                index=True)
    client_id = Column(BigInteger, nullable=True, index=True, unique=True,
                       comment='Идентификатор шифра в системе клиента')
    code = Column(String(100), nullable=True,
                  comment='Буквенноцифровой код Шифра в системе клиента')
    name = Column(String(200), nullable=True,
                  comment='Наименование шифра в системе клиента')
    company_name = Column(String(200), nullable=True,
                          comment='Наименование компании в системе клиента')
    start_date = Column(DateTime, nullable=False,
                        comment='Начальная дата периода действия шифра')
    end_date = Column(DateTime, nullable=False,
                      comment='Конечная дата периода действия шифра')
    financial_type_id = Column(Integer, ForeignKey('financial_types.id'), nullable=False,
                               comment='Идентификатор финансового типа шифра')
    is_active = Column(Boolean, default=True,
                       comment='Флаг активна/не активна')

    financial_type = relationship('FinancialTypeTable', lazy='joined')


class PolicyTable(Base):
    """Модель Policy - полис. Утвержденная"""

    __tablename__ = 'policies'
    __table_args__ = {
        'comment': 'Таблица "Полисы"'
    }

    id = Column(Integer,
                primary_key=True,
                index=True)

    client_id = Column(BigInteger, nullable=True, index=True, unique=True,
                       comment='Идентификатор полиса в системе клиента')
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False,
                     comment='Идентификатор пользователя')
    shifr_id = Column(Integer, ForeignKey('shifrs.id'), nullable=False,
                      comment='Идентификатор шифра')
    start_date = Column(DateTime, nullable=True,
                        comment='Начальная дата периода действия полиса')
    end_date = Column(DateTime, nullable=True,
                      comment='Конечная дата периода действия полиса')
    status = Column(Integer, nullable=False,
                    comment='Статус полиса')
    series = Column(String(50), nullable=True,
                            comment='Серия полиса')
    number = Column(String(100), nullable=True,
                    comment='Номер полиса')
    contract_date = Column(DateTime, nullable=True,
                            comment='Дата выдачи полиса')
    price = Column(Float, nullable=True,
                    comment="Цена полиса")
    discount = Column(Float, nullable=True,
                        comment='Скидка на полис')
    discount_coefficient = Column(Float, nullable=True,
                                    comment='Коэффициент на скидку')
    amount = Column(Float, nullable=True,
                    comment="Итоговая стоимость полиса")
    current_paid = Column(Float, nullable=True,
                    comment="Текущая оплаченная сумма")
    is_active = Column(Boolean, default=True,
                        comment='Флаг активна/не активна')
    medical_center_id = Column(Integer, ForeignKey('medical_centers.id'), nullable=True,
                               comment='Идентификатор медицинского центра')

    user = relationship('UserTable', lazy='joined')
    shifr = relationship('ShifrTable', lazy='joined')
    medical_center = relationship('MedicalCenterTable', lazy='joined')


class UserSubscribeTable(BaseNameDescriptionTable):
    """Модель UserSubscribe - абонемент пользователя. Утвержденная"""

    __tablename__ = 'users_subscribes'
    __table_args__ = {
        'comment': 'Таблица "Абонементы пользователя"'
    }

    id = Column(Integer,
                primary_key=True,
                index=True)

    client_id = Column(BigInteger, nullable=True, index=True, unique=True,
                       comment='Идентификатор абонемента пользователя в системе клиента')
    policy_id = Column(Integer, ForeignKey('policies.id'), nullable=False,
                       comment='Идентификатор полиса')
    service_id = Column(Integer, ForeignKey('services.id'), nullable=False,
                       comment='Идентификатор услуги')

    policy = relationship('PolicyTable', lazy='joined')
    service = relationship('ServiceTable', lazy='joined')


class DoctorReplacementTable(Base):
    """Модель DoctorReplacement. Утверждженная"""

    __tablename__ = 'doctors_replacements'
    __table_args__ = {
        'comment': 'Таблица "Подмены докторов на абонементах"'
    }

    id = Column(Integer,
                primary_key=True,
                index=True)
    client_id = Column(BigInteger, nullable=True, index=True, unique=True,
                       comment='Идентификатор записи подмены в системе клиента')
    doctor_id = Column(Integer, ForeignKey('doctors.id'), nullable=False,
                       comment='Идентификатор подменяющего доктора')
    start_date = Column(DateTime, nullable=False,
                        comment='Начальная дата периода подмены')
    end_date = Column(DateTime, nullable=False,
                      comment='Конечная дата периода подмены')
    description = Column(Text, nullable=True,
                      comment='Описание')
    is_active = Column(Boolean, default=True,
                        comment='Флаг активна/не активна')

    doctor = relationship('DoctorTable', lazy='joined')


class SubscribeDoctorTable(Base):
    """Модель SubscribeDoctor. Утвержденная"""

    __tablename__ = 'subscribes_doctors'
    __table_args__ = {
        'comment': 'Таблица "Врачи абонементов пользователей"'
    }

    id = Column(Integer,
                primary_key=True,
                index=True)
    client_id = Column(BigInteger, nullable=True, index=True, unique=True,
                       comment='Идентификатор доктра на абонементе в системе клиента')
    user_subscribe_id = Column(Integer, ForeignKey('users_subscribes.id'), nullable=False,
                               comment='Идентификатор абонемента пользователя')
    doctor_mcenters_id = Column(Integer, ForeignKey('doctors_medical_centers.id'), nullable=False,
                                comment='Идентификатор доктора')
    description = Column(Text, nullable=True,
                         comment='Описание')
    start_date = Column(DateTime, nullable=True,
                        comment='Начальная дата периода задействования доктора')
    end_date = Column(DateTime, nullable=True,
                      comment='Конечная дата периода Задействования доктора')
    role_id = Column(Integer, nullable=True,
                     comment='Идентификатор роли доктора')
    doctor_replacement_id = Column(Integer, ForeignKey('doctors_replacements.id'), nullable=True,
                                comment='Идентификатор записи о подмене доктора')
    is_active = Column(Boolean, default=True,
                       comment='Флаг активна/не активна')
    role_id = Column(Integer, ForeignKey('subscribe_roles.id'), nullable=True,
                                         comment='Идентификатор роли доктора')

    user_subscribe = relationship('UserSubscribeTable', lazy='joined')
    doctor_mcenters = relationship('DoctorMedicalCenterTable', lazy='joined')
    doctor_replacement = relationship('DoctorReplacementTable', lazy='joined')
    role = relationship('SubscribeRoleTable', lazy='joined')


class PackTypeTable(BaseNameDescriptionTable):
    """Модель PackType. Утвержденная"""

    __tablename__ = 'packs_types'
    __table_args__ = {
        'comment': 'Таблица "Типы пакетов услуг в абонементе"'
    }

    client_id = Column(BigInteger, nullable=True, index=True, unique=True,
                       comment='Идентификатор типа пакета в системе клиента')
    name = Column(String(200), nullable=False, unique=True,
                  comment='Наименование типа пакета услуг')


class SubscribeServicePackTable(BaseNameDescriptionTable):
    """Модель SubscribeServicePack. Утвержденная"""

    __tablename__ = 'subscribes_services_packs'
    __table_args__ = {
        'comment': 'Таблица "Пакеты услуг абонементов"'
    }

    id = Column(Integer,
                primary_key=True,
                index=True)
    client_id = Column(BigInteger, nullable=True, index=True, unique=True,
                       comment='Идентификатор групп услуг аьонементов в системе клиента')
    user_subscribe_id = Column(Integer, ForeignKey('users_subscribes.id'), nullable=False,
                               comment='Идентификатор абонемента пользователя')
    code = Column(String(50), nullable=True,
                         comment='Код пакета для нужд клиента')
    pack_type_id = Column(Integer, ForeignKey('packs_types.id'), nullable=True,
                          comment='Идентификатор типа пакета услуг абонементов (на  дому или в МЦ)')
    pack_tag = Column(Integer, nullable=True,
                      comment='тэг пакета: 1 - услуга, 2 - группа прейскуранта')
    min_quantity = Column(Integer, nullable=True,
                          comment='Минимальное количество')
    max_quantity = Column(Integer, nullable=True,
                          comment='Максимальное количество')
    quantity = Column(Integer, nullable=True,
                          comment='Количество')

    user_subscribe = relationship('UserSubscribeTable', lazy='joined')
    pack_type = relationship('PackTypeTable', lazy='joined')


class SubscribeSpackRecordTable(Base):
    """Модель SubscribeSpackRecord. Утвержденная"""

    __tablename__ = 'subscribes_spacks_records'
    __table_args__ = {
        'comment': 'Таблица "Элементы пакетов услуг абонементов"'
    }

    id = Column(Integer,
                primary_key=True,
                index=True)
    client_id = Column(BigInteger, nullable=True, index=True, unique=True,
                       comment='Идентификатор записи пакета услуги абонемента в системе клиента')
    subscribe_services_pack_id = Column(Integer, ForeignKey('subscribes_services_packs.id'), nullable=False,
                               comment='Идентификатор пакеты услуг абонемента')
    service_id = Column(Integer, ForeignKey('services.id'), nullable=True,
                       comment='Идентификатор услуги')
    service_group_id = Column(Integer, ForeignKey('services_groups.id'), nullable=True,
                              comment='Идентификатор группы прейскуранта')
    quantity = Column(Integer, nullable=True,
                   comment='Разрешенное количество услуг')
    is_active = Column(Boolean, default=True,
                       comment='Флаг активна/не активна')

    subscribe_services_pack = relationship('SubscribeServicePackTable', lazy='joined')
    service = relationship('ServiceTable', lazy='joined')
    service_group = relationship('ServiceGroupTable', lazy='joined')


class ShifrDiscountPeriodTable(Base):
    """Модель DiscountShifrPeriod. Утвержденная"""

    __tablename__ = 'shifrs_discounts_periods'
    __table_args__ = {
        'comment': 'Таблица "Периоды действия скидок шифров"'
    }

    id = Column(Integer,
                primary_key=True,
                index=True)
    client_id = Column(BigInteger, nullable=True, index=True, unique=True,
                       comment='Идентификатор периода скидок шифра в системе клиента')
    start_date = Column(DateTime, nullable=False,
                        comment='Начальная дата периода')
    end_date = Column(DateTime, nullable=False,
                      comment='Конечная дата периода')
    is_active = Column(Boolean, default=True,
                       comment='Флаг активна/не активна')


class ShifrDiscountTable(Base):
    """Модель ShifrDiscount. Утвержденная"""

    __tablename__ = 'shifrs_discounts'
    __table_args__ = {
        'comment': 'Таблица "Скидки шифров"'
    }

    id = Column(Integer,
                primary_key=True,
                index=True)
    client_id = Column(BigInteger, nullable=True, index=True, unique=True,
                       comment='идентификатор скидки шифра в системе клиента')
    shifr_discount_period_id = Column(Integer, ForeignKey('shifrs_discounts_periods.id'),
                                      comment='идентификатор периода скидок шифра')
    service_group_id = Column(Integer, ForeignKey('services_groups.id'), nullable=True,
                              comment='Идентификатор группы прейскуранта, если тэг = 2')
    service_id = Column(Integer, ForeignKey('services.id'), nullable=True,
                       comment='Идентификатор услуги, если тэг = 1')
    shifr_id = Column(Integer, ForeignKey('shifrs.id'), nullable=True,
                   comment='Идентификатор шифра')
    comment = Column(Text, nullable=True,
                  comment='Комментарий')
    discount_coefficient_a = Column(Float, nullable=True,
                                 comment='Коэффициент скидки для амбулаторий')
    discount_coefficient_s = Column(Float, nullable=True,
                                 comment='Коэффициент скидки для стационара')

    shift_discount_period = relationship('ShifrDiscountPeriodTable', lazy='joined')
    service = relationship('ServiceTable', lazy='joined')
    service_group = relationship('ServiceGroupTable', lazy='joined')
    shifr = relationship('ShifrTable', lazy='joined')


class UserPurchaseTable(Base):
    """Модель UserPurchase. Утвержденная"""

    __tablename__ = 'users_purchases'
    __table_args__ = {
        'comment': 'Таблица "Покупки пользователей"'
    }

    id = Column(Integer,
                primary_key=True,
                index=True)
    client_id = Column(BigInteger, nullable=True, index=True, unique=True,
                       comment='Идентификатор покупки пользователя в системе клиента')
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False,
                     comment='Идентификатор пользователя')
    policy_id = Column(Integer, ForeignKey('policies.id'), nullable=True,
                       comment='Идентификатор полиса')
    shifr_id = Column(Integer, ForeignKey('shifrs.id'), nullable=True,
                   comment='Идентификатор шифра')
    user_payment_id = Column(Integer, ForeignKey('users_payments.id', ondelete='CASCADE'), nullable=True,
                             comment='Идентификатор платежа пользовталя, СДЕЛАТЬ ForeignKey')
    doctor_mcenter_exec_id = Column(Integer, ForeignKey('doctors_medical_centers.id'), nullable=True,
                            comment='Идентификатор доктора, выполнившего услугу')
    doctor_mcenter_nurse_id = Column(Integer, ForeignKey('doctors_medical_centers.id'), nullable=True,
                             comment='Идентификатор медсестры, выполнившей услугу')
    payment_date = Column(DateTime, nullable=True,
                          comment='Дата и время платежа')
    service_id = Column(Integer, ForeignKey('services.id'), nullable=False,
                       comment='Идентификатор услуги')
    service_quantity = Column(Integer, default=1,
                              comment='Количество таких услуг')
    price = Column(Float, nullable=True,
                   comment='Цена услуги')
    discount = Column(Float, nullable=True,
                      comment='Скидка на цену услуги в %')
    discount_koef = Column(Float, nullable=True,
                           comment='Коэффициент скидки')
    amount = Column(Float, nullable=True,
                    comment='Итоговая стоимость услуги')

    user = relationship(UserTable, lazy='joined')
    policy = relationship(PolicyTable, lazy='joined')
    shifr = relationship(ShifrTable, lazy='joined')
    doctor_mcenter_exec = relationship(DoctorMedicalCenterTable, foreign_keys=[doctor_mcenter_exec_id], lazy='joined')
    doctor_mcenter_nurse = relationship(DoctorMedicalCenterTable, foreign_keys=[doctor_mcenter_nurse_id], lazy='joined')
    service = relationship(ServiceTable, lazy='joined')
    user_payment = relationship('UserPaymentTable', lazy='joined', backref=backref('purchases', passive_deletes=True))


class PricePeriodTable(Base):
    """Модель PricePeriod. Утвержденная"""

    __tablename__ = 'prices_periods'
    __table_args__ = {
        'comment': 'Таблица "Периоды действия прайсов"'
    }

    id = Column(Integer,
                primary_key=True,
                index=True)
    client_id = Column(BigInteger, nullable=True, index=True, unique=True,
                       comment='Идентификатор периода действия в системе клиента')
    start_date = Column(DateTime, nullable=False,
                        comment='Начальная дата периода')
    end_date = Column(DateTime, nullable=False,
                      comment='Конечная дата периода')
    is_active = Column(Boolean, default=True,
                       comment='Флаг активна/не активна')


class PriceNameTable(Base):
    """Модель PriceName. Утвержденная"""

    __tablename__ = 'prices_names'
    __table_args__ = {
        'comment': 'Таблица "Наименования прайсов"'
    }

    id = Column(Integer,
                primary_key=True,
                index=True)
    client_id = Column(BigInteger, nullable=True, index=True, unique=True,
                       comment='Идентификатор имени прайса в системе клиента')
    name = Column(String(200), nullable=False, unique=True,
                  comment='Наименование')
    description = Column(Text, nullable=True,
                         comment='Описание')
    is_active = Column(Boolean, default=True,
                       comment='Флаг активно/неактивно')


class PriceTable(Base):
    """Модель Price. Утвержденная"""

    __tablename__ = 'prices'
    __table_args__ = {
        'comment': 'Таблица "Прайсы"'
    }

    id = Column(Integer,
                primary_key=True,
                index=True)
    client_id = Column(BigInteger, nullable=True, index=True, unique=True,
                       comment='Идентификатор прайса в системе клиента')
    service_id = Column(Integer, ForeignKey('services.id'), nullable=False,
                        comment='Идентификатор услуги')
    price_period_id = Column(Integer, ForeignKey('prices_periods.id'), nullable=True,
                             comment='Идентификатор периода действия прайса')
    price_name_id = Column(Integer, ForeignKey('prices_names.id'), nullable=False,
                           comment='Идентификатор периода наименования прайса')
    price_beznal = Column(Float, nullable=True,
                          comment='Цена безнал')
    price_nal = Column(Float, nullable=True,
                       comment='Цена нал')

    service = relationship(ServiceTable, lazy='joined')
    price_period = relationship(PricePeriodTable, lazy='joined')
    price_name = relationship(PriceNameTable, lazy='joined')

    def __str__(self):
        return f'{self.price_nal}'


class PaymentTypeTable(Base):
    """Модель PaymentType. Утвержденная"""

    __tablename__ = 'payments_types'
    __table_args__ = {
        'comment': 'Таблица "Типы платежей"'
    }

    id = Column(Integer,
                primary_key=True,
                index=True)
    client_id = Column(BigInteger, nullable=True, index=True, unique=True,
                       comment='Идентификатор типа платежа в системе клиента')
    name = Column(String(200), nullable=False, unique=True,
                  comment='Наименование')
    description = Column(Text, nullable=True,
                         comment='Описание')
    is_active = Column(Boolean, default=True,
                       comment='Флаг активно/неактивно')


class UserPaymentTable(Base):
    """Модель UserPayment. Утвержденная"""

    __tablename__ = 'users_payments'
    __table_args__ = {
        'comment': 'Таблица "Платежи пользователей"'
    }

    id = Column(Integer,
                primary_key=True,
                index=True)
    client_id = Column(BigInteger, nullable=True, index=True, unique=True,
                       comment='Идентификатор платежа пользователя в системе клиента')
    user_id = Column(BigInteger, ForeignKey('users.id'), nullable=False,
                     comment='Идентификатор пользователя')
    policy_id = Column(Integer, ForeignKey('policies.id'), nullable=True,
                       comment='Идентификатор полиса')
    shifr_id = Column(Integer, ForeignKey('shifrs.id'), nullable=True,
                      comment='Идентификатор шифра')
    payment_type_id = Column(Integer, ForeignKey('payments_types.id'), nullable=True,
                             comment='Тип платежа')
    linked_user_payment_id = Column(Integer, ForeignKey('users_payments.id'), nullable=True,
                                    comment='Идентификатор платежа пользователя для целей возврата')
    avance_status = Column(Integer, nullable=True,
                           comment='Статус аванса')
    payment_date = Column(DateTime, nullable=False,
                          comment='Дата платежа')
    payment_status = Column(Integer, default=0,
                            comment='Статус платежа')
    amount = Column(Float, nullable=False,
                    comment='Сумма платежа')
    full_amount = Column(Float, nullable=True,
                         comment='Полная сумма платежа')
    discount_amount = Column(Float, nullable=True,
                                comment='Сумма дисконта')
    used_amount = Column(Float, nullable=True,
                            comment='Использованная сумма')
    avance_amount = Column(Float, nullable=True,
                           comment='Сумма аванса')
    card_amount = Column(Float, nullable=True,
                            comment='Сумма по карточке')
    sbp_amount = Column(Float, nullable=True,
                        comment='Сумма через СБП')
    debt_amount = Column(Float, nullable=True,
                         comment='Сумма задолженности')
    edit_now_status = Column(Boolean, default=True,
                             comment='Статус текущего редактирования')
    lpu_id = Column(Integer, ForeignKey('lpus.id'), nullable=True,
                    comment='Идентификатор лпу')
    cashier_id = Column(Integer, nullable=True,
                        comment='Идентификатор кассираг')
    transaction_code = Column(String(200), nullable=True,
                              comment='Код транзакции от платежной системы')

    user = relationship(UserTable, lazy='joined')
    policy = relationship(PolicyTable, lazy='joined')
    shifr = relationship(ShifrTable, lazy='joined')
    payment_type = relationship(PaymentTypeTable, lazy='joined')
    linked_user_payment = relationship('UserPaymentTable', lazy='joined')
    lpu = relationship(LpuTable, lazy='joined')
    # purchases = relationship(UserPurchaseTable, lazy='joined')


class UserPurchaseReturnTable(Base):
    """Модель UserPurchasesReturn. Утвержденная"""

    __tablename__ = 'users_purchases_returns'
    __table_args__ = {
        'comment': 'Таблица "Возвраты покупок пользователя"'
    }

    id = Column(Integer,
                primary_key=True,
                index=True)
    client_id = Column(BigInteger, nullable=True, index=True, unique=True,
                       comment='Идентификатор возврата покупки пользователя в системе клиента')
    user_purchase_id = Column(Integer, ForeignKey('users_purchases.id'), nullable=False,
                              comment='Идентификатор покупки пользователя')
    user_payments_id = Column(Integer, ForeignKey('users_payments.id'), nullable=False,
                           comment='Идентификатор платежа пользовтеля')
    quantity = Column(Integer, nullable=True,
                        comment='Количество отменяемых услуг')
    sum = Column(Float, nullable=False,
                    comment='Сумма платежа')
    sum_card = Column(Float, nullable=True,
                        comment='Сумма платежа по карте')
    sum_sbp = Column(Float, nullable=True,
                     comment='Сумма платежа через СБП')
    sum_avance = Column(Float, nullable=True,
                     comment='Сумма аванса')

    user_purchase = relationship(UserPurchaseTable, lazy='joined')
    user_payments = relationship(UserPaymentTable, lazy='joined')


class RefuseReasonTable(Base):
    """Модель RefuseReason. Утвержденная"""

    __tablename__ = 'refuses_reasons'
    __table_args__ = {
        'comment': 'Таблица "Причины отказов"'
    }

    id = Column(Integer,
                primary_key=True,
                index=True)
    client_id = Column(BigInteger, nullable=True, index=True, unique=True,
                       comment='Идентификатор причины отказа в системе клиента')
    text = Column(String(4000), nullable=False,
                  comment='Наименование')
    description = Column(Text, nullable=True,
                         comment='Описание')
    is_active = Column(Boolean, default=True,
                       comment='Флаг активно/неактивно')


class UserServiceCartTable(Base):
    """Модель UserServiceCart. Утвержденная"""

    __tablename__ = 'users_services_carts'
    __table_args__ = {
        'comment': 'Таблица "Корзины пользователей"'
    }

    id = Column(Integer,
                primary_key=True,
                index=True)
    client_id = Column(BigInteger, nullable=True, index=True, unique=True,
                       comment='Идентификатор записи в корзине в системе клиента')
    service_id = Column(Integer, ForeignKey('services.id'), nullable=False,
                        comment='Идентификатор услуги')
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False,
                     comment='Идентификатор пользователя')
    shifr_id = Column(Integer, ForeignKey('shifrs.id'), nullable=True,
                      comment='Идентификатор шифра')
    policy_id = Column(Integer, ForeignKey('policies.id'), nullable=True,
                       comment='Идентификатор полиса')
    medical_center_id = Column(Integer, ForeignKey('medical_centers.id'), nullable=False,
                               comment='Идентификатор медицинского центра')
    access_ticket_id = Column(Integer, ForeignKey('access_tickets.id'), nullable=True,
                              comment='Идентификатор номерка')
    doctor_mcenter_id = Column(Integer, ForeignKey('doctors_medical_centers.id'), nullable=True,
                       comment='Идентификатор доктора, выбранного в услуге')
    doctor_mcenter_exec_id = Column(Integer, ForeignKey('doctors_medical_centers.id'), nullable=True,
                            comment='Идентификатор доктора, выполнявшего услугу')
    doctor_mcenter_send_id = Column(Integer, ForeignKey('doctors_medical_centers.id'), nullable=True,
                            comment='Идентификатор доктора, назначившего услугу')
    doctor_mcenter_nurse_id = Column(Integer, ForeignKey('doctors_medical_centers.id'), nullable=True,
                             comment='Идентификатор медсестры, выполнявшей услугу')
    doctor_mcenter_paramedic_id = Column(Integer, ForeignKey('doctors_medical_centers.id'), nullable=True,
                                 comment='Идентификатор доктора - парамедика, выполнявшего услугу')
    start_date = Column(DateTime, nullable=True,
                        comment='Дата и время начала выполнения услуги')
    end_date = Column(DateTime, nullable=True,
                      comment='Дата и время окончания выполнения услуги')
    complex_service_id = Column(Integer, ForeignKey('complex_services.id'), nullable=True,
                                comment='Идентификатор комплексной услуги')
    complex_service_status = Column(Integer, nullable=True,
                                    comment='Статус комплексной услуги: ставится 1 если услуга комплексная (верхний уровень), для услуги нижнего уровня ставится 0')
    service_status = Column(
        Integer,
        nullable=True,
        comment="Статус услуги: 0 / 3 - назначена, 1 - выполнена, 2 - отменена"
    )
    quantity = Column(Integer, nullable=True,
                      comment='Количество услуг')
    stac_satus = Column(Boolean, default=True,
                        comment='Флаг стационарная да\нет')
    cito_status = Column(Boolean, default=False,
                         comment='Флаг срочная да\нет')
    refuse_date = Column(DateTime, nullable=True,
                         comment='Дата отказа от выполнения услуги')
    refuse_reason_id = Column(Integer, ForeignKey('refuses_reasons.id'), nullable=True,
                              comment='Идентификатор причины отказа')
    description = Column(Text, nullable=True,
                         comment='Описание')
    discount = Column(Float, nullable=True,
                      comment='Скидка')
    discount_coefficient = Column(Float, nullable=True,
                                  comment='Коэффициент на скидку')
    price_id = Column(Integer, ForeignKey('prices.id'), nullable=True,
                      comment='Идентификатор прайсовой стоимости услуги')
    user_purchase_id = Column(Integer, ForeignKey('users_purchases.id', ondelete='SET NULL'),
                              nullable=True, comment='Идентификатор покупки пользователя')

    service = relationship(ServiceTable, lazy='joined')
    user = relationship(UserTable, lazy='joined')
    shifr = relationship(ShifrTable, lazy='joined')
    policy = relationship(PolicyTable, lazy='joined')
    medical_center = relationship(MedicalCenterTable, lazy='joined')
    access_ticket = relationship('AccessTicketTable', lazy='joined')
    doctor_mcenter = relationship(DoctorMedicalCenterTable, foreign_keys=[doctor_mcenter_id], lazy='joined')
    # doctor_mcenter_exec = relationship(DoctorMedicalCenterTable, foreign_keys=[doctor_mcenter_exec_id], lazy='joined')
    # doctor_mcenter_send = relationship(DoctorMedicalCenterTable, foreign_keys=[doctor_mcenter_send_id], lazy='joined')
    # doctor_mcenter_nurse = relationship(DoctorMedicalCenterTable, foreign_keys=[doctor_mcenter_nurse_id], lazy='joined')
    # doctor_mcenter_paramedic = relationship(DoctorMedicalCenterTable, foreign_keys=[doctor_mcenter_paramedic_id], lazy='joined')
    complex_service = relationship(ComplexServiceTable, lazy='joined')
    user_purchase = relationship(UserPurchaseTable, lazy='joined',
                                 backref=backref('services_carts', passive_deletes=True))
    refuse_reason = relationship(RefuseReasonTable, lazy='joined')
    price = relationship(PriceTable, lazy='joined')


class UserServicePlanTable(Base):
    """Модель UserServicePlane. Утвержденная"""

    __tablename__ = 'users_services_plans'
    __table_args__ = {
        'comment': 'Таблица "Запланированные услуги пользователей"'
    }

    id = Column(Integer,
                primary_key=True,
                index=True)
    client_id = Column(BigInteger, nullable=True, index=True, unique=True,
                       comment='Идентификатор запланированной услуги в системе клиента')
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False,
                     comment='Идентификатор пользователя')
    service_id = Column(Integer, ForeignKey('services.id'), nullable=False,
                        comment='Идентификатор услуги')
    policy_id = Column(Integer, ForeignKey('policies.id'), nullable=True,
                        comment='Идентификатор полиса')
    shifr_id = Column(Integer, ForeignKey('shifrs.id'), nullable=True,
                      comment='Идентификатор шифра')
    quantity = Column(Integer, nullable=True,
                      comment='Количество услуги')
    plan_date = Column(DateTime, nullable=False,
                       comment='Плановая дата выполнения услуги')
    description = Column(Text, nullable=True,
                         comment='Описание')
    doctor_send_id = Column(Integer, ForeignKey('doctors_medical_centers.id'), nullable=True,
                            comment='Идентификатор доктора, назначившего услугу')
    medical_center_id = Column(Integer, ForeignKey('medical_centers.id'), nullable=False,
                               comment='Идентификатор медицинского центра')
    status = Column(Integer, nullable=True,
                    comment='Статус запланированной услуги')
    refuse_reason_id = Column(Integer, ForeignKey('refuses_reasons.id'), nullable=True,
                              comment='Идентификатор причины отказа')
    refuse_date = Column(DateTime, nullable=True,
                         comment='Дата отказа от выполнения услуги')
    user_service_cart_id = Column(Integer, ForeignKey('users_services_carts.id'), nullable=True,
                                  comment='Идентификатор услуги в корзине')

    service = relationship(ServiceTable, lazy='joined')
    user = relationship(UserTable, lazy='joined')
    shifr = relationship(ShifrTable, lazy='joined')
    policy = relationship(PolicyTable, lazy='joined')
    doctor_send = relationship(DoctorMedicalCenterTable, foreign_keys=[doctor_send_id], lazy='joined')
    medical_center = relationship(MedicalCenterTable, lazy='joined')
    refuse_reason = relationship(RefuseReasonTable, lazy='joined')
    # user_service_cart = relationship(UserServiceCartTable, lazy='joined')


class AccessTicketTable(Base):
    """Модель AccessTicket. Утвержденная"""

    __tablename__ = 'access_tickets'
    __table_args__ = {
        'comment': 'Таблица "Номерки"'
    }

    id = Column(Integer,
                primary_key=True,
                index=True)
    client_id = Column(BigInteger, nullable=True, index=True, unique=True,
                       comment='Идентификатор номерка в системе клиента')
    doctor_mcenters_id = Column(Integer, ForeignKey('doctors_medical_centers.id', ondelete='CASCADE'), index=True,
                                nullable=False, comment='Идентификатор доктора номерка')
    user_id = Column(Integer, ForeignKey('users.id', ondelete='SET NULL'),
                        comment='Идентификатор пользователя')
    ticket_datetime = Column(DateTime, nullable=False,
                             comment='Дата номерка')
    ticket_duration = Column(Integer, nullable=True,
                             comment='Длительность услуги в минутах')
    ticket_room = Column(String(24), nullable=True,
                         comment='Кабинет номерка')
    firststatus = Column(Boolean, nullable=True,
                         comment='Первый статус номерка')
    bl_status = Column(Integer, nullable=True,
                       comment="""Статус номерка: 0 - блокирован для выдачи в регистратуре,\
                                  1 - активный, 2 - выдан пациенту, 3 - зарезервирован;""")
    is_active = Column(Boolean, default=True,
                       comment='Флаг активно/неактивно')
    is_reserv = Column(Boolean, default=True,
                       comment='Флаг в резерве/не в резерве')
    expire_date = Column(DateTime, nullable=True,
                         comment='Дата истечения номерка')
    from_internet_status = Column(Boolean, nullable=True,
                                  comment='Флаг активно/неактивно')

    doctor_mcenters = relationship(DoctorMedicalCenterTable, lazy='joined', backref=backref('tickets', passive_deletes=True))
    user = relationship(UserTable, lazy='joined', backref=backref('user_purchases', passive_deletes=True))

    Index('idx_date', func.date(ticket_datetime))


class DoctorMedicalCenterServiceTable(Base):
    """Модель DoctorMedicalCenterService. Утвержденная"""

    __tablename__ = 'doctors_mcenters_services'
    __table_args__ = {
        'comment': 'Таблица "Услуги докторов в медицинских центрах"'
    }

    id = Column(Integer,
                primary_key=True,
                index=True)
    client_id = Column(BigInteger, nullable=True, index=True, unique=True,
                       comment='Идентификатор услуги доктора в медцентре в системе клиента')
    service_id = Column(Integer, ForeignKey('services.id'), nullable=False,
                        comment='Идентификатор услуги')
    doctor_mcenters_id = Column(Integer, ForeignKey('doctors_medical_centers.id'), nullable=False,
                                comment='Идентификатор доктора в медцентре')
    is_active = Column(Boolean, default=True,
                       comment='Флаг активно/неактивно')

    service = relationship(ServiceTable, lazy='joined')
    doctor_mcenters = relationship(DoctorMedicalCenterTable, lazy='joined')


class MedicalCenterPriceNameTable(Base):
    """Модель MedicalCenterPriceName. Утвержденная"""

    __tablename__ = 'mcenters_price_names'
    __table_args__ = {
        'comment': 'Таблица "Услуги наименование прайсов в медцентрах"'
    }

    id = Column(Integer,
                primary_key=True,
                index=True)
    client_id = Column(BigInteger, nullable=True, index=True, unique=True,
                       comment='Идентификатор услуги доктора в медцентре в системе клиента')
    medical_center_id = Column(Integer, ForeignKey('medical_centers.id'), nullable=True,
                               comment='Идентификатор медицинского центра')
    price_name_id = Column(Integer, ForeignKey('prices_names.id'), nullable=False,
                           comment='Идентификатор наименования прайса')
    service_type_id = Column(Integer, ForeignKey('services_types.id'), nullable=True,
                             comment='Идентификатор типа услуги')
    is_active = Column(Boolean, default=True,
                       comment='Флаг активно/неактивно')

    medical_center = relationship(MedicalCenterTable, lazy='joined')
    price_name = relationship(PriceNameTable, lazy='joined')
    service_type = relationship(ServiceTypeTable, lazy='joined')


class UserDefaultObjectTable(Base):
    """Модель UserDefaultObject. Утвержденная"""

    __tablename__ = 'users_default_objects'
    __table_args__ = {
        'comment': 'Таблица "Объекты по умолчанию для пользователей"'
    }

    id = Column(Integer,
                primary_key=True,
                index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, unique=True,
                     comment='Идентификатор пользователя')
    default_patient_id = Column(Integer, ForeignKey('users.id'), nullable=False,
                                comment='Идентификатор пациента по умолчанию')
    default_medical_center_id = Column(Integer, ForeignKey('medical_centers.id'), nullable=True,
                                       comment='Идентификатор медицинского центра по умолчанию')
    default_doctor_mcenters_id = Column(Integer, ForeignKey('doctors_medical_centers.id'), nullable=True,
                                        comment='Идентификатор доктора по умолчанию')

    user = relationship(UserTable, foreign_keys=[user_id], lazy='joined')
    default_patient = relationship(UserTable, foreign_keys=[default_patient_id], lazy='joined')
    default_medical_center = relationship(MedicalCenterTable, lazy='joined')
    default_doctor_mcenters = relationship(DoctorMedicalCenterTable, lazy='joined')


class AccessTicketListTable(Base):
    """Модель AccessTicketList. Утвержденная"""

    __tablename__ = 'access_tickets_lists'
    __table_args__ = {
        'comment': 'Таблица "Группы номерков прилинкованных к главному номерку, на который записываются все услуги из группы"'
    }

    id = Column(Integer,
                primary_key=True,
                index=True)
    main_access_ticket_client_id = Column(String, nullable=False,
                                          comment='Идентификатор номерка (главного номерка), на который записываются услуги из группы')
    access_ticket_client_id = Column(String, nullable=False,
                                     comment='Идентификатор номерка, относящегося к главному')
    user_client_id = Column(BigInteger, nullable=True,
                            comment='Идентификатор карточки пользователя в системе клиента')


class UserUsedAdvanceTable(Base):
    """Модель UserUsedAdvance. Утвержденная"""

    __tablename__ = 'users_used_advances'
    __table_args__ = {
        'comment': 'Таблица "Использование пользователем внесенного ранее аванса"'
    }

    id = Column(Integer,
                primary_key=True,
                index=True)
    client_id = Column(BigInteger, nullable=True, index=True, unique=True,
                       comment='Идентификатор записи в системе клиента')
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False,
                     comment='Идентификатор пользователя')
    payment_advance_id = Column(Integer, ForeignKey('users_payments.id', ondelete='CASCADE'), nullable=False,
                                comment='Идентификатор авансового платежа пользовтеля')
    payment_spend_id = Column(Integer, ForeignKey('users_payments.id'), nullable=False,
                              comment='Идентификатор платежа пользовтеля, в котором используется аванс')
    amount = Column(Float, nullable=False,
                    comment='Сумма использования аванса')

    payment_advance = relationship('UserPaymentTable', foreign_keys=[payment_advance_id], lazy='joined',
                                   backref=backref('advances', passive_deletes=True))


class PayKeeperPaymentDataTable(Base):
    """Модель PayKeeperPayment. Утвержденная"""

    __tablename__ = 'paykeeper_payments_data'
    __table_args__ = {
        'comment': 'Таблица "Таблица данных системы Pay Keeper"'
    }

    id = Column(Integer,
                primary_key=True,
                index=True)
    user_payment_id = Column(Integer, ForeignKey('users_payments.id', ondelete='CASCADE'), nullable=False, unique=True,
                             comment='Идентификатор платежа пользовтеля в PG')
    paykeeper_id = Column(String, nullable=False,
                          comment='Идентификатор платежа в личном кабинете системы PeyKeeper')
    pay_amount = Column(Float, nullable=True,
                        comment='Сумма платежа')
    refund_amount = Column(Float, nullable=True,
                           comment='Возвращенная часть платежа')
    clientid = Column(String, nullable=False,
                      comment='Идентификатор клиента в системе магазина (информация о пользователе)')
    orderid = Column(String, nullable=False,
                     comment='Номер заказа в системе магазина (наш payment_id)')
    payment_system_id = Column(String, nullable=True,
                               comment='Идентификатор платежной системы')
    unique_id = Column(String, nullable=True,
                               comment='Уникальный идентификатор транзакции')
    status = Column(String, nullable=True,
                    comment='Статус платежа: ("obtained", "stuck", "success", "canceled", "failed", "pending",\
                            "refunding", "refunded", "partially_refunded")')
    repeat_counter = Column(Integer, nullable=True,
                            comment='Количество отправленных запросов при проведении платежа в систему магазина')
    pending_datetime = Column(DateTime, nullable=True,
                              comment='Дата/Время создания платежа')
    obtain_datetime = Column(DateTime, nullable=True,
                             comment='Дата/Время создания платежа')
    success_datetime = Column(DateTime, nullable=True,
                              comment='Дата/Время информирования магазина о проведенном платеже')

    user_payment = relationship('UserPaymentTable', lazy='joined',
                                backref=backref('paykeepers', passive_deletes=True))


class PolicyPaymentPlanTable(Base):
    """Модель PolicyPaymentPlan. Утвержденная"""

    __tablename__ = 'policies_payments_plans'
    __table_args__ = {
        'comment': 'Таблица "График платежей по полису"'
    }

    id = Column(Integer,
                primary_key=True,
                index=True)
    client_id = Column(BigInteger, nullable=True, index=True, unique=True,
                       comment='Идентификатор записи в системе клиента')
    policy_id = Column(Integer, ForeignKey('policies.id'), nullable=False,
                       comment='Идентификатор полиса')
    planed_date = Column(DateTime, nullable=False,
                         comment='Дата оплаты по плану')
    amount = Column(Float, nullable=False,
                    comment='Планируемая сумма оплаты')


class SubscribeRoleTable(Base):
    """Модель SubscribeRole. Утвержденная"""

    __tablename__ = 'subscribe_roles'
    __table_args__ = {
        'comment': 'Таблица "Роли в абонементе"'
    }

    id = Column(Integer,
                primary_key=True,
                index=True)
    client_id = Column(BigInteger, nullable=True, index=True, unique=True,
                       comment='Идентификатор роли в системе клиента')
    name = Column(String(200), nullable=False,
                  comment='Наименование')
    description = Column(Text, nullable=True,
                         comment='Описание')
    is_active = Column(Boolean, default=True,
                       comment='Флаг активно/неактивно')


class TemporaryPaymentTable(Base):
    """Модель TemporaryPayment. Утвержденная"""

    __tablename__ = 'temporary_payments'
    __table_args__ = {
        'comment': 'Таблица "Временные платежи"'
    }

    id = Column(Integer,
                primary_key=True,
                index=True)
    payment_id = Column(Integer, nullable=False,
                        comment='Идентификатор временного платежа')
    payment_time = Column(DateTime, default=datetime.now(), nullable=False,
                          comment='Дата и время инициации платежа')


class InitproPaymentReceiptTable(Base):
    """Модель PaymentReceipt. Утвержденная"""

    __tablename__ = 'initpro_payments_receipts'
    __table_args__ = {
        'comment': 'Таблица "Регистрация документа в онлайн кассе Инитпро"'
    }

    id = Column(Integer,
                primary_key=True,
                index=True)
    payment_id = Column(Integer, nullable=False,
                        comment='Идентификатор платежа в таблице users_payment')
    initpro_payment_method = Column(String(15), nullable=False,
                                    comment='Признак способа расчёта в системе Инитпро')
    initpro_payment_object = Column(String(15), nullable=False,
                                    comment='Признак предмета расчёта в системе Инитпро')
    initpro_payment_type = Column(Integer, nullable=False,
                                  comment='Вид оплаты в системе Инитпро')
    timestamp = Column(DateTime, nullable=False,
                       comment='Дата и время возникновения текущего статуса')
    uuid = Column(String(36), nullable=True,
                  comment='Идентификатор документа в системе Инитпро')
    status = Column(String(20), nullable=True,
                    comment='Статус регистрации документа в системе Инитпро: None, "wait", "done"')
    error_id = Column(String(50), nullable=True,
                      comment='Идентификатор ошибки в системе Инитпро')
    error_code = Column(Integer, nullable=True,
                        comment='Код ошибки в системе Инитпро')
    error_text = Column(String, nullable=True,
                        comment='Сообщение об ошибке в системе Инитпро')
    error_type = Column(String(20), nullable=True,
                        comment='Тип ошибки в системе Инитпро')
    payload_total = Column(String, nullable=True,
                           comment='Параметр total в системе Инитпро')
    payload_fns_site = Column(String, nullable=True,
                              comment='Параметр fns_site в системе Инитпро')
    payload_fn_number = Column(String, nullable=True,
                               comment='Параметр fn_number в системе Инитпро')
    payload_shift_number = Column(String, nullable=True,
                                  comment='Параметр shifr_number в системе Инитпро')
    payload_receipt_datetime = Column(DateTime, nullable=True,
                                      comment='Параметр receipt_datetime в системе Инитпро')
    payload_fiscal_receipt_number = Column(String, nullable=True,
                                           comment='Параметр receipt_number в системе Инитпро')
    payload_fiscal_document_number = Column(String, nullable=True,
                                            comment='Параметр fiscal_document_number в системе Инитпро')
    payload_ecr_registration_number = Column(String, nullable=True,
                                             comment='Параметр ecr_registration_number в системе Инитпро')
    payload_fiscal_document_attribute = Column(String, nullable=True,
                                               comment='Параметр fiscal_document_attribute в системе Инитпро')
    group_code = Column(String, nullable=True,
                                comment='Параметр group_code в системе Инитпро')
    daemon_code = Column(String, nullable=True,
                                comment='Параметр daemon_code в системе Инитпро')
    device_code = Column(String, nullable=True,
                                 comment='Параметр device_code в системе Инитпро')
    warnings = Column(String, nullable=True,
                              comment='Параметр warnings в системе Инитпро')
    external_id = Column(String, nullable=True,
                         comment='Параметр external_id в системе Инитпро')
    callback_url = Column(String, nullable=True,
                                  comment='Параметр callback_ur в системе Инитпро')
    lpu_client_id = Column(BigInteger, nullable=True,
                           comment='Идентификатор lpu в системе клиента')
    operation_type = Column(String, nullable=True,
                            comment='Тип операции в системе Инитпро')


class UserDocumentRequestTable(Base):
    """Модель UserDocumentRequest. Утвержденная"""

    __tablename__ = 'users_documents_requests'
    __table_args__ = {
        'comment': 'Таблица "Запросы документов пользователями"'
    }

    id = Column(Integer,
                primary_key=True,
                index=True)
    client_id = Column(BigInteger, nullable=True, index=True, unique=True,
                       comment='Идентификатор запроса в системе клиента')
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False,
                     comment='Идентификатор пользователя')
    user_service_cart_client_id = Column(String, nullable=True,
                                         comment='Идентификатор услуги пользователя в системе клиента')
    doc_client_id = Column(String, nullable=True,
                           comment='Идентификатор документа в системе клиента')
    doc_params = Column(String, nullable=True,
                        comment='Параметры документа в виде json-строки')
    doc_name = Column(String, nullable=True,
                      comment='Название документа')
    request_date = Column(DateTime, nullable=True,
                          comment='Дата запроса документа')
    is_requested = Column(Boolean, default=False,
                          comment='Флаг запрошен/незапрошен')
    payment_id = Column(Integer, nullable=True,
                        comment='Идентификатор платежа для платной услуги')
    is_paid = Column(Boolean, default=False,
                     comment='Флаг оплачен/неоплачен для платной услуги')
    medical_center_id = Column(Integer, ForeignKey('medical_centers.id'), nullable=True,
                                       comment='Идентификатор медицинского центра по умолчанию')
    obtaining_method = Column(Integer, nullable=True,
                              comment='Метод получения: 0 - В МЦ / 1 - По эл. почте.')
    status = Column(Integer, nullable=True,
                              comment='Статус запроса: 0 - Новый / 1 - Отправлено оповещение сотруднику / 2 - Ожидает выдачи в МЦ / 3 - Выдан / 99 - Ошибка от МИС')
    status_description = Column(String, nullable=True,
                                comment='Пояснение к статусу')

    user = relationship(UserTable, foreign_keys=[user_id], lazy='joined')
    medical_center = relationship(MedicalCenterTable, lazy='joined')

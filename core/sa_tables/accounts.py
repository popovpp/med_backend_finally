import secrets
from datetime import datetime, date
from sqlalchemy import (Column, String, DateTime, Boolean, Date, Integer, ForeignKey, Float,
                        Time, Text, BigInteger)
from sqlalchemy.orm import relationship, backref
from passlib.context import CryptContext

from ..config.db import Base


class AddressMisKladrTable(Base):
    """Модель AddressMisKladr. Утвержденная"""

    __tablename__ = "address_mis_kladr"
    __table_args__ = {
        'comment': 'Таблица-справочник "ADDRS"'
    }

    id = Column(Integer,
                primary_key=True,
                index=True)
    client_id = Column(BigInteger, nullable=True, index=True, unique=True,
                       comment='Идентификатор записи в таблице ADDRS в системе клиента')
    client_user_id = Column(BigInteger, nullable=True,
                            comment='Идентификатор пользователя в системе клиента')
    tag = Column(Integer, nullable=True,
                 comment='1 - прописка; 2 - проживание')
    luid = Column(Integer, nullable=True,
                  comment='Тип адреса (LU.TAG = 1)')
    region = Column(String(128), nullable=True,
                    comment='Субъект РФ или страна')
    region_code = Column(String(32), nullable=True,
                         comment='Код субъекта РФ или страны')
    area = Column(String(128), nullable=True,
                  comment='Область')
    area_code = Column(String(32), nullable=True,
                       comment='Код области')
    city = Column(String(128), nullable=True,
                  comment='Город')
    city_code = Column(String(32), nullable=True,
                       comment='Код города')
    town = Column(String(128), nullable=True,
                  comment='Населенный пункт (не город)')
    town_code = Column(String(32), nullable=True,
                       comment='Код населенного пункта')
    street = Column(String(128), nullable=True,
                    comment='Улица')
    street_code = Column(String(32), nullable=True,
                         comment='Код улицы')
    house = Column(String(100), nullable=True,
                   comment='Дом')
    corp = Column(String(20), nullable=True,
                  comment='Корпус')
    flat = Column(String(10), nullable=True,
                  comment='Квартира')
    note = Column(String(256), nullable=True,
                  comment='Комментарий к адресу')
    status = Column(Integer, nullable=True,
                    comment='Статус: 0 - архивный, 1 - активный')
    lives_lu_id = Column(Integer, nullable=True,
                         comment='Место проживания (городской или сельский житела)')
    house_code = Column(String(32), nullable=True,
                        comment='Код дома')


class CityTable(Base):
    """Модель City"""

    __tablename__ = "cities"
    __table_args__ = {
        'comment': 'Таблица-справочник "Города"'
    }

    id = Column(Integer,
                primary_key=True,
                index=True)
    client_id = Column(BigInteger, nullable=True, index=True, unique=True,
                       comment='Идентификатор города в системе клиента')
    name = Column(String(200), nullable=False, unique=True,
                  comment='Наименование города')
    is_active = Column(Boolean, default=True,
                       comment='Флаг активный/не активный')


class LpuTable(Base):
    """Модель Lpu. Утвержденная"""

    __tablename__ = 'lpus'
    __table_args__ = {
        'comment': 'Таблица "Лечебныо-профилактические учреждения"'
    }

    id = Column(Integer,
                primary_key=True,
                index=True)
    client_id = Column(BigInteger, nullable=True, index=True, unique=True,
                       comment='Идентификатор записи в системе клиента')
    name = Column(String(200), nullable=False,
                  comment='Наименование ЛПУ')
    description = Column(Text, nullable=True,
                         comment='Описание ЛПУ')
    start_date = Column(DateTime, nullable=True,
                        comment='Дата и время начала использования')
    end_date = Column(DateTime, nullable=True,
                      comment='Дата и время окончания использования')
    is_active = Column(Boolean, default=True,
                       comment='Флаг активно/неактивно')


class MedicalCenterTable(Base):
    """Модель MedicalCenter"""

    __tablename__ = "medical_centers"
    __table_args__ = {
        'comment': 'Таблица-справочник "Медицинские центры клиента"'
    }

    id = Column(Integer,
                primary_key=True,
                index=True)
    client_id = Column(BigInteger, nullable=True, index=True, unique=True,
                       comment='Идентификатор медицинского центра в системе клиента')
    city_id = Column(Integer, ForeignKey('cities.id'), nullable=False,
                     comment='Идентификатор города')
    name = Column(String(200), nullable=False, unique=True,
                  comment='Наименование медицинского центра')
    address = Column(String(200), nullable=False,
                     comment='Адрес медицинского центра')
    longitude = Column(Float, nullable=True,
                       comment='Долгота в градусах')
    latitude = Column(Float, nullable=True,
                      comment='Широта в градусах')
    description = Column(Text, nullable=True,
                         comment='Описание медицинского центра')
    inn = Column(String(20), nullable=False,
                 comment='ИНН (индивидуальный номер налогоплательщика)')
    bank_bic = Column(String(20), nullable=False,
                      comment='БИК банка')
    settlement_account = Column(String(40), nullable=False,
                                comment='Расчетный счет медитцинского центра')
    correspondent_account = Column(String(40), nullable=False,
                                   comment='Корреспондентский счет медицинского центра')
    kpp = Column(String(40), nullable=False,
                 comment='Код КПП медицинского центра')
    is_active = Column(Boolean, default=True,
                       comment='Флаг активен/не активен')
    logo = Column(String(200), nullable=True,
                  comment='Ссылка на логотип медцентра')
    website_url = Column(String(200), nullable=True,
                         comment='Ссылка на веб-сайт медцентра')
    phone_fax = Column(String(25), nullable=False,
                       comment='Основной телефон-факс медцентра')
    dms_phone = Column(String(25), nullable=True,
                       comment='Телефон для клиентов страховых компаний, имеющих полис ДМС')
    work_time = Column(String(200), nullable=False,
                       comment='Время работы медцентра')
    collection_tests_time = Column(String(200), nullable=True,
                                   comment='Время забора анализов')
    vaccination_time = Column(String(200), nullable=True,
                                     comment='Время забора анализов')
    lpu_id = Column(Integer, ForeignKey('lpus.id'), nullable=True,
                     comment='Идентификатор лпу')
    show_in_lk = Column(Boolean, nullable=True,
                        comment='Флаг показывать в ЛК/не показывать в ЛК')
    email = Column(String(200), nullable=True,
                   comment='Электронная почта пользователя')
    sno = Column(Integer, nullable=True, default=0,
                 comment='Код системы налогообложения')

    city = relationship(CityTable, lazy='joined')
    lpu = relationship(LpuTable, lazy='joined')

    def __str__(self):
        return f'{self.name}, {self.address}'

    def as_dict(self):
        """Представить в виде словаря"""
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class UserTable(Base):
    """Модель User. Утверждённая"""

    __tablename__ = "users"
    __table_args__ = {
        'comment': 'Таблица "Пользователи"'
    }
    hasher= CryptContext(schemes=['bcrypt'])

    id = Column(Integer,
                primary_key=True,
                index=True)
    client_id = Column(BigInteger, nullable=True, index=True, unique=True,
                       comment='Идентификатор карточки пользователя в системе клиента')
    first_name = Column(String(100), nullable=True,
                        comment='Имя пользователя')
    last_name = Column(String(100), nullable=True,
                       comment='Фамилия пользователя')
    patronymic = Column(String(100), nullable=True,
                        comment='Отчество пользователя (если есть)')
    birth_date = Column(Date, nullable=True,
                        comment='Дата рождения пользователя')
    gender = Column(String(1), nullable=True,
                    comment='Пол пользователя')
    email = Column(String(200), nullable=True,
                   comment='Электронная почта пользователя')
    phone_number = Column(String(25), nullable=False,
                          comment='Номер телефона пользователя')
    additional_phone_number = Column(String(25), nullable=True,
                                     comment='Дополнительный номер телефона пользователя')
    doc_type = Column(Integer, nullable=True,
                      comment='Тип документа, удостоверяющего личность')
    doc_series = Column(String(50), nullable=True,
                        comment='Серия документа, удостоверяющего личность)')
    doc_number = Column(String(50), nullable=True,
                        comment='Номер документа, удостоверяющего личность)')
    doc_giving_dep_name = Column(String(200), nullable=True,
                                 comment='Наименование департамента, выдавшего документ)')
    doc_giving_dep_code = Column(String(50), nullable=True,
                                 comment='Код департамента, выдавшего документ)')
    doc_date = Column(DateTime, nullable=True,
                      comment='Дата выдачи документа')
    doc_reg_address = Column(String(500), nullable=True,
                             comment='Адрес регистрации, указанный в документе)')
    snils = Column(String(20), nullable=True,
                   comment='СНИЛС)')
    inn = Column(String(20), nullable=True,
                 comment='ИНН)')
    city_id = Column(Integer, ForeignKey('cities.id'), nullable=True,
                     comment='Идентификатор города')
    address_full = Column(String(1000), nullable=True,
                          comment='Полный адрес')
    address_mis_kladr_id = Column(Integer, ForeignKey('address_mis_kladr.id'), nullable=True,
                                  comment='Идентификатор адреса пользователя')
    longitude = Column(Float, nullable=True,
                       comment='Долгота в градусах')
    latitude = Column(Float, nullable=True,
                      comment='Широта в градусах')
    zone_number = Column(Integer, nullable=True,
                         comment='Номер зоны')
    default_medical_center_id = Column(Integer, ForeignKey('medical_centers.id'), nullable=True,
                                       comment='Идентификатор медицинского центра, выбранного по умолчанию')
    login_phone_number = Column(String(25), nullable=True, unique=True,
                                comment='Номер телефона пользователя, используемый в качестве логина')
    password = Column(String(500), nullable=True,
                      comment='Пароль для авторизации')
    is_verified = Column(Boolean, default=False,
                         comment='Флаг пользователь верефицирован/не верефицирован')
    info_way_id = Column(Integer, ForeignKey('information_ways.id'), nullable=True,
                                             comment='Канал поступления к пользователю информации о клинике')
    notification_time = Column(Time, nullable=True,
                               comment='Предпочтительное время информирования')
    pref_notification_contact_id = Column(Integer, ForeignKey('users.id'), nullable=True,
                                          comment='Идентификатор пользователя, контакт которого будет использован при информировании')
    is_active = Column(Boolean, default=True,
                       comment='Флаг активный/не активный')
    created = Column(DateTime, default=datetime.now(),
                     comment='Дата создания записи пользователя')
    medical_card_number = Column(BigInteger, nullable=True,
                                 comment='Номер медицинмкой карты')

    city = relationship(CityTable, lazy='joined')
    default_medical_center = relationship('MedicalCenterTable', lazy='joined')
    info_way = relationship('InformationWayTable', lazy='joined')
    pref_notification_contact = relationship(
        'UserTable', remote_side=id, backref='sub_users'
    )
    address_mis_kladr = relationship(AddressMisKladrTable, lazy='joined')


    def set_login_phone_number(self, phone_number):
        """Установить номер телефона в качестве логина"""
        self.login_phone_number = phone_number

    def set_password(self, password):
        """Установить пароль"""
        self.password = self.hasher.hash(password)

    def set_random_password(self):
        """Установить случайный пароль"""
        self.password = self.hasher.hash(secrets.token_hex(nbytes=5))

    def set_is_active_false(self):
        """Установить флаг is_active в False"""
        self.is_active = False

    def set_is_active_true(self):
        """Установить флаг is_active в True"""
        self.is_active = True

    def set_is_verified_false(self):
        """Установить флаг is_verified в False"""
        self.is_verified = False

    def set_is_verified_true(self):
        """Установить флаг is_verified в True"""
        self.is_verified = True

    def set_capitalize_fio(self):
        """Установка заглавных букв для ФИО"""
        if self.first_name:
            self.first_name = self.first_name.capitalize()
        if self.last_name:
            self.last_name = self.last_name.capitalize()
        if self.patronymic:
            self.patronymic = self.patronymic.capitalize()

    def as_dict(self):
        """Представить в виде словаря"""
        return {c.name: getattr(self, c.name)
                if not isinstance(getattr(self, c.name), date)
                else getattr(self, c.name).strftime("%Y-%m-%d")
                for c in self.__table__.columns}

    def fio(self):
        """Получение ФИО пользователя"""
        user_fio = ''
        if self.last_name:
            self.last_name = self.last_name.capitalize()
            user_fio += f'{self.last_name} '
        if self.first_name:
            self.first_name = self.first_name.capitalize()
            user_fio += f'{self.first_name} '
        if self.patronymic:
            self.patronymic = self.patronymic.capitalize()
            user_fio += f'{self.patronymic}'
        return user_fio.strip()


class AdminUserTable(Base):
    """Модель AdminUser"""

    __tablename__ = "admin_users"
    hasher= CryptContext(schemes=['bcrypt'])

    id = Column(Integer,
                primary_key=True,
                index=True)
    email = Column(String(100), nullable=False)
    mobile = Column(String(25), nullable=False, unique=True)
    password = Column(String(200), nullable=False)
    first_name = Column(String(100), nullable=True)
    last_name = Column(String(100), nullable=True)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    is_superuser = Column(Boolean, default=False)
    created = Column(DateTime(timezone=True), default=datetime.now())
    birth_date = Column(Date, nullable=True)
    gender = Column(String(1), nullable=True)

    last_login = Column(DateTime, nullable=True)
    last_visit = Column(DateTime, nullable=True)

    def set_password(self, password):
        """Установить пароль"""
        self.password = self.hasher.hash(password)

    def set_is_active_false(self):
        """Установить флаг is_active в False"""
        self.is_active = False

    def set_is_superuser_false(self):
        """Установить флаг is_superuser в False"""
        self.is_superuser = False

    def set_is_active_true(self):
        """Установить флаг is_active в True"""
        self.is_active = True

    def set_is_superuser_true(self):
        """Установить флаг is_superuser в True"""
        self.is_superuser = True

    def set_is_verified_false(self):
        """Установить флаг is_verified в False"""
        self.is_verified = False

    def set_is_verified_true(self):
        """Установить флаг is_verified в True"""
        self.is_verified = True

    def set_last_login(self):
        """Установить время последнего входа пользователя"""
        self.last_login = str(datetime.now())

    def set_last_visit(self):
        """Установить время последнего посещения"""
        self.last_visit = str(datetime.now())


class InformationWayTable(Base):
    """Модель InformationWay - каналы поступления информации. Утверждённая"""

    __tablename__ = "information_ways"
    __table_args__ = {
        'comment': 'Таблица "Каналы поступления информации"'
    }

    id = Column(Integer,
                primary_key=True,
                index=True)
    client_id = Column(BigInteger, nullable=True, index=True, unique=True,
                       comment='Идентификатор канала поступления информации в системе клиента')
    name = Column(String(200), nullable=False,
                  comment='Наименование')
    description = Column(Text, nullable=True,
                         comment='Описание')
    is_active = Column(Boolean, default=True,
                       comment='Флаг активно/неактивно')


class NotificationWayTable(Base):
    """Модель NotificationWay - каналы рассылки уведомлений. Утверждённая"""

    __tablename__ = "notifications_ways"
    __table_args__ = {
        'comment': 'Таблица "Каналы рассылки уведомлений"'
    }

    id = Column(Integer,
                primary_key=True,
                index=True)
    client_id = Column(BigInteger, nullable=True, index=True, unique=True,
                       comment='Идентификатор канала рассылки уведомлений в системе клиента')
    name = Column(String(200), nullable=False,
                  comment='Наименование')
    description = Column(Text, nullable=True,
                         comment='Описание')
    is_active = Column(Boolean, default=True,
                       comment='Флаг активно/неактивно')


class UserNotificationWay(Base):
    """Модель UserNotificationWay - каналы рассылки уведомлений пользователей. Утверждённая"""

    __tablename__ = "users_notifications_ways"
    __table_args__ = {
        'comment': 'Таблица "Каналы рассылки уведомлений пользователей"'
    }

    id = Column(Integer,
                primary_key=True,
                index=True)
    client_id = Column(BigInteger, nullable=True, index=True, unique=True,
                       comment='Идентификатор канала рассылки уведомлений в системе клиента')
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False,
                                          comment='Идентификатор пользователя')
    notification_way_id = Column(Integer, ForeignKey('notifications_ways.id'), nullable=False,
                                                     comment='Идентификатор канал рассылки уведомлений пользователю')

    user = relationship('UserTable', lazy='joined')


class RelationshipDegreesTable(Base):
    """Модель RelationshipDegrees. Утвержденная"""

    __tablename__ = "relationship_degreeses"
    __table_args__ = {
        'comment': 'Таблица "Степени родства"'
    }

    id = Column(Integer,
                primary_key=True,
                index=True)
    client_id = Column(BigInteger, nullable=True, index=True, unique=True,
                       comment='Идентификатор степени родства в системе клиента')
    name = Column(String(10), nullable=False,
                  comment='Наименование степени родства: отец, мать, сын, дочь, опекун, подопечный, другой')
    description = Column(Text, nullable=True,
                         comment='Описание')
    is_active = Column(Boolean, default=True,
                       comment='Флаг активно/неактивно')
    mis_sort_field = Column(Integer, default = 0,
                    comment='Поле для сортировки на стороне МИС')


class UserRelativeTable(Base):
    """Модель RelationshipDegrees. Утвержденная"""

    __tablename__ = "users_relatives"
    __table_args__ = {
        'comment': 'Таблица "Родственники пользователя"'
    }

    id = Column(Integer,
                primary_key=True,
                index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False,
                                          comment='Идентификатор пользователя')
    client_id = Column(BigInteger, nullable=True, index=True, unique=True,
                       comment='Идентификатор степени родства в системе клиента')
    relative_id = Column(Integer, ForeignKey('users.id'), nullable=False,
                                             comment='Идентификатор родственника пользователя')
    relationship_degree_id = Column(Integer, ForeignKey('relationship_degreeses.id'), nullable=False,
                                    comment='Идентификатор родственной связи')
    extra_rights = Column(Boolean, default=False,
                          comment='Флаг - дополнительные права - это права на просмотр результатов лечения - есть/нет')
    block_status = Column(Boolean, default=True,
                          comment='Флаг - статус блокировки, если пользователь отказывается предоставлять доступ к своему аккаунту родственнику,- вкл/выкл')

    user = relationship('UserTable', foreign_keys=[user_id], lazy='joined')
    relative = relationship('UserTable', foreign_keys=[relative_id], lazy='joined')
    relationship_degree = relationship('RelationshipDegreesTable', lazy='joined')

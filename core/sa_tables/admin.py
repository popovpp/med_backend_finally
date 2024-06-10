from datetime import datetime
from sqlalchemy import (Column, String, Integer, ForeignKey, BigInteger,
                        Time, Text)
from sqlalchemy.orm import relationship
from passlib.context import CryptContext

from ..config.db import Base


class UserAdminTable(Base):
    """Модель UserAdmin."""

    __tablename__ = "users_admin"
    __table_args__ = {
        'comment': 'Таблица администрирования таблицы users'
    }

    id = Column(Integer,
                primary_key=True,
                index=True)
    client_id = Column(BigInteger, nullable=True, index=True, unique=True,
                       comment='Идентификатор записи в таблице администрирования в системе клиента')
    user_id = Column(Integer, ForeignKey('users.id'), nullable=True, unique=True,
                                         comment='Идентификатор пользователя')
    registration_visible_fields = Column(String, nullable=True,
                                         comment='Строка, содержащая через "," наименование отображаемых полей')
    registration_required_fields = Column(String, nullable=True,
                                          comment='Строка, содержащая через "," наименование обязательных полей')

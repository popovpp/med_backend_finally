from pydantic import BaseModel
from typing import Optional


class ErrorField(BaseModel):

    field: str = 'Название поля'
    message: Optional[str] = 'Сообщение с ошибкой'


class Error(BaseModel):

    detail: str = 'Ошибка'
    errors: Optional[list[ErrorField]]


class ErrorNotFound(BaseModel):
    detail: str = 'Не найдено'


class ErrorAction(BaseModel):
    detail: str = 'Ошибка в действии'


class Success(BaseModel):

    detail: str = 'ОК'


class ErrorUnauthorized(BaseModel):
    detail: str = 'Не авторизован'

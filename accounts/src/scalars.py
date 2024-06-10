import strawberry
from typing import Optional, List
from datetime import datetime, time

from core.config.validators import LoginEmail
from core.config.scalars import RequestResult, RelationshipDegreesIn, UserRelativeIn, UserIn
from core.config.mapped_scalars import (User, RelationshipDegrees, UserRelative)


@strawberry.type
class Token:
    token: str


@strawberry.type
class LoginResult(RequestResult):
    data: Optional[Token] = None


@strawberry.input
class PatientUpdate:
    client_id: Optional[int] = None
    id: Optional[int] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    patronymic: Optional[str] = None
    birth_date: Optional[str] = None
    gender: Optional[str] = None
    email: Optional[str] = None
    phone_number: str
    additional_phone_number: Optional[str] = None
    doc_type: Optional[str] = None
    doc_series: Optional[str] = None
    doc_number: Optional[str] = None
    doc_giving_dep_name: Optional[str] = None
    doc_giving_dep_code: Optional[str] = None
    doc_date: Optional[datetime] = None
    doc_reg_address: Optional[str] = None
    snils: Optional[str] = None
    inn: Optional[str] = None
    city_id: Optional[int] = None
    address_mis_kladr_id: Optional[int] = None
    longitude: Optional[float] = None
    latitude: Optional[float] = None
    default_medical_center_id: Optional[int] = None
    login_phone_number: Optional[str] = None
    password: Optional[str] = None
    info_way_id: Optional[int] = None
    notification_time: Optional[time] = None
    pref_notification_contact_id: Optional[int] = None
    # relative_id: Optional[int] = None
    # relative_type_id: Optional[int] = None

    def vaildation(self):
        if self.gender:
            if not isinstance(self.gender, str) and len(self.gender) >1:
                return RequestResult(status_code=422, details='Поле "gender" не должно быть длинне 1 символа')
            if self.gender.lower() not in ('м', 'ж'):
                return RequestResult(status_code=422, details='Поле "gender" должно содержать "м" или "ж"')
            else:
                if self.gender == 'м':
                    self.gender = '0'
                elif self.gender == 'ж':
                    self.gender = '1'
        if self.email:
            LoginEmail(login=self.email)
        if self.phone_number or self.phone_number.strip() == '':
            if not isinstance(self.phone_number, str) or not self.phone_number.isdigit():
                return RequestResult(status_code=422, details='Поле "phone_number" не должно содержать других символов, кроме цифр')
        if self.login_phone_number != None:
            if self.login_phone_number or self.login_phone_number.strip() == '':
                if not isinstance(self.login_phone_number, str) or not self.login_phone_number.isdigit():
                    return RequestResult(status_code=422, details='Поле "login_phone_number" не должно содержать других символов, кроме цифр')
        if self.additional_phone_number != None:
            if self.additional_phone_number or self.additional_phone_number.strip() == '':
                if not isinstance(self.additional_phone_number, str) or not self.additional_phone_number.isdigit():
                    return RequestResult(status_code=422, details='Поле "additional_phone_number" не должно содержать других символов, кроме цифр.')
        if self.password:
            if not isinstance(self.password, str) or len(self.password) < 8:
                return RequestResult(status_code=422, details='Длина поля "password" менее 8-ми символов')
        if self.birth_date:
            birth_date = datetime.strptime(self.birth_date, "%Y-%m-%d").date()

        return RequestResult(
            status_code=200,
            details='Ok'
        )


@strawberry.input
class PatientRegistration(PatientUpdate):
    default_medical_center_id: int
    relative_id: Optional[int] = None
    relative_type_id: Optional[int] = None


@strawberry.input
class FlashCallCode:
    login_phone_number: str
    code: str

    def vaildation(self):
        if not isinstance (self.login_phone_number, str) or not self.login_phone_number.isdigit():
            return RequestResult(status_code=422, details='Поле "phone_number" не должно содержать других символов, кроме цифр')
        len_code = len(self.code)
        if not isinstance (self.code, str) or len_code != 4:
            return RequestResult(status_code=422, details='Поле "code" не соответствует установленным требованиям')

        return RequestResult(
            status_code=200,
            details='Ok'
        )


@strawberry.type
class UserView(User):
    client_id: Optional[str] = None


@strawberry.type
class UserData(RequestResult):
    data: Optional[UserView]


@strawberry.input
class RelationshipDegreesInput(RelationshipDegreesIn):
    id: Optional[List[int]] = None


@strawberry.input
class UserRelativeInput(UserRelativeIn):
    id: Optional[List[int]] = None


@strawberry.input
class UserInput(UserIn):
    client_id: Optional[int] = None
    city_id: Optional[int] = None
    address_mis_kladr_id: Optional[int] = None
    default_medical_center_id: Optional[int] = None
    info_way_id: Optional[int] = None
    pref_notification_contact_id: Optional[int] = None

    def vaildation(self):
        if self.gender:
            if not isinstance(self.gender, str) and len(self.gender) >1:
                return RequestResult(status_code=422, details='Поле "gender" не должно быть длинне 1 символа')
            if self.gender.lower() not in ('м', 'ж'):
                return RequestResult(status_code=422, details='Поле "gender" должно содержать "м" или "ж"')
            else:
                if self.gender == 'м':
                    self.gender = '0'
                elif self.gender == 'ж':
                    self.gender = '1'
        if self.email:
            LoginEmail(login=self.email)
        if self.login_phone_number:
            if not isinstance(self.login_phone_number, str) or not self.login_phone_number.isdigit():
                return RequestResult(status_code=422, details='Поле "login_phone_number" не должно содержать других символов, кроме цифр')
        if self.additional_phone_number:
            if self.additional_phone_number is not None:
                if not isinstance(self.additional_phone_number, str) or not self.additional_phone_number.isdigit():
                    return RequestResult(status_code=422, details='Поле "additional_phone_number" не должно содержать других символов, кроме цифр.')
        if self.password:
            if not isinstance(self.password, str) or len(self.password) < 8:
                return RequestResult(status_code=422, details='Длина поля "password" менее 8-ми символов')
        # if self.birth_date:
        #     birth_date = datetime.strptime(self.birth_date, "%Y-%m-%d").date()

        return RequestResult(
            status_code=200,
            details='Ok'
        )


@strawberry.type
class RelationshipDegreesResult(RequestResult):
    data: Optional[List[RelationshipDegrees]]


@strawberry.type
class UserRelativeResult(RequestResult):
    data: Optional[List[UserRelative]]


@strawberry.type
class UserRelativeShort:
    user_id: Optional[int] = None
    client_id: Optional[int] =None
    relative_id: Optional[int] = None
    relationship_degree_id: Optional[int] = None
    extra_rights:Optional[bool] = None
    block_status: Optional[bool] = None


@strawberry.type
class UserRelativeShortResult(RequestResult):
    data: Optional[List[UserRelativeShort]]


@strawberry.type
class UserResult(RequestResult):
    data: Optional[User]

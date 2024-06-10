import strawberry
import json
import hashlib
import typing
from strawberry.types import Info
from kafka import KafkaProducer
from typing import Optional
from fastapi import Request, WebSocket

from core.config.cache_connector import CacheConnector
from core.config.settings import EXP_TIME_FOR_FLASH_CALL_DATA
from core.authorization.auth import Auth
from core.authorization.permissions import IsAuthenticated, get_auth_user_by_auth_header
from core.sa_tables.accounts import RelationshipDegreesTable, UserRelativeTable
from core.config.scalars import RequestResult
from core.src.common_resolvers import getting_objs
from .utils import flash_code_generator, multi_clicking_protection
from .scalars import (LoginResult, FlashCallCode, Token, UserData, RelationshipDegreesInput,
                      RelationshipDegreesResult, UserRelativeResult, UserRelativeInput)
from .resolvers import getting_user_data


hasher= hashlib.sha256
cache = CacheConnector()


@strawberry.type
class QueryUser:
    @strawberry.field
    async def patien_login_by_password(self, info:Info, login_phone_number: str, password: str) -> LoginResult:

        """Авторизация посредством логина и пароля"""

        login = login_phone_number.strip()
        password = password.strip()

        # Валидация поля phone_number
        if not isinstance (login_phone_number, str) or not login_phone_number.isdigit():
            return LoginResult(
                status_code=422,
                details='Поле "phone_number" не должно содержать других символов, кроме цифр'
            )

        auth_handler = Auth()

        user = await auth_handler.get_auth_user_by_login(login)

        if not user:
            return LoginResult(status_code=404, details='Пользователь не найден')

        is_verified = await auth_handler.verify_password(password, user.password)

        if not is_verified:
            return LoginResult(status_code=401, details=f'Неверный пароль, попробуйте еще раз.')

        token = await auth_handler.encode_token(user.login_phone_number, user.password)

        return LoginResult(
            data=Token(token=token),
            status_code=200,
            details='Ok'
        )


    @strawberry.field
    async def patient_login_by_phone(self, info:Info, login_phone_number: str) -> LoginResult:

        """Авторизация через телефон потльзователя с использованием процедуры Flash-call"""

        # Валидация поля phone_number
        if not isinstance (login_phone_number, str) or not login_phone_number.isdigit():
            return LoginResult(
                status_code=422,
                details='Поле "login_phone_number" не должно содержать других символов, кроме цифр'
            )

        login = login_phone_number.strip()

        auth_handler = Auth()

        user = await auth_handler.get_auth_user_by_login(login)

        if not user:
            return LoginResult(status_code=404, details='Пользователь не найден')
        
        if not await multi_clicking_protection(user, info):
            return LoginResult(status_code=422, details='Следующее подтверждение по СМС доступно через 1 минуту')

        producer = KafkaProducer(
            bootstrap_servers=['kafka:9092'],
            acks=1,
            linger_ms=40,
            value_serializer=lambda m: json.dumps(m).encode('ascii')
        )

        ver_code = await flash_code_generator()
        key = str(hasher(f'{user.login_phone_number}{ver_code}'.encode()).hexdigest())
        cache.set(
            key,
            user.login_phone_number,
            EXP_TIME_FOR_FLASH_CALL_DATA
        )

        try:
            producer.send('flash-call-topic', {'phone':user.login_phone_number, 'code': ver_code})
        except Exception as e:
            print(e)
            return LoginResult(status_code=422,
                               details=f'Функция входа по телефону временно недоступна. Воспользуйтесь входом при помощи пароля или повторите попытку позже.')

        result = LoginResult(status_code=200,
                             details=f'Инициирована процедура Flash Call')
        return result


    @strawberry.field()
    async def login_flash_call_code(
        self,
        info:Info,
        flash_call_code: FlashCallCode
    ) -> LoginResult:
        """
        Передача flash-call кода пользователя
        """

        auth_handler = Auth()

        # Валидация
        result = flash_call_code.vaildation()
        if result.status_code != 200:
            return result

        user = await auth_handler.get_auth_user_by_login(flash_call_code.login_phone_number)

        if not user:
            return LoginResult(status_code=404, details='Пользователь не найден')

        key = str(hasher(f'{flash_call_code.login_phone_number.strip()}{flash_call_code.code.strip()}'.encode()).hexdigest())

        patient_login_phone_number = cache.get(key)

        if patient_login_phone_number != user.login_phone_number:
            return LoginResult(status_code=404,
                               details=f'От пользователя получен неверный код')

        token = await auth_handler.encode_token(user.login_phone_number, user.password)

        return LoginResult(
            data=Token(token=token),
            status_code=200,
            details='Ok'
        )

    @strawberry.field(permission_classes=[IsAuthenticated])
    async def get_user_data(self, info:Info) -> UserData:

        """Получение данных авторизованного пользователя (своих данных)"""

        user, _ = await get_auth_user_by_auth_header(info)

        result = await getting_user_data(info, user)

        return UserData(
            data=result,
            status_code=200,
            details='Ok'
        )

    @strawberry.field
    async def guest_login(self) -> LoginResult:
        """Получение токена гостевого пользователя"""

        auth_handler = Auth()

        token = await auth_handler.encode_token('guest', 'guest')

        return LoginResult(
            data=Token(token=token),
            status_code=200,
            details='Ok'
        )

    @strawberry.field
    async def admin_login_by_password(self, info:Info, mobile: str, password: str) -> LoginResult:

        """Авторизация посредством логина и пароля"""

        login = mobile.strip()
        password = password.strip()

        # Валидация поля mobile
        if not isinstance (mobile, str) or not mobile.isdigit():
            return LoginResult(
                status_code=422,
                details='Поле "mobile" не должно содержать других символов, кроме цифр'
            )

        auth_handler = Auth()

        user = await auth_handler.get_admin_user_by_login(login)

        if not user:
            return LoginResult(status_code=404, details='Пользователь не найден')

        is_verified = await auth_handler.verify_password(password, user.password)

        if not is_verified:
            return LoginResult(status_code=401, details=f'Невалидный пароль для пользователя {user.email}')

        token = await auth_handler.encode_token(user.mobile, user.password)

        return LoginResult(
            data=Token(token=token),
            status_code=200,
            details='Ok'
        )

    @strawberry.field(permission_classes=[IsAuthenticated])
    async def get_relationship_degrees(self,
                                       info:Info,
                                       filtering_attrs: Optional[RelationshipDegreesInput] = None,
                                       ordering_attrs: Optional[RelationshipDegreesInput] = None,
                                       skip: Optional[int] = 1,
                                       limit: Optional[int] = 1000,
                                       desc_sorting: Optional[bool] = None) -> RelationshipDegreesResult:

        """Получение степеней родства"""

        user, _ = await get_auth_user_by_auth_header(info)

        result_list, records_count, pages_count = await getting_objs(info, user, RelationshipDegreesTable,
                                                                     filtering_attrs,
                                                                     ordering_attrs,
                                                                     skip,
                                                                     limit,
                                                                     desc_sorting)

        return RelationshipDegreesResult(
            data=result_list,
            records_count=records_count,
            pages_count=pages_count,
            status_code=200,
            details='Ok'
        )

    @strawberry.field(permission_classes=[IsAuthenticated])
    async def get_user_relatives(
        self,
        info:Info,
        filtering_attrs: Optional[UserRelativeInput] = None,
        ordering_attrs: Optional[UserRelativeInput] = None,
        skip: Optional[int] = 1,
        limit: Optional[int] = 1000,
        desc_sorting: Optional[bool] = None
    ) -> UserRelativeResult:
        """Получение списка родственников пользователя"""

        user, _ = await get_auth_user_by_auth_header(info)

        if filtering_attrs:
            filtering_attrs.user_id = user.id
        else:
            filtering_attrs = UserRelativeInput(
                user_id=user.id
            )

        result_list, records_count, pages_count = await getting_objs(info, user, UserRelativeTable,
                                                                     filtering_attrs,
                                                                     ordering_attrs,
                                                                     skip,
                                                                     limit,
                                                                     desc_sorting)

        return UserRelativeResult(
            data=result_list,
            records_count=records_count,
            pages_count=pages_count,
            status_code=200,
            details='Ok'
        )

    @strawberry.field(permission_classes=[IsAuthenticated])
    async def get_user_ip(
        self,
        info:Info
    ) -> RequestResult:
        """Получение ip пользователя"""

        user, _ = await get_auth_user_by_auth_header(info)

        request: typing.Union[Request, WebSocket] = info.context["request"]

        return RequestResult(
            data=request.headers['Host'],
            status_code=200,
            details='Ok'
        )

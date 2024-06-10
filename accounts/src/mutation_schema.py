import strawberry
import json
import hashlib
import logging
import xmltodict
from strawberry.types import Info
from kafka import KafkaProducer
from typing import Optional

from core.config.scalars import RequestResult
from core.config.cache_connector import CacheConnector
from core.config.settings import EXP_TIME_FOR_FLASH_CALL_DATA, EXP_TIME_FOR_EMAIL_DATA
from core.sa_tables.accounts import UserRelativeTable,UserTable
from core.authorization.auth import Auth
from core.src.common_resolvers import getting_relatives_ids, getting_objs
from core.authorization.permissions import IsAuthenticated, get_auth_user_by_auth_header, IsAuthenticatedOrGuest
from core.src.common_resolvers import deleting_obj, getting_user_relatives_ids
from oracle_connector.config.settings import ORACLE_PROC_CHECK_PATIENT, ORACLE_PROC_CONFIRM_PATIENT_BY_EMAIL
from accounts.config import settings
from .scalars import (PatientRegistration, FlashCallCode, LoginResult, UserInput, UserResult,
                      UserRelativeShortResult)
from .utils import flash_code_generator, multi_clicking_protection
from .resolvers import (patient_registration, changing_password, changing_login_phone, adding_relative,
                        email_confirmation_code_patient_update, changing_user,
                        adding_existing_relative)
                        


hasher= hashlib.sha256
cache = CacheConnector()
auth = Auth()

logging.basicConfig(
    level=logging.getLevelName(settings.LOGGING_LEVEL),
    format=settings.LOGGING_FORMAT
)


logger = logging.getLogger(__name__)


@strawberry.type
class MutationUser:

    @strawberry.field(permission_classes=[IsAuthenticatedOrGuest])
    async def patient_registration(
        self,
        info:Info,
        patient: PatientRegistration
    ) -> RequestResult:
        """
        Запрос на регистрацию пользователя
        """

        # Валидация
        result = patient.vaildation()
        if result.status_code != 200:
            return result

        if patient.login_phone_number is None:
            patient.login_phone_number = patient.phone_number

        patient.relative_type_id = None

        print('#######################', patient.relative_type_id)

        user = await auth.get_auth_user_by_login(patient.login_phone_number)

        if user is not None:
            return RequestResult(status_code=422,
                details=f'По данному номеру телефона уже существует запись в Личном кабинете. Вы можете, войти в Личный кабинет при опции "Без пароля".',
                details_ru=f'По данному номеру телефона уже существует запись в Личном кабинете. Вы можете, войти в Личный кабинет при опции "Без пароля".'
            )

        user_in_header, _ = await get_auth_user_by_auth_header(info)

        if not await multi_clicking_protection(user_in_header, info):
            return LoginResult(status_code=422, details='Следующее подтверждение по СМС доступно через 1 минуту')

        producer = KafkaProducer(
            bootstrap_servers=['kafka:9092'],
            acks=1,
            linger_ms=40,
            value_serializer=lambda m: json.dumps(m).encode('ascii')
        )

        ver_code = await flash_code_generator()

        key = str(hasher(f'{patient.login_phone_number}{ver_code}'.encode()).hexdigest())

        cache.set(
            key,
            json.dumps(patient.__dict__).encode(),
            EXP_TIME_FOR_FLASH_CALL_DATA
        )

        try:
            producer.send('flash-call-topic', {'phone':patient.login_phone_number, 'code': ver_code})
            producer.send('check-patient-in-oracle-topic', {'key': key})
        except Exception as e:
            print(e)
            return RequestResult(status_code=422,
                                 details=f'Operation is temporarily unavailable')

        result = RequestResult(status_code=200,
                               details=f'Flash Call has been initiated')
        return result

    @strawberry.field(permission_classes=[IsAuthenticatedOrGuest])
    async def registration_flash_call_code(
        self,
        info:Info,
        flash_call_code: FlashCallCode
    ) -> LoginResult:
        """
        Передача flash-call кода пользователя
        """

        producer = KafkaProducer(
            bootstrap_servers=['kafka:9092'],
            acks=1,
            linger_ms=40,
            value_serializer=lambda m: json.dumps(m).encode('ascii')
        )

        # Валидация
        result = flash_call_code.vaildation()
        if result.status_code != 200:
            return result

        key = str(hasher(f'{flash_call_code.login_phone_number.strip()}{flash_call_code.code.strip()}'.encode()).hexdigest())

        try:
           oracle_check_result = json.loads(cache.get(f'{key}_{ORACLE_PROC_CHECK_PATIENT}'))
        except Exception as e:
            print(e)
            oracle_check_result = None
            return LoginResult(
                status_code=422,
                details='The user code is wrong or the code lifetime has been expired. Repeat a registration.',
                details_ru='Введенный секретный код ошибочный или время его жизни истекло. Повторите регистрацию.'
            )

        if oracle_check_result and (oracle_check_result['result'] is not None):

            if oracle_check_result['result'][0] == 200:
                result = await patient_registration(flash_call_code, oracle_check_result=oracle_check_result)
            elif oracle_check_result['result'][0] == 201:

                try:
                    patient = json.loads(cache.get(key))
                except Exception as e:
                    print(e)
                    return LoginResult(
                        status_code=422,
                        details='The data lifetime has expired. Repeat the process please.'
                    )

                oracle_patient = xmltodict.parse(oracle_check_result['result'][2].lower())['data']['user']

                ver_code = await flash_code_generator()

                email_key = str(hasher(f'{patient["login_phone_number"]}{ver_code}'.encode()).hexdigest())

                cache.set(
                    email_key,
                    json.dumps({"input_patient": patient, "oracle_patient": oracle_patient}).encode(),
                    EXP_TIME_FOR_EMAIL_DATA
                )

                try:
                    producer.send('confirm-patient-by-email-oracle-topic', {
                        'key': email_key,
                        'data': {
                            'email': oracle_patient['email'],
                            'ver_code': ver_code,
                            'client_id': oracle_patient['client_id']
                        }
                    })
                    return RequestResult(status_code=201,
                                         details=f"""The same user has been discover in the MIS. He has different\
phone number. The message containung a secret code has been send to your email - {oracle_patient['email']}""",
                                         details_ru=f"""Похоже, что вы у нас уже зарегистрированы. Данные имеющиеся в\
нашей базе отличаются от введенных вами только номером телефона. На ваш почтовый ящик {oracle_patient['email']} \
направлено сообщение, содержащее секретный код. Введите этот код в форму и отправьте нам для подтверждения \
вашего аккаунта""")
                except Exception as e:
                    print(e)
                    return RequestResult(status_code=422,
                                         details='Operation is temporarily unavailable/ Repeat it later',
                                         details_ru='Операция временно недоступна. Повторите попытку позже')

            elif oracle_check_result['result'][0] == 202:
                return LoginResult(
                    status_code=422,
                    details='There are several users with same data in the MIS. Visit our clinic to resolve the issue, please.'
                )
            elif oracle_check_result['result'][0] == 404:
                result = await patient_registration(flash_call_code)
            elif oracle_check_result['result'][0] == 405:
                pass
            elif oracle_check_result['result'][0] == 500:
                return LoginResult(
                    status_code=500,
                    details='Operation is temporarily unavailable'
                )
        else:
            return LoginResult(
                status_code=500,
                details='The oracle connection is absent'
            )

        return result


    @strawberry.field(permission_classes=[IsAuthenticated])
    async def change_password_by_phone(
        self,
        info:Info,
        new_password: str
    ) -> RequestResult:
        """
        Запрос на изменение пароля пользователя с подтверждением по телефону
        """

        if not isinstance (new_password, str) or len(new_password) < 8:
            return RequestResult(status_code=422, details='Длина поля "new_password" менее 8-ми символов')

        user, _ = await get_auth_user_by_auth_header(info)

        if user is None:
            return RequestResult(status_code=422,
                details=f'Пользователь с телефоном {user.login_phone_number} не зарегистрирован в системе.'
            )
        
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
            new_password,
            EXP_TIME_FOR_FLASH_CALL_DATA
        )

        try:
            producer.send('flash-call-topic', {'phone':user.login_phone_number, 'code': ver_code})
        except Exception as e:
            return RequestResult(status_code=422,
                                 details=f'Функция изменения пароля временно недоступна. Повторите попытку позже.')

        result = RequestResult(status_code=200,
                               details=f'Инициирована процедура Flash Call')
        return result


    @strawberry.field(permission_classes=[IsAuthenticated])
    async def change_password_flash_call_code(
        self,
        info:Info,
        flash_call_code: FlashCallCode
    ) -> RequestResult:
        """
        Передача flash-call кода пользователя
        """

        # Валидация
        result = flash_call_code.vaildation()
        if result.status_code != 200:
            return result

        user, _ = await get_auth_user_by_auth_header(info)

        result = await changing_password(user, flash_call_code)

        return result


    @strawberry.field(permission_classes=[IsAuthenticated])
    async def change_login_phone_by_phone(
        self,
        info:Info,
        old_phone_number: str,
        new_phone_number: str
    ) -> RequestResult:
        """
        Запрос на изменение телефона пользователя с подтверждением по телефону
        """

        if not isinstance (old_phone_number, str) or not old_phone_number.isdigit():
            return RequestResult(status_code=422,
                                 details='Поле "old_phone_number" не должно содержать других символов, кроме цифр')

        if not isinstance (new_phone_number, str) or not new_phone_number.isdigit():
            return RequestResult(status_code=422,
                                 details='Поле "new_phone_number" не должно содержать других символов, кроме цифр')

        user, _ = await get_auth_user_by_auth_header(info)

        if user is None:
            return RequestResult(status_code=422,
                details=f'Пользователь с телефоном {user.login_phone_number} не зарегистрирован в системе.'
            )

        if user.login_phone_number != old_phone_number:
            return RequestResult(status_code=422,
                details=f'Поле old_phone_number не соответствуеи полю phone_number авторизованного пользователя.'
            )
        
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
            new_phone_number,
            EXP_TIME_FOR_FLASH_CALL_DATA
        )

        try:
            producer.send('flash-call-topic', {'phone':new_phone_number, 'code': ver_code})
        except Exception as e:
            return RequestResult(status_code=422,
                                 details=f'Функция изменения пароля временно недоступна. Повторите попытку позже.')

        result = RequestResult(status_code=200,
                               details=f'Инициирована процедура Flash Call')
        return result


    @strawberry.field(permission_classes=[IsAuthenticated])
    async def change_phone_flash_call_code(
        self,
        info:Info,
        flash_call_code: FlashCallCode
    ) -> RequestResult:
        """
        Передача flash-call кода пользователя для изменения телефона
        """

        # Валидация
        result = flash_call_code.vaildation()
        if result.status_code != 200:
            return result

        user, _ = await get_auth_user_by_auth_header(info)

        result = await changing_login_phone(user, flash_call_code)

        return result

    @strawberry.field(permission_classes=[IsAuthenticated])
    async def add_relatives(
        self,
        info:Info,
        relationship_degree_id: int,
        patient: PatientRegistration,
    ) -> UserRelativeShortResult:
        """
        Запрос на регистрацию пользователя-родственника
        """

        # Валидация
        result = patient.vaildation()
        if result.status_code != 200:
            return result

        try:
            if patient.last_name:
                patient.last_name = patient.last_name.capitalize()
            if patient.first_name:
                patient.first_name = patient.first_name.capitalize()
            if patient.patronymic:
                patient.patronymic = patient.patronymic.capitalize()
        except Exception as e:
            print(e)

        user, _ = await get_auth_user_by_auth_header(info)

        if patient.relative_type_id is None:
            return UserRelativeShortResult(
                status_code = 422,
                details="The field patient.relative_type_id is required.s",
                details_ru = 'Поле patient.relative_type_id является обязательным.'
            )

        result = await adding_relative(info, user, patient, relationship_degree_id)

        return result

    @strawberry.field(permission_classes=[IsAuthenticated])
    async def change_user(
        self,
        info: Info,
        user_changings: UserInput,
        user_id: Optional[int] = None
    ) -> UserResult:
        """
        Запрос на редактирование пользователя
        """

        # Валидация
        result = user_changings.vaildation()
        if result.status_code != 200:
            return result

        user, _ = await get_auth_user_by_auth_header(info)

         # Получаем айдишники всех родственников
        relatives_ids = await getting_relatives_ids(user.id)
        if user_id == user.id:
            pass
        else:
            if user_id not in relatives_ids:
                return UserResult(
                    status_code=422,
                    details=f'The patient with number {user_id} is not your relatives',
                    details_ru=f'Пациент с номером {user_id} не является вашим родственником'
                )
            filtering_attrs = UserInput(
                id=user_id
            )
            result_list, _, _ = await getting_objs(info, user, UserTable,
                                                   filtering_attrs)
            user = result_list[0]

        result = await changing_user(user, user_changings)

        return result

    @strawberry.field(permission_classes=[IsAuthenticatedOrGuest])
    async def patient_confirmation_code(
        self,
        info:Info,
        email_code: FlashCallCode
    ) -> LoginResult:
        """
        Передача email кода пользователя
        """

         # Валидация
        result = email_code.vaildation()
        if result.status_code != 200:
            return result

        key = str(hasher(f'{email_code.login_phone_number.strip()}{email_code.code.strip()}'.encode()).hexdigest())

        try:
           oracle_check_result = json.loads(cache.get(f'{key}_{ORACLE_PROC_CONFIRM_PATIENT_BY_EMAIL}'))
        except Exception as e:
            print(e)
            oracle_check_result = None
            return LoginResult(
                status_code=422,
                details='The user code is wrong or the code lifetime has been expired. Repeat a process.',
                details_ru='От пользователя получен неверный код или время жизни кода истекло. Посвторите процесс, пожалуйста'
            )

        if oracle_check_result and (oracle_check_result['result'] is not None):

            if oracle_check_result['result'][0] == 200:
                result = await email_confirmation_code_patient_update(key)
                return result
            else:
                return LoginResult(
                status_code=422,
                details='The user code is wrong or the code lifetime has been expired. Repeat a process.',
                details_ru='От пользователя получен неверный код или время жизни кода истекло. Посвторите процесс, пожалуйста'
            )

    @strawberry.field(permission_classes=[IsAuthenticatedOrGuest])
    async def relative_confirmation_code(
        self,
        info:Info,
        ver_code: str
    ) -> RequestResult:
        """
        Передача верификационного кода родственника
        """

        user, _ = await get_auth_user_by_auth_header(info)

        result = await adding_existing_relative(info, user, ver_code)

        return result

    @strawberry.field(permission_classes=[IsAuthenticated])
    async def delete_user_relative(
        self,
        info: Info,
        user_relative_id: int
    ) -> RequestResult:
        """
        Запрос на удаление родственной связи пользователя с пользователем user_relative_id
        """

        user, _ = await get_auth_user_by_auth_header(info)

        # Получаем айдишники всех родственных связей
        user_relatives_ids = await getting_user_relatives_ids(user.id)

        if user_relative_id not in user_relatives_ids:
            return RequestResult(
                status_code=422,
                details=f"You donn't have the relationship id = {user_relative_id}.",
                details_ru=f"У вас нет родственной связи с id = {user_relative_id}."
            )

        result = await deleting_obj(user_relative_id, UserRelativeTable)

        return result

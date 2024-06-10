import json
import hashlib
import logging
import xmltodict
from datetime import datetime, date
from sqlalchemy.future import select as async_select
from sqlalchemy import inspect, INTEGER, DATE, TIMESTAMP, DOUBLE_PRECISION, TIME, BIGINT
from kafka import KafkaProducer

from core.config.db import get_session, engine, metadata, Base
from core.config.cache_connector import CacheConnector
from core.authorization.auth import Auth

from core.config.scalars import RequestResult, UserIn, UserRelativeIn
from core.sa_tables.accounts import (UserTable, UserRelativeTable, RelationshipDegreesTable,
                                     InformationWayTable)
from core.sa_tables.main_process import (UserDefaultObjectTable, PolicyTable, ShifrTable)
from oracle_connector.scripts.oracle_connector import call_oracle_proc
from oracle_connector.config.settings import (ORACLE_PROC_UDATE_USER_PATIENT, ORACLE_PROC_CREATE_USER_PATIENT,
                                              ORACLE_PROC_CHECK_PATIENT, ORACLE_PROC_ADD_PATIENT_RELATIVE)
from core.config.settings import (EXP_TIME_FOR_FLASH_CALL_DATA, EXP_TIME_FOR_EMAIL_DATA)
from core.src.utils import (get_model_class, input_obj_constructor, input_obj_constructor_with_fk,
                            table_to_schema_constructor, input_obj_constructor_with_fk_id)
from core.src.common_resolvers import getting_objs
from oracle_connector.scripts.oracle_connector import call_oracle_proc
from accounts.config import settings
from .utils import flash_code_generator
from .scalars import (LoginResult, Token, RelationshipDegreesInput, PatientUpdate, UserResult,
                      UserRelativeResult, UserRelativeShortResult, PatientRegistration)
from accounts.config.settings import POLICY_END_DATE, POLICY_SHIFR_ID, POLICY_STATUS


cache = CacheConnector()
hasher= hashlib.sha256

logging.basicConfig(
    level=logging.getLevelName(settings.LOGGING_LEVEL),
    format=settings.LOGGING_FORMAT
)


logger = logging.getLogger(__name__)


async def patient_registration(flash_call_code, oracle_check_result=None):

    proc_name = ORACLE_PROC_CREATE_USER_PATIENT

    auth_handler = Auth()

    today = datetime.today()

    # Восстанавливаем ключ для чтения из кэша
    key = str(hasher(f'{flash_call_code.login_phone_number.strip()}{flash_call_code.code.strip()}'.encode()).hexdigest())

    patient = cache.get(key)

    if patient is None:
        return LoginResult(status_code=404,
                           details=f'The received code is wrong.')

    patient = json.loads(patient)

    new_patient = UserTable()

    # Определяем типы колонок и внешние ключи
    users_col_type_dict = {}
    users_col_id_dict = {}
    async with engine.connect() as conn:
        columns_user_table = await conn.run_sync(
            lambda sync_conn: inspect(sync_conn).get_columns('users')
        )
        for c in columns_user_table :
            users_col_type_dict[c['name']] = c['type']
    for c in metadata.tables['users'].columns:
        for fk in c.foreign_keys:
            users_col_id_dict[str(c.name)] = await get_model_class(fk.column.table.name)
    # Если None, то случай 404 (пациент не найден в МИСС), если нет, то случай 200 (пациент найден в МИСС)
    if oracle_check_result is not None:

        oracle_check_data = xmltodict.parse(oracle_check_result['result'][2].lower())

        async with get_session() as s:

            if oracle_check_data is not None:

                # Перекладываем данные из объекта oracle_check_data в объект new_patient
                for attr in UserTable.__dict__.keys():
                    try:
                        value = oracle_check_data['data']['user'][attr]
                        if value is not None:
                            if isinstance(users_col_type_dict[attr], INTEGER):
                                value = int(value)
                            elif isinstance(users_col_type_dict[attr], BIGINT):
                                value = int(value)
                            elif isinstance(users_col_type_dict[attr], DATE):
                                value = datetime.strptime(value, '%Y-%m-%d')
                            elif isinstance(users_col_type_dict[attr], TIMESTAMP):
                                value = datetime.strptime(value, '%Y-%m-%d')
                            elif isinstance(users_col_type_dict[attr], TIME):
                                value = datetime.strptime(value, '%H:%M').time()
                            elif isinstance(users_col_type_dict[attr], DOUBLE_PRECISION):
                                value = float(value)
                            try:
                                obj = (await s.execute(async_select(users_col_id_dict[attr]).filter(
                                    getattr(users_col_id_dict[attr], 'client_id', None) == value
                                ))).unique().scalars().one_or_none()
                                if obj:
                                    value = obj.id
                                else:
                                    value = None
                            except Exception:
                                pass
                            setattr(new_patient, attr, value)
                    except Exception:
                        pass
                    if new_patient.login_phone_number is None:
                        new_patient.login_phone_number = patient['login_phone_number']
                    if new_patient.password is None:
                        if patient['password'] is not None:
                            new_patient.set_password(patient['password'])
                        else:
                            new_patient.set_random_password()
                    if new_patient.info_way_id:
                        new_patient.info_way_id = (await s.execute(async_select(
                            InformationWayTable.id
                        ).filter(
                            InformationWayTable.client_id == int(new_patient.info_way_id)
                        ))).scalars().one_or_none()

    else:
        await input_obj_constructor(UserTable, new_patient, patient)

        if patient['password'] is not None:
            new_patient.set_password(patient['password'])
        else:
            new_patient.set_random_password()
        new_patient.set_is_active_true()

    new_patient.set_capitalize_fio()

    try:
        # Записываем пациента в базу
        async with get_session() as s:
            s.add(new_patient)
            await s.flush()
            # Записываем в базу пациента по умолчанию и медцентр по умолчанию
            new_default_patient = UserDefaultObjectTable(
                user_id=new_patient.id,
                default_patient_id=new_patient.id,
                default_medical_center_id=new_patient.default_medical_center_id
            )
            s.add(new_default_patient)
            await s.flush()

            patient['id'] = new_patient.id
            patient['client_id'] = new_patient.client_id

            # Вызываем процедуру создания пациента в МИСС
            data_for_oracle = [value for key, value in patient.items()]
            oracle_create_result = await call_oracle_proc(data_for_oracle, proc_name)
            if oracle_create_result is not None:
                oracle_create_data = xmltodict.parse(oracle_create_result[2].lower())
            if oracle_create_result[0] == 200:
                if oracle_create_data['data'] is not None:
                    client_id = int(oracle_create_data['data']['user_id'])
                    if new_patient.client_id is None or new_patient.client_id == client_id:
                        new_patient.client_id = client_id
                        s.add(new_patient)
                        await s.flush()
                        # Создаем новому пациенту первичный полис
                        new_policy = PolicyTable(
                            client_id=int(oracle_create_data['data']['policies_id']),
                            user_id=new_patient.id,
                            shifr_id=POLICY_SHIFR_ID,
                            start_date=today,
                            end_date=datetime.strptime(POLICY_END_DATE, '%d.%m.%Y'),
                            status=POLICY_STATUS
                        )
                        s.add(new_policy)
                        await s.commit()
                        # Выдаем токен авторизации
                        return LoginResult(
                            data = Token(token = await auth_handler.encode_token(new_patient.login_phone_number, new_patient.password)),
                            details='Ok',
                            status_code=200
                        )
                    else:
                        await s.rollback()
                        return LoginResult(
                            status_code=500,
                            details="There are different the pg users' client_id and the miss' users client_id "
                        )
                else:
                    await s.rollback()
                    return LoginResult(
                        status_code=500,
                        details="MISS didn't return client_id for registrated user"
                    )
            else:
                await s.rollback()
                return LoginResult(
                    status_code=500,
                    details="MISS didn't return any data after request"
                )
    except Exception as e:
        await s.rollback()
        return LoginResult(
                    status_code=500,
                    details=f"The error '{e}' has been got. You need to repeat the registration.",
                    details_ru=f"Получена ошибка '{e}'. Повторите регистрацию."
                )


async def changing_password(user, flash_call_code):

    key = str(hasher(f'{flash_call_code.login_phone_number.strip()}{flash_call_code.code.strip()}'.encode()).hexdigest())

    new_password = cache.get(key)

    if new_password is None:
        return RequestResult(status_code=404,
                             details=f'От пользователя получен неверный код')

    async with get_session() as s:
        try:
            user.set_password(new_password)
            s.add(user)
            await s.commit()
            result = RequestResult(
                details='Ok',
                status_code=200
            )
        except Exception as e:
            print(e)
            result = RequestResult(
                status_code=422,
                details=f'Изменение пароля для {user.login_phone_number} временно недоступно, повторите попытку позже.'
            )

    return result


async def changing_login_phone(user, flash_call_code):

    key = str(hasher(f'{flash_call_code.login_phone_number.strip()}{flash_call_code.code.strip()}'.encode()).hexdigest())

    new_phone = cache.get(key)

    if new_phone is None:
        return RequestResult(status_code=404,
                             details=f'От пользователя получен неверный код')

    async with get_session() as s:
        try:
            user.login_phone_number = new_phone
            s.add(user)
            await s.commit()
            result = RequestResult(
                details='Ok',
                status_code=200
            )
        except Exception as e:
            print(e)
            result = RequestResult(
                status_code=422,
                details=f'Изменение телефонного номера для {user.login_phone_number} временно недоступно, повторите попытку позже.'
            )

    return result


async def getting_user_data(info, user):

    async with get_session() as s:

        result_sql = async_select(UserTable).filter(UserTable.id == user.id)

        result = (await s.execute(result_sql)).unique().scalars().one_or_none()

    return result


async def adding_relative(info, user, patient, relationship_degree_id):
    """Добавление пациента-родственника"""

    # proc_name = ORACLE_PROC_CREATE_USER_PATIENT

    today = datetime.today()

    patients_list, _, _ = await getting_objs(info, user, UserTable,
                                             filtering_attrs=UserIn(
                                                 first_name=patient.first_name,
                                                 last_name=patient.last_name,
                                                 patronymic=patient.patronymic,
                                                 birth_date=datetime.strptime(patient.birth_date, "%Y-%m-%d").date(),
                                                 phone_number=patient.phone_number,
                                                 email=patient.email
                                             ),
                                             ordering_attrs=UserIn(
                                                 last_name=''
                                             ),
                                             skip = 1,
                                             limit = 1000,
                                             desc_sorting = None,
                                             is_active_filtering = True)

    # Проверяем наличие пациента в МИС
    try:
        if patient.relative_type_id is not None:
            patient.relative_type_id = str(patient.relative_type_id)
        data_for_oracle = [value for key, value in patient.__dict__.items()]
        print(data_for_oracle)
        check_result = await call_oracle_proc(data_for_oracle, ORACLE_PROC_CHECK_PATIENT)
        print(check_result)
        if check_result is not None:
            check_result_data = xmltodict.parse(check_result[2].lower())
            print(check_result_data)
            if check_result_data['data'] != None:
                mis_patient = check_result_data['data']['user']
                try:
                    if mis_patient['last_name']:
                        mis_patient['last_name'] = mis_patient['last_name'].capitalize()
                    if mis_patient['first_name']:
                        mis_patient['first_name'] = mis_patient['first_name'].capitalize()
                    if mis_patient['patronymic']:
                        mis_patient['patronymic'] = mis_patient['patronymic'].capitalize()
                except Exception as e:
                    print(e)

                policy_client_id = check_result_data['data']['policies_id']
                shifr_client_id = check_result_data['data']['shifrs_id']
            else:
                mis_patient = None
                policy_client_id = None
                shifr_client_id = None
    except Exception as e:
        print(f'ERROR - {e}')
        logger.error(f'on_event_check_patient_in_oracle() has got error {e}')
        return UserRelativeShortResult(
            status_code=500,
            details='MIS is not available',
            details_ru='МИС недоступна'
        )
#####################################

    if len(patients_list) > 1 or check_result[0] == 202:
        return UserRelativeShortResult(
            status_code=422,
            details='There are more then one the same patients in the database PG. Contact with system administrator.',
            details_ru='Найдено несколько пациентов с указанными параметрами. Обратитесь, пожалуйста, к системному администратору.'
        )
    elif not patients_list and check_result[0] == 404:
        new_patient = UserTable()
        new_patient =  await input_obj_constructor(UserTable, new_patient, patient.__dict__)
        if new_patient.password:
            new_patient.set_password(new_patient.password)
        # Записываем пациента в базу
        async with get_session() as s:
            try:
                s.add(new_patient)
                await s.flush()

                relative_degree, _, _ = await getting_objs(info, user, RelationshipDegreesTable,
                                                  filtering_attrs=RelationshipDegreesInput(
                                                      id=int(patient.relative_type_id)#relationship_degree_id
                                                  ),
                                                  skip = 1,
                                                  limit = 1)

                if not relative_degree:
                    return UserRelativeShortResult(
                    status_code=422,
                    details="The relationship_degree_id parameter is wrong."
                )

                new_relative = UserRelativeTable(
                    relationship_degree_id=relative_degree[0].id,
                    relative_id=new_patient.id,
                    user_id=user.id
                )
                s.add(new_relative)
                await s.flush()

                patient.id = new_patient.id
                patient.client_id = new_patient.client_id
                patient.relative_type_id = str(relative_degree[0].client_id)
                patient.relative_id = user.client_id

                # Вызываем процедуру создания (обновления) пациента в МИСС
                data_for_oracle = [value for key, value in patient.__dict__.items()]
                oracle_create_result = await call_oracle_proc(
                    data_for_oracle,
                    ORACLE_PROC_CREATE_USER_PATIENT
                )

                if oracle_create_result is not None:
                    oracle_create_data = xmltodict.parse(oracle_create_result[2].lower())
                    try:
                        if oracle_create_result[0] == 200 or oracle_create_data['data'] is None:
                            new_patient.client_id = int(oracle_create_data['data']['user_id'])
                            new_relative.client_id = int(oracle_create_data['data']['users_relatives']['client_id'])
                            s.add(new_patient)
                            s.add(new_relative)
                            # Создаем новому пациенту первичный полис
                            new_policy = PolicyTable(
                                client_id=int(oracle_create_data['data']['policies_id']),
                                user_id=new_patient.id,
                                shifr_id=POLICY_SHIFR_ID,
                                start_date=today,
                                end_date=datetime.strptime(POLICY_END_DATE, '%d.%m.%Y'),
                                status=POLICY_STATUS
                            )
                            s.add(new_policy)
                            # Устанавливаем пациента по умолчанию
                            user_default_obj = (await s.execute(async_select(
                                UserDefaultObjectTable
                            ).filter(
                                UserDefaultObjectTable.user_id == user.id
                            ))).scalars().one_or_none()
                            if not user_default_obj:
                                user_default_obj = UserDefaultObjectTable(
                                    user_id=user.id,
                                    default_patient_id=new_patient.id
                                )
                            else:
                                user_default_obj.user_id = user.id
                                user_default_obj.default_patient_id = new_patient.id
                            s.add(user_default_obj)
                            await s.commit()
                            return UserRelativeShortResult(
                                data=[new_relative,],
                                status_code=200,
                                details="Ok"
                            )
                        else:
                            raise Exception("MIS didn't return status_code==200")
                    except Exception as e:
                        raise Exception(f"MIS returned wrong data: {str(e)} {oracle_create_data['data']}")
                else:
                    raise Exception("MIS didn't return anything")
            except Exception as e:
                await s.rollback()
                print(e)
                return UserRelativeShortResult(
                    status_code=422,
                    details="Can't save new patient. Repeat attempt."
                )
    else:
        if patients_list:
            if patients_list[0].id == user.id:
                return UserRelativeShortResult(
                    status_code=422,
                    details="You can't be a relative for yourself"
                )

            relatives_list, _, _ = await getting_objs(info, user, UserRelativeTable,
                                                    filtering_attrs=UserRelativeIn(
                                                        user_id=user.id
                                                    ),
                                                    skip = 1,
                                                    limit = 1000)

            relatives_list_ides = [item.relative_id for item in relatives_list]

            if relatives_list:
                if patients_list[0].id in relatives_list_ides:
                    return UserRelativeShortResult(
                        status_code=422,
                        details=f"Patient {patients_list[0].id} is already your relative."
                    )

        if patients_list:
            pg_patient = patients_list[0].as_dict()
        else:
            pg_patient = None

        ##################################################

        producer = KafkaProducer(
            bootstrap_servers=['kafka:9092'],
            acks=1,
            linger_ms=40,
            value_serializer=lambda m: json.dumps(m).encode('ascii')
        )

        ver_code = await flash_code_generator()

        # Определяем канал, по которому будем запрашивать подтверждение родственника
        confirmation_email = None
        confirmation_phone_number = None

        if mis_patient != None:
            if mis_patient['email'] != None:
                confirmation_email = mis_patient['email']
            elif mis_patient['phone_number'] != None:
                confirmation_phone_number = mis_patient['phone_number']
            else:
                if pg_patient != None:
                    if pg_patient['email'] != None:
                        confirmation_email = pg_patient['email']
                    elif pg_patient['phone_number'] != None:
                        confirmation_phone_number = pg_patient['phone_number']
        else:
            if pg_patient != None:
                if pg_patient['email'] != None:
                    confirmation_email = pg_patient['email']
                elif pg_patient['phone_number'] != None:
                    confirmation_phone_number = pg_patient['phone_number']

        confirmation_key = str(hasher(f'{user.client_id}{ver_code}'.encode()).hexdigest())

        print(confirmation_key)

        if confirmation_email:
            cache.set(
                confirmation_key,
                json.dumps({"mis_patient": mis_patient, "pg_patient": pg_patient,
                            "relationship_degree_id": patient.relative_type_id,#relationship_degree_id,
                            "policy_client_id": policy_client_id,
                            "shifr_client_id": shifr_client_id}).encode(),
                EXP_TIME_FOR_EMAIL_DATA
            )
            try:
                producer.send('confirm-patient-by-email-oracle-topic', {
                    'key': confirmation_key,
                    'data': {
                        'email': confirmation_email,
                        'ver_code': ver_code,
                        'client_id': mis_patient['client_id'] if mis_patient else pg_patient['client_id']
                    }
                })
                return RequestResult(
                    status_code=250,
                    details='The relative confirmation procedure by an e-mail has been started',
                    details_ru='Процедура подтверждения родственника была инициирована через электронную почту.'
                )
            except Exception as e:
                print(e)
                return RequestResult(
                    status_code=422,
                    details='The relative confirmation procedure temporary is not available.',
                    details_ru='Процедура подтверждения родственника временно не доступна.'
                )
        elif confirmation_phone_number:
            cache.set(
                confirmation_key,
                json.dumps({"mis_patient": mis_patient, "pg_patient": pg_patient,
                            "relationship_degree_id": patient.relative_type_id,#relationship_degree_id,
                            "policy_client_id": policy_client_id,
                            "shifr_client_id": shifr_client_id}).encode(),
                EXP_TIME_FOR_FLASH_CALL_DATA
            )
            try:
                producer.send('flash-call-topic', {'phone':confirmation_phone_number, 'code': ver_code})
            except Exception as e:
                print(e)
                return RequestResult(
                    status_code=422,
                    details='The relative confirmation procedure has not been started',
                    details_ru='Процедура подтверждения родственника не была инициирована'
                )

            return RequestResult(status_code=270,
                                details='Flash Call has been initiated',
                                details_ru='Инициирована процедура смс подтверждения')

        else:
            return RequestResult(
                status_code=422,
                details='The relative confirmation procedure has not been started',
                details_ru='Невозможно связаться с пациентом, которого вы пытаетесь указать, как родственника'
            )


async def email_confirmation_code_patient_update(email_key):

    proc_name = ORACLE_PROC_UDATE_USER_PATIENT

    auth_handler = Auth()

    data = json.loads(cache.get(email_key))

    if data is not None:
        input_patient = data['input_patient']
        oracle_patient = data['oracle_patient']
    else:
        return LoginResult(
            status_code=422,
            details='Operation is temporarily unavailable. Repeat it later',
            details_ru='Операция временно недоступна. Повторите попытку позже'
        )

    if input_patient is None or oracle_patient is None:
        return LoginResult(
            status_code=422,
            details='Operation is temporarily unavailable. Repeat it later',
            details_ru='Операция временно недоступна. Повторите попытку позже'
        )

    async with get_session() as s:

        pg_patient_sql = async_select(UserTable).filter(UserTable.client_id == int(oracle_patient['client_id']))

        pg_patient = (await s.execute(pg_patient_sql)).unique().scalars().one_or_none()

        if pg_patient is not None:
            pg_patient.phone_number = pg_patient.login_phone_number = input_patient['phone_number']
            s.add(pg_patient)
            await s.flush()
        else:
            oracle_patient['phone_number'] = oracle_patient['login_phone_number'] = input_patient['phone_number']
            pg_patient = UserTable()
            pg_patient = await input_obj_constructor_with_fk(UserTable, pg_patient, oracle_patient, date_time_format='%d.%m.%Y')
            pg_patient.set_capitalize_fio()
            pg_patient.set_random_password()
            s.add(pg_patient)
            await s.flush()
            new_default_patient = UserDefaultObjectTable(
                user_id=pg_patient.id,
                default_patient_id=pg_patient.id
            )
            s.add(new_default_patient)
            await s.flush()

        oracle_patient_update = PatientUpdate(phone_number=pg_patient.phone_number)

        for key in oracle_patient_update.__dict__.keys():
            try:
                value = pg_patient.__dict__[key]
                if isinstance(value, date) or isinstance(value,datetime):
                    value = value.strftime('%Y-%m-%d')
                if key == 'notification_time':
                    value = value.strftime("%H:%M")
                if key == 'gender':
                    value = int(value)
                oracle_patient_update.__dict__[key] = value
            except Exception as e:
                pass

        # Вызываем процедуру обновления пациента в МИС
        data_for_oracle = [value for key, value in oracle_patient_update.__dict__.items()]
        oracle_update_result = await call_oracle_proc(data_for_oracle, proc_name)
        if oracle_update_result[0] == 200:
            await s.commit()
            return LoginResult(
                        data = Token(token = await auth_handler.encode_token(pg_patient.login_phone_number, pg_patient.password)),
                        details='Ok',
                        status_code=200
                    )
        else:
            await s.rollback()
            return LoginResult(
                status_code=422,
                details='Operation is temporarily unavailable. Repeat it later',
                details_ru='Операция временно недоступна. Повторите попытку позже'
            )


async def changing_user(user, user_changings):

    proc_name = ORACLE_PROC_UDATE_USER_PATIENT

    changed_user = await input_obj_constructor_with_fk_id(UserTable, user, user_changings.__dict__, updating=True)

    async with get_session() as s:

        s.add(changed_user)
        await s.flush()

        # Вызываем процедуру обновления пациента в МИС
        changed_user_schema = PatientUpdate(phone_number=changed_user.phone_number)
        changed_user_schema = await table_to_schema_constructor(changed_user, changed_user_schema, updating=True)
        data_for_oracle = [value for key, value in changed_user_schema.__dict__.items()]
        oracle_update_result = await call_oracle_proc(data_for_oracle, proc_name)
        if oracle_update_result[0] == 200:
            await s.commit()

            return UserResult(
                        data = changed_user,
                        details='Ok',
                        details_ru='Ок',
                        status_code=200
                    )
        else:
            await s.rollback()
            return UserResult(
                status_code=422,
                details='Operation is temporarily unavailable. Repeat it later',
                details_ru='Операция временно недоступна. Повторите попытку позже'
            )


async def adding_existing_relative(info, user, ver_code):

    today = datetime.now()
    confirmation_key = str(hasher(f'{user.client_id}{ver_code}'.encode()).hexdigest())

    print(confirmation_key)

    try:
        patients = json.loads(cache.get(confirmation_key))

        relative_degree, _, _ = await getting_objs(info, user, RelationshipDegreesTable,
                                                   filtering_attrs=RelationshipDegreesInput(
                                                   id=int(patients['relationship_degree_id'])
                                                  ),
                                                  skip = 1,
                                                  limit = 1)

        if not relative_degree:
            return RequestResult(
            status_code=422,
            details="The relationship_degree_id parameter is wrong."
        )
    except Exception as e:
        print(e)
        return RequestResult(
            status_code=422,
            details='The user code is wrong or the code lifetime has been expired. Repeat a process.',
            details_ru='От пользователя получен неверный код или время жизни кода истекло. Повторите процесс, пожалуйста'
        )

    print(patients)

    if patients['mis_patient'] != None and patients['pg_patient'] == None:

        new_patient = UserTable(phone_number='')
        new_patient =  await input_obj_constructor(UserTable, new_patient, patients['mis_patient'])
        if new_patient.password:
            new_patient.set_password(new_patient.password)
        # Записываем пациента в базу
        async with get_session() as s:
            if new_patient.info_way_id:
                new_patient.info_way_id = (await s.execute(async_select(
                    InformationWayTable.id
                ).filter(
                    InformationWayTable.client_id == int(new_patient.info_way_id)
                ))).scalars().one_or_none()
                if new_patient.info_way_id is None:
                    return RequestResult(
                        status_code=422,
                        details="The new_patient.info_way_id is wrong from MIS",
                        details_ru="Из МИС поступило некорректное значение поля new_patient.info_way_id."
                    )
            try:
                s.add(new_patient)
                await s.flush()

                new_relative = UserRelativeTable(
                    relationship_degree_id=relative_degree[0].id,
                    relative_id=new_patient.id,
                    user_id=user.id
                )
                s.add(new_relative)
                await s.flush()

                # Вызываем процедуру добавления родственника пациента в МИСС
                data_for_oracle = [
                    user.client_id,
                    new_patient.client_id,
                    str(relative_degree[0].client_id)
                ]
                oracle_create_result = await call_oracle_proc(
                    data_for_oracle,
                    ORACLE_PROC_ADD_PATIENT_RELATIVE
                )

                if oracle_create_result is not None:
                    try:
                        if oracle_create_result[0] == 200:
                            # Создаем новому пациенту первичный полис
                            new_policy = PolicyTable(
                                client_id=int(patients['policy_client_id']),
                                user_id=new_patient.id,
                                shifr_id=(await s.execute(async_select(
                                    ShifrTable.id
                                ).filter(
                                    ShifrTable.client_id == int(patients['shifr_client_id'])
                                ))).scalars().one_or_none(),
                                start_date=today,
                                end_date=datetime.strptime(POLICY_END_DATE, '%d.%m.%Y'),
                                status=POLICY_STATUS
                            )
                            s.add(new_policy)
                            # Устанавливаем пациента по умолчанию
                            user_default_obj = (await s.execute(async_select(
                                UserDefaultObjectTable
                            ).filter(
                                UserDefaultObjectTable.user_id == user.id
                            ))).scalars().one_or_none()
                            if not user_default_obj:
                                user_default_obj = UserDefaultObjectTable(
                                    user_id=user.id,
                                    default_patient_id=new_patient.id
                                )
                            else:
                                user_default_obj.user_id = user.id
                                user_default_obj.default_patient_id = new_patient.id
                            s.add(user_default_obj)
                            await s.commit()
                            return RequestResult(
                                data=str(new_relative.id),
                                status_code=200,
                                details="Ok"
                            )
                        else:
                            raise Exception("MIS didn't return status_code==200")
                    except Exception as e:
                        raise Exception(f"Something goes wrong: {str(e)}")
                else:
                    raise Exception("MIS didn't return anything")
            except Exception as e:
                await s.rollback()
                print(e)
                return RequestResult(
                    status_code=422,
                    details="Can't save new patient. Repeat attempt."
                )
    elif patients['mis_patient'] != None and patients['pg_patient'] != None:

        async with get_session() as s:
            try:
                new_relative = UserRelativeTable(
                    relationship_degree_id=relative_degree[0].id,
                    relative_id=patients['pg_patient']['id'],
                    user_id=user.id
                )
                s.add(new_relative)
                await s.flush()

                # Вызываем процедуру добавления родственника пациента в МИСС
                data_for_oracle = [
                    user.client_id,
                    patients['pg_patient']['client_id'],
                    str(relative_degree[0].client_id)
                ]
                oracle_create_result = await call_oracle_proc(
                    data_for_oracle,
                    ORACLE_PROC_ADD_PATIENT_RELATIVE
                )
                if oracle_create_result[0] != 200:
                    raise Exception("MIS didn't return status_code==200")
                else:
                    await s.commit()
            except Exception as e:
                await s.rollback()
                print(e)
                return RequestResult(
                    status_code=422,
                    details="Can't save new family connection. Repeat attempt.",
                    details_ru="Не могу записать родственную связь в базу. Повторите попытку позже."
                )
    elif patients['mis_patient'] == None and patients['pg_patient'] != None:
        # Записываем родственную связь в базу
        async with get_session() as s:
            try:

                pg_patient = (await s.execute(async_select(
                    UserTable
                ).filter(
                    UserTable.id == patients['pg_patient']['id']
                ))).scalars().one_or_none()

                new_relative = UserRelativeTable(
                    relationship_degree_id=relative_degree[0].id,
                    relative_id=pg_patient.id,
                    user_id=user.id
                )
                s.add(new_relative)
                await s.flush()

                patient = PatientRegistration(
                    phone_number='',
                    default_medical_center_id = 0
                )

                patient = await table_to_schema_constructor(pg_patient, patient)

                patient.relative_type_id = str(relative_degree[0].client_id)
                patient.relative_id = user.client_id

                # Вызываем процедуру создания (обновления) пациента в МИСС
                data_for_oracle = [value for key, value in patient.__dict__.items()]
                oracle_create_result = await call_oracle_proc(data_for_oracle, ORACLE_PROC_CREATE_USER_PATIENT)

                if oracle_create_result is not None:
                    oracle_create_data = xmltodict.parse(oracle_create_result[2].lower())
                    try:
                        if oracle_create_result[0] == 200 or oracle_create_data['data'] is None:
                            pg_patient.client_id = int(oracle_create_data['data']['user_id'])
                            new_relative.client_id = int(oracle_create_data['data']['users_relatives']['client_id'])
                            s.add(pg_patient)
                            s.add(new_relative)
                            # Устанавливаем пациента по умолчанию
                            user_default_obj = (await s.execute(async_select(
                                UserDefaultObjectTable
                            ).filter(
                                UserDefaultObjectTable.user_id == user.id
                            ))).scalars().one_or_none()
                            if not user_default_obj:
                                user_default_obj = UserDefaultObjectTable(
                                    user_id=user.id,
                                    default_patient_id=pg_patient.id
                                )
                            else:
                                user_default_obj.user_id = user.id
                                user_default_obj.default_patient_id = pg_patient.id
                            s.add(user_default_obj)
                            await s.commit()
                            return RequestResult(
                                data=str(new_relative.id),
                                status_code=200,
                                details="Ok"
                            )
                        else:
                            raise Exception("MIS didn't return status_code==200")
                    except Exception as e:
                        raise Exception(f"MIS returned wrong data: {str(e)} {oracle_create_data['data']}")
                else:
                    raise Exception("MIS didn't return anything")

            except Exception as e:
                await s.rollback()
                print(e)
                return RequestResult(
                    status_code=422,
                    details="Can't save new patient. Repeat attempt."
                )

    return RequestResult(
        status_code=200,
        details='Ok',
        details_ru='Ок'
    )

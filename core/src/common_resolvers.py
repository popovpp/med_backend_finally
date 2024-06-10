import math
import time
import json
from datetime import datetime, timedelta
from sqlalchemy.future import select as async_select
from sqlalchemy import select, func, and_, delete

import core.sa_tables.main_process
from core.config.db import get_session
from core.config.cache_connector import CacheConnector
from core.config.settings import EXP_TIME_FOR_SUBSCRIBE_NET_DATA
from core.config.scalars import (IntFilteringInterval, DateTimeFilteringInterval, RequestResult,
                                 SubscribeNetNode, UserServiceCartSubscribe,
                                 UserServiceCartSubscribeResult, UserDefaultObjectIn)
from core.sa_tables.main_process import (UserDefaultObjectTable, UserPaymentTable,
                                         UserPurchaseTable, UserServiceCartTable,
                                         AccessTicketTable, PayKeeperPaymentDataTable)
from core.sa_tables.accounts import UserRelativeTable
from oracle_connector.scripts.oracle_connector import call_oracle_proc
from oracle_connector.config.settings import ORACLE_PROC_DELETE_PAYMENT


cache = CacheConnector()


async def get_has_obj(has_obj_list, ending_filter):

        has_obj = ending_filter

        for item in has_obj_list:
            has_obj = getattr(
                        item[0],
                        item[1]
                    ).has(has_obj)
        return has_obj


async def deep_filtering(model, filterring_attrs, select_filter, has_obj_list):

    for key in filterring_attrs.__dict__.keys():
        value = filterring_attrs.__dict__[key]
        if value is not None:
            try:
                if isinstance(value, datetime):
                    raise Exception
                nested_model = getattr(core.sa_tables.main_process, type(value).__name__.replace('In', 'Table'))
                has_obj_list.insert(0, (model, key))
                select_filter.extend(
                    await deep_filtering(
                        nested_model,
                        value,
                        select_filter,
                        has_obj_list
                    )
                )
            except Exception as error:
                print(error)
                if (value is not None) and (value !=''):
                    # Возможность по айдишникам задать значение None
                    if (value == [0] or value == 0) and key[-2:] == 'id':
                        value = None
                    if isinstance(value, str):
                        if has_obj_list:
                            select_filter.append(
                                await get_has_obj(has_obj_list, getattr(model, key, None).ilike(f'%{value}%'))
                            )
                        else:
                            select_filter.append(
                                getattr(model, key, None).ilike(f'%{value}%')
                            )
                    elif isinstance(value, IntFilteringInterval) or isinstance(value, DateTimeFilteringInterval):
                        if value.equals:
                            if has_obj_list:
                                select_filter.append(
                                    await get_has_obj(has_obj_list, getattr(model, key, None) == value.equals)
                                )
                            else:
                                select_filter.append(
                                    getattr(model, key, None) == value.equals
                                )
                        elif value.less and value.more:
                            if has_obj_list:
                                select_filter.append(
                                    await get_has_obj(has_obj_list, and_(
                                        getattr(model, key, None) < value.less,
                                        getattr(model, key, None) > value.more
                                    )
                                ))
                            else:
                                select_filter.append(
                                    and_(
                                        getattr(model, key, None) < value.less,
                                        getattr(model, key, None) > value.more
                                    )
                                )
                        elif value.less and not value.more:
                            if has_obj_list:
                                select_filter.append(
                                    await get_has_obj(has_obj_list, getattr(model, key, None) < value.less)
                                )
                            else:
                                select_filter.append(
                                    getattr(model, key, None) < value.less
                                )
                        elif value.more and not value.less:
                            if has_obj_list:
                                select_filter.append(
                                    await get_has_obj(has_obj_list, getattr(model, key, None) > value.more)
                                )
                            else:
                                select_filter.append(
                                    getattr(model, key, None) > value.more
                                )
                        elif value.less_or_equals and not value.more_or_equals:
                            if has_obj_list:
                                select_filter.append(
                                    await get_has_obj(has_obj_list, getattr(model, key, None) <= value.less_or_equals + timedelta(days=1))
                                )
                            else:
                                select_filter.append(
                                    getattr(model, key, None) <= value.less_or_equals
                                )
                        elif value.more_or_equals and not value.less_or_equals:
                            if has_obj_list:
                                select_filter.append(
                                    await get_has_obj(has_obj_list, getattr(model, key, None) >= value.more_or_equals)
                                )
                            else:
                                select_filter.append(
                                    getattr(model, key, None) >= value.more_or_equals
                                )
                        elif value.more_or_equals and value.less_or_equals:
                            if has_obj_list:
                                select_filter.append(
                                    await get_has_obj(has_obj_list, and_(
                                        getattr(model, key, None) <= value.less_or_equals + timedelta(days=1),
                                        getattr(model, key, None) >= value.more_or_equals
                                    )
                                ))
                            else:
                                select_filter.append(
                                    and_(
                                        getattr(model, key, None) <= value.less_or_equals + timedelta(days=1),
                                        getattr(model, key, None) >= value.more_or_equals
                                    )
                                )
                    elif isinstance(value, list):
                        if has_obj_list:
                            select_filter.append(
                                await get_has_obj(has_obj_list, getattr(model, key, None).in_(value))
                            )
                        else:
                            select_filter.append(
                                getattr(model, key, None).in_(value)
                            )
                    elif isinstance(value, datetime):
                        if has_obj_list:
                            select_filter.append(
                                await get_has_obj(has_obj_list, getattr(model, key, None) >= value)
                            )
                            select_filter.append(
                                await get_has_obj(has_obj_list, getattr(model, key, None) <= value + timedelta(days=1))
                            )
                        else:
                            select_filter.append(
                                getattr(model, key, None) >= value
                            )
                            select_filter.append(
                                getattr(model, key, None) <= value + timedelta(days=1)
                            )
                    else:
                        if has_obj_list:
                            select_filter.append(
                                await get_has_obj(has_obj_list, getattr(model, key, None) == value)
                            )
                        else:
                            select_filter.append(
                                getattr(model, key, None) == value
                            )

    return select_filter


async def getting_objs(info, user, model,
                       filtering_attrs=None,
                       ordering_attrs=None,
                       skip = 1,
                       limit = 1000,
                       desc_sorting = None,
                       is_active_filtering = True):

    select_filter = []
    if filtering_attrs:

        select_filter = await deep_filtering(model, filtering_attrs, select_filter, [])

    async with get_session() as s:

        result_sql = async_select(model).filter(
            *select_filter
        )

        # Сортировка
        if ordering_attrs:
            for key in ordering_attrs.__dict__.keys():
                if ordering_attrs.__dict__[key] is not None:
                    if not desc_sorting:
                        result_sql = result_sql.order_by(getattr(model, key, None))
                    else:
                        result_sql = result_sql.order_by(getattr(model, key, None).desc())

        # Фильтруем только активные
        if 'is_active' in model.__dict__.keys() and is_active_filtering:
            result_sql = result_sql.filter(getattr(model, 'is_active', None) == True)
            select_filter.append(
                getattr(model, 'is_active', None) == True
            )

        if skip < 1:
            skip = 1
        if limit <= 0:
            limit = 1

        # Количество записей
        result = await s.execute(
            select(func.count())
            .select_from(model).filter(*select_filter)
        )

        records_count = result.scalars().one_or_none()

        result_sql = result_sql.offset((skip-1)*limit).limit(limit)

        result = (await s.execute(result_sql)).unique().scalars().all()

        pages_count = math.ceil(records_count/limit)

    return result, records_count, pages_count


async def adding_updating_obj(input_obj, model, id_obj):

    table_obj = None

    async with get_session() as s:
        if id_obj is not None:
            table_obj = (await s.execute(async_select(model).filter(
                model.id == id_obj
            ))).unique().scalars().one_or_none()

        if not table_obj:
            table_obj = model()

        input_obj_attrs_list = input_obj.__dict__.keys()

        for attr in input_obj_attrs_list:
            value = getattr(input_obj, attr, None)
            if value is not None:
                if value == 0 and 'id' in attr:
                    value = None
                setattr(table_obj, attr, value)

        try:
            s.add(table_obj)
            await s.commit()
            result = RequestResult(
                data=table_obj,
                details='Ok',
                status_code=200
            )
        except Exception as e:
            print(e)
            result = RequestResult(
                status_code=422,
                details_ru=f'Добавление записи временно недоступно, повторите попытку позже.'
            )

    return result


async def deleting_obj(obj_id, model):

    async with get_session() as s:
        obj = (await s.execute(async_select(model).filter(
                    model.id == obj_id
                ))).unique().scalars().one_or_none()
        if obj:
            try:
                await s.delete(obj)
                await s.commit()
                result = RequestResult(
                    details='Ok',
                    status_code=200
                )
            except Exception as e:
                print(e)
                result = RequestResult(
                    status_code=422,
                    details=f'Удаление записи из таблицы временно недоступно, повторите попытку позже.'
                )
        else:
            result = RequestResult(
                status_code=422,
                details=f'Запись с id = {obj_id} не существует.'
            )

    return result


async def getting_patient_suscribes_net(patient):

    async with get_session() as s:

        # Получаем абонементы пользователя
        patient_subscribes = (await s.execute(async_select(
            core.sa_tables.main_process.UserSubscribeTable.id,
            core.sa_tables.main_process.SubscribeServicePackTable.id,
            core.sa_tables.main_process.SubscribeServicePackTable.pack_type_id,
            core.sa_tables.main_process.SubscribeServicePackTable.min_quantity,
            core.sa_tables.main_process.SubscribeServicePackTable.max_quantity,
            core.sa_tables.main_process.SubscribeServicePackTable.quantity,
            core.sa_tables.main_process.SubscribeSpackRecordTable.service_id,
            core.sa_tables.main_process.SubscribeSpackRecordTable.quantity
        ).outerjoin(
            core.sa_tables.main_process.SubscribeServicePackTable,
            core.sa_tables.main_process.SubscribeServicePackTable.user_subscribe_id == core.sa_tables.main_process.UserSubscribeTable.id
        ).outerjoin(
            core.sa_tables.main_process.SubscribeSpackRecordTable,
            core.sa_tables.main_process.SubscribeSpackRecordTable.subscribe_services_pack_id == core.sa_tables.main_process.SubscribeServicePackTable.id
        ).filter(
            core.sa_tables.main_process.UserSubscribeTable.policy_id.in_(async_select(
                core.sa_tables.main_process.PolicyTable.id
            ).filter(
                core.sa_tables.main_process.PolicyTable.user_id == patient.id
            ))
        ))).all()

        patient_subscribes_dict = {}

        for item in patient_subscribes:
            node = SubscribeNetNode(
                user_subscribe_id=item[0],
                pack_id=item[1],
                pack_type_id=item[2],
                pack_min_quantity=item[3],
                pack_max_quantity=item[4],
                pack_quantity=item[5],
                pack_record_service_id=item[6],
                pack_record_quantity=item[7]
            )
            try:
                patient_subscribes_dict[node.pack_record_service_id].append(node.__dict__)
            except Exception:
                patient_subscribes_dict[node.pack_record_service_id] = [node.__dict__,]

    return patient_subscribes_dict


async def getting_patient_prescribe_services(patient, patient_suscribes_net_ids):

    async with get_session() as s:

        patient_prescribe_services = (await s.execute(async_select(
            core.sa_tables.main_process.UserServiceCartTable.service_id,
            func.count(core.sa_tables.main_process.UserServiceCartTable.service_id)
        ).filter(
            core.sa_tables.main_process.UserServiceCartTable.user_id == patient.id,
            core.sa_tables.main_process.UserServiceCartTable.policy.has(core.sa_tables.main_process.PolicyTable.user_id == patient.id),
            core.sa_tables.main_process.UserServiceCartTable.service_id.in_(patient_suscribes_net_ids),
            core.sa_tables.main_process.UserServiceCartTable.service_status != 2
        ).group_by(
            core.sa_tables.main_process.UserServiceCartTable.service_id
        )
        )).all()

        patient_subscribes_dict = {}

        for item in patient_prescribe_services:
            try:
                patient_subscribes_dict[item[0]] += item[1]
            except Exception:
                patient_subscribes_dict[item[0]] = item[1]

    return patient_subscribes_dict


async def service_subscribe_availability(user, service_to_pay) -> UserServiceCartSubscribeResult:

        start = time.time()

        # Формируем сетку абонементов и сетку полученных услуг
        key_net_dict = f'service_subscribe_availability{user.id}patient_suscribes_net_dict'
        key_services_dict = f'service_subscribe_availability{user.id}patient_prescribed_services_dict'
        try:
            patient_suscribes_net_dict = json.loads(cache.get(key_net_dict))
            patient_prescribed_services_dict = json.loads(cache.get(key_services_dict))
        except Exception as e:
            print(f'The cache is empty - {e}')
        # if not patient_suscribes_net_dict or not patient_prescribed_services_dict:
            patient_suscribes_net_dict = await getting_patient_suscribes_net(user)
            patient_suscribes_net_services_ids = [
                value[0]['pack_record_service_id'] for key, value in patient_suscribes_net_dict.items()
            ]
            patient_prescribed_services_dict = await getting_patient_prescribe_services(
                user,
                patient_suscribes_net_services_ids
            )

            cache.set(
                key_net_dict,
                json.dumps(patient_suscribes_net_dict).encode(),
                EXP_TIME_FOR_SUBSCRIBE_NET_DATA
            )
            cache.set(
                key_services_dict,
                json.dumps(patient_prescribed_services_dict).encode(),
                EXP_TIME_FOR_SUBSCRIBE_NET_DATA
            )

        service_with_subscribe = UserServiceCartSubscribe(
            service_id=service_to_pay.service_id,
            medical_center_id=service_to_pay.medical_center_id,
            access_ticket_id=service_to_pay.access_ticket_id,
            doctor_mcenter_id=service_to_pay.doctor_mcenter_id,
            quantity=service_to_pay.quantity,
            price_id=service_to_pay.price_id
        )
        try:
            subscribes_list = patient_suscribes_net_dict[str(service_to_pay.service_id)]
        except Exception as e:
            return UserServiceCartSubscribeResult(
            status_code=422,
            details=f'Exception - {e}',
            details_ru=f'Исключение - {e}'
        )
        for subscribe in subscribes_list:
            if subscribe['pack_record_quantity'] is None:
                subscribe['pack_record_quantity'] = 100000000
            if (subscribe['pack_record_quantity'] == 0 and
                subscribe['pack_min_quantity'] == 0):
                service_with_subscribe.subscribe_id = subscribe['user_subscribe_id']

                end1 = time.time()
                print(f'Полное время на выполнение процедуры service_subscribe_availability {(end1-start)*1000} мс')

                return UserServiceCartSubscribeResult(
                    data=service_with_subscribe,
                    status_code=200,
                    details='Ok',
                    details_ru='Ок'
                )
            elif subscribe['pack_min_quantity'] > 0:
                try:
                    got_sum = patient_prescribed_services_dict[str(service_to_pay.service_id)]
                except Exception as e:
                    print(e)
                    got_sum = 0
                if ((got_sum + service_to_pay.quantity) <
                    subscribe['pack_min_quantity']):
                    service_with_subscribe.subscribe_id = subscribe['user_subscribe_id']

                    end1 = time.time()
                    print(f'Полное время на выполнение процедуры service_subscribe_availability {(end1-start)*1000} мс')

                    return UserServiceCartSubscribeResult(
                        data=service_with_subscribe,
                        status_code=200,
                        details='Ok',
                        details_ru='Ок'
                    )
                else:
                    service_with_subscribe.error_message += f""" The limit of self recording for this service {service_to_pay.service_id} is ended /
                    in the subscribe {subscribe['user_subscribe_id']}."""
                    service_with_subscribe.error_message_ru += f""" Лимит самостоятельной записи на услугу {service_to_pay.service_id} по /
                    абонементу {subscribe['user_subscribe_id']} исчерпан."""
                    continue
            elif (subscribe['pack_record_quantity'] > 0 and
                subscribe['pack_min_quantity'] == 0):
                try:
                    got_sum = patient_prescribed_services_dict[str(service_to_pay.service_id)]
                except Exception as e:
                    print(e)
                    got_sum = 0
                if ((got_sum + service_to_pay.quantity) <
                    subscribe['pack_record_quantity']):
                    service_with_subscribe.subscribe_id = subscribe['user_subscribe_id']

                    end1 = time.time()
                    print(f'Полное время на выполнение процедуры service_subscribe_availability {(end1-start)*1000} мс')

                    return UserServiceCartSubscribeResult(
                        data=service_with_subscribe,
                        status_code=200,
                        details='Ok',
                        details_ru='Ок'
                    )
                else:
                    service_with_subscribe.error_message += f""" The limit of recording for this service {service_to_pay.service_id} is ended /
                    in the subscribe {subscribe['user_subscribe_id']}."""
                    service_with_subscribe.error_message_ru += f""" Лимит записи на услугу {service_to_pay.service_id} по /
                    абонементу {subscribe['user_subscribe_id']} исчерпан."""
                    continue

        end1 = time.time()
        print(f'Полное время на выполнение процедуры service_subscribe_availability {(end1-start)*1000} мс')

        return UserServiceCartSubscribeResult(
            status_code=422,
            details=service_with_subscribe.error_message,
            details_ru=service_with_subscribe.error_message_ru
        )


async def getting_default_patient_by_user(info, user):

    # Получаем пациента по умолчанию
    filtering_attrs = UserDefaultObjectIn(
        user_id=user.id
    )
    user_default_objs, _, _ = await getting_objs(
        info, user, UserDefaultObjectTable, filtering_attrs
    )
    if user_default_objs:
        patient = user_default_objs[0].default_patient
    else:
        patient = user

    return patient


async def getting_relatives_ids(user_id):

    async with get_session() as s:

        relatives_ids = (await s.execute(async_select(
            UserRelativeTable.relative_id
        ).filter(
            UserRelativeTable.user_id == user_id
        ))).scalars().all()

    return relatives_ids


async def remove_temporary_payment(payment_id):

    async with get_session() as s:

        payment_relative_objs = (await s.execute(async_select(
            UserPaymentTable.id,
            UserPurchaseTable.id,
            UserServiceCartTable.id,
            AccessTicketTable.id,
            UserPaymentTable.client_id
        ).outerjoin(
            UserPurchaseTable,
            UserPurchaseTable.user_payment_id == UserPaymentTable.id
        ).outerjoin(
            UserServiceCartTable,
            UserServiceCartTable.user_purchase_id == UserPurchaseTable.id
        ).outerjoin(
            AccessTicketTable,
            AccessTicketTable.id == UserServiceCartTable.access_ticket_id
        ).filter(
            UserPaymentTable.id == payment_id
        ))).unique().one_or_none()

        # Проверяем подтверждение оплаты
        paykeeper_payment_obj = (await s.execute(async_select(
            PayKeeperPaymentDataTable.id
        ).filter(
            PayKeeperPaymentDataTable.user_payment_id == payment_id
        ))).scalars().one_or_none()

        if not paykeeper_payment_obj:
            # Удаляем платеж, покупки пользователя и услугу
            if payment_relative_objs:
                (await s.execute(delete(
                    UserServiceCartTable
                ).filter(
                    UserServiceCartTable.id == payment_relative_objs[2]
                )))

                (await s.execute(delete(
                    UserPaymentTable
                ).filter(
                    UserPaymentTable.id == payment_relative_objs[0]
                )))

                (await s.execute(delete(
                    UserPurchaseTable
                ).filter(
                    UserPurchaseTable.id == payment_relative_objs[1]
                )))

                # Изменяем статус номерка
                if payment_relative_objs[3]:
                    access_ticket = (await s.execute(async_select(
                        AccessTicketTable
                    ).filter(
                        AccessTicketTable.id == payment_relative_objs[3]
                    ))).scalars().one_or_none()
                    if access_ticket:
                        access_ticket.bl_status = 3
                        s.add(access_ticket)
                        await s.flush()

                await s.commit()
                await s.close()

                # Вызываем процедуру Оракла для удаления платежа
                data_for_oracle = [str(payment_relative_objs[4]), '1']
                oracle_set_result = await call_oracle_proc(data_for_oracle, ORACLE_PROC_DELETE_PAYMENT)

                print('Temporary payment has been removed from MIS:', oracle_set_result)
            else:
                print(f"The payment {payment_id} doesn't exist")


async def getting_user_relatives_ids(user_id):

    async with get_session() as s:

        user_relatives_ids = (await s.execute(async_select(
            UserRelativeTable.id
        ).filter(
            UserRelativeTable.user_id == user_id
        ))).scalars().all()

    return user_relatives_ids

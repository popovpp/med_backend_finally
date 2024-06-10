# import time
import json
# import datetime
from datetime import datetime, timedelta
from sqlalchemy.future import select as async_select
from sqlalchemy import and_

# import core.config.mapped_scalars
from core.sa_tables.main_process import (ServiceTable, AccessTicketTable, MedicalCenterTable, DoctorMedicalCenterTable,
                                         PriceTable, UserServiceCartTable, PolicyTable, ShifrDiscountTable,
                                         ShifrDiscountPeriodTable)
from core.config.scalars import RequestResult
from core.config.db import get_session
from core.config.cache_connector import CacheConnector
from core.config.settings import EXP_TIME_FOR_GUEST_CART_RECORD
# from core.src.common_resolvers import adding_updating_obj, getting_objs
# from core.src.utils import get_model_class
from .scalars import (UserServiceCartOutputCache, UserServiceCartOutputCacheResult)


cache = CacheConnector()


async def filling_data_user_service(user_id, data_user_service):

    today = datetime.today()

    attrs_list = [x for x in UserServiceCartOutputCache.__dict__.keys() if '_id' in x ]

    async with get_session() as s:

        new_service_cart_obj = UserServiceCartTable()
        for attr in attrs_list:
            value = data_user_service[attr]
            setattr(new_service_cart_obj, attr, value)

        new_service_cart_obj.user_id = user_id
        new_service_cart_obj.quantity = data_user_service['quantity']

        policy_obj = (await s.execute(async_select(PolicyTable).filter(
            PolicyTable.user_id == user_id
        ))).unique().scalars().one_or_none()
        if policy_obj:
            new_service_cart_obj.policy_id = policy_obj.id
            new_service_cart_obj.shifr_id = policy_obj.shifr_id

            shifr_discount_obj = (await s.execute(async_select(ShifrDiscountTable).filter(
                ShifrDiscountTable.id == policy_obj.shifr_id,
                ShifrDiscountTable.service_id == data_user_service['service_id'],
                and_(
                    ShifrDiscountTable.shift_discount_period.has(ShifrDiscountPeriodTable.start_date <= today),
                    ShifrDiscountTable.shift_discount_period.has(ShifrDiscountPeriodTable.end_date >= today)
                )
            ))).unique().scalars().one_or_none()
            if shifr_discount_obj:
                new_service_cart_obj.discount_coefficient = shifr_discount_obj.discount_coefficient_a
        
        access_ticket_obj = (await s.execute(async_select(AccessTicketTable).filter(
            AccessTicketTable.id == data_user_service['access_ticket_id']
        ))).unique().scalars().one_or_none()
        if access_ticket_obj:
            new_service_cart_obj.start_date = access_ticket_obj.ticket_datetime

        service_obj = (await s.execute(async_select(ServiceTable).filter(
            ServiceTable.id == data_user_service['service_id']
        ))).unique().scalars().one_or_none()
        if service_obj:
            new_service_cart_obj.complex_service_id = service_obj.id if service_obj.is_complex_service else None
            new_service_cart_obj.complex_service_status = 1 if service_obj.is_complex_service else 0
            new_service_cart_obj.stac_satus = not service_obj.is_for_home_only
            new_service_cart_obj.cito_status = service_obj.is_urgent
            if new_service_cart_obj.start_date:
                new_service_cart_obj.end_date = new_service_cart_obj.start_date + timedelta(minutes=service_obj.execution_time)

    return new_service_cart_obj


async def add_update_item_to_cache_cart(info, user, key, data_user_service, user_service_cart_id):

    try:
        cache_data = json.loads(cache.get(key))
        user_services_cart = cache_data["data"]
        last_id = cache_data["last_id"] + 1
    except Exception as e:
        print(e)
        user_services_cart = []
        last_id = 0
        user_service_cart_id = None

    if user_service_cart_id is None:
        data_user_service_for_cache = UserServiceCartOutputCache()
    else:
        data_user_service_for_cache_dict = next((item for item in user_services_cart if item["id"] == user_service_cart_id), None)
        data_user_service_for_cache = UserServiceCartOutputCache(**data_user_service_for_cache_dict)
        last_id = user_service_cart_id
        item_to_remove = next((item for item in user_services_cart if item["id"] == user_service_cart_id), None)
        if item_to_remove is not None:
            user_services_cart.remove(item_to_remove)

    async with get_session() as s:

        for attr in data_user_service_for_cache.__dict__.keys():
            try:
                if attr == 'access_ticket_id':
                    access_ticket_obj = (await s.execute(async_select(AccessTicketTable).filter(
                        AccessTicketTable.id == data_user_service.access_ticket_id
                    ))).unique().scalars().one_or_none()
                    if access_ticket_obj:
                        data_user_service_for_cache.access_ticket_id = access_ticket_obj.id
                        data_user_service_for_cache.access_ticket_ticket_datetime = access_ticket_obj.ticket_datetime.strftime('%d.%m.%Y %H:%M')
                elif attr == 'service_id':
                    service_obj = (await s.execute(async_select(ServiceTable).filter(
                        ServiceTable.id == data_user_service.service_id
                    ))).unique().scalars().one_or_none()
                    if service_obj:
                        data_user_service_for_cache.service_id = service_obj.id
                        data_user_service_for_cache.service_name_for_lk = service_obj.name_for_lk
                elif attr == 'medical_center_id':
                    medical_center_obj = (await s.execute(async_select(MedicalCenterTable).filter(
                        MedicalCenterTable.id == data_user_service.medical_center_id
                    ))).unique().scalars().one_or_none()
                    if medical_center_obj:
                        data_user_service_for_cache.medical_center_id = medical_center_obj.id
                        data_user_service_for_cache.medical_center_name = medical_center_obj.name
                        data_user_service_for_cache.medical_center_address = medical_center_obj.address
                elif attr == 'doctor_mcenter_id':
                    doctor_mcenter_obj = (await s.execute(async_select(DoctorMedicalCenterTable).filter(
                        DoctorMedicalCenterTable.id == data_user_service.doctor_mcenter_id
                    ))).unique().scalars().one_or_none()
                    if doctor_mcenter_obj:
                        data_user_service_for_cache.doctor_mcenter_id = doctor_mcenter_obj.id
                        data_user_service_for_cache.doctor_mcenter_mposition_view_name = doctor_mcenter_obj.medical_position.view_name
                        data_user_service_for_cache.doctor_mcenter_fio = doctor_mcenter_obj.__str__()
                elif attr == 'price_id':
                    price_obj = (await s.execute(async_select(PriceTable).filter(
                        PriceTable.id == data_user_service.price_id
                    ))).unique().scalars().one_or_none()
                    if price_obj:
                        data_user_service_for_cache.price_id = price_obj.id
                        data_user_service_for_cache.price_nal = price_obj.price_nal
                else:
                    value = data_user_service.__dict__[attr]
                    setattr(data_user_service_for_cache, attr, value)
            except Exception as e:
                pass

    data_user_service_for_cache.id = last_id
    user_services_cart.append(data_user_service_for_cache.__dict__)

    cache.delete(key)

    cache.set(key, json.dumps({"last_id": last_id, "data": user_services_cart}).encode(), EXP_TIME_FOR_GUEST_CART_RECORD)

    result_list = sorted(json.loads(cache.get(key))["data"], key=lambda x: x['id'])

    result = UserServiceCartOutputCacheResult(
                data=[UserServiceCartOutputCache(**x) for x in result_list],
                status_code=200,
                details='Ok'
            )

    return result


async def delete_item_from_cache_cart(key, user_service_cart_id):

    try:
        cache_data = json.loads(cache.get(key))
        user_services_cart = cache_data["data"]
        last_id = cache_data["last_id"]
    except Exception as e:
        print(e)
        return RequestResult(
            status_code=422,
            details_ru='Операция временно не доступна. Повторите ее позже',
            details="Life time of guest's cart ended."
        )

    item_to_remove = next((item for item in user_services_cart if item["id"] == user_service_cart_id), None)

    if item_to_remove is not None:
        user_services_cart.remove(item_to_remove)
        cache.delete(key)
        cache.set(key, json.dumps({"last_id": last_id, "data": user_services_cart}).encode(), EXP_TIME_FOR_GUEST_CART_RECORD)
    else:
        return RequestResult(
            status_code=422,
            details_ru='Невозможно удалить несуществующий элемент.',
            details="An element for deleting doesn't exist. "
        )


async def move_cart_from_cache_to_database(user_id, key):

    today = datetime.today()

    try:
        cache_data = json.loads(cache.get(key))
        user_services_cart = cache_data["data"]
    except Exception as e:
        print(e)
        return RequestResult(
            status_code=422,
            details_ru='Операция временно не доступна. Повторите ее позже',
            details="Life time of guest's cart ended or sended wrong half_token parameter"
        )

    attrs_list = [x for x in UserServiceCartOutputCache.__dict__.keys() if '_id' in x ]

    async with get_session() as s:

        for service in user_services_cart:
            new_service_cart_obj = UserServiceCartTable()
            for attr in attrs_list:
                value = service[attr]
                setattr(new_service_cart_obj, attr, value)

            new_service_cart_obj.user_id = user_id

            policy_obj = (await s.execute(async_select(PolicyTable).filter(
                PolicyTable.user_id == user_id
            ))).unique().scalars().one_or_none()
            if policy_obj:
                new_service_cart_obj.policy_id = policy_obj.id
                new_service_cart_obj.shifr_id = policy_obj.shifr_id

                shifr_discount_obj = (await s.execute(async_select(ShifrDiscountTable).filter(
                    ShifrDiscountTable.id == policy_obj.shifr_id,
                    ShifrDiscountTable.service_id == service['service_id'],
                    and_(
                        ShifrDiscountTable.shift_discount_period.has(ShifrDiscountPeriodTable.start_date <= today),
                        ShifrDiscountTable.shift_discount_period.has(ShifrDiscountPeriodTable.end_date >= today)
                    )
                ))).unique().scalars().one_or_none()
                if shifr_discount_obj:
                    new_service_cart_obj.discount_coefficient = shifr_discount_obj.discount_coefficient_a

            service_obj = (await s.execute(async_select(ServiceTable).filter(
                ServiceTable.id == service['service_id']
            ))).unique().scalars().one_or_none()
            if service_obj:
                new_service_cart_obj.start_date = datetime.strptime(
                    service['access_ticket_ticket_datetime'],
                    '%d.%m.%Y %H:%M'
                )
                new_service_cart_obj.end_date = new_service_cart_obj.start_date + timedelta(minutes=service_obj.execution_time)
                new_service_cart_obj.complex_service_id = service_obj.id if service_obj.is_complex_service else None
                new_service_cart_obj.complex_service_status = 1 if service_obj.is_complex_service else 0
                new_service_cart_obj.stac_satus = not service_obj.is_for_home_only
                new_service_cart_obj.cito_status = service_obj.is_urgent

            new_service_cart_obj.quantity = service['quantity']

            s.add(new_service_cart_obj)
            await s.flush()

        cache.delete(key)
        await s.commit()

    return RequestResult(
            status_code=200,
            details_ru='Ок',
            details="Ok"
        )

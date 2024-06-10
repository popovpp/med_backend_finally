import time
import datetime
from typing import List
from sqlalchemy.future import select as async_select
from sqlalchemy import and_, or_, update

from core.sa_tables.main_process import (ServiceGroupTable, ServiceTable, DoctorMedicalCenterServiceTable,
                                         PriceTable, PricePeriodTable, MedicalCenterPriceNameTable, AccessTicketListTable,
                                         AccessTicketTable, ShifrDiscountTable, PolicyTable, ShifrDiscountPeriodTable,
                                         DoctorMedicalCenterTable, DoctorTable, MedicalPositionTable,
                                         ServiceMedicalSpecialityTable, SubscribeDoctorTable, UserSubscribeTable,
                                         PolicyPaymentPlanTable, PayKeeperPaymentDataTable, SubscribeSpackRecordTable,
                                         UserServiceCartTable, UserPurchaseTable, UserPaymentTable,
                                         TemporaryPaymentTable, UserServicePlanTable)
from core.sa_tables.accounts import UserTable, MedicalCenterTable
from core.config.mapped_scalars import ServiceGroup
from core.config.db import get_session
from core.config.cache_connector import CacheConnector
from core.config.scalars import (RequestResult, SubscribeServicePackIn, UserSubscribeIn,
                                 PolicyIn, UserServiceCartSubscribe)
from core.config.settings import (SUBSCRIBE_PAYMENT_SERVICE_CLIENT_SERVICE_CODE,
                                  ADVANCE_PAYMENT_SERVICE_CLIENT_SERVICE_CODE)
from core.src.common_resolvers import (getting_objs, service_subscribe_availability,
                                       getting_relatives_ids)
from oracle_connector.config.settings import (ORACLE_PROC_SET_TICKET_PATIENT,
                                              ORACLE_PROC_FREE_TICKET,
                                              ORACLE_PROC_CHANGE_RNUMB_FOR_PATSERV,
                                              ORACLE_PROC_DELETE_PAYMENT,
                                              ORACLE_PROC_UPDATE_USER_DEFAULT_MC)
from oracle_connector.scripts.oracle_connector import call_oracle_proc

from .scalars import (ServiceGroupResult, ServiceWithPrice, AccessTicketResult, SubscribeDoctorInput,
                      SubscribeInfoBlocksResult, SubscribeInfoBlocks, SubscribeCommonInfo, UserSubscribeInput,
                      SubscribeFinance, PolicyPaymentPlanInput, PolicyPaymentPlanWithDebt, SubscribeSpackRecordInput,
                      SubscribeServicePackWithQuantity, EventsCalendar, VisitHistoryRecord)
from .utils import getting_subscribe_paid_sum


cache = CacheConnector()


async def sorting_xmembers(service_group_node):

    service_group_node.xmembers = sorted(service_group_node.xmembers, key=lambda x: x.level_sorting_code)

    for item in service_group_node.xmembers:
        await sorting_xmembers(item)

    return service_group_node


async def getting_service_group1(name):

    label_list = []
    result_list = []

    start = time.time()

    async with get_session() as s:

        if name is not None and name != '':
            name_list = [x.strip() for x in name.split(',') if x.strip() != '']
            label_list = []
            for name in name_list:
                label_sql = async_select(ServiceGroupTable.id).filter(ServiceGroupTable.name.ilike(f'%{name}%'))
                label_list.extend((await s.execute(label_sql)).scalars().all())
            if not label_list:
                return ServiceGroupResult(
                    data=None,
                    status_code=422,
                    details=f'Имя узла {name} отсутствует в прейскуранте'
                )
        else:
            label_list.append(None)

        for label in label_list:
            select_filter = []
            if label is not None:
                select_filter.append(
                    ServiceGroupTable.path.ilike(f'%{str(label)}%')
                )

            result_sql = async_select(ServiceGroupTable).filter(*select_filter)

            result = (await s.execute(result_sql)).scalars().all()

            if not result:
                return ServiceGroupResult(
                    data=result_list,
                    status_code=200,
                    details='ok'
                )

            end1 = time.time()
            print(f'Затрачено времени на запрос в БД {(end1-start)*1000} мс')

            if name is not None and name != '':
                first_layer_sql = result_sql.filter(ServiceGroupTable.id == label)
            else:
                first_layer_sql = result_sql.filter(ServiceGroupTable.id == int(f'{result[0].path.split(".")[0]}'))

            root_node = (await s.execute(first_layer_sql)).unique().scalars().one()

            nodes_dict = {}

            for item in result:
                path=[x for x in str(item.path).split('.')]
                if not item.level_sorting_code:
                    level_sorting_code = 100
                else:
                    level_sorting_code = item.level_sorting_code
                str_node = ServiceGroup(
                    id=item.id,
                    client_id=item.client_id,
                    name=item.name,
                    view_name=item.view_name,
                    description=item.description,
                    path=path,
                    client_service_group_code=item.client_service_group_code,
                    level_sorting_code=level_sorting_code,
                    is_active=item.is_active,
                    xmembers=[]
                )
                nodes_dict[path[-1]] = str_node

            for item in nodes_dict.items():
                for i in range(0, len(item[1].path)-1):
                    try:
                        if nodes_dict[item[1].path[i+1]] not in nodes_dict[item[1].path[i]].xmembers:
                            nodes_dict[item[1].path[i]].xmembers.append(nodes_dict[item[1].path[i+1]])
                    except Exception as e:
                        pass
            result_list.append(await sorting_xmembers(nodes_dict[str(root_node.id)]))
    end = time.time()
    print(f'Затрачено времени на выпорлнение всей функции {(end-start)*1000} мс')

    return ServiceGroupResult(
        data=result_list,
        status_code=200,
        details='ok'
    )


async def getting_service_group2(services_ides):

    result_list = []
    select_filter = []
    service_group_select_filter = []

    start = time.time()

    async with get_session() as s:

        if services_ides:
            select_filter.append(
                ServiceTable.id.in_(services_ides)
            )

        services_result_sql = async_select(ServiceTable).filter(*select_filter)

        services_result = (await s.execute(services_result_sql)).scalars().all()

        services_result = sorted(services_result, key=lambda x: x.service_group_id)

        services_result_dict = {}

        key = 0
        services_group_ides = []
        for item in services_result:
            if item.service_group_id != key:
                services_result_dict[item.service_group_id] = []
                services_result_dict[item.service_group_id].append(item)
                key = item.service_group_id
            else:
                services_result_dict[key].append(item)
            path_list = [int(x) for x in item.service_group.path.split('.')]
            services_group_ides.extend(path_list)

        services_group_ides = list(set(services_group_ides))

        or_filter = []
        for group_id in services_group_ides:
            or_filter.append(ServiceGroupTable.id == group_id)
        service_group_select_filter.append(or_(
            *or_filter
        ))
        service_group_result_sql = async_select(ServiceGroupTable).filter(
            *service_group_select_filter
        )

        service_group_result = (await s.execute(service_group_result_sql.order_by(
            ServiceGroupTable.name
        ))).scalars().all()

        if not service_group_result:
            return ServiceGroupResult(
                data=result_list,
                status_code=200,
                details='ok'
            )

        end1 = time.time()
        print(f'Затрачено времени на запрос из group2 в БД {(end1-start)*1000} мс')

        first_layer_sql = service_group_result_sql.filter(
            ServiceGroupTable.id == int(f'{service_group_result[0].path.split(".")[0]}')
        )
        root_node = (await s.execute(first_layer_sql)).unique().scalars().one()
        nodes_dict = {}

        for item in service_group_result:

            path=[x for x in str(item.path).split('.')]
            if not item.level_sorting_code:
                level_sorting_code = 100
            else:
                level_sorting_code = item.level_sorting_code

            wservices = []
            try:
                wservices = sorted(services_result_dict[item.id], key=lambda x: x.name_for_lk)
            except Exception as e:
                pass
            str_node = ServiceGroup(
                id=item.id,
                client_id=item.client_id,
                name=item.name,
                view_name=item.view_name,
                description=item.description,
                path=path,
                client_service_group_code=item.client_service_group_code,
                level_sorting_code=level_sorting_code,
                is_active=item.is_active,
                xmembers=[],
                wservices=[]
            )
            str_node.wservices.extend(wservices)
            nodes_dict[path[-1]] = str_node

        for item in nodes_dict.items():
            for i in range(0, len(item[1].path)-1):
                try:
                    if nodes_dict[item[1].path[i+1]] not in nodes_dict[item[1].path[i]].xmembers:
                        nodes_dict[item[1].path[i]].xmembers.append(nodes_dict[item[1].path[i+1]])
                except Exception as e:
                    pass
        result_list.append(await sorting_xmembers(nodes_dict[str(root_node.id)]))

    end = time.time()
    print(f'Затрачено времени на выпорлнение всей функции group2 {(end-start)*1000} мс')

    return ServiceGroupResult(
        data=result_list,
        status_code=200,
        details='ok'
    )


async def getting_services_with_price(info, user, doctor_mcenter_ides, medical_centers_ides,
                                      search_list):

    start = time.time()

    today = datetime.datetime.today()

    async with get_session() as s:

        services_in_groups_sql = async_select(
            ServiceTable.id,
        ).outerjoin(
            ServiceGroupTable,
            ServiceGroupTable.id == ServiceTable.service_group_id
        ).outerjoin(
            ShifrDiscountTable,
            ShifrDiscountTable.service_group_id == ServiceGroupTable.id
        ).outerjoin(
            PolicyTable,
            PolicyTable.shifr_id == ShifrDiscountTable.shifr_id
        ).filter(
            PolicyTable.user_id == user.id,
            and_(
                ShifrDiscountTable.shift_discount_period.has(
                    ShifrDiscountPeriodTable.start_date <= today
                ),
                ShifrDiscountTable.shift_discount_period.has(
                    ShifrDiscountPeriodTable.end_date >= today
                ),
                ShifrDiscountTable.shift_discount_period.has(
                    ShifrDiscountPeriodTable.is_active == True
                ),
            )
        )

        services_without_groups_sql = async_select(
            ShifrDiscountTable.service_id
        ).outerjoin(
            PolicyTable,
            PolicyTable.shifr_id == ShifrDiscountTable.shifr_id
        ).filter(
            ShifrDiscountTable.service_id != None,
            PolicyTable.user_id == user.id,
            and_(
                ShifrDiscountTable.shift_discount_period.has(
                    ShifrDiscountPeriodTable.start_date <= today
                ),
                ShifrDiscountTable.shift_discount_period.has(
                    ShifrDiscountPeriodTable.end_date >= today
                ),
                ShifrDiscountTable.shift_discount_period.has(
                    ShifrDiscountPeriodTable.is_active == True
                ),
            )
        )

        services_under_shifr = services_in_groups_sql.union(
            services_without_groups_sql
        )

        services_with_group_discount_sql = async_select(
            PriceTable,
            MedicalCenterPriceNameTable,
            ShifrDiscountTable
        ).outerjoin(
            MedicalCenterPriceNameTable,
            MedicalCenterPriceNameTable.price_name_id == PriceTable.price_name_id
        ).outerjoin(
            DoctorMedicalCenterServiceTable,
            DoctorMedicalCenterServiceTable.service_id == PriceTable.service_id
        ).outerjoin(
            PricePeriodTable,
            PricePeriodTable.id == PriceTable.price_period_id
        ).outerjoin(
            ServiceTable,
            ServiceTable.id == PriceTable.service_id
        ).outerjoin(
            ShifrDiscountTable,
            ShifrDiscountTable.service_group_id == ServiceTable.service_group_id
        ).outerjoin(
            PolicyTable,
            PolicyTable.shifr_id == ShifrDiscountTable.shifr_id
        ).filter(
            DoctorMedicalCenterServiceTable.doctor_mcenters_id.in_(doctor_mcenter_ides),
            MedicalCenterPriceNameTable.medical_center_id.in_(medical_centers_ides),
            PriceTable.price_nal > 0,
            PolicyTable.user_id == user.id,
            and_(
                PricePeriodTable.start_date <= today,
                PricePeriodTable.end_date >= today,
                PricePeriodTable.is_active == True
            ),
            PriceTable.service_id.in_(services_in_groups_sql),
            ShifrDiscountTable.service_group_id != None,
            and_(
                ShifrDiscountTable.shift_discount_period.has(
                    ShifrDiscountPeriodTable.start_date <= today
                ),
                ShifrDiscountTable.shift_discount_period.has(
                    ShifrDiscountPeriodTable.end_date >= today
                ),
                ShifrDiscountTable.shift_discount_period.has(
                    ShifrDiscountPeriodTable.is_active == True
                ),
            ),
            DoctorMedicalCenterServiceTable.doctor_mcenters.has(
                DoctorMedicalCenterTable.medical_center_id == MedicalCenterPriceNameTable.medical_center_id
            )
        ).distinct(PriceTable.service_id).order_by(PriceTable.service_id)

        services_result_with_group_discount = list(
            (await s.execute(services_with_group_discount_sql)).unique().all()
        )

        services_with_service_discount_sql = async_select(
            PriceTable,
            MedicalCenterPriceNameTable,
            ShifrDiscountTable
        ).outerjoin(
            MedicalCenterPriceNameTable,
            MedicalCenterPriceNameTable.price_name_id == PriceTable.price_name_id
        ).outerjoin(
            DoctorMedicalCenterServiceTable,
            DoctorMedicalCenterServiceTable.service_id == PriceTable.service_id
        ).outerjoin(
            PricePeriodTable,
            PricePeriodTable.id == PriceTable.price_period_id
        ).outerjoin(
            ShifrDiscountTable,
            ShifrDiscountTable.service_id == PriceTable.service_id
        ).outerjoin(
            PolicyTable,
            PolicyTable.shifr_id == ShifrDiscountTable.shifr_id
        ).filter(
            DoctorMedicalCenterServiceTable.doctor_mcenters_id.in_(doctor_mcenter_ides),
            MedicalCenterPriceNameTable.medical_center_id.in_(medical_centers_ides),
            PriceTable.price_nal > 0,
            PolicyTable.user_id == user.id,
            and_(
                PricePeriodTable.start_date <= today,
                PricePeriodTable.end_date >= today,
                PricePeriodTable.is_active == True
            ),
            PriceTable.service_id.in_(services_without_groups_sql),
            ShifrDiscountTable.service_id != None,
            and_(
                ShifrDiscountTable.shift_discount_period.has(
                    ShifrDiscountPeriodTable.start_date <= today
                ),
                ShifrDiscountTable.shift_discount_period.has(
                    ShifrDiscountPeriodTable.end_date >= today
                ),
                ShifrDiscountTable.shift_discount_period.has(
                    ShifrDiscountPeriodTable.is_active == True
                ),
            ),
            DoctorMedicalCenterServiceTable.doctor_mcenters.has(
                DoctorMedicalCenterTable.medical_center_id == MedicalCenterPriceNameTable.medical_center_id
            )
        ).distinct(PriceTable.service_id).order_by(PriceTable.service_id)

        services_result_with_service_discount = list(
            (await s.execute(services_with_service_discount_sql)).unique().all()
        )

        services_without_discount_sql = async_select(
            PriceTable,
            MedicalCenterPriceNameTable,
            ShifrDiscountTable
        ).outerjoin(
            MedicalCenterPriceNameTable,
            MedicalCenterPriceNameTable.price_name_id == PriceTable.price_name_id
        ).outerjoin(
            DoctorMedicalCenterServiceTable,
            DoctorMedicalCenterServiceTable.service_id == PriceTable.service_id
        ).outerjoin(
            PricePeriodTable,
            PricePeriodTable.id == PriceTable.price_period_id
        ).outerjoin(
            ShifrDiscountTable,
            ShifrDiscountTable.service_id == PriceTable.service_id
        ).filter(
            DoctorMedicalCenterServiceTable.doctor_mcenters_id.in_(doctor_mcenter_ides),
            MedicalCenterPriceNameTable.medical_center_id.in_(medical_centers_ides),
            PriceTable.price_nal > 0,
            and_(
                PricePeriodTable.start_date <= today,
                PricePeriodTable.end_date >= today,
                PricePeriodTable.is_active == True
            ),
            and_(
                ShifrDiscountTable.shift_discount_period.has(
                    ShifrDiscountPeriodTable.start_date <= today
                ),
                ShifrDiscountTable.shift_discount_period.has(
                    ShifrDiscountPeriodTable.end_date >= today
                ),
                ShifrDiscountTable.shift_discount_period.has(
                    ShifrDiscountPeriodTable.is_active == True
                ),
            ),
            PriceTable.service_id.not_in(services_under_shifr),
            DoctorMedicalCenterServiceTable.doctor_mcenters.has(
                DoctorMedicalCenterTable.medical_center_id == MedicalCenterPriceNameTable.medical_center_id
            )
        ).distinct(PriceTable.service_id).order_by(PriceTable.service_id)

        services_without_discount = (await s.execute(services_without_discount_sql)).unique().all()

        services_without_discount = [(x[0], x[1], None) for x in services_without_discount]

        services_result_with_group_discount.extend(services_result_with_service_discount)
        services_result_with_group_discount.extend(services_without_discount)

        # Старый блок удалить
        # services_result_with_group_discount = sorted(
        #     services_result_with_group_discount, key=lambda x: x[0].service.name_for_lk
        # )

        # Получаем идентификаторы услуг, доступных по абонементу пользователя
        # subscribe_service_pack_records_filter_attrs = SubscribeSpackRecordInput(
        #     subscribe_services_pack=SubscribeServicePackIn(
        #         user_subscribe=UserSubscribeIn(
        #             policy=PolicyIn(
        #                 user_id=user.id
        #             )
        #         )
        #     )
        # )
        # subscribe_service_pack_records, _, _ = await getting_objs(
        #     info, user, SubscribeSpackRecordTable,
        #     subscribe_service_pack_records_filter_attrs
        # )
        # subscribe_services_ids = [x.service_id for x in subscribe_service_pack_records]
        # subscribe_service_group_ids = [x.service_group_id for x in subscribe_service_pack_records]
        # service_group_filter_attrs = ServiceInput(
        #     service_group_id=subscribe_service_group_ids
        # )
        # services_in_groups, _, _ = await getting_objs(
        #     info, user, ServiceTable,
        #     service_group_filter_attrs
        # )
        # services_ids_in_groups = [x.id for x in services_in_groups]
        # subscribe_services_ids.extend(services_ids_in_groups)
        # subscribe_services_ids.sort()

        # Готовим выходные данные
        result = []
        searching_result = []
        result_dict = {}
        for item in services_result_with_group_discount:
            if item[2]:
                discount_coefficient_a = item[2].discount_coefficient_a
            else:
                discount_coefficient_a = 1

            # Проверяем доступность по абонементам
            service_with_subscribe = UserServiceCartSubscribe(
                service_id=item[0].service.id,
                quantity=1
            )
            subscribe_result = await service_subscribe_availability(user, service_with_subscribe)
            # if item[0].service.id in subscribe_services_ids:
            if subscribe_result.status_code == 200:
                available_in_user_suscribe = True
            else:
                available_in_user_suscribe = False
            swp = ServiceWithPrice(
                medical_center=item[1].medical_center,
                service=item[0].service,
                price=item[0],
                discount=round((1-discount_coefficient_a)*100, 2),
                discounted_price=round(discount_coefficient_a * item[0].price_nal, 2),
                available_in_user_suscribe=available_in_user_suscribe
            )
            try:
                result_swp = result_dict[swp.service.id]
                if swp.discounted_price < result_swp.discounted_price:
                    result_dict[swp.service.id] = swp
            except Exception:
                result_dict[swp.service.id] = swp
        if search_list:
            for key, value in result_dict.items():
                for word in search_list:
                    if word in value.service.name_for_lk.lower():
                        searching_result.append(value)
        else:
            result = [value for key, value in result_dict.items()]

        end1 = time.time()
        print(f'Полное время на выполнение процедуры getting_services_with_price {(end1-start)*1000} мс')

    if searching_result:
        return sorted(searching_result, key=lambda x: x.service.name_for_lk)
    else:
        return sorted(result, key=lambda x: x.service.name_for_lk)


async def getting_service_group3(service_price_list):

    result_list = []
    # select_filter = []
    service_group_select_filter = []

    start = time.time()

    async with get_session() as s:

        if not service_price_list:
            return AccessTicketResult(
                status_code=422,
                details='Expexted 1 argument',
                details_ru='Ожидался 1 входной аргумент'
            )

        services_result = service_price_list

        services_result = sorted(services_result, key=lambda x: x.service.service_group_id)

        services_result_dict = {}

        key = 0
        services_group_ides = []
        for item in services_result:
            if item.service.service_group_id != key:
                services_result_dict[item.service.service_group_id] = []
                services_result_dict[item.service.service_group_id].append(item)
                key = item.service.service_group_id
            else:
                services_result_dict[key].append(item)
            path_list = [int(x) for x in item.service.service_group.path.split('.')]
            services_group_ides.extend(path_list)

        services_group_ides = list(set(services_group_ides))

        or_filter = []
        for group_id in services_group_ides:
            or_filter.append(ServiceGroupTable.id == group_id)
        service_group_select_filter.append(or_(
            *or_filter
        ))
        service_group_result_sql = async_select(ServiceGroupTable).filter(
            *service_group_select_filter
        )

        service_group_result = (await s.execute(service_group_result_sql.order_by(ServiceGroupTable.name))).scalars().all()

        if not service_group_result:
            return ServiceGroupResult(
                data=result_list,
                status_code=200,
                details='ok'
            )

        end1 = time.time()
        print(f'Затрачено времени на запрос из group3 в БД {(end1-start)*1000} мс')

        first_layer_sql = service_group_result_sql.filter(ServiceGroupTable.id == int(f'{service_group_result[0].path.split(".")[0]}'))
        root_node = (await s.execute(first_layer_sql)).unique().scalars().one()
        nodes_dict = {}

        for item in service_group_result:

            path=[x for x in str(item.path).split('.')]
            if not item.level_sorting_code:
                level_sorting_code = 100
            else:
                level_sorting_code = item.level_sorting_code

            wservices = []
            try:
                wservices = sorted(services_result_dict[item.id], key=lambda x: x.service.name_for_lk)
            except Exception as e:
                pass
            str_node = ServiceGroup(
                id=item.id,
                client_id=item.client_id,
                name=item.name,
                view_name=item.view_name,
                description=item.description,
                path=path,
                client_service_group_code=item.client_service_group_code,
                level_sorting_code=level_sorting_code,
                is_active=item.is_active,
                xmembers=[],
                wservices=[]
            )
            str_node.wservices.extend(wservices)
            nodes_dict[path[-1]] = str_node

        for item in nodes_dict.items():
            for i in range(0, len(item[1].path)-1):
                try:
                    if nodes_dict[item[1].path[i+1]] not in nodes_dict[item[1].path[i]].xmembers:
                        nodes_dict[item[1].path[i]].xmembers.append(nodes_dict[item[1].path[i+1]])
                except Exception as e:
                    pass
        result_list.append(await sorting_xmembers(nodes_dict[str(root_node.id)]))

    end = time.time()
    print(f'Затрачено времени на выпорлнение всей функции group3 {(end-start)*1000} мс')

    return ServiceGroupResult(
        data=result_list,
        status_code=200,
        details='ok'
    )


async def booking_access_tickets(user, main_access_ticket_client_id, tickets_clients_ides):

    proc_name_to_book = ORACLE_PROC_SET_TICKET_PATIENT
    proc_name_to_free = ORACLE_PROC_FREE_TICKET

    booked_list = []

    async with get_session() as s:

        access_ticket_list = (await s.execute(async_select(AccessTicketListTable).filter(
            AccessTicketListTable.access_ticket_client_id.in_(tickets_clients_ides)
        ))).scalars().all()
        if len(access_ticket_list):
            booked_tickets = [x.access_ticket_client_id for x in access_ticket_list]
            return RequestResult(
                    status_code=422,
                    details=f"The access_tickets {booked_tickets} already booked",
                    details_ru=f"Номерки {booked_tickets} уже забронированы"
                )

        for ticket_client_id in tickets_clients_ides:

            # Проверяем существование номерков
            access_ticket = (await s.execute(async_select(AccessTicketTable).filter(
                AccessTicketTable.client_id == int(ticket_client_id)
            ))).unique().scalars().one_or_none()
            if access_ticket:
                access_ticket.user_id = user.id
                access_ticket.bl_status = 3
                s.add(access_ticket)
                await s.flush()
            else:
                return RequestResult(
                    status_code=422,
                    details=f"The access_ticker {ticket_client_id} doesn't exist",
                    details_ru=f"Номерок с client_id={ticket_client_id} не существует"
                )

            # Создаем новую запись в пакете номерков
            new_ticket_to_list = AccessTicketListTable(
                main_access_ticket_client_id=main_access_ticket_client_id,
                access_ticket_client_id=ticket_client_id,
                user_client_id=user.client_id
            )
            s.add(new_ticket_to_list)
            await s.flush()

            # Вызываем процедуру Оракула бронирования
            data_for_oracle = [ticket_client_id, str(user.client_id), '3']
            oracle_set_result = await call_oracle_proc(data_for_oracle, proc_name_to_book)
            try:
                if oracle_set_result[0] == 500:
                    return RequestResult(
                        status_code=500,
                        details=oracle_set_result[1],
                        details_ru=oracle_set_result[2]
                    )
                if oracle_set_result[0] != 200:
                    for item in booked_list:
                        # Вызываем процедуру Оракула освобождения
                        data_for_oracle = [item]
                        oracle_free_result = await call_oracle_proc(data_for_oracle, proc_name_to_free)
                        if oracle_free_result[0] != 200:
                            await s.rollback()
                            return RequestResult(
                                status_code=500,
                                details="The process is temporary anavailable.",
                                details_ru="Процедура временно не доступна."
                            )
                    await s.rollback()
                    # await s.commit()
                    return RequestResult(
                        status_code=422,
                        details=f"Can't book the ticket{ticket_client_id}",
                        details_ru=f"Не могу забрнировать номерок {ticket_client_id}"
                    )
                else:
                    booked_list.append(ticket_client_id)
            except Exception as e:
                print(e)
                return RequestResult(
                    status_code=500,
                    details='Error of the Oracle procedure calling',
                    details_ru='Сбой обращения к процедуре Оракл'
                )

        await s.commit()

    return RequestResult(
        status_code=200,
        details='Ok',
        details_ru='Ок'
    )


async def setting_free_access_tickets(patient_client_id, main_access_ticket_client_id):

    start = time.time()

    proc_name_to_book = ORACLE_PROC_SET_TICKET_PATIENT
    proc_name_to_free = ORACLE_PROC_FREE_TICKET

    set_free_list = []

    async with get_session() as s:

        # Проверяем существование номерка
        access_ticket_list = (await s.execute(async_select(AccessTicketListTable).filter(
            AccessTicketListTable.main_access_ticket_client_id == main_access_ticket_client_id,
            AccessTicketListTable.user_client_id == patient_client_id
        ))).scalars().all()
        if not access_ticket_list:
            return RequestResult(
                status_code=422,
                details=f"The access_ticket {main_access_ticket_client_id} doesn't book or booked to other user",
                details_ru=f"Номерок {main_access_ticket_client_id} не забронирован или забронирован на другого пользователя"
            )

        time_1 = time.time()
        print(f'Затрачено времени на проверку существования номерка {(time_1-start)*1000} мс')

        # Проверяем, связан ли главный номерок с услугами и освобождаем их
        user_service_cart_ids = (await s.execute(async_select(
            UserServiceCartTable.id
        ).filter(
            UserServiceCartTable.access_ticket.has(
                AccessTicketTable.client_id == int(main_access_ticket_client_id)
            )
        ))).unique().scalars().all()
        if user_service_cart_ids:
            for cart_id in user_service_cart_ids:
                (await s.execute(update(
                    UserServiceCartTable
                ).filter(
                    UserServiceCartTable.id == cart_id
                ).values(
                    access_ticket_id=None
                )))
                await s.flush()

        # Удаляем пакет номерков
        try:
            for ticket in access_ticket_list:
                await s.delete(ticket)
                await s.flush()
                access_ticket = (await s.execute(async_select(AccessTicketTable).filter(
                    AccessTicketTable.client_id == int(ticket.access_ticket_client_id)
                ))).scalars().one_or_none()
                if access_ticket:
                    access_ticket.user_id = None
                    access_ticket.bl_status = 1
                    s.add(access_ticket)
                    await s.flush()
        except Exception as e:
            print(e)
            return RequestResult(
                status_code=422,
                details=f"Can't delete ticket {main_access_ticket_client_id} and liked with him",
                details_ru=f"Не могу удалить номерок {main_access_ticket_client_id} и связанные с ним"
            )

        for ticket in access_ticket_list:
            # Вызываем процедуру Оракула освобождения
            data_for_oracle = [ticket.access_ticket_client_id]
            oracle_set_result = await call_oracle_proc(data_for_oracle, proc_name_to_free)
            if oracle_set_result[0] != 200:
                for ticket in set_free_list:
                    # Вызываем процедуру Оракула бронирования
                    data_for_oracle = [ticket.access_ticket_client_id, str(ticket.user_client_id), '3']
                    oracle_set_result = await call_oracle_proc(data_for_oracle, proc_name_to_book)
                await s.rollback()
                # await s.commit()
                return RequestResult(
                    status_code=422,
                    details=f"Can't set free the ticket{ticket.access_ticket_client_id}",
                    details_ru=f"Не могу освоболить номерок {ticket.access_ticket_client_id}"
                )
            else:
                set_free_list.append(ticket)
        await s.commit()

        time_4 = time.time()
        print(f'Всего затрачено времени {(time_4-start)*1000} мс')

    return RequestResult(
        status_code=200,
        details='Ok',
        details_ru='Ок'
    )


async def finding_access_tickets_ides(search_list):

    search_filter = []

    for word in search_list:
        search_filter.append(or_(
            AccessTicketTable.doctor_mcenters.has(DoctorMedicalCenterTable.doctor.has(DoctorTable.first_name.ilike(f'%{word}%'))),
            AccessTicketTable.doctor_mcenters.has(DoctorMedicalCenterTable.doctor.has(DoctorTable.last_name.ilike(f'%{word}%'))),
            AccessTicketTable.doctor_mcenters.has(DoctorMedicalCenterTable.doctor.has(DoctorTable.patronymic.ilike(f'%{word}%'))),
            # AccessTicketTable.doctor_mcenters.has(DoctorMedicalCenterTable.doctor.has(DoctorTable.email.ilike(f'%{word}%'))),
            # AccessTicketTable.doctor_mcenters.has(DoctorMedicalCenterTable.medical_speciality.has(
            #     MedicalSpecialityTable.search_name.ilike(f'%{word}%')
            # )),
            # AccessTicketTable.doctor_mcenters.has(DoctorMedicalCenterTable.medical_speciality.has(
            #     MedicalSpecialityTable.search_description.ilike(f'%{word}%')
            # )),
            # AccessTicketTable.doctor_mcenters.has(DoctorMedicalCenterTable.medical_speciality.has(
            #     MedicalSpecialityTable.view_name.ilike(f'%{word}%')
            # )),
            AccessTicketTable.doctor_mcenters.has(DoctorMedicalCenterTable.medical_position.has(
                MedicalPositionTable.search_name.ilike(f'%{word}%')
            )),
            # AccessTicketTable.doctor_mcenters.has(DoctorMedicalCenterTable.medical_position.has(
            #     MedicalPositionTable.search_description.ilike(f'%{word}%')
            # )),
            # AccessTicketTable.doctor_mcenters.has(DoctorMedicalCenterTable.medical_position.has(
            #     MedicalPositionTable.view_name.ilike(f'%{word}%')
            # )),
            ServiceMedicalSpecialityTable.service.has(ServiceTable.name_for_lk.ilike(f'%{word}%')),
            DoctorMedicalCenterServiceTable.service.has(ServiceTable.name_for_lk.ilike(f'%{word}%'))
            ))

    async with get_session() as s:

        result = (await s.execute(async_select(
            AccessTicketTable.id
        ).outerjoin(
            ServiceMedicalSpecialityTable,
            ServiceMedicalSpecialityTable.medical_speciality_id == async_select(
                DoctorMedicalCenterTable.medical_speciality_id
            ).filter(
                DoctorMedicalCenterTable.id == AccessTicketTable.doctor_mcenters_id
            )
        ).outerjoin(
            DoctorMedicalCenterServiceTable,
            DoctorMedicalCenterServiceTable.doctor_mcenters_id == AccessTicketTable.doctor_mcenters_id
        ).outerjoin(
            ServiceTable,
            ServiceTable.id == DoctorMedicalCenterServiceTable.service_id
        ).filter(
            *search_filter
        ))).unique().scalars().all()

        return result


async def getting_subscribe_info_blocks(info, patient, subscribe_id):

    start = time.time()

    today = datetime.datetime.today()

    # Получаем абонемент пациента
    subscribe_filtering_attrs = UserSubscribeInput(
        id=[subscribe_id]
    )
    subscribe_list, _, _ = await getting_objs(info, patient, UserSubscribeTable,
                                              subscribe_filtering_attrs)

    if not subscribe_list:
        return SubscribeInfoBlocksResult(
            status_code=422,
            details=f"The subscribe with the number {subscribe_id} doesn't exist for patient {patient.id}",
            details_ru=f"Абонемента с номером {subscribe_id} у пользователя {patient.id} не существует"
        )

    # Получаем персонал абонемента
    subscribe_doctor_filtering_attrs = SubscribeDoctorInput(
        user_subscribe_id=subscribe_id
    )
    subscribe_doctors_list, _, _ = await getting_objs(info, patient, SubscribeDoctorTable,
                                                      subscribe_doctor_filtering_attrs)

    # Получаем график платежей
    payments_plan_filtering_attrs = PolicyPaymentPlanInput(
        policy_id=subscribe_list[0].policy.id
    )
    policy_payments_plan, _, _ = await getting_objs(info, patient, PolicyPaymentPlanTable,
                                                   payments_plan_filtering_attrs)

    #Получаем суммы оплат
    subscribe_paid_sum = await getting_subscribe_paid_sum(patient.id, subscribe_list[0].policy.id)

    # Получаем пакеты услуг
    subscribe_service_pack_records_filter_attrs = SubscribeSpackRecordInput(
        subscribe_services_pack=SubscribeServicePackIn(
            user_subscribe=UserSubscribeIn(
                policy=PolicyIn(
                    id=subscribe_list[0].policy.id,
                    user_id=patient.id
                )
            )
        )
    )

    subscribe_service_pack_records, _, _ = await getting_objs(info, patient, SubscribeSpackRecordTable,
                                                              subscribe_service_pack_records_filter_attrs)

    subscribe_service_pack_dict = dict([(x.subscribe_services_pack, 0)
                                        for x in subscribe_service_pack_records])
    subscribe_service_pack_list = []
    for item in subscribe_service_pack_records:
        subscribe_service_pack_dict[item.subscribe_services_pack] += item.quantity
    for key, value in subscribe_service_pack_dict.items():
        if value > 0:
            subscribe_service_pack_list.append(
                SubscribeServicePackWithQuantity(
                    service_pack=key,
                    services_quantity=value
                )
            )

    # Формируем выходные данные
    service_manager = None
    trusted_pediatrician = None
    if subscribe_doctors_list:
        for person in subscribe_doctors_list:
            # if 'сервисный' in person.role.name.lower():
            #     service_manager=person.doctor_mcenters
            #     subscribe_doctors_list.remove(person)
            # if 'педиатр' in person.doctor_mcenters.medical_position.view_name.lower():
            #     trusted_pediatrician=person.doctor_mcenters
            #     subscribe_doctors_list.remove(person)
            if str(person.role.client_id) == '88997000':
                service_manager=person.doctor_mcenters
                subscribe_doctors_list.remove(person)
            if str(person.role.client_id) == '88998000':
                trusted_pediatrician=person.doctor_mcenters
                subscribe_doctors_list.remove(person)

    policy_payments_plan_with_debt = []
    plan_amount = 0
    for item in policy_payments_plan:
        plan_amount += item.amount
        if item.planed_date <= today:
            if subscribe_paid_sum >= plan_amount:
                debt = None
                show_payment_button = False
            else:
                debt = plan_amount - subscribe_paid_sum
                show_payment_button = True
        else:
            debt = None
            show_payment_button = True
        policy_payments_plan_with_debt.append(
            PolicyPaymentPlanWithDebt(
                id=item.id,
                client_id=str(item.client_id),
                policy_id=item.policy_id,
                planed_date=item.planed_date,
                amount=item.amount,
                debt=debt,
                show_payment_button=show_payment_button
            )
        )

    finally_result = SubscribeInfoBlocksResult(
        data=SubscribeInfoBlocks(
            common_block=SubscribeCommonInfo(
                medical_center=subscribe_list[0].policy.medical_center,
                start_date=subscribe_list[0].policy.start_date,
                end_date=subscribe_list[0].policy.end_date,
                service_manager=service_manager,
                trusted_pediatrician=trusted_pediatrician,
                specialists=subscribe_doctors_list
            ),
            description_block=subscribe_list[0].description,
            financial_block=SubscribeFinance(
                subscribe_price=subscribe_list[0].policy.amount,
                subscribe_discount=subscribe_list[0].policy.discount,
                subscribe_payment_plan=policy_payments_plan_with_debt,
                common_subscribe_debt=subscribe_list[0].policy.amount - subscribe_paid_sum
            ),
            services_block=subscribe_service_pack_list
        ),
        details='Ok',
        details_ru='Ок',
        status_code=200
    )

    end = time.time()

    print(f'Полное время на выполнение процедуры getting_subscribe_info_blocks {(end-start)*1000} мс')

    return finally_result


async def getting_events_calendar(info, start_date, end_date, patient_ids):

    patient_select_filter = []
    payment_select_filter = []

    if patient_ids:
        patient_select_filter.append(
            UserServiceCartTable.user_id.in_(patient_ids)
        )

    async with get_session() as s:

        subscribe_dict = {}

        # Получаем на каждого пациента набор его полисов, относящихся к его абонементам
        for patient_id in patient_ids:
            user_subscribes_policies_ids = (await s.execute(async_select(
                UserSubscribeTable.policy_id
            ).outerjoin(
                PolicyTable,
                PolicyTable.id == UserSubscribeTable.policy_id
            ).outerjoin(
                UserTable,
                UserTable.id == patient_id
            ).filter(
                UserSubscribeTable.is_active == True,
                PolicyTable.is_active == True
            ))).scalars().all()
            subscribe_dict[patient_id] = user_subscribes_policies_ids

        # Исключаем временные платежи
        temporary_payments_ids = (await s.execute(async_select(
            TemporaryPaymentTable.payment_id
        ).join(
            UserPaymentTable,
            UserPaymentTable.id == TemporaryPaymentTable.payment_id
        ).filter(
            UserPaymentTable.user_id.in_(patient_ids)
        ))).scalars().all()

        if temporary_payments_ids:
            payment_select_filter.append(
                UserServiceCartTable.user_purchase.has(
                    UserPurchaseTable.user_payment_id.not_in(temporary_payments_ids)
                )
            )

        user_events_list = (await s.execute(async_select(
            UserServiceCartTable.client_id,
            AccessTicketTable,
            ServiceTable,
            PayKeeperPaymentDataTable.status,
            UserTable,
            UserServiceCartTable.service_status,
            UserPurchaseTable.user_payment_id,
            UserServiceCartTable.user_id,
            UserServiceCartTable.policy_id
        ).outerjoin(
            AccessTicketTable,
            AccessTicketTable.id == UserServiceCartTable.access_ticket_id
        ).outerjoin(
            ServiceTable,
            ServiceTable.id == UserServiceCartTable.service_id
        ).outerjoin(
            UserPurchaseTable,
            UserPurchaseTable.id == UserServiceCartTable.user_purchase_id
        ).outerjoin(
            UserPaymentTable,
            UserPaymentTable.id == UserPurchaseTable.user_payment_id
        ).outerjoin(
            PayKeeperPaymentDataTable,
            PayKeeperPaymentDataTable.user_payment_id == UserPaymentTable.id
        ).outerjoin(
            UserTable,
            UserTable.id == UserServiceCartTable.user_id
        ).filter(
            UserServiceCartTable.access_ticket_id !=None,
            UserServiceCartTable.service.has(
                ServiceTable.client_service_code != SUBSCRIBE_PAYMENT_SERVICE_CLIENT_SERVICE_CODE
            ),
            UserServiceCartTable.service.has(
                ServiceTable.client_service_code != ADVANCE_PAYMENT_SERVICE_CLIENT_SERVICE_CODE
            ),
            AccessTicketTable.ticket_datetime >= start_date,
            AccessTicketTable.ticket_datetime <= end_date,
            *patient_select_filter,
            *payment_select_filter
        ).order_by(AccessTicketTable.ticket_datetime)
        )).unique().all()

        result_list = []

        for item in user_events_list:
            if item[3] == 'success':
                is_paid = True
                payment_method = 'Оплачена'
            elif item[8] in subscribe_dict[item[7]]:
                is_paid = True
                payment_method = 'По договору'
            else:
                is_paid = False
                payment_method = 'Не оплачена'
            is_done = False
            is_canceled = False
            if item[5]:
                if item[5] == 1:
                    is_done = True
                elif item[5] == 2:
                    is_canceled = True
            result_list.append(
                EventsCalendar(
                    user_id=item[4].id,
                    user_fio=item[4].fio(),
                    user_birth_date=item[4].birth_date,
                    doctors_fio=item[1].doctor_mcenters.doctor.fio(),
                    doctors_position=item[1].doctor_mcenters.medical_position.view_name,
                    service_date_and_time=item[1].ticket_datetime,
                    service_name=item[2].name_for_lk,
                    service_preparation_rules=item[2].preparation_rules,
                    service_duration=str(item[2].execution_time),
                    medical_center_name=item[1].doctor_mcenters.medical_center.name,
                    medical_center_address=item[1].doctor_mcenters.medical_center.address,
                    room_number=item[1].ticket_room,
                    is_paid=is_paid,
                    is_done=is_done,
                    is_canceled=is_canceled,
                    user_service_cart_client_id=item[0],
                    access_ticket_client_id=item[1].client_id,
                    payment_id = item[6],
                    doctor_mcenters_id=item[1].doctor_mcenters_id,
                    service_id=item[2].id,
                    medical_center_id=item[1].doctor_mcenters.medical_center_id,
                    payment_method=payment_method
                )
            )

    return result_list


async def changing_user_service_booking(user_service_cart_client_id: str,
                                        new_main_access_ticket_client_id: str,
                                        new_tickets_client_ids: List[str]
                                       ):

    async with get_session() as s:

        # Получаем запись user_service_cart
        user_service_cart_obj = (await s.execute(async_select(
            UserServiceCartTable
        ).filter(
            UserServiceCartTable.client_id == int(user_service_cart_client_id)
        ))).unique().scalars().one_or_none()

        if not user_service_cart_obj:
            return RequestResult(
                status_code = 422,
                details=f"The user_service_cart with client_id {user_service_cart_client_id} doesn't exist",
                details_ru=f"Записи на услугу с user_service_cart_client_id {user_service_cart_client_id} не существует"
            )

        old_main_access_ticket_client_id = user_service_cart_obj.access_ticket.client_id

        # Бронируем новый номерок с пакетом других, если требуется
        new_booking_result = await booking_access_tickets(
            user_service_cart_obj.user,
            new_main_access_ticket_client_id,
            new_tickets_client_ids
        )
        if new_booking_result.status_code != 200:
            return new_booking_result
        new_access_ticket_obj = (await s.execute(async_select(
            AccessTicketTable
        ).filter(
            AccessTicketTable.client_id == int(new_main_access_ticket_client_id)
        ))).unique().scalars().one_or_none()
        user_service_cart_obj.access_ticket_id = new_access_ticket_obj.id
        user_service_cart_obj.start_date = new_access_ticket_obj.ticket_datetime
        user_service_cart_obj.end_date = new_access_ticket_obj.ticket_datetime + datetime.timedelta(
            minutes=new_access_ticket_obj.ticket_duration
        )
        s.add(user_service_cart_obj)

        # Вызываем процедуру Оракула перезаписи услуги на новый номерок
        data_for_oracle = [user_service_cart_client_id, new_main_access_ticket_client_id]
        oracle_set_result = await call_oracle_proc(data_for_oracle, ORACLE_PROC_CHANGE_RNUMB_FOR_PATSERV)
        if oracle_set_result[0] != 200:
            await s.rollback()
            result_free_access_ticket = await setting_free_access_tickets(
                user_service_cart_obj.user.client_id,
                new_main_access_ticket_client_id
            )
            return RequestResult(
                status_code=422,
                details=f"Can't change the ticket for the servoce {user_service_cart_client_id}",
                details_ru=f"Не могу перезаписать номерок для услуги {user_service_cart_client_id}"
            )

        # Освобождаем старые номерки
        result_free_access_ticket = await setting_free_access_tickets(
            user_service_cart_obj.user.client_id,
            str(old_main_access_ticket_client_id)
        )
        if result_free_access_ticket.status_code != 200:
            await s.rollback()
            return RequestResult(
                status_code=422,
                details=f"Can't set free the ticket{new_main_access_ticket_client_id}",
                details_ru=f"Не могу освоболить номерок {new_main_access_ticket_client_id}"
            )

        await s.commit()

    return result_free_access_ticket


async def canceling_not_paid_service(user, user_service_cart_client_id):

    # Получаем айдишники всех родственников
    relatives_ids = await getting_relatives_ids(user.id)
    relatives_ids.append(user.id)

    async with get_session() as s:

        # Получаем запись user_service_cart
        user_service_cart_obj = (await s.execute(async_select(
            UserServiceCartTable
        ).filter(
            UserServiceCartTable.client_id == int(user_service_cart_client_id),
            UserServiceCartTable.service_status != 1
        ))).unique().scalars().one_or_none()

        if not user_service_cart_obj:
            return RequestResult(
                status_code = 422,
                details=f"The service {user_service_cart_client_id} doesn't exist \
                          or it has been done. It can't be canceled.",
                details_ru=f"Услуга {user_service_cart_client_id} не существует или \
                             уже выполнена и не может быть отменена."
            )

        if user_service_cart_obj.user_id not in relatives_ids:
            return RequestResult(
                status_code = 422,
                details=f"You can't cancel the service {user_service_cart_client_id} \
                          because the user {user_service_cart_obj.user_id} isn't your \
                          relative",
                details_ru=f"ВЫ не можете отменить услугу {user_service_cart_client_id} \
                             потому что пациент {user_service_cart_obj.user_id} не \
                             является вашим родственником."
            )

        # Получаем данные об оплате услуги
        pay_keeper_obj = (await s.execute(async_select(
            PayKeeperPaymentDataTable.id
        ).filter(
            PayKeeperPaymentDataTable.user_payment_id == user_service_cart_obj.user_purchase.user_payment_id
        ))).unique().scalars().one_or_none()

        if pay_keeper_obj:
            return RequestResult(
                status_code = 422,
                details=f"The services {user_service_cart_obj.service.name_forlk} is \
                          paid. You can rebooking it",
                details_ru=f"Услуга {user_service_cart_obj.service.name_forlk} \
                             оплачена. Вы ее можете перенести или отменить в МЦ."
            )

        # Вызываем процедуру Оракла для удаления платежа
        data_for_oracle = [str(user_service_cart_obj.user_purchase.user_payment.client_id), '1']
        oracle_set_result = await call_oracle_proc(data_for_oracle, ORACLE_PROC_DELETE_PAYMENT)
        if oracle_set_result[0] != 200:
            return RequestResult(
                status_code=422,
                details=f"Can't delete the service {user_service_cart_client_id} \
                          from Oracle",
                details_ru=f"Не могу удалить услугу \
                             {user_service_cart_client_id}"
            )

        # Освобождаем номерки
        res = await setting_free_access_tickets(
            user_service_cart_obj.user.client_id,
            str(user_service_cart_obj.access_ticket.client_id)
        )
        if res.status_code != 200:
            return RequestResult(
                status_code = 422,
                details=f"The access ticket {user_service_cart_obj.access_ticket.client_id} is wrong",
                details_ru=f"Ошибочный номерок {user_service_cart_obj.access_ticket.client_id}"
            )

        # Удаляем платеж, покупки пользователя и услугу

        # (await s.execute(delete(
        #     TemporaryPaymentTables
        # ).filter(
        #     TemporaryPaymentTable.payment_id == payment_id
        # )))

        await s.delete(user_service_cart_obj.user_purchase)
        await s.flush()
        await s.delete(user_service_cart_obj.user_purchase.user_payment)
        await s.flush()
        await s.delete(user_service_cart_obj)
        await s.flush()
        await s.commit()

    return RequestResult(
        status_code = 200,
        details='Ok',
        details_ru='Ок'
    )


async def mis_update_users_default_mc(user, default_medical_center_id):
    # Вызываем процедуру Оракула для изменения медцентра по умолчанию

    async with get_session() as s:

        default_medical_center = (await s.execute(async_select(
            MedicalCenterTable
        ).filter(
            MedicalCenterTable.id == default_medical_center_id
        ))).unique().scalars().one_or_none()

        data_for_oracle = [user.client_id, str(default_medical_center.client_id)]
        oracle_set_result = await call_oracle_proc(data_for_oracle, ORACLE_PROC_UPDATE_USER_DEFAULT_MC)
        if oracle_set_result[0] != 200:
            return RequestResult(
                status_code=oracle_set_result[0],
                details=f"The Orakle's procedure {ORACLE_PROC_UPDATE_USER_DEFAULT_MC} has been failed",
                details_ru=f"Процедура Оракл {ORACLE_PROC_UPDATE_USER_DEFAULT_MC} потерпела неудачу"
            )
        else:
            return RequestResult(
                status_code = 200,
                details="Ok",
                details_ru="Ок"
            )


async def getting_visits_history(info, start_date, end_date, patient_ids):
    """
    Процедура формирования истории посещений
    """
    async with get_session() as s:
        user_services_objs = (await s.execute(async_select(
            UserServiceCartTable.client_id,
            ServiceTable.name_for_lk,
            UserServiceCartTable.start_date,
            DoctorMedicalCenterTable,
            UserServiceCartTable.service_status,
            UserSubscribeTable.name,
            UserTable,
            UserServiceCartTable.policy_id,
            UserServiceCartTable.shifr_id
        ).outerjoin(
            ServiceTable,
            ServiceTable.id == UserServiceCartTable.service_id
        ).outerjoin(
            UserSubscribeTable,
            UserSubscribeTable.policy_id == UserServiceCartTable.policy_id
        ).outerjoin(
            DoctorMedicalCenterTable,
            DoctorMedicalCenterTable.id == UserServiceCartTable.doctor_mcenter_exec_id
        ).outerjoin(
            UserTable,
            UserTable.id == UserServiceCartTable.user_id
        ).filter(
            UserServiceCartTable.start_date >= start_date,
            UserServiceCartTable.start_date <= end_date,
            UserServiceCartTable.service_status != None,
            UserServiceCartTable.user_id.in_(patient_ids),
            UserServiceCartTable.service.has(
                ServiceTable.client_service_code != ADVANCE_PAYMENT_SERVICE_CLIENT_SERVICE_CODE
            ),
            UserServiceCartTable.service.has(
                ServiceTable.client_service_code != SUBSCRIBE_PAYMENT_SERVICE_CLIENT_SERVICE_CODE
            )
        ).order_by(UserServiceCartTable.start_date.desc()))).all()

        user_plan_services_objs = (await s.execute(async_select(
            UserServicePlanTable.service_id,
            ServiceTable.name_for_lk,
            UserServicePlanTable.plan_date,
            DoctorMedicalCenterTable,
            UserServicePlanTable.status,
            UserSubscribeTable.name,
            UserTable,
            UserServicePlanTable.policy_id,
            UserServicePlanTable.shifr_id
        ).outerjoin(
            ServiceTable,
            ServiceTable.id == UserServicePlanTable.service_id
        ).outerjoin(
            UserSubscribeTable,
            UserSubscribeTable.policy_id == UserServicePlanTable.policy_id
        ).outerjoin(
            DoctorMedicalCenterTable,
            DoctorMedicalCenterTable.id == UserServicePlanTable.doctor_send_id
        ).outerjoin(
            UserTable,
            UserTable.id == UserServicePlanTable.user_id
        ).filter(
            UserServicePlanTable.plan_date >= start_date,
            UserServicePlanTable.plan_date <= end_date,
            UserServicePlanTable.status != None,
            UserServicePlanTable.user_id.in_(patient_ids)
        ).order_by(UserServicePlanTable.plan_date.desc()))).all()

    result_list = []
    for item in user_services_objs:
        if item[4] == 0 or item[4] == 3:
            status = 'Назначена'
        elif item[4] == 1:
            status = 'Выполнена'
        elif item[4] == 2:
            status = 'Отменена'
        if item[5] is not None:
            obtaining_method = item[5]
        else:
            obtaining_method = 'Платно'
        result_list.append(
            VisitHistoryRecord(
                user_services_carts_client_id=item[0],
                user_services_plans_client_id=None,
                service_name=item[1],
                service_data=item[2],
                service_doctor=item[3],
                service_status=status,
                obtaining_method=obtaining_method,
                user=item[6]
            )
        )

    for item in user_plan_services_objs:
        if item[4] == 0 or item[4] == 1:
            status = 'Рекоментована'
        elif item[4] == 2:
            status = 'Отменена'
        if item[6] is not None:
            obtaining_method = item[5]
        else:
            obtaining_method = 'Платно'
        result_list.append(
            VisitHistoryRecord(
                user_services_carts_client_id=None,
                user_services_plans_client_id=item[0],
                service_name=item[1],
                service_data=item[2],
                service_doctor=item[3],
                service_status=status,
                obtaining_method=obtaining_method,
                user=item[6]
            )
        )

    result_list = sorted(result_list, key=lambda x: x.service_data, reverse=True)

    return result_list


async def getting_objs_rew(info, patient, model,
                            filtering_attrs,
                            ordering_attrs,
                            skip,
                            limit,
                            desc_sorting):

    async with get_session() as s:

        tickets_list = (await s.execute(async_select(
            AccessTicketTable
        ).offset(skip).limit(limit).order_by(AccessTicketTable.ticket_datetime.desc()))).scalars().all()

    return tickets_list, None, None
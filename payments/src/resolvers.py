import xmltodict
from datetime import datetime, timedelta
from sqlalchemy.future import select as async_select
from sqlalchemy import and_, func, or_

from core.sa_tables.main_process import (ServiceTable, AccessTicketTable,
                                         PriceTable, UserServiceCartTable, PolicyTable, ShifrDiscountTable,
                                         ShifrDiscountPeriodTable, UserPurchaseTable, UserPaymentTable,
                                         UserUsedAdvanceTable, PricePeriodTable, PaymentTypeTable,
                                         MedicalCenterPriceNameTable, MedicalCenterTable, PayKeeperPaymentDataTable,
                                         UserSubscribeTable, UserDocumentRequestTable)
from core.sa_tables.accounts import UserTable
from core.config.scalars import RequestResult
from core.config.db import get_session
from core.config.settings import (SUBSCRIBE_PAYMENT_SERVICE_CLIENT_SERVICE_CODE,
                                  ADVANCE_PAYMENT_SERVICE_CLIENT_SERVICE_CODE)
from core.config.cache_connector import CacheConnector
from core.src.common_resolvers import getting_relatives_ids
from oracle_connector.scripts.oracle_connector import call_oracle_proc
from oracle_connector.config.settings import (ORACLE_PROC_CREATE_PATIENT_SERVICE,
                                              ORACLE_PROC_CREATE_PAYMENT_FOR_PATSERV,
                                              ORACLE_PROC_CREATE_EMAIL_PAYSERV_INFO)
from payments.config.settings import (POSTPONED_ADVANCE, ADVANCE_SERVICE_CLIENT_ID,
                                      COMMON_SERVICE_TAX_RATE)
from .scalars import (ServicePaymentInfo, PaymentInfo, PaymentDataResult, PaynemtData,
                      UserServicesForOracle, UserPaymentForOracle, McentersUnuseAdvancesSum,
                      ServiceCurrentDebt, PaymentsWithServices, ServicesDebt, CurrentDebt)
from .utils import getting_subscribes_users_debt_sum


cache = CacheConnector()


async def creating_user_payment_and_purchases(user, patient, services_to_pay,
                                              payment_type_client_id,
                                              lpu_id,
                                              patient_unused_advances_sum=None,
                                              medical_center_client_id=None,
                                              subscribe_amount_to_pay=None,
                                              user_subscribe=None):

    today = datetime.today()

    services_payment_list = []
    user_services_for_oracle_list = []

    async with get_session() as s:

        # Получаем тип платежа.
        payment_type_obj = (await s.execute(async_select(
            PaymentTypeTable
        ).filter(
            PaymentTypeTable.client_id == int(payment_type_client_id),
        ))).scalars().one_or_none()

        if not payment_type_obj:
            return RequestResult(
                status_code=422,
                details=f"The payment_type_client_id={payment_type_client_id} doesn't exist",
                details_ru=f"Параметр payment_type_client_id {payment_type_client_id} не существует"
            )

        # Создаем новый платеж
        new_user_payment_obj = UserPaymentTable(
            user_id=patient.id,
            payment_date=today,
            amount=0,
            payment_type_id=payment_type_obj.id,
            lpu_id=lpu_id
        )
        s.add(new_user_payment_obj)
        await s.flush()

        payment_amount = 0
        discount_amount = 0
        full_amount = 0
        access_ticket_obj = None

        for service in services_to_pay:
            # Проверяем наличие прайса
            if not service.price_id:
                price_obj = (await s.execute(async_select(
                    PriceTable
                ).filter(
                    PriceTable.service_id == service.service_id,
                    and_(
                        PriceTable.price_period.has(PricePeriodTable.start_date <= today),
                        PriceTable.price_period.has(PricePeriodTable.end_date >= today)
                    ),
                    PriceTable.price_name_id == (async_select(
                        MedicalCenterPriceNameTable.price_name_id
                    ).filter(
                        MedicalCenterPriceNameTable.medical_center_id == service.medical_center_id
                    ))
                ))).scalars().one_or_none()
            else:
                price_obj = (await s.execute(async_select(PriceTable).filter(
                    PriceTable.id == service.price_id,
                    PriceTable.service_id == service.service_id,
                    and_(
                        PriceTable.price_period.has(PricePeriodTable.start_date <= today),
                        PriceTable.price_period.has(PricePeriodTable.end_date >= today)
                    )
                ))).unique().scalars().one_or_none()
            if not price_obj:
                return RequestResult(
                status_code=422,
                details=f"The price {service.price_id} for the service {service.service_id} doesn't exist",
                details_ru=f"Прайс {service.price_id} для услуги {service.service_id} не существует"
            )

            # Создаем новую запись в корзине пользователя
            new_user_service_cart_obj = UserServiceCartTable(
                user_id=patient.id,
                service_id=service.service_id,
                medical_center_id=service.medical_center_id,
                price_id=price_obj.id,
                access_ticket_id=service.access_ticket_id,
                quantity=service.quantity,
                doctor_mcenter_id=service.doctor_mcenter_id,
                service_status=0,
                stac_satus=False
            )

            # Получаем полис пациента
            if user_subscribe is not None:
                policy_obj = user_subscribe.policy
                max_discount_coefficient=policy_obj.discount_coefficient
            else:
                policy_objs = (await s.execute(async_select(PolicyTable).filter(
                    PolicyTable.user_id == patient.id,
                    and_(
                        PolicyTable.start_date <= today,
                        or_(
                            PolicyTable.end_date >= today,
                            PolicyTable.end_date == None
                        )
                    )
                ))).unique().scalars().all()

                if policy_objs:

                    policy_obj = policy_objs[0]

                    shifr_ides = [x.shifr_id for x in policy_objs]

                    service_group_id_subquery = async_select(ServiceTable.service_group_id
                    ).filter(
                        ServiceTable.id == service.service_id
                    ).scalar_subquery()

                    shifr_discount_and_policy_obj = (await s.execute(async_select(
                        ShifrDiscountTable,
                        PolicyTable
                    ).outerjoin(
                        ServiceTable,
                        ServiceTable.id == ShifrDiscountTable.service_id
                    ).outerjoin(
                        PolicyTable,
                        PolicyTable.shifr_id == ShifrDiscountTable.shifr_id
                    ).filter(
                        ShifrDiscountTable.shifr_id.in_(shifr_ides),
                        or_(
                            and_(
                                ShifrDiscountTable.service_id == service.service_id,
                                ShifrDiscountTable.service_group_id == None
                            ),
                            and_(
                                ShifrDiscountTable.service_group_id == service_group_id_subquery,
                                ShifrDiscountTable.service_id == None
                            )
                        ),
                        and_(
                            ShifrDiscountTable.shift_discount_period.has(ShifrDiscountPeriodTable.start_date <= today),
                            ShifrDiscountTable.shift_discount_period.has(ShifrDiscountPeriodTable.end_date >= today)
                        )
                    ).distinct(PolicyTable.shifr_id).order_by(PolicyTable.shifr_id))).unique().all()

                    if shifr_discount_and_policy_obj:
                        max_discount_coefficient = min([x[0].discount_coefficient_a for x in shifr_discount_and_policy_obj])
                    else:
                        max_discount_coefficient = 1

                    for item in shifr_discount_and_policy_obj:
                        if item[0].discount_coefficient_a == max_discount_coefficient:
                            policy_obj = item[1]
                else:
                    return RequestResult(
                        status_code=422,
                        details=f"The user {patient.id} doesn't have a valid policy",
                        details_ru=f"Пользователь {patient.id} не имеет действующего полиса"
                    )
            new_user_service_cart_obj.policy_id = policy_obj.id
            new_user_service_cart_obj.shifr_id = policy_obj.shifr_id
            new_user_service_cart_obj.discount_coefficient = max_discount_coefficient

            # Валидируем номерок
            if service.access_ticket_id:
                if not access_ticket_obj:
                    # Проверяем, связан ли главный номерок с услугой
                    # user_service_cart_id = (await s.execute(async_select(
                    #     UserServiceCartTable.id
                    # ).filter(
                    #     UserServiceCartTable.access_ticket.has(
                    #         AccessTicketTable.id == service.access_ticket_id
                    #     )
                    # ))).scalars().one_or_none()
                    # if user_service_cart_id:
                    #     return RequestResult(
                    #         status_code=422,
                    #         details=f"""The access_ticket {service.access_ticket_id}\
                    #                  has been connected with a service.To set the access ticket free you\
                    #                  must change the connect between the ticket and the service.""",
                    #         details_ru=f"""Номерок {service.access_ticket_id} связан с услугой.\
                    #                     Чтобы освободить номерок, вы должны перезаписать услугу на другой."""
                    #     )
                    # Получаем номерок
                    access_ticket_obj = (await s.execute(async_select(AccessTicketTable).filter(
                        AccessTicketTable.id == service.access_ticket_id,
                        AccessTicketTable.user_id == patient.id,
                        # AccessTicketTable.bl_status == 3
                    ))).unique().scalars().one_or_none()
                if access_ticket_obj:
                    new_user_service_cart_obj.start_date = access_ticket_obj.ticket_datetime
                    access_ticket_obj.bl_status = 2
                    s.add(access_ticket_obj)
                    await s.flush()
                else:
                    return RequestResult(
                        status_code=422,
                        details=f"The access ticket {service.access_ticket_id} didn't book for the patient {patient.id} or it is used secondary",
                        details_ru=f"Номерок {service.access_ticket_id} не забронирован для пациента {patient.id} либо используется повторно"
                    )
                if access_ticket_obj.doctor_mcenters.medical_center_id != service.medical_center_id:
                    return RequestResult(
                        status_code=422,
                        details=f"The access ticket {service.access_ticket_id} didn't correspond with medical center {service.medical_center_id}",
                        details_ru=f"Номерок {service.access_ticket_id} не соответствует медицинскому центру {service.medical_center_id}"
                    )

            # Валидируем услугу
            service_obj = (await s.execute(async_select(ServiceTable).filter(
                ServiceTable.id == service.service_id
            ))).unique().scalars().one_or_none()

            if service_obj:
                new_user_service_cart_obj.complex_service_id = service_obj.id if service_obj.is_complex_service else None
                new_user_service_cart_obj.complex_service_status = 1 if service_obj.is_complex_service else 0
                new_user_service_cart_obj.stac_satus = None
                new_user_service_cart_obj.cito_status = service_obj.is_urgent
                new_user_service_cart_obj.description = service_obj.full_description
                if (patient_unused_advances_sum is None) and (user_subscribe is None):
                    new_user_service_cart_obj.service_status = 0  #1  # Need to set "0" after texting
            else:
                return RequestResult(
                    status_code=422,
                    details=f"The service {service.service_id} doesn't exist",
                    details_ru=f"Услуга {service.service_id} не существует"
                )
            if new_user_service_cart_obj.start_date:
                new_user_service_cart_obj.end_date = new_user_service_cart_obj.start_date + timedelta(minutes=service_obj.execution_time)
            else:
                new_user_service_cart_obj.start_date = datetime.today()

            # Если оплата абонемента (договора)
            if subscribe_amount_to_pay is not None:
                new_user_service_cart_obj.discount_coefficient = 1

            new_user_service_cart_obj.price_id = price_obj.id
            if new_user_service_cart_obj.discount_coefficient and payment_type_client_id != POSTPONED_ADVANCE:
                new_user_service_cart_obj.discount = price_obj.price_nal * (1 - new_user_service_cart_obj.discount_coefficient)
            else:
                new_user_service_cart_obj.discount = 0
            s.add(new_user_service_cart_obj)
            await s.flush()

            # Создаем новую запись в покупках пользователя
            new_user_purches_obj = UserPurchaseTable(
                user_id=patient.id,
                user_payment_id=new_user_payment_obj.id,
                payment_date=new_user_payment_obj.payment_date,
                service_quantity=service.quantity
            )

            new_user_purches_obj.policy_id = policy_obj.id
            new_user_purches_obj.shifr_id = policy_obj.shifr_id
            new_user_purches_obj.discount_koef = max_discount_coefficient
            new_user_purches_obj.service_id = service_obj.id
            # new_user_purches_obj.service_quantity = service.quantity
            new_user_purches_obj.price = price_obj.price_nal
            new_user_purches_obj.discount = new_user_service_cart_obj.discount
            new_user_purches_obj.amount = new_user_purches_obj.price - new_user_service_cart_obj.discount

            s.add(new_user_purches_obj)
            await s.flush()

            new_user_service_cart_obj.user_purchase_id = new_user_purches_obj.id
            s.add(new_user_service_cart_obj)
            await s.flush()

            # Готовим список для создания услуг в МИС
            user_services_for_oracle = UserServicesForOracle()
            for key in user_services_for_oracle.__dict__.keys():
                value = getattr(new_user_service_cart_obj, key, None)
                if isinstance(value, datetime):
                    value = value.strftime("%Y-%m-%d")
                setattr(user_services_for_oracle, key, value)
            user_services_for_oracle.service_client_id = str(service_obj.client_id)
            user_services_for_oracle.user_client_id = str(patient.client_id)
            user_services_for_oracle.policy_client_id = str(policy_obj.client_id)
            user_services_for_oracle.medical_center_client_id = str(
                access_ticket_obj.doctor_mcenters.medical_center.client_id
            ) if access_ticket_obj else medical_center_client_id
            user_services_for_oracle.price_client_id = str(price_obj.client_id)
            user_services_for_oracle.shifr_client_id = str(policy_obj.shifr.client_id)
            user_services_for_oracle.access_ticket_client_id = str(
                access_ticket_obj.client_id
            ) if access_ticket_obj else None
            user_services_for_oracle.doctor_mcenter_client_id = str(
                access_ticket_obj.doctor_mcenters.client_id
            ) if access_ticket_obj else None
            if service_obj.is_urgent:
                user_services_for_oracle.cito_status = 1
            else:
                user_services_for_oracle.cito_status = 0
            if new_user_service_cart_obj.stac_satus:
                user_services_for_oracle.stac_satus = None
            else:
                user_services_for_oracle.stac_satus = None
            user_services_for_oracle.description = ''
            user_services_for_oracle_list.append(
                (user_services_for_oracle, new_user_service_cart_obj, new_user_purches_obj)
            )

            # Создаем Список услуг и информацию для выполнения оплаты
            if not subscribe_amount_to_pay:
                service_amount = new_user_purches_obj.amount * new_user_purches_obj.service_quantity
                # price = new_user_purches_obj.amount
            else:
                service_amount = subscribe_amount_to_pay
                # price = subscribe_amount_to_pay
            services_payment_list.append(
                ServicePaymentInfo(
                    name=f'{service_obj.name_for_mz}',
                    price=new_user_purches_obj.amount,
                    quantity=new_user_purches_obj.service_quantity,
                    sum=service_amount,
                    tax=COMMON_SERVICE_TAX_RATE
                ) if service_obj.client_id != ADVANCE_SERVICE_CLIENT_ID else ServicePaymentInfo(
                    name=f'{service_obj.name_for_mz}',
                    price=service_amount,
                    quantity=1,
                    sum=service_amount,
                    tax=COMMON_SERVICE_TAX_RATE
                )
            )
            payment_amount += service_amount
            discount_amount += new_user_service_cart_obj.discount * new_user_purches_obj.service_quantity
            full_amount += new_user_purches_obj.price * new_user_purches_obj.service_quantity

        new_user_payment_obj.policy_id = policy_obj.id
        new_user_payment_obj.shifr_id = policy_obj.shifr_id
        new_user_payment_obj.amount = payment_amount
        new_user_payment_obj.discount_amount = discount_amount
        new_user_payment_obj.full_amount = full_amount
        if payment_type_client_id == POSTPONED_ADVANCE:
            new_user_payment_obj.avance_amount = payment_amount
            new_user_payment_obj.avance_status = 0
        s.add(new_user_payment_obj)
        await s.flush()

        payment_info = PaymentInfo(
            pay_amount=payment_amount,
            user_id=user.fio(),
            user_payment_id=new_user_payment_obj.id,
            user_email=user.email,
            user_phone_number=user.phone_number
        )

        # Вызываем процедуры МИС для создания услуг и отложенного платежа
        if patient_unused_advances_sum:
            if patient_unused_advances_sum < payment_amount:
                return RequestResult(
                    status_code=422,
                    details=f"The unused advance amount {patient_unused_advances_sum} is less than summary services cost {payment_amount}",
                    details_ru=f"Сумма неиспользованных авансов {patient_unused_advances_sum} меньше, чем суммарная стоимость выбранных услуг {payment_amount}"
                )
            else:
                advance_user_payment_client_ides = (await s.execute(async_select(
                    UserPaymentTable.client_id
                ).filter(
                    UserPaymentTable.user_id == patient.id,
                    UserPaymentTable.avance_status == 0,
                    UserPaymentTable.lpu_id == lpu_id,
                    UserPaymentTable.id.in_(async_select(
                        PayKeeperPaymentDataTable.user_payment_id
                    ))
                ))).scalars().all()
                advance_user_payment_client_ides = ",".join([str(x) for x in advance_user_payment_client_ides])
                used_advance_amount = payment_amount
        else:
            advance_user_payment_client_ides = None
            used_advance_amount = None
        user_payment_for_oracle = UserPaymentForOracle(
            patient_client_id=str(patient.client_id),
            policy_client_id=str(policy_obj.client_id),
            shifr_client_id=str(policy_obj.shifr.client_id),
            payment_type_client_id=payment_type_client_id,
            medical_center_client_id=str(
                access_ticket_obj.doctor_mcenters.medical_center.client_id
            ) if access_ticket_obj else medical_center_client_id,
            advance_user_payment_cliend_ides=advance_user_payment_client_ides,
            advance_amount=used_advance_amount,
            payment_date=new_user_payment_obj.payment_date.strftime("%Y-%m-%d")
        )

        # Вызываем процедуру Оракула создания услуг
        user_service_cart_client_ides = ''
        for item in user_services_for_oracle_list:
            data_for_oracle = [value for key, value in item[0].__dict__.items()]
            oracle_result = await call_oracle_proc(data_for_oracle, ORACLE_PROC_CREATE_PATIENT_SERVICE)
            if oracle_result[0] != 200:
                await s.rollback()
                return RequestResult(
                    status_code=oracle_result[0],
                    details="The process is temporary anavailable.",
                    details_ru=f"{oracle_result[1]}, {oracle_result[2]}"
                )
            else:
                oracle_check_data = xmltodict.parse(oracle_result[2].lower())
                user_service_cart_client_id =  oracle_check_data['data']['client_id']
                item[1].client_id = int(user_service_cart_client_id)
                s.add(item[1])
                await s.flush()
                user_service_cart_client_ides += f',{user_service_cart_client_id}'
        user_payment_for_oracle.user_service_cart_client_ides = user_service_cart_client_ides[1:]

        # Вызываем процедуру Оракла создания отложенного платежа
        data_for_oracle = [value for key, value in user_payment_for_oracle.__dict__.items()]
        oracle_result = await call_oracle_proc(data_for_oracle, ORACLE_PROC_CREATE_PAYMENT_FOR_PATSERV)

        if oracle_result[0] != 200:
            await s.rollback()
            return RequestResult(
                status_code=oracle_result[0],
                details="The process is temporary anavailable.",
                details_ru=f"{oracle_result[1]}, {oracle_result[2]}"
            )
        else:
            oracle_check_data = xmltodict.parse(oracle_result[2].lower())
            try:
                if isinstance(oracle_check_data['data']['users_purchases']['row'], list):
                    user_purchases_dict = dict([(int(x['users_services_carts.client_id']), int(x['client_id'])) for x in oracle_check_data['data']['users_purchases']['row']])
                elif isinstance(oracle_check_data['data']['users_purchases']['row'], dict):
                    user_purchases_dict = dict(
                        [(int(oracle_check_data['data']['users_purchases']['row']['users_services_carts.client_id']),
                        int(oracle_check_data['data']['users_purchases']['row']['client_id'])
                        )]
                    )
                else:
                    await s.rollback()
                    return RequestResult(
                        status_code=500,
                        details="The format of the Oracle answer has been changed",
                        details_ru="Изменился формат ответа Оракула"
                    )
            except Exception as e:
                await s.rollback()
                return RequestResult(
                    status_code=500,
                    details=f"e<{e}> The format of the Oracle answer has been changed",
                    details_ru=f"e<{e}> Изменился формат ответа Оракула"
                )
            if oracle_check_data['data']['used_advances']:
                try:
                    if isinstance(oracle_check_data['data']['used_advances']['row'], list):
                        user_used_advances_list = oracle_check_data['data']['used_advances']['row']
                    elif isinstance(oracle_check_data['data']['used_advances']['row'], dict):
                        user_used_advances_list = [oracle_check_data['data']['used_advances']['row']]
                    else:
                        await s.rollback()
                        return RequestResult(
                            status_code=500,
                            details="The format of the Oracle answer has been changed",
                            details_ru="Изменился формат ответа Оракула"
                        )
                except Exception as e:
                    await s.rollback()
                    return RequestResult(
                        status_code=500,
                        details=f"e<{e}> The format of the Oracle answer has been changed",
                        details_ru=f"e<{e}> Изменился формат ответа Оракула"
                    )
                # Обрабатываем использованный аванс
                for item in user_used_advances_list:
                    payment_advance_id = (await s.execute(async_select(
                        UserPaymentTable.id
                    ).filter(
                        UserPaymentTable.client_id == int(item['payment_advance_client_id'])
                    ))).scalar()
                    if not payment_advance_id:
                        return RequestResult(
                            status_code=500,
                            details="The answer of the Oracle isn't correct",
                            details_ru="Некорректный ответ Оракула: авансовый платеж отсутствует"
                        )
                    new_user_used_advance_obj = UserUsedAdvanceTable(
                        client_id=int(item['client_id']),
                        user_id=patient.id,
                        payment_spend_id=new_user_payment_obj.id,
                        payment_advance_id=payment_advance_id,
                        amount=float(item['amount'])
                    )
                    s.add(new_user_used_advance_obj)
                    await s.flush()

            for item in user_services_for_oracle_list:
                item[2].client_id = user_purchases_dict[item[1].client_id]
                s.add(item[2])
                await s.flush()

        new_user_payment_obj.client_id = int(oracle_check_data['data']['users_payments']['client_id'])
        # if payment_type_client_id == POSTPONED_ADVANCE:
        #     new_user_payment_obj.avance_amount = payment_amount
        # new_user_payment_obj.lpu_id = lpu_idss
        s.add(new_user_payment_obj)
        # await s.flush()

        await s.commit()

    return PaymentDataResult(
        data=PaynemtData(
            services_payment_list=services_payment_list,
            payment_info=payment_info
        ),
        status_code=200,
        details_ru='Ок',
        details='Ok'
    )


async def getting_unused_advances_sum(patient, lpu_id):

    selected_filter = []

    if lpu_id:
        selected_filter.append(
            UserPaymentTable.lpu_id == lpu_id
        )

    async with get_session() as s:

        user_full_advances_sum = (await s.execute(async_select(
            UserPaymentTable.lpu_id,
            func.sum(UserPaymentTable.avance_amount)
        ).filter(
            UserPaymentTable.user_id == patient.id,
            UserPaymentTable.avance_amount != None,
            UserPaymentTable.avance_status == 0,
            UserPaymentTable.id.in_(async_select(
                PayKeeperPaymentDataTable.user_payment_id
            )),
            *selected_filter
        ).group_by(
            UserPaymentTable.lpu_id
        )
        )).all()

        unused_advances_sum_dict = dict(user_full_advances_sum)

        user_used_advances_sum = (await s.execute(async_select(
            UserPaymentTable.lpu_id,
            func.sum(UserUsedAdvanceTable.amount)
        ).outerjoin(
            UserUsedAdvanceTable,
            UserUsedAdvanceTable.payment_advance_id == UserPaymentTable.id
        ).filter(
            UserPaymentTable.user_id == patient.id,
            UserPaymentTable.avance_amount != None,
            UserPaymentTable.avance_status == 0,
            UserPaymentTable.id.in_(async_select(
                PayKeeperPaymentDataTable.user_payment_id
            )),
            UserUsedAdvanceTable.user_id == patient.id,
            *selected_filter
        ).group_by(
            UserPaymentTable.lpu_id
        )
        )).all()

        for item in user_used_advances_sum:
            unused_advances_sum_dict[item[0]] = unused_advances_sum_dict[item[0]] - item[1]

        result_list = []

        for key, value in unused_advances_sum_dict.items():
            if key:
                medical_center_objs = (await s.execute(async_select(
                    MedicalCenterTable
                ).filter(
                    MedicalCenterTable.lpu_id == key,
                ))).scalars().all()
                result_list.append(
                    McentersUnuseAdvancesSum(
                        medical_centers=medical_center_objs,
                        unused_advances_sum=value
                    )
                )

    return result_list


async def getting_services_by_suscribtion(
        user, patient, services_to_pay,
        medical_center_client_id
    ):

    today = datetime.today()

    # services_payment_list = []
    user_services_for_oracle_list = []

    async with get_session() as s:

        access_ticket_obj = None

        for service in services_to_pay:
            # Получаем абонемент
            user_subscribe = (await s.execute(async_select(
                UserSubscribeTable
            ).filter(
                UserSubscribeTable.id == service.subscribe_id
            ))).scalars().one_or_none()
            if not user_subscribe:
                return RequestResult(
                    status_code=422,
                    details=f"The subscribe {service.subscribe_id} is absent",
                    details_ru=f"Абонемент {service.subscribe_id} не существует"
                )
            # Проверяем наличие прайса
            if not service.price_id:
                price_obj = (await s.execute(async_select(
                    PriceTable
                ).filter(
                    PriceTable.service_id == service.service_id,
                    and_(
                        PriceTable.price_period.has(PricePeriodTable.start_date <= today),
                        PriceTable.price_period.has(PricePeriodTable.end_date >= today)
                    ),
                    PriceTable.price_name_id == (async_select(
                        MedicalCenterPriceNameTable.price_name_id
                    ).filter(
                        MedicalCenterPriceNameTable.medical_center_id == service.medical_center_id
                    ))
                ))).scalars().one_or_none()
            else:
                price_obj = (await s.execute(async_select(PriceTable).filter(
                    PriceTable.id == service.price_id,
                    and_(
                        PriceTable.price_period.has(PricePeriodTable.start_date <= today),
                        PriceTable.price_period.has(PricePeriodTable.end_date >= today)
                    )
                ))).unique().scalars().one_or_none()

            # Создаем новую запись в корзине пользователя
            new_user_service_cart_obj = UserServiceCartTable(
                user_id=patient.id,
                service_id=service.service_id,
                medical_center_id=service.medical_center_id,
                price_id=price_obj.id,
                access_ticket_id=service.access_ticket_id,
                quantity=service.quantity,
                doctor_mcenter_id=service.doctor_mcenter_id
            )

            # Получаем полис пациента, шифр и максимальную скидку
            service_group_id_subquery = async_select(ServiceTable.service_group_id
            ).filter(
                ServiceTable.id == service.service_id
            ).scalar_subquery()

            shifr_discount_objs = (await s.execute(async_select(
                ShifrDiscountTable
            ).outerjoin(
                ServiceTable,
                ServiceTable.id == ShifrDiscountTable.service_id
            ).outerjoin(
                PolicyTable,
                PolicyTable.shifr_id == ShifrDiscountTable.shifr_id
            ).filter(
                ShifrDiscountTable.shifr_id == user_subscribe.policy.shifr_id,
                or_(
                    and_(
                        ShifrDiscountTable.service_id == service.service_id,
                        ShifrDiscountTable.service_group_id == None
                    ),
                    and_(
                        ShifrDiscountTable.service_group_id == service_group_id_subquery,
                        ShifrDiscountTable.service_id == None
                    )
                ),
                and_(
                    ShifrDiscountTable.shift_discount_period.has(ShifrDiscountPeriodTable.start_date <= today),
                    ShifrDiscountTable.shift_discount_period.has(ShifrDiscountPeriodTable.end_date >= today)
                )
            ).distinct(PolicyTable.shifr_id).order_by(PolicyTable.shifr_id))).unique().all()

            if shifr_discount_objs:
                max_discount_coefficient = min([x[0].discount_coefficient_a for x in shifr_discount_objs])
            else:
                max_discount_coefficient = 1

            new_user_service_cart_obj.policy_id = user_subscribe.policy.id
            new_user_service_cart_obj.shifr_id = user_subscribe.policy.shifr_id
            new_user_service_cart_obj.discount_coefficient = max_discount_coefficient

            # Валидируем номерок
            if service.access_ticket_id:
                if not access_ticket_obj:
                    access_ticket_obj = (await s.execute(async_select(AccessTicketTable).filter(
                        AccessTicketTable.id == service.access_ticket_id,
                        AccessTicketTable.user_id == patient.id
                    ))).unique().scalars().one_or_none()
                if access_ticket_obj:
                    new_user_service_cart_obj.start_date = access_ticket_obj.ticket_datetime
                    access_ticket_obj.bl_status = 2
                    s.add(access_ticket_obj)
                    await s.flush()
                else:
                    return RequestResult(
                        status_code=422,
                        details=f"The access ticket {service.access_ticket_id} didn't book for the patient {patient.id}",
                        details_ru=f"Номерок {service.access_ticket_id} не забронирован для пациента {patient.id}"
                    )
                if access_ticket_obj.doctor_mcenters.medical_center_id != service.medical_center_id:
                    return RequestResult(
                        status_code=422,
                        details=f"The access ticket {service.access_ticket_id} didn't correspond with medical center {service.medical_center_id}",
                        details_ru=f"Номерок {service.access_ticket_id} не соответствует медицинскому центру {service.medical_center_id}"
                    )

            # Валидируем услугу
            service_obj = (await s.execute(async_select(ServiceTable).filter(
                ServiceTable.id == service.service_id
            ))).unique().scalars().one_or_none()
            if service_obj:
                new_user_service_cart_obj.complex_service_id = service_obj.id if service_obj.is_complex_service else None
                new_user_service_cart_obj.complex_service_status = 1 if service_obj.is_complex_service else 0
                new_user_service_cart_obj.stac_satus = None
                new_user_service_cart_obj.cito_status = service_obj.is_urgent
                new_user_service_cart_obj.description = service_obj.full_description
                new_user_service_cart_obj.service_status = 0
            else:
                return RequestResult(
                    status_code=422,
                    details=f"The service {service.service_id} doesn't exist",
                    details_ru=f"Услуга {service.service_id} не существует"
                )
            if new_user_service_cart_obj.start_date:
                new_user_service_cart_obj.end_date = new_user_service_cart_obj.start_date + timedelta(
                    minutes=service_obj.execution_time
                )
            else:
                new_user_service_cart_obj.start_date = datetime.today()

            if price_obj:
                new_user_service_cart_obj.price_id = price_obj.id
                if new_user_service_cart_obj.discount_coefficient:
                    new_user_service_cart_obj.discount = price_obj.price_nal * (
                        1 - new_user_service_cart_obj.discount_coefficient
                    )
                else:
                    new_user_service_cart_obj.discount = 0
            else:
                return RequestResult(
                    status_code=422,
                    details=f"The price {service.price_id} doesn't exist",
                    details_ru=f"Прайс {service.price_id} не существует"
                )
            s.add(new_user_service_cart_obj)
            await s.flush()

            # Готовим список для создания услуг в МИС
            user_services_for_oracle = UserServicesForOracle()
            for key in user_services_for_oracle.__dict__.keys():
                value = getattr(new_user_service_cart_obj, key, None)
                if isinstance(value, datetime):
                    value = value.strftime("%Y-%m-%d")
                setattr(user_services_for_oracle, key, value)
            user_services_for_oracle.service_client_id = str(service_obj.client_id)
            user_services_for_oracle.user_client_id = str(patient.client_id)
            user_services_for_oracle.policy_client_id = str(user_subscribe.policy.client_id)
            user_services_for_oracle.medical_center_client_id = str(
                access_ticket_obj.doctor_mcenters.medical_center.client_id
            ) if access_ticket_obj else medical_center_client_id
            user_services_for_oracle.price_client_id = str(price_obj.client_id)
            user_services_for_oracle.shifr_client_id = str(user_subscribe.policy.shifr.client_id)
            user_services_for_oracle.access_ticket_client_id = str(
                access_ticket_obj.client_id
            ) if access_ticket_obj else None
            user_services_for_oracle.doctor_mcenter_client_id = str(
                access_ticket_obj.doctor_mcenters.client_id
            ) if access_ticket_obj else None
            if service_obj.is_urgent:
                user_services_for_oracle.cito_status = 1
            else:
                user_services_for_oracle.cito_status = 0
            if new_user_service_cart_obj.stac_satus:
                user_services_for_oracle.stac_satus = None
            else:
                user_services_for_oracle.stac_satus = None
            user_services_for_oracle.description = ''
            user_services_for_oracle_list.append(
                (user_services_for_oracle, new_user_service_cart_obj, None)
            )

        # Вызываем процедуру Оракула создания услуг
        for item in user_services_for_oracle_list:
            data_for_oracle = [value for key, value in item[0].__dict__.items()]
            oracle_result = await call_oracle_proc(
                data_for_oracle, ORACLE_PROC_CREATE_PATIENT_SERVICE
            )
            if oracle_result[0] != 200:
                await s.rollback()
                return RequestResult(
                    status_code=oracle_result[0],
                    details="The process is temporary anavailable.",
                    details_ru=f"{oracle_result[1]}, {oracle_result[2]}"
                )
            else:
                oracle_check_data = xmltodict.parse(oracle_result[2].lower())
                user_service_cart_client_id =  oracle_check_data['data']['client_id']
                item[1].client_id = int(user_service_cart_client_id)
                s.add(item[1])
                await s.flush()

        await s.commit()

    return RequestResult(
        status_code=200,
        details_ru='Ок',
        details='Ok'
    )


async def payment_recovery(payment_id):

    user_services_for_oracle_list = []

    async with get_session() as s:

        # Получаем список Carts
        services_cart_list = (await s.execute(async_select(
            UserServiceCartTable
        ).filter(
            UserServiceCartTable.user_purchase.has(
                UserPurchaseTable.user_payment_id == payment_id
            )
        ))).unique().scalars().all()

        if not services_cart_list:
            return PaymentDataResult(
                status_code=422,
                details_ru=f'Для платежа {payment_id} в корзиине нет услуг',
                details=f"The payment {payment_id} doesn't have any services in the cart"
            )

        # Готовим список для создания услуг в МИС
        for item in services_cart_list:
            user_services_for_oracle = UserServicesForOracle()
            for key in user_services_for_oracle.__dict__.keys():
                value = getattr(item, key, None)
                if isinstance(value, datetime):
                    value = value.strftime("%Y-%m-%d")
                setattr(user_services_for_oracle, key, value)
            user_services_for_oracle.service_client_id = str(item.service.client_id)
            user_services_for_oracle.user_client_id = str(item.user.client_id)
            user_services_for_oracle.policy_client_id = str(item.policy.client_id)
            user_services_for_oracle.medical_center_client_id = str(
                item.access_ticket.doctor_mcenters.medical_center.client_id
            ) if item.access_ticket else None
            user_services_for_oracle.price_client_id = str(item.price.client_id)
            user_services_for_oracle.shifr_client_id = str(item.policy.shifr.client_id)
            user_services_for_oracle.access_ticket_client_id = str(
                item.access_ticket.client_id
            ) if item.access_ticket else None
            user_services_for_oracle.doctor_mcenter_client_id = str(
                item.access_ticket.doctor_mcenters.client_id
            ) if item.access_ticket else None
            if item.service.is_urgent:
                user_services_for_oracle.cito_status = 1
            else:
                user_services_for_oracle.cito_status = 0
            if item.stac_satus:
                user_services_for_oracle.stac_satus = None
            else:
                user_services_for_oracle.stac_satus = None
            user_services_for_oracle.description = ''
            user_services_for_oracle_list.append(
                (user_services_for_oracle, item, item.user_purchase)
            )

        user_payment_for_oracle = UserPaymentForOracle(
            patient_client_id=str(services_cart_list[0].user.client_id),
            policy_client_id=str(services_cart_list[0].policy.client_id),
            shifr_client_id=str(services_cart_list[0].policy.shifr.client_id),
            payment_type_client_id=services_cart_list[0].user_purchase.user_payment.payment_type.client_id,
            medical_center_client_id=str(
                services_cart_list[0].access_ticket.doctor_mcenters.medical_center.client_id
            ) if services_cart_list[0].access_ticket else None,
            advance_user_payment_cliend_ides=None,
            advance_amount=None,
            payment_date=services_cart_list[0].user_purchase.user_payment.payment_date.strftime("%Y-%m-%d")
        )

        # Вызываем процедуру Оракула создания услуг
        user_service_cart_client_ides = ''
        for item in user_services_for_oracle_list:
            data_for_oracle = [value for key, value in item[0].__dict__.items()]
            oracle_result = await call_oracle_proc(data_for_oracle, ORACLE_PROC_CREATE_PATIENT_SERVICE)
            if oracle_result[0] != 200:
                return RequestResult(
                    status_code=oracle_result[0],
                    details="The process is temporary anavailable.",
                    details_ru=f"{oracle_result[1]}, {oracle_result[2]}"
                )
            else:
                oracle_check_data = xmltodict.parse(oracle_result[2].lower())
                user_service_cart_client_id =  oracle_check_data['data']['client_id']
                item[1].client_id = int(user_service_cart_client_id)
                s.add(item[1])
                await s.flush()
                user_service_cart_client_ides += f',{user_service_cart_client_id}'
        user_payment_for_oracle.user_service_cart_client_ides = user_service_cart_client_ides[1:]

        # Вызываем процедуру Оракла создания отложенного платежа
        data_for_oracle = [value for key, value in user_payment_for_oracle.__dict__.items()]
        oracle_result = await call_oracle_proc(data_for_oracle, ORACLE_PROC_CREATE_PAYMENT_FOR_PATSERV)

        if oracle_result[0] != 200:
            await s.rollback()
            return RequestResult(
                status_code=oracle_result[0],
                details="The process is temporary anavailable.",
                details_ru=f"{oracle_result[1]}, {oracle_result[2]}"
            )
        else:
            oracle_check_data = xmltodict.parse(oracle_result[2].lower())
            try:
                if isinstance(oracle_check_data['data']['users_purchases']['row'], list):
                    user_purchases_dict = dict([(int(x['users_services_carts.client_id']), int(x['client_id'])) for x in oracle_check_data['data']['users_purchases']['row']])
                elif isinstance(oracle_check_data['data']['users_purchases']['row'], dict):
                    user_purchases_dict = dict(
                        [(int(oracle_check_data['data']['users_purchases']['row']['users_services_carts.client_id']),
                        int(oracle_check_data['data']['users_purchases']['row']['client_id'])
                        )]
                    )
                else:
                    await s.rollback()
                    return RequestResult(
                        status_code=500,
                        details="The format of the Oracle answer has been changed",
                        details_ru="Изменился формат ответа Оракула"
                    )
            except Exception as e:
                await s.rollback()
                return RequestResult(
                    status_code=500,
                    details=f"e<{e}> The format of the Oracle answer has been changed",
                    details_ru=f"e<{e}> Изменился формат ответа Оракула"
                )

            for item in user_services_for_oracle_list:
                item[2].client_id = user_purchases_dict[item[1].client_id]
                s.add(item[2])
                await s.flush()

        services_cart_list[0].user_purchase.user_payment.client_id = int(oracle_check_data['data']['users_payments']['client_id'])
        s.add(services_cart_list[0].user_purchase.user_payment)
        await s.flush()

        await s.commit()

    return PaymentDataResult(
        status_code=200,
        details_ru='Ок',
        details='Ok'
    )


async def getting_services_with_current_debt(info, user,
                                             medical_center_ids=None,
                                             patient_ids=None,
                                             payment_ids=None
                                            ):
    medical_center_select_filter = []
    patient_select_filter = []
    payment_select_filter = []

    if medical_center_ids:
        medical_center_select_filter.append(
            UserServiceCartTable.medical_center_id.in_(medical_center_ids)
        )
    if patient_ids:
        patient_select_filter.append(
            UserServiceCartTable.user_id.in_(patient_ids)
        )
    if payment_ids:
        patient_select_filter.append(
            UserPaymentTable.id.in_(payment_ids)
        )

    async with get_session() as s:

        # Получаем список Carts
        services_cart_list = (await s.execute(async_select(
            UserServiceCartTable,
            UserPurchaseTable.amount,
            UserPaymentTable.id
        ).outerjoin(
            UserPurchaseTable,
            UserPurchaseTable.id == UserServiceCartTable.user_purchase_id
        ).outerjoin(
            UserPaymentTable,
            UserPaymentTable.id == UserPurchaseTable.user_payment_id
        ).outerjoin(
            PayKeeperPaymentDataTable,
            PayKeeperPaymentDataTable.user_payment_id == UserPaymentTable.id
        ).filter(
            PayKeeperPaymentDataTable.user_payment_id == None,
            UserServiceCartTable.service_status == 1,
            UserServiceCartTable.user_purchase_id != None,
            UserServiceCartTable.service.has(
                ServiceTable.client_service_code != ADVANCE_PAYMENT_SERVICE_CLIENT_SERVICE_CODE
            ),
            UserServiceCartTable.service.has(
                ServiceTable.client_service_code != SUBSCRIBE_PAYMENT_SERVICE_CLIENT_SERVICE_CODE
            ),
            *medical_center_select_filter,
            *patient_select_filter,
            *payment_select_filter
        )
        )).unique().all()

    result_list = []
    for item in services_cart_list:
        result_list.append(
            ServiceCurrentDebt(
               user=item[0].user,
               medical_center=item[0].medical_center,
               service_in_cart=item[0],
               debt=item[1]*item[0].quantity,
               payment_id=item[2]
            )
        )

    return result_list


async def getting_current_debt(info, user,
                               medical_center_ids=None,
                               patient_ids=None
                              ):

    # data_for_oracle = [str(user.client_id)]
    # oracle_result = await call_oracle_proc(data_for_oracle, ORACLE_PROC_GET_PATIENT_DEBT)
    # print(oracle_result)
    # # 1/0
    # if oracle_result[0] != 200:
    #     return RequestResult(
    #         status_code=oracle_result[0],
    #         details="The process is temporary anavailable.",
    #         details_ru=f"{oracle_result[1]}, {oracle_result[2]}"
    #     )
    # else:
    #     oracle_check_data = xmltodict.parse(oracle_result[2].lower())
    #     print(oracle_check_data)
    #     1/0
    #     user_service_cart_client_id =  oracle_check_data['data']['client_id']

    medical_center_select_filter = []
    patient_select_filter = []

    if medical_center_ids:
        medical_center_select_filter.append(
            UserServiceCartTable.medical_center_id.in_(medical_center_ids)
        )
    if patient_ids:
        patient_select_filter.append(
            UserServiceCartTable.user_id.in_(patient_ids)
        )

    async with get_session() as s:

        # Получаем список Carts
        user_debt_list = (await s.execute(async_select(
            UserServiceCartTable.medical_center_id,
            UserPurchaseTable.user_id,
            func.sum(UserPurchaseTable.amount*UserPurchaseTable.service_quantity)
        ).outerjoin(
            UserPurchaseTable,
            UserPurchaseTable.id == UserServiceCartTable.user_purchase_id
        ).outerjoin(
            UserPaymentTable,
            UserPaymentTable.id == UserPurchaseTable.user_payment_id
        ).outerjoin(
            PayKeeperPaymentDataTable,
            PayKeeperPaymentDataTable.user_payment_id == UserPaymentTable.id
        ).filter(
            PayKeeperPaymentDataTable.user_payment_id == None,
            UserServiceCartTable.service_status == 1,
            UserServiceCartTable.service.has(
                ServiceTable.client_service_code != ADVANCE_PAYMENT_SERVICE_CLIENT_SERVICE_CODE
            ),
            UserServiceCartTable.service.has(
                ServiceTable.client_service_code != SUBSCRIBE_PAYMENT_SERVICE_CLIENT_SERVICE_CODE
            ),
            UserPurchaseTable.user_id != None,
            *medical_center_select_filter,
            *patient_select_filter
        ).group_by(
            UserServiceCartTable.medical_center_id,
            UserPurchaseTable.user_id
        ).order_by(
            UserServiceCartTable.medical_center_id
        ))).unique().all()

        # Получаем абонементы пациентов
        patients_suscribes = (await s.execute(async_select(
            UserSubscribeTable.policy_id,
            PolicyTable
        ).outerjoin(
            PolicyTable,
            PolicyTable.id == UserSubscribeTable.policy_id
        ).filter(
            UserSubscribeTable.policy.has(PolicyTable.user_id.in_(patient_ids))
        ))).unique().all()

        #Получаем суммы задолженности по абонементу
        subscribe_debt_sum = await getting_subscribes_users_debt_sum(
            list(set([x[1].user_id for x in patients_suscribes])),
            list(set([x[0] for x in patients_suscribes])))
        subscribe_debt_sum_dict = {}
        for item in subscribe_debt_sum:
            try:
                subscribe_debt_sum_dict[item[0]] += item[1]
            except Exception:
                subscribe_debt_sum_dict[item[0]] = item[1]

        result_list = []
        services_debt_list = []
        services_debt_dict = {}
        result_medical_center = None
        medical_center_id = None

        sum_services_debt = 0
        for item in user_debt_list:
            if not result_medical_center or item[0] != medical_center_id:
                result_medical_center = (await s.execute(async_select(
                    MedicalCenterTable
                ).filter(
                    MedicalCenterTable.id == item[0]
                ))).scalars().one_or_none()
                medical_center_id = result_medical_center.id
                sum_services_debt = 0
            try:
                services_debt_dict[item[1]].append((result_medical_center, item[2]))
            except Exception:
                services_debt_dict[item[1]] = [(result_medical_center, item[2])]

        all_keys = list(set(list(subscribe_debt_sum_dict.keys()) + list(services_debt_dict.keys())))

        for user_id in all_keys:
            user = (await s.execute(async_select(
                UserTable
            ).filter(
                UserTable.id == user_id
            ))).scalars().one_or_none()
            try:
                services_debt_list = []
                sum_services_debt = 0
                for item in services_debt_dict[user_id]:
                    services_debt_list.append(
                        ServicesDebt(
                            services_medical_center=item[0],
                            services_debt=item[1]
                        )
                    )
                    sum_services_debt += item[1]
            except Exception:
                services_debt_list = None
            try:
                subscribe_debt=subscribe_debt_sum_dict[user_id]
            except Exception:
                subscribe_debt = None
            try:
                subscribe_debt_sum_dict = subscribe_debt_sum_dict[user_id]
                sum_debt = sum_services_debt + subscribe_debt_sum_dict
            except Exception:
                sum_debt = sum_services_debt
            result_list.append(
                CurrentDebt(
                    user=user,
                    services_debt_list=services_debt_list,
                    sum_services_debt=sum_services_debt,
                    subscribe_debt=subscribe_debt,
                    sum_debt=sum_debt
                )
            )

    return result_list


async def getting_payments_history(
            info, user,
            start_date,
            end_date,
            patient_ids=None
        ):

    patient_select_filter = []

    if patient_ids:
        patient_select_filter.append(
            UserPurchaseTable.user_id.in_(patient_ids)
        )

    async with get_session() as s:

        # user_purchases_list = (await s.execute(async_select(
        #     UserPurchaseTable
        # ).outerjoin(
        #     PayKeeperPaymentDataTable,
        #     PayKeeperPaymentDataTable.user_payment_id == UserPurchaseTable.user_payment_id
        # ).filter(
        #     UserPurchaseTable.user_payment.has(
        #         UserPaymentTable.payment_date >= start_date
        #     ),
        #     UserPurchaseTable.user_payment.has(
        #         UserPaymentTable.payment_date <= end_date
        #     ),
        #     PayKeeperPaymentDataTable.user_payment_id == UserPaymentTable.id,
        #     *patient_select_filter
        # ).order_by(UserPaymentTable.payment_date)
        # )).unique().scalars().all()

        user_purchases_list = (await s.execute(async_select(
            UserPaymentTable,
            UserPurchaseTable
        ).outerjoin(
            UserPurchaseTable,
            UserPurchaseTable.user_payment_id == UserPaymentTable.id
        ).outerjoin(
            PayKeeperPaymentDataTable,
            PayKeeperPaymentDataTable.user_payment_id == UserPaymentTable.id
        ).filter(
            UserPaymentTable.payment_date >= start_date,
            UserPaymentTable.payment_date <= end_date,
            PayKeeperPaymentDataTable.user_payment_id == UserPaymentTable.id,
            *patient_select_filter
        ).order_by(UserPaymentTable.payment_date.desc())
        )).unique().all()

        result_list = []
        for item in user_purchases_list:
            if item[0].payment_type.client_id in (24001, 24002, 24003, 24004):
                payment_type = 'Наличные'
            elif item[0].payment_type.client_id in (85232000, 85233000, 85324000,
                                                 85235000, 85236000, 85237000):
                payment_type = 'Карта'
            elif item[0].payment_type.client_id in (89303692, 89303693, 89303694,
                                                 89303695):
                payment_type = 'Безналичная оплата'
            else:
                payment_type = ''
            result_list.append(
                PaymentsWithServices(
                    payment_date=item[0].payment_date,
                    payment_id=item[0].id,
                    user_id=item[0].user_id,
                    payment_type=payment_type,
                    service=item[1].service,
                    amount=item[0].amount
                )
            )

    return result_list


async def getting_returned_payment_mrssage(user, user_service_cart_client_id):

    # Получаем айдишники всех родственников
    relatives_ids = await getting_relatives_ids(user.id)
    relatives_ids.append(user.id)

    async with get_session() as s:

        # Получаем запись user_service_cart
        user_service_cart_obj = (await s.execute(async_select(
            UserServiceCartTable.user_id,
            UserPurchaseTable.id,
            UserPaymentTable.id
        ).outerjoin(
            UserPurchaseTable,
            UserPurchaseTable.id == UserServiceCartTable.user_purchase_id
        ).outerjoin(
            UserPaymentTable,
            UserPaymentTable.id == UserPurchaseTable.user_payment_id
        ).filter(
            UserServiceCartTable.client_id == int(user_service_cart_client_id),
            UserServiceCartTable.service_status != 1
        ))).unique().one_or_none()

        if not user_service_cart_obj:
            return RequestResult(
                status_code = 422,
                details=f"The service {user_service_cart_client_id} doesn't exist \
                          or it has been done. It can't be canceled.",
                details_ru=f"Услуга {user_service_cart_client_id} не существует или \
                             уже выполнена и не может быть отменена."
            )

        if user_service_cart_obj[0] not in relatives_ids:
            return RequestResult(
                status_code = 422,
                details=f"You can't cancel the service {user_service_cart_client_id} \
                          because the user {user_service_cart_obj[0]} isn't your \
                          relative",
                details_ru=f"ВЫ не можете отменить услугу {user_service_cart_client_id} \
                             потому что пациент {user_service_cart_obj[0]} не \
                             является вашим родственником."
            )

        # Получаем данные об оплате услуги
        pay_keeper_obj = (await s.execute(async_select(
            PayKeeperPaymentDataTable.id
        ).filter(
            PayKeeperPaymentDataTable.user_payment_id == user_service_cart_obj[2]
        ))).unique().scalars().one_or_none()

        if not pay_keeper_obj:
            return RequestResult(
                status_code = 422,
                details=f"The services {user_service_cart_client_id} is not \
                          paid. You can canceling it inside LK",
                details_ru=f"Услуга {user_service_cart_client_id} \
                             не оплачена. Вы ее можете перенести или отменить в ЛК."
            )

    # Вызываем процедуру Ораклу для отправки сообщения по эл. почте
    data_for_oracle = [user_service_cart_client_id]
    print(data_for_oracle)
    oracle_set_result = await call_oracle_proc(
        data_for_oracle,
        ORACLE_PROC_CREATE_EMAIL_PAYSERV_INFO
    )

    if oracle_set_result[0] != 200:
        return RequestResult(
            status_code=422,
            details=f"Can't processing the service {user_service_cart_client_id} \
                        from Oracle",
            details_ru=f"Не могу обработать услугу \
                            {user_service_cart_client_id}"
        )
    else:
        return RequestResult(
            status_code=200,
            details=f'To refund of the service {user_service_cart_client_id} contact \
                      to medical center, please',
            details_ru=f"""Для возврата оплаты за услугу {user_service_cart_client_id} \
                           обратитесь, пожалуйста, в регистратуру медицинского центра"""
        )


async def creating_user_service_cart_for_getting_doc_without_pay(
    patient, service_obj, medical_center_obj, doc_params
):

    async with get_session() as s:

        new_user_service_cart_obj = UserServiceCartTable(
            service_id=service_obj.id,
            user_id=patient.id,
            medical_center_id=medical_center_obj.id,
            start_date=datetime.now(),
            quantity=1
        )
        s.add(new_user_service_cart_obj)
        await s.flush()

        # Готовим услугу для создания в МИС
        user_services_for_oracle = UserServicesForOracle()
        for key in user_services_for_oracle.__dict__.keys():
            value = getattr(new_user_service_cart_obj, key, None)
            if isinstance(value, datetime):
                value = value.strftime("%Y-%m-%d")
            setattr(user_services_for_oracle, key, value)
        user_services_for_oracle.service_client_id = str(service_obj.client_id)
        user_services_for_oracle.user_client_id = str(patient.client_id)
        user_services_for_oracle.policy_client_id = None
        user_services_for_oracle.medical_center_client_id = medical_center_obj.client_id
        user_services_for_oracle.price_client_id = None
        user_services_for_oracle.shifr_client_id = None
        user_services_for_oracle.access_ticket_client_id = None
        user_services_for_oracle.doctor_mcenter_client_id = None
        if service_obj.is_urgent:
            user_services_for_oracle.cito_status = 1
        else:
            user_services_for_oracle.cito_status = 0
        if new_user_service_cart_obj.stac_satus:
            user_services_for_oracle.stac_satus = None
        else:
            user_services_for_oracle.stac_satus = None
        user_services_for_oracle.description = ''

        data_for_oracle = [value for key, value in user_services_for_oracle.__dict__.items()]
        oracle_result = await call_oracle_proc(data_for_oracle, ORACLE_PROC_CREATE_PATIENT_SERVICE)

        if oracle_result[0] != 200:
            await s.rollback()
            return RequestResult(
                status_code=oracle_result[0],
                details="The process is temporary anavailable.",
                details_ru=f"{oracle_result[1]}, {oracle_result[2]}"
            )
        else:
            oracle_check_data = xmltodict.parse(oracle_result[2].lower())
            new_user_service_cart_obj.client_id = int(oracle_check_data['data']['client_id'])
            s.add(new_user_service_cart_obj)
            await s.flush()
            new_user_doc_request = UserDocumentRequestTable(
                user_id=patient.id,
                doc_client_id=doc_params.doc_client_id,
                doc_params=doc_params.doc_params,
                user_service_cart_client_id=str(new_user_service_cart_obj.client_id)
            )
            s.add(new_user_doc_request)
            await s.commit()

    return RequestResult(
        status_code=200,
        details='Ok',
        details_ru='Ок'
    )


async def creating_record_for_request_paid_doc(
    patient_id, payment_id, doc_params
):
    try:
        async with get_session() as s:

            user_service_cart_client_ids = (await s.execute(async_select(
                UserServiceCartTable.client_id
            ).outerjoin(
                UserPurchaseTable,
                UserPurchaseTable.id == UserServiceCartTable.user_purchase_id
            ).filter(
                UserPurchaseTable.user_payment_id == payment_id
            ))).scalars().all()

            for item in user_service_cart_client_ids:
                new_user_doc_request = UserDocumentRequestTable(
                    user_id=patient_id,
                    doc_client_id=doc_params.doc_client_id,
                    doc_params=doc_params.doc_params,
                    user_service_cart_client_id=str(item),
                    payment_id=payment_id
                )
                s.add(new_user_doc_request)
                await s.flush()
            await s.commit()
            return RequestResult(
                status_code=200,
                details='Ok',
                details_ru='Ок'
            )
    except Exception as e:
        print(e)
        return RequestResult(
            status_code=500,
            details=f'Непредвиденная ошибка - {e}',
            details_ru=f'Непредвиденная ошибка - {e}'
        )

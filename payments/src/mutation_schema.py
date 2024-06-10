import strawberry
import hashlib
import json
import time
import datetime
from typing import List
from strawberry.types import Info
from kafka import KafkaProducer
from sqlalchemy.future import select as async_select
from sqlalchemy import and_, func, or_

from core.config.cache_connector import CacheConnector
from core.config.settings import (PAYKEEPER_CONFIRM_PAYMENT_TOPIC,
                                  SUBSCRIBE_PAYMENT_SERVICE_CLIENT_SERVICE_CODE,
                                  ADVANCE_PAYMENT_SERVICE_CLIENT_SERVICE_CODE)
from core.config.db import get_session
from core.authorization.auth import Auth
from core.authorization.permissions import IsAuthenticated, get_auth_user_by_auth_header
from core.config.scalars import (RequestResult, UserDefaultObjectIn, UserSubscribeIn,
                                 PayKeeperPaymentDataIn, UserPaymentIn, ServiceIn,
                                 PaymentTypeIn, UserPurchaseIn)
from core.sa_tables.main_process import (UserDefaultObjectTable, UserSubscribeTable,
                                         PayKeeperPaymentDataTable, ServiceTable,
                                         UserServiceCartTable, PriceTable, PricePeriodTable,
                                         MedicalCenterPriceNameTable)
from core.sa_tables.accounts import MedicalCenterTable
from core.src.common_resolvers import (getting_objs, service_subscribe_availability,
                                       getting_default_patient_by_user, remove_temporary_payment)
from payments.config.settings import (POSTPONED_PAYMENT, POSTPONED_ADVANCE,
                                      CONFIRMED_PAYMENT, INITPRO_PAYMENT_METHOD_ADVANCE,
                                      INITPRO_PAYMENT_METHOD_FULL_PAYMENT, INITPRO_PAYMENT_OBJECT_SERVICE,
                                      INITPRO_PAYMENTS_TYPE_FOR_ADVANCE, INITPRO_PAYMENTS_TYPE_FOR_OTHER,
                                      INITPRO_OPERATION_TYPE_SELL, INITPRO_PAYMENT_OBJECT_PAYMENT)
from .scalars import (UserServiceCartInputMut, UserServiceCartInputAdv, MedicalCenterInputPay,
                      UserServiceCartInputPay, ServicePaymentInfo, PaymentInfo, DocParams,
                      UserServiceCartInputDoc)
from .resolvers import (creating_user_payment_and_purchases, getting_unused_advances_sum,
                        getting_services_by_suscribtion, creating_user_service_cart_for_getting_doc_without_pay,
                        creating_record_for_request_paid_doc)
from .scripts import get_paykeeper_invoice
from .utils import create_temporary_payment_record, creating_receipt


hasher= hashlib.sha256
cache = CacheConnector()
auth = Auth()


@strawberry.type
class MutationPayments:

    @strawberry.field(permission_classes=[IsAuthenticated])
    async def put_services_to_pay(
        self,
        info:Info,
        services_to_pay: List[UserServiceCartInputMut],
    ) -> RequestResult:
        """
        Отправка списка услуг на оплату
        """

        start = time.time()

        producer = KafkaProducer(
            bootstrap_servers=['kafka:9092'],
            acks=1,
            linger_ms=40,
            value_serializer=lambda m: json.dumps(m).encode('ascii')
        )

        user, _ = await get_auth_user_by_auth_header(info)

        # Получаем пациента по умолчанию
        filtering_attrs = UserDefaultObjectIn(
            user_id=user.id
        )
        user_default_objs, _, _ = await getting_objs(info, user, UserDefaultObjectTable, filtering_attrs)
        if user_default_objs:
            patient = user_default_objs[0].default_patient
        else:
            patient = user

        # Получаем медицинский центр
        mcenter_filtering_attrs = MedicalCenterInputPay(
            id=services_to_pay[0].medical_center_id,
            show_in_lk=True
        )
        medical_center_objs, _, _ = await getting_objs(info, user, MedicalCenterTable, mcenter_filtering_attrs)
        if not medical_center_objs:
            return RequestResult(
                status_code=422,
                details_ru=f'Медицинского центра с идентификатором {services_to_pay[0].medical_center_id} не существует',
                details=f"The medical center with nubber {services_to_pay[0].medical_center_id} doesn't exist"
            )

        payment_data_result = await creating_user_payment_and_purchases(
            user, patient, services_to_pay,
            POSTPONED_PAYMENT,
            medical_center_objs[0].lpu_id
        )

        if payment_data_result.status_code != 200:
            try:
                await remove_temporary_payment(
                    payment_data_result.data.payment_info.user_payment_id
                )
            except Exception as e:
                print(e)
            return payment_data_result

        invoice_result = await get_paykeeper_invoice(payment_data_result.data.services_payment_list,
                                                     payment_data_result.data.payment_info,
                                                     medical_center_objs[0].lpu.client_id)

        if not invoice_result:
            try:
                await remove_temporary_payment(
                    payment_data_result.data.payment_info.user_payment_id
                )
            except Exception as e:
                print(e)
            return RequestResult(
                status_code=422,
                details_ru='Нет соединения с платежной системой',
                details="The connect with the payment system is absent"
            )

        if invoice_result.status_code != 200:
            try:
                await remove_temporary_payment(
                    payment_data_result.data.payment_info.user_payment_id
                )
            except Exception as e:
                print(e)
            return invoice_result
        else:
            invoice_result_data = json.loads(invoice_result.data)
            payment_data_result.data.payment_info.invoice_id = invoice_result_data['invoice_id']
            try:
                producer.send(
                    PAYKEEPER_CONFIRM_PAYMENT_TOPIC,
                    {
                        'data': payment_data_result.data.payment_info.__dict__,
                        'lpu_client_id': medical_center_objs[0].lpu.client_id,
                        'payment_method': INITPRO_PAYMENT_METHOD_FULL_PAYMENT,
                        'payment_object': INITPRO_PAYMENT_OBJECT_SERVICE,
                        'payments_type': INITPRO_PAYMENTS_TYPE_FOR_OTHER,
                        'operation_type': INITPRO_OPERATION_TYPE_SELL
                    }
                )
            except Exception as e:
                print(e)
                try:
                    await remove_temporary_payment(
                        payment_data_result.data.payment_info.user_payment_id
                    )
                except Exception as ee:
                    print(ee)
                return RequestResult(status_code=500,
                                     details=f'Error - {e}.')

            result_record = await create_temporary_payment_record(
                payment_data_result.data.payment_info.user_payment_id
            )
            if result_record:
                result = RequestResult(
                    data=invoice_result_data['invoice_url'],
                    status_code=200,
                    details_ru='Ок',
                    details='Ok'
                )
            else:
                try:
                    await remove_temporary_payment(
                        payment_data_result.data.payment_info.user_payment_id
                    )
                except Exception as e:
                    print(e)
                result = RequestResult(status_code=500,
                                       details=f"Can't create thee temporary payment")

        end1 = time.time()
        print(f'Полное время на выполнение процедуры put_services_to_pay {(end1-start)*1000} мс')

        return result

    @strawberry.field(permission_classes=[IsAuthenticated])
    async def put_services_to_pay_by_advance(
        self,
        info:Info,
        services_to_pay: List[UserServiceCartInputMut]
    ) -> RequestResult:
        """
        Отправка списа услуг на оплату за счет аванса
        """

        start = time.time()

        # Получаем пациента по умолчанию
        user, _ = await get_auth_user_by_auth_header(info)
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

        # Получаем медицинский центр
        filtering_attrs = MedicalCenterInputPay(
            id=services_to_pay[0].medical_center_id,
            show_in_lk=True
        )
        medical_center_objs, _, _ = await getting_objs(
            info, user, MedicalCenterTable, filtering_attrs
        )
        if not medical_center_objs:
            return RequestResult(
                status_code=422,
                details_ru=f'Медицинского центра с идентификатором {services_to_pay[0].medical_center_id} не существует',
                details=f"The medical center with number {services_to_pay[0].medical_center_id} doesn't exist"
            )

        patient_unused_advances_sum = await getting_unused_advances_sum(
            patient, medical_center_objs[0].lpu_id
        )

        try:
            unused_advances_sum = patient_unused_advances_sum[0].unused_advances_sum
        except Exception as e:
            print(e)
            unused_advances_sum = 0

        if unused_advances_sum:
            payment_data_result = await creating_user_payment_and_purchases(
                user, patient, services_to_pay, CONFIRMED_PAYMENT, medical_center_objs[0].lpu_id,
                patient_unused_advances_sum=unused_advances_sum
            )
            if payment_data_result.status_code == 200:

                result_receipt = await creating_receipt(payment_data_result.data.payment_info.user_payment_id,
                                                        INITPRO_PAYMENT_METHOD_FULL_PAYMENT,
                                                        INITPRO_PAYMENT_OBJECT_SERVICE,
                                                        INITPRO_PAYMENTS_TYPE_FOR_ADVANCE,
                                                        medical_center_objs[0].lpu.client_id,
                                                        INITPRO_OPERATION_TYPE_SELL)
                if not result_receipt:
                    print('Сбой процедуры регистрации чека')
                    # TO DO Направить уведомление в аварийный топик 
                    # или записать в базу номер платежа для последующей отправки чека

                payment_data_result.data = None
        else:
            payment_data_result = RequestResult(
                status_code=422,
                details="The paitient doesn't have any advances",
                details_ru="Пациент не имеет никаких авансов"
            )

        end1 = time.time()
        print(f'Полное время на выполнение процедуры put_services_to_pay {(end1-start)*1000} мс')

        return payment_data_result

    @strawberry.field(permission_classes=[IsAuthenticated])
    async def put_advance_to_pay(
        self,
        info:Info,
        advance_amount: int,
        medical_center_id: int
    ) -> RequestResult:
        """
        Отправка аванса на оплату
        """

        start = time.time()

        producer = KafkaProducer(
            bootstrap_servers=['kafka:9092'],
            acks=1,
            linger_ms=40,
            value_serializer=lambda m: json.dumps(m).encode('ascii')
        )

        #Получаем пациента по умолчанию
        user, _ = await get_auth_user_by_auth_header(info)

        patients_filtering_attrs = UserDefaultObjectIn(
            user_id=user.id
        )
        user_default_objs, _, _ = await getting_objs(info, user, UserDefaultObjectTable, patients_filtering_attrs)
        if user_default_objs:
            patient = user_default_objs[0].default_patient
        else:
            patient = user

        # Получаем медицинский центр
        mc_filtering_attrs = MedicalCenterInputPay(
            id=medical_center_id,
            show_in_lk=True
        )
        medical_center_objs, _, _ = await getting_objs(info, user, MedicalCenterTable, mc_filtering_attrs)
        if not medical_center_objs:
            return RequestResult(
                status_code=422,
                details_ru=f'Медицинского центра с идентификатором {medical_center_id} не существует',
                details=f"The medical center with nubber {medical_center_id} doesn't exist"
            )

        # Получаем услугу оплаты аванса
        service_filtering_attrs = ServiceIn(
            client_service_code=ADVANCE_PAYMENT_SERVICE_CLIENT_SERVICE_CODE
        )
        service_objs, _, _ = await getting_objs(info, user, ServiceTable, service_filtering_attrs)
        if not service_objs:
            return RequestResult(
                status_code=422,
                details_ru=f'Услуги с параметром client_service_code {ADVANCE_PAYMENT_SERVICE_CLIENT_SERVICE_CODE} не существует',
                details=f"The service with the parameter 'client_service_code' {ADVANCE_PAYMENT_SERVICE_CLIENT_SERVICE_CODE} doesn't exist"
            )

        # Формируем услугу
        services_to_pay = [UserServiceCartInputAdv(
            service_id=service_objs[0].id,
            medical_center_id=medical_center_id,
            quantity=advance_amount
        ),]

        payment_data_result = await creating_user_payment_and_purchases(
            user, patient, services_to_pay,
            POSTPONED_ADVANCE,
            medical_center_objs[0].lpu_id,
            medical_center_client_id=medical_center_objs[0].client_id
        )

        if payment_data_result.status_code != 200:
            try:
                await remove_temporary_payment(
                    payment_data_result.data.payment_info.user_payment_id
                )
            except Exception as e:
                print(e)
            return payment_data_result

        invoice_result = await get_paykeeper_invoice(payment_data_result.data.services_payment_list,
                                                     payment_data_result.data.payment_info,
                                                     medical_center_objs[0].lpu.client_id)

        if invoice_result.status_code != 200:
            try:
                await remove_temporary_payment(
                    payment_data_result.data.payment_info.user_payment_id
                )
            except Exception as e:
                print(e)
            return invoice_result
        else:
            invoice_result_data = json.loads(invoice_result.data)
            payment_data_result.data.payment_info.invoice_id = invoice_result_data['invoice_id']
            try:
                producer.send(
                    PAYKEEPER_CONFIRM_PAYMENT_TOPIC,
                    {
                        'data': payment_data_result.data.payment_info.__dict__,
                        'lpu_client_id': medical_center_objs[0].lpu.client_id,
                        'payment_method': INITPRO_PAYMENT_METHOD_ADVANCE,
                        'payment_object': INITPRO_PAYMENT_OBJECT_PAYMENT,
                        'payments_type': INITPRO_PAYMENTS_TYPE_FOR_OTHER,
                        'operation_type': INITPRO_OPERATION_TYPE_SELL
                    }
                )
            except Exception as e:
                try:
                    await remove_temporary_payment(
                        payment_data_result.data.payment_info.user_payment_id
                    )
                except Exception as ee:
                    print(ee)
                print(e)
                return RequestResult(status_code=422,
                                    details='Operation is temporarily unavailable')

            result_record = await create_temporary_payment_record(
                payment_data_result.data.payment_info.user_payment_id
            )
            if result_record:
                result = RequestResult(
                    data=json.loads(invoice_result.data)['invoice_url'],
                    status_code=200,
                    details_ru='Ок',
                    details=invoice_result.details# 'Ok'
                )
            else:
                try:
                    await remove_temporary_payment(
                        payment_data_result.data.payment_info.user_payment_id
                    )
                except Exception as e:
                    print(e)
                result = RequestResult(status_code=500,
                                       details=f"Can't create thee temporary payment")

        end1 = time.time()
        print(f'Полное время на выполнение процедуры put_services_to_pay {(end1-start)*1000} мс')

        return result

    @strawberry.field(permission_classes=[IsAuthenticated])
    async def put_subscribe_to_pay(
        self,
        info:Info,
        user_subscribe_id: int,
        medical_center_id: int,
        amount: float
    ) -> RequestResult:
        """
        Оплата абонемента
        """

        start = time.time()

        today = datetime.datetime.today()

        producer = KafkaProducer(
            bootstrap_servers=['kafka:9092'],
            acks=1,
            linger_ms=40,
            value_serializer=lambda m: json.dumps(m).encode('ascii')
        )

        user, _ = await get_auth_user_by_auth_header(info)

        # Получаем пациента по умолчанию
        filtering_attrs = UserDefaultObjectIn(
            user_id=user.id
        )
        user_default_objs, _, _ = await getting_objs(
            info, user, UserDefaultObjectTable,
            filtering_attrs
        )
        if user_default_objs:
            patient = user_default_objs[0].default_patient
        else:
            patient = user

        # Получаем абонемент
        subscribe_filtering_attrs = UserSubscribeIn(
            id=user_subscribe_id
        )
        patient_subscribe, _, _ = await getting_objs(
            info, patient, UserSubscribeTable,
            subscribe_filtering_attrs
        )
        if not patient_subscribe:
            return RequestResult(
                status_code=422,
                details_ru=f'Абонемента с идентификатором {user_subscribe_id} не существует',
                details=f"The subscribtion with number {user_subscribe_id} doesn't exist"
            )

        # Получаем медицинский центр
        filtering_attrs = MedicalCenterInputPay(
            id=patient_subscribe[0].policy.medical_center_id,
            show_in_lk=True
        )
        medical_center_objs, _, _ = await getting_objs(
            info, user, MedicalCenterTable,
            filtering_attrs
        )
        if not medical_center_objs:
            filtering_attrs = MedicalCenterInputPay(
                id=medical_center_id,
                show_in_lk=True
            )
            medical_center_objs, _, _ = await getting_objs(
                info, user, MedicalCenterTable,
                filtering_attrs
            )
            if not medical_center_objs:
                return RequestResult(
                    status_code=422,
                    details_ru=f'Медицинского центра с идентификатором {medical_center_id} не существует',
                    details=f"The medical center with number {medical_center_id} doesn't exist"
                )

        # Получаем суммы оплат
        paykeeper_payment_data_filter_attrs = PayKeeperPaymentDataIn(
            user_payment=UserPaymentIn(
                user_id=patient.id,
                policy_id=patient_subscribe[0].policy.id
            )
        )
        subscribe_paykeeper_payments, _, _ = await getting_objs(
            info, patient, PayKeeperPaymentDataTable,
            paykeeper_payment_data_filter_attrs
        )
        subscribe_paid_sum = sum([x.pay_amount for x in subscribe_paykeeper_payments])
        subscribe_debt = patient_subscribe[0].policy.amount - subscribe_paid_sum
        if subscribe_debt <= 0:
            return RequestResult(
                status_code=422,
                details_ru=f'Абонемент с идентификатором {patient_subscribe[0].id} полностью оплачен',
                details=f"The subscription with number {patient_subscribe[0].id} has been paid fully"
            )
        elif amount > subscribe_debt:
            return RequestResult(
                status_code=422,
                details_ru=f'Сумма платежа {amount} больше имеющейся задолженности {subscribe_debt}',
                details=f"The payment sum {amount} is more than the debt {subscribe_debt}"
            )

        # Получаем услугу "Оплата абонемента"
        services_filtering_attrs = ServiceIn(
            client_service_code=SUBSCRIBE_PAYMENT_SERVICE_CLIENT_SERVICE_CODE
        )
        services_objs, _, _ = await getting_objs(
            info, patient, ServiceTable,
            services_filtering_attrs
        )
        if not services_objs:
            return RequestResult(
                status_code=422,
                details_ru=f'Услуга с client_service_code = 11.00 не существует',
                details=f"The service with client_service_code = 11.00 doesn't exist"
            )

        # Формируем услугу к оплате
        services_to_pay = [UserServiceCartInputAdv(
            service_id=services_objs[0].id,
            medical_center_id=medical_center_objs[0].id,
            quantity=amount,
            price_id=None
        )]

        payment_data_result = await creating_user_payment_and_purchases(
            user, patient, services_to_pay,
            POSTPONED_PAYMENT,
            medical_center_objs[0].lpu_id,
            medical_center_client_id=medical_center_objs[0].client_id,
            subscribe_amount_to_pay=amount,
            user_subscribe=patient_subscribe[0]
        )

        if payment_data_result.status_code != 200:
            try:
                await remove_temporary_payment(
                    payment_data_result.data.payment_info.user_payment_id
                )
            except Exception as e:
                print(e)
            return payment_data_result

        invoice_result = await get_paykeeper_invoice(payment_data_result.data.services_payment_list,
                                                     payment_data_result.data.payment_info,
                                                     medical_center_objs[0].lpu.client_id)

        if not invoice_result:
            try:
                await remove_temporary_payment(
                    payment_data_result.data.payment_info.user_payment_id
                )
            except Exception as e:
                print(e)
            return RequestResult(
                status_code=422,
                details_ru='Нет соединения с платежной системой',
                details="The connect with the payment system is absent"
            )

        if invoice_result.status_code != 200:
            try:
                await remove_temporary_payment(
                    payment_data_result.data.payment_info.user_payment_id
                )
            except Exception as e:
                print(e)
            return invoice_result
        else:
            invoice_result_data = json.loads(invoice_result.data)
            payment_data_result.data.payment_info.invoice_id = invoice_result_data['invoice_id']
            try:
                producer.send(
                    PAYKEEPER_CONFIRM_PAYMENT_TOPIC,
                    {
                        'data': payment_data_result.data.payment_info.__dict__,
                        'lpu_client_id': medical_center_objs[0].lpu.client_id,
                        'payment_method': INITPRO_PAYMENT_METHOD_FULL_PAYMENT,
                        'payment_object': INITPRO_PAYMENT_OBJECT_SERVICE,
                        'payments_type': INITPRO_PAYMENTS_TYPE_FOR_OTHER,
                        'operation_type': INITPRO_OPERATION_TYPE_SELL
                    }
                )
            except Exception as e:
                try:
                    await remove_temporary_payment(
                        payment_data_result.data.payment_info.user_payment_id
                    )
                except Exception as ee:
                    print(ee)
                print(e)
                return RequestResult(status_code=422,
                                     details='Operation is temporarily unavailable')

            result_record = await create_temporary_payment_record(
                payment_data_result.data.payment_info.user_payment_id
            )
            if result_record:
                result = RequestResult(
                    data=invoice_result_data['invoice_url'],
                    status_code=200,
                    details_ru='Ок',
                    details='Ok'
                )
            else:
                try:
                    await remove_temporary_payment(
                        payment_data_result.data.payment_info.user_payment_id
                    )
                except Exception as e:
                    print(e)
                result = RequestResult(status_code=500,
                                       details="Can't create thee temporary payment")

        end1 = time.time()
        print(f'Полное время на выполнение процедуры put_services_to_pay {(end1-start)*1000} мс')

        return result

    @strawberry.field(permission_classes=[IsAuthenticated])
    async def put_services_to_pay_by_suscribe(
        self,
        info:Info,
        services_to_pay: List[UserServiceCartInputMut]
    ) -> RequestResult:
        """
        Отправка списка услуг на оплату за счет абонемента
        """

        start = time.time()

        user, _ = await get_auth_user_by_auth_header(info)

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

        # Получаем медицинский центр
        filtering_attrs = MedicalCenterInputPay(
            id=services_to_pay[0].medical_center_id,
            show_in_lk=True
        )
        medical_center_objs, _, _ = await getting_objs(
            info, user, MedicalCenterTable, filtering_attrs
        )
        if not medical_center_objs:
            return RequestResult(
                status_code=422,
                details_ru=f'Медицинского центра с идентификатором {services_to_pay[0].medical_center_id} не существует',
                details=f"The medical center with nubber {services_to_pay[0].medical_center_id} doesn't exist"
            )

        # Проверяем услуги на достутность по абонементам
        services_to_pay_with_subscribe = []
        for item in services_to_pay:
            subscribe_result = await service_subscribe_availability(patient, item)
            if subscribe_result.status_code !=200:
                return subscribe_result
            else:
                services_to_pay_with_subscribe.append(subscribe_result.data)

        payment_data_result = await getting_services_by_suscribtion(
            user, patient, services_to_pay_with_subscribe, medical_center_objs[0].client_id
        )

        end1 = time.time()
        print(f'Полное время на выполнение процедуры put_services_to_pay {(end1-start)*1000} мс')

        return payment_data_result

    @strawberry.field(permission_classes=[IsAuthenticated])
    async def put_services_to_pay_in_mcenter(
        self,
        info:Info,
        services_to_pay: List[UserServiceCartInputMut],
    ) -> RequestResult:
        """
        Отправка списка услуг на создание с оплатой в медцентре (отложенный платеж)
        """

        start = time.time()

        user, _ = await get_auth_user_by_auth_header(info)

        # Получаем пациента по умолчанию
        patient = await getting_default_patient_by_user(info, user)

        # Получаем медицинский центр
        mcenter_filtering_attrs = MedicalCenterInputPay(
            id=services_to_pay[0].medical_center_id,
            show_in_lk=True
        )
        medical_center_objs, _, _ = await getting_objs(info, user, MedicalCenterTable, mcenter_filtering_attrs)
        if not medical_center_objs:
            return RequestResult(
                status_code=422,
                details_ru=f'Медицинского центра с идентификатором {services_to_pay[0].medical_center_id} не существует',
                details=f"The medical center with nubber {services_to_pay[0].medical_center_id} doesn't exist"
            )

        payment_data_result = await creating_user_payment_and_purchases(
            user, patient, services_to_pay,
            POSTPONED_PAYMENT,
            medical_center_objs[0].lpu_id
        )

        if payment_data_result.status_code == 200:
            payment_data_result.data = None

        end1 = time.time()
        print(f'Полное время на выполнение процедуры put_services_to_pay {(end1-start)*1000} мс')

        return payment_data_result

    @strawberry.field(permission_classes=[IsAuthenticated])
    async def put_postponed_payment_to_pay(
        self,
        info:Info,
        postponed_payment_id: int
    ) -> RequestResult:
        """
        Отправка отложенного платежа на оплату
        """

        start = time.time()

        producer = KafkaProducer(
            bootstrap_servers=['kafka:9092'],
            acks=1,
            linger_ms=40,
            value_serializer=lambda m: json.dumps(m).encode('ascii')
        )

        user, _ = await get_auth_user_by_auth_header(info)

        # Получаем пациента по умолчанию
        patient_filtering_attrs = UserDefaultObjectIn(
            user_id=user.id
        )
        user_default_objs, _, _ = await getting_objs(info, user, UserDefaultObjectTable, patient_filtering_attrs)
        if user_default_objs:
            patient = user_default_objs[0].default_patient
        else:
            patient = user

        # Валидируем отложенный платеж и получаем услуги
        user_cart_filtering_attrs = UserServiceCartInputPay(
            user_purchase=UserPurchaseIn(
                user_payment=UserPaymentIn(
                    id=postponed_payment_id,
                    user_id=patient.id,
                    payment_type=PaymentTypeIn(
                        client_id=int(POSTPONED_PAYMENT)
                    )
                )
            )
        )
        postponed_payments_list, _, _ = await getting_objs(
            info, patient, UserServiceCartTable,
            user_cart_filtering_attrs
        )
        if not postponed_payments_list:
            return RequestResult(
                status_code=422,
                details_ru=f'У пользователя {patient.id} отложенный платеж с номером {postponed_payment_id} отсутствует',
                details=f"The petient {patient.id} doesn't have the postponed payment {postponed_payment_id}"
            )

        # Формируем данные для оплаты
        services_payment_list = []
        pay_amount = 0
        for item in postponed_payments_list:
            full_sum = item.user_purchase.amount * item.quantity
            services_payment_list.append(
                ServicePaymentInfo(
                    name=item.service.name_for_lk,
                    price=item.user_purchase.amount,
                    quantity=item.quantity,
                    sum=full_sum,
                    tax=0
                )
            )
            pay_amount += full_sum

        payment_info = PaymentInfo(
            pay_amount= pay_amount,
            user_id=user.client_id,
            user_payment_id=postponed_payments_list[0].user_purchase.user_payment.id,
            user_email=user.email,
            user_phone_number=user.phone_number,
            invoice_id=''
        )

        invoice_result = await get_paykeeper_invoice(services_payment_list,
                                                     payment_info,
                                                     postponed_payments_list[0].user_purchase.user_payment.lpu.client_id)

        if not invoice_result:
            try:
                await remove_temporary_payment(
                    postponed_payments_list[0].user_purchase.user_payment.id
                )
            except Exception as e:
                print(e)
            return RequestResult(
                status_code=422,
                details_ru='Нет соединения с платежной системой',
                details="The connect thi the payment system is absent"
            )

        if invoice_result.status_code != 200:
            try:
                await remove_temporary_payment(
                    postponed_payments_list[0].user_purchase.user_payment.id
                )
            except Exception as e:
                print(e)
            return invoice_result
        else:
            invoice_result_data = json.loads(invoice_result.data)
            payment_info.invoice_id = invoice_result_data['invoice_id']
            try:
                producer.send(
                    PAYKEEPER_CONFIRM_PAYMENT_TOPIC,
                    {
                        'data': payment_info.__dict__,
                        'lpu_client_id': postponed_payments_list[0].user_purchase.user_payment.lpu.client_id,
                        'payment_method': INITPRO_PAYMENT_METHOD_FULL_PAYMENT,
                        'payment_object': INITPRO_PAYMENT_OBJECT_SERVICE,
                        'payments_type': INITPRO_PAYMENTS_TYPE_FOR_OTHER,
                        'operation_type': INITPRO_OPERATION_TYPE_SELL
                    }
                )
            except Exception as e:
                try:
                    await remove_temporary_payment(
                        postponed_payments_list[0].user_purchase.user_payment.id
                    )
                except Exception as ee:
                    print(ee)
                print(e)
                return RequestResult(status_code=422,
                                    details=f'Operation is temporarily unavailable')

            result_record = await create_temporary_payment_record(postponed_payments_list[0].user_purchase.user_payment.id)
            if result_record:
                result = RequestResult(
                    data=invoice_result_data['invoice_url'],
                    status_code=200,
                    details_ru='Ок',
                    details='Ok'
                )
            else:
                try:
                    await remove_temporary_payment(
                        postponed_payments_list[0].user_purchase.user_payment.id
                    )
                except Exception as e:
                    print(e)
                result = RequestResult(status_code=500,
                                       details=f"Can't create thee temporary payment")

        end1 = time.time()
        print(f'Полное время на выполнение процедуры put_services_to_pay {(end1-start)*1000} мс')

        return result

    @strawberry.field(permission_classes=[IsAuthenticated])
    async def request_available_document(
        self,
        info:Info,
        doc_params: DocParams,
        medical_center_id: int
        ) -> RequestResult:
        """
        Запрос на получение доступного документа
        """

        json.loads(doc_params.doc_params)

        start = time.time()

        today = datetime.datetime.today()

        user, _ = await get_auth_user_by_auth_header(info)

        producer = KafkaProducer(
            bootstrap_servers=['kafka:9092'],
            acks=1,
            linger_ms=40,
            value_serializer=lambda m: json.dumps(m).encode('ascii')
        )

        # Получаем пациента по умолчанию
        patient = await getting_default_patient_by_user(info, user)

        async with get_session() as s:

            # Получаем медицинский центр
            medical_center_obj = (await s.execute(async_select(
                MedicalCenterTable
            ).filter(
                MedicalCenterTable.id == medical_center_id
            ))).scalars().one_or_none()

            if not medical_center_obj:
                return RequestResult(
                    status_code=422,
                    details_ru=f'Медицинского центра с идентификатором {medical_center_id} не существует',
                    details=f"The medical center with nubber {medical_center_id} doesn't exist"
                )

            # Получаем услугу
            service_obj = (await s.execute(async_select(
                ServiceTable
            ).filter(
                ServiceTable.client_id == int(doc_params.service_client_id)
            ))).scalars().one_or_none()

            if not service_obj:
                return RequestResult(
                    status_code=422,
                    details_ru=f'Услуги с идентификатором {doc_params.service_client_id} не существует',
                    details=f"The service with nubber {doc_params.service_client_id} doesn't exist"
                )

            # Получаем прайс
            service_price_obj = (await s.execute(async_select(
                PriceTable
            ).filter(
                PriceTable.service_id == service_obj.id,
                and_(
                    PriceTable.price_period.has(PricePeriodTable.start_date <= today),
                    PriceTable.price_period.has(PricePeriodTable.end_date >= today)
                ),
                PriceTable.price_name_id == (async_select(
                    MedicalCenterPriceNameTable.price_name_id
                ).filter(
                    MedicalCenterPriceNameTable.medical_center_id == medical_center_id
                ))
            ))).scalars().one_or_none()

        if not service_price_obj:
            result_create_service_cart = await creating_user_service_cart_for_getting_doc_without_pay(
                patient, service_obj, medical_center_obj, doc_params
            )
            result = result_create_service_cart
        else:
            services_to_pay = [UserServiceCartInputDoc(
                service_id=service_obj.id,
                medical_center_id=medical_center_id,
                price_id=service_price_obj.id
            )]

            payment_data_result = await creating_user_payment_and_purchases(
                user, patient, services_to_pay,
                POSTPONED_PAYMENT,
                medical_center_obj.lpu_id
            )

            if payment_data_result.status_code != 200:
                try:
                    await remove_temporary_payment(
                        payment_data_result.data.payment_info.user_payment_id
                    )
                except Exception as e:
                    print(e)
                    return payment_data_result

            invoice_result = await get_paykeeper_invoice(payment_data_result.data.services_payment_list,
                                                         payment_data_result.data.payment_info,
                                                         medical_center_obj.lpu.client_id)

            if not invoice_result:
                try:
                    await remove_temporary_payment(
                        payment_data_result.data.payment_info.user_payment_id
                    )
                except Exception as e:
                    print(e)
                return RequestResult(
                    status_code=422,
                    details_ru='Нет соединения с платежной системой',
                    details="The connect with the payment system is absent"
                )

            if invoice_result.status_code != 200:
                try:
                    await remove_temporary_payment(
                        payment_data_result.data.payment_info.user_payment_id
                    )
                except Exception as e:
                    print(e)
                return invoice_result
            else:
                invoice_result_data = json.loads(invoice_result.data)
                payment_data_result.data.payment_info.invoice_id = invoice_result_data['invoice_id']
                try:
                    producer.send(
                        PAYKEEPER_CONFIRM_PAYMENT_TOPIC,
                        {
                            'data': payment_data_result.data.payment_info.__dict__,
                            'lpu_client_id': medical_center_obj.lpu.client_id,
                            'payment_method': INITPRO_PAYMENT_METHOD_FULL_PAYMENT,
                            'payment_object': INITPRO_PAYMENT_OBJECT_SERVICE,
                            'payments_type': INITPRO_PAYMENTS_TYPE_FOR_OTHER,
                            'operation_type': INITPRO_OPERATION_TYPE_SELL
                        }
                    )
                except Exception as e:
                    print(e)
                    try:
                        await remove_temporary_payment(
                            payment_data_result.data.payment_info.user_payment_id
                        )
                    except Exception as ee:
                        print(ee)
                    return RequestResult(status_code=500,
                                        details=f'Error - {e}.')

                result_payment_record = await create_temporary_payment_record(
                    payment_data_result.data.payment_info.user_payment_id
                )
                if result_payment_record:
                    result_request_doc_record = await creating_record_for_request_paid_doc(
                        patient.id, payment_data_result.data.payment_info.user_payment_id, doc_params
                    )
                    if result_request_doc_record.status_code == 200:
                        result = RequestResult(
                            data=invoice_result_data['invoice_url'],
                            status_code=200,
                            details_ru='Ок',
                            details=f'{payment_data_result.data.payment_info.__dict__}'
                        )
                    else:
                        try:
                            await remove_temporary_payment(
                                payment_data_result.data.payment_info.user_payment_id
                            )
                        except Exception as e:
                            print(e)
                        result = RequestResult(status_code=500,
                                               details="Can't create the document request record")
                else:
                    try:
                        await remove_temporary_payment(
                            payment_data_result.data.payment_info.user_payment_id
                        )
                    except Exception as e:
                        print(e)
                    result = RequestResult(status_code=500,
                                        details="Can't create the temporary payment")

        end1 = time.time()
        print(f'Полное время на выполнение процедуры request_available_document {(end1-start)*1000} мс')

        return result

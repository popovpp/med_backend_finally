import strawberry
from sqlalchemy.future import select as async_select
from sqlalchemy import func, delete
from datetime import datetime

from core.sa_tables.main_process import (PayKeeperPaymentDataTable, UserPaymentTable,
                                         UserPurchaseTable, ServiceTable,
                                         PolicyTable, TemporaryPaymentTable,
                                         UserServiceCartTable, InitproPaymentReceiptTable,
                                         UserDocumentRequestTable)
from core.sa_tables.accounts import UserTable, MedicalCenterTable
from core.config.scalars import RequestResult
from core.config.db import get_session
from core.config.settings import (SUBSCRIBE_PAYMENT_SERVICE_CLIENT_SERVICE_CODE,
                                  SUPPORT_PHONE, SUPPORT_EMAIL)
from payments.config.settings import (INITPRO_VAT_TYPE_NONE, INITPRO_SNO_OSN,
                                      INITPRO_PAYMENT_METHOD_ADVANCE, INITPRO_PAYMENT_METHOD_FULL_PAYMENT,
                                      INITPRO_PAYMENT_OBJECT_SERVICE, INITPRO_PAYMENTS_TYPE_FOR_ADVANCE)
from .scalars import (InitproRegistrationPayload, InitproItem, InitproItemVat,
                      InitproPayment, InitproReceipt, InitproClient, InitproCompany,
                      InitproVat)
from .scripts_initpro import initpro_document_registration, get_document_registration_result


async def getting_subscribes_users_paid_sum(patient_ids, policy_ids):

    policies_select_filter = []

    if policy_ids:
        policies_select_filter.append(
            PayKeeperPaymentDataTable.user_payment.has(UserPaymentTable.policy_id.in_(policy_ids)),
        )

    async with get_session() as s:

        subscribe_paid_sum = (await s.execute(async_select(
            UserPaymentTable.user_id,
            func.sum(PayKeeperPaymentDataTable.pay_amount),
        ).outerjoin(
            UserPaymentTable,
            UserPaymentTable.id == PayKeeperPaymentDataTable.user_payment_id
        ).outerjoin(
            UserPurchaseTable,
            UserPurchaseTable.user_payment_id == UserPaymentTable.id
        ).filter(
            # PayKeeperPaymentDataTable.user_payment.has(UserPaymentTable.policy_id.in_(policy_ids)),
            *policies_select_filter,
            PayKeeperPaymentDataTable.user_payment.has(UserPaymentTable.user_id.in_(patient_ids)),
            UserPurchaseTable.service.has(
                ServiceTable.client_service_code == SUBSCRIBE_PAYMENT_SERVICE_CLIENT_SERVICE_CODE
            )
        ).group_by(
            UserPaymentTable.user_id
        ))).unique().all()

    return subscribe_paid_sum


async def getting_subscribes_users_debt_sum(patient_ids, policy_ids):

    policies_select_filter = []

    if policy_ids:
        policies_select_filter.append(
            PayKeeperPaymentDataTable.user_payment.has(UserPaymentTable.policy_id.in_(policy_ids)),
        )

    async with get_session() as s:

        subscribe_debt_sum = (await s.execute(async_select(
            UserTable.id,
            func.sum(PolicyTable.amount)
        ).outerjoin(
            PolicyTable,
            PolicyTable.user_id == UserTable.id
        ).filter(
            PolicyTable.user_id.in_(patient_ids),
            PolicyTable.id.in_(policy_ids),
            PolicyTable.is_active == True
        ).group_by(
            UserTable.id
        ))).unique().all()

        subscribe_paid_sum = (await s.execute(async_select(
            UserTable.id,
            func.sum(UserPaymentTable.amount)
        ).outerjoin(
            UserPaymentTable,
            UserPaymentTable.user_id == UserTable.id
        ).outerjoin(
            PolicyTable,
            PolicyTable.id == UserPaymentTable.policy_id
        ).filter(
            UserPaymentTable.payment_type_id == 26,
            PolicyTable.user_id.in_(patient_ids),
            PolicyTable.id.in_(policy_ids),
            PolicyTable.is_active == True,
            UserPaymentTable.policy_id.in_(policy_ids)
        ).group_by(
            UserTable.id
        ))).unique().all()

        subscribe_debt_full = []

        for item in subscribe_debt_sum:
            item_1 = item[1]
            for elem in subscribe_paid_sum:
                if elem[0] == item[0]:
                    item_1 = item[1] - elem[1]
            subscribe_debt_full.append(
                (item[0], item_1)
            )

    return subscribe_debt_full


async def create_temporary_payment_record(payment_id):

    async with get_session() as s:
        try:
            new_temporary_payment = TemporaryPaymentTable(
                payment_id=payment_id,
                payment_time=datetime.now()
            )
            s.add(new_temporary_payment)
            await s.commit()
        except Exception as e:
            print(e)
            return False

    return True


async def delete_temporary_payment_record(payment_id):

    async with get_session() as s:
        try:
            (await s.execute(delete(
                TemporaryPaymentTable
            ).filter(
                TemporaryPaymentTable.payment_id == payment_id
            )))
            await s.commit()
        except Exception as e:
            print(e)
            return False

    return True


async def create_initpro_payload(payment_id,
                                 payment_method,
                                 payment_object,
                                 payments_type):

    async with get_session() as s:

        if not (payment_method == INITPRO_PAYMENT_METHOD_FULL_PAYMENT and
                payment_object == INITPRO_PAYMENT_OBJECT_SERVICE and
                payments_type == INITPRO_PAYMENTS_TYPE_FOR_ADVANCE):
            payment_result = (await s.execute(async_select(
                PayKeeperPaymentDataTable.id,
                PayKeeperPaymentDataTable.obtain_datetime,
                UserTable.email,
                UserTable.login_phone_number,
                UserTable.phone_number,
                UserPurchaseTable.amount,
                UserPurchaseTable.service_quantity,
                ServiceTable.name_for_mz,
                MedicalCenterTable.email,
                MedicalCenterTable.sno,
                MedicalCenterTable.inn,
                MedicalCenterTable.website_url
            ).outerjoin(
                UserPaymentTable,
                UserPaymentTable.id == PayKeeperPaymentDataTable.user_payment_id
            ).outerjoin(
                UserTable,
                UserTable.id == UserPaymentTable.user_id
            ).outerjoin(
                UserPurchaseTable,
                UserPurchaseTable.user_payment_id == UserPaymentTable.id
            ).outerjoin(
                UserServiceCartTable,
                UserServiceCartTable.user_purchase_id == UserPurchaseTable.id
            ).outerjoin(
                ServiceTable,
                ServiceTable.id == UserServiceCartTable.service_id
            ).outerjoin(
                MedicalCenterTable,
                MedicalCenterTable.id == UserServiceCartTable.medical_center_id
            ).filter(
                PayKeeperPaymentDataTable.user_payment_id == payment_id
            ))).unique().all()
        else:
            payment_result = (await s.execute(async_select(
                UserPaymentTable.id,
                UserPaymentTable.payment_date,
                UserTable.email,
                UserTable.login_phone_number,
                UserTable.phone_number,
                UserPurchaseTable.amount,
                UserPurchaseTable.service_quantity,
                ServiceTable.name_for_mz,
                MedicalCenterTable.email,
                MedicalCenterTable.sno,
                MedicalCenterTable.inn,
                MedicalCenterTable.website_url
            ).outerjoin(
                UserTable,
                UserTable.id == UserPaymentTable.user_id
            ).outerjoin(
                UserPurchaseTable,
                UserPurchaseTable.user_payment_id == UserPaymentTable.id
            ).outerjoin(
                UserServiceCartTable,
                UserServiceCartTable.user_purchase_id == UserPurchaseTable.id
            ).outerjoin(
                ServiceTable,
                ServiceTable.id == UserServiceCartTable.service_id
            ).outerjoin(
                MedicalCenterTable,
                MedicalCenterTable.id == UserServiceCartTable.medical_center_id
            ).filter(
                UserPaymentTable.id == payment_id
            ))).unique().all()

        # Формируем payload для передачи в Инитпро кассу
        initpro_receipt_items = []
        initpro_payments = []
        initpro_vats = []
        total_sum = 0
        vat_type = INITPRO_VAT_TYPE_NONE

        for item in payment_result:
            price = item[5]
            quantity = item[6]
            item_sum = round(price*quantity)
            if payment_method == INITPRO_PAYMENT_METHOD_ADVANCE:
                price = item_sum
                quantity = 1
            total_sum += item_sum
            if vat_type == INITPRO_VAT_TYPE_NONE:
                vat_sum = 0.00
            if item[7]:
                name = item[7]
            else:
                name = 'Медициинская услуга'
            initpro_receipt_items.append(
                InitproItem(
                    name=name,
                    price=price,
                    quantity=quantity,
                    sum=item_sum,
                    payment_method=payment_method,
                    payment_object=payment_object,
                    vat=InitproItemVat(
                        type=vat_type,
                        sum=vat_sum
                    )
                )
            )

        initpro_payments.append(
            InitproPayment(
                type=payments_type,
                sum=round(total_sum, 2)
            )
        )

        if vat_type == INITPRO_VAT_TYPE_NONE:
            vat_sum = 0.00
        initpro_vats.append(
            InitproVat(
                type=vat_type,
                sum=vat_sum
            )
        )

        client_phone = None
        client_email = None
        if payment_result[0][3]:
            client_phone = f'+{payment_result[0][3]}'
        elif payment_result[0][4]:
            client_phone = f'+{payment_result[0][4]}'
        else:
            client_email = SUPPORT_EMAIL
        if payment_result[0][2]:
            client_email = payment_result[0][2]

        if not payment_result[0][9]:
            sno = INITPRO_SNO_OSN
        else:
            sno = payment_result[0][9]
        initpro_receipt = InitproReceipt(
            client=InitproClient(
                email=client_email,
                phone=client_phone
            ),
            company=InitproCompany(
                email=payment_result[0][8],
                sno=sno,
                inn="5902034504",#TO DO Восстановить после тестирования payment_result[0][10],
                payment_address="https://test.com",#TO DO Восстановить после тестироаия payment_result[0][11]
            ),
            items=initpro_receipt_items,
            payments=initpro_payments,
            vats=initpro_vats,
            total=total_sum
        )

        initpro_payload = InitproRegistrationPayload(
            external_id=str(payment_id),
            receipt=initpro_receipt,
            timestamp=payment_result[0][1].strftime('%d.%m.%Y %H:%M:%S')
        )

        return initpro_payload


async def creating_receipt(payment_id,
                           payment_method,
                           payment_object,
                           payments_type,
                           lpu_client_id,
                           operation):

    async with get_session() as s:

        payload = strawberry.asdict(await create_initpro_payload(payment_id,
                                                                payment_method,
                                                                payment_object,
                                                                payments_type))

        initpro_payment_receipt = (await s.execute(async_select(
            InitproPaymentReceiptTable
        ).filter(
            InitproPaymentReceiptTable.payment_id == payment_id
        ))).scalars().one_or_none()

        try:
            result_registration = await initpro_document_registration(lpu_client_id, operation, payload)
            if result_registration.status_code == 500:
                raise Exception(f"ERROR. The reciept was not created! - {result_registration}")
            else:
                if initpro_payment_receipt:
                    new_initpro_payment_receipt = initpro_payment_receipt
                    new_initpro_payment_receipt.payment_id = payment_id
                    new_initpro_payment_receipt.initpro_payment_method = payment_method
                    new_initpro_payment_receipt.initpro_payment_object = payment_object
                    new_initpro_payment_receipt.initpro_payment_type = payments_type
                    new_initpro_payment_receipt.uuid = result_registration.data['uuid']
                    new_initpro_payment_receipt.status = result_registration.data['status']
                    new_initpro_payment_receipt.timestamp = datetime.strptime(
                        result_registration.data['timestamp'],
                        '%d.%m.%Y %H:%M:%S'
                    )
                    new_initpro_payment_receipt.lpu_client_id = lpu_client_id
                    new_initpro_payment_receipt.operation_type = operation
                else:
                    new_initpro_payment_receipt = InitproPaymentReceiptTable(
                        payment_id=payment_id,
                        initpro_payment_method=payment_method,
                        initpro_payment_object=payment_object,
                        initpro_payment_type=payments_type,
                        uuid=result_registration.data['uuid'],
                        status=result_registration.data['status'],
                        timestamp=datetime.strptime(result_registration.data['timestamp'], '%d.%m.%Y %H:%M:%S'),
                        lpu_client_id=lpu_client_id,
                        operation_type=operation
                    )
                if result_registration.data['error'] != None:
                    new_initpro_payment_receipt.error_id = str(result_registration.data['error']['error_id'])
                    new_initpro_payment_receipt.error_code = result_registration.data['error']['code']
                    new_initpro_payment_receipt.error_text = result_registration.data['error']['text']
                    new_initpro_payment_receipt.error_type = result_registration.data['error']['type']
                else:
                    new_initpro_payment_receipt.error_id = None
                    new_initpro_payment_receipt.error_code = None
                    new_initpro_payment_receipt.error_text = None
                    new_initpro_payment_receipt.error_type = None

            s.add(new_initpro_payment_receipt)
            await s.commit()
            return True
        except Exception as e:
            print(e)
            if not initpro_payment_receipt:
                err_initpro_payment_receipt = InitproPaymentReceiptTable(
                                payment_id=payment_id,
                                initpro_payment_method=payment_method,
                                initpro_payment_object=payment_object,
                                initpro_payment_type=payments_type,
                                lpu_client_id=lpu_client_id,
                                timestamp=datetime.now(),
                                operation_type=operation
                            )
            else:
                err_initpro_payment_receipt = initpro_payment_receipt
                err_initpro_payment_receipt.payment_id=payment_id,
                err_initpro_payment_receipt.initpro_payment_method=payment_method,
                err_initpro_payment_receipt.initpro_payment_object=payment_object,
                err_initpro_payment_receipt.initpro_payment_type=payments_type,
                err_initpro_payment_receipt.lpu_client_id=lpu_client_id,
                err_initpro_payment_receipt.timestamp=datetime.now(),
                err_initpro_payment_receipt.operation_type=operation
            s.add(err_initpro_payment_receipt)
            await s.commit()
            return False


async def getting_registration_result(initpro_payment_receipt_obj_id,
                                      lpu_client_id,
                                      doc_uuid):

    try:

        async with get_session() as s:

            initpro_payment_receipt_obj = (await s.execute(async_select(
                InitproPaymentReceiptTable
            ).filter(
                InitproPaymentReceiptTable.id == initpro_payment_receipt_obj_id
            ))).scalars().one_or_none()

            if initpro_payment_receipt_obj:
                result_getting_result = await get_document_registration_result(lpu_client_id, doc_uuid)
                if result_getting_result.status_code == 500:
                    raise Exception(f"ERROR. The reciept was not created! - {result_getting_result}")
                elif result_getting_result.status_code == 200:
                    initpro_payment_receipt_obj.status = result_getting_result.data['status']
                    initpro_payment_receipt_obj.timestamp = datetime.strptime(
                        result_getting_result.data['timestamp'],
                        '%d.%m.%Y %H:%M:%S'
                    )
                    initpro_payment_receipt_obj.payload_total = str(result_getting_result.data['payload']['total'])
                    initpro_payment_receipt_obj.payload_fns_site = result_getting_result.data['payload']['fns_site']
                    initpro_payment_receipt_obj.payload_fn_number = str(result_getting_result.data['payload']['fn_number'])
                    initpro_payment_receipt_obj.payload_shifr_number = str(result_getting_result.data['payload']['shift_number'])
                    initpro_payment_receipt_obj.payload_receipt_datetime = datetime.strptime(
                        result_getting_result.data['payload']['receipt_datetime'],
                        '%Y-%m-%d %H:%M:%S'
                    )
                    initpro_payment_receipt_obj.payload_fiscal_receipt_number = str(result_getting_result.data['payload']['fiscal_receipt_number'])
                    initpro_payment_receipt_obj.payload_fiscal_document_number = str(result_getting_result.data['payload']['fiscal_document_number'])
                    initpro_payment_receipt_obj.payload_ecr_registration_number = str(result_getting_result.data['payload']['ecr_registration_number'])
                    initpro_payment_receipt_obj.payload_fiscal_document_attribute = str(result_getting_result.data['payload']['fiscal_document_attribute'])
                    initpro_payment_receipt_obj.group_code = str(result_getting_result.data['group_code'])
                    initpro_payment_receipt_obj.daemon_code = str(result_getting_result.data['daemon_code'])
                    initpro_payment_receipt_obj.device_code = str(result_getting_result.data['device_code'])
                    initpro_payment_receipt_obj.warnings = result_getting_result.data['warnings']
                    initpro_payment_receipt_obj.external_id = str(result_getting_result.data['external_id'])
                    initpro_payment_receipt_obj.callback_url = result_getting_result.data['callback_url']
                    initpro_payment_receipt_obj.error_id = None
                    initpro_payment_receipt_obj.error_code = None
                    initpro_payment_receipt_obj.error_text = None
                    initpro_payment_receipt_obj.error_type = None
                else:
                    initpro_payment_receipt_obj.status = result_getting_result.data['status']
                    initpro_payment_receipt_obj.timestamp = datetime.strptime(
                        result_getting_result.data['timestamp'],
                        '%d.%m.%Y %H:%M:%S'
                    )
                    if result_getting_result.data['error'] != None:
                        initpro_payment_receipt_obj.error_id = str(result_getting_result.data['error']['error_id'])
                        initpro_payment_receipt_obj.error_code = result_getting_result.data['error']['code']
                        initpro_payment_receipt_obj.error_text = result_getting_result.data['error']['text']
                        initpro_payment_receipt_obj.error_type = result_getting_result.data['error']['type']
                    else:
                        initpro_payment_receipt_obj.error_id = None
                        initpro_payment_receipt_obj.error_code = None
                        initpro_payment_receipt_obj.error_text = None
                        initpro_payment_receipt_obj.error_type = None
                s.add(initpro_payment_receipt_obj)
                await s.commit()
            else:
                print(f"The receipt object {initpro_payment_receipt_obj_id} doesn't exist.")
                return None
    except Exception as e:
        print(f'ERROR - {e}')
        return None

    return initpro_payment_receipt_obj


async def set_true_paid_flag_for_doc_request_record(payment_id):

    # print(payment_id)
    # 1/0

    try:
        async with get_session() as s:

            doc_request_record = (await s.execute(async_select(
                UserDocumentRequestTable
            ).filter(
                UserDocumentRequestTable.payment_id == payment_id
            ))).scalars().one_or_none()

            # print(doc_request_record)
            # 1/0

            if doc_request_record:
                doc_request_record.is_paid = True
                s.add(doc_request_record)
                await s.commit()

            return True
    except Exception as e:
        print(f'ERROR - {e}')
        return False

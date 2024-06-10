import asyncio
import logging
import faust
import json
import time
import xmltodict
from datetime import datetime, timedelta
from prometheus_client import Counter
from sqlalchemy.future import select as async_select
from sqlalchemy import delete, or_


from phone_auth.src.scripts import sms_ru_agent_handler
from faustians.config import settings
from core.config.settings import (WAITING_CONFIRMING_PAYMENT_PERIOD, TEMPORARY_PAYMENTS_CLEAN_INTERVAL,
                                  GETTING_REGISTRATION_RECEIPT_INTERVAL, SENDING_DOCUMENT_REQUEST_INTERVAL)
from core.config.db import get_session
from core.sa_tables.main_process import (UserPaymentTable, PayKeeperPaymentDataTable,
                                         TemporaryPaymentTable, InitproPaymentReceiptTable,
                                         UserServiceCartTable, ServiceTable, ServiceGroupTable,
                                         UserDocumentRequestTable)
from core.sa_tables.accounts import LpuTable
from core.src.common_resolvers import remove_temporary_payment
from oracle_connector.scripts.oracle_connector import call_oracle_proc
from oracle_connector.config.settings import (ORACLE_PROC_CHECK_PATIENT, ORACLE_PROC_CREATE_USER_PATIENT,
                                              ORACLE_PROC_CONFIRM_PATIENT_BY_EMAIL, ORACLE_PROC_CONFIRM_PAYMENT,
                                              ORACLE_PROC_REQUEST_DOCUMENT)
from core.config.cache_connector import CacheConnector
from core.config.settings import (EXP_TIME_FOR_ORACLE_PROC_RESULT, EXP_TIME_FOR_EMAIL_DATA, FLASH_CALL_TOPIC,
                                  PATIENT_REGISTRATION_TOPIC, CHECK_PATIENT_IN_ORACLE_TOPIC, CONFIRM_PATIENT_BY_EMAIL,
                                  PAYKEEPER_CONFIRM_PAYMENT_TOPIC)
from payments.src.scripts import get_payments_list_info
from payments.src.resolvers import payment_recovery
from payments.src.utils import (delete_temporary_payment_record, creating_receipt,
                                getting_registration_result, set_true_paid_flag_for_doc_request_record)


REQUEST_CNT = Counter('request', 'Sent request count')
SUCCESS_RESPONSE_CNT = Counter('success_response', 'Received response with valid data')
ERROR_RESPONSE_CNT = Counter('error_response', 'Received response with error count')


cache = CacheConnector()


logging.basicConfig(
    level=logging.getLevelName(settings.LOGGING_LEVEL),
    format=settings.LOGGING_FORMAT
)


logger = logging.getLogger(__name__)


app = faust.App(
    settings.SYSTEM_NAME,
    broker=settings.KAFKA_BROKER,
    store='rocksdb://'
)


flash_call_topic = app.topic(FLASH_CALL_TOPIC, partitions=1)
create_patient_in_oracle_topic = app.topic(PATIENT_REGISTRATION_TOPIC, partitions=1)
check_patient_in_oracle_topic = app.topic(CHECK_PATIENT_IN_ORACLE_TOPIC, partitions=1)
confirm_patient_by_email_topic = app.topic(CONFIRM_PATIENT_BY_EMAIL, partitions=1)
paykeeper_confirm_payment_topic = app.topic(PAYKEEPER_CONFIRM_PAYMENT_TOPIC, partitions=1)


@app.agent(flash_call_topic, concurrency=settings.FAUST_CONCURRENCY)
async def on_event_flash_call(stream):
    async for msg_key, msg_value in stream.items():
        await asyncio.sleep(3)
        # await flash_call_agent_handler(msg_value)
        await sms_ru_agent_handler(msg_value)


@app.agent(check_patient_in_oracle_topic, concurrency=settings.FAUST_CONCURRENCY)
async def on_event_check_patient_in_oracle(stream):

    data = []
    async for msg_key, msg_value in stream.items():
        key = msg_value['key']
        try:
            data = cache.get(key)
            if data:
                data_for_oracle = [value for key, value in json.loads(data).items()]
            else:
                return 'data is wrong'
            print(data_for_oracle)
            result = await call_oracle_proc(data_for_oracle, ORACLE_PROC_CHECK_PATIENT)
            print(result)
            cache.set(
                f'{key}_{ORACLE_PROC_CHECK_PATIENT}',
                json.dumps({'result':result, 'error': None}).encode(),
                EXP_TIME_FOR_ORACLE_PROC_RESULT
            )
        except Exception as e:
            print(e)
            cache.set(
                f'{key}_{ORACLE_PROC_CHECK_PATIENT}',
                json.dumps({'result': None, 'error': str(e)}).encode(),
                EXP_TIME_FOR_ORACLE_PROC_RESULT
            )
            logger.error(f'on_event_check_patient_in_oracle() has got error {e}')


@app.agent(create_patient_in_oracle_topic, concurrency=settings.FAUST_CONCURRENCY)
async def on_event_create_patient_in_oracle_topic(stream):
    proc_name = ORACLE_PROC_CREATE_USER_PATIENT
    data = []
    async for msg_key, msg_value in stream.items():
        try:
            key = msg_value['key']
            data = msg_value['data']
            data_for_oracle = [value for key, value in data.items()]
            result = await call_oracle_proc(data_for_oracle, proc_name)
            cache.set(
                f'{key}_{proc_name}',
                json.dumps({'result':result, 'error': None}).encode(),
                EXP_TIME_FOR_ORACLE_PROC_RESULT
            )
        except Exception as e:
            print(e)
            cache.set(
                f'{key}_{proc_name}',
                json.dumps({'result': None, 'error': str(e)}).encode(),
                EXP_TIME_FOR_ORACLE_PROC_RESULT
            )
            logger.error(f'on_event_create_patient_in_oracle_topic() has got error {e}')


@app.agent(confirm_patient_by_email_topic, concurrency=settings.FAUST_CONCURRENCY)
async def on_event_confirm_patient_by_email_topic(stream):
    proc_name = ORACLE_PROC_CONFIRM_PATIENT_BY_EMAIL
    data = []
    async for msg_key, msg_value in stream.items():
        key = msg_value['key']
        data = msg_value['data']
        data_for_oracle = [str(value) for key, value in data.items()]
        repeat = 5
        while repeat > 0:
            try:    
                result = await call_oracle_proc(data_for_oracle, proc_name)
                if result[0] == 200:
                    repeat = 0
                    cache.set(
                    f'{key}_{proc_name}',
                    json.dumps({'result':result, 'error': None}).encode(),
                    EXP_TIME_FOR_EMAIL_DATA
                )
                else:
                    repeat -= 1
                    if repeat == 0:
                        cache.set(
                        f'{key}_{proc_name}',
                        json.dumps({'result':result, 'error': None}).encode(),
                        EXP_TIME_FOR_EMAIL_DATA
                )
            except Exception as e:
                repeat -= 1
                print(e)
                if repeat == 0:
                    cache.set(
                        f'{key}_{proc_name}',
                        json.dumps({'result': None, 'error': str(e)}).encode(),
                        EXP_TIME_FOR_EMAIL_DATA
                    )
                logger.error(f'on_event_create_patient_in_oracle_topic() has got error {e}')


@app.agent(paykeeper_confirm_payment_topic, concurrency=settings.FAUST_CONCURRENCY)
async def on_event_paykeeper_confirm_payment_topic(stream):

    data = []
    async for msg_key, msg_value in stream.items():

        today = datetime.today()
        start_date = (today - timedelta(days=2)).strftime('%Y-%m-%d')
        end_date = today.strftime('%Y-%m-%d')
        start_timer = time.time()
        timer = 0
        timer_stop = 0

        data = []

        data = msg_value['data']
        lpu_client_id = msg_value['lpu_client_id']
        payment_method = msg_value['payment_method']
        payment_object = msg_value['payment_object']
        payments_type = msg_value['payments_type']
        operation_type = msg_value['operation_type']

        print(data)

        print(timer, "$$$$$$$$$$$$$$$$$$", data)

        while timer <= WAITING_CONFIRMING_PAYMENT_PERIOD:

            print('timer = ', timer)

            await asyncio.sleep(settings.REQUESTING_CONFIRMING_INTERVAL)

            result = await get_payments_list_info(500, 0, start_date, end_date, lpu_client_id)

            if result.data is not None:
                result.data.sort(key=lambda x: x['id'])
                result_payments_dict = dict([(str(x['orderid']), x) for x in result.data])
            else:
                result_payments_dict = {}

            try:
                async with get_session() as s:
                    if result_payments_dict[str(data['user_payment_id'])]['status'] in ("obtained", "stuck", "success"):
                        print('########PAYMENT CONFIRMED###############')

                        payment_obj = (await s.execute(async_select(UserPaymentTable).filter(
                            UserPaymentTable.id == int(data['user_payment_id'])
                        ))).unique().scalars().one_or_none()

                        print(payment_obj.__dict__)

                        # Меняем статус платежа на подтвержденный
                        if payment_obj.payment_type_id == 7:
                            payment_obj.payment_type_id = 26
                        elif payment_obj.payment_type_id == 6:
                            payment_obj.payment_type_id = 25
                            lpu_obj = (await s.execute(async_select(LpuTable).filter(
                                LpuTable.client_id == int(lpu_client_id)
                            ))).unique().scalars().one_or_none()
                            payment_obj.lpu_id = lpu_obj.id
                            payment_obj.avance_amount = payment_obj.amount
                        else:
                            print('########PAYMENT_TYPE IS WRONG###############')
                            timer = time.time() - start_timer + WAITING_CONFIRMING_PAYMENT_PERIOD
                            print('timer =', timer)
                            return timer

                        # Проверяем наличие платежа в таблице PayKeeperPaymentDataTable
                        new_paykeeper_data_obj = (await s.execute(async_select(
                            PayKeeperPaymentDataTable
                        ).filter(
                            PayKeeperPaymentDataTable.user_payment_id == payment_obj.id
                        ))).scalars().one_or_none()

                        if not new_paykeeper_data_obj:
                            # Создаем запись о платеже в таблице платежной системы
                            new_paykeeper_data_obj = PayKeeperPaymentDataTable(
                                user_payment_id=payment_obj.id,
                                paykeeper_id=result_payments_dict[str(data['user_payment_id'])]['id'],
                                pay_amount=float(result_payments_dict[str(data['user_payment_id'])]['pay_amount']),
                                refund_amount=float(result_payments_dict[str(data['user_payment_id'])]['refund_amount']),
                                clientid=result_payments_dict[str(data['user_payment_id'])]['clientid'],
                                orderid=result_payments_dict[str(data['user_payment_id'])]['orderid'],
                                payment_system_id=result_payments_dict[str(data['user_payment_id'])]['payment_system_id'],
                                unique_id=result_payments_dict[str(data['user_payment_id'])]['unique_id'],
                                status=result_payments_dict[str(data['user_payment_id'])]['status'],
                                repeat_counter=int(result_payments_dict[str(data['user_payment_id'])]['repeat_counter']),
                                pending_datetime=datetime.strptime(
                                    result_payments_dict[str(data['user_payment_id'])]['pending_datetime'],
                                    '%Y-%m-%d %H:%M:%S'
                                ),
                                obtain_datetime=datetime.strptime(
                                    result_payments_dict[str(data['user_payment_id'])]['obtain_datetime'],
                                    '%Y-%m-%d %H:%M:%S'
                                ),
                                success_datetime= datetime.strptime(
                                    result_payments_dict[str(data['user_payment_id'])]['success_datetime'],
                                    '%Y-%m-%d %H:%M:%S'
                                )
                            )

                            s.add(payment_obj)
                            s.add(new_paykeeper_data_obj)
                            # await s.flush()
                            await s.commit()

                        repeat = 5
                        while repeat > 0:
                            try:
                                data_for_oracle = [str(payment_obj.client_id)]
                                result = await call_oracle_proc(data_for_oracle, ORACLE_PROC_CONFIRM_PAYMENT)
                                print(result)
                                if result[0] == 200:
                                    # time.sleep(3)
                                    # payment_obj.lpu_id = lpu_obj.id
                                    # payment_obj.avance_amount = payment_obj.amount
                                    # s.add(payment_obj)
                                    # await s.commit()
                                    repeat = 0
                                    print("*********COMMIT-COMMIT*************")
                                    del_tem_pay_rec = await delete_temporary_payment_record(payment_obj.id)
                                    print(f"The record has been deleted from temporary_payments_records, status={del_tem_pay_rec}")

                                    result_receipt = await creating_receipt(payment_obj.id,
                                                                            payment_method,
                                                                            payment_object,
                                                                            payments_type,
                                                                            lpu_client_id,
                                                                            operation_type)
                                    if not result_receipt:
                                        print('Сбой процедуры регистрации чека')
                                        # TO DO Направить уведомление в аварийный топик 
                                        # или записать в базу номер платежа для последующей отправки чека

                                    result_set_flag = await set_true_paid_flag_for_doc_request_record(payment_obj.id)
                                    if not result_set_flag:
                                        print('Сбой процедуры установки признака оплаты услуги заказа документа')
                                        # TO DO Направить уведомление в аварийный топик 
                                        # или записать в базу номер платежа для последующей установки

                                elif result[0] == 500 or result[0] == 504:
                                    # await s.delete(new_paykeeper_data_obj)
                                    await s.close()
                                    recovery_result = await payment_recovery(payment_obj.id)
                                    print('!!!!!!!!!!!!!!!!!!!!!!!', recovery_result)
                                    if recovery_result.status_code == 200:
                                        repeat = -1
                                    else:
                                        # TO DO Вызов процедуры отправки E-mail с уведомлением
                                        # о невозможности передать подтверждение платежа.
                                        timer_stop += WAITING_CONFIRMING_PAYMENT_PERIOD
                            except Exception as e:
                                repeat -= 1
                                print(e)
                                logger.error(f'on_event_payment confirming_in_oracle_topic() has got error {e}')

                        if repeat == 0:
                            timer_stop += WAITING_CONFIRMING_PAYMENT_PERIOD
            except Exception as e:
                print(e)

            timer = time.time() - start_timer + timer_stop
    print('Процедура on_event_paykeeper_confirm_payment_topic завершена', 'timer =', timer)
    return timer


@app.timer(interval=TEMPORARY_PAYMENTS_CLEAN_INTERVAL)
async def delete_temporary_payments():

    try:
        at_moment = datetime.now()

        async with get_session() as s:

            temporary_payments = (await s.execute(async_select(
                TemporaryPaymentTable
            ))).scalars().all()

        if temporary_payments:
            print([x.payment_id for x in temporary_payments])
            for temp_payment in temporary_payments:
                print('@@@@@@', (temp_payment.payment_time + timedelta(seconds=WAITING_CONFIRMING_PAYMENT_PERIOD)))
                if (temp_payment.payment_time + timedelta(seconds=WAITING_CONFIRMING_PAYMENT_PERIOD)) <= at_moment:
                    await remove_temporary_payment(temp_payment.payment_id)
                    async with get_session() as s:
                        check_payment = (await s.execute(async_select(
                            UserPaymentTable.id
                        ).filter(
                            UserPaymentTable.id == temp_payment.payment_id
                        ))).scalars().one_or_none()
                        if not check_payment:
                            (await s.execute(delete(
                                TemporaryPaymentTable
                            ).filter(
                                TemporaryPaymentTable.id == temp_payment.id
                            )))
                            await s.commit()
        else:
            print("Temporary payments are absent")

        print('The delete_temporary_payments() has been finished')
    except Exception as e:
        print(f'There is a crush error in the delete_temporary_payments() - {e}')
        # TO DO направить сообщение в аварийный топик


@app.timer(interval=GETTING_REGISTRATION_RECEIPT_INTERVAL)
async def getting_receipt_registration_result():

    try:
        async with get_session() as s:

            receipts = (await s.execute(async_select(
                InitproPaymentReceiptTable
            ).filter(or_(
                InitproPaymentReceiptTable.status == None,
                InitproPaymentReceiptTable.status == 'wait'
            )
            ))).scalars().all()

            if receipts:
                print([x.payment_id for x in receipts])
                for rec in receipts:
                    rec_uuid = rec.uuid
                    if rec.status == None:
                        result_receipt = await creating_receipt(rec.payment_id,
                                                                rec.initpro_payment_method,
                                                                rec.initpro_payment_object,
                                                                rec.initpro_payment_type,
                                                                rec.lpu_client_id,
                                                                rec.operation_type)
                        if not result_receipt:
                            print(f'Сбой процедуры регистрации чека: {rec}')
                            # TO DO Направить уведомление в аварийный топик 
                            # или записать в базу номер платежа для последующей отправки чека
                        else:
                            rec_uuid = result_receipt.data['uuid']

                    initpro_payment_receipt_obj = await getting_registration_result(
                        rec.id,
                        rec.lpu_client_id,
                        rec_uuid
                    )

                    if initpro_payment_receipt_obj:
                        print(f'The operation with {rec.id} was ok.')

            else:
                print("There are not any initpro_payment_receipt objects with the status 'None' or 'wait'.")

            print('The getting_receipt_registration_result() has been finished')
    except Exception as e:
        print(f'There is a crush error in the getting_receipt_registration_result() - {e}')
        # TO DO направить сообщение в аварийный топик


@app.timer(interval=SENDING_DOCUMENT_REQUEST_INTERVAL)
async def sending_request_to_get_document():

    try:
        async with get_session() as s:

            doc_requests_records = (await s.execute(async_select(
                UserDocumentRequestTable
            ).filter(
                UserDocumentRequestTable.is_requested == False,
                UserDocumentRequestTable.status != 99
            ))).scalars().all()

            print(doc_requests_records)

            if doc_requests_records:
                for item in doc_requests_records:
                    data_for_oracle = [
                        item.user_service_cart_client_id,
                        xmltodict.unparse({"root": json.loads(item.doc_params)}, pretty=True)
                    ]
                    result = await call_oracle_proc(data_for_oracle, ORACLE_PROC_REQUEST_DOCUMENT)
                    print(result)
                    if result[0] == 200:
                        oracle_check_data = xmltodict.parse(result[2].lower())
                        item.client_id = int(oracle_check_data['data']['client_id'])
                        item.is_requested = True
                        item.request_date = datetime.now()
                        await s.flush()
                    else:
                        item.status = 99
                        item.status_description = str(result)
                        await s.flush()

                await s.commit()

            print('The sending_request_to_get_document has been finished')
    except Exception as e:
        print(f'There is a crush error in the sending_request_to_get_document() - {e}')
        # TO DO направить сообщение в аварийный топик

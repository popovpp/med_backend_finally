import requests
import time
import json
from datetime import datetime, timedelta

from requests.auth import HTTPBasicAuth
from core.config.scalars import RequestResult
from core.config.settings import WAITING_CONFIRMING_PAYMENT_PERIOD
from payments.config.settings import (PAY_KEEPER_REPEAT, PAY_KEEPER_DICT)


async def get_paykeeper_token(lpu_client_id):
    """
    Вызов API PayKeeper, получение токена безопасности
    """

    pay_keeper_params = PAY_KEEPER_DICT[lpu_client_id]

    auth = HTTPBasicAuth(pay_keeper_params[0], pay_keeper_params[1])

    repeat = int(PAY_KEEPER_REPEAT)
    token = None
    while repeat>0:
        try:
            res = requests.get(f'{pay_keeper_params[2]}/info/settings/token',
                               auth=auth, timeout=15)
            if res.status_code == 200:
                result = res.json()
                req = res.request
                print('{}\n{}\r\n{}\r\n\r\n{}'.format(
                    '-----------START-----------',
                    req.method + ' ' + req.url,
                    '\r\n'.join('{}: {}'.format(k, v) for k, v in req.headers.items()),
                    req.body,
                ))
                print(result)
                # 1/0
                try:
                    token = result['token']
                    repeat = 0
                except Exception as e:
                    print(e)
                    repeat = 0
            else:
                print('#############', res.status_code, res.text)
                repeat -= 1
                time.sleep(1)
        except Exception as e:
            error = 'При вызове API произошла ошибка: ' + str(e)
            print(error)
            # logging.info(error)
            repeat -= 1
            time.sleep(1)
    # logging.info('Finish')
    return token


async def get_paykeeper_invoice(services_list, payment_info, lpu_client_id):
    """
    Вызов API PayKeeper, получение ссылки на счет для оплаты
    """
    #########################################################
    # Формат записи об оплачиваемых элементах
    # service_name = f""";PKC|{json.dumps([
    #     {
    #             "name": 'Стол обеденный 2x3',
    #             "price": 1.50,
    #             "quantity": 1,
    #             "sum": 1.50,
    #             "tax": 'none'
    #     },
    #     {
    #             "name": 'Книга о вкусной и здоровой пище',
    #             "price": 2,
    #             "quantity": 3,
    #             "sum": 6,
    #             "tax": 'none',
    #     }
    # ])}|"""
    #########################################################

    pay_keeper_params = PAY_KEEPER_DICT[lpu_client_id]

    token = await get_paykeeper_token(lpu_client_id)

    if not token:
        return None

    auth = HTTPBasicAuth(pay_keeper_params[0], pay_keeper_params[1])

    service_name = f""";PKC|{json.dumps([x.__dict__ for x in services_list])}|"""

    payload = {
        "pay_amount": payment_info.pay_amount,
        "clientid": payment_info.user_id,
        "orderid": payment_info.user_payment_id,
        "service_name": service_name,
        "client_email": payment_info.user_email,
        "client_phone": payment_info.user_phone_number,
        # Формат поля expiry "YYYY-MM-DD HH:MM"
        "expiry": (datetime.now() + timedelta(seconds=WAITING_CONFIRMING_PAYMENT_PERIOD)).strftime('%Y-%m-%d %H:%M'),
        "token": token
    }

    repeat = int(PAY_KEEPER_REPEAT)
    result = None
    error = None
    res = None
    while repeat>0:
        try:
            res = requests.post(f'{pay_keeper_params[2]}/change/invoice/preview/',
                                auth=auth, data=payload, timeout=15)
            if res.status_code == 200:
                result = res.json()
                repeat = 0
                return RequestResult(
                    data=json.dumps({"invoice_url": result['invoice_url'],
                        "invoice_id": result['invoice_id'],
                        "invoice": result['invoice']
                    }),
                    status_code=200,
                    details_ru='Ок',
                    details=f"Ok - {payload['expiry']}"
                )
            else:
                print('#############', res.status_code, res.text)
                # logging.info(error)
                repeat -= 1
                time.sleep(1)
        except Exception as e:
            error = 'При вызове API произошла ошибка: ' + str(e)
            print(error)
            # logging.info(error)
            repeat -= 1
            time.sleep(1)
    # logging.info('Finish')
    details = ''
    if result:
        details = f"Result of request - {result} - {payload['expiry']}"
    if error:
        details += f'{details}, exception - {error}'
    return RequestResult(
        status_code=500,
        details_ru='Платежная система временно недоступна. Повторите попытку позже.',
        details=details
    )


# async def get_paykeeper_sbp_qrcode():
#     """
#     Вызов API PayKeeper, получение ссылки на форму с QR-кодом
#     """

#     # token = await get_paykeeper_token()

#     # if not token:
#     #     return None

#     auth = HTTPBasicAuth(PAY_KEEPER_USER, PAY_KEEPER_PASSWORD)

#     payload = {
#         "sum": 100,
#         "clientid": "Ivanov",
#         "orderid":	"2",
#         "service_name":	"uzi",
#         "client_email": "admin@admin.com",
#         "client_phone": "79211111111",
#         "pstype": "sbp_default",
#         "json": "true"
#     }

#     repeat = int(PAY_KEEPER_REPEAT)
#     result = None
#     while repeat>0:
#         try:
#             res = requests.post(f'{PAY_KEEPER_URL}/create/',
#                                data=payload, timeout=15)
#             print(res.status_code)
#             if res.status_code == 200:
#                 result = res.text#res.json()
#                 print(result)
#                 repeat = 0
#             else:
#                 print('#############', res.status_code, res.text)
#         except Exception as e:
#             error = 'При вызове API произошла ошибка: ' + str(e)
#             print(error)
#             # logging.info(error)
#             repeat -= 1
#             time.sleep(1)
#     # logging.info('Finish')
#     return result


# async def get_paykeeper_change_formfield():
#     """
#     Вызов API PayKeeper, изменния полей в платежной форме
#     """

#     token = await get_paykeeper_token()

#     if not token:
#         return None

#     auth = HTTPBasicAuth(PAY_KEEPER_USER, PAY_KEEPER_PASSWORD)

#     payload = {

#         'pk_name': 'pstype',
#         'displayed_name': 'pstype',
#         'required': 'false',
#         'placeholder': 'sbp_default',
#         'enabled': 'true',
#         'type': 'text',
#         'order': 100,
#         "token": token
#     }

#     repeat = int(PAY_KEEPER_REPEAT)
#     result = None
#     while repeat>0:
#         try:
#             res = requests.post(f'{PAY_KEEPER_URL}/change/organization/formfield/',
#                                auth=auth, data=payload, timeout=15)
#             print(res.status_code)
#             if res.status_code == 200:
#                 result = res.json()
#                 print(result)
#                 repeat = 0
#             else:
#                 print('#############', res.status_code, res.text)
#         except Exception as e:
#             error = 'При вызове API произошла ошибка: ' + str(e)
#             print(error)
#             # logging.info(error)
#             repeat -= 1
#             time.sleep(1)
#     # logging.info('Finish')
#     return result['result']


# async def get_payment_information(paykeeper_invoice_id):
#     """
#     Вызов API PayKeeper, получение информации о платеже
#     """

#     # token = await get_paykeeper_token()

#     # if not token:
#     #     return None

#     auth = HTTPBasicAuth(PAY_KEEPER_USER, PAY_KEEPER_PASSWORD)

#     repeat = int(PAY_KEEPER_REPEAT)
#     result = None
#     error = None
#     res = None
#     while repeat>0:
#         try:
#             res = requests.get(f'{PAY_KEEPER_URL}/info/payments/byid/?id={int(paykeeper_invoice_id)}',#&advanced=true',
#                                auth=auth, timeout=15)
#             print(res.status_code)
#             if res.status_code == 200:
#                 # result = res.text
#                 result = res.json()
#                 print(result)
#                 repeat = 0
#                 return RequestResult(
#                     data=result,
#                     status_code=200,
#                     details_ru='Ок',
#                     details='Ok'
#                 )
#             else:
#                 print('#############', res.status_code, res.text)
#                 # logging.info(error)
#                 repeat -= 1
#                 time.sleep(1)
#         except Exception as e:
#             error = 'При вызове API произошла ошибка: ' + str(e)
#             print(error)
#             # logging.info(error)
#             repeat -= 1
#             time.sleep(1)
#     # logging.info('Finish')
#     details = ''
#     if res:
#         details = f'Result of request - {res}'
#     if error:
#         details = f'{details}, exception - {error}'
#     return RequestResult(
#         status_code=500,
#         details_ru='Платежная система временно недоступна. Повторите попытку позже.',
#         details=details
#     )


async def get_payments_list_info(limit, skip, start_date, end_date, lpu_client_id):
    """
    Вызов API PayKeeper, получение реестра платежей
    """

    pay_keeper_params = PAY_KEEPER_DICT[lpu_client_id]

    params = {
        "limit": limit,
        "from": skip,
        "start": start_date,
        "end": end_date,
        "status[]": ["obtained", "stuck", "success", "canceled", "failed", "pending", "refunding",
                   "refunded", "partially_refunded"],
        "payment_system_id[]": [9, 127]
    }

    auth = HTTPBasicAuth(pay_keeper_params[0], pay_keeper_params[1])

    repeat = int(PAY_KEEPER_REPEAT)
    result = None
    error = None
    res = None
    while repeat>0:
        try:
            res = requests.get(f'{pay_keeper_params[2]}/info/payments/bydate/',
                               auth=auth, params=params, timeout=15)
            print(res)
            print(res.__dict__)
            if res.status_code == 200:
                if res.__dict__['_content']:
                    result = res.json()
                repeat = 0
                return RequestResult(
                    data=result,
                    status_code=200,
                    details_ru='Ок',
                    details='Ok'
                )
            else:
                print('#############', res.status_code, res.text)
                # logging.info(error)
                repeat -= 1
                time.sleep(1)
        except Exception as e:
            error = 'При вызове API произошла ошибка: ' + str(e)
            print(error)
            # logging.info(error)
            repeat -= 1
            time.sleep(1)
    # logging.info('Finish')
    details = ''
    if res:
        details = f'Result of request - {res}'
    if error:
        details = f'{details}, exception - {error}'
    return RequestResult(
        status_code=500,
        details_ru='Платежная система временно недоступна. Повторите попытку позже.',
        details=details
    )

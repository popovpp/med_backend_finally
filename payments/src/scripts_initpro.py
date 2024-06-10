import requests
import time
import json

from core.config.scalars import RequestResult
from payments.config.settings import (INITPRO_REPEAT, INITPRO_DICT)


async def get_initpro_token(lpu_client_id):
    """
    Вызов API Инитпро, получение токена безопасности
    """
    time.sleep(0.1)
    pay_keeper_params = INITPRO_DICT[lpu_client_id]

    repeat = int(INITPRO_REPEAT)
    token = None
    while repeat>0:
        try:
            res = requests.get(f'{pay_keeper_params[2]}/getToken?login={pay_keeper_params[0]}&pass={pay_keeper_params[1]}',
                               timeout=15)
            if res.status_code == 200:
                result = res.json()
                try:
                    token = result['token']
                    repeat = 0
                except Exception as e:
                    print(e)
            else:
                print('#############', res.status_code, res.json())
                repeat -= 1
        except Exception as e:
            error = 'При вызове API произошла ошибка: ' + str(e)
            print(error)
            # logging.info(error)
            repeat -= 1
    # logging.info('Finish')
    return token


async def initpro_document_registration(lpu_client_id, operation, input_payload):
    """
    Вызов API Инитпро, регистрация документа
    """

    pay_keeper_params = INITPRO_DICT[lpu_client_id]

    token = await get_initpro_token(lpu_client_id)

    if not token:
        return None

    payload = json.dumps(input_payload)

    headers = {'Content-Type': 'application/json; charset=utf-8'}
    headers["Token"] = token

    repeat = int(INITPRO_REPEAT)
    result = None
    error = None
    res = None
    while repeat>0:
        try:
            res = requests.post(f'{pay_keeper_params[2]}/{pay_keeper_params[3]}/{operation}',
                                headers=headers, data=payload, timeout=15)
            if res.status_code == 200:
                result = res.json()
                print(result)
                repeat = 0
                return RequestResult(
                    data=result,
                    status_code=200,
                    details_ru='Ок',
                    details='Ok'
                )
            else:
                print('#############', res.status_code, res.json())
                # logging.info(error)
                repeat -= 1
        except Exception as e:
            error = 'При вызове API произошла ошибка: ' + str(e)
            print(error)
            # logging.info(error)
            repeat -= 1
            time.sleep(1)
    # logging.info('Finish')
    details = ''
    data=None
    status_code=500
    if res != None:
        data=res.json()
        status_code=res.status_code
        details = f'Result of request - {res}'
    if error:
        details += f'{details}, exception - {error}'
    return RequestResult(
        data=data,
        status_code=status_code,
        details_ru='Облачная касса временно недоступна. Повторите попытку позже.',
        details=details
    )


async def get_document_registration_result(lpu_client_id, doc_uuid):
    """
    Вызов API Инитпро, запрос результата обработки документа
    """

    pay_keeper_params = INITPRO_DICT[lpu_client_id]

    token = await get_initpro_token(lpu_client_id)

    if not token:
        return None

    headers = {'Content-Type': 'application/json; charset=utf-8'}
    headers["Token"] = token

    repeat = int(INITPRO_REPEAT)
    result = None
    error = None
    res = None
    while repeat>0:
        try:
            res = requests.get(f'{pay_keeper_params[2]}/{pay_keeper_params[3]}/report/{doc_uuid}',
                                headers=headers, timeout=15)
            if res.status_code == 200:
                result = res.json()
                print(result)
                repeat = 0
                return RequestResult(
                    data=result,
                    status_code=200,
                    details_ru='Ок',
                    details='Ok'
                )
            else:
                print('#############', res.status_code, res.json())
                # logging.info(error)
                repeat -= 1
        except Exception as e:
            error = 'При вызове API произошла ошибка: ' + str(e)
            print(error)
            # logging.info(error)
            repeat -= 1
            time.sleep(1)
    # logging.info('Finish')
    details = ''
    if result:
        details = f'Result of request - {result}'
    if error:
        details += f'{details}, exception - {error}'
    return RequestResult(
        status_code=500,
        details_ru='Облачная касса временно недоступна. Повторите попытку позже.',
        details=details
    )

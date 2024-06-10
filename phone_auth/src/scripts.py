import requests
import logging
import pprint
import time
from uuid import uuid4

from ..config.settings import (FLASH_CALL_KEY, FLASH_CALL_ID, FLASH_CALL_URL,
                               FLASH_CALL_REPEAT, FLASH_CALL_INTERVAL, SMS_RU_API_KEY,
                               SMS_RU_CODE_ATTEMPTS_MAX, SMS_RU_TIMEOUT_SECONDS,
                               SMS_RU_MESSAGE_MAX_ALIVE, SMS_RU_URL, SMS_RU_SEND_INTERVAL)


async def flash_call_agent_handler(message):
    """
    Вызов API uCaller, метод initCall - авторизация пользователя по телефону
    """
    result = None
    # logging.info('Start')
    client = f"{message['phone'][:4]}***{message['phone'][-5:]}"
    payload = {
        'phone': message['phone'],
        'code': message['code'],
        'client': client,
        'unique': uuid4(),
        'voice': False,
        'key': FLASH_CALL_KEY,
        'service_id': FLASH_CALL_ID
    }

    repeat = FLASH_CALL_REPEAT
    while repeat>0:
        try:
            res = requests.get(FLASH_CALL_URL,
                                params=payload, timeout=15)
            if res.status_code == 200:
                result = res.json()
                repeat = 0
                print(result)
            else:
                print('#############', res.status_code, res.text)
                pprint.pprint(res.json())
                return None
        except Exception as e:
            error = 'При вызове API произошла ошибка: ' + str(e)
            print(error)
            # logging.info(error)
            repeat -= 1
            time.sleep(FLASH_CALL_INTERVAL)
    # logging.info('Finish')
    return result


async def sms_ru_agent_handler(message):
    """
    Вызов API sms.ru, Отправить СМС сообщение HTTP запросом
    """
    time.sleep(SMS_RU_SEND_INTERVAL)
    result = None
    # logging.info('Start')
    payload = {
        "api_id": SMS_RU_API_KEY,
        # 'from': '79817505500',
        'to': str(message['phone']),
        'msg': str(message['code']),
        'json': 1,
        'ttl': SMS_RU_MESSAGE_MAX_ALIVE,
        # 'test': 1
    }

    repeat = SMS_RU_CODE_ATTEMPTS_MAX
    while repeat>0:
        try:
            res = requests.get(SMS_RU_URL,#?api_id={SMS_RU_API_KEY}&from=79817505500&to={message['phone']}&msg={message['code']}&json=1")#,
                                params=payload, timeout=SMS_RU_TIMEOUT_SECONDS)
            if res.status_code == 200:
                result = res.json()
                repeat = 0
                print(result)
            else:
                print('#############', res.status_code, res.text)
                pprint.pprint(res.json())
                return None
        except Exception as e:
            error = 'При вызове API произошла ошибка: ' + str(e)
            print(error)
            # logging.info(error)
            repeat -= 1
            # time.sleep(SMS_RU_SEND_INTERVAL)
    # logging.info('Finish')
    return result

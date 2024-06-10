import random
import typing
from fastapi import Request, WebSocket

from core.config.cache_connector import CacheConnector
from core.config.settings import EXP_TIME_FOR_TIME_MARKER


cache = CacheConnector()


async def flash_code_generator():
    random.seed(version=2)
    s =''
    result = ''
    char = ''
    for i in range(0,4):
        while s == char:
            char = str(random.randint(1, 9))
        s = char
        result = result + char
    print(result)
    return str(result)


async def multi_clicking_protection(user, info):

    request: typing.Union[Request, WebSocket] = info.context["request"]

    ip = request.headers['Host']

    key = f'{user.id}:{ip}'

    try:
        time_marker = cache.get(key)
        print(time_marker)
        if time_marker:
            return False
        else:
            cache.set(key, ip, EXP_TIME_FOR_TIME_MARKER)
            return True
    except Exception as e:
        print(e)

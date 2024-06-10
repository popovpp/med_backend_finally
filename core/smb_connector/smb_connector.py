import asyncio
# import concurrent
import smbprotocol
from smbclient import open_file, register_session

from core.config.settings import (SMB_PASSWORD, SMB_SERVER_IP, SMB_SHARED_FOLDER, SMB_USERNAME,
                                  PING_REPEATING)
from core.src.utils import address_ping_with_repeat


# register_session(SMB_SERVER_IP, username=SMB_USERNAME, password=SMB_PASSWORD)

try:
    register_session(SMB_SERVER_IP, username=SMB_USERNAME, password=SMB_PASSWORD)
    REGISTER_SESSION = True
except Exception as e:
    REGISTER_SESSION = False
    print(f"Error - {e}. Отсутствует соединение с {SMB_SERVER_IP}.")


async def get_file_by_smb(file_path):

    global REGISTER_SESSION

    def_ping_result = await address_ping_with_repeat(
        SMB_SERVER_IP,
        PING_REPEATING,
        [500, 'ping -> False', f"Отсутствует соединение с {SMB_SERVER_IP}."],
        [200, 'ping -> True', "Ok"]
    )

    if def_ping_result[0] !=200:
        REGISTER_SESSION = False
        return def_ping_result
    else:
        print(def_ping_result)
        if not REGISTER_SESSION:
            register_session(SMB_SERVER_IP, username=SMB_USERNAME, password=SMB_PASSWORD)

    # Читаем файл, как байтовый массив
    try:
        with open_file(f"\\{SMB_SERVER_IP}{SMB_SHARED_FOLDER}{file_path}", mode="rb") as fd:
            data = fd.read()
    except Exception as e:
        return [404, f'{e}', f"Файл не найден на {SMB_SERVER_IP}."]

    return data

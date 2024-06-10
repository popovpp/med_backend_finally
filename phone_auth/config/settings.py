import os


# Flash Call parameters
FLASH_CALL_KEY = os.environ.get('FLASH_CALL_KEY', default='1111111111')
FLASH_CALL_ID = os.environ.get('FLASH_CALL_ID', default=1111111111)
FLASH_CALL_URL = os.environ.get('FLASH_CALL_URL', default='http://')
FLASH_CALL_REPEAT = int(os.environ.get('FLASH_CALL_REPEAT', default=2))
FLASH_CALL_INTERVAL = float(os.environ.get('FLASH_CALL_INTERVAL', default=0.04))


# SMS.RU parameters
SMS_RU_API_KEY=os.environ.get('SMS_RU_API_KEY', default='1111111111')
SMS_RU_URL=os.environ.get('SMS_RU_URL', default='https://sms.ru/sms/send')
SMS_RU_TIMEOUT_SECONDS=int(os.environ.get('SMS_RU_TIMEOUT_SECONDS', default=15))
SMS_RU_MESSAGE_MAX_ALIVE=int(os.environ.get('SMS_RU_MESSAGE_MAX_ALIVE', default=3))
SMS_RU_CODE_ATTEMPTS_MAX=int(os.environ.get('SMS_RU_CODE_ATTEMPTS_MAX', default=5))
SMS_RU_SEND_INTERVAL = float(os.environ.get('FLASH_CALL_INTERVAL', default=0.04))

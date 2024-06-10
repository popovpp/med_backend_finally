import os
from pathlib import Path

# Debug
DEBUG = True
if os.environ.get('DEBUG') and os.environ.get('DEBUG') == 'false':
    DEBUG = False

if DEBUG:
    SECRET_KEY = """R/R1yrLduYL0O2R+9kvs/zc4VdxaRhJo09QcLcC0NsdfpC1AYe5dKzB11OmaMLD+
BdyGj0EW8AHFuieKgKBH6KdFUlmrKi1vYiPhV98XAA4sMLfzyUeQ/xjt/gnCJt2r
93OlrIMlAPO5cfPTVdpiZXSNi3gjRePC"""
else:
    SECRET_KEY = os.environ.get('SECRET_KEY')


BASE_DIR = Path(__file__).resolve().parent
STATIC_ROOT = BASE_DIR.parent / 'static'
MEDIA_ROOT = BASE_DIR.parent / 'media'
DOWNLOAD_PATH = os.path.join(MEDIA_ROOT, 'downloads')

if not os.path.isdir(DOWNLOAD_PATH):
    os.makedirs(DOWNLOAD_PATH)


# System
SYSTEM_NAME = 'Payments'
APP_URL = os.environ.get('APP_URL', default='')
MEDIA_URL = '/media/'

# Postgres database
PG_HOST = os.environ.get('PG_HOST', default='localhost')
PG_PORT = os.environ.get('PG_PORT', default='5432')
PG_USER = os.environ.get('PG_USER', default='postgres')
PG_PASSWORD = os.environ.get('PG_PASSWORD', default='postgres')
PG_DB = os.environ.get('PG_DB', default='main_db')

# Pagination
PAGINATION_PAGE_SIZE = 100
PAGINATION_PAGE_SIZE_MAX = 100000

# Cache
# REDIS_CONN_STR = 'redis://localhost/0'

# Description
PROJECT_VERSION = '0.1.0'
PROJECT_TITLE = 'Payments'
PROJECT_DESCRIPTION = '''
Payments is service of Patient personal area
'''

# PayKeeper parameters
PAY_KEEPER_USER_1 = os.environ.get('PAY_KEEPER_USER_1', default='json')
PAY_KEEPER_PASSWORD_1 = os.environ.get('PAY_KEEPER_PASSWORD_1', default='json')
PAY_KEEPER_URL_1 = os.environ.get('PAY_KEEPER_URL_1', default='http://')

PAY_KEEPER_USER_2 = os.environ.get('PAY_KEEPER_USER_2', default='json')
PAY_KEEPER_PASSWORD_2 = os.environ.get('PAY_KEEPER_PASSWORD_2', default='json')
PAY_KEEPER_URL_2 = os.environ.get('PAY_KEEPER_URL_2', default='http://')

PAY_KEEPER_USER_3 = os.environ.get('PAY_KEEPER_USER_3', default='json')
PAY_KEEPER_PASSWORD_3 = os.environ.get('PAY_KEEPER_PASSWORD_3', default='json')
PAY_KEEPER_URL_3 = os.environ.get('PAY_KEEPER_URL_3', default='http://')

PAY_KEEPER_USER_4 = os.environ.get('PAY_KEEPER_USER_4', default='json')
PAY_KEEPER_PASSWORD_4 = os.environ.get('PAY_KEEPER_PASSWORD_4', default='json')
PAY_KEEPER_URL_4 = os.environ.get('PAY_KEEPER_URL_4', default='http://')

PAY_KEEPER_USER_6 = os.environ.get('PAY_KEEPER_USER_6', default='json')
PAY_KEEPER_PASSWORD_6 = os.environ.get('PAY_KEEPER_PASSWORD_6', default='json')
PAY_KEEPER_URL_6 = os.environ.get('PAY_KEEPER_URL_6', default='http://')

PAY_KEEPER_USER_8 = os.environ.get('PAY_KEEPER_USER_8', default='json')
PAY_KEEPER_PASSWORD_8 = os.environ.get('PAY_KEEPER_PASSWORD_8', default='json')
PAY_KEEPER_URL_8 = os.environ.get('PAY_KEEPER_URL_8', default='http://')

PAY_KEEPER_DICT = {
    1: (PAY_KEEPER_USER_1, PAY_KEEPER_PASSWORD_1, PAY_KEEPER_URL_1),
    2: (PAY_KEEPER_USER_2, PAY_KEEPER_PASSWORD_2, PAY_KEEPER_URL_2),
    3: (PAY_KEEPER_USER_3, PAY_KEEPER_PASSWORD_3, PAY_KEEPER_URL_3),
    4: (PAY_KEEPER_USER_4, PAY_KEEPER_PASSWORD_4, PAY_KEEPER_URL_4),
    6: (PAY_KEEPER_USER_6, PAY_KEEPER_PASSWORD_6, PAY_KEEPER_URL_6),
    8: (PAY_KEEPER_USER_8, PAY_KEEPER_PASSWORD_8, PAY_KEEPER_URL_8)
}

PAY_KEEPER_REPEAT = os.environ.get('PAY_KEEPER_REPEAT', default=5)
PAY_KEEPER_EXPIRY_INTERVAL_MIN = 15


# Payments types
POSTPONED_PAYMENT = '24007'
CONFIRMED_PAYMENT = '89303694'
POSTPONED_ADVANCE = '24006'
CONFIRMED_ADVANCE = '89303693'

ADVANCE_SERVICE_CLIENT_ID = 931000
COMMON_SERVICE_TAX_RATE = 0


# Initpro parameters
INITPRO_USER_1 = os.environ.get('INITPRO_USER_1', default='json')
INITPRO_PASSWORD_1 = os.environ.get('INITPRO_PASSWORD_1', default='json')
INITPRO_URL_1 = os.environ.get('INITPRO_URL_1', default='http://')
INITPRO_GROUP_CODE_1=os.environ.get('INITPRO_GROUP_CODE_1', default='json')

INITPRO_USER_2 = os.environ.get('INITPRO_USER_2', default='json')
INITPRO_PASSWORD_2 = os.environ.get('INITPRO_PASSWORD_2', default='json')
INITPRO_URL_2 = os.environ.get('INITPRO_URL_2', default='http://')
INITPRO_GROUP_CODE_2=os.environ.get('INITPRO_GROUP_CODE_2', default='json')

INITPRO_USER_3 = os.environ.get('INITPRO_USER_3', default='json')
INITPRO_PASSWORD_3 = os.environ.get('INITPRO_PASSWORD_3', default='json')
INITPRO_URL_3 = os.environ.get('INITPRO_URL_3', default='http://')
INITPRO_GROUP_CODE_3=os.environ.get('INITPRO_GROUP_CODE_3', default='json')

INITPRO_USER_4 = os.environ.get('INITPRO_USER_4', default='json')
INITPRO_PASSWORD_4 = os.environ.get('INITPRO_PASSWORD_4', default='json')
INITPRO_URL_4 = os.environ.get('INITPRO_URL_4', default='http://')
INITPRO_GROUP_CODE_4=os.environ.get('INITPRO_GROUP_CODE_4', default='json')

INITPRO_USER_6 = os.environ.get('INITPRO_USER_6', default='json')
INITPRO_PASSWORD_6 = os.environ.get('INITPRO_PASSWORD_6', default='json')
INITPRO_URL_6 = os.environ.get('INITPRO_URL_6', default='http://')
INITPRO_GROUP_CODE_6=os.environ.get('INITPRO_GROUP_CODE_6', default='json')

INITPRO_USER_8 = os.environ.get('INITPRO_USER_8', default='json')
INITPRO_PASSWORD_8 = os.environ.get('INITPRO_PASSWORD_8', default='json')
INITPRO_URL_8 = os.environ.get('INITPRO_URL_8', default='http://')
INITPRO_GROUP_CODE_8=os.environ.get('INITPRO_GROUP_CODE_8', default='json')

INITPRO_DICT = {
    1: (INITPRO_USER_1, INITPRO_PASSWORD_1, INITPRO_URL_1, INITPRO_GROUP_CODE_1),
    2: (INITPRO_USER_2, INITPRO_PASSWORD_2, INITPRO_URL_2, INITPRO_GROUP_CODE_2),
    3: (INITPRO_USER_3, INITPRO_PASSWORD_3, INITPRO_URL_3, INITPRO_GROUP_CODE_3),
    4: (INITPRO_USER_4, INITPRO_PASSWORD_4, INITPRO_URL_4, INITPRO_GROUP_CODE_4),
    6: (INITPRO_USER_6, INITPRO_PASSWORD_6, INITPRO_URL_6, INITPRO_GROUP_CODE_6),
    8: (INITPRO_USER_8, INITPRO_PASSWORD_8, INITPRO_URL_8, INITPRO_GROUP_CODE_8)
}

INITPRO_REPEAT = os.environ.get('INITPRO_REPEAT', default=5)
INITPRO_EXPIRY_INTERVAL_MIN = 15

INITPRO_PAYMENT_METHOD_ADVANCE = 'advance'
INITPRO_PAYMENT_METHOD_FULL_PAYMENT = 'full_payment'
INITPRO_PAYMENT_OBJECT_SERVICE = 'service'
INITPRO_PAYMENT_OBJECT_PAYMENT = 'payment'
INITPRO_PAYMENTS_TYPE_FOR_ADVANCE = 2
INITPRO_PAYMENTS_TYPE_FOR_OTHER = 1
INITPRO_VAT_TYPE_NONE = 'none'
INITPRO_OPERATION_TYPE_SELL = 'sell'
INITPRO_SNO_OSN = 'osn'


# Sms
# SMS_URL = 'https://sms.ru/sms/send?api_id=2430897F-FCAA-C1EE-EFFE-B6FC2173BD84&to={phone}&msg={message}&json=1'
# SMS_TIMEOUT_SECONDS = 60 * 2  # 2 минуты
# SMS_CODE_MAX_ALIVE = 60 * 60  # 1 час
# SMS_CODE_ATTEMPTS_MAX = 5
# SMS_PUBLIC_PHONE = '+79000000000'
# SMS_PUBLIC_CODE = '1234'

# Пути изображений
# IMAGES_PATH_MEDIA = os.environ.get('IMAGES_PATH_STORE', default='/work/www/shop-survey/media/')
# IMAGES_PATH_ICEMAN_STORE = 'iceman/stores/photos/'
# IMAGES_PATH_ICEMAN_STORE_DOCUMENT = 'iceman/stores/documents/'
# IMAGES_PATH_ICEMAN_QR = 'iceman/qr/'
# IMAGES_PATH_ICEMAN_PRODUCTS = 'iceman/products/'

# Тиньков
# TINKOFF_TERMINAL_KEY = '1639142013666'
# TINKOFF_PASSWORD = 'm0l2avpxji3yeszf'
# TINKOFF_PAYMENT_URL = 'https://securepay.tinkoff.ru/v2/Init'
# TINKOFF_QR_URL = 'https://securepay.tinkoff.ru/v2/GetQr'
# TINKOFF_CANCEL_URL = 'https://securepay.tinkoff.ru/v2/Cancel'

# Dadata
# DADATA_KEY = '096aae6e9f53500da116ab7f3568b1bbb04c9e56'
# DADATA_SECRET = '8632b49788d8e1774e52224b9d0b92b71583324c'

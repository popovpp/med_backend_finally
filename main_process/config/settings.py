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
SYSTEM_NAME = 'Main process'
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
PROJECT_TITLE = 'Main process'
PROJECT_DESCRIPTION = '''
Main process is service of Patient personal area
'''

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

# Санкции
# SANCTIONS_REGIONS = (
#     'херс', 'запор', 'крым', 'симф', 'сева', 'днр', 'лнр', 'донец', 'луганс'
# )

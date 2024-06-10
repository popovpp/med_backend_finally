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
SYSTEM_NAME = 'Faustians'
APP_URL = os.environ.get('APP_URL', default='')
MEDIA_URL = '/media/'


# Description
PROJECT_VERSION = '0.1.0'
PROJECT_TITLE = 'Faustians'
PROJECT_DESCRIPTION = '''
Faustians is service of Patient personal area
'''

LOGGING_LEVEL='INFO'
LOGGING_FORMAT='%(asctime)-15s | %(levelname)s | %(filename)s | %(lineno)d: %(message)s'

KAFKA_BROKER='kafka://kafka'
KAFKA_WEB_HOST='kafka'
KAFKA_WEB_PORT=9092

# WAITING_CONFIRMING_PAYMENT_PERIOD = 900
REQUESTING_CONFIRMING_INTERVAL = 15
FAUST_CONCURRENCY = 10

# Postgres database
PG_HOST = os.environ.get('PG_HOST', default='localhost')
PG_PORT = os.environ.get('PG_PORT', default='5432')
PG_USER = os.environ.get('PG_USER', default='postgres')
PG_PASSWORD = os.environ.get('PG_PASSWORD', default='postgres')
PG_DB = os.environ.get('PG_DB', default='main_db')


MED_DOCS_SERVICE_GROUP_CLIENT_ID = 86137
SELECTION_LIMIT_FOR_REQUEST_DOCS = 10000


# # Kafka topics
# FLASH_CALL_TOPIC='flash-call-topic'
# PATIENT_REGISTRATION_TOPIC='create-patient-in-oracle-topic'
# CHECK_PATIENT_IN_ORACLE_TOPIC = 'check-patient-in-oracle-topic'
# CONFIRM_PATIENT_BY_EMAIL = 'confirm-patient-by-email-oracle-topic'
# PAYKEEPER_CONFIRM_PAYMENT_TOPIC = 'paykeeper-confirm-payment-topic'

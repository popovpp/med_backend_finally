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
SYSTEM_NAME = 'Accounts'
APP_URL = os.environ.get('APP_URL', default='')
MEDIA_URL = '/media/'

# Pagination
PAGINATION_PAGE_SIZE = 100
PAGINATION_PAGE_SIZE_MAX = 100000

# Description
PROJECT_VERSION = '1.0.0'
PROJECT_TITLE = 'Accounts'
PROJECT_DESCRIPTION = '''
Accounts service of Patient personal area
'''

# New policy parameters
POLICY_SHIFR_ID = 167
POLICY_END_DATE = '31.12.2099'
POLICY_STATUS = 1

LOGGING_LEVEL='INFO'
LOGGING_FORMAT='%(asctime)-15s | %(levelname)s | %(filename)s | %(lineno)d: %(message)s'

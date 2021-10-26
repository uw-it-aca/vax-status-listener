from .base_settings import *
import os

INSTALLED_APPS += [
    'vs_listener.apps.VSListenerConfig',
]

DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'

DOCUSIGN_CONNECT_SECRET = bytes(os.getenv('DOCUSIGN_CONNECT_SECRET', ''),
                                encoding='utf8')
EMAIL_DOMAINS = ['uw.edu', 'washington.edu']
REQUESTOR_ROLES = ['student', 'requestor']

REG_STATUS_ALLOWED = 4
REG_STATUS_BLOCKED = 1

OK_PROCESSING_STATUS = [200, 202, 404, 412]

from .base_settings import *
import os

INSTALLED_APPS += [
    'vs_listener.apps.VSListenerConfig',
]

DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'

DOCUSIGN_CONNECT_SECRET = bytes(os.getenv('DOCUSIGN_CONNECT_SECRET', ''),
                                encoding='utf8')
EMAIL_DOMAINS = ['uw.edu', 'washington.edu']
SIGNER_ROLES = ['student', 'requestor']

from .base_settings import *
import os

INSTALLED_APPS += [
    'vs_listener.apps.VSListenerConfig',
]

DOCUSIGN_CONNECT_SECRET = bytes(os.getenv('DOCUSIGN_CONNECT_SECRET', ''),
                                encoding='utf8')

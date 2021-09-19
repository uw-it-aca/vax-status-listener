from .base_settings import *
import os

INSTALLED_APPS += [
    'vs_listener.apps.VSListenerConfig',
]

DOCUSIGN_CONNECT_SECRET = os.getenv('DOCUSIGN_CONNECT_SECRET', '')

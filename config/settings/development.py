from .base import *

DEBUG = True

INSTALLED_APPS += ['django_extensions']

# Emails dans la console
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

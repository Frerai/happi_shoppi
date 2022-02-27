import os
import dj_database_url  # For using the database URL in production environment.
from .common import *

SECRET_KEY = os.environ['SECRET_KEY']


DEBUG = False


# Production version of the app. Only domain name needs to be provided, no "http" or "/"".
ALLOWED_HOSTS = ['happi-shoppi-prod.herokuapp.com']


DATABASES = {
    # This "config()" function reads the configured environment variable "DATABASE_URL", then parses the connection string, and returns a dictionary that is used here as the default setting.
    'default': dj_database_url.config()
}


# Must first be read as an environment variable.
REDIS_URL = os.environ['REDIS_URL']

# Setting for Celery. Set to Redis server. Port is also specified in the Docker container. The "1" is, by convention, name of the database.
CELERY_BROKER_URL = REDIS_URL


# For Redis caching server.
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': REDIS_URL,
        'TIMEOUT': 10 * 60,  # Timer for how long cache is stored.
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}


# The "smtp" backend is the default setting, and this setting does not need to be specified since it is the default. This may be overwritten to console or other backends, if desired.
# If console backend is wanting to be used, swap "smtp" out with "console" - which is the name of the module. Also "filebased" backend module can be used to write emails to a file.
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

# When using an smtp (Simple Mail Transfer Protocol) server, the adress of the smtp server must be provided.
# All settings are provided from the configuration of production environment variable on Heroku.
EMAIL_HOST = os.environ['MAILGUN_SMTP_SERVER']

EMAIL_HOST_USER = os.environ['MAILGUN_SMTP_LOGIN']

EMAIL_HOST_PASSWORD = os.environ['MAILGUN_SMTP_PASSWORD']

EMAIL_PORT = os.environ['MAILGUN_SMTP_PORT']

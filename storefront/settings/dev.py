from .common import *

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config('SECRET_KEY')


# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True


if DEBUG:
    # Profiling tool - execution profile of apps. Should only be added when in development and testing.
    # Used to identify the source of the issue of functions, queries, data sent to DB etc. and profiles these executions.
    MIDDLEWARE += ['silk.middleware.SilkyMiddleware', ]

# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'storefront3',
        'HOST': 'localhost',
        'USER': 'root',
        'PASSWORD': config('SECRET_PW')
    }
}

# Setting for Celery. Set to Redis server. Port is also specified in the Docker container. The "1" is, by convention, name of the database.
CELERY_BROKER_URL = 'redis://localhost:6379/1'

# For Redis caching server.
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/2',
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
EMAIL_HOST = 'localhost'

# The fake smtp server doesn't have a user or pw, so this this empty.
EMAIL_HOST_USER = ''

# Settings must be set, when actual host, user and pw are used. This is neglectable for a fake smtp server used for development purposes.
EMAIL_HOST_PASSWORD = ''

EMAIL_PORT = 2525  # By default runs on port 25, but fake server runs 2525.

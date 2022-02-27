import os  # For setting path.
from celery import Celery  # Class for engaging workers.

'''
Commands for workers to activate, since this runs on Windows OS:
"celery -A storefront worker -l info -P gevent" command for starting worker
"celery -A storefront beat" command for starting beat
"celery -A storefront flower" command for starting flower
'''

# First argument is the variable of which to environ must look for. Second argument is the path to the settings module.
# Basically this environment variable is set to "storefront.settings", which references the settings module inside "storefront" folder.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'storefront.settings.dev')

# Creating celery instance, and give it a name - "storefront".
celery = Celery('storefront')

# Sepcifying where the instance "celery" can find configuration variables.
# First argument is, go into "django.conf" module and load the "settings" object.
# Second argument is a keyword argument "namespace", which means all configuration settings should start with whatever passed in - "CELERY".
celery.config_from_object('django.conf:settings', namespace='CELERY')

# The tasks which are specified in the "tasks" module in the "playground" app.
# Calling this method tells celery to automatically discover all tasks.
celery.autodiscover_tasks()

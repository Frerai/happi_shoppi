# Must be loaded here in this package, otherwise Python will not execute the code written at "celery.py" in this app..
from .celery import celery

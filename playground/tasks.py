from time import sleep  # For simulation purposes.
# Decorator. May also decorate with "celery.task" object imported from "storefront.celery". But this will create a dependancy between the apps.
from celery import shared_task  # From celery library.


@shared_task
def notify_customers(message):
    print("Sending 10 THOUSAND FISTS IN THE AIIIIRRRR!!!")
    print(message)
    sleep(10)  # Simulating a long running task by sleeping.
    print("Emails were successfully sent in the AIIIIIIIIIR!!!")

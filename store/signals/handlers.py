# A decorator. It tells Django to use whatever function is decorated, when a "User" model is saved.
from django.dispatch import receiver
from django.db.models.signals import post_save  # A "post save" signal.
# To avoid building dependencies between apps, settings is imported, since the User setting is defined there as AUTH_USER_MODEL.
from django.conf import settings

from store.models import Customer


# Tells Django to use this function whenever a "User" model is saved. The function creates a new "customer" when a user is created.
# First argument is the signal we're interested in - a "POST" save. Second argument is which models "post save" signal/event should be listened to. AUTH_USER_MODEL is defined in the settings, which is a custom defined "User" class.
@receiver(post_save, sender=settings.AUTH_USER_MODEL)  # A signal handler.
# Initializes a new customer whenever a user is created.
def create_customer_for_new_user(sender, **kwargs):
    if kwargs["created"]:  # A key. Checking to see if a new model instance is created
        # Customer is created. To get the instance go to the keyword arguments and pick the instance.
        Customer.objects.create(user=kwargs["instance"])

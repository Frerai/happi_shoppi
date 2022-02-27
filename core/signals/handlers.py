from django.dispatch import receiver  # Receiver decorator.

# Receiving the signal from "store" app.
from store.signals import order_created


# A handler function.
@receiver(order_created)  # Receiving this signal.
def on_order_created(sender, **kwargs):
    print(kwargs["order"])

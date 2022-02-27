# This is where signals are defined.

from django.dispatch import Signal  # Importing the Signal class.


# Creating a signal object. A signal is an instance of the "Signal" class.
order_created = Signal()

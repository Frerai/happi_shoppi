# For sending single mail. If more than one mail is wanted to be sent at once "send_mass_mail" is prefered.
# "BadHeaderError" is to prevent email attacks.
# The "EmailMessage" class methods can be used to sending email with atachements. Use ".attach_file(playground/static/images/whatever.jpg)" and ".send()"
import requests
import logging  # For creating and writing logs.
from django.core.cache import cache  # The low-level cache API.
from django.core.mail import send_mail, mail_admins, BadHeaderError
from django.shortcuts import render  # To render http requests.
# For decorating the "cache_page" decorator. Otherwise "cache_page" decorator will not work on class-based views, only function-based views.
from django.utils.decorators import method_decorator
# Decorator for caching views. Allows to gather the "get()" and "set()" methods for getting a key and then caching the data. Only works on function-based views.
from django.views.decorators.cache import cache_page

from rest_framework.views import APIView  # For creating a class-based view.
# Extends "EmailMessage" from Django, and has all of its methods like attaching files, sending emails etc.
from templated_mail.mail import BaseEmailMessage

# from .tasks import notify_customers  # Tasks using celery.

# Pass in the magic attribute "__name__" which basically replaces "playground.views" for best practice. This is for the logger bucket, so this name can be added to the list of logs to capture messages from.
logger = logging.getLogger(__name__)
"""
The logger object has methods for writing different types of log messages.
logger.info - logger.debug - logger.error - logger.critical - logger.warning
"""


class HelloView(APIView):
    # Timer for caching. "method_decorator" is a decorator for making "cache_page" decorator work on a class-based view.
    # @method_decorator(cache_page(3 * 60))
    def get(self, request):  # Defining a "get()" method with 2 parameters.
        try:
            # Writing a severity level of "info" message to the log.
            logger.info(
                "Info: sending request to endpoint httpbin.")
            # Sending a https request to another service, which simulates a slow third-party service with a delay of 2 seconds respond time.
            # This creates a response.
            response = requests.get("https://httpbin.org/delay/2")
            logger.info("Info: response was received at endpoint httpbin.")
            # Getting response, making it a json, and storing it in "data".
            data = response.json()
        except requests.ConnectionError:  # Catching exceptions of type ConnectionError.
            logger.critical(
                "The accessed endpoint is currently not responding.")  # Critical error msg.
        # Using data the retrieved from httpbin. Looks like no cache is created, but the decorator takes care of this.
        return render(request, 'hello.html', {'name': "Frerai"})


# send_mail(
#             "Subject - Learning to send mail",
#             "Message - I am learning to send emails with Django. I wonder if this might be it?",
#             "from_sender@domain.com",
#             ["to_receiver@recipient_list.com", "marley@dodo.com",
#                 "bob@dada.com", "dylan@ohla.com"]
#         )

    # try:
    #     message = BaseEmailMessage(
    #         template_name="emails/hello.html",  # The template created at templates folder
    #         # Context object used to pass data to the template. The "name" key is a variable expected in the template.
    #         context={"name": "Frerai"}
    #     )
    #     message.send(["better_mail_class@dorito.com"])
    # except BadHeaderError:
    #     pass

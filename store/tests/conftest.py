# Special file for pytest. Fixtures and reuseable functions defined here, pytest will automatically load them, without explicitly loading this module every time.

from django.contrib.auth.models import User
from rest_framework.test import APIClient
import pytest


@pytest.fixture  # Applying the fixture decorator to make this function a fixture
def api_client():  # Function for importing the APIclient class.
    return APIClient()  # Returning an APIClient instance.


@pytest.fixture
def authenticate(api_client):  # Takes api_client for posting purposes.
    # Is set to False to avoid specifying this value in every test.
    def do_authenticate(is_staff=False):
        # Creating an User object to avoid importing User class in every test module. The value of is_staff is set to what is received in the inner function.
        return api_client.force_authenticate(user=User(is_staff=is_staff))
    return do_authenticate

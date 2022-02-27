# For authenticating users, for testing.
from django.contrib.auth.models import User

from rest_framework import status  # For testing status on requests.
# For testing sending requests to the server. This is an API client class.
from rest_framework .test import APIClient

# For avoiding to fill in many irrelevant fields of an instance of a model, that must be filled in, when accessing models like Product and Collection. "baker" will fill it with random values.
from model_bakery import baker
import pytest  # For access to decorator "django.db" for testing.

# For testing if collections exists so they can be retrieved.
from store.models import Collection

'''
Commands for testing with pytest:
"pytest" for all tests. "pytest store/tests" will only execute tests in given directory. "pytest store/tests/test_collections.py" will only execute tests in given module.
"pytest store/tests/test_collections.py::TestCreateCollection" will target specific class. "pytest store/tests/test_collections.py::TestCreateCollection::test_whatever" will test specific method.
"pytest -k authenticated" is used for specifying a pattern of testing various tests with a given word in their name.
"ptw" for running pytestwatch which is a library for continous testing.
'''


# Fixture for creating collection. To avoid re-calling "/store/collections/" endpoint every time a POST request is sent for testing.
# This fixture is created here rather than conftests.py, since it's only relevant for this module and not for general purpose of testings.
@pytest.fixture
def create_collection(api_client):  # Needed for posting requests to server.
    def do_create_collection(collection):
        # Not hardcoding a collection here since both valid/invalid collections may be passed in for various testings.
        # Creating an inner function that takes "collection" and returns the collection to the outer function.
        # When sending a post request to the server, a response is returned. "APIClient()" is now therefore no longer needed to be created as an instance of a client in every test.
        return api_client.post('/store/collections/', collection)
    # Return for use in testing when creating collections that posts requests to the "/store/collections/" endpoint, and allows to pass values such as title as object.
    return do_create_collection


# Applying decorator to access db even though in test-mode, so all methods in this class inherits this decorator.
@pytest.mark.django_db
# @pytest.mark.skip decorator applied for skipping a test on any classes and methods.
class TestCreateCollection:
    # Takes in "self" and second parameter is a fixture "api_client" defined in the "conftest.py" module of the "tests" folder. Pytest will call the function and return its value here.
    def test_if_user_is_anonymous_returns_401(self, create_collection):
        # AAA - Arrange, Act, Assert. Tripple As needed for when testing.

        # Act part - the behaviour wanting to be tested. Creating a "client" object.
        # client = APIClient()  Can be left out, since apiclient fixture is added as a parameter.

        # Fixture for the request body. An object of collections with a title. This is the inner function of "create_collection". This calls that function, and allows to pass it a collection.
        response = create_collection({'title': 'a'})

        # Assert part - checking to see if the expected behaviour will happen or not.
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_if_user_is_not_admin_returns_403(self, authenticate, create_collection):
        # Fixture for authenticating users - "is_staff=False" is not required and may be removed in this case.
        authenticate()
        # client = APIClient()
        # Method for authenticating a user. Testing to see if the user is not admin authenticated. User is set to an empty dict.
        # client.force_authenticate(user={}) Not needed since a fixture has been added.
        # Sending a POST request. First argument is the endpoint that is posted. Second argument is the request body, and an object is included here. An object of collections, with a given title.
        response = create_collection({'title': 'a'})
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_if_data_is_invalid_returns_400(self, authenticate, create_collection):
        authenticate(is_staff=True)
        # client = APIClient()
        # Setting user to a real user object fra djangos "User" class. Is staff is True, so the user acts as an admin.
        # client.force_authenticate(user=User(is_staff=True))
        # Focus is on invalid data, so title is set to an empty string. Entered title may not be null.
        response = create_collection({'title': ''})

        assert response.status_code == status.HTTP_400_BAD_REQUEST

        # An assertion for the expected error message. The data is a dictionary, so the title property can be accessed to search for. Basically title may not be None/Null.
        assert response.data['title'] is not None

    def test_if_data_is_valid_returns_201(self, authenticate, create_collection):
        authenticate(is_staff=True)

        response = create_collection({'title': 'a'})

        assert response.status_code == status.HTTP_201_CREATED
        # In the body of the request, the id of the new collection should be found. This value must be greater than 0, since the test if for valid data.
        assert response.data['id'] > 0


@pytest.mark.django_db  # To allow database access.
class TestRetrieveCollection:
    """Class for organizing the tests for when retrieving a collection.
    """

    def test_if_collection_exists_returns_200(self, api_client):
        # "baker" allows to avoid initializing individual properties of a model.
        collection = baker.make(Collection)

        # Sending a GET request at this endpoint, with the collection id. This creates a response.
        # Django automatically redirects by adding "/" at end of URL.
        response = api_client.get(f'/store/collections/{collection.id}/')

        # Making an assertion of the response. Testing if status code is OK.
        assert response.status_code == status.HTTP_200_OK
        # The collection object is in the body of the response. Since this data is a dictionary, each individual property can be accessed and compared like "response.data['id'] == collection.id"
        # The entire data object can also be compared with another dictionary, like below.
        assert response.data == {
            'id': collection.id,
            'title': collection.title,
            'products_count': 0
        }

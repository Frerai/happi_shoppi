import pytest
from model_bakery import baker
from rest_framework import status
from store.models import Product


@pytest.fixture
def create_product(api_client):
    def do_create_product(product):
        return api_client.post('/store/products/', product)
    return do_create_product


@pytest.mark.django_db
class TestCreateProduct:
    def test_if_user_is_anonymous_returns_401(self, create_product):

        response = create_product({"Product": "a"})

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from products.models import Category, Product


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def user(db):
    User = get_user_model()
    return User.objects.create_user(
        username="tester", email="tester@example.com", password="Test12345!"
    )


@pytest.fixture
def auth_client(api_client, user):
    # Obtain JWT token via API and set Authorization header
    resp = api_client.post(
        "/api/auth/token/",
        {"username": user.username, "password": "Test12345!"},
        format="json",
    )
    assert resp.status_code == 200, resp.content
    token = resp.data["access"]
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
    return api_client


@pytest.fixture
def category(db):
    return Category.objects.create(name="Electronics")


@pytest.fixture
def product(db, category):
    return Product.objects.create(
        title="Phone",
        description="Smart phone",
        price=499.99,
        category=category,
        stock=10,
    )

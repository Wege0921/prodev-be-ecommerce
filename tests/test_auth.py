import pytest
from django.contrib.auth import get_user_model


@pytest.mark.django_db
def test_register_and_token_and_me(api_client):
    # register
    payload = {
        "username": "u1",
        "password": "Test12345!",
        "password2": "Test12345!",
        "email": "u1@example.com",
        "first_name": "U",
        "last_name": "One",
    }
    r = api_client.post("/api/auth/register/", payload, format="json")
    assert r.status_code == 201, r.content

    # token
    t = api_client.post(
        "/api/auth/token/", {"username": "u1", "password": "Test12345!"}, format="json"
    )
    assert t.status_code == 200, t.content
    access = t.data["access"]

    # me
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")
    me = api_client.get("/api/auth/me/")
    assert me.status_code == 200
    assert me.data["username"] == "u1"

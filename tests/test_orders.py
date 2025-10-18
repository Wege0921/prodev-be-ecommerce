import pytest
from products.models import Product


@pytest.mark.django_db
def test_orders_success_decrements_stock(auth_client, product):
    # initial stock
    assert product.stock == 10

    payload = {
        "status": "PENDING",
        "items": [
            {"product_id": product.id, "quantity": 3},
        ],
    }
    r = auth_client.post("/api/orders/", payload, format="json")
    assert r.status_code in (200, 201), r.content

    # refresh and check stock decremented
    product.refresh_from_db()
    assert product.stock == 7


@pytest.mark.django_db
def test_orders_insufficient_stock_fails(auth_client, product):
    # attempt over-purchase
    payload = {
        "status": "PENDING",
        "items": [
            {"product_id": product.id, "quantity": 999},
        ],
    }
    r = auth_client.post("/api/orders/", payload, format="json")
    assert r.status_code == 400

    # ensure stock unchanged
    product.refresh_from_db()
    assert product.stock == 10

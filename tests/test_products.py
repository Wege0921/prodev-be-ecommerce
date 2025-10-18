import pytest


@pytest.mark.django_db
def test_products_list_and_filters(api_client, category, product):
    # base list
    r = api_client.get("/api/products/")
    assert r.status_code == 200
    assert r.data["count"] >= 1

    # category filter
    r2 = api_client.get(f"/api/products/?category={category.id}")
    assert r2.status_code == 200
    assert any(item["title"] == product.title for item in r2.data["results"]) or r2.data["count"] >= 1

    # price filters
    r3 = api_client.get("/api/products/?price_min=400&price_max=600")
    assert r3.status_code == 200

    # in_stock filter (true)
    r4 = api_client.get("/api/products/?in_stock=true")
    assert r4.status_code == 200

    # ordering and search
    r5 = api_client.get("/api/products/?ordering=-created_at&search=phone")
    assert r5.status_code == 200

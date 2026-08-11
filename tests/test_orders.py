def test_create_order_success(client, make_user, make_product):
    user = make_user()
    product = make_product(price=1000, stock=10)

    response = client.post(
        "/api/orders",
        json={"user_id": user["id"], "product_id": product["id"], "quantity": 2},
    )
    body = response.get_json()

    assert response.status_code == 201
    assert body["user_id"] == user["id"]
    assert body["product_id"] == product["id"]
    assert body["quantity"] == 2
    assert body["total_price"] == 2000
    assert body["status"] == "confirmed"

    product_response = client.get(f"/api/products/{product['id']}")
    assert product_response.get_json()["stock"] == 8


def test_create_order_invalid_user(client, make_product):
    product = make_product()
    response = client.post(
        "/api/orders", json={"user_id": 9999, "product_id": product["id"], "quantity": 1}
    )
    assert response.status_code == 404
    assert response.get_json() == {"error": "User not found"}


def test_create_order_invalid_product(client, make_user):
    user = make_user()
    response = client.post(
        "/api/orders", json={"user_id": user["id"], "product_id": 9999, "quantity": 1}
    )
    assert response.status_code == 404
    assert response.get_json() == {"error": "Product not found"}


def test_create_order_insufficient_stock(client, make_user, make_product):
    user = make_user()
    product = make_product(stock=1)

    response = client.post(
        "/api/orders",
        json={"user_id": user["id"], "product_id": product["id"], "quantity": 5},
    )
    assert response.status_code == 400
    assert "error" in response.get_json()

    product_response = client.get(f"/api/products/{product['id']}")
    assert product_response.get_json()["stock"] == 1


def test_create_order_invalid_quantity(client, make_user, make_product):
    user = make_user()
    product = make_product()

    response = client.post(
        "/api/orders",
        json={"user_id": user["id"], "product_id": product["id"], "quantity": 0},
    )
    assert response.status_code == 400


def test_get_orders_list(client, make_user, make_product):
    user = make_user()
    product = make_product(stock=10)
    client.post(
        "/api/orders",
        json={"user_id": user["id"], "product_id": product["id"], "quantity": 1},
    )

    response = client.get("/api/orders")
    assert response.status_code == 200
    assert len(response.get_json()) == 1


def test_get_order_by_id(client, make_user, make_product):
    user = make_user()
    product = make_product(stock=10)
    created = client.post(
        "/api/orders",
        json={"user_id": user["id"], "product_id": product["id"], "quantity": 1},
    ).get_json()

    response = client.get(f"/api/orders/{created['id']}")
    assert response.status_code == 200
    assert response.get_json()["id"] == created["id"]


def test_get_order_not_found(client):
    response = client.get("/api/orders/9999")
    assert response.status_code == 404
    assert response.get_json() == {"error": "Order not found"}

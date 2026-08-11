def test_create_product_success(client):
    response = client.post(
        "/api/products", json={"name": "Laptop", "price": 57800, "stock": 10}
    )
    body = response.get_json()

    assert response.status_code == 201
    assert body["name"] == "Laptop"
    assert body["price"] == 57800
    assert body["stock"] == 10


def test_create_product_missing_fields(client):
    response = client.post("/api/products", json={"name": "Laptop"})
    assert response.status_code == 400
    assert "error" in response.get_json()


def test_create_product_negative_price(client):
    response = client.post(
        "/api/products", json={"name": "Laptop", "price": -5, "stock": 10}
    )
    assert response.status_code == 400
    assert "error" in response.get_json()


def test_create_product_negative_stock(client):
    response = client.post(
        "/api/products", json={"name": "Laptop", "price": 100, "stock": -1}
    )
    assert response.status_code == 400
    assert "error" in response.get_json()


def test_get_products_list(client, make_product):
    make_product(name="Laptop")
    make_product(name="Mouse", price=500, stock=50)

    response = client.get("/api/products")
    assert response.status_code == 200
    assert len(response.get_json()) == 2


def test_get_product_by_id(client, make_product):
    created = make_product()
    response = client.get(f"/api/products/{created['id']}")
    assert response.status_code == 200
    assert response.get_json()["id"] == created["id"]


def test_get_product_not_found(client):
    response = client.get("/api/products/9999")
    assert response.status_code == 404
    assert response.get_json() == {"error": "Product not found"}

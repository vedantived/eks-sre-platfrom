def test_create_user_success(client):
    response = client.post(
        "/api/users", json={"name": "Nayan", "email": "nayan@example.com"}
    )
    body = response.get_json()

    assert response.status_code == 201
    assert body["name"] == "Nayan"
    assert body["email"] == "nayan@example.com"
    assert "id" in body
    assert "created_at" in body


def test_create_user_missing_name(client):
    response = client.post("/api/users", json={"email": "nayan@example.com"})
    assert response.status_code == 400
    assert "error" in response.get_json()


def test_create_user_invalid_email(client):
    response = client.post("/api/users", json={"name": "Nayan", "email": "not-an-email"})
    assert response.status_code == 400
    assert "error" in response.get_json()


def test_create_user_duplicate_email(client, make_user):
    make_user(email="dup@example.com")
    response = client.post(
        "/api/users", json={"name": "Someone Else", "email": "dup@example.com"}
    )
    assert response.status_code == 409
    assert "error" in response.get_json()


def test_get_users_list(client, make_user):
    make_user(name="A", email="a@example.com")
    make_user(name="B", email="b@example.com")

    response = client.get("/api/users")
    assert response.status_code == 200
    body = response.get_json()
    assert len(body) == 2


def test_get_user_by_id(client, make_user):
    created = make_user()
    response = client.get(f"/api/users/{created['id']}")
    assert response.status_code == 200
    assert response.get_json()["id"] == created["id"]


def test_get_user_not_found(client):
    response = client.get("/api/users/9999")
    assert response.status_code == 404
    assert response.get_json() == {"error": "User not found"}

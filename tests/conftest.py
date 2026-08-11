"""Shared pytest fixtures.

Tests run against an isolated in-memory SQLite database (TestConfig) so
they never touch the developer's local sre_demo.db file.
"""
import pytest

from app import create_app
from app.config import TestConfig
from app.extensions import db as _db


@pytest.fixture()
def app():
    application = create_app(TestConfig)

    with application.app_context():
        yield application
        _db.session.remove()
        _db.drop_all()


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def make_user(client):
    def _make_user(name="Nayan", email="nayan@example.com"):
        response = client.post("/api/users", json={"name": name, "email": email})
        assert response.status_code == 201
        return response.get_json()

    return _make_user


@pytest.fixture()
def make_product(client):
    def _make_product(name="Laptop", price=57800, stock=10):
        response = client.post(
            "/api/products", json={"name": name, "price": price, "stock": stock}
        )
        assert response.status_code == 201
        return response.get_json()

    return _make_product

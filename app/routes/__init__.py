"""Blueprint registration for the application."""
from flask import Flask

from app.routes.health import health_bp
from app.routes.orders import orders_bp
from app.routes.products import products_bp
from app.routes.users import users_bp


def register_routes(app: Flask) -> None:
    app.register_blueprint(health_bp)
    app.register_blueprint(users_bp)
    app.register_blueprint(products_bp)
    app.register_blueprint(orders_bp)

"""Product endpoints."""
import logging

from flask import Blueprint, jsonify, request

from app.error_handlers import NotFoundError
from app.extensions import db
from app.models import Product
from app.validation import (
    require_json_object,
    require_non_negative_int,
    require_positive_number,
    require_string,
)

logger = logging.getLogger(__name__)

products_bp = Blueprint("products", __name__, url_prefix="/api/products")


@products_bp.route("", methods=["POST"])
def create_product():
    payload = require_json_object(request.get_json(silent=True))
    name = require_string(payload, "name")
    price = require_positive_number(payload, "price")
    stock = require_non_negative_int(payload, "stock")

    product = Product(name=name, price=price, stock=stock)
    db.session.add(product)
    db.session.commit()
    logger.info("Created product id=%s name=%s", product.id, product.name)

    return jsonify(product.to_dict()), 201


@products_bp.route("", methods=["GET"])
def list_products():
    products = Product.query.order_by(Product.id).all()
    return jsonify([product.to_dict() for product in products]), 200


@products_bp.route("/<int:product_id>", methods=["GET"])
def get_product(product_id: int):
    product = db.session.get(Product, product_id)
    if product is None:
        raise NotFoundError("Product not found")
    return jsonify(product.to_dict()), 200

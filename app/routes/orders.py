"""Order endpoints."""
import logging

from flask import Blueprint, jsonify, request

from app.error_handlers import NotFoundError
from app.extensions import db
from app.models import Order
from app.services.order_service import create_order
from app.validation import require_json_object, require_positive_int

logger = logging.getLogger(__name__)

orders_bp = Blueprint("orders", __name__, url_prefix="/api/orders")


@orders_bp.route("", methods=["POST"])
def create_order_route():
    payload = require_json_object(request.get_json(silent=True))
    user_id = require_positive_int(payload, "user_id")
    product_id = require_positive_int(payload, "product_id")
    quantity = require_positive_int(payload, "quantity")

    order = create_order(user_id=user_id, product_id=product_id, quantity=quantity)
    logger.info(
        "Created order",
        extra={
            "order_id": order.id,
            "user_id": order.user_id,
            "product_id": order.product_id,
            "quantity": order.quantity,
        },
    )

    return jsonify(order.to_dict()), 201


@orders_bp.route("", methods=["GET"])
def list_orders():
    orders = Order.query.order_by(Order.id).all()
    return jsonify([order.to_dict() for order in orders]), 200


@orders_bp.route("/<int:order_id>", methods=["GET"])
def get_order(order_id: int):
    order = db.session.get(Order, order_id)
    if order is None:
        raise NotFoundError("Order not found")
    return jsonify(order.to_dict()), 200

"""Business logic for order creation.

Kept out of the route layer so the transactional rules (stock checks,
stock deduction, commit/rollback) live in one place and can be unit
tested independently of HTTP concerns.
"""
import logging

from app.error_handlers import NotFoundError, ValidationError
from app.extensions import db
from app.models import Order, Product, User

logger = logging.getLogger(__name__)


def create_order(user_id: int, product_id: int, quantity: int) -> Order:
    """Validate stock/existence, then atomically create an order and deduct stock.

    Raises NotFoundError if the user or product does not exist, and
    ValidationError if there is insufficient stock. On any unexpected
    failure the transaction is rolled back before the exception propagates.
    """
    user = db.session.get(User, user_id)
    if user is None:
        raise NotFoundError("User not found")

    product = db.session.get(Product, product_id)
    if product is None:
        raise NotFoundError("Product not found")

    if product.stock < quantity:
        raise ValidationError(
            f"Insufficient stock for product '{product.name}': "
            f"requested {quantity}, available {product.stock}"
        )

    try:
        total_price = product.price * quantity
        product.stock -= quantity

        order = Order(
            user_id=user.id,
            product_id=product.id,
            quantity=quantity,
            total_price=total_price,
        )
        db.session.add(order)
        db.session.commit()
        return order
    except Exception:
        db.session.rollback()
        logger.exception(
            "Failed to create order for user_id=%s product_id=%s", user_id, product_id
        )
        raise

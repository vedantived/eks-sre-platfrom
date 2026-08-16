"""User endpoints."""
import logging

from flask import Blueprint, jsonify, request

from app.error_handlers import ConflictError, NotFoundError
from app.extensions import db
from app.models import User
from app.validation import require_email, require_json_object, require_string

logger = logging.getLogger(__name__)

users_bp = Blueprint("users", __name__, url_prefix="/api/users")


@users_bp.route("", methods=["POST"])
def create_user():
    payload = require_json_object(request.get_json(silent=True))
    name = require_string(payload, "name")
    email = require_email(payload)

    if User.query.filter_by(email=email).first() is not None:
        raise ConflictError(f"A user with email '{email}' already exists")

    user = User(name=name, email=email)
    db.session.add(user)
    db.session.commit()
    logger.info("Created user", extra={"user_id": user.id, "email": user.email})

    return jsonify(user.to_dict()), 201


@users_bp.route("", methods=["GET"])
def list_users():
    users = User.query.order_by(User.id).all()
    return jsonify([user.to_dict() for user in users]), 200


@users_bp.route("/<int:user_id>", methods=["GET"])
def get_user(user_id: int):
    user = db.session.get(User, user_id)
    if user is None:
        raise NotFoundError("User not found")
    return jsonify(user.to_dict()), 200

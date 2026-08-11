"""Shared request-body validation helpers used by the route modules."""
import re

from app.error_handlers import ValidationError

EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def require_json_object(payload) -> dict:
    """Ensure the parsed request body is a JSON object."""
    if payload is None or not isinstance(payload, dict):
        raise ValidationError("Request body must be a JSON object")
    return payload


def require_string(payload: dict, field: str) -> str:
    value = payload.get(field)
    if not isinstance(value, str) or not value.strip():
        raise ValidationError(f"'{field}' is required and must be a non-empty string")
    return value.strip()


def require_email(payload: dict, field: str = "email") -> str:
    value = require_string(payload, field)
    if not EMAIL_PATTERN.match(value):
        raise ValidationError(f"'{field}' must be a valid email address")
    return value


def require_positive_number(payload: dict, field: str) -> float:
    value = payload.get(field)
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValidationError(f"'{field}' is required and must be a number")
    if value <= 0:
        raise ValidationError(f"'{field}' must be greater than zero")
    return value


def require_positive_int(payload: dict, field: str) -> int:
    value = payload.get(field)
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValidationError(f"'{field}' is required and must be an integer")
    if value <= 0:
        raise ValidationError(f"'{field}' must be greater than zero")
    return value


def require_non_negative_int(payload: dict, field: str) -> int:
    value = payload.get(field)
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValidationError(f"'{field}' is required and must be an integer")
    if value < 0:
        raise ValidationError(f"'{field}' must be zero or greater")
    return value

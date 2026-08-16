"""Centralized error handling.

Defines the applications typed exceptions and registers JSON error
handlers on the Flask app so every error path returns a consistent,
client-safe JSON body instead of an HTML error page or a stack trace.
"""
import logging

from flask import Flask, jsonify, request
from werkzeug.exceptions import HTTPException

logger = logging.getLogger(__name__)


class ApiError(Exception):
    """Base class for expected, client-facing API errors."""

    status_code = 500

    def __init__(self, message: str):
        super().__init__(message)
        self.message = message


class ValidationError(ApiError):
    """Request body/params failed validation. Maps to HTTP 400."""

    status_code = 400


class NotFoundError(ApiError):
    """Requested resource does not exist. Maps to HTTP 404."""

    status_code = 404


class ConflictError(ApiError):
    """Request conflicts with existing state (e.g. duplicate email). Maps to HTTP 409."""

    status_code = 409


def register_error_handlers(app: Flask) -> None:
    """Attach JSON error handlers to the given Flask app."""

    @app.errorhandler(ApiError)
    def handle_api_error(error: ApiError):
        return jsonify({"error": error.message}), error.status_code

    @app.errorhandler(HTTPException)
    def handle_http_exception(error: HTTPException):
        return jsonify({"error": error.description}), error.code

    @app.errorhandler(Exception)
    def handle_unexpected_exception(error: Exception):
        logger.exception(
            "Unhandled exception while processing request",
            extra={"method": request.method, "path": request.path},
        )
        return jsonify({"error": "Internal server error"}), 500

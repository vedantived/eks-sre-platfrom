"""Application factory for the SRE Demo API."""
import logging
import time

from flask import Flask, g, request

from app.config import Config
from app.error_handlers import register_error_handlers
from app.extensions import db
from app.routes import register_routes

logger = logging.getLogger(__name__)


def configure_logging() -> None:
    """Configure a clean, structured log format suitable for later
    collection by a log shipper (e.g. Fluent Bit) without further changes.
    """
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )


def create_app(config_object=Config) -> Flask:
    configure_logging()

    app = Flask(__name__)
    app.config.from_object(config_object)

    db.init_app(app)
    register_error_handlers(app)
    register_routes(app)

    with app.app_context():
        from app import models  # noqa: F401  ensure models are registered

        db.create_all()

    @app.before_request
    def log_request_start():
        g.request_start_time = time.monotonic()
        logger.info("Incoming request method=%s path=%s", request.method, request.path)

    @app.after_request
    def log_request_end(response):
        duration_ms = (time.monotonic() - g.get("request_start_time", time.monotonic())) * 1000
        logger.info(
            "Completed request method=%s path=%s status=%s duration_ms=%.2f",
            request.method,
            request.path,
            response.status_code,
            duration_ms,
        )
        return response

    logger.info("SRE Demo API startup complete (env=%s)", app.config.get("FLASK_ENV"))

    return app

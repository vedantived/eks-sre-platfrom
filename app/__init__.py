"""Application factory for the SRE Demo API."""
import logging
import time

from flask import Flask, g, request

from app.config import Config
from app.error_handlers import register_error_handlers
from app.extensions import db
from app.logging_utils import configure_logging
from app.middleware import register_request_id_middleware
from app.routes import register_routes

logger = logging.getLogger(__name__)


def create_app(config_object=Config) -> Flask:
    configure_logging()

    app = Flask(__name__)
    app.config.from_object(config_object)

    db.init_app(app)
    register_error_handlers(app)
    register_routes(app)
    register_request_id_middleware(app)

    with app.app_context():
        from app import models  # noqa: F401  ensure models are registered

        db.create_all()

    @app.before_request
    def log_request_start():
        g.request_start_time = time.monotonic()
        logger.info(
            "Incoming request",
            extra={"method": request.method, "path": request.path},
        )

    @app.after_request
    def log_request_end(response):
        duration_ms = (time.monotonic() - g.get("request_start_time", time.monotonic())) * 1000
        logger.info(
            "Completed request",
            extra={
                "method": request.method,
                "path": request.path,
                "status": response.status_code,
                "duration_ms": round(duration_ms, 2),
            },
        )
        return response

    logger.info("SRE Demo API startup complete", extra={"env": app.config.get("FLASK_ENV")})

    return app

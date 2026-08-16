"""JSON log formatting and request-id correlation.

Every log line is emitted as a single JSON object, with a request_id
field automatically stamped onto any record produced while handling an
HTTP request (see app/middleware.py for where that id comes from). This
lets log lines shipped to a centralized store (e.g. Fluent Bit -> ELK)
be filtered per-request, regardless of how many pods or interleaved
requests are writing to the stream at once.
"""
import json
import logging
from datetime import datetime, timezone

from flask import g

REQUEST_ID_HEADER = "X-Request-ID"

_STANDARD_LOG_RECORD_ATTRS = set(logging.LogRecord("", 0, "", 0, "", (), None).__dict__.keys())


class RequestIdFilter(logging.Filter):
    """Stamps the current requests id onto every log record it touches."""

    def filter(self, record: logging.LogRecord) -> bool:
        try:
            record.request_id = getattr(g, "request_id", "-")
        except RuntimeError:
            record.request_id = "-"
        return True


class JsonFormatter(logging.Formatter):
    """Renders each log record as a single-line JSON object."""

    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "timestamp": datetime.fromtimestamp(record.created, tz=timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "request_id": getattr(record, "request_id", "-"),
        }

        for key, value in record.__dict__.items():
            if key not in _STANDARD_LOG_RECORD_ATTRS and key != "request_id":
                payload[key] = value

        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)

        return json.dumps(payload)


def configure_logging() -> None:
    """Configure root logging to emit structured JSON, correlated by request id."""
    handler = logging.StreamHandler()
    handler.setFormatter(JsonFormatter())
    handler.addFilter(RequestIdFilter())

    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    root_logger.addHandler(handler)
    root_logger.setLevel(logging.INFO)

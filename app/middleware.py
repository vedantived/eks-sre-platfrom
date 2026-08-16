"""Request-scoped middleware: correlates every request with a unique id.

If the caller supplies an X-Request-ID header, it is honored (useful when
a proxy or another service upstream already assigned one). Otherwise a
new id is generated. Either way, the id is echoed back on the response
and stamped onto every log line produced while handling the request
(see app/logging_utils.py).
"""
import uuid

from flask import Flask, g, request

from app.logging_utils import REQUEST_ID_HEADER


def register_request_id_middleware(app: Flask) -> None:
    @app.before_request
    def assign_request_id():
        g.request_id = request.headers.get(REQUEST_ID_HEADER) or uuid.uuid4().hex[:12]

    @app.after_request
    def attach_request_id_header(response):
        response.headers[REQUEST_ID_HEADER] = getattr(g, "request_id", "-")
        return response

"""Liveness and readiness endpoints.

Kept separate on purpose: Kubernetes will later wire these to distinct
probes (livenessProbe vs readinessProbe) with different failure semantics.
"""
import logging

from flask import Blueprint, jsonify
from sqlalchemy import text

from app.extensions import db

logger = logging.getLogger(__name__)

health_bp = Blueprint("health", __name__)


@health_bp.route("/health", methods=["GET"])
def health():
    """Lightweight liveness check. Does not touch the database."""
    return jsonify({"status": "healthy"}), 200


@health_bp.route("/ready", methods=["GET"])
def ready():
    """Readiness check. Verifies the application can reach the database."""
    try:
        db.session.execute(text("SELECT 1"))
        return jsonify({"status": "ready"}), 200
    except Exception:
        logger.exception("Readiness check failed: database unreachable")
        return jsonify({"status": "not ready", "error": "database unavailable"}), 503

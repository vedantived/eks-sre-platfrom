"""Shared Flask extension instances.

Kept in their own module (separate from app/__init__.py) so that models and
routes can import `db` without triggering circular imports.
"""
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

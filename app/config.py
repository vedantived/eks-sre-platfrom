"""Application configuration loaded from environment variables."""
import os


class Config:
    """Base configuration shared by all environments."""

    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL", "sqlite:///sre_demo.db"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    FLASK_ENV = os.environ.get("FLASK_ENV", "development")


class TestConfig(Config):
    """Configuration used by the pytest suite. Isolated in-memory database."""

    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "TEST_DATABASE_URL", "sqlite:///:memory:"
    )
    TESTING = True

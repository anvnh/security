"""Application configuration module using pathlib for cross-platform support."""

from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent
INSTANCE_DIR = BASE_DIR / "instance"
DATABASE_PATH = INSTANCE_DIR / "app.db"
SCHEMA_PATH = Path(__file__).resolve().parent / "schema.sql"
SEED_PATH = Path(__file__).resolve().parent / "seed.sql"


class Config:
    """Base application configuration."""

    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key-change-in-production")
    DATABASE = DATABASE_PATH
    SESSION_COOKIE_HTTPONLY = True
    BLOG_PORT = int(os.environ.get("BLOG_PORT", 5000))
    LAB_PORT = int(os.environ.get("LAB_PORT", 5001))


class TestConfig(Config):
    """Testing configuration."""

    TESTING = True
    SECRET_KEY = "test-secret-key"
    DATABASE = ":memory:"

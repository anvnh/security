"""Pytest fixtures and configuration."""

import pytest
import sqlite3
from app import create_app
from app.config import TestConfig, SCHEMA_PATH, SEED_PATH
from app.db import execute_sql_file


@pytest.fixture
def db_config(tmp_path):
    """Create and seed a shared temporary SQLite database configuration."""
    db_file = tmp_path / "test.db"

    class CustomTestConfig(TestConfig):
        DATABASE = db_file

    conn = sqlite3.connect(str(db_file))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    execute_sql_file(conn, SCHEMA_PATH)
    execute_sql_file(conn, SEED_PATH)
    conn.commit()
    conn.close()

    return CustomTestConfig


@pytest.fixture
def app(db_config):
    """Combined application instance for CLI tests."""
    return create_app(db_config, role="full")


@pytest.fixture
def blog_app(db_config):
    """User-facing blog application (:5000 role)."""
    return create_app(db_config, role="blog")


@pytest.fixture
def lab_app(db_config):
    """Lab guide and attacker C2 application (:5001 role)."""
    return create_app(db_config, role="lab")


@pytest.fixture
def client(app):
    """A test client for the combined app."""
    return app.test_client()


@pytest.fixture
def blog_client(blog_app):
    """A test client for the pure user blog (:5000)."""
    return blog_app.test_client()


@pytest.fixture
def lab_client(lab_app):
    """A test client for the lab guide and attacker server (:5001)."""
    return lab_app.test_client()


@pytest.fixture
def runner(app):
    """A test CLI runner for the app."""
    return app.test_cli_runner()

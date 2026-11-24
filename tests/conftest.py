"""Pytest fixtures and configuration."""

import pytest
import sqlite3
from app import create_app
from app.config import TestConfig, SCHEMA_PATH, SEED_PATH
from app.db import execute_sql_file


@pytest.fixture
def app(tmp_path):
    """Create and configure a clean test application with a temporary database."""
    db_file = tmp_path / "test.db"

    class CustomTestConfig(TestConfig):
        DATABASE = db_file

    # Seed the temporary database
    conn = sqlite3.connect(str(db_file))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    execute_sql_file(conn, SCHEMA_PATH)
    execute_sql_file(conn, SEED_PATH)
    conn.commit()
    conn.close()

    app_instance = create_app(CustomTestConfig)
    yield app_instance


@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()


@pytest.fixture
def runner(app):
    """A test CLI runner for the app."""
    return app.test_cli_runner()

"""Database management module using standard sqlite3 and pathlib."""

import sqlite3
import sys
from pathlib import Path
from flask import current_app, g
from flask.cli import with_appcontext
import click

from app.config import DATABASE_PATH, INSTANCE_DIR, SCHEMA_PATH, SEED_PATH


def get_db(db_path=None):
    """Open a new database connection if there is none yet for the current app context."""
    if "db" not in g:
        target_path = db_path or current_app.config["DATABASE"]
        
        # If target path is a string (e.g., ':memory:') or Path
        if isinstance(target_path, Path):
            target_path.parent.mkdir(parents=True, exist_ok=True)
            conn_target = str(target_path)
        else:
            conn_target = target_path

        g.db = sqlite3.connect(conn_target, timeout=10.0)
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON;")
    return g.db


def close_db(e=None):
    """Close the database connection if open."""
    db = g.pop("db", None)
    if db is not None:
        db.close()


def execute_sql_file(conn, file_path: Path):
    """Read and execute a SQL script file."""
    with open(file_path, "r", encoding="utf-8") as f:
        conn.executescript(f.read())


def init_db(db_path: Path = DATABASE_PATH):
    """Initialize schema and seed initial predictable demonstration data."""
    if isinstance(db_path, Path):
        db_path.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(str(db_path))
    else:
        conn = sqlite3.connect(db_path)

    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    try:
        execute_sql_file(conn, SCHEMA_PATH)
        execute_sql_file(conn, SEED_PATH)
        conn.commit()
    finally:
        conn.close()


def reset_db(db_path: Path = DATABASE_PATH):
    """Reset database to predictable initial demonstration state."""
    init_db(db_path)


@click.command("init-db")
@with_appcontext
def init_db_command():
    """Clear existing data and create new tables with demo seed."""
    init_db(current_app.config["DATABASE"])
    click.echo("Initialized and seeded the database.")


@click.command("reset-db")
@with_appcontext
def reset_db_command():
    """Reset the database to initial demonstration state."""
    reset_db(current_app.config["DATABASE"])
    click.echo("Reset database to initial demonstration state.")


def init_app(app):
    """Register database functions and CLI commands with the Flask app."""
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
    app.cli.add_command(reset_db_command)


if __name__ == "__main__":
    action = sys.argv[1] if len(sys.argv) > 1 else "init"
    INSTANCE_DIR.mkdir(parents=True, exist_ok=True)
    if action in ("init", "reset"):
        reset_db(DATABASE_PATH)
        print(f"Database successfully {action}ed at {DATABASE_PATH}")
    else:
        print(f"Unknown action: {action}. Use 'init' or 'reset'.")

"""Global security mode management (SQLite-backed) and password hashing."""

import sqlite3
from flask import session
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError, VerificationError, InvalidHashError
from app.db import get_db

MODE_SECURE = "secure"
MODE_VULNERABLE = "vulnerable"
DEFAULT_MODE = MODE_SECURE

# Argon2id password hasher (active in both modes)
_hasher = PasswordHasher()


def get_security_mode() -> str:
    """Return global security mode from SQLite, defaulting to SECURE."""
    try:
        db = get_db()
        row = db.execute(
            "SELECT value FROM lab_settings WHERE key = 'security_mode'"
        ).fetchone()
        if row and row["value"] in (MODE_SECURE, MODE_VULNERABLE):
            return row["value"]
    except sqlite3.OperationalError:
        pass
    return DEFAULT_MODE


def set_security_mode(mode: str) -> str:
    """Validate and persist global security mode in SQLite."""
    if mode not in (MODE_SECURE, MODE_VULNERABLE):
        raise ValueError(f"Invalid security mode: {mode}")
    db = get_db()
    db.execute(
        "INSERT INTO lab_settings (key, value) VALUES ('security_mode', ?) "
        "ON CONFLICT(key) DO UPDATE SET value = excluded.value",
        (mode,),
    )
    db.commit()
    return mode


def is_secure_mode() -> bool:
    """Check if the application is currently in Secure Mode."""
    return get_security_mode() == MODE_SECURE


def is_vulnerable_mode() -> bool:
    """Check if the application is currently in Vulnerable Mode."""
    return get_security_mode() == MODE_VULNERABLE


def hash_password(password: str) -> str:
    """Hash password using Argon2id."""
    return _hasher.hash(password)


def verify_password(hash_value: str, password: str) -> bool:
    """Verify password against Argon2id hash."""
    try:
        return _hasher.verify(hash_value, password)
    except (VerifyMismatchError, VerificationError, InvalidHashError):
        return False


def login_user(user_id: int):
    """Log in user with a fresh session."""
    session.clear()
    session["user_id"] = user_id


def logout_user():
    """Clear current user session."""
    session.clear()

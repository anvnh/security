"""Security mode management and password hashing."""

from flask import session
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError, VerificationError, InvalidHashError

MODE_SECURE = "secure"
MODE_VULNERABLE = "vulnerable"
DEFAULT_MODE = MODE_SECURE

# Argon2id password hasher (active in both modes)
_hasher = PasswordHasher()


def get_security_mode() -> str:
    """Return current security mode for the session, defaulting to SECURE."""
    mode = session.get("security_mode")
    if mode not in (MODE_SECURE, MODE_VULNERABLE):
        mode = DEFAULT_MODE
        session["security_mode"] = mode
    return mode


def set_security_mode(mode: str) -> str:
    """Validate and update the security mode in the session."""
    if mode not in (MODE_SECURE, MODE_VULNERABLE):
        raise ValueError(f"Invalid security mode: {mode}")
    session["security_mode"] = mode
    return mode


def is_secure_mode() -> bool:
    """Check if the current session is in Secure Mode."""
    return get_security_mode() == MODE_SECURE


def is_vulnerable_mode() -> bool:
    """Check if the current session is in Vulnerable Mode."""
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
    """Log in user while preserving security mode across auth transition."""
    current_mode = get_security_mode()
    session.clear()
    session["user_id"] = user_id
    session["security_mode"] = current_mode


def logout_user():
    """Log out user while preserving security mode across auth transition."""
    current_mode = get_security_mode()
    session.clear()
    session["security_mode"] = current_mode

"""Tests for security mode management, persistence, and session isolation."""

from flask import session
from app.security import MODE_SECURE, MODE_VULNERABLE


def test_default_security_mode_is_secure(client):
    """Application defaults to Secure Mode for all new sessions."""
    res = client.get("/")
    assert res.status_code == 200
    assert b"Secure Mode" in res.data
    assert b"Vulnerable Mode" not in res.data


def test_toggle_security_mode_endpoint(client):
    """Security mode toggle switches state between Secure and Vulnerable."""
    # Switch to vulnerable mode
    res = client.post(
        "/security/toggle",
        data={"mode": MODE_VULNERABLE},
        follow_redirects=True,
    )
    assert res.status_code == 200
    assert b"Vulnerable Mode" in res.data

    # Switch back to secure mode
    res = client.post(
        "/security/toggle",
        data={"mode": MODE_SECURE},
        follow_redirects=True,
    )
    assert res.status_code == 200
    assert b"Secure Mode" in res.data


def test_security_mode_preserved_across_login_and_logout(client):
    """Switching mode must persist across login and logout authentication transitions."""
    # Switch to Vulnerable Mode
    client.post(
        "/security/toggle",
        data={"mode": MODE_VULNERABLE},
        follow_redirects=True,
    )

    # Log in as alice
    client.post(
        "/login",
        data={"username": "alice", "password": "alice123"},
        follow_redirects=True,
    )

    # Verify session remains in Vulnerable Mode after login
    with client.session_transaction() as sess:
        assert sess.get("security_mode") == MODE_VULNERABLE
        assert sess.get("user_id") is not None

    # Log out
    client.post("/logout", follow_redirects=True)

    # Verify session remains in Vulnerable Mode after logout
    with client.session_transaction() as sess:
        assert sess.get("security_mode") == MODE_VULNERABLE
        assert sess.get("user_id") is None


def test_security_mode_session_isolation(app):
    """Different client sessions maintain completely independent security modes."""
    client_a = app.test_client()
    client_b = app.test_client()

    # Client A toggles to vulnerable mode
    client_a.post(
        "/security/toggle",
        data={"mode": MODE_VULNERABLE},
        follow_redirects=True,
    )

    with client_a.session_transaction() as sess_a:
        assert sess_a.get("security_mode") == MODE_VULNERABLE

    # Client B should still default to secure mode
    client_b.get("/")
    with client_b.session_transaction() as sess_b:
        assert sess_b.get("security_mode") == MODE_SECURE

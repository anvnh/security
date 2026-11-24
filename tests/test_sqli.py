"""Tests for SQL Injection Full Attack Chain (Search Data Exfiltration & Login Authentication Bypass)."""

from app.security import MODE_SECURE, MODE_VULNERABLE


# --- Phase 1: Search Data Exfiltration Tests ---

def test_sqli_search_data_exfiltration_in_vulnerable_mode(client):
    """In Vulnerable Mode, SQLi in search dumps the users table into the blog feed."""
    with client.session_transaction() as sess:
        sess["security_mode"] = MODE_VULNERABLE

    payload = "' UNION SELECT id, username, password_hash, bio, created_at, 'admin' FROM users --"
    res = client.get(f"/?q={payload}")

    assert res.status_code == 200
    assert b"$argon2id$" in res.data
    assert b"alice" in res.data
    assert b"bob" in res.data


def test_sqli_search_prevented_in_secure_mode(client):
    """In Secure Mode, parameterized queries treat search input as literal text."""
    with client.session_transaction() as sess:
        sess["security_mode"] = MODE_SECURE

    payload = "' UNION SELECT id, username, password_hash, bio, created_at, 'admin' FROM users --"
    res = client.get(f"/?q={payload}")

    assert res.status_code == 200
    assert b"$argon2id$" not in res.data
    assert b"No posts matched your search query" in res.data


# --- Phase 2: Login Authentication Bypass Tests ---

def test_sqli_auth_bypass_via_union_in_vulnerable_mode(client):
    """In Vulnerable Mode, an attacker logs in as admin dynamically via subquery UNION."""
    with client.session_transaction() as sess:
        sess["security_mode"] = MODE_VULNERABLE

    payload = "' UNION SELECT (SELECT id FROM users WHERE username = 'admin'), 'admin', password_hash FROM users WHERE username = 'alice' --"
    res = client.post(
        "/login",
        data={"username": payload, "password": "alice123"},
        follow_redirects=True,
    )
    assert res.status_code == 200
    assert b"Logged in successfully as admin." in res.data
    assert b"@admin" in res.data

    with client.session_transaction() as sess:
        assert sess.get("user_id") == 1


def test_sqli_auth_bypass_prevented_in_secure_mode(client):
    """In Secure Mode, parameterized queries treat injection payloads as literal strings."""
    with client.session_transaction() as sess:
        sess["security_mode"] = MODE_SECURE

    payload = "' UNION SELECT (SELECT id FROM users WHERE username = 'admin'), 'admin', password_hash FROM users WHERE username = 'alice' --"
    res = client.post(
        "/login",
        data={"username": payload, "password": "alice123"},
        follow_redirects=True,
    )
    assert res.status_code == 401
    assert b"Invalid username or password." in res.data
    assert b"@admin" not in res.data

    with client.session_transaction() as sess:
        assert sess.get("user_id") is None


def test_legitimate_login_works_in_both_modes(client):
    """Legitimate users with valid Argon2id credentials can log in in both modes."""
    # Vulnerable Mode
    with client.session_transaction() as sess:
        sess["security_mode"] = MODE_VULNERABLE

    res_vuln = client.post(
        "/login",
        data={"username": "alice", "password": "alice123"},
        follow_redirects=True,
    )
    assert res_vuln.status_code == 200
    assert b"@alice" in res_vuln.data

    client.post("/logout", follow_redirects=True)

    # Secure Mode
    with client.session_transaction() as sess:
        sess["security_mode"] = MODE_SECURE

    res_sec = client.post(
        "/login",
        data={"username": "alice", "password": "alice123"},
        follow_redirects=True,
    )
    assert res_sec.status_code == 200
    assert b"@alice" in res_sec.data

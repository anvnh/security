"""Tests for global SQLite security mode management and :5000 / :5001 server separation."""

from app.security import MODE_SECURE, MODE_VULNERABLE, get_security_mode


def test_default_security_mode_is_secure(lab_client, blog_app):
    """Application defaults to Secure Mode and blog pages do not expose the toggle widget."""
    lab_res = lab_client.get("/lab/guide")
    assert lab_res.status_code == 200
    assert b"Secure Mode (ON)" in lab_res.data

    blog_res = blog_app.test_client().get("/")
    assert blog_res.status_code == 200
    assert b"securityToggleWidget" not in blog_res.data
    assert b"/security/toggle" not in blog_res.data

    with blog_app.app_context():
        assert get_security_mode() == MODE_SECURE


def test_blog_server_does_not_expose_lab_or_toggle(blog_client):
    """The pure user blog (:5000) does not expose lab routes or security toggle."""
    assert blog_client.get("/lab/guide").status_code == 404
    assert blog_client.get("/lab/attacker").status_code == 404
    assert blog_client.post("/security/toggle", data={"mode": MODE_VULNERABLE}).status_code == 404


def test_only_guide_has_security_toggle_not_attacker(lab_client):
    """On :5001, only /lab/guide has the toggle; /lab/attacker has no toggle controls."""
    root_res = lab_client.get("/", follow_redirects=False)
    assert root_res.status_code == 302
    assert "/lab/guide" in root_res.headers["Location"]

    guide_res = lab_client.get("/lab/guide")
    assert guide_res.status_code == 200
    assert b"/security/toggle" in guide_res.data
    assert b"Secure Mode (ON)" in guide_res.data

    attacker_res = lab_client.get("/lab/attacker")
    assert attacker_res.status_code == 200
    assert b"/security/toggle" not in attacker_res.data
    assert b"Secure Mode" not in attacker_res.data
    assert b"Vulnerable Mode" not in attacker_res.data


def test_global_security_mode_syncs_across_clients(lab_client, blog_app):
    """Toggling mode on :5001/lab/guide syncs globally to all :5000 clients."""
    toggle_vuln = lab_client.post(
        "/security/toggle",
        data={"mode": MODE_VULNERABLE},
        follow_redirects=True,
    )
    assert toggle_vuln.status_code == 200
    assert b"Secure Mode (OFF)" in toggle_vuln.data

    with blog_app.app_context():
        assert get_security_mode() == MODE_VULNERABLE

    # Independent :5000 clients immediately observe Vulnerable Mode
    client_a = blog_app.test_client()
    client_b = blog_app.test_client()
    payload = "' UNION SELECT id, username, password_hash, bio, created_at, 'admin' FROM users --"
    assert b"$argon2id$" in client_a.get(f"/?q={payload}").data
    assert b"$argon2id$" in client_b.get(f"/?q={payload}").data

    # Switch back to Secure Mode on :5001
    toggle_sec = lab_client.post(
        "/security/toggle",
        data={"mode": MODE_SECURE},
        follow_redirects=True,
    )
    assert toggle_sec.status_code == 200
    assert b"Secure Mode (ON)" in toggle_sec.data

    with blog_app.app_context():
        assert get_security_mode() == MODE_SECURE

    assert b"$argon2id$" not in client_a.get(f"/?q={payload}").data


def test_security_mode_preserved_across_login_and_logout(lab_client, blog_client, blog_app):
    """Global security mode persists across login and logout transitions on :5000."""
    lab_client.post(
        "/security/toggle",
        data={"mode": MODE_VULNERABLE},
        follow_redirects=True,
    )

    blog_client.post(
        "/login",
        data={"username": "alice", "password": "alice123"},
        follow_redirects=True,
    )
    with blog_app.app_context():
        assert get_security_mode() == MODE_VULNERABLE

    blog_client.post("/logout", follow_redirects=True)
    with blog_app.app_context():
        assert get_security_mode() == MODE_VULNERABLE

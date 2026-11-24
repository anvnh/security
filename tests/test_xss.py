"""Tests for Stored XSS vulnerability in Vulnerable Mode vs Context-Aware Output Encoding in Secure Mode."""

from app.security import MODE_SECURE, MODE_VULNERABLE


def _login_alice(client):
    """Authenticate as demo user alice while preserving current session security mode."""
    client.post(
        "/login",
        data={"username": "alice", "password": "alice123"},
        follow_redirects=True,
    )


def test_xss_in_secure_mode(client):
    """In Secure Mode, user comment content is safely escaped by Jinja2."""
    with client.session_transaction() as sess:
        sess["security_mode"] = MODE_SECURE
    _login_alice(client)

    payload = "<script>alert('SECURE_TEST_XSS')</script>"
    client.post(
        "/posts/1/comments",
        data={"content": payload},
        follow_redirects=True,
    )

    view_res = client.get("/posts/1")
    assert view_res.status_code == 200
    # Encoded output: HTML entities are used, raw script tags are NOT rendered
    assert b"&lt;script&gt;alert(&#39;SECURE_TEST_XSS&#39;)&lt;/script&gt;" in view_res.data or \
           b"&lt;script&gt;alert('SECURE_TEST_XSS')&lt;/script&gt;" in view_res.data
    assert b"<script>alert('SECURE_TEST_XSS')</script>" not in view_res.data


def test_xss_in_vulnerable_mode(client):
    """In Vulnerable Mode, user comment content is rendered unescaped (| safe)."""
    with client.session_transaction() as sess:
        sess["security_mode"] = MODE_VULNERABLE
    _login_alice(client)

    payload = "<script>alert('VULN_TEST_XSS')</script>"
    client.post(
        "/posts/1/comments",
        data={"content": payload},
        follow_redirects=True,
    )

    view_res = client.get("/posts/1")
    assert view_res.status_code == 200
    # Raw unescaped script tag is present in the rendered HTML
    assert b"<script>alert('VULN_TEST_XSS')</script>" in view_res.data


def test_attacker_panel_and_credential_exfiltration_api(client):
    """Verify Attacker Control Panel and simulated credential capture API."""
    # Initially, panel has 0 captured events
    res_panel = client.get("/lab/attacker")
    assert res_panel.status_code == 200
    assert b"No exfiltrated credentials captured yet" in res_panel.data

    # Simulated victim submits fake login credentials via XSS payload
    post_res = client.post(
        "/lab/api/captured-credentials",
        json={
            "username": "victim_alice",
            "password": "SuperSecretPassword123!",
            "source_page": "/posts/1",
        },
    )
    assert post_res.status_code == 201
    assert post_res.get_json()["status"] == "success"

    # API returns captured event
    get_res = client.get("/lab/api/captured-credentials")
    assert get_res.status_code == 200
    events = get_res.get_json()["events"]
    assert len(events) == 1
    assert events[0]["username"] == "victim_alice"
    assert events[0]["password"] == "SuperSecretPassword123!"

    # Attacker panel reflects captured credential in HTML
    res_panel_updated = client.get("/lab/attacker")
    assert res_panel_updated.status_code == 200
    assert b"victim_alice" in res_panel_updated.data
    assert b"SuperSecretPassword123!" in res_panel_updated.data

    # Clear logs
    clear_res = client.post("/lab/api/captured-credentials/clear", json={})
    assert clear_res.status_code == 200
    assert clear_res.get_json()["status"] == "cleared"

    # Verify empty after clearing
    get_after_clear = client.get("/lab/api/captured-credentials")
    assert len(get_after_clear.get_json()["events"]) == 0


def test_fake_login_xss_behavior_in_both_modes(client):
    """Test fake login payload executes in Vulnerable Mode and is escaped in Secure Mode."""
    phish_payload = (
        '<div id="phish-modal"><h3>Session Expired</h3>'
        '<form id="phish-form"><input id="phish-u"><input id="phish-p"></form></div>'
        '<script>fetch("/lab/api/captured-credentials");</script>'
    )

    # 1. Vulnerable Mode
    with client.session_transaction() as sess:
        sess["security_mode"] = MODE_VULNERABLE
    _login_alice(client)

    client.post(
        "/posts/2/comments",
        data={"content": phish_payload},
        follow_redirects=True,
    )

    view_vuln = client.get("/posts/2")
    assert view_vuln.status_code == 200
    # In vulnerable mode, raw modal and script tags are in DOM
    assert b'<div id="phish-modal">' in view_vuln.data
    assert b'<script>fetch("/lab/api/captured-credentials");</script>' in view_vuln.data

    # 2. Secure Mode
    with client.session_transaction() as sess:
        sess["security_mode"] = MODE_SECURE

    view_sec = client.get("/posts/2")
    assert view_sec.status_code == 200
    # In secure mode, tags are escaped to &lt;div and &lt;script
    assert b'<div id="phish-modal">' not in view_sec.data
    assert b'<script>fetch' not in view_sec.data
    assert b'&lt;div id=&#34;phish-modal&#34;&gt;' in view_sec.data or b'&lt;div id="phish-modal"&gt;' in view_sec.data

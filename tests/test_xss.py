"""Tests for Stored XSS vulnerability in Vulnerable Mode vs Context-Aware Output Encoding in Secure Mode."""

from app.security import MODE_SECURE, MODE_VULNERABLE


def test_xss_in_secure_mode(client):
    """In Secure Mode, user comment content is safely escaped by Jinja2."""
    with client.session_transaction() as sess:
        sess["security_mode"] = MODE_SECURE

    payload = "<script>alert('SECURE_TEST_XSS')</script>"
    client.post(
        "/posts/1/comments",
        data={
            "author_name": "Attacker",
            "content": payload,
        },
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

    payload = "<script>alert('VULN_TEST_XSS')</script>"
    client.post(
        "/posts/1/comments",
        data={
            "author_name": "Attacker",
            "content": payload,
        },
        follow_redirects=True,
    )

    view_res = client.get("/posts/1")
    assert view_res.status_code == 200
    # Raw unescaped script tag is present in the rendered HTML
    assert b"<script>alert('VULN_TEST_XSS')</script>" in view_res.data

"""Tests for standard application workflows and database reset predictability."""

def test_user_registration_and_login_flow(client):
    """Users can register with Argon2id, log in, view posts, and comment."""
    # Register new user
    reg_res = client.post(
        "/register",
        data={
            "username": "tester",
            "password": "Password123!",
            "bio": "A quality assurance tester.",
        },
        follow_redirects=True,
    )
    assert reg_res.status_code == 200
    assert b"Registration successful" in reg_res.data
    assert b"@tester" in reg_res.data

    # Log out
    logout_res = client.post("/logout", follow_redirects=True)
    assert logout_res.status_code == 200
    assert b"You have been logged out" in logout_res.data

    # Log in again
    login_res = client.post(
        "/login",
        data={
            "username": "tester",
            "password": "Password123!",
        },
        follow_redirects=True,
    )
    assert login_res.status_code == 200
    assert b"Logged in successfully" in login_res.data


def test_unauthenticated_post_view_hides_full_content_and_blocks_comments(client):
    """Unauthenticated visitors see a partial preview and cannot post comments."""
    res = client.get("/posts/16")
    assert res.status_code == 200
    # Intro preview is shown
    assert b"Phil Karlton" in res.data
    # Later article sections are hidden on the server side
    assert b"Surrogate Keys and Cache Tagging" not in res.data
    assert b"Architectural Checklist for Production Caching" not in res.data
    # Login gate and comment login prompt are shown
    assert b"Sign in to read the full article" in res.data
    assert b"You must be signed in to post a comment." in res.data
    assert b"/posts/16/comments" not in res.data

    # Direct POST to comment endpoint without authentication is rejected
    blocked = client.post(
        "/posts/16/comments",
        data={
            "author_name": "AnonAttacker",
            "content": "Unauthenticated comment attempt",
        },
        follow_redirects=False,
    )
    assert blocked.status_code == 302
    assert "/login" in blocked.headers["Location"]

    followed = client.post(
        "/posts/16/comments",
        data={"content": "Unauthenticated comment attempt"},
        follow_redirects=True,
    )
    assert b"Please sign in to post a comment." in followed.data

    verify_res = client.get("/posts/16")
    assert b"Unauthenticated comment attempt" not in verify_res.data


def test_post_view_and_comment_flow(client):
    """Authenticated users can read full posts and add legitimate comments."""
    res = client.get("/")
    assert res.status_code == 200
    assert b"Articles & Dispatches" in res.data
    assert b"Effective Cache Invalidation Strategies" in res.data

    # Sign in as alice with next redirect back to post 1
    login_res = client.post(
        "/login",
        data={
            "username": "alice",
            "password": "alice123",
            "next": "/posts/1",
        },
        follow_redirects=True,
    )
    assert login_res.status_code == 200
    assert b"Architectural Checklist for Production Readiness" in login_res.data
    assert b"Sign in to read the full article" not in login_res.data
    assert b"Commenting as" in login_res.data

    # Post a legitimate comment (author_name spoofing is ignored; uses authenticated user)
    post_comment = client.post(
        "/posts/1/comments",
        data={
            "author_name": "SpoofedName",
            "content": "This is a legitimate comment analyzing defenses.",
        },
        follow_redirects=True,
    )
    assert post_comment.status_code == 200
    assert b"This is a legitimate comment analyzing defenses." in post_comment.data
    assert b"SpoofedName" not in post_comment.data


def test_login_ignores_unsafe_external_next_redirect(client):
    """External or protocol-relative next URLs fall back to home page."""
    for unsafe_next in ("https://evil.example/phish", "//evil.example/phish", "/\\evil.example"):
        res = client.post(
            "/login",
            data={
                "username": "alice",
                "password": "alice123",
                "next": unsafe_next,
            },
            follow_redirects=False,
        )
        assert res.status_code == 302
        assert res.headers["Location"].endswith("/")
        client.post("/logout")


def test_blog_pagination_flow(client):
    """Blog paginates articles at 4 per page."""
    # Page 1
    res_p1 = client.get("/")
    assert res_p1.status_code == 200
    assert b"Page 1 of 4" in res_p1.data
    assert b"Effective Cache Invalidation Strategies" in res_p1.data

    # Page 2
    res_p2 = client.get("/?page=2")
    assert res_p2.status_code == 200
    assert b"Page 2 of 4" in res_p2.data
    assert b"Next &rarr;" in res_p2.data

    # Page 4 (last page)
    res_p4 = client.get("/?page=4")
    assert res_p4.status_code == 200
    assert b"Page 4 of 4" in res_p4.data
    assert b"Designing Resilient Distributed Systems" in res_p4.data


def test_lab_guide_and_reset(client):
    """Lab guide is accessible and database reset restores initial state."""
    guide_res = client.get("/lab/guide")
    assert guide_res.status_code == 200
    assert b"Security Laboratory Demonstration Guide" in guide_res.data
    assert b"SQL Injection" in guide_res.data
    assert b"Cross-Site Scripting" in guide_res.data

    # Trigger laboratory reset
    reset_res = client.post("/lab/reset", follow_redirects=True)
    assert reset_res.status_code == 200
    assert b"Laboratory database has been reset" in reset_res.data


def test_cli_commands(runner):
    """Verify init-db and reset-db CLI commands."""
    res_init = runner.invoke(args=["init-db"])
    assert res_init.exit_code == 0
    assert "Initialized and seeded" in res_init.output

    res_reset = runner.invoke(args=["reset-db"])
    assert res_reset.exit_code == 0
    assert "Reset database" in res_reset.output


def test_post_markdown_rendering(client):
    """Verify authenticated users see full blog post Markdown rendered into semantic HTML."""
    client.post("/login", data={"username": "alice", "password": "alice123"})
    res = client.get("/posts/16")
    assert res.status_code == 200
    assert b"<h3>1. Fundamental Caching Topologies</h3>" in res.data
    assert b"<div class=\"code-block\"><pre><code class=\"language-python\">" in res.data
    assert b"<li>Cache-Aside" in res.data
    assert b"<strong>" in res.data

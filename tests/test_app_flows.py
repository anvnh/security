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


def test_post_view_and_comment_flow(client):
    """Browsing posts and adding legitimate comments."""
    res = client.get("/")
    assert res.status_code == 200
    assert b"Articles & Dispatches" in res.data
    assert b"Effective Cache Invalidation Strategies" in res.data

    # Post a legitimate comment
    post_comment = client.post(
        "/posts/1/comments",
        data={
            "author_name": "Reviewer",
            "content": "This is a legitimate comment analyzing defenses.",
        },
        follow_redirects=True,
    )
    assert post_comment.status_code == 200
    assert b"This is a legitimate comment analyzing defenses." in post_comment.data


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
    """Verify blog post content renders Markdown into semantic HTML."""
    res = client.get("/posts/16")
    assert res.status_code == 200
    assert b"<h3>1. Fundamental Caching Topologies</h3>" in res.data
    assert b"<div class=\"code-block\"><pre><code class=\"language-python\">" in res.data
    assert b"<li>Cache-Aside" in res.data
    assert b"<strong>" in res.data

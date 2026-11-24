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
    assert b"Welcome to the Web Security Lab" in res.data

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

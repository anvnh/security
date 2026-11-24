"""Authentication routes demonstrating SQL Injection Authentication Bypass via UNION."""

import sqlite3
from urllib.parse import urlparse
from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    session,
)
from app.db import get_db
from app.security import (
    hash_password,
    verify_password,
    login_user,
    logout_user,
    is_secure_mode,
)

auth_bp = Blueprint("auth", __name__)


def _get_safe_next_url(target: str | None) -> str | None:
    """Validate that a post-auth redirect target is a safe local relative path."""
    if not target:
        return None
    candidate = target.strip()
    if not candidate.startswith("/") or candidate.startswith(("//", "/\\")):
        return None
    parsed = urlparse(candidate)
    if parsed.scheme or parsed.netloc or "\\" in parsed.netloc:
        return None
    return candidate


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    """Register a new user account."""
    next_url = _get_safe_next_url(
        request.form.get("next") if request.method == "POST" else request.args.get("next")
    )

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()
        bio = request.form.get("bio", "").strip()

        if not username or not password:
            flash("Username and password are required.", "danger")
            return render_template("auth/register.html", next_url=next_url), 400

        db = get_db()
        existing = db.execute(
            "SELECT id FROM users WHERE username = ?", (username,)
        ).fetchone()

        if existing:
            flash("Username is already taken.", "danger")
            return render_template("auth/register.html", next_url=next_url), 409

        password_hash = hash_password(password)
        cursor = db.execute(
            "INSERT INTO users (username, password_hash, bio) VALUES (?, ?, ?)",
            (username, password_hash, bio),
        )
        db.commit()

        login_user(cursor.lastrowid)
        flash("Registration successful. Welcome!", "success")
        return redirect(next_url or url_for("blog.index"))

    return render_template("auth/register.html", next_url=next_url)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    """Login route demonstrating SQL Injection authentication bypass via UNION vs parameterized query."""
    next_url = _get_safe_next_url(
        request.form.get("next") if request.method == "POST" else request.args.get("next")
    )

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        if not username or not password:
            flash("Please provide both username and password.", "danger")
            return render_template("auth/login.html", next_url=next_url), 400

        db = get_db()
        user = None

        if is_secure_mode():
            # SECURE MODE: Parameterized query prevents SQL injection
            user = db.execute(
                "SELECT id, username, password_hash FROM users WHERE username = ?",
                (username,),
            ).fetchone()
        else:
            # VULNERABLE MODE: Unsafe string formatting allows SQL injection
            raw_sql = f"SELECT id, username, password_hash FROM users WHERE username = '{username}'"
            try:
                user = db.execute(raw_sql).fetchone()
            except sqlite3.OperationalError as e:
                flash(f"Database Error: {e}", "danger")
                return render_template("auth/login.html", next_url=next_url), 400

        # Identical authentication logic in both modes using Argon2id
        if user and verify_password(user["password_hash"], password):
            login_user(user["id"])
            flash(f"Logged in successfully as {user['username']}.", "success")
            return redirect(next_url or url_for("blog.index"))

        flash("Invalid username or password.", "danger")
        return render_template("auth/login.html", next_url=next_url), 401

    return render_template("auth/login.html", next_url=next_url)


@auth_bp.route("/logout", methods=["POST", "GET"])
def logout():
    """Log out current user while preserving security mode."""
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("blog.index"))


@auth_bp.route("/profile")
def profile():
    """View the authenticated user's profile."""
    user_id = session.get("user_id")
    if not user_id:
        flash("Please sign in to view your profile.", "warning")
        return redirect(url_for("auth.login", next=url_for("auth.profile")))

    db = get_db()
    user = db.execute(
        "SELECT id, username, bio, created_at FROM users WHERE id = ?",
        (user_id,),
    ).fetchone()
    if not user:
        logout_user()
        flash("Please sign in to view your profile.", "warning")
        return redirect(url_for("auth.login", next=url_for("auth.profile")))

    posts = db.execute(
        "SELECT id, title, created_at FROM posts WHERE user_id = ? ORDER BY created_at DESC",
        (user["id"],),
    ).fetchall()
    comments = db.execute(
        "SELECT c.id, c.post_id, c.content, c.created_at, p.title AS post_title "
        "FROM comments c JOIN posts p ON c.post_id = p.id "
        "WHERE c.user_id = ? ORDER BY c.created_at DESC",
        (user["id"],),
    ).fetchall()

    return render_template(
        "auth/profile.html",
        user=user,
        posts=posts,
        comments=comments,
    )

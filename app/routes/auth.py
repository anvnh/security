"""Authentication routes demonstrating SQL Injection Authentication Bypass via UNION."""

import sqlite3
from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash,
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


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    """Register a new user account."""
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()
        bio = request.form.get("bio", "").strip()

        if not username or not password:
            flash("Username and password are required.", "danger")
            return render_template("auth/register.html"), 400

        db = get_db()
        existing = db.execute(
            "SELECT id FROM users WHERE username = ?", (username,)
        ).fetchone()

        if existing:
            flash("Username is already taken.", "danger")
            return render_template("auth/register.html"), 409

        password_hash = hash_password(password)
        cursor = db.execute(
            "INSERT INTO users (username, password_hash, bio) VALUES (?, ?, ?)",
            (username, password_hash, bio),
        )
        db.commit()

        login_user(cursor.lastrowid)
        flash("Registration successful. Welcome!", "success")
        return redirect(url_for("blog.index"))

    return render_template("auth/register.html")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    """Login route demonstrating SQL Injection authentication bypass via UNION vs parameterized query."""
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        if not username or not password:
            flash("Please provide both username and password.", "danger")
            return render_template("auth/login.html"), 400

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
                return render_template("auth/login.html"), 400

        # Identical authentication logic in both modes using Argon2id
        if user and verify_password(user["password_hash"], password):
            login_user(user["id"])
            flash(f"Logged in successfully as {user['username']}.", "success")
            return redirect(url_for("blog.index"))

        flash("Invalid username or password.", "danger")
        return render_template("auth/login.html"), 401

    return render_template("auth/login.html")


@auth_bp.route("/logout", methods=["POST", "GET"])
def logout():
    """Log out current user while preserving security mode."""
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("blog.index"))

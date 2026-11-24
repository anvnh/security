"""Blog and comment routes demonstrating SQL Injection Data Exfiltration and Stored XSS."""

import sqlite3
from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    session,
    abort,
)
from app.db import get_db
from app.security import is_secure_mode

blog_bp = Blueprint("blog", __name__)


@blog_bp.route("/")
def index():
    """List blog posts with search filter demonstrating SQL Injection Data Exfiltration."""
    db = get_db()
    query = request.args.get("q", "").strip()
    error_message = None
    posts = []

    if query:
        if is_secure_mode():
            # SECURE MODE: Parameterized query prevents SQL injection
            search_param = f"%{query}%"
            posts = db.execute(
                "SELECT p.*, u.username FROM posts p JOIN users u ON p.user_id = u.id "
                "WHERE p.title LIKE ? OR p.content LIKE ? "
                "ORDER BY p.created_at DESC",
                (search_param, search_param),
            ).fetchall()
        else:
            # VULNERABLE MODE: Unsafe string formatting allows UNION Data Exfiltration
            raw_sql = (
                "SELECT p.*, u.username FROM posts p JOIN users u ON p.user_id = u.id "
                f"WHERE p.title LIKE '%{query}%' OR p.content LIKE '%{query}%' "
                "ORDER BY p.created_at DESC"
            )
            try:
                posts = db.execute(raw_sql).fetchall()
            except sqlite3.OperationalError as e:
                error_message = f"Database Error: {e}"
    else:
        posts = db.execute(
            "SELECT p.*, u.username FROM posts p JOIN users u ON p.user_id = u.id "
            "ORDER BY p.created_at DESC"
        ).fetchall()

    return render_template(
        "blog/index.html",
        posts=posts,
        query=query,
        error_message=error_message,
    )


@blog_bp.route("/posts/<int:post_id>")
def post_detail(post_id):
    """View a single post and its comments (XSS target)."""
    db = get_db()
    post = db.execute(
        "SELECT p.*, u.username FROM posts p JOIN users u ON p.user_id = u.id WHERE p.id = ?",
        (post_id,),
    ).fetchone()

    if not post:
        abort(404)

    comments = db.execute(
        "SELECT * FROM comments WHERE post_id = ? ORDER BY created_at ASC",
        (post_id,),
    ).fetchall()

    return render_template("blog/post.html", post=post, comments=comments)


@blog_bp.route("/posts/<int:post_id>/comments", methods=["POST"])
def add_comment(post_id):
    """Add a new comment demonstrating XSS storage and rendering."""
    db = get_db()
    post = db.execute("SELECT id FROM posts WHERE id = ?", (post_id,)).fetchone()
    if not post:
        abort(404)

    user_id = session.get("user_id")
    author_name = request.form.get("author_name", "").strip()
    content = request.form.get("content", "").strip()

    if user_id:
        user = db.execute("SELECT username FROM users WHERE id = ?", (user_id,)).fetchone()
        if user:
            author_name = user["username"]

    if not author_name:
        author_name = "Anonymous"

    if not content:
        flash("Comment content cannot be empty.", "danger")
        return redirect(url_for("blog.post_detail", post_id=post_id))

    db.execute(
        "INSERT INTO comments (post_id, user_id, author_name, content) VALUES (?, ?, ?, ?)",
        (post_id, user_id, author_name, content),
    )
    db.commit()

    flash("Comment submitted successfully.", "success")
    return redirect(url_for("blog.post_detail", post_id=post_id))

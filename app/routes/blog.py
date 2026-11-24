"""Blog and comment routes demonstrating SQL Injection Data Exfiltration and Stored XSS."""

import math
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

PER_PAGE = 4


def _split_markdown_blocks(content: str) -> list[str]:
    """Split Markdown content into logical blocks without breaking fenced code blocks."""
    lines = content.replace("\r\n", "\n").split("\n")
    blocks = []
    current = []
    in_code_fence = False

    for line in lines:
        if line.startswith("```"):
            in_code_fence = not in_code_fence
            current.append(line)
            continue

        if not in_code_fence and not line.strip():
            if current:
                blocks.append("\n".join(current))
                current = []
        else:
            current.append(line)

    if current:
        blocks.append("\n".join(current))

    return blocks


def build_post_preview(content: str) -> tuple[str, bool]:
    """Return a partial preview of post content and whether content was truncated."""
    if not content:
        return "", False

    blocks = _split_markdown_blocks(content)
    if len(blocks) >= 2:
        preview_count = min(2, len(blocks) // 2)
        return "\n\n".join(blocks[:preview_count]), True

    stripped = content.strip()
    if len(stripped) <= 20:
        return stripped, False

    cutoff = min(300, max(1, len(stripped) // 2))
    snippet = stripped[:cutoff]
    last_space = snippet.rfind(" ")
    if last_space > cutoff // 2:
        snippet = snippet[:last_space]
    return snippet.rstrip() + "...", True


def _get_authenticated_user(db):
    """Return the authenticated user row if session user_id is valid, else None."""
    user_id = session.get("user_id")
    if not user_id:
        return None
    return db.execute(
        "SELECT id, username FROM users WHERE id = ?",
        (user_id,),
    ).fetchone()


@blog_bp.route("/")
def index():
    """List blog posts with pagination and search filter demonstrating SQL Injection Data Exfiltration."""
    db = get_db()
    query = request.args.get("q", "").strip()
    page = max(1, request.args.get("page", 1, type=int))
    error_message = None
    posts = []
    total_posts = 0

    if query:
        if is_secure_mode():
            # SECURE MODE: Parameterized query prevents SQL injection
            search_param = f"%{query}%"
            count_row = db.execute(
                "SELECT COUNT(*) FROM posts p "
                "WHERE p.title LIKE ? OR p.content LIKE ?",
                (search_param, search_param),
            ).fetchone()
            total_posts = count_row[0] if count_row else 0
            total_pages = max(1, math.ceil(total_posts / PER_PAGE))
            page = min(page, total_pages)
            offset = (page - 1) * PER_PAGE

            posts = db.execute(
                "SELECT p.*, u.username FROM posts p JOIN users u ON p.user_id = u.id "
                "WHERE p.title LIKE ? OR p.content LIKE ? "
                "ORDER BY p.created_at DESC "
                "LIMIT ? OFFSET ?",
                (search_param, search_param, PER_PAGE, offset),
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
                total_posts = len(posts)
                total_pages = 1
            except sqlite3.OperationalError as e:
                error_message = f"Database Error: {e}"
                posts = []
                total_pages = 1
    else:
        count_row = db.execute("SELECT COUNT(*) FROM posts").fetchone()
        total_posts = count_row[0] if count_row else 0
        total_pages = max(1, math.ceil(total_posts / PER_PAGE))
        page = min(page, total_pages)
        offset = (page - 1) * PER_PAGE

        posts = db.execute(
            "SELECT p.*, u.username FROM posts p JOIN users u ON p.user_id = u.id "
            "ORDER BY p.created_at DESC "
            "LIMIT ? OFFSET ?",
            (PER_PAGE, offset),
        ).fetchall()

    popular_posts = db.execute(
        "SELECT p.id, p.title, p.created_at, u.username, COUNT(c.id) AS comment_count "
        "FROM posts p "
        "JOIN users u ON p.user_id = u.id "
        "LEFT JOIN comments c ON c.post_id = p.id "
        "GROUP BY p.id "
        "ORDER BY comment_count DESC, p.created_at DESC "
        "LIMIT 4"
    ).fetchall()

    featured_authors = db.execute(
        "SELECT u.username, u.bio, COUNT(p.id) AS post_count "
        "FROM users u "
        "JOIN posts p ON p.user_id = u.id "
        "GROUP BY u.id "
        "ORDER BY post_count DESC, u.id ASC "
        "LIMIT 3"
    ).fetchall()

    recommended_topics = [
        "Distributed Systems",
        "Rust",
        "SQLite",
        "Python",
        "CSS",
        "Caching",
        "WebAssembly",
        "HTTP/3",
    ]

    return render_template(
        "blog/index.html",
        posts=posts,
        query=query,
        current_page=page,
        total_pages=total_pages,
        total_posts=total_posts,
        error_message=error_message,
        popular_posts=popular_posts,
        featured_authors=featured_authors,
        recommended_topics=recommended_topics,
    )


@blog_bp.route("/posts/<int:post_id>")
def post_detail(post_id):
    """View a single post (partial preview when unauthenticated) and its comments (XSS target)."""
    db = get_db()
    post = db.execute(
        "SELECT p.*, u.username FROM posts p JOIN users u ON p.user_id = u.id WHERE p.id = ?",
        (post_id,),
    ).fetchone()

    if not post:
        abort(404)

    authenticated_user = _get_authenticated_user(db)
    if authenticated_user:
        display_content = post["content"]
        is_truncated = False
    else:
        display_content, is_truncated = build_post_preview(post["content"])

    comments = db.execute(
        "SELECT * FROM comments WHERE post_id = ? ORDER BY created_at ASC",
        (post_id,),
    ).fetchall()

    return render_template(
        "blog/post.html",
        post=post,
        display_content=display_content,
        is_truncated=is_truncated,
        comments=comments,
    )


@blog_bp.route("/posts/<int:post_id>/comments", methods=["POST"])
def add_comment(post_id):
    """Add a new comment (authenticated users only) demonstrating XSS storage and rendering."""
    db = get_db()
    post = db.execute("SELECT id FROM posts WHERE id = ?", (post_id,)).fetchone()
    if not post:
        abort(404)

    authenticated_user = _get_authenticated_user(db)
    if not authenticated_user:
        flash("Please sign in to post a comment.", "warning")
        return redirect(
            url_for("auth.login", next=url_for("blog.post_detail", post_id=post_id))
        )

    content = request.form.get("content", "").strip()
    if not content:
        flash("Comment content cannot be empty.", "danger")
        return redirect(url_for("blog.post_detail", post_id=post_id))

    db.execute(
        "INSERT INTO comments (post_id, user_id, author_name, content) VALUES (?, ?, ?, ?)",
        (post_id, authenticated_user["id"], authenticated_user["username"], content),
    )
    db.commit()

    flash("Comment submitted successfully.", "success")
    return redirect(url_for("blog.post_detail", post_id=post_id))

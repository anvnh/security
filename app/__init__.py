"""Flask application factory."""

from flask import Flask, session, request, redirect, url_for
from app.config import Config, TestConfig
from app.db import init_app as init_db_app, get_db
from app.security import (
    get_security_mode,
    MODE_SECURE,
)


def create_app(test_config=None, role="full"):
    """Application factory for the user blog ('blog'), lab/attacker ('lab'), or combined ('full')."""
    if role not in ("blog", "lab", "full"):
        raise ValueError(f"Invalid application role: {role}")

    app = Flask(__name__)

    if test_config is None:
        app.config.from_object(Config)
    else:
        app.config.from_object(test_config)

    # Initialize database extensions and CLI commands
    init_db_app(app)

    # Register custom template filters
    from app.markdown import render_markdown
    app.add_template_filter(render_markdown, "markdown")

    # Inject security mode, current user, and cross-port URL helpers into Jinja templates
    @app.context_processor
    def inject_template_globals():
        current_user = None
        if role in ("blog", "full"):
            user_id = session.get("user_id")
            if user_id:
                db = get_db()
                current_user = db.execute(
                    "SELECT id, username, bio, created_at FROM users WHERE id = ?",
                    (user_id,),
                ).fetchone()

        host = request.host.split(":")[0] if request.host else "127.0.0.1"
        scheme = request.scheme or "http"

        def blog_url(path="/"):
            clean_path = path if path.startswith("/") else f"/{path}"
            if role == "lab":
                return f"{scheme}://{host}:{app.config['BLOG_PORT']}{clean_path}"
            return clean_path

        def lab_url(path="/"):
            clean_path = path if path.startswith("/") else f"/{path}"
            if role == "blog":
                return f"{scheme}://{host}:{app.config['LAB_PORT']}{clean_path}"
            return clean_path

        mode = get_security_mode()
        return {
            "current_user": current_user,
            "security_mode": mode,
            "is_secure": (mode == MODE_SECURE),
            "app_role": role,
            "blog_url": blog_url,
            "lab_url": lab_url,
        }

    # Register blueprints according to server role
    if role in ("blog", "full"):
        from app.routes.auth import auth_bp
        from app.routes.blog import blog_bp

        app.register_blueprint(auth_bp)
        app.register_blueprint(blog_bp)

    if role in ("lab", "full"):
        from app.routes.security_mode import security_mode_bp
        from app.routes.lab import lab_bp

        app.register_blueprint(security_mode_bp)
        app.register_blueprint(lab_bp)

    if role == "lab":
        @app.route("/")
        def lab_root():
            """Redirect lab server root directly to the demonstration guide."""
            return redirect(url_for("lab.guide"))

    return app

"""Flask application factory."""

from flask import Flask, session
from app.config import Config, TestConfig
from app.db import init_app as init_db_app, get_db
from app.security import (
    get_security_mode,
    MODE_SECURE,
)


def create_app(test_config=None):
    """Application factory for the security laboratory."""
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

    # Inject security mode and current user into Jinja templates
    @app.context_processor
    def inject_template_globals():
        current_user = None
        user_id = session.get("user_id")
        if user_id:
            db = get_db()
            current_user = db.execute(
                "SELECT id, username, bio, created_at FROM users WHERE id = ?",
                (user_id,),
            ).fetchone()

        mode = get_security_mode()
        return {
            "current_user": current_user,
            "security_mode": mode,
            "is_secure": (mode == MODE_SECURE),
        }

    # Register blueprints
    from app.routes.security_mode import security_mode_bp
    from app.routes.auth import auth_bp
    from app.routes.blog import blog_bp
    from app.routes.lab import lab_bp

    app.register_blueprint(security_mode_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(blog_bp)
    app.register_blueprint(lab_bp)

    return app

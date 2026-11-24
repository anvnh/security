"""Demonstration guide route for presenters and lab reset."""

from flask import (
    Blueprint,
    render_template,
    redirect,
    url_for,
    flash,
    current_app,
)
from app.db import reset_db

lab_bp = Blueprint("lab", __name__)


@lab_bp.route("/lab/guide")
def guide():
    """Presenter demonstration guide detailing root causes, test steps, and defenses."""
    return render_template("lab/guide.html")


@lab_bp.route("/lab/reset", methods=["POST"])
def reset_laboratory():
    """Reset the database to initial demonstration state."""
    reset_db(current_app.config["DATABASE"])
    flash(
        "Laboratory database has been reset to its initial demonstration state.",
        "success",
    )
    return redirect(url_for("lab.guide"))

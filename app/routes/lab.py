"""Demonstration guide route for presenters, attacker control panel, and lab reset."""

from flask import (
    Blueprint,
    render_template,
    redirect,
    url_for,
    flash,
    current_app,
    request,
    jsonify,
)
from app.db import reset_db, get_db

lab_bp = Blueprint("lab", __name__)


@lab_bp.route("/lab/guide")
def guide():
    """Presenter demonstration guide detailing root causes, test steps, and defenses."""
    return render_template("lab/guide.html")


@lab_bp.route("/lab/attacker")
def attacker_panel():
    """Simulated Attacker Control Panel monitoring exfiltrated credentials in real-time."""
    db = get_db()
    logs = db.execute(
        "SELECT * FROM captured_credentials ORDER BY created_at DESC"
    ).fetchall()
    return render_template("lab/attacker.html", logs=logs)


@lab_bp.route("/lab/api/captured-credentials", methods=["GET", "POST"])
def captured_credentials():
    """API endpoint to receive exfiltrated credentials from XSS or query active logs."""
    db = get_db()
    if request.method == "POST":
        data = request.get_json(silent=True) or request.form
        username = data.get("username", "").strip()
        password = data.get("password", "").strip()
        source_page = data.get("source_page", "").strip() or request.referrer or ""
        user_agent = request.headers.get("User-Agent", "")

        if username or password:
            cursor = db.execute(
                "INSERT INTO captured_credentials (username, password, source_page, user_agent) VALUES (?, ?, ?, ?)",
                (username, password, source_page, user_agent),
            )
            db.commit()
            return jsonify({
                "status": "success",
                "message": "Credential captured by attacker listener",
                "id": cursor.lastrowid,
            }), 201
        return jsonify({"status": "error", "message": "Missing username or password"}), 400

    # GET: return list of captured credentials
    rows = db.execute(
        "SELECT id, username, password, source_page, user_agent, created_at FROM captured_credentials ORDER BY id DESC"
    ).fetchall()
    events = [
        {
            "id": row["id"],
            "username": row["username"],
            "password": row["password"],
            "source_page": row["source_page"],
            "user_agent": row["user_agent"],
            "created_at": str(row["created_at"]),
        }
        for row in rows
    ]
    return jsonify({"events": events, "count": len(events)})


@lab_bp.route("/lab/api/captured-credentials/clear", methods=["POST"])
def clear_captured_credentials():
    """Clear all captured logs from the demonstration listener."""
    db = get_db()
    db.execute("DELETE FROM captured_credentials")
    db.commit()
    if request.is_json:
        return jsonify({"status": "cleared", "count": 0})
    flash("Attacker demonstration logs have been cleared.", "info")
    return redirect(url_for("lab.attacker_panel"))


@lab_bp.route("/lab/reset", methods=["POST"])
def reset_laboratory():
    """Reset the database to initial demonstration state."""
    reset_db(current_app.config["DATABASE"])
    flash(
        "Laboratory database has been reset to its initial demonstration state.",
        "success",
    )
    return redirect(url_for("lab.guide"))

"""Security mode toggle route."""

from flask import Blueprint, request, jsonify, redirect, url_for, flash
from app.security import (
    get_security_mode,
    set_security_mode,
    MODE_SECURE,
    MODE_VULNERABLE,
)

security_mode_bp = Blueprint("security_mode", __name__)


@security_mode_bp.route("/security/toggle", methods=["POST"])
def toggle():
    """Toggle between Secure Mode and Vulnerable Mode."""
    target_mode = request.form.get("mode") or (request.json.get("mode") if request.is_json else None)

    if not target_mode:
        current = get_security_mode()
        target_mode = MODE_VULNERABLE if current == MODE_SECURE else MODE_SECURE

    try:
        new_mode = set_security_mode(target_mode)
    except ValueError:
        return jsonify({"status": "error", "message": "Invalid mode"}), 400

    if request.is_json or request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return jsonify({
            "status": "success",
            "security_mode": new_mode,
            "is_secure": new_mode == MODE_SECURE,
        })

    flash(
        f"Security mode switched to: {'SECURE' if new_mode == MODE_SECURE else 'VULNERABLE'}",
        "info" if new_mode == MODE_SECURE else "warning",
    )
    return redirect(url_for("lab.guide"))

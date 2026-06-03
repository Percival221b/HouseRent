from flask import Blueprint, redirect, url_for

tenant_bp = Blueprint("tenant", __name__)


@tenant_bp.route("/")
def dashboard():
    return redirect(url_for("user.history"))

from flask import Blueprint, render_template

tenant_bp = Blueprint("tenant", __name__)


@tenant_bp.route("/")
def dashboard():
    return render_template("tenant/dashboard.html")


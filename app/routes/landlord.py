from flask import Blueprint, render_template

landlord_bp = Blueprint("landlord", __name__)


@landlord_bp.route("/")
def dashboard():
    return render_template("landlord/dashboard.html")


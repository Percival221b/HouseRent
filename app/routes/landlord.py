from flask import Blueprint, redirect, url_for

landlord_bp = Blueprint("landlord", __name__)


@landlord_bp.route("/")
def dashboard():
    return redirect(url_for("user.history"))

from flask import Blueprint, render_template

houses_bp = Blueprint("houses", __name__)


@houses_bp.route("/")
def list_houses():
    return render_template("houses/list.html")


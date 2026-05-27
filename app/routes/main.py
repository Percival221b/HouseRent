from flask import Blueprint, render_template

from app.models import House

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def index():
    featured_houses = (
        House.query.filter(House.status == "vacant")
        .order_by(House.created_at.desc())
        .limit(6)
        .all()
    )
    return render_template("index.html", featured_houses=featured_houses)

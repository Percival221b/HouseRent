from flask import Blueprint, redirect, render_template, url_for
from flask_login import logout_user

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login")
def login():
    return render_template("auth/login.html")


@auth_bp.route("/register")
def register():
    return render_template("auth/register.html")


@auth_bp.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("main.index"))

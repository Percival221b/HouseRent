from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from app.extensions import db
from app.models.user import User
from app.utils.decorators import role_required

admin_bp = Blueprint("admin", __name__)


@admin_bp.route("/")
@login_required
@role_required("admin")
def dashboard():
    return render_template("admin/dashboard.html")


@admin_bp.route("/users")
@login_required
@role_required("admin")
def users():
    page = request.args.get("page", 1, type=int)
    per_page = 15
    query = User.query.order_by(User.created_at.desc())
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    return render_template("admin/users.html", pagination=pagination, users=pagination.items)


@admin_bp.route("/users/<int:user_id>/status", methods=["POST"])
@login_required
@role_required("admin")
def toggle_user_status(user_id: int):
    user = db.session.get(User, user_id)
    if not user:
        flash("用户不存在", "error")
        return redirect(url_for("admin.users"))

    if user.id == current_user.id:
        flash("不能操作自己", "error")
        return redirect(url_for("admin.users"))

    if user.status == "active":
        user.status = "disabled"
        flash(f"用户 {user.username} 已被禁用", "info")
    elif user.status == "disabled":
        user.status = "active"
        flash(f"用户 {user.username} 已恢复", "info")
    elif user.status == "pending":
        user.status = "active"
        flash(f"用户 {user.username} 已通过审核", "success")

    db.session.commit()
    return redirect(url_for("admin.users"))


@admin_bp.route("/logs")
@login_required
@role_required("admin")
def logs():
    from app.models.user import LoginLog

    page = request.args.get("page", 1, type=int)
    per_page = 20
    pagination = (
        LoginLog.query
        .order_by(LoginLog.created_at.desc())
        .paginate(page=page, per_page=per_page, error_out=False)
    )
    return render_template("admin/logs.html", pagination=pagination, logs=pagination.items)

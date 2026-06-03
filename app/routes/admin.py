from datetime import datetime, timedelta

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required
from sqlalchemy import func

from app.extensions import db
from app.models.house import House
from app.models.lease import Contract, Payment
from app.models.log import SystemLog
from app.models.user import User
from app.utils.decorators import role_required

admin_bp = Blueprint("admin", __name__)


@admin_bp.route("/")
@login_required
@role_required("admin", "system_admin")
def dashboard():
    if current_user.role == "system_admin":
        return redirect("/admin/report")
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


@admin_bp.route("/report")
@login_required
@role_required("admin", "system_admin")
def report():
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)

    total_houses = House.query.count()
    rented_houses = House.query.filter_by(status="rented").count()
    vacant_houses = House.query.filter_by(status="vacant").count()
    offline_houses = House.query.filter_by(status="offline").count()
    rental_rate = (rented_houses / total_houses * 100) if total_houses else 0

    active_contracts = Contract.query.filter_by(status="active").count()
    expected_monthly_income = (
        db.session.query(func.coalesce(func.sum(Contract.monthly_rent), 0))
        .filter(Contract.status == "active")
        .scalar()
    )
    paid_income_total = (
        db.session.query(func.coalesce(func.sum(Payment.amount), 0))
        .filter(Payment.status == "paid")
        .scalar()
    )
    paid_income_30d = (
        db.session.query(func.coalesce(func.sum(Payment.amount), 0))
        .filter(Payment.status == "paid", Payment.paid_at >= thirty_days_ago)
        .scalar()
    )

    total_users = User.query.count()
    tenant_count = User.query.filter_by(role="tenant").count()
    landlord_count = User.query.filter_by(role="landlord").count()
    active_users_30d = User.query.filter(User.last_login_at >= thirty_days_ago).count()

    from app.models.user import LoginLog

    successful_logins_30d = LoginLog.query.filter(
        LoginLog.status == "success",
        LoginLog.created_at >= thirty_days_ago,
    ).count()
    unique_login_users_30d = (
        db.session.query(func.count(func.distinct(LoginLog.user_id)))
        .filter(
            LoginLog.status == "success",
            LoginLog.user_id.isnot(None),
            LoginLog.created_at >= thirty_days_ago,
        )
        .scalar()
    )

    recent_system_logs = (
        SystemLog.query
        .order_by(SystemLog.created_at.desc())
        .limit(25)
        .all()
    )

    return render_template(
        "admin/report.html",
        total_houses=total_houses,
        rented_houses=rented_houses,
        vacant_houses=vacant_houses,
        offline_houses=offline_houses,
        rental_rate=rental_rate,
        active_contracts=active_contracts,
        expected_monthly_income=expected_monthly_income,
        paid_income_total=paid_income_total,
        paid_income_30d=paid_income_30d,
        total_users=total_users,
        tenant_count=tenant_count,
        landlord_count=landlord_count,
        active_users_30d=active_users_30d,
        successful_logins_30d=successful_logins_30d,
        unique_login_users_30d=unique_login_users_30d,
        recent_system_logs=recent_system_logs,
    )

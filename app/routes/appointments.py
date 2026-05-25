from datetime import datetime

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user

from app.extensions import db
from app.forms.appointment import AppointmentForm
from app.models.appointment import Appointment
from app.models.house import House
from app.models.user import User

appointments_bp = Blueprint("appointments", __name__, url_prefix="/appointments")


@appointments_bp.route("/")
@login_required
def list_appointments():
    role = current_user.role
    if role == "tenant":
        appointments = (
            Appointment.query
            .filter_by(tenant_id=current_user.id)
            .order_by(Appointment.created_at.desc())
            .all()
        )
    elif role == "landlord":
        appointments = (
            Appointment.query
            .filter_by(landlord_id=current_user.id)
            .order_by(Appointment.created_at.desc())
            .all()
        )
    else:
        appointments = Appointment.query.order_by(Appointment.created_at.desc()).all()

    return render_template("appointments/list.html", appointments=appointments)


@appointments_bp.route("/<int:appointment_id>")
@login_required
def detail(appointment_id):
    appointment = Appointment.query.get_or_404(appointment_id)
    return render_template("appointments/detail.html", appointment=appointment)


@appointments_bp.route("/new", methods=["GET", "POST"])
@login_required
def create():
    if current_user.role != "tenant":
        flash("只有租客才能预约看房。", "error")
        return redirect(url_for("appointments.list_appointments"))

    houses = House.query.filter_by(status="vacant").all()
    selected_house_id = request.args.get("house_id", type=int)
    form = AppointmentForm()

    if form.validate_on_submit():
        house = House.query.get_or_404(form.house_id.data)
        appointment = Appointment(
            house_id=house.id,
            tenant_id=current_user.id,
            landlord_id=house.landlord_id,
            appointment_time=form.appointment_time.data,
            remark=form.remark.data,
        )
        db.session.add(appointment)
        db.session.commit()
        flash("预约已提交，等待房东确认。", "success")
        return redirect(url_for("appointments.list_appointments"))

    if form.house_id.data is None and selected_house_id:
        form.house_id.data = selected_house_id

    return render_template(
        "appointments/create.html", form=form, houses=houses, selected_house_id=selected_house_id
    )


@appointments_bp.route("/<int:appointment_id>/approve", methods=["POST"])
@login_required
def approve(appointment_id):
    appointment = Appointment.query.get_or_404(appointment_id)
    if current_user.id != appointment.landlord_id:
        flash("无权操作此预约。", "error")
        return redirect(url_for("appointments.list_appointments"))

    reply = request.form.get("reply", "")
    appointment.status = "approved"
    appointment.reply = reply
    db.session.commit()
    flash("已同意预约。", "success")
    return redirect(url_for("appointments.detail", appointment_id=appointment_id))


@appointments_bp.route("/<int:appointment_id>/reject", methods=["POST"])
@login_required
def reject(appointment_id):
    appointment = Appointment.query.get_or_404(appointment_id)
    if current_user.id != appointment.landlord_id:
        flash("无权操作此预约。", "error")
        return redirect(url_for("appointments.list_appointments"))

    reply = request.form.get("reply", "")
    appointment.status = "rejected"
    appointment.reply = reply
    db.session.commit()
    flash("已拒绝预约。", "success")
    return redirect(url_for("appointments.detail", appointment_id=appointment_id))


@appointments_bp.route("/<int:appointment_id>/cancel", methods=["POST"])
@login_required
def cancel(appointment_id):
    appointment = Appointment.query.get_or_404(appointment_id)
    if current_user.id != appointment.tenant_id:
        flash("无权操作此预约。", "error")
        return redirect(url_for("appointments.list_appointments"))

    if appointment.status not in ("pending", "approved"):
        flash("当前状态不可取消。", "error")
        return redirect(url_for("appointments.detail", appointment_id=appointment_id))

    appointment.status = "cancelled"
    db.session.commit()
    flash("预约已取消。", "success")
    return redirect(url_for("appointments.detail", appointment_id=appointment_id))


@appointments_bp.route("/<int:appointment_id>/complete", methods=["POST"])
@login_required
def complete(appointment_id):
    appointment = Appointment.query.get_or_404(appointment_id)
    if current_user.id not in (appointment.tenant_id, appointment.landlord_id):
        flash("无权操作此预约。", "error")
        return redirect(url_for("appointments.list_appointments"))

    if appointment.status != "approved":
        flash("只有已同意的预约才能标记完成。", "error")
        return redirect(url_for("appointments.detail", appointment_id=appointment_id))

    appointment.status = "completed"
    db.session.commit()
    flash("预约已完成。", "success")
    return redirect(url_for("appointments.detail", appointment_id=appointment_id))


# --- 开发辅助：临时切换用户（B 组完成登录后删除此路由） ---
@appointments_bp.route("/dev-login/<int:user_id>")
def dev_login(user_id):
    user = User.query.get_or_404(user_id)
    login_user(user)
    flash(f"已切换为 {user.username}（角色：{user.role}）", "info")
    return redirect(url_for("appointments.list_appointments"))

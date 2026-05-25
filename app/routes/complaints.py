from datetime import datetime

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from app.extensions import db
from app.forms.complaint import ComplaintForm
from app.models.house import House
from app.models.maintenance import Complaint
from app.models.user import User

complaints_bp = Blueprint("complaints", __name__, url_prefix="/complaints")


@complaints_bp.route("/")
@login_required
def list_complaints():
    role = current_user.role
    if role == "tenant":
        complaints = (
            Complaint.query
            .filter_by(tenant_id=current_user.id)
            .order_by(Complaint.created_at.desc())
            .all()
        )
    elif role == "landlord":
        complaints = (
            Complaint.query
            .filter_by(target_user_id=current_user.id)
            .order_by(Complaint.created_at.desc())
            .all()
        )
    else:
        complaints = Complaint.query.order_by(Complaint.created_at.desc()).all()

    return render_template("complaints/list.html", complaints=complaints)


@complaints_bp.route("/<int:complaint_id>")
@login_required
def detail(complaint_id):
    complaint = Complaint.query.get_or_404(complaint_id)
    return render_template("complaints/detail.html", complaint=complaint)


@complaints_bp.route("/new", methods=["GET", "POST"])
@login_required
def create():
    if current_user.role != "tenant":
        flash("只有租客才能提交投诉。", "error")
        return redirect(url_for("complaints.list_complaints"))

    houses = House.query.all()
    landlords = User.query.filter_by(role="landlord", status="active").all()
    form = ComplaintForm()
    form.house_id.choices = [(-1, "不关联房源")] + [(h.id, f"{h.title} - {h.address}") for h in houses]
    form.target_user_id.choices = [(-1, "不指定")] + [(u.id, u.username) for u in landlords]

    if form.validate_on_submit():
        complaint = Complaint(
            house_id=form.house_id.data if form.house_id.data and form.house_id.data != -1 else None,
            tenant_id=current_user.id,
            target_user_id=form.target_user_id.data if form.target_user_id.data and form.target_user_id.data != -1 else None,
            title=form.title.data,
            content=form.content.data,
        )
        db.session.add(complaint)
        db.session.commit()
        flash("投诉已提交，等待处理。", "success")
        return redirect(url_for("complaints.list_complaints"))

    return render_template("complaints/create.html", form=form)


@complaints_bp.route("/<int:complaint_id>/process", methods=["POST"])
@login_required
def process(complaint_id):
    complaint = Complaint.query.get_or_404(complaint_id)
    if current_user.role not in ("landlord", "admin"):
        flash("无权处理投诉。", "error")
        return redirect(url_for("complaints.list_complaints"))

    if complaint.status != "pending":
        flash("只有待处理的投诉才能接单。", "error")
        return redirect(url_for("complaints.detail", complaint_id=complaint_id))

    complaint.status = "processing"
    complaint.handler_id = current_user.id
    db.session.commit()
    flash("已接单，请尽快处理。", "success")
    return redirect(url_for("complaints.detail", complaint_id=complaint_id))


@complaints_bp.route("/<int:complaint_id>/resolve", methods=["POST"])
@login_required
def resolve(complaint_id):
    complaint = Complaint.query.get_or_404(complaint_id)
    if current_user.id != complaint.handler_id:
        flash("只有接单人才能处理。", "error")
        return redirect(url_for("complaints.list_complaints"))

    if complaint.status != "processing":
        flash("只有处理中的投诉才能标记解决。", "error")
        return redirect(url_for("complaints.detail", complaint_id=complaint_id))

    result = request.form.get("result", "")
    complaint.status = "resolved"
    complaint.result = result
    complaint.handled_at = datetime.utcnow()
    db.session.commit()
    flash("投诉已解决。", "success")
    return redirect(url_for("complaints.detail", complaint_id=complaint_id))


@complaints_bp.route("/<int:complaint_id>/reject", methods=["POST"])
@login_required
def reject(complaint_id):
    complaint = Complaint.query.get_or_404(complaint_id)
    if current_user.role not in ("landlord", "admin"):
        flash("无权处理投诉。", "error")
        return redirect(url_for("complaints.list_complaints"))

    if complaint.status != "pending":
        flash("只有待处理的投诉才能驳回。", "error")
        return redirect(url_for("complaints.detail", complaint_id=complaint_id))

    result = request.form.get("result", "")
    complaint.status = "rejected"
    complaint.result = result
    complaint.handler_id = current_user.id
    complaint.handled_at = datetime.utcnow()
    db.session.commit()
    flash("投诉已驳回。", "success")
    return redirect(url_for("complaints.detail", complaint_id=complaint_id))

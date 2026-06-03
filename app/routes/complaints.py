from datetime import datetime

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from app.extensions import db
from app.forms.complaint import ComplaintForm
from app.models.house import House
from app.models.lease import Contract
from app.models.maintenance import Complaint
from app.models.user import User

complaints_bp = Blueprint("complaints", __name__, url_prefix="/complaints")

TENANT_SERVICE_CONTRACT_STATUSES = ("active",)


def _tenant_service_houses(tenant_id: int):
    return (
        House.query
        .join(Contract, Contract.house_id == House.id)
        .filter(
            Contract.tenant_id == tenant_id,
            Contract.status.in_(TENANT_SERVICE_CONTRACT_STATUSES),
        )
        .order_by(House.created_at.desc())
        .all()
    )


def _tenant_house(tenant_id: int, house_id: int) -> House | None:
    return (
        House.query
        .join(Contract, Contract.house_id == House.id)
        .filter(
            Contract.tenant_id == tenant_id,
            Contract.house_id == house_id,
            Contract.status.in_(TENANT_SERVICE_CONTRACT_STATUSES),
        )
        .first()
    )


def _landlord_can_access_complaint(complaint: Complaint, landlord_id: int) -> bool:
    if complaint.target_user_id == landlord_id:
        return True
    return complaint.house is not None and complaint.house.landlord_id == landlord_id


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
            .outerjoin(House)
            .filter(
                (Complaint.target_user_id == current_user.id)
                | (House.landlord_id == current_user.id)
            )
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
    if current_user.role == "tenant" and complaint.tenant_id != current_user.id:
        flash("无权查看此投诉。", "error")
        return redirect(url_for("complaints.list_complaints"))
    if current_user.role == "landlord" and not _landlord_can_access_complaint(
        complaint, current_user.id
    ):
        flash("无权查看此投诉。", "error")
        return redirect(url_for("complaints.list_complaints"))
    return render_template("complaints/detail.html", complaint=complaint)


@complaints_bp.route("/new", methods=["GET", "POST"])
@login_required
def create():
    if current_user.role != "tenant":
        flash("只有租客才能提交投诉。", "error")
        return redirect(url_for("complaints.list_complaints"))

    houses = _tenant_service_houses(current_user.id)
    house_landlord_ids = {h.landlord_id for h in houses}
    landlords = []
    if house_landlord_ids:
        landlords = (
            User.query
            .filter(
                User.role == "landlord",
                User.status == "active",
                User.id.in_(house_landlord_ids),
            )
            .order_by(User.username.asc())
            .all()
        )
    form = ComplaintForm()
    form.house_id.choices = [(-1, "请选择关联房源")] + [
        (h.id, f"{h.title} - {h.address}") for h in houses
    ]
    form.target_user_id.choices = [(-1, "按房源自动匹配房东")] + [
        (u.id, u.username) for u in landlords
    ]

    if form.validate_on_submit():
        house = None
        if form.house_id.data and form.house_id.data != -1:
            house = _tenant_house(current_user.id, form.house_id.data)
            if not house:
                flash("只能提交自己当前租住房源相关的投诉。", "error")
                return render_template("complaints/create.html", form=form)

        target_user_id = (
            form.target_user_id.data
            if form.target_user_id.data and form.target_user_id.data != -1
            else None
        )
        if house:
            target_user_id = house.landlord_id
        elif target_user_id and target_user_id not in house_landlord_ids:
            flash("只能投诉自己当前租住房源对应的房东。", "error")
            return render_template("complaints/create.html", form=form)
        elif not target_user_id:
            flash("请选择关联房源或被投诉房东。", "error")
            return render_template("complaints/create.html", form=form)

        complaint = Complaint(
            house_id=house.id if house else None,
            tenant_id=current_user.id,
            target_user_id=target_user_id,
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
    if current_user.role == "landlord" and not _landlord_can_access_complaint(
        complaint, current_user.id
    ):
        flash("无权处理此投诉。", "error")
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
    if current_user.role == "landlord" and not _landlord_can_access_complaint(
        complaint, current_user.id
    ):
        flash("无权处理此投诉。", "error")
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

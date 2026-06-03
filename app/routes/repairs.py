from datetime import datetime

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from app.extensions import db
from app.forms.repair import RepairForm
from app.models.house import House
from app.models.lease import Contract
from app.models.maintenance import RepairRequest

repairs_bp = Blueprint("repairs", __name__, url_prefix="/repairs")

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


def _tenant_can_access_house(tenant_id: int, house_id: int) -> bool:
    return (
        Contract.query
        .filter(
            Contract.tenant_id == tenant_id,
            Contract.house_id == house_id,
            Contract.status.in_(TENANT_SERVICE_CONTRACT_STATUSES),
        )
        .first()
        is not None
    )


@repairs_bp.route("/")
@login_required
def list_repairs():
    role = current_user.role
    if role == "tenant":
        repairs = (
            RepairRequest.query
            .filter_by(tenant_id=current_user.id)
            .order_by(RepairRequest.created_at.desc())
            .all()
        )
    elif role == "landlord":
        repairs = (
            RepairRequest.query
            .join(House)
            .filter(House.landlord_id == current_user.id)
            .order_by(RepairRequest.created_at.desc())
            .all()
        )
    else:
        repairs = RepairRequest.query.order_by(RepairRequest.created_at.desc()).all()

    return render_template("repairs/list.html", repairs=repairs)


@repairs_bp.route("/<int:repair_id>")
@login_required
def detail(repair_id):
    repair = RepairRequest.query.get_or_404(repair_id)
    return render_template("repairs/detail.html", repair=repair)


@repairs_bp.route("/new", methods=["GET", "POST"])
@login_required
def create():
    if current_user.role != "tenant":
        flash("只有租客才能报修。", "error")
        return redirect(url_for("repairs.list_repairs"))

    form = RepairForm()
    selected_house_id = request.args.get("house_id", type=int)
    houses = _tenant_service_houses(current_user.id)

    if form.validate_on_submit():
        house = House.query.get_or_404(form.house_id.data)
        if not _tenant_can_access_house(current_user.id, house.id):
            flash("只能提交自己当前租住房源的报修。", "error")
            return render_template(
                "repairs/create.html", form=form, houses=houses,
                selected_house_id=selected_house_id,
            )

        repair = RepairRequest(
            house_id=house.id,
            tenant_id=current_user.id,
            title=form.title.data,
            description=form.description.data,
        )
        db.session.add(repair)
        db.session.commit()
        flash("报修已提交，等待处理。", "success")
        return redirect(url_for("repairs.list_repairs"))

    if form.house_id.data is None and selected_house_id:
        form.house_id.data = selected_house_id

    return render_template(
        "repairs/create.html", form=form, houses=houses,
        selected_house_id=selected_house_id,
    )


@repairs_bp.route("/<int:repair_id>/process", methods=["POST"])
@login_required
def process(repair_id):
    repair = RepairRequest.query.get_or_404(repair_id)
    house = repair.house
    if current_user.role not in ("landlord", "admin") or (
        current_user.role == "landlord" and house.landlord_id != current_user.id
    ):
        flash("无权操作此报修。", "error")
        return redirect(url_for("repairs.list_repairs"))

    if repair.status != "pending":
        flash("只有待处理的报修才能接单。", "error")
        return redirect(url_for("repairs.detail", repair_id=repair_id))

    repair.status = "processing"
    repair.handler_id = current_user.id
    db.session.commit()
    flash("已接单，请尽快处理。", "success")
    return redirect(url_for("repairs.detail", repair_id=repair_id))


@repairs_bp.route("/<int:repair_id>/finish", methods=["POST"])
@login_required
def finish(repair_id):
    repair = RepairRequest.query.get_or_404(repair_id)
    if current_user.id != repair.handler_id:
        flash("只有接单人才能标记完成。", "error")
        return redirect(url_for("repairs.list_repairs"))

    if repair.status != "processing":
        flash("只有处理中的报修才能标记完成。", "error")
        return redirect(url_for("repairs.detail", repair_id=repair_id))

    result = request.form.get("result", "")
    repair.status = "finished"
    repair.result = result
    repair.handled_at = datetime.utcnow()
    db.session.commit()
    flash("报修已处理完成。", "success")
    return redirect(url_for("repairs.detail", repair_id=repair_id))


@repairs_bp.route("/<int:repair_id>/reject", methods=["POST"])
@login_required
def reject(repair_id):
    repair = RepairRequest.query.get_or_404(repair_id)
    house = repair.house
    if current_user.role not in ("landlord", "admin") or (
        current_user.role == "landlord" and house.landlord_id != current_user.id
    ):
        flash("无权操作此报修。", "error")
        return redirect(url_for("repairs.list_repairs"))

    if repair.status != "pending":
        flash("只有待处理的报修才能拒绝。", "error")
        return redirect(url_for("repairs.detail", repair_id=repair_id))

    result = request.form.get("result", "")
    repair.status = "rejected"
    repair.result = result
    repair.handler_id = current_user.id
    repair.handled_at = datetime.utcnow()
    db.session.commit()
    flash("报修已拒绝。", "success")
    return redirect(url_for("repairs.detail", repair_id=repair_id))

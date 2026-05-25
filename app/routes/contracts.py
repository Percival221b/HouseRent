import secrets
from datetime import date, datetime

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from app.extensions import db
from app.forms.contract import ContractForm
from app.models.appointment import Appointment
from app.models.house import House
from app.models.lease import Contract
from app.models.user import User

contracts_bp = Blueprint("contracts", __name__, url_prefix="/contracts")


def _generate_contract_no() -> str:
    today = date.today().strftime("%Y%m%d")
    suffix = secrets.token_hex(2).upper()
    return f"CON-{today}-{suffix}"


@contracts_bp.route("/")
@login_required
def list_contracts():
    role = current_user.role
    if role == "tenant":
        contracts = (
            Contract.query
            .filter_by(tenant_id=current_user.id)
            .order_by(Contract.created_at.desc())
            .all()
        )
    elif role == "landlord":
        contracts = (
            Contract.query
            .filter_by(landlord_id=current_user.id)
            .order_by(Contract.created_at.desc())
            .all()
        )
    else:
        contracts = Contract.query.order_by(Contract.created_at.desc()).all()

    return render_template("contracts/list.html", contracts=contracts)


@contracts_bp.route("/<int:contract_id>")
@login_required
def detail(contract_id):
    contract = Contract.query.get_or_404(contract_id)
    return render_template("contracts/detail.html", contract=contract)


@contracts_bp.route("/new", methods=["GET", "POST"])
@login_required
def create():
    if current_user.role not in ("landlord", "admin"):
        flash("只有房东才能创建合同。", "error")
        return redirect(url_for("contracts.list_contracts"))

    houses = House.query.all()
    tenants = User.query.filter_by(role="tenant", status="active").all()
    form = ContractForm()

    # 从预约创建时，预填字段
    appointment_id = request.args.get("appointment_id", type=int)
    appointment = None
    if appointment_id:
        appointment = Appointment.query.get(appointment_id)

    if form.validate_on_submit():
        house = House.query.get_or_404(form.house_id.data)
        tenant = User.query.get_or_404(form.tenant_id.data)
        if tenant.role != "tenant":
            flash("只能与租客签订合同。", "error")
            return render_template(
                "contracts/create.html", form=form, houses=houses, tenants=tenants
            )

        contract = Contract(
            contract_no=_generate_contract_no(),
            house_id=house.id,
            tenant_id=tenant.id,
            landlord_id=current_user.id,
            start_date=form.start_date.data,
            end_date=form.end_date.data,
            monthly_rent=form.monthly_rent.data,
            deposit=form.deposit.data,
            content=form.content.data,
            status="draft",
        )
        db.session.add(contract)
        db.session.commit()
        flash(f"合同 {contract.contract_no} 已创建。", "success")
        return redirect(url_for("contracts.detail", contract_id=contract.id))

    # 预填
    if appointment:
        if form.house_id.data is None:
            form.house_id.data = appointment.house_id
        if form.tenant_id.data is None:
            form.tenant_id.data = appointment.tenant_id
        if form.content.data is None:
            form.content.data = (
                f"通过看房预约 #{appointment.id} 创建。\n"
                f"看房时间：{appointment.appointment_time}\n"
            )

    return render_template(
        "contracts/create.html", form=form, houses=houses, tenants=tenants,
        appointment=appointment,
    )


@contracts_bp.route("/<int:contract_id>/sign", methods=["POST"])
@login_required
def sign(contract_id):
    contract = Contract.query.get_or_404(contract_id)
    if contract.status not in ("draft", "pending_signed"):
        flash("当前状态不可签署。", "error")
        return redirect(url_for("contracts.detail", contract_id=contract_id))

    if current_user.id == contract.landlord_id:
        if contract.signed_by_landlord_at:
            flash("你已签署过此合同。", "info")
        else:
            contract.signed_by_landlord_at = datetime.utcnow()
            contract.status = "pending_signed"
            db.session.commit()
            flash("你已签署合同，等待租客签署。", "success")
    elif current_user.id == contract.tenant_id:
        if contract.signed_by_tenant_at:
            flash("你已签署过此合同。", "info")
        else:
            contract.signed_by_tenant_at = datetime.utcnow()
            # 双方都签署后合同生效
            if contract.signed_by_landlord_at:
                contract.status = "active"
            else:
                contract.status = "pending_signed"
            db.session.commit()
            flash("你已签署合同。", "success")
    else:
        flash("无权操作此合同。", "error")

    return redirect(url_for("contracts.detail", contract_id=contract_id))


@contracts_bp.route("/<int:contract_id>/end", methods=["POST"])
@login_required
def end_contract(contract_id):
    contract = Contract.query.get_or_404(contract_id)
    if current_user.id not in (contract.landlord_id, contract.tenant_id):
        flash("无权操作此合同。", "error")
        return redirect(url_for("contracts.list_contracts"))

    if contract.status not in ("draft", "pending_signed", "active"):
        flash("当前状态不可终止。", "error")
        return redirect(url_for("contracts.detail", contract_id=contract_id))

    contract.status = "ended"
    db.session.commit()
    flash("合同已终止。", "success")
    return redirect(url_for("contracts.detail", contract_id=contract_id))


@contracts_bp.route("/<int:contract_id>/cancel", methods=["POST"])
@login_required
def cancel_contract(contract_id):
    contract = Contract.query.get_or_404(contract_id)
    if current_user.role != "landlord" and current_user.id != contract.landlord_id:
        flash("只有房东可以取消合同。", "error")
        return redirect(url_for("contracts.list_contracts"))

    if contract.status == "active":
        flash("已生效的合同不可取消，请使用终止合同。", "error")
        return redirect(url_for("contracts.detail", contract_id=contract_id))

    contract.status = "cancelled"
    db.session.commit()
    flash("合同已取消。", "success")
    return redirect(url_for("contracts.detail", contract_id=contract_id))

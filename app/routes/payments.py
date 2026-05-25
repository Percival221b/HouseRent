import secrets
from datetime import datetime

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from app.extensions import db
from app.forms.payment import PaymentForm
from app.models.lease import Contract, Payment

payments_bp = Blueprint("payments", __name__, url_prefix="/payments")


def _generate_transaction_no() -> str:
    suffix = secrets.token_hex(4).upper()
    return f"TXN-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}-{suffix}"


@payments_bp.route("/")
@login_required
def list_payments():
    role = current_user.role
    if role == "tenant":
        payments = (
            Payment.query
            .filter_by(payer_id=current_user.id)
            .order_by(Payment.created_at.desc())
            .all()
        )
    elif role == "landlord":
        payments = (
            Payment.query
            .join(Contract)
            .filter(Contract.landlord_id == current_user.id)
            .order_by(Payment.created_at.desc())
            .all()
        )
    else:
        payments = Payment.query.order_by(Payment.created_at.desc()).all()

    return render_template("payments/list.html", payments=payments)


@payments_bp.route("/<int:payment_id>")
@login_required
def detail(payment_id):
    payment = Payment.query.get_or_404(payment_id)
    return render_template("payments/detail.html", payment=payment)


@payments_bp.route("/new", methods=["GET", "POST"])
@login_required
def create():
    if current_user.role not in ("landlord", "admin"):
        flash("只有房东才能创建收款单。", "error")
        return redirect(url_for("payments.list_payments"))

    contracts = Contract.query.filter_by(landlord_id=current_user.id, status="active").all()
    form = PaymentForm()
    selected_contract_id = request.args.get("contract_id", type=int)

    if form.validate_on_submit():
        contract = Contract.query.get_or_404(form.contract_id.data)
        if contract.status != "active":
            flash("只能对已生效的合同创建收款。", "error")
            return render_template("payments/create.html", form=form, contracts=contracts)

        payment = Payment(
            contract_id=contract.id,
            payer_id=contract.tenant_id,
            amount=form.amount.data,
            payment_type=form.payment_type.data,
            payment_method=form.payment_method.data,
            due_date=form.due_date.data,
            status="pending",
        )
        db.session.add(payment)
        db.session.commit()
        flash("收款单已创建，等待租客支付。", "success")
        return redirect(url_for("payments.detail", payment_id=payment.id))

    if form.contract_id.data is None and selected_contract_id:
        form.contract_id.data = selected_contract_id

    return render_template(
        "payments/create.html", form=form, contracts=contracts,
        selected_contract_id=selected_contract_id,
    )


@payments_bp.route("/<int:payment_id>/pay", methods=["POST"])
@login_required
def pay(payment_id):
    payment = Payment.query.get_or_404(payment_id)
    if current_user.id != payment.payer_id:
        flash("只有付款方才能支付。", "error")
        return redirect(url_for("payments.list_payments"))

    if payment.status != "pending":
        flash("当前状态不可支付。", "error")
        return redirect(url_for("payments.detail", payment_id=payment_id))

    payment.status = "paid"
    payment.paid_at = datetime.utcnow()
    payment.transaction_no = _generate_transaction_no()
    db.session.commit()
    flash(f"支付成功，交易号：{payment.transaction_no}", "success")
    return redirect(url_for("payments.detail", payment_id=payment_id))


@payments_bp.route("/<int:payment_id>/cancel", methods=["POST"])
@login_required
def cancel(payment_id):
    payment = Payment.query.get_or_404(payment_id)
    contract = payment.contract
    if current_user.id != contract.landlord_id:
        flash("只有房东才能取消收款单。", "error")
        return redirect(url_for("payments.list_payments"))

    if payment.status != "pending":
        flash("只有待支付状态才能取消。", "error")
        return redirect(url_for("payments.detail", payment_id=payment_id))

    payment.status = "cancelled"
    db.session.commit()
    flash("收款单已取消。", "success")
    return redirect(url_for("payments.detail", payment_id=payment_id))


@payments_bp.route("/<int:payment_id>/refund", methods=["POST"])
@login_required
def refund(payment_id):
    payment = Payment.query.get_or_404(payment_id)
    contract = payment.contract
    if current_user.id != contract.landlord_id:
        flash("只有房东才能退款。", "error")
        return redirect(url_for("payments.list_payments"))

    if payment.status != "paid":
        flash("只有已支付的收款单才能退款。", "error")
        return redirect(url_for("payments.detail", payment_id=payment_id))

    payment.status = "refunded"
    db.session.commit()
    flash("已退款。", "success")
    return redirect(url_for("payments.detail", payment_id=payment_id))

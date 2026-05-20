from datetime import datetime

from app.extensions import db


class Contract(db.Model):
    __tablename__ = "contracts"

    id = db.Column(db.BigInteger, primary_key=True)
    contract_no = db.Column(db.String(40), unique=True, nullable=False, index=True)
    house_id = db.Column(db.BigInteger, db.ForeignKey("houses.id"), nullable=False, index=True)
    tenant_id = db.Column(db.BigInteger, db.ForeignKey("users.id"), nullable=False, index=True)
    landlord_id = db.Column(db.BigInteger, db.ForeignKey("users.id"), nullable=False, index=True)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    monthly_rent = db.Column(db.Numeric(10, 2), nullable=False)
    deposit = db.Column(db.Numeric(10, 2), nullable=True)
    status = db.Column(db.String(30), default="draft", index=True)
    content = db.Column(db.Text, nullable=True)
    signed_by_landlord_at = db.Column(db.DateTime, nullable=True)
    signed_by_tenant_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    house = db.relationship("House", backref=db.backref("contracts", lazy="dynamic"))
    tenant = db.relationship("User", foreign_keys=[tenant_id], backref=db.backref("tenant_contracts", lazy="dynamic"))
    landlord = db.relationship("User", foreign_keys=[landlord_id], backref=db.backref("landlord_contracts", lazy="dynamic"))


class Payment(db.Model):
    __tablename__ = "payments"

    id = db.Column(db.BigInteger, primary_key=True)
    contract_id = db.Column(db.BigInteger, db.ForeignKey("contracts.id"), nullable=False, index=True)
    payer_id = db.Column(db.BigInteger, db.ForeignKey("users.id"), nullable=False, index=True)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    payment_type = db.Column(db.String(30), default="rent")
    payment_method = db.Column(db.String(50), default="mock")
    status = db.Column(db.String(30), default="pending", index=True)
    due_date = db.Column(db.Date, nullable=True, index=True)
    paid_at = db.Column(db.DateTime, nullable=True)
    transaction_no = db.Column(db.String(80), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    contract = db.relationship("Contract", backref=db.backref("payments", lazy="dynamic"))
    payer = db.relationship("User", backref=db.backref("payments", lazy="dynamic"))

from datetime import datetime

from app.extensions import db


class RepairRequest(db.Model):
    __tablename__ = "repair_requests"

    id = db.Column(db.BigInteger, primary_key=True)
    house_id = db.Column(db.BigInteger, db.ForeignKey("houses.id"), nullable=False, index=True)
    tenant_id = db.Column(db.BigInteger, db.ForeignKey("users.id"), nullable=False, index=True)
    handler_id = db.Column(db.BigInteger, db.ForeignKey("users.id"), nullable=True, index=True)
    title = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(30), default="pending", index=True)
    result = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    handled_at = db.Column(db.DateTime, nullable=True)

    house = db.relationship("House", backref=db.backref("repair_requests", lazy="dynamic"))
    tenant = db.relationship("User", foreign_keys=[tenant_id], backref=db.backref("repair_requests", lazy="dynamic"))
    handler = db.relationship("User", foreign_keys=[handler_id], backref=db.backref("handled_repairs", lazy="dynamic"))


class Complaint(db.Model):
    __tablename__ = "complaints"

    id = db.Column(db.BigInteger, primary_key=True)
    house_id = db.Column(db.BigInteger, db.ForeignKey("houses.id"), nullable=True, index=True)
    tenant_id = db.Column(db.BigInteger, db.ForeignKey("users.id"), nullable=False, index=True)
    target_user_id = db.Column(db.BigInteger, db.ForeignKey("users.id"), nullable=True, index=True)
    handler_id = db.Column(db.BigInteger, db.ForeignKey("users.id"), nullable=True, index=True)
    title = db.Column(db.String(120), nullable=False)
    content = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(30), default="pending", index=True)
    result = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    handled_at = db.Column(db.DateTime, nullable=True)

    house = db.relationship("House", backref=db.backref("complaints", lazy="dynamic"))
    tenant = db.relationship("User", foreign_keys=[tenant_id], backref=db.backref("complaints", lazy="dynamic"))
    target_user = db.relationship("User", foreign_keys=[target_user_id], backref=db.backref("targeted_complaints", lazy="dynamic"))
    handler = db.relationship("User", foreign_keys=[handler_id], backref=db.backref("handled_complaints", lazy="dynamic"))

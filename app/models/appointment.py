from datetime import datetime

from app.extensions import db


class Appointment(db.Model):
    __tablename__ = "appointments"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    house_id = db.Column(db.Integer, db.ForeignKey("houses.id"), nullable=False, index=True)
    tenant_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    landlord_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    appointment_time = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(30), default="pending", index=True)
    remark = db.Column(db.Text, nullable=True)
    reply = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    house = db.relationship("House", backref=db.backref("appointments", lazy="dynamic"))
    tenant = db.relationship("User", foreign_keys=[tenant_id], backref=db.backref("tenant_appointments", lazy="dynamic"))
    landlord = db.relationship("User", foreign_keys=[landlord_id], backref=db.backref("landlord_appointments", lazy="dynamic"))

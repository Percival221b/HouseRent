from datetime import datetime

from app.extensions import db


class Message(db.Model):
    __tablename__ = "messages"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    sender_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    receiver_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    house_id = db.Column(db.Integer, db.ForeignKey("houses.id"), nullable=True, index=True)
    content = db.Column(db.Text, nullable=False)
    message_type = db.Column(db.String(30), default="text")
    is_read = db.Column(db.Boolean, default=False)
    read_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    sender = db.relationship("User", foreign_keys=[sender_id], backref=db.backref("sent_messages", lazy="dynamic"))
    receiver = db.relationship("User", foreign_keys=[receiver_id], backref=db.backref("received_messages", lazy="dynamic"))
    house = db.relationship("House", backref=db.backref("messages", lazy="dynamic"))

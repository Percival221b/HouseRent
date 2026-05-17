from datetime import datetime

from app.extensions import db


class House(db.Model):
    __tablename__ = "houses"

    id = db.Column(db.Integer, primary_key=True)
    landlord_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    title = db.Column(db.String(120), nullable=False)
    address = db.Column(db.String(255), nullable=False)
    district = db.Column(db.String(80), nullable=True)
    community = db.Column(db.String(120), nullable=True)
    layout = db.Column(db.String(50), nullable=True)
    house_type = db.Column(db.String(50), nullable=True)
    area = db.Column(db.Numeric(10, 2), nullable=True)
    rent = db.Column(db.Numeric(10, 2), nullable=False)
    deposit = db.Column(db.Numeric(10, 2), nullable=True)
    decoration = db.Column(db.String(50), nullable=True)
    status = db.Column(db.String(30), default="vacant")
    description = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class HouseImage(db.Model):
    __tablename__ = "house_images"

    id = db.Column(db.Integer, primary_key=True)
    house_id = db.Column(db.Integer, db.ForeignKey("houses.id"), nullable=False)
    file_path = db.Column(db.String(255), nullable=False)
    is_cover = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


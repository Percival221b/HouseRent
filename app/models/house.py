from datetime import datetime

from app.extensions import db


class House(db.Model):
    __tablename__ = "houses"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    landlord_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    title = db.Column(db.String(120), nullable=False)
    address = db.Column(db.String(255), nullable=False)
    district = db.Column(db.String(80), nullable=True, index=True)
    business_area = db.Column(db.String(120), nullable=True)
    community = db.Column(db.String(120), nullable=True)
    layout = db.Column(db.String(50), nullable=True, index=True)
    house_type = db.Column(db.String(50), nullable=True)
    floor = db.Column(db.Integer, nullable=True)
    total_floor = db.Column(db.Integer, nullable=True)
    orientation = db.Column(db.String(30), nullable=True)
    area = db.Column(db.Numeric(10, 2), nullable=True)
    rent = db.Column(db.Numeric(10, 2), nullable=False, index=True)
    deposit = db.Column(db.Numeric(10, 2), nullable=True)
    decoration = db.Column(db.String(50), nullable=True)
    facilities = db.Column(db.JSON, nullable=True)
    status = db.Column(db.String(30), default="vacant", index=True)
    description = db.Column(db.Text, nullable=True)
    video_url = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    landlord = db.relationship("User", backref=db.backref("houses", lazy="dynamic"))
    images = db.relationship("HouseImage", backref="house", cascade="all, delete-orphan", lazy="dynamic")


class HouseImage(db.Model):
    __tablename__ = "house_images"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    house_id = db.Column(db.Integer, db.ForeignKey("houses.id"), nullable=False, index=True)
    file_path = db.Column(db.String(255), nullable=False)
    caption = db.Column(db.String(120), nullable=True)
    sort_order = db.Column(db.Integer, default=0)
    is_cover = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

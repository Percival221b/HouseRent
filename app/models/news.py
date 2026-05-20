from datetime import datetime

from app.extensions import db


class News(db.Model):
    __tablename__ = "news"

    id = db.Column(db.BigInteger, primary_key=True)
    author_id = db.Column(db.BigInteger, db.ForeignKey("users.id"), nullable=False, index=True)
    title = db.Column(db.String(150), nullable=False)
    category = db.Column(db.String(50), nullable=True)
    content = db.Column(db.Text, nullable=False)
    is_published = db.Column(db.Boolean, default=True, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    author = db.relationship("User", backref=db.backref("news_posts", lazy="dynamic"))

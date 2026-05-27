from datetime import datetime, timedelta

from flask import url_for
from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

from app.extensions import db, login_manager


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.BigInteger, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=True, index=True)
    phone = db.Column(db.String(30), unique=True, nullable=True, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default="tenant")
    real_name = db.Column(db.String(80), nullable=True)
    avatar_url = db.Column(db.String(255), nullable=True)
    id_card_number = db.Column(db.String(30), nullable=True)
    status = db.Column(db.String(20), nullable=False, default="active", index=True)
    two_factor_enabled = db.Column(db.Boolean, default=False)
    login_fail_count = db.Column(db.Integer, default=0)
    locked_until = db.Column(db.DateTime, nullable=True)
    last_login_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    @property
    def is_active(self) -> bool:
        return self.status == "active"

    @property
    def is_locked(self) -> bool:
        if self.locked_until and self.locked_until > datetime.utcnow():
            return True
        return False

    def record_failed_login(self) -> bool:
        self.login_fail_count = (self.login_fail_count or 0) + 1
        if self.login_fail_count >= 5:
            self.locked_until = datetime.utcnow() + timedelta(minutes=15)
            self.login_fail_count = 0
            db.session.commit()
            return True
        db.session.commit()
        return False

    def reset_login_fail(self) -> None:
        self.login_fail_count = 0
        self.locked_until = None
        self.last_login_at = datetime.utcnow()

    def set_password(self, password: str) -> None:
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)

    def avatar_path(self) -> str:
        if self.avatar_url:
            return url_for("static", filename=self.avatar_url.replace("app/static/", ""))
        return url_for("static", filename="images/default-avatar.png")


class VerificationCode(db.Model):
    __tablename__ = "verification_codes"

    id = db.Column(db.BigInteger, primary_key=True)
    target = db.Column(db.String(120), nullable=False, index=True)
    code = db.Column(db.String(10), nullable=False)
    code_type = db.Column(db.String(20), nullable=False, default="register")
    expires_at = db.Column(db.DateTime, nullable=False)
    used = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    @property
    def is_valid(self) -> bool:
        return not self.used and self.expires_at > datetime.utcnow()


class LoginLog(db.Model):
    __tablename__ = "login_logs"

    id = db.Column(db.BigInteger, primary_key=True)
    user_id = db.Column(db.BigInteger, db.ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    ip_address = db.Column(db.String(45), nullable=True)
    device_info = db.Column(db.String(255), nullable=True)
    status = db.Column(db.String(20), nullable=False, default="success")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


@login_manager.user_loader
def load_user(user_id: str):
    return db.session.get(User, int(user_id))

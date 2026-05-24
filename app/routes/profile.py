import os
import uuid

from flask import Blueprint, current_app, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required
from werkzeug.utils import secure_filename
from werkzeug.security import check_password_hash

from app.extensions import db
from app.utils.decorators import role_required

user_bp = Blueprint("user", __name__)

ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png"}


@user_bp.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    if request.method == "GET":
        return render_template("user/profile.html", user=current_user)

    # POST — 更新资料
    real_name = (request.form.get("real_name") or "").strip()
    phone = (request.form.get("phone") or "").strip()
    email = (request.form.get("email") or "").strip()

    if real_name:
        current_user.real_name = real_name

    if phone and phone != current_user.phone:
        from app.models.user import User
        if User.query.filter(User.phone == phone, User.id != current_user.id).first():
            flash("手机号已被使用", "error")
            return redirect(url_for("user.profile"))
        current_user.phone = phone

    if email and email != current_user.email:
        from app.models.user import User
        if User.query.filter(User.email == email, User.id != current_user.id).first():
            flash("邮箱已被使用", "error")
            return redirect(url_for("user.profile"))
        current_user.email = email

    db.session.commit()
    flash("资料已更新", "success")
    return redirect(url_for("user.profile"))


@user_bp.route("/avatar", methods=["POST"])
@login_required
def upload_avatar():
    file = request.files.get("avatar")
    if not file or not file.filename:
        flash("请选择文件", "error")
        return redirect(url_for("user.profile"))

    ext = (file.filename.rsplit(".", 1)[-1] if file.filename else "").lower()
    if ext not in ALLOWED_EXTENSIONS:
        flash("仅支持 JPG、PNG 格式", "error")
        return redirect(url_for("user.profile"))

    upload_dir = os.path.join(current_app.instance_path, "..", "app", "static", "uploads", "avatars")
    upload_dir = os.path.abspath(upload_dir)
    os.makedirs(upload_dir, exist_ok=True)

    filename = f"{current_user.id}_{uuid.uuid4().hex[:8]}.{ext}"
    filepath = os.path.join(upload_dir, filename)
    file.save(filepath)

    current_user.avatar_url = f"/static/uploads/avatars/{filename}"
    db.session.commit()

    flash("头像已更新", "success")
    return redirect(url_for("user.profile"))


@user_bp.route("/password", methods=["POST"])
@login_required
def change_password():
    old_password = request.form.get("old_password") or ""
    new_password = request.form.get("new_password") or ""
    confirm_password = request.form.get("confirm_password") or ""

    errors = []
    if not current_user.check_password(old_password):
        errors.append("原密码不正确")
    if len(new_password) < 8 or len(new_password) > 20:
        errors.append("新密码长度需为 8-20 位")
    if new_password != confirm_password:
        errors.append("两次输入的新密码不一致")
    if current_user.username.lower() in new_password.lower():
        errors.append("密码不能包含用户名")

    if errors:
        for e in errors:
            flash(e, "error")
        return redirect(url_for("user.profile"))

    current_user.set_password(new_password)
    db.session.commit()
    flash("密码已修改，请重新登录", "success")
    return redirect(url_for("auth.login"))


@user_bp.route("/history")
@login_required
def history():
    from app.models.lease import Contract, Payment

    if current_user.role == "tenant":
        contracts = (
            Contract.query
            .filter_by(tenant_id=current_user.id)
            .order_by(Contract.created_at.desc())
            .limit(20)
            .all()
        )
        return render_template("user/tenant_history.html", contracts=contracts)

    if current_user.role == "landlord":
        from app.models.house import House
        houses = (
            House.query
            .filter_by(landlord_id=current_user.id)
            .order_by(House.created_at.desc())
            .limit(20)
            .all()
        )
        return render_template("user/landlord_history.html", houses=houses)

    flash("未知角色", "error")
    return redirect(url_for("user.profile"))

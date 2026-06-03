import random
import re
from datetime import datetime, timedelta

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user

from app.extensions import db
from app.models.user import LoginLog, User, VerificationCode
from app.utils.email import send_email

auth_bp = Blueprint("auth", __name__)

USERNAME_RE = re.compile(r"^[a-zA-Z0-9_]{4,20}$")
EMAIL_RE = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")
PHONE_RE = re.compile(r"^1[3-9]\d{9}$")
PASSWORD_RE = re.compile(r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).{8,20}$")


def _generate_code() -> str:
    return str(random.randint(100000, 999999))


def _send_verification_code(target: str, code_type: str = "register") -> str:
    code = _generate_code()
    vc = VerificationCode(
        target=target,
        code=code,
        code_type=code_type,
        expires_at=datetime.utcnow() + timedelta(minutes=5),
    )
    db.session.add(vc)
    send_email(
        target,
        "房屋租赁系统注册验证码",
        f"您好，您的注册验证码是：{code}\n\n验证码 5 分钟内有效。若非本人操作，请忽略本邮件。",
    )
    db.session.commit()
    return code


def _validate_password(password: str, username: str) -> str | None:
    if len(password) < 8 or len(password) > 20:
        return "密码长度需为 8-20 位"
    if not re.search(r"[a-z]", password):
        return "密码需包含小写字母"
    if not re.search(r"[A-Z]", password):
        return "密码需包含大写字母"
    if not re.search(r"\d", password):
        return "密码需包含数字"
    if username.lower() in password.lower():
        return "密码不能包含用户名"
    return None


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))

    if request.method == "GET":
        return render_template("auth/login.html")

    # POST — 处理登录
    login_id = (request.form.get("login_id") or "").strip()
    password = request.form.get("password") or ""
    remember = request.form.get("remember") == "on"

    if not login_id or not password:
        flash("请输入账号和密码", "error")
        return render_template("auth/login.html")

    user = User.query.filter(
        (User.email == login_id) | (User.phone == login_id) | (User.username == login_id)
    ).first()

    if not user:
        log_login(None, "failed")
        flash("账号或密码错误", "error")
        return render_template("auth/login.html")

    if user.is_locked:
        remaining = int((user.locked_until - datetime.utcnow()).total_seconds() // 60) + 1
        flash(f"账号已锁定，请 {remaining} 分钟后重试", "error")
        return render_template("auth/login.html")

    if user.status == "disabled":
        flash("账号已被禁用，请联系管理员", "error")
        return render_template("auth/login.html")

    if user.status == "pending":
        flash("账号正在审核中，请等待管理员审核通过", "info")
        return render_template("auth/login.html")

    if not user.check_password(password):
        locked = user.record_failed_login()
        log_login(user.id, "failed")
        if locked:
            flash("登录失败次数过多，账号已锁定 15 分钟", "error")
        else:
            flash("账号或密码错误", "error")
        return render_template("auth/login.html")

    user.reset_login_fail()
    db.session.commit()
    login_user(user, remember=remember)
    log_login(user.id, "success")

    next_url = request.args.get("next")
    if next_url:
        return redirect(next_url)
    if user.role == "system_admin":
        return redirect("/admin/report")
    return redirect(url_for("main.index"))


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))

    if request.method == "GET":
        return render_template("auth/register.html")

    # POST — 处理注册
    username = (request.form.get("username") or "").strip()
    email = (request.form.get("email") or "").strip()
    phone = (request.form.get("phone") or "").strip()
    password = request.form.get("password") or ""
    password_confirm = request.form.get("password_confirm") or ""
    role = request.form.get("role") or "tenant"
    code = (request.form.get("code") or "").strip()
    code_type = request.form.get("code_type") or "register"

    # 校验
    errors = []
    if not USERNAME_RE.match(username):
        errors.append("用户名为 4-20 位字母、数字或下划线")
    if not EMAIL_RE.match(email):
        errors.append("邮箱格式不正确")
    if phone and not PHONE_RE.match(phone):
        errors.append("手机号格式不正确")
    if role not in ("tenant", "landlord"):
        errors.append("角色选择无效")

    pw_err = _validate_password(password, username)
    if pw_err:
        errors.append(pw_err)
    if password != password_confirm:
        errors.append("两次输入的密码不一致")

    # 唯一性检查
    if User.query.filter_by(username=username).first():
        errors.append("用户名已存在")
    if email and User.query.filter_by(email=email).first():
        errors.append("邮箱已被注册")
    if phone and User.query.filter_by(phone=phone).first():
        errors.append("手机号已被注册")

    vc = None
    if not re.fullmatch(r"\d{6}", code):
        errors.append("验证码应为 6 位数字")
    else:
        vc = (
            VerificationCode.query
            .filter_by(target=email, code=code, code_type=code_type, used=False)
            .order_by(VerificationCode.created_at.desc())
            .first()
        )
        if not vc or not vc.is_valid:
            errors.append("验证码错误或已过期")

    if errors:
        for e in errors:
            flash(e, "error")
        return render_template("auth/register.html", form=request.form)

    # 创建用户
    if vc:
        vc.used = True
    user = User(username=username, email=email, phone=phone or None, role=role)
    if user.role == "landlord":
        user.status = "pending"
    user.set_password(password)
    db.session.add(user)
    db.session.commit()

    flash("注册成功，请登录", "success")
    return redirect(url_for("auth.login"))


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("已退出登录", "info")
    return redirect(url_for("main.index"))


@auth_bp.route("/send-code", methods=["POST"])
def send_code():
    target = (request.form.get("target") or request.form.get("email") or "").strip()
    code_type = request.form.get("code_type") or "register"

    if not target:
        flash("请输入邮箱", "error")
        return render_template("auth/register.html", form=request.form)

    if not EMAIL_RE.match(target):
        flash("邮箱格式不正确", "error")
        return render_template("auth/register.html", form=request.form)

    if code_type != "register":
        flash("验证码类型无效", "error")
        return render_template("auth/register.html", form=request.form)

    if User.query.filter_by(email=target).first():
        flash("邮箱已被注册", "error")
        return render_template("auth/register.html", form=request.form)

    # 限流：1 分钟内同一目标只能发 1 条
    recent = (
        VerificationCode.query
        .filter_by(target=target)
        .order_by(VerificationCode.created_at.desc())
        .first()
    )
    if recent and (datetime.utcnow() - recent.created_at).total_seconds() < 60:
        flash("验证码发送过于频繁，请 1 分钟后重试", "error")
        return render_template("auth/register.html", form=request.form)

    try:
        _send_verification_code(target, code_type)
    except Exception:
        db.session.rollback()
        flash("验证码邮件发送失败，请检查邮箱地址或稍后重试", "error")
        return render_template("auth/register.html", form=request.form)

    flash("验证码已发送，请查收邮箱", "info")
    return render_template("auth/register.html", form=request.form)


def log_login(user_id: int | None, status: str) -> None:
    try:
        log = LoginLog(
            user_id=user_id,
            ip_address=(request.remote_addr or "")[:45],
            device_info=(request.user_agent.string or "")[:255],
            status=status,
        )
        db.session.add(log)
        db.session.commit()
    except Exception:
        db.session.rollback()

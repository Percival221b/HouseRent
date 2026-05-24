from functools import wraps

from flask import abort, flash, redirect, url_for
from flask_login import current_user, login_required  # noqa: F401


def role_required(*roles: str):
    """限制访问角色。用法: @role_required('landlord', 'admin')"""

    def decorator(f):
        @wraps(f)
        @login_required
        def wrapper(*args, **kwargs):
            if current_user.role not in roles:
                abort(403)
            return f(*args, **kwargs)

        return wrapper

    return decorator


def owner_or_admin(user_id: int):
    """资源所有者或管理员可访问。用法: @owner_or_admin(house.landlord_id)"""

    def decorator(f):
        @wraps(f)
        @login_required
        def wrapper(*args, **kwargs):
            if current_user.role == "admin" or current_user.id == user_id:
                return f(*args, **kwargs)
            abort(403)

        return wrapper

    return decorator

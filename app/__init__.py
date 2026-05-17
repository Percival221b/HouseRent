from flask import Flask

from app.config import config_by_name
from app.extensions import db, login_manager, migrate


def create_app(config_name: str | None = None) -> Flask:
    app = Flask(__name__)
    app.config.from_object(config_by_name(config_name))

    register_extensions(app)
    register_blueprints(app)
    register_error_handlers(app)

    return app


def register_extensions(app: Flask) -> None:
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"
    login_manager.login_message = "请先登录后再访问该页面。"


def register_blueprints(app: Flask) -> None:
    from app.routes.admin import admin_bp
    from app.routes.auth import auth_bp
    from app.routes.houses import houses_bp
    from app.routes.landlord import landlord_bp
    from app.routes.main import main_bp
    from app.routes.tenant import tenant_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(houses_bp, url_prefix="/houses")
    app.register_blueprint(landlord_bp, url_prefix="/landlord")
    app.register_blueprint(tenant_bp, url_prefix="/tenant")
    app.register_blueprint(admin_bp, url_prefix="/admin")


def register_error_handlers(app: Flask) -> None:
    from flask import render_template

    @app.errorhandler(403)
    def forbidden(error):
        return render_template("errors/403.html"), 403

    @app.errorhandler(404)
    def not_found(error):
        return render_template("errors/404.html"), 404

    @app.errorhandler(500)
    def internal_error(error):
        return render_template("errors/500.html"), 500


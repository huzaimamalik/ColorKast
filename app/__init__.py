import os
from datetime import timedelta
from pathlib import Path

import click
from dotenv import load_dotenv
from flask import Flask, render_template, request
from flask_wtf.csrf import CSRFError
from sqlalchemy.exc import SQLAlchemyError

from app.color_utils import format_timing
from app.extensions import csrf, db, login_manager


def create_app(test_config=None):
    load_dotenv(Path(__file__).resolve().parent.parent / ".env")
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY=os.environ.get("SECRET_KEY"),
        SQLALCHEMY_DATABASE_URI=os.environ.get("DATABASE_URL", "sqlite:///colorkast.db"),
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE="Lax",
        SESSION_COOKIE_SECURE=os.environ.get("COOKIE_SECURE", "false").lower() == "true",
        PERMANENT_SESSION_LIFETIME=timedelta(days=30),
        MAX_CONTENT_LENGTH=64 * 1024,
    )
    if test_config:
        app.config.update(test_config)
    if not app.config["SECRET_KEY"] or len(app.config["SECRET_KEY"]) < 32:
        raise RuntimeError("Set SECRET_KEY to a random value of at least 32 characters in your environment or .env.")
    Path(app.instance_path).mkdir(parents=True, exist_ok=True)
    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)

    from app.models import AdminUser
    from app.public.routes import public
    from app.admin.routes import admin
    from app.auth.routes import auth
    from app.auth.permissions import can

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(AdminUser, int(user_id)) if user_id.isdecimal() else None

    @login_manager.unauthorized_handler
    def unauthorized():
        return render_template("errors/error.html", code=403, message="Sign in as an administrator to access this page."), 403

    app.register_blueprint(public)
    app.register_blueprint(admin)
    app.register_blueprint(auth)
    app.jinja_env.globals["can"] = can
    app.jinja_env.filters["timing"] = format_timing
    register_errors(app)

    @app.after_request
    def response_headers(response):
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "same-origin"
        if request.endpoint != "static":
            response.headers["Cache-Control"] = "no-store"
        return response

    @app.cli.command("init-db")
    def init_db():
        """Create tables without deleting existing records."""
        db.create_all()
        click.echo("Database tables created.")

    @app.cli.command("seed")
    def seed_command():
        """Load deterministic demo records and environment-supplied admins."""
        from seed import seed_database
        try:
            seed_database()
        except ValueError as error:
            raise click.ClickException(str(error)) from error
        click.echo("Seed complete: 4 collections, 40 paints, 20 mappings, 3 demo admins (existing rows preserved).")

    return app


def register_errors(app):
    messages = {
        400: "The request was invalid. Check your input and try again.",
        403: "Access denied. Your administrator level does not permit this action.",
        404: "The requested page or record could not be found.",
        500: "Something went wrong on the server. Please try again later.",
    }

    def friendly_error(error):
        code = getattr(error, "code", 500)
        if code == 500:
            db.session.rollback()
        return render_template("errors/error.html", code=code, message=messages[code]), code

    for code in messages:
        app.register_error_handler(code, friendly_error)

    @app.errorhandler(CSRFError)
    def csrf_error(error):
        app.logger.info("Rejected CSRF request: %s", error.description)
        return render_template("errors/error.html", code=400, message="The form security token is missing or expired. Reload the page and submit again."), 400

    @app.errorhandler(SQLAlchemyError)
    def database_error(error):
        db.session.rollback()
        app.logger.exception("Database operation failed")
        return render_template("errors/error.html", code=500, message=messages[500]), 500

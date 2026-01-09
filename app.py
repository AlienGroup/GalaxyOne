from flask import Flask
from config import Config
from extensions import db, migrate, mail, login_manager, limiter

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)  # ✅ Needed for flask db commands
    mail.init_app(app)
    login_manager.init_app(app)
    limiter.init_app(app)

    # Register blueprints
    from routes import main_bp, admin_bp
    app.register_blueprint(main_bp)
    app.register_blueprint(admin_bp)

    return app

# This exposes the app instance for Flask CLI (e.g., flask db migrate)
app = create_app()

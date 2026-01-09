from flask import Flask
from config import Config
from extensions import db, migrate, mail, login_manager, limiter

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    mail.init_app(app)
    login_manager.init_app(app)
    limiter.init_app(app)

    # Register blueprints
    from routes import main_bp, admin_bp
    app.register_blueprint(main_bp)
    app.register_blueprint(admin_bp)

    return app

# Expose app for Flask CLI and WSGI servers (Render, Gunicorn)
app = create_app()

# Allow running locally: python app.py
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

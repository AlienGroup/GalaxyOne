import os
import re

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    # =========================
    # Basic Flask Configuration
    # =========================
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key")

    # =========================
    # Database Configuration - FIXED
    # =========================
    DATABASE_URL = os.environ.get("DATABASE_URL")
    
    if DATABASE_URL:
        # Handle both 'postgres://' and 'postgresql://' URLs
        # Heroku/Render sometimes use 'postgres://', SQLAlchemy needs 'postgresql://'
        if DATABASE_URL.startswith('postgres://'):
            DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)
        
        # Use PostgreSQL if DATABASE_URL is provided
        SQLALCHEMY_DATABASE_URI = DATABASE_URL
        print(f"Using PostgreSQL database: {DATABASE_URL[:50]}...")  # Debug logging
    else:
        # Fallback to SQLite for local development
        SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(basedir, "instance", "app.db")
        print("Using SQLite database for local development")
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # =========================
    # Flask-Mail Configuration
    # =========================
    MAIL_SERVER = "smtp.gmail.com"
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USE_SSL = False

    MAIL_USERNAME = os.environ.get(
        "MAIL_USERNAME",
        "alienemergencyfund@gmail.com"
    )
    MAIL_PASSWORD = os.environ.get(
        "MAIL_PASSWORD",
        "hqoz jlrv qqci jcqm"
    )

    MAIL_DEFAULT_SENDER = ("Alien Emergency Fund", MAIL_USERNAME)

    # =========================
    # Admin Notifications
    # =========================
    ADMIN_EMAIL = os.environ.get(
        "ADMIN_EMAIL",
        "alienemergencyfund@gmail.com"
    )

    # =========================
    # File Upload Configuration
    # =========================
    UPLOAD_FOLDER = os.path.join(basedir, "uploads")
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB

    # =========================
    # Loan Configuration
    # =========================
    INTEREST_RATE = float(os.environ.get("INTEREST_RATE", 0.05))

    # =========================
    # reCAPTCHA Configuration
    # =========================
    RECAPTCHA_PUBLIC_KEY = os.environ.get(
        "RECAPTCHA_PUBLIC_KEY",
        "6LfVbjsrAAAAAK7SzEAyo5cZ3KpIhjxLv3_QtTI9"
    )
    RECAPTCHA_PRIVATE_KEY = os.environ.get(
        "RECAPTCHA_PRIVATE_KEY",
        "6LfVbjsrAAAAACNCghqacyyWYRghSbv93z2J8LVN"
    )

    # =========================
    # PayFast (Sandbox)
    # =========================
    PAYFAST_MERCHANT_ID = os.environ.get("PAYFAST_MERCHANT_ID", "10000100")
    PAYFAST_MERCHANT_KEY = os.environ.get("PAYFAST_MERCHANT_KEY", "46f0cd694581a")

    PAYFAST_RETURN_URL = os.environ.get(
        "PAYFAST_RETURN_URL",
        "http://localhost:5000/payment-success"
    )
    PAYFAST_CANCEL_URL = os.environ.get(
        "PAYFAST_CANCEL_URL",
        "http://localhost:5000/payment-cancel"
    )
    PAYFAST_NOTIFY_URL = os.environ.get(
        "PAYFAST_NOTIFY_URL",
        "http://localhost:5000/payment-notify"
    )

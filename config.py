import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    # =========================
    # Basic Flask Configuration
    # =========================
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key")

    # =========================
    # Database Configuration
    # =========================
    # ALWAYS store SQLite DB in instance folder
    DATABASE_URL = os.environ.get("DATABASE_URL")

    if DATABASE_URL:
        # Render / Production
        SQLALCHEMY_DATABASE_URI = DATABASE_URL
    else:
        # Local development
        SQLALCHEMY_DATABASE_URI = f"sqlite:///{os.path.join(basedir, 'instance', 'app.db')}"

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # =========================
    # Ensure instance folder exists
    # =========================
    INSTANCE_PATH = os.path.join(basedir, "instance")
    os.makedirs(INSTANCE_PATH, exist_ok=True)

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
        "prbheqvherstlbld"
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
    INTEREST_RATE = float(os.environ.get("INTEREST_RATE", 0.12))

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

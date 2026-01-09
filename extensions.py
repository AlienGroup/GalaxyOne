from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_mail import Mail
from flask_login import LoginManager
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()
mail = Mail()
login_manager = LoginManager()
limiter = Limiter(key_func=get_remote_address)
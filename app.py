from flask import Flask
from config import Config
from extensions import db, migrate, mail, login_manager, limiter
import os

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    mail.init_app(app)
    login_manager.init_app(app)
    limiter.init_app(app)

    # ⬇️ ENHANCED Database Initialization ⬇️
    with app.app_context():
        # Import ALL models
        from models import User, Application, LoanFinance, Notification, Transaction
        
        print("=" * 60)
        print("DATABASE INITIALIZATION")
        print("=" * 60)
        
        # Check database connection
        try:
            from sqlalchemy import text
            db.session.execute(text('SELECT 1'))
            print("✓ Database connection successful")
        except Exception as e:
            print(f"✗ Database connection failed: {e}")
            return app  # Early return if DB connection fails
        
        # Get current tables
        from sqlalchemy import inspect
        inspector = inspect(db.engine)
        existing_tables = inspector.get_table_names()
        print(f"Existing tables: {existing_tables}")
        
        # Create all tables
        try:
            db.create_all()
            print("✓ db.create_all() executed")
            
            # Check what was created
            inspector = inspect(db.engine)
            new_tables = inspector.get_table_names()
            print(f"Tables after creation: {new_tables}")
            
            # Check for user table specifically
            if 'user' in new_tables:
                print("✓ 'user' table is ready")
                # Check columns in user table
                columns = inspector.get_columns('user')
                print(f"  Columns: {[c['name'] for c in columns]}")
            else:
                print("✗ 'user' table was NOT created")
                print(f"  Available tables: {new_tables}")
                
        except Exception as e:
            print(f"✗ Error creating tables: {e}")
            import traceback
            traceback.print_exc()
        
        print("=" * 60)
    # ⬆️ END OF DATABASE INIT ⬆️

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
from datetime import datetime
from flask_login import UserMixin
from extensions import db
from itsdangerous import URLSafeTimedSerializer
from flask import current_app
import json

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    phone = db.Column(db.String(20))
    
    # Detailed address fields - ALL NULLABLE for migration
    address_line1 = db.Column(db.String(100), nullable=True)
    address_line2 = db.Column(db.String(100), nullable=True)
    suburb = db.Column(db.String(50), nullable=True)
    city = db.Column(db.String(50), nullable=True)
    postal_code = db.Column(db.String(10), nullable=True)
    country = db.Column(db.String(50), nullable=True)
    
    total_balance = db.Column(db.Float, nullable=False, default=0.0)
    amount_due = db.Column(db.Float, nullable=False, default=0.0)
    due_date = db.Column(db.Date, default=datetime.today)
    notifications = db.relationship('Notification', backref='user', lazy=True)
    transactions = db.relationship('Transaction', backref='user', lazy=True)
    applications = db.relationship('Application', backref='user', lazy=True)
    
    def __repr__(self):
        return f'<User {self.email}>'

    # Property to get full address as string for backward compatibility
    @property
    def address(self):
        address_parts = []
        if self.address_line1:
            address_parts.append(self.address_line1)
        if self.address_line2:
            address_parts.append(self.address_line2)
        if self.suburb:
            address_parts.append(self.suburb)
        if self.city:
            address_parts.append(self.city)
        if self.postal_code:
            address_parts.append(self.postal_code)
        if self.country:
            address_parts.append(self.country)
        return ", ".join(address_parts) if address_parts else None

    # Alternative property for formatted address display
    @property
    def full_address(self):
        address_parts = []
        if self.address_line1:
            address_parts.append(self.address_line1)
        if self.address_line2:
            address_parts.append(self.address_line2)
        if self.suburb:
            address_parts.append(self.suburb)
        if self.city:
            address_parts.append(self.city)
        if self.postal_code:
            address_parts.append(self.postal_code)
        if self.country:
            address_parts.append(self.country)
        return ", ".join(address_parts) if address_parts else "No address provided"

    def get_reset_token(self):
        serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
        return serializer.dumps({'user_id': self.id})
    
    @staticmethod
    def verify_reset_token(token, expires_sec=1800):
        serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
        try:
            user_id = serializer.loads(token, max_age=expires_sec)['user_id']
        except:
            return None
        return User.query.get(user_id)


class Application(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    # Personal details (snapshot at application time)
    full_name = db.Column(db.String(100), nullable=False)
    id_number = db.Column(db.String(30), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    
    # Updated address fields - make required ones NOT NULL
    address_line1 = db.Column(db.String(100), nullable=False)
    address_line2 = db.Column(db.String(100), nullable=True)
    suburb = db.Column(db.String(50), nullable=True)
    city = db.Column(db.String(50), nullable=False)
    postal_code = db.Column(db.String(10), nullable=False)
    country = db.Column(db.String(50), nullable=False)

    # Employment and financial
    employer = db.Column(db.String(100), nullable=False)
    employer_contact = db.Column(db.String(20), nullable=False)
    job_title = db.Column(db.String(100), nullable=True)
    monthly_income = db.Column(db.Numeric(12, 2), nullable=False)
    employment_duration = db.Column(db.String(50), nullable=False)

    # Loan details
    loan_amount = db.Column(db.Numeric(12, 2), nullable=False)
    loan_term = db.Column(db.Integer, nullable=False)  # in months
    purpose = db.Column(db.String(500))
    interest_rate = db.Column(db.Float, nullable=False)

    # Status
    status = db.Column(db.String(20), default='Pending')
    admin_note = db.Column(db.String(500))
    date_submitted = db.Column(db.DateTime, default=datetime.utcnow)
    date_approved = db.Column(db.DateTime)
    date_declined = db.Column(db.DateTime)
    date_signed = db.Column(db.DateTime)
    signed_ip = db.Column(db.String(45))

    # File path storage - UPDATED FOR MULTIPLE FILES
    id_document_path = db.Column(db.String(200))  # Single file
    proof_address_path = db.Column(db.String(200))  # Single file
    
    # CHANGED: Now storing multiple files as JSON strings
    payslips_path = db.Column(db.Text, default='[]')  # JSON list of file paths
    bank_statements_path = db.Column(db.Text, default='[]')  # JSON list of file paths

    def __repr__(self):
        return f'<Application {self.id} {self.status}>'

    # Property to get full address as string
    @property
    def full_address(self):
        address_parts = []
        if self.address_line1:
            address_parts.append(self.address_line1)
        if self.address_line2:
            address_parts.append(self.address_line2)
        if self.suburb:
            address_parts.append(self.suburb)
        if self.city:
            address_parts.append(self.city)
        if self.postal_code:
            address_parts.append(self.postal_code)
        if self.country:
            address_parts.append(self.country)
        return ", ".join(address_parts) if address_parts else "No address provided"

    # Properties to get document lists with fallbacks
    @property
    def payslips_list(self):
        """Get payslips as list with backward compatibility"""
        if self.payslips_path:
            try:
                # Try to parse as JSON (new format)
                return json.loads(self.payslips_path)
            except:
                # Fallback to single file (old format)
                return [self.payslips_path] if self.payslips_path else []
        # Check old field name for backward compatibility
        elif hasattr(self, 'payslip_path') and self.payslip_path:
            return [self.payslip_path]
        return []

    @property
    def bank_statements_list(self):
        """Get bank statements as list with backward compatibility"""
        if self.bank_statements_path:
            try:
                # Try to parse as JSON (new format)
                return json.loads(self.bank_statements_path)
            except:
                # Fallback to single file (old format)
                return [self.bank_statements_path] if self.bank_statements_path else []
        # Check old field name for backward compatibility
        elif hasattr(self, 'bank_statement_path') and self.bank_statement_path:
            return [self.bank_statement_path]
        return []

    # Methods to add documents
    def add_payslip(self, file_path):
        """Add a payslip file path to the list"""
        current = self.payslips_list
        current.append(file_path)
        self.payslips_path = json.dumps(current)

    def add_bank_statement(self, file_path):
        """Add a bank statement file path to the list"""
        current = self.bank_statements_list
        current.append(file_path)
        self.bank_statements_path = json.dumps(current)


class LoanFinance(db.Model):
    __tablename__ = 'loan_finance'

    id = db.Column(db.Integer, primary_key=True)

    application_id = db.Column(
        db.Integer,
        db.ForeignKey('application.id'),
        nullable=False
    )
    user_id = db.Column(
        db.Integer,
        db.ForeignKey('user.id'),
        nullable=False
    )

    loan_amount = db.Column(db.Numeric(12, 2), nullable=False)
    total_repayment = db.Column(db.Numeric(12, 2), nullable=False)
    monthly_installment = db.Column(db.Numeric(12, 2), nullable=False)

    amount_paid = db.Column(db.Numeric(12, 2), default=0)
    balance_remaining = db.Column(db.Numeric(12, 2), nullable=False)

    funds_released = db.Column(db.Boolean, default=False)
    date_released = db.Column(db.DateTime)

    status = db.Column(
        db.String(20),
        default='Active'
    )  # Active | Paid | In Arrears

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # OPTIONAL (but recommended)
    application = db.relationship('Application', backref='finance')
    user = db.relationship('User', backref='loans')


class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    message = db.Column(db.String(255), nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Notification {self.id} for User {self.user_id}>'


class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    type = db.Column(db.String(20), nullable=False)  # e.g., "Payment", "Disbursement", "Refund"
    status = db.Column(db.String(20), default="Completed")  # e.g., "Completed", "Pending", "Failed"
    reference = db.Column(db.String(100))
    description = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Transaction {self.id} {self.type} {self.amount}>'
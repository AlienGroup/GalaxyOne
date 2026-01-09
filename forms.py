from flask_wtf import FlaskForm, RecaptchaField
from wtforms import (
    StringField, PasswordField, BooleanField, SubmitField,
    IntegerField, DecimalField, TextAreaField,
    MultipleFileField, SelectField
)
from wtforms.validators import DataRequired, Email, EqualTo, Length, NumberRange, Optional, ValidationError
from flask_wtf.file import FileField, FileAllowed, FileRequired

ALLOWED_FILE_EXTENSIONS = ['jpg', 'jpeg', 'png', 'pdf']

# Custom validator for multiple files
def multiple_files_required(min_files=1):
    def _multiple_files_required(form, field):
        if len(field.data) == 0 or not any(field.data):
            raise ValidationError(f'At least {min_files} file(s) are required.')
        # Count actual files with filenames
        valid_files = [f for f in field.data if f and f.filename]
        if len(valid_files) < min_files:
            raise ValidationError(f'At least {min_files} file(s) are required.')
    return _multiple_files_required

class RegistrationForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired(), Length(max=50)])
    last_name = StringField('Last Name', validators=[DataRequired(), Length(max=50)])
    email = StringField('Email', validators=[DataRequired(), Email(), Length(max=120)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password', message='Passwords must match')])
    submit = SubmitField('Sign Up')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')

class ForgotPasswordForm(FlaskForm):
    email = StringField('Enter your registered email address', validators=[DataRequired(), Email()])
    recaptcha = RecaptchaField()
    submit = SubmitField('Request Password Reset')

class ResetPasswordForm(FlaskForm):
    password = PasswordField('New Password', validators=[DataRequired(), Length(min=6)])
    confirm = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Reset Password')

class LoanApplicationForm(FlaskForm):
    # Personal details
    full_name = StringField('Full Name', validators=[DataRequired()])
    id_number = StringField('South African ID Number', validators=[DataRequired(), Length(min=6, max=30)])
    email = StringField('Email Address', validators=[DataRequired(), Email()])
    phone = StringField('Mobile Number', validators=[DataRequired(), Length(min=8, max=20)])
    
    # Enhanced Address Fields
    address_line1 = StringField('Address Line 1', validators=[DataRequired(), Length(max=100)])
    address_line2 = StringField('Address Line 2 (Optional)', validators=[Optional(), Length(max=100)])
    suburb = StringField('Suburb (Optional)', validators=[Optional(), Length(max=50)])
    city = StringField('City', validators=[DataRequired(), Length(max=50)])
    postal_code = StringField('Postal Code', validators=[DataRequired(), Length(min=4, max=4)])
    country = SelectField('Country', choices=[
        ('', 'Select Country'),
        ('South Africa', 'South Africa'),
        ('Lesotho', 'Lesotho'),
        ('Botswana', 'Botswana'),
        ('Namibia', 'Namibia'),
        ('Eswatini', 'Eswatini'),
        ('Mozambique', 'Mozambique'),
        ('Zimbabwe', 'Zimbabwe'),
        ('Other', 'Other')
    ], validators=[DataRequired()])

    # Employment
    employer = StringField('Employer Name', validators=[DataRequired(), Length(max=100)])
    employer_contact = StringField('Employer Contact', validators=[DataRequired(), Length(min=8, max=20)])
    job_title = StringField('Job Title', validators=[Optional(), Length(max=100)])
    monthly_income = DecimalField('Net Monthly Income (R)', places=2, validators=[DataRequired()])
    employment_duration = StringField('Employment Duration', validators=[DataRequired(), Length(max=100)])

    # Loan
    loan_amount = DecimalField('Loan Amount Needed (ZAR)', places=2, validators=[DataRequired(), NumberRange(min=1000)])
    loan_term = IntegerField('Repayment Term', validators=[DataRequired(), NumberRange(min=1, max=60)])
    purpose = SelectField('Purpose of Loan', choices=[
        ('', 'Select...'),
        ('medical', 'Medical Expenses'),
        ('education', 'Education Fees'),
        ('transport', 'Transport/Vehicle Repair'),
        ('rent', 'Rent/Bond Payment'),
        ('utilities', 'Utilities/Accounts'),
        ('other', 'Other Emergency')
    ], validators=[DataRequired()])

    # File uploads with render_kw to support custom styling & JS preview
    id_document = FileField(
        'RSA ID/Smart ID Copy',
        validators=[FileRequired(), FileAllowed(ALLOWED_FILE_EXTENSIONS, 'PDF/JPG/PNG only!')],
        render_kw={"id": "id_document", "style": "display:none;"}
    )
    proof_address = FileField(
        'Proof of Address',
        validators=[FileRequired(), FileAllowed(ALLOWED_FILE_EXTENSIONS, 'PDF/JPG/PNG only!')],
        render_kw={"id": "proof_address", "style": "display:none;"}
    )
    payslips = MultipleFileField(
        '3 Recent Payslips',
        validators=[
            multiple_files_required(min_files=1),  # Custom validator - require at least 1 file
            FileAllowed(ALLOWED_FILE_EXTENSIONS, 'PDF/JPG/PNG only!')
        ],
        render_kw={"id": "payslips", "multiple": True, "style": "display:none;"}
    )
    bank_statements = MultipleFileField(
        '3 Month Bank Statements',
        validators=[
            multiple_files_required(min_files=1),  # Custom validator - require at least 1 file
            FileAllowed(ALLOWED_FILE_EXTENSIONS, 'PDF/JPG/PNG only!')
        ],
        render_kw={"id": "bank_statements", "multiple": True, "style": "display:none;"}
    )

    # Consent
    accept_terms = BooleanField('I agree to the Terms and Conditions and consent to data processing (NCA, POPIA compliance).', validators=[DataRequired()])
    submit = SubmitField('Submit Application')

class FeedbackForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(max=100)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    message = TextAreaField('Message', validators=[DataRequired(), Length(max=1000)])
    submit = SubmitField('Send Feedback')

class DecisionForm(FlaskForm):
    note = TextAreaField('Admin Notes', validators=[Optional(), Length(max=500)])
    submit_approve = SubmitField('Approve Application')
    submit_decline = SubmitField('Decline Application')

class EditProfileForm(FlaskForm):
    # Email field for profile editing
    email = StringField('Email Address', validators=[DataRequired(), Email(), Length(max=120)])
    
    # Phone field with South African validation
    phone = StringField('Phone Number', validators=[DataRequired(), Length(min=9, max=9, message='Phone number must be 9 digits (without +27)')])
    
    # Enhanced Address Fields
    address_line1 = StringField('Address Line 1', validators=[DataRequired(), Length(max=100)])
    address_line2 = StringField('Address Line 2 (Optional)', validators=[Optional(), Length(max=100)])
    suburb = StringField('Suburb (Optional)', validators=[Optional(), Length(max=50)])
    city = StringField('City', validators=[DataRequired(), Length(max=50)])
    postal_code = StringField('Postal Code', validators=[DataRequired(), Length(min=4, max=4, message='Postal code must be 4 digits')])
    country = SelectField('Country', choices=[
        ('', 'Select Country'),
        ('South Africa', 'South Africa'),
        ('Lesotho', 'Lesotho'),
        ('Botswana', 'Botswana'),
        ('Namibia', 'Namibia'),
        ('Eswatini', 'Eswatini'),
        ('Mozambique', 'Mozambique'),
        ('Zimbabwe', 'Zimbabwe'),
        ('Other', 'Other')
    ], validators=[DataRequired()])
    
    submit = SubmitField('Save Changes')
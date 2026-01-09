from flask import Blueprint, render_template, redirect, url_for, request, flash, abort, current_app, send_from_directory
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from datetime import datetime
import os
from models import User, Application, LoanFinance
from extensions import db, mail, login_manager, limiter
from forms import RegistrationForm, LoginForm, LoanApplicationForm, FeedbackForm, DecisionForm, ForgotPasswordForm, EditProfileForm, ResetPasswordForm
from flask_mail import Message, Mail
from app import mail
from utils.payfast import generate_payfast_url
from utils.pdf import generate_contract_pdf
from sqlalchemy import or_, cast, String
import json
from decimal import Decimal

main_bp = Blueprint('main', __name__)
admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Ensure login view for @login_required
login_manager.login_view = 'main.login'
login_manager.login_message_category = 'info'

@main_bp.route("/profile", methods=["GET"])
@login_required
def profile():
    return render_template("profile.html")  # This shows the profile

@main_bp.route("/edit-profile", methods=["GET", "POST"])
@login_required
def edit_profile():
    form = EditProfileForm(obj=current_user)
    if form.validate_on_submit():
        current_user.phone = form.phone.data
        # Update detailed address fields
        current_user.address_line1 = form.address_line1.data
        current_user.address_line2 = form.address_line2.data
        current_user.suburb = form.suburb.data
        current_user.city = form.city.data
        current_user.postal_code = form.postal_code.data
        current_user.country = form.country.data
        
        db.session.commit()
        flash("Your profile has been updated.", "success")
        return redirect(url_for("main.profile"))
    return render_template("edit_profile.html", form=form)

@main_bp.route('/forgot-password', methods=['GET', 'POST'])
@limiter.limit("3 per hour")
def forgot_password():
    form = ForgotPasswordForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.strip().lower()).first()
        if user:
            token = user.get_reset_token()
            reset_url = url_for('main.reset_password', token=token, _external=True)
            msg = Message('Password Reset Request',
                          recipients=[user.email])
            msg.body = f'''To reset your password, click the link below:

{reset_url}

If you did not request this, please ignore this email.
'''
            try:
                mail.send(msg)
            except Exception as e:
                print("Email failed:", e)
        flash('If your email is registered, a reset link has been sent.', 'info')
        return redirect(url_for('main.login'))
    return render_template('forgot_password.html', form=form)

@main_bp.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    user = User.verify_reset_token(token)
    if not user:
        flash('Invalid or expired token.', 'danger')
        return redirect(url_for('main.forgot_password'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.password_hash = generate_password_hash(form.password.data)
        db.session.commit()
        flash('Your password has been updated. You can now log in.', 'success')
        return redirect(url_for('main.login'))
    return render_template('reset_password.html', form=form)

@main_bp.route('/')
def index():
    return render_template('index.html')

@main_bp.route('/calculator')
def calculator():
    return render_template('calculator.html')

@main_bp.route('/about')
def about_us():
    return render_template('about_us.html')

@main_bp.route('/privacy')
def privacy():
    return render_template('privacy.html')

@main_bp.route('/terms')
def terms():
    return render_template('terms.html')

@main_bp.route('/faq')
def faq():
    return render_template('faq.html')

@main_bp.route('/compliance')
def compliance():
    return render_template('compliance.html')


@main_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        # Check if email already exists
        existing_user = User.query.filter_by(email=form.email.data.lower()).first()
        if existing_user:
            flash('An account with that email already exists.', 'warning')
            return render_template('register.html', form=form)
        # Create new user
        new_user = User(
            first_name=form.first_name.data.strip(),
            last_name=form.last_name.data.strip(),
            email=form.email.data.lower().strip(),
            password_hash=generate_password_hash(form.password.data),
            is_admin=False
        )
        db.session.add(new_user)
        db.session.commit()
        flash('Registration successful! You can now log in.', 'success')
        return redirect(url_for('main.login'))
    return render_template('register.html', form=form)

@main_bp.route('/login', methods=['GET', 'POST'])
@limiter.limit("5 per minute")
def login():
    if current_user.is_authenticated:
        # redirect to appropriate dashboard
        if current_user.is_admin:
            return redirect(url_for('admin.index'))
        else:
            return redirect(url_for('main.dashboard'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower()).first()
        if user and check_password_hash(user.password_hash, form.password.data):
            login_user(user, remember=form.remember.data)
            # after login, go to next page if exists
            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
            else:
                if user.is_admin:
                    return redirect(url_for('admin.index'))
                else:
                    return redirect(url_for('main.dashboard'))
        else:
            flash('Invalid email or password. Please try again.', 'danger')
    return render_template('login.html', form=form)

@main_bp.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form.get('fullName')
        email = request.form.get('email')
        message = request.form.get('message')

        if not name or not email or not message:
            flash('All fields are required.', 'danger')
            return redirect(url_for('main.contact'))

        # Email to admin
        admin_msg = Message(
            subject='New Contact Form Message',
            recipients=[current_app.config['ADMIN_EMAIL']],
            body=f"""
New contact form submission:

Name: {name}
Email: {email}

Message:
{message}
"""
        )
        mail.send(admin_msg)

        # Confirmation email to user
        user_msg = Message(
            subject='We received your message',
            recipients=[email],
            body=f"""
Hi {name},

Thank you for contacting Alien Emergency Fund.
We have received your message and will respond within 24 hours.

Regards,
Alien Emergency Fund
"""
        )
        mail.send(user_msg)

        flash('Message sent successfully!', 'success')
        return redirect(url_for('main.contact'))

    return render_template('feedback.html')


@main_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('main.index'))
    
@main_bp.route('/uploads/<path:filename>')
@login_required
def uploaded_file(filename):
    return send_from_directory(current_app.config['UPLOAD_FOLDER'], filename)

@main_bp.route('/apply', methods=['GET', 'POST'])
@login_required
def apply():
    if current_user.is_admin:
        flash('Admins cannot apply for loans.', 'danger')
        return redirect(url_for('main.index'))

    existing = Application.query.filter(
        Application.user_id == current_user.id,
        Application.status.in_(['Pending', 'Approved'])
    ).first()
    if existing:
        flash('You already have an application in progress.', 'warning')
        return redirect(url_for('main.dashboard'))

    form = LoanApplicationForm()

    if request.method == 'GET':
        form.email.data = current_user.email
        # Pre-fill with user's existing address if available
        if current_user.address_line1:
            form.address_line1.data = current_user.address_line1
            form.address_line2.data = current_user.address_line2
            form.suburb.data = current_user.suburb
            form.city.data = current_user.city
            form.postal_code.data = current_user.postal_code
            form.country.data = current_user.country

    if form.validate_on_submit():
        # Parse full name
        full_name = form.full_name.data.strip()
        first_name, last_name = (full_name.split(' ', 1) + [''])[:2]

        try:
            interest_rate = float(os.getenv('INTEREST_RATE', 0.12))
        except:
            interest_rate = 0.12

        # Create the application with detailed address fields
        application = Application(
            user_id=current_user.id,
            full_name=full_name,
            id_number=form.id_number.data.strip(),
            email=form.email.data.strip(),
            phone=form.phone.data.strip(),
            # Updated: Use detailed address fields instead of single address field
            address_line1=form.address_line1.data.strip(),
            address_line2=form.address_line2.data.strip() if form.address_line2.data else None,
            suburb=form.suburb.data.strip() if form.suburb.data else None,
            city=form.city.data.strip(),
            postal_code=form.postal_code.data.strip(),
            country=form.country.data,
            employer=form.employer.data.strip(),
            employer_contact=form.employer_contact.data.strip(),
            job_title=form.job_title.data.strip() if form.job_title.data else '',
            monthly_income=form.monthly_income.data,
            employment_duration=form.employment_duration.data.strip(),
            loan_amount=form.loan_amount.data,
            loan_term=form.loan_term.data,
            purpose=form.purpose.data,
            interest_rate=interest_rate,
            status='Pending',
            date_submitted=datetime.utcnow()
        )

        db.session.add(application)
        db.session.commit()
        app_id = application.id

        # File upload directory
        upload_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], str(app_id))
        os.makedirs(upload_dir, exist_ok=True)

        def save_file(file, prefix):
            if file and file.filename:  # Check if file exists and has filename
                filename = secure_filename(file.filename)
                path = os.path.join(upload_dir, f"{prefix}_{filename}")
                file.save(path)
                return f'uploads/{app_id}/{prefix}_{filename}'
            return None

        # Save single files
        application.id_document_path = save_file(form.id_document.data, 'id')
        application.proof_address_path = save_file(form.proof_address.data, 'address')

        # Save multiple payslips as JSON
        payslip_paths = []
        for i, file in enumerate(form.payslips.data):
            if file and file.filename:
                payslip_paths.append(save_file(file, f"payslip_{i}"))
        application.payslips_path = json.dumps(payslip_paths)  # Using payslips_path (with 's') and JSON

        # Save multiple bank statements as JSON
        bank_paths = []
        for i, file in enumerate(form.bank_statements.data):
            if file and file.filename:
                bank_paths.append(save_file(file, f"bank_{i}"))
        application.bank_statements_path = json.dumps(bank_paths)  # Using bank_statements_path (with 's') and JSON

        db.session.commit()

        # Admin email notification
        try:
            admin_email = os.getenv('ADMIN_EMAIL')
            if admin_email:
                msg = Message(f'Loan Application #{app_id}', recipients=[admin_email])
                msg.body = (
                    f"New loan application submitted by {full_name}.\n"
                    f"Loan: R{application.loan_amount} over {application.loan_term} months.\n\n"
                    f"Approve: {request.url_root.rstrip('/')}/admin/approve/{app_id}\n"
                    f"Decline: {request.url_root.rstrip('/')}/admin/decline/{app_id}"
                )
                mail.send(msg)
        except Exception as e:
            print(f"[EMAIL TO ADMIN FAILED]: {e}")

        # Applicant email notification
        try:
            msg = Message('Loan Application Received', recipients=[application.email])
            msg.body = (
                f"Dear {application.full_name},\n\n"
                f"Your loan application (Ref #{app_id}) has been received successfully.\n"
                f"Our team will review it and update you shortly.\n\n"
                f"Regards,\nAlien Emergency Fund"
            )
            mail.send(msg)
        except Exception as e:
            print(f"[EMAIL TO APPLICANT FAILED]: {e}")

        flash('Your loan application was submitted successfully!', 'success')
        return redirect(url_for('main.dashboard'))

    return render_template('application_form.html', form=form)
    
@main_bp.route('/dashboard')
@login_required
def dashboard():
    if current_user.is_admin:
        return redirect(url_for('admin.index'))

    applications = Application.query.filter_by(
        user_id=current_user.id
    ).order_by(Application.date_submitted.desc()).all()

    loan_finance = LoanFinance.query.filter_by(
        user_id=current_user.id
    ).order_by(LoanFinance.created_at.desc()).first()

    return render_template(
        'dashboard.html',
        applications=applications,
        loan_finance=loan_finance
    )

@main_bp.route("/pay-now")
@login_required
def pay_now():
    amount_due = current_user.amount_due or 0

    if amount_due <= 0:
        flash("You don't have any payments due.", "info")
        return redirect(url_for("main.dashboard"))

    payfast_url = generate_payfast_url(current_user)
    return redirect(payfast_url)

@main_bp.route("/payfast/ipn", methods=["POST"])
def payfast_ipn():
    from utils.payfast_ipn import verify_payfast_ipn

    data = request.form.to_dict()
    is_valid, reason = verify_payfast_ipn(data)

    if not is_valid:
        current_app.logger.warning(f"PayFast IPN failed: {reason}")
        return "INVALID", 400

    payment_status = data.get("payment_status")
    payment_id = data.get("m_payment_id")
    amount_paid = float(data.get("amount_gross", 0))

    if payment_status != "COMPLETE":
        return "IGNORED", 200

    # Extract user ID
    try:
        user_id = int(payment_id.split("-")[1])
    except Exception:
        return "INVALID", 400

    user = User.query.get(user_id)
    if not user:
        return "USER NOT FOUND", 404

    # ✅ Prevent double payment
    if user.amount_due <= 0:
        return "ALREADY PAID", 200

    # ✅ Amount validation
    if round(user.amount_due, 2) != round(amount_paid, 2):
        current_app.logger.error("Amount mismatch")
        return "AMOUNT MISMATCH", 400

    # ✅ MARK AS PAID
    user.amount_due = 0
    user.total_balance = 0
    db.session.commit()

    return "OK", 200

@main_bp.route("/payment-success")
@login_required
def payment_success():
    flash("Payment received. Processing confirmation…", "success")
    return render_template("payment_success.html")

@main_bp.route("/payment-cancel")
@login_required
def payment_cancel():
    flash("Payment was cancelled.", "warning")
    return render_template("payment_cancel.html")

@main_bp.route('/application/<int:app_id>/sign', methods=['GET', 'POST'])
@login_required
def sign_contract(app_id):
    app_data = Application.query.get_or_404(app_id)

    # Ownership check
    if app_data.user_id != current_user.id:
        abort(403)

    # Status check
    if app_data.status != 'Approved':
        flash('This application is not available for signing.', 'warning')
        return redirect(url_for('main.dashboard'))

    # === CALCULATE PAYMENT DETAILS ===
    loan_amount = float(app_data.loan_amount)
    interest_rate = float(app_data.interest_rate)  # annual
    loan_term = int(app_data.loan_term)             # months

    total_interest = loan_amount * interest_rate
    total_payment = loan_amount + total_interest
    monthly_payment = total_payment / loan_term

    if request.method == 'POST':
        # === UPDATE STATUS + LEGAL METADATA ===
        app_data.status = 'Signed'
        app_data.date_signed = datetime.utcnow()
        app_data.signed_ip = request.remote_addr
        db.session.commit()

        # === CREATE LOAN FINANCE RECORD (ONLY AFTER SIGNING) ===
        from models import LoanFinance

        existing_finance = LoanFinance.query.filter_by(
            application_id=app_data.id
        ).first()

        if not existing_finance:
            finance = LoanFinance(
                application_id=app_data.id,
                user_id=app_data.user_id,
                loan_amount=loan_amount,
                total_repayment=total_payment,
                monthly_installment=monthly_payment,
                amount_paid=0,
                balance_remaining=total_payment,
                funds_released=False,
                status='Pending Release'
            )
            db.session.add(finance)
            db.session.commit()

        # === GENERATE CONTRACT PDF ===
        pdf_path = None
        try:
            pdf_path = generate_contract_pdf(
                app_data,
                monthly_payment,
                total_payment
            )
            print("PDF GENERATED AT:", pdf_path)
        except Exception as e:
            print("PDF generation failed HARD:", str(e))


        # === EMAIL ADMIN ===
        try:
            admin_email = current_app.config.get('ADMIN_EMAIL')
            if admin_email:
                admin_msg = Message(
                    subject=f'Application #{app_id} Contract Signed',
                    recipients=[admin_email]
                )
                admin_msg.body = (
                    f'Applicant {app_data.full_name} has signed '
                    f'the loan agreement for application #{app_id}.'
                )
                mail.send(admin_msg)
        except Exception as e:
            print("Failed to send admin email:", e)

        # === EMAIL APPLICANT WITH PDF ===
        try:
            applicant_msg = Message(
                subject="Your Loan Agreement Has Been Signed",
                recipients=[app_data.email]
            )

            applicant_msg.body = f"""
Dear {app_data.full_name},

Thank you for signing your loan agreement.

Loan Amount: R{loan_amount:,.2f}
Total Repayment: R{total_payment:,.2f}
Monthly Repayment: R{monthly_payment:,.2f}
Loan Term: {loan_term} months

💰 PAYOUT TIMELINE
Funds will be deposited within 1–2 business days after
final verification of your bank statements.

📞 NEED ASSISTANCE?
Email: alienemergencyfund@gmail.com
Office Hours: Monday–Friday, 08:00–17:00

Please find your signed loan agreement attached.

Kind regards,
Alien Emergency Fund
"""

            if pdf_path and os.path.exists(pdf_path):
                with open(pdf_path, 'rb') as f:
                    applicant_msg.attach(
                        filename=f'Loan_Contract_{app_data.id}.pdf',
                        content_type='application/pdf',
                        data=f.read()
                    )

            mail.send(applicant_msg)

        except Exception as e:
            print("Failed to send applicant email:", e)

        flash(
            'Contract signed successfully. A copy has been emailed to you. '
            'Funds will be deposited within 1–2 business days.',
            'success'
        )
        return redirect(url_for('main.dashboard'))

    # === RENDER SIGNING PAGE ===
    return render_template(
        'sign_contract.html',
        application=app_data,
        monthly_payment=monthly_payment,
        total_payment=total_payment
    )

@main_bp.route('/feedback', methods=['GET', 'POST'])
def feedback():
    form = FeedbackForm()
    if form.validate_on_submit():
        # In a real app, this could send an email or save to DB
        try:
            admin_email = os.getenv('ADMIN_EMAIL', None)
            if admin_email:
                msg = Message('Website Feedback', recipients=[admin_email])
                msg.body = f"From: {form.name.data} <{form.email.data}>\n\nMessage:\n{form.message.data}"
                mail.send(msg)
        except Exception as e:
            print("Failed to send feedback email:", e)
        flash('Thank you for your feedback!', 'success')
        return redirect(url_for('main.index'))
    return render_template('feedback.html', form=form)


@admin_bp.route('/')
@login_required
def index():
    if not current_user.is_admin:
        abort(403)
    # Gather stats for dashboard
    total = Application.query.count()
    pending = Application.query.filter_by(status='Pending').count()
    approved = Application.query.filter_by(status='Approved').count()
    signed = Application.query.filter_by(status='Signed').count()
    declined = Application.query.filter_by(status='Declined').count()
    return render_template('admin_dashboard.html', total=total, pending=pending, approved=approved, signed=signed, declined=declined)

@admin_bp.route('/applications')
@login_required
def list_applications():
    if not current_user.is_admin:
        abort(403)
    
    status_filter = request.args.get('status')
    search_term = request.args.get('search', '').lower()
    
    # Start with base query
    query = Application.query
    
    # Apply status filter if provided
    if status_filter and status_filter in ['Pending', 'Approved', 'Signed', 'Declined']:
        query = query.filter_by(status=status_filter)
    else:
        status_filter = 'All'
    
    # Get all applications
    applications = query.order_by(Application.date_submitted.desc()).all()
    
    # Apply search filter in Python if provided
    if search_term:
        filtered_applications = []
        for app in applications:
            # Search in full_name and ID
            if (search_term in app.full_name.lower() or 
                search_term in str(app.id)):
                filtered_applications.append(app)
        
        applications = filtered_applications
    
    return render_template('admin_applications.html', 
                         applications=applications, 
                         filter=status_filter)

@admin_bp.route('/application/<int:app_id>', methods=['GET', 'POST'])
@login_required
def view_application(app_id):
    if not current_user.is_admin:
        abort(403)

    app_data = Application.query.get_or_404(app_id)
    form = DecisionForm()

    if form.validate_on_submit():
        if form.submit_approve.data and app_data.status == 'Pending':
            app_data.status = 'Approved'
            app_data.date_approved = datetime.utcnow()
            if form.note.data:
                app_data.admin_note = form.note.data
            db.session.commit()

            # Send approval email
            try:
                recipient_name = app_data.full_name
                msg = Message('Your loan application is Approved', recipients=[app_data.email])
                msg.body = (
                    f"Dear {recipient_name},\n\n"
                    f"Congratulations! Your loan application #{app_id} has been approved.\n"
                    f"Please visit the following link to review and sign your loan agreement:\n"
                    f"{request.url_root}application/{app_id}/sign\n\n"
                    f"Thank you for choosing Alien Emergency Fund."
                )
                mail.send(msg)
            except Exception as e:
                print(f"[EMAIL ERROR - APPROVAL]: {e}")

            flash('Application approved and applicant notified.', 'success')
            return redirect(url_for('admin.list_applications'))

        elif form.submit_decline.data and app_data.status == 'Pending':
            app_data.status = 'Declined'
            app_data.date_declined = datetime.utcnow()
            if form.note.data:
                app_data.admin_note = form.note.data
            db.session.commit()

            # Send decline email
            try:
                recipient_name = app_data.full_name
                msg = Message('Loan Application Update', recipients=[app_data.email])
                msg.body = (
                    f"Dear {recipient_name},\n\n"
                    f"Unfortunately, your loan application #{app_id} has not been approved."
                    f"{' Reason: ' + form.note.data if form.note.data else ''}\n\n"
                    f"You are welcome to apply again in the future.\n\n"
                    f"Regards,\nAlien Emergency Fund"
                )
                mail.send(msg)
            except Exception as e:
                print(f"[EMAIL ERROR - DECLINE]: {e}")

            flash('Application declined and applicant notified.', 'info')
            return redirect(url_for('admin.list_applications'))

    return render_template('admin_application_view.html', application=app_data, form=form)


@admin_bp.route('/approve/<int:app_id>')
@login_required
def quick_approve(app_id):
    if not current_user.is_admin:
        abort(403)

    app_data = Application.query.get_or_404(app_id)

    if app_data.status != 'Pending':
        flash('Cannot approve this application.', 'warning')
        return redirect(url_for('admin.list_applications'))

    # ✅ APPROVE APPLICATION
    app_data.status = 'Approved'
    app_data.date_approved = datetime.utcnow()
    db.session.commit()

    # ✅ SEND APPROVAL EMAIL (APPLICANT)
    try:
        msg = Message(
            subject='Your Loan Application Has Been Approved',
            recipients=[app_data.email]
        )
        msg.body = f"""
Dear {app_data.full_name},

Congratulations! 🎉

Your loan application (Reference #{app_data.id}) has been approved.

NEXT STEP:
Please review and sign your loan agreement using the link below:

{request.url_root}application/{app_data.id}/sign

Once signed, funds will be released within 1–2 business days,
subject to final verification of your bank statements.

If you have any questions, contact us at:
alienemergencyfund@gmail.com

Kind regards,
Alien Emergency Fund
"""

        mail.send(msg)
        print(f"[APPROVAL EMAIL SENT] Application #{app_id}")

    except Exception as e:
        print(f"[EMAIL ERROR - QUICK APPROVE]: {e}")

    flash(f'Application #{app_id} approved and applicant notified.', 'success')
    return redirect(url_for('admin.list_applications', status='Pending'))


@admin_bp.route('/decline/<int:app_id>')
@login_required
def quick_decline(app_id):
    if not current_user.is_admin:
        abort(403)

    app_data = Application.query.get_or_404(app_id)
    if app_data.status != 'Pending':
        flash('Cannot decline this application.', 'warning')
        return redirect(url_for('admin.list_applications'))

    app_data.status = 'Declined'
    app_data.date_declined = datetime.utcnow()
    db.session.commit()

    # Send decline email
    try:
        recipient_name = app_data.full_name
        msg = Message('Loan Application Update', recipients=[app_data.email])
        msg.body = (
            f"Dear {recipient_name},\n\n"
            f"We regret to inform you that your loan application #{app_id} has not been approved.\n\n"
            f"We encourage you to try again in the future.\n\n"
            f"Regards,\nAlien Emergency Fund"
        )
        mail.send(msg)
    except Exception as e:
        print(f"[EMAIL ERROR - QUICK DECLINE]: {e}")

    flash(f'Application #{app_id} declined.', 'info')
    return redirect(url_for('admin.list_applications', status='Pending'))

@admin_bp.route('/finance')
@login_required
def finance_dashboard():
    if not current_user.is_admin:
        abort(403)

    status = request.args.get('status')
    funds = request.args.get('funds')
    app_id = request.args.get('application_id')
    user_id = request.args.get('user_id')

    query = LoanFinance.query

    if status:
        query = query.filter(LoanFinance.status == status)

    if funds == 'released':
        query = query.filter(LoanFinance.funds_released.is_(True))
    elif funds == 'pending':
        query = query.filter(LoanFinance.funds_released.is_(False))

    if app_id:
        query = query.filter(LoanFinance.application_id == app_id)

    if user_id:
        query = query.filter(LoanFinance.user_id == user_id)

    loans = query.order_by(LoanFinance.created_at.desc()).all()

    return render_template(
        'admin_finance.html',
        loans=loans
    )

@admin_bp.route('/finance/release/<int:finance_id>', methods=['POST'])
@login_required
def release_funds(finance_id):
    if not current_user.is_admin:
        abort(403)

    finance = LoanFinance.query.get_or_404(finance_id)
    application = Application.query.get(finance.application_id)

    if application.status != 'Signed':
        flash('Cannot release funds before contract is signed.', 'danger')
        return redirect(url_for('admin.finance_dashboard'))

    if finance.funds_released:
        flash('Funds already released.', 'warning')
        return redirect(url_for('admin.finance_dashboard'))

    finance.funds_released = True
    finance.date_released = datetime.utcnow()
    finance.status = 'Active'

    db.session.commit()

    flash('Funds released successfully.', 'success')
    return redirect(url_for('admin.finance_dashboard'))

@admin_bp.route('/finance/repayment/<int:finance_id>', methods=['POST'])
@login_required
def record_repayment(finance_id):
    if not current_user.is_admin:
        abort(403)

    finance = LoanFinance.query.get_or_404(finance_id)

    try:
        amount = Decimal(request.form.get('amount'))
    except:
        flash('Invalid repayment amount.', 'danger')
        return redirect(url_for('admin.finance_dashboard'))

    if amount <= 0:
        flash('Invalid repayment amount.', 'danger')
        return redirect(url_for('admin.finance_dashboard'))

    finance.amount_paid += amount
    finance.balance_remaining -= amount

    if finance.balance_remaining <= 0:
        finance.balance_remaining = Decimal('0.00')
        finance.status = 'Paid'

    db.session.commit()
    flash('Repayment recorded.', 'success')
    return redirect(url_for('admin.finance_dashboard'))

@admin_bp.route('/finance/arrears/<int:finance_id>', methods=['POST'])
@login_required
def mark_in_arrears(finance_id):
    if not current_user.is_admin:
        abort(403)

    finance = LoanFinance.query.get_or_404(finance_id)
    finance.status = 'In Arrears'
    db.session.commit()

    flash('Loan marked as in arrears.', 'warning')
    return redirect(url_for('admin.finance_dashboard'))






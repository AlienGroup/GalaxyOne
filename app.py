from flask import Flask, render_template, request, redirect, url_for, flash
from flask_mail import Mail, Message
import os

app = Flask(__name__)
app.secret_key = "your_secret_key"

# Configure Flask-Mail
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'alienemergencyfund@gmail.com'  # Replace with your email
app.config['MAIL_PASSWORD'] = 'gnij yrdx ianb deaw'  # Replace with your email password
app.config['MAIL_DEFAULT_SENDER'] = ('Alien Emergency Fund', 'alienemergencyfund@gmail.com')  # Replace with your sender name and email
mail = Mail(app)

UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@app.route('/')
def loan_form():
    return render_template('loan_form.html')

@app.route('/submit', methods=['POST'])
def submit_loan():
    try:
        # Get form data
        name = request.form['name']
        email = request.form['email']
        address = request.form['address']
        contact = request.form['contact']
        employer_name = request.form['employer_name']
        employer_contact = request.form['employer_contact']
        income = float(request.form['income'])
        loan_amount = float(request.form['loan_amount'])
        repayment_period = int(request.form['repayment_period'])

        # Calculate repayment details
        interest_rate = 0.28  # 28% annual interest
        monthly_interest_rate = interest_rate / 2.33
        total_repayment = loan_amount * ((1 + monthly_interest_rate) ** repayment_period)
        monthly_repayment = total_repayment / repayment_period

        # Handle file uploads
        proof_of_address = request.files['proof_of_address']
        payslips = request.files['payslips']
        bank_statements = request.files['bank_statements']

        # Save uploaded files
        if proof_of_address:
            proof_of_address.save(os.path.join(app.config['UPLOAD_FOLDER'], proof_of_address.filename))
        payslips.save(os.path.join(app.config['UPLOAD_FOLDER'], payslips.filename))
        bank_statements.save(os.path.join(app.config['UPLOAD_FOLDER'], bank_statements.filename))

        # Send emails
        # Email to the applicant
        applicant_subject = "Loan Application Submitted"
        applicant_body = f"""
        Dear {name},

        Thank you for applying for an Alien Emergency Fund. Your application has been received.

        Loan Details:
        - Total Loan Amount: R{loan_amount:.2f}
        - Repayment Period: {repayment_period} months
        - Monthly Repayment: R{monthly_repayment:.2f}
        - Estimated Total Repayment: R{total_repayment:.2f}

        We will review your application and contact you shortly.

        Best regards,
        Alien Loans Team
        """
        send_email(email, applicant_subject, applicant_body)

        # Email to the lender/administrator
        lender_subject = f"New Emergency Fund Application from {name}"
        lender_body = f"""
        A new Emergency Fund application has been submitted:

        Applicant Details:
        - Name: {name}
        - Email: {email}
        - Address: {address}
        - Contact: {contact}
        - Employer Name: {employer_name}
        - Employer Contact: {employer_contact}
        - Monthly Income: R{income:.2f}

        Loan Details:
        - Total Loan Amount: R{loan_amount:.2f}
        - Repayment Period: {repayment_period} months
        - Monthly Repayment: R{monthly_repayment:.2f}
        - Estimated Total Repayment: R{total_repayment:.2f}

        Attached files have been saved in the server's upload folder.

        Please review the application.

        Thanks and Regards,
        Alien Emergency Fund
        Elliotdale
        5070
        alienemergencyfund@gmail.com
        """
        send_email("alienemergencyfund@gmail.com", lender_subject, lender_body)  # Replace with lender's email

        # Success message
        flash("Emergency fund application submitted successfully!", "success")
        return redirect(url_for('loan_form'))

    except Exception as e:
        flash(f"An error occurred: {str(e)}", "danger")
        return redirect(url_for('loan_form'))

def send_email(recipient, subject, body):
    try:
        msg = Message(subject, recipients=[recipient], body=body)
        mail.send(msg)
    except Exception as e:
        raise Exception(f"Failed to send email to {recipient}: {e}")

@app.route('/about_us')
def about_us():
    return render_template('about_us.html')

@app.route('/faq')
def faq():
    return render_template('faq.html')

@app.route('/feedback')
def feedback():
    return render_template('feedback.html')

@app.route('/loan_calculator', methods=['GET', 'POST'])
def loan_calculator():
    if request.method == 'POST':
        # Get input values from the form
        loan_amount = float(request.form['loan_amount'])
        repayment_period = int(request.form['repayment_period'])

        # Current South Africa base interest rate (11.75% as an example)
        base_interest_rate = 0.28
        monthly_interest_rate = base_interest_rate / 2.33

        # Calculate total repayment using compound interest
        total_repayment = loan_amount * ((1 + monthly_interest_rate) ** repayment_period)
        monthly_repayment = total_repayment / repayment_period

        # Pass calculated values back to the template
        return render_template(
            'loan_calculator.html',
            loan_amount=loan_amount,
            repayment_period=repayment_period,
            monthly_repayment=monthly_repayment,
            total_repayment=total_repayment

        )
    else:
        # Render the form if the request is GET
        return render_template('loan_calculator.html')

if __name__ == '__main__':
    app.run(debug=True)

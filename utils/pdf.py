import os
import textwrap
from decimal import Decimal
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.colors import (
    black, white, navy, darkblue, darkgreen, 
    firebrick, goldenrod, lightgrey, gray
)
from reportlab.lib.units import cm
from flask import current_app

def generate_contract_pdf(application, monthly_payment, total_payment):
    """
    Generate professional loan contract PDF - FIXED DECIMAL ISSUE
    """
    
    # ===== CONVERT ALL DECIMALS TO FLOAT =====
    # Convert Decimal to float for calculations
    loan_amount = float(application.loan_amount)
    monthly_income = float(application.monthly_income) if application.monthly_income else 0
    interest_rate = float(application.interest_rate)
    loan_term = int(application.loan_term)
    
    # Also convert the passed parameters
    monthly_payment = float(monthly_payment)
    total_payment = float(total_payment)
    
    # ===== CONFIGURATION =====
    upload_root = current_app.config['UPLOAD_FOLDER']
    app_dir = os.path.join(upload_root, str(application.id))
    os.makedirs(app_dir, exist_ok=True)
    
    pdf_path = os.path.join(app_dir, f"Loan_Contract_{application.id}.pdf")
    
    # ===== CREATE CANVAS =====
    c = canvas.Canvas(pdf_path, pagesize=A4)
    width, height = A4
    
    # ===== SIMPLE LETTERHEAD =====
    # Blue header bar
    c.setFillColor(navy)
    c.rect(0, height - 2*cm, width, 2*cm, fill=1, stroke=0)
    
    # Company name in white
    c.setFillColor(white)
    c.setFont("Helvetica-Bold", 16)
    c.drawString(2*cm, height - 1.2*cm, "ALIEN EMERGENCY FUND")
    
    c.setFont("Helvetica", 9)
    c.drawString(2*cm, height - 1.8*cm, "NCR Registered: NCRCP12345")
    
    # Contact info on right
    c.drawRightString(width - 2*cm, height - 1.2*cm, "alienemergencyfund@gmail.com")
    c.drawRightString(width - 2*cm, height - 1.6*cm, "043 123 4567")
    
    # Reset y position after letterhead
    y = height - 3*cm
    
    # ===== DOCUMENT TITLE =====
    c.setFont("Helvetica-Bold", 20)
    c.setFillColor(darkblue)
    c.drawCentredString(width/2, y, "LOAN AGREEMENT")
    y -= 0.8*cm
    
    c.setFont("Helvetica", 12)
    c.setFillColor(black)
    c.drawCentredString(width/2, y, "National Credit Act 34 of 2005")
    y -= 1*cm
    
    # ===== REFERENCE =====
    c.setFont("Helvetica", 9)
    c.drawString(2*cm, y, f"Agreement: AEF-{application.id}")
    c.drawRightString(width - 2*cm, y, f"Date: {application.date_signed.strftime('%d %B %Y')}")
    y -= 0.8*cm
    
    # Separator line
    c.setStrokeColor(lightgrey)
    c.setLineWidth(0.5)
    c.line(2*cm, y, width - 2*cm, y)
    y -= 1*cm
    
    # ===== WATERMARK =====
    c.saveState()
    c.setFont("Helvetica-Bold", 60)
    c.setFillColor(lightgrey)
    c.translate(width/2, height/2)
    c.rotate(45)
    c.drawCentredString(0, 0, "SIGNED")
    
    # Date and IP
    c.setFont("Helvetica", 20)
    c.drawCentredString(0, -1.5*cm, application.date_signed.strftime('%d %B %Y'))
    c.setFont("Helvetica", 16)
    c.drawCentredString(0, -2.5*cm, f"IP: {application.signed_ip}")
    c.restoreState()
    
    # ===== SECTION 1: CONSUMER DETAILS =====
    c.setFont("Helvetica-Bold", 12)
    c.setFillColor(darkblue)
    c.drawString(2*cm, y, "1. CONSUMER DETAILS")
    y -= 0.6*cm
    
    c.setFont("Helvetica", 10)
    c.setFillColor(black)
    
    details = [
        f"Full Name: {application.full_name}",
        f"ID Number: {application.id_number}",
        f"Email: {application.email}",
        f"Phone: {application.phone}",
        f"Address: {application.full_address}",
        f"Employer: {application.employer}",
        f"Monthly Income: R{monthly_income:,.2f}",
        f"Employment Duration: {application.employment_duration}"
    ]
    
    for detail in details:
        if y < 100:  # New page if needed
            c.showPage()
            y = height - 2*cm
        c.drawString(2.5*cm, y, detail)
        y -= 0.5*cm
    
    y -= 0.5*cm
    
    # ===== SECTION 2: LOAN DETAILS =====
    c.setFont("Helvetica-Bold", 12)
    c.setFillColor(darkblue)
    c.drawString(2*cm, y, "2. LOAN DETAILS")
    y -= 0.6*cm
    
    c.setFont("Helvetica", 10)
    c.setFillColor(black)
    
    # Calculate total interest
    total_interest = total_payment - loan_amount
    interest_percent = (total_interest / total_payment) * 100
    
    loan_details = [
        f"Loan Amount: R{loan_amount:,.2f}",
        f"Interest Rate: {interest_rate * 100:.2f}% per month",
        f"Loan Term: {loan_term} months",
        f"Monthly Payment: R{monthly_payment:,.2f}",
        f"Total Repayment: R{total_payment:,.2f}",
        f"Total Interest: R{total_interest:,.2f} ({interest_percent:.1f}% of total)",
        f"Purpose: {application.purpose or 'Not specified'}"
    ]
    
    for detail in loan_details:
        if y < 100:
            c.showPage()
            y = height - 2*cm
        c.drawString(2.5*cm, y, detail)
        y -= 0.5*cm
    
    y -= 0.5*cm
    
    # ===== SECTION 3: TERMS & CONDITIONS =====
    if y < 150:
        c.showPage()
        y = height - 2*cm
    
    c.setFont("Helvetica-Bold", 12)
    c.setFillColor(darkblue)
    c.drawString(2*cm, y, "3. TERMS & CONDITIONS")
    y -= 0.6*cm
    
    c.setFont("Helvetica", 9)
    c.setFillColor(black)
    
    terms = [
        "• This agreement is governed by the National Credit Act 34 of 2005.",
        "• You have the right to receive a copy of this agreement.",
        "• You may settle the loan early without penalty.",
        "• Late payments may incur fees and affect your credit record.",
        "• Personal data is processed in compliance with POPIA.",
        "• Funds disbursed within 1-2 business days.",
        "• Use reference AEF-" + str(application.id) + " for payments."
    ]
    
    for term in terms:
        if y < 100:
            c.showPage()
            y = height - 2*cm
        c.drawString(2.5*cm, y, term)
        y -= 0.4*cm
    
    y -= 0.5*cm
    
    # ===== SECTION 4: SIGNATURE =====
    if y < 200:
        c.showPage()
        y = height - 2*cm
    
    c.setFont("Helvetica-Bold", 12)
    c.setFillColor(darkblue)
    c.drawString(2*cm, y, "4. ELECTRONIC SIGNATURE")
    y -= 0.6*cm
    
    # Draw signature box
    c.setStrokeColor(black)
    c.setLineWidth(1)
    c.rect(2*cm, y - 3*cm, width - 4*cm, 2.5*cm)
    
    c.setFont("Helvetica", 10)
    c.setFillColor(black)
    
    signature_details = [
        f"Signed By: {application.full_name}",
        f"Date & Time: {application.date_signed.strftime('%d %B %Y at %H:%M:%S')}",
        f"IP Address: {application.signed_ip}",
        f"Document ID: AEF-{application.id}-SIGNED",
        f"Status: ELECTRONICALLY EXECUTED"
    ]
    
    sig_y = y - 0.5*cm
    for detail in signature_details:
        c.drawString(2.5*cm, sig_y, detail)
        sig_y -= 0.5*cm
    
    # ===== FOOTER =====
    footer_y = 2*cm
    c.setFont("Helvetica", 8)
    c.setFillColor(navy)
    c.drawCentredString(width/2, footer_y, "Alien Emergency Fund (Pty) Ltd • NCR Registered • POPIA Compliant")
    c.drawCentredString(width/2, footer_y - 0.4*cm, f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    c.drawCentredString(width/2, footer_y - 0.8*cm, f"Email copy sent to: {application.email}")
    
    # ===== SAVE PDF =====
    c.showPage()
    c.save()
    
    # Verify PDF was created
    if not os.path.exists(pdf_path):
        raise RuntimeError(f"PDF generation failed - file not created")
    
    file_size = os.path.getsize(pdf_path)
    print(f"✅ PDF generated: {pdf_path} ({file_size} bytes)")
    
    return pdf_path

def send_contract_email(application, pdf_path):
    """Send contract PDF via email"""
    from flask_mail import Message
    from extensions import mail
    
    try:
        # Convert Decimal to float for display
        loan_amount = float(application.loan_amount)
        interest_rate = float(application.interest_rate)
        loan_term = int(application.loan_term)
        
        # Calculate for email
        total_interest = loan_amount * interest_rate * loan_term
        total_payment = loan_amount + total_interest
        monthly_payment = total_payment / loan_term
        
        msg = Message(
            subject=f"Your Loan Agreement - AEF-{application.id}",
            recipients=[application.email],
            sender=current_app.config['MAIL_DEFAULT_SENDER']
        )
        
        msg.body = f"""
Dear {application.full_name},

Your loan agreement has been successfully signed and is attached.

LOAN DETAILS:
• Amount: R{loan_amount:,.2f}
• Term: {loan_term} months
• Interest Rate: {interest_rate * 100:.2f}% per month
• Monthly Payment: R{monthly_payment:,.2f}
• Total Repayment: R{total_payment:,.2f}

Please keep this agreement for your records and use reference AEF-{application.id} for payments.

Thank you,
Alien Emergency Fund Team
NCR Registered Credit Provider
        """
        
        # Attach PDF
        with open(pdf_path, 'rb') as f:
            msg.attach(
                filename=f"Loan_Agreement_AEF_{application.id}.pdf",
                content_type="application/pdf",
                data=f.read()
            )
        
        mail.send(msg)
        print(f"✅ Email sent to {application.email}")
        
    except Exception as e:
        print(f"❌ Email failed: {e}")
        raise
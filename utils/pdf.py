import os
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.colors import lightgrey
from flask import current_app
from datetime import datetime

def generate_contract_pdf(application, monthly_payment, total_payment):
    # ✅ Store inside applicant folder
    upload_root = current_app.config['UPLOAD_FOLDER']
    app_dir = os.path.join(upload_root, str(application.id))
    os.makedirs(app_dir, exist_ok=True)

    pdf_path = os.path.join(app_dir, f"Loan_Contract_{application.id}.pdf")

    c = canvas.Canvas(pdf_path, pagesize=A4)
    width, height = A4

    # ===== WATERMARK =====
    c.saveState()
    c.setFont("Helvetica-Bold", 60)
    c.setFillColor(lightgrey)
    c.translate(300, 400)
    c.rotate(45)
    c.drawCentredString(0, 0, "SIGNED")
    c.restoreState()

    y = height - 50

    def draw(text, bold=False):
        nonlocal y
        c.setFont("Helvetica-Bold" if bold else "Helvetica", 10)
        c.drawString(50, y, text)
        y -= 16

    # ===== HEADER =====
    draw("ALIEN EMERGENCY FUND", bold=True)
    draw("REGISTERED CREDIT PROVIDER (NCR)", bold=True)
    y -= 10

    # ===== APPLICANT DETAILS =====
    draw("APPLICANT DETAILS", bold=True)
    draw(f"Full Name: {application.full_name}")
    draw(f"ID Number: {application.id_number}")
    draw(f"Email: {application.email}")
    draw(f"Address: {application.full_address}")
    y -= 10

    # ===== LOAN DETAILS =====
    draw("LOAN DETAILS", bold=True)
    draw(f"Loan Amount: R{float(application.loan_amount):,.2f}")
    draw(f"Interest Rate: {application.interest_rate * 100:.2f}% per annum")
    draw(f"Loan Term: {application.loan_term} months")
    draw(f"Monthly Repayment: R{monthly_payment:,.2f}")
    draw(f"Total Repayment: R{total_payment:,.2f}")
    y -= 10

    # ===== NCR & LEGAL TERMS =====
    draw("LEGAL & NCR TERMS", bold=True)
    draw("• This agreement is governed by the National Credit Act (NCA).")
    draw("• You have the right to receive a copy of this agreement.")
    draw("• You may settle the loan early subject to NCA provisions.")
    draw("• Late or missed payments may incur fees and affect your credit record.")
    draw("• Default may result in legal action or handover to debt collectors.")
    draw("• Personal data is processed in compliance with POPIA.")
    y -= 10

    # ===== PAYOUT INFO =====
    draw("PAYOUT INFORMATION", bold=True)
    draw("Funds will be deposited within 1–2 business days")
    draw("after final verification of your bank statements.")
    y -= 10

    # ===== CONTACT DETAILS =====
    draw("LENDER CONTACT DETAILS", bold=True)
    draw("Alien Emergency Fund")
    draw("Email: alienemergencyfund@gmail.com")
    draw("Office Hours: Mon–Fri 08:00–17:00")
    y -= 20

    # ===== SIGNATURE =====
    draw("ELECTRONIC SIGNATURE", bold=True)
    draw(f"Signed by: {application.full_name}")
    draw(f"Date Signed: {application.date_signed.strftime('%Y-%m-%d %H:%M:%S')}")
    draw(f"IP Address: {application.signed_ip}")

    c.showPage()
    c.save()

    if not os.path.exists(pdf_path):
        raise RuntimeError("PDF generation failed")

    return pdf_path

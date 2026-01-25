import os
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.colors import lightgrey, black, white, navy, darkblue
from reportlab.lib.units import inch, cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from flask import current_app
from datetime import datetime
import textwrap

def generate_contract_pdf(application, monthly_payment, total_payment):
    # ✅ Store inside applicant folder
    upload_root = current_app.config['UPLOAD_FOLDER']
    app_dir = os.path.join(upload_root, str(application.id))
    os.makedirs(app_dir, exist_ok=True)

    pdf_path = os.path.join(app_dir, f"Loan_Contract_{application.id}.pdf")
    
    # Create canvas
    c = canvas.Canvas(pdf_path, pagesize=A4)
    width, height = A4
    
    # ===== REGISTER FONTS =====
    try:
        # Try to register a nicer font if available
        pdfmetrics.registerFont(TTFont('Helvetica', 'Helvetica.ttf'))
        pdfmetrics.registerFont(TTFont('Helvetica-Bold', 'Helvetica-Bold.ttf'))
        title_font = 'Helvetica-Bold'
        body_font = 'Helvetica'
    except:
        title_font = 'Helvetica-Bold'
        body_font = 'Helvetica'
    
    # ===== DRAW LETTERHEAD BACKGROUND =====
    c.setFillColor(navy)
    c.rect(0, height - 2*cm, width, 2*cm, fill=1, stroke=0)
    
    # ===== DRAW LOGO AREA =====
    c.setFillColor(white)
    c.setFont(title_font, 16)
    c.drawString(2*cm, height - 1.5*cm, "ALIEN EMERGENCY FUND")
    
    c.setFont(body_font, 9)
    c.drawString(2*cm, height - 2.2*cm, "Registered Credit Provider - NCRCP12345")
    
    # ===== COMPANY INFO ON RIGHT =====
    c.setFont(body_font, 8)
    company_info = [
        "123 Main Road, Elliotdale",
        "Eastern Cape, South Africa",
        "Email: alienemergencyfund@gmail.com",
        "Tel: 043 123 4567"
    ]
    
    y_info = height - 1.5*cm
    for line in company_info:
        c.drawRightString(width - 2*cm, y_info, line)
        y_info -= 0.4*cm
    
    # ===== SEPARATOR LINE =====
    c.setStrokeColor(black)
    c.setLineWidth(0.5)
    c.line(2*cm, height - 2.5*cm, width - 2*cm, height - 2.5*cm)
    
    # Reset y position after letterhead
    y = height - 3*cm
    
    # ===== DOCUMENT TITLE =====
    c.setFont(title_font, 20)
    c.setFillColor(darkblue)
    c.drawCentredString(width/2, y, "LOAN AGREEMENT")
    y -= 0.8*cm
    
    c.setFont(body_font, 12)
    c.setFillColor(black)
    c.drawCentredString(width/2, y, "National Credit Act 34 of 2005")
    y -= 1*cm
    
    # ===== REFERENCE INFO =====
    c.setFont(body_font, 9)
    c.drawString(2*cm, y, f"Agreement No: AEF-{application.id}")
    c.drawRightString(width - 2*cm, y, f"Date: {application.date_signed.strftime('%d %B %Y')}")
    y -= 0.6*cm
    
    # Draw separator
    c.setStrokeColor(lightgrey)
    c.setLineWidth(0.3)
    c.line(2*cm, y, width - 2*cm, y)
    y -= 0.8*cm
    
    # ===== WATERMARK (TRANSPARENT) =====
    c.saveState()
    c.setFont(title_font, 60)
    c.setFillColor(lightgrey)
    c.translate(width/2, height/2)
    c.rotate(45)
    c.drawCentredString(0, 0, "SIGNED")
    
    # Add date watermark
    c.setFont(body_font, 20)
    c.drawCentredString(0, -1.5*cm, application.date_signed.strftime('%d %B %Y'))
    c.drawCentredString(0, -2.5*cm, f"IP: {application.signed_ip}")
    c.restoreState()
    
    # ===== FUNCTION TO DRAW SECTIONS =====
    def draw_section(title, content_lines, y_pos):
        # Section title
        c.setFont(title_font, 12)
        c.setFillColor(darkblue)
        c.drawString(2*cm, y_pos, title)
        y_pos -= 0.5*cm
        
        # Draw line under title
        c.setStrokeColor(darkblue)
        c.setLineWidth(0.5)
        c.line(2*cm, y_pos, 6*cm, y_pos)
        y_pos -= 0.4*cm
        
        # Content
        c.setFont(body_font, 10)
        c.setFillColor(black)
        
        for line in content_lines:
            if isinstance(line, tuple):
                # Label-value pair
                label, value = line
                c.drawString(2.5*cm, y_pos, f"{label}:")
                c.drawString(6*cm, y_pos, str(value))
                y_pos -= 0.5*cm
            else:
                # Simple text line
                # Wrap long lines
                max_width = 80
                wrapped_lines = textwrap.wrap(line, width=max_width)
                for wrapped_line in wrapped_lines:
                    c.drawString(2.5*cm, y_pos, wrapped_line)
                    y_pos -= 0.4*cm
                y_pos -= 0.1*cm
        
        return y_pos - 0.5*cm  # Add spacing after section
    
    # ===== SECTION 1: APPLICANT DETAILS =====
    applicant_details = [
        ("Full Name", application.full_name),
        ("ID Number", application.id_number),
        ("Email", application.email),
        ("Phone", application.phone),
        ("Address", application.full_address),
        ("Employer", application.employer)
    ]
    y = draw_section("1. APPLICANT DETAILS", applicant_details, y)
    
    # ===== SECTION 2: LOAN DETAILS =====
    loan_details = [
        ("Loan Amount", f"R{float(application.loan_amount):,.2f}"),
        ("Interest Rate", f"{application.interest_rate * 100:.2f}% per month"),
        ("Loan Term", f"{application.loan_term} months"),
        ("Monthly Payment", f"R{monthly_payment:,.2f}"),
        ("Total Repayment", f"R{total_payment:,.2f}"),
        ("Total Interest", f"R{total_payment - application.loan_amount:,.2f}")
    ]
    y = draw_section("2. LOAN DETAILS", loan_details, y)
    
    # ===== SECTION 3: NCR TERMS =====
    ncr_terms = [
        "This agreement is governed by the National Credit Act 34 of 2005.",
        "You have the right to receive a copy of this agreement free of charge.",
        "You may settle the loan early without penalty as per Section 125 of the NCA.",
        "Late or missed payments may incur default charges and affect your credit record.",
        "Default may result in legal action or handover to debt collectors.",
        "Personal data is processed in compliance with POPIA Act 4 of 2013."
    ]
    y = draw_section("3. LEGAL TERMS & CONDITIONS", ncr_terms, y)
    
    # ===== SECTION 4: DISBURSEMENT =====
    disbursement = [
        "Funds will be deposited to your nominated bank account within 1-2 business days.",
        "Payment reference must be: AEF-" + str(application.id),
        "Ensure your bank details are correct to avoid delays."
    ]
    y = draw_section("4. DISBURSEMENT", disbursement, y)
    
    # ===== SECTION 5: ELECTRONIC SIGNATURE =====
    if y < 5*cm:  # Check if we need new page
        c.showPage()
        # Redraw letterhead on new page
        c.setFillColor(navy)
        c.rect(0, height - 1*cm, width, 1*cm, fill=1, stroke=0)
        c.setFillColor(white)
        c.setFont(title_font, 12)
        c.drawString(2*cm, height - 0.7*cm, f"Loan Agreement - AEF-{application.id} - Page 2")
        y = height - 2*cm
    
    signature_details = [
        ("Signed By", application.full_name),
        ("Date & Time", application.date_signed.strftime('%d %B %Y at %H:%M:%S')),
        ("IP Address", application.signed_ip),
        ("Document ID", f"AEF-{application.id}-SIGNED")
    ]
    y = draw_section("5. ELECTRONIC SIGNATURE", signature_details, y)
    
    # ===== SIGNATURE BOX =====
    c.setStrokeColor(black)
    c.setLineWidth(1)
    c.rect(2*cm, y - 3*cm, width - 4*cm, 2.5*cm)
    
    c.setFont(title_font, 11)
    c.setFillColor(darkblue)
    c.drawCentredString(width/2, y - 0.8*cm, "ELECTRONICALLY SIGNED & ACCEPTED")
    
    c.setFont(body_font, 9)
    c.setFillColor(black)
    c.drawString(2.5*cm, y - 1.5*cm, "This constitutes a legally binding electronic signature")
    c.drawString(2.5*cm, y - 2.1*cm, "in terms of the Electronic Communications and Transactions Act.")
    
    # ===== FOOTER =====
    c.setFont(body_font, 8)
    c.setFillColor(navy)
    footer_y = 2*cm
    
    c.drawCentredString(width/2, footer_y, "Alien Emergency Fund (Pty) Ltd • NCR Registered Credit Provider")
    c.drawCentredString(width/2, footer_y - 0.4*cm, "NCRCP12345 • POPIA Compliant • Consumer Protection Act Compliant")
    c.drawCentredString(width/2, footer_y - 0.8*cm, f"Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    c.drawCentredString(width/2, footer_y - 1.2*cm, f"Copy sent to: {application.email}")
    
    # ===== FINALIZE PDF =====
    c.showPage()
    c.save()
    
    if not os.path.exists(pdf_path):
        raise RuntimeError("PDF generation failed")
    
    return pdf_path
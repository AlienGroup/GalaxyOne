import os
import textwrap
from datetime import datetime
from reportlab.lib.pagesizes import A4, letter, landscape
from reportlab.pdfgen import canvas
from reportlab.lib.colors import (
    black, white, navy, darkblue, darkgreen, 
    firebrick, goldenrod, lightgrey, gray
)
from reportlab.lib.units import inch, cm, mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from reportlab.lib.utils import ImageReader
from flask import current_app
import base64
from io import BytesIO

def generate_contract_pdf(application, monthly_payment, total_payment):
    """
    Generate professional loan contract PDF with all features from HTML template
    Returns: Path to generated PDF file
    """
    
    # ===== CONFIGURATION =====
    upload_root = current_app.config['UPLOAD_FOLDER']
    app_dir = os.path.join(upload_root, str(application.id))
    os.makedirs(app_dir, exist_ok=True)
    
    pdf_path = os.path.join(app_dir, f"Loan_Contract_{application.id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf")
    
    # ===== CREATE CANVAS =====
    c = canvas.Canvas(pdf_path, pagesize=A4)
    width, height = A4
    
    # Register fonts (try to use better fonts if available)
    try:
        pdfmetrics.registerFont(TTFont('Helvetica', 'Helvetica.ttf'))
        pdfmetrics.registerFont(TTFont('Helvetica-Bold', 'Helvetica-Bold.ttf'))
        title_font = 'Helvetica-Bold'
        body_font = 'Helvetica'
    except:
        title_font = 'Helvetica-Bold'
        body_font = 'Helvetica'
    
    # ===== DRAW LETTERHEAD =====
    def draw_letterhead():
        """Draw professional letterhead with logo area"""
        # Blue header bar
        c.setFillColor(navy)
        c.rect(0, height - 2.5*cm, width, 2.5*cm, fill=1, stroke=0)
        
        # Try to load and draw logo
        logo_path = os.path.join(current_app.root_path, 'static', 'images', 'logo.png')
        if os.path.exists(logo_path):
            try:
                c.drawImage(logo_path, 2*cm, height - 2.2*cm, 
                           width=2*cm, height=1.5*cm, preserveAspectRatio=True)
            except:
                # Fallback to text logo
                draw_text_logo()
        else:
            draw_text_logo()
        
        # Company name
        c.setFillColor(white)
        c.setFont(title_font, 18)
        c.drawString(4.5*cm, height - 1.8*cm, "ALIEN EMERGENCY FUND (PTY) LTD")
        
        # NCR Registration
        c.setFont(body_font, 10)
        c.drawString(4.5*cm, height - 2.3*cm, "NCR Registered Credit Provider: NCRCP12345")
        
        # Contact info on right
        contact_info = [
            "123 Main Road, Elliotdale",
            "Eastern Cape, South Africa",
            "Email: alienemergencyfund@gmail.com",
            "Tel: 043 123 4567 | Fax: 043 123 4568"
        ]
        
        y_contact = height - 1.7*cm
        for line in contact_info:
            c.drawRightString(width - 2*cm, y_contact, line)
            y_contact -= 0.4*cm
    
    def draw_text_logo():
        """Draw text-based logo as fallback"""
        c.setFillColor(goldenrod)
        c.setFont(title_font, 16)
        c.drawString(2*cm, height - 1.8*cm, "AEF")
        c.setFillColor(white)
        c.setFont(title_font, 10)
        c.drawString(2*cm, height - 2.3*cm, "ALIEN EMERGENCY")
        c.drawString(2*cm, height - 2.6*cm, "FUND")
    
    # ===== WATERMARK =====
    def draw_watermark():
        """Draw signed watermark"""
        c.saveState()
        c.setFont(title_font, 72)
        c.setFillColor(lightgrey)
        c.setFillAlpha(0.1)  # More transparent
        
        # Position and rotate
        c.translate(width/2, height/2)
        c.rotate(315)  # -45 degrees
        
        # Watermark text
        c.drawCentredString(0, 0, "SIGNED")
        
        # Date and IP
        c.setFont(body_font, 24)
        c.drawCentredString(0, -1.5*cm, application.date_signed.strftime('%d %B %Y'))
        c.setFont(body_font, 18)
        c.drawCentredString(0, -2.5*cm, f"IP: {application.signed_ip}")
        
        c.restoreState()
    
    # ===== DRAW SECTION FUNCTION =====
    def draw_section(title, content, y_pos, is_table=False, table_data=None):
        """Draw a section with title and content"""
        # Section title
        c.setFont(title_font, 12)
        c.setFillColor(darkblue)
        c.drawString(2*cm, y_pos, title)
        
        # Underline
        c.setStrokeColor(darkblue)
        c.setLineWidth(0.5)
        c.line(2*cm, y_pos - 0.2*cm, 6*cm, y_pos - 0.2*cm)
        
        y_pos -= 0.6*cm
        
        if is_table and table_data:
            # Draw table
            table = Table(table_data, colWidths=[4*cm, 10*cm])
            table.setStyle(TableStyle([
                ('FONTNAME', (0,0), (-1,-1), body_font),
                ('FONTSIZE', (0,0), (-1,-1), 10),
                ('TEXTCOLOR', (0,0), (-1,-1), black),
                ('GRID', (0,0), (-1,-1), 0.5, gray),
                ('BACKGROUND', (0,0), (0,-1), lightgrey),
                ('ALIGN', (0,0), (0,-1), 'LEFT'),
                ('ALIGN', (1,0), (1,-1), 'LEFT'),
                ('VALIGN', (0,0), (-1,-1), 'TOP'),
                ('PADDING', (0,0), (-1,-1), 6),
            ]))
            
            table.wrapOn(c, width - 4*cm, height)
            table.drawOn(c, 2*cm, y_pos - table._height)
            y_pos -= table._height + 0.5*cm
            
        else:
            # Draw text content
            c.setFont(body_font, 10)
            c.setFillColor(black)
            
            for line in content:
                # Wrap long lines
                wrapped_lines = textwrap.wrap(line, width=100)
                for wrapped in wrapped_lines:
                    if y_pos < 3*cm:  # Near bottom of page
                        c.showPage()
                        y_pos = height - 3*cm
                        draw_letterhead()
                    
                    c.drawString(2.5*cm, y_pos, wrapped)
                    y_pos -= 0.4*cm
                
                y_pos -= 0.1*cm  # Space between paragraphs
        
        return y_pos - 0.5*cm  # Extra space after section
    
    # ===== START DRAWING =====
    # Draw watermark first (background)
    draw_watermark()
    
    # Draw letterhead
    draw_letterhead()
    
    y = height - 4*cm  # Start below letterhead
    
    # ===== DOCUMENT TITLE =====
    c.setFont(title_font, 24)
    c.setFillColor(darkblue)
    c.drawCentredString(width/2, y, "LOAN AGREEMENT")
    y -= 0.8*cm
    
    c.setFont(title_font, 14)
    c.setFillColor(darkgreen)
    c.drawCentredString(width/2, y, "National Credit Act 34 of 2005")
    y -= 1*cm
    
    # ===== REFERENCE INFO =====
    c.setFont(body_font, 10)
    c.setFillColor(black)
    c.drawString(2*cm, y, f"Agreement Number: AEF-{application.id}")
    c.drawRightString(width - 2*cm, y, 
                     f"Date Issued: {application.date_signed.strftime('%d %B %Y')}")
    y -= 0.8*cm
    
    # Separator line
    c.setStrokeColor(gray)
    c.setLineWidth(0.3)
    c.line(2*cm, y, width - 2*cm, y)
    y -= 1.2*cm
    
    # ===== SECTION 1: CONSUMER DETAILS =====
    consumer_table = [
        ["Full Name", application.full_name],
        ["ID Number", application.id_number],
        ["Email Address", application.email],
        ["Contact Number", application.phone],
        ["Residential Address", application.full_address],
        ["Employer", f"{application.employer} ({application.job_title or 'Not specified'})"],
        ["Monthly Income", f"R{float(application.monthly_income):,.2f}"],
        ["Employment Duration", application.employment_duration]
    ]
    
    y = draw_section("1. CONSUMER DETAILS", [], y, is_table=True, table_data=consumer_table)
    
    # ===== SECTION 2: CREDIT PROVIDER DISCLOSURE =====
    disclosure_text = [
        "Alien Emergency Fund (Pty) Ltd (Registration Number: 2023/123456/07) is a registered",
        "credit provider in terms of the National Credit Act 34 of 2005 (NCRCP12345) and",
        "conducts its business in accordance with all applicable South African legislation,",
        "including the Consumer Protection Act 68 of 2008 and the Protection of Personal",
        "Information Act 4 of 2013."
    ]
    
    y = draw_section("2. CREDIT PROVIDER DISCLOSURE", disclosure_text, y)
    
    # ===== SECTION 3: LOAN SUMMARY =====
    # Important note box
    c.setFillColor(lightgrey)
    c.setStrokeColor(darkblue)
    c.setLineWidth(1)
    c.roundRect(2*cm, y - 1*cm, width - 4*cm, 1*cm, 5, fill=1, stroke=1)
    
    c.setFont(title_font, 9)
    c.setFillColor(darkblue)
    note_text = "⚠️ This agreement constitutes a short-term credit transaction with a maximum repayment period of six (6) months"
    c.drawString(2.5*cm, y - 0.6*cm, note_text)
    y -= 1.5*cm
    
    # Loan details table
    total_interest = total_payment - application.loan_amount
    interest_percent = (total_interest / total_payment) * 100
    
    loan_table = [
        ["Principal Loan Amount", f"R{float(application.loan_amount):,.2f}"],
        ["Interest Rate", f"{application.interest_rate * 100:.2f}% per month (short-term credit)"],
        ["Loan Term", f"{application.loan_term} months"],
        ["Total Amount Payable", f"R{total_payment:,.2f}"],
        ["Monthly Instalment", f"R{monthly_payment:,.2f} ({application.loan_term} payments)"],
        ["Total Interest Payable", f"R{total_interest:,.2f} ({interest_percent:.1f}% of total)"],
        ["Purpose of Loan", application.purpose or "Not specified"]
    ]
    
    y = draw_section("3. LOAN SUMMARY", [], y, is_table=True, table_data=loan_table)
    
    # Interest calculation note
    calc_note = [
        "Interest Calculation: Simple interest calculated monthly on the principal loan amount",
        f"at {application.interest_rate * 100:.2f}% per month for {application.loan_term} months.",
        "Total repayment amount represents the full cost of credit excluding any default charges."
    ]
    
    c.setFont(body_font, 9)
    c.setFillColor(gray)
    for line in calc_note:
        c.drawString(2.5*cm, y, line)
        y -= 0.4*cm
    y -= 0.5*cm
    
    # Check if we need new page
    if y < 10*cm:
        c.showPage()
        draw_letterhead()
        draw_watermark()
        y = height - 4*cm
    
    # ===== SECTION 4: DISBURSEMENT OF FUNDS =====
    disbursement_text = [
        "Loan proceeds will be paid into the Consumer's nominated bank account following",
        "successful verification and acceptance of this agreement. Disbursement occurs",
        "within 1–2 business days of approval, subject to final validation of supporting",
        "documents and compliance checks."
    ]
    
    y = draw_section("4. DISBURSEMENT OF FUNDS", disbursement_text, y)
    
    # ===== SECTION 5: CONSUMER RIGHTS =====
    rights_text = [
        "✓ Right to receive a copy of this agreement free of charge",
        "✓ Right to early settlement without penalty (National Credit Act, Section 125)",
        "✓ Right to request statements of account at any time",
        "✓ Right to apply for debt review if over-indebted",
        "✓ Right to lodge complaints with the National Credit Regulator (NCR)",
        "✓ Right to rescind the agreement within 5 business days (cooling-off period)",
        "✓ Right to protection from unlawful discrimination"
    ]
    
    y = draw_section("5. CONSUMER RIGHTS", rights_text, y)
    
    # ===== SECTION 6: DEFAULT & ENFORCEMENT =====
    default_text = [
        "Failure to make payment on the due date may result in:",
        "• Default interest as permitted by the National Credit Act",
        "• Collection costs and administration fees",
        "• Legal action and associated legal costs (attorney-client scale)",
        "• Adverse credit bureau listings",
        "• Handover to debt collection agencies",
        "• Summary judgment proceedings in terms of the NCA"
    ]
    
    y = draw_section("6. DEFAULT, ENFORCEMENT & LEGAL COSTS", default_text, y)
    
    # ===== SECTION 7: POPIA COMPLIANCE =====
    popia_text = [
        "All personal information is processed lawfully, securely, and transparently",
        "in accordance with the Protection of Personal Information Act 4 of 2013.",
        "Information is used solely for:",
        "• Credit assessment and affordability calculations",
        "• Account administration and management",
        "• Statutory reporting to credit bureaus and regulators",
        "• Debt collection (if applicable)",
        "• As required by South African law"
    ]
    
    y = draw_section("7. PROTECTION OF PERSONAL INFORMATION (POPIA)", popia_text, y)
    
    # Check page space
    if y < 8*cm:
        c.showPage()
        draw_letterhead()
        draw_watermark()
        y = height - 4*cm
    
    # ===== SECTION 8: REPAYMENT BANKING DETAILS =====
    banking_table = [
        ["Bank Name", "_______________________________"],
        ["Account Holder", "_______________________________"],
        ["Account Number", "_______________________________"],
        ["Branch Code", "_______________________________"],
        ["Reference (IMPORTANT)", f"AEF-{application.id}"]
    ]
    
    y = draw_section("8. REPAYMENT BANKING DETAILS", [], y, is_table=True, table_data=banking_table)
    
    # ===== SECTION 9: ELECTRONIC SIGNATURE =====
    esign_text = [
        "By electronically accepting this agreement, the Consumer acknowledges that this",
        "constitutes a legally binding electronic signature in terms of the Electronic",
        "Communications and Transactions Act 25 of 2002. This electronic signature has",
        "the same legal force and effect as a handwritten signature."
    ]
    
    y = draw_section("9. ELECTRONIC SIGNATURE & ACCEPTANCE", esign_text, y)
    
    # ===== SIGNATURE BOX =====
    c.setStrokeColor(darkblue)
    c.setLineWidth(2)
    c.roundRect(2*cm, y - 4*cm, width - 4*cm, 3.5*cm, 5, stroke=1, fill=0)
    
    # Signature title
    c.setFont(title_font, 14)
    c.setFillColor(darkgreen)
    c.drawCentredString(width/2, y - 0.8*cm, "SIGNED BY CONSUMER")
    
    # Signature details
    sig_y = y - 1.8*cm
    signature_details = [
        ("Full Name:", application.full_name),
        ("Date & Time:", application.date_signed.strftime('%d %B %Y at %H:%M:%S')),
        ("IP Address:", application.signed_ip),
        ("Document ID:", f"AEF-{application.id}-SIGNED"),
        ("Agreement Status:", "ELECTRONICALLY EXECUTED")
    ]
    
    c.setFont(body_font, 10)
    for label, value in signature_details:
        c.setFillColor(darkblue)
        c.drawString(3*cm, sig_y, label)
        c.setFillColor(black)
        c.drawString(5*cm, sig_y, value)
        sig_y -= 0.6*cm
    
    y = y - 5*cm
    
    # ===== FOOTER =====
    footer_y = 2*cm
    
    # Footer separator
    c.setStrokeColor(gray)
    c.setLineWidth(0.5)
    c.line(2*cm, footer_y + 1*cm, width - 2*cm, footer_y + 1*cm)
    
    # Footer text
    c.setFont(body_font, 8)
    c.setFillColor(navy)
    
    footer_lines = [
        "Alien Emergency Fund (Pty) Ltd • NCR Registered Credit Provider (NCRCP12345) • POPIA Compliant",
        f"This document is electronically generated and requires no physical signature. A copy has been emailed to {application.email}",
        f"Generated on {datetime.now().strftime('%Y-%m-%d at %H:%M:%S')} • Document Version: 2.0 • Page 1 of 1",
        "© 2024 Alien Emergency Fund (Pty) Ltd. All rights reserved."
    ]
    
    for i, line in enumerate(footer_lines):
        c.drawCentredString(width/2, footer_y - (i * 0.3*cm), line)
    
    # ===== FINALIZE PDF =====
    c.showPage()
    c.save()
    
    # Verify PDF was created
    if not os.path.exists(pdf_path):
        raise RuntimeError(f"PDF generation failed - file not created at {pdf_path}")
    
    file_size = os.path.getsize(pdf_path)
    if file_size < 1024:  # Less than 1KB
        raise RuntimeError(f"PDF file too small ({file_size} bytes) - likely empty")
    
    print(f"✅ PDF successfully generated: {pdf_path} ({file_size} bytes)")
    
    return pdf_path

# ===== ADDITIONAL UTILITY FUNCTIONS =====
def send_contract_email(application, pdf_path):
    """Send contract PDF via email"""
    from flask_mail import Message
    from extensions import mail
    
    try:
        subject = f"Your Loan Agreement - AEF-{application.id}"
        
        msg = Message(
            subject=subject,
            recipients=[application.email],
            sender=current_app.config['MAIL_DEFAULT_SENDER']
        )
        
        # Email body
        msg.body = f"""
Dear {application.full_name},

Your loan agreement has been successfully signed and is attached.

Loan Details:
- Amount: R{application.loan_amount:,.2f}
- Term: {application.loan_term} months
- Monthly Payment: R{(application.loan_amount + (application.loan_amount * application.interest_rate * application.loan_term)) / application.loan_term:,.2f}

Please keep this agreement for your records.

Thank you for choosing Alien Emergency Fund.

Best regards,
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
        print(f"✅ Contract email sent to {application.email}")
        
    except Exception as e:
        print(f"❌ Failed to send email: {e}")
        raise

def create_contract_for_application(app_id):
    """Complete contract generation workflow"""
    from models import Application
    
    application = Application.query.get_or_404(app_id)
    
    # Calculate payments
    total_interest = application.loan_amount * application.interest_rate * application.loan_term
    total_payment = application.loan_amount + total_interest
    monthly_payment = total_payment / application.loan_term
    
    # Generate PDF
    pdf_path = generate_contract_pdf(application, monthly_payment, total_payment)
    
    # Send email
    send_contract_email(application, pdf_path)
    
    return pdf_path
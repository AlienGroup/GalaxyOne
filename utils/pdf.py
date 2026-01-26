import os
import textwrap
from decimal import Decimal
from datetime import datetime
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.colors import (
    black, white, gray, HexColor
)
from reportlab.lib.units import cm
from flask import current_app
import base64
from io import BytesIO

def generate_contract_pdf(application, monthly_payment, total_payment):
    """
    Generate professional loan contract PDF with LOGO support
    Colors: Orange and Black theme
    """
    
    # ===== CONVERT DECIMALS TO FLOAT =====
    loan_amount = float(application.loan_amount)
    monthly_income = float(application.monthly_income) if application.monthly_income else 0
    interest_rate = float(application.interest_rate)
    loan_term = int(application.loan_term)
    monthly_payment = float(monthly_payment)
    total_payment = float(total_payment)
    
    # ===== CONFIGURATION =====
    upload_root = current_app.config['UPLOAD_FOLDER']
    app_dir = os.path.join(upload_root, str(application.id))
    os.makedirs(app_dir, exist_ok=True)
    
    pdf_path = os.path.join(app_dir, f"Loan_Contract_AEF_{application.id}.pdf")
    
    # ===== CREATE CANVAS =====
    c = canvas.Canvas(pdf_path, pagesize=A4)
    width, height = A4
    
    # ===== CUSTOM ORANGE COLORS =====
    ORANGE_PRIMARY = HexColor('#FF8C00')  # Dark orange
    ORANGE_SECONDARY = HexColor('#FFA500')  # Standard orange
    ORANGE_LIGHT = HexColor('#FFE5CC')  # Light orange background
    ORANGE_DARK = HexColor('#E67E22')  # Darker orange
    ORANGE_BRIGHT = HexColor('#FF6B00')  # Bright orange
    
    # Track current page for watermark
    current_page = 0
    
    # ===== HELPER FUNCTION TO ADD WATERMARK =====
    def add_current_page_watermark():
        """Add watermark to the current page"""
        c.saveState()
        c.setFont("Helvetica-Bold", 80)
        c.setFillColor(HexColor('#FFE5CC'))  # Very light orange
        c.translate(width/2, height/2)
        c.rotate(-35)  # Rotated watermark
        
        # Watermark text
        c.drawCentredString(0, 0, "SIGNED")
        
        # Date and IP below
        c.setFont("Helvetica", 24)
        date_text = application.date_signed.strftime('%d %B %Y')
        c.drawCentredString(0, -2*cm, date_text)
        
        c.setFont("Helvetica", 18)
        ip_text = f"IP: {application.signed_ip}"
        c.drawCentredString(0, -3.5*cm, ip_text)
        
        c.restoreState()
    
    # ===== LETTERHEAD WITH LOGO (FIRST PAGE) =====
    current_page += 1
    
    # Add watermark for first page (before other content)
    add_current_page_watermark()
    
    # Orange header bar
    c.setFillColor(ORANGE_PRIMARY)
    c.rect(0, height - 2.5*cm, width, 2.5*cm, fill=1, stroke=0)
    
    # ===== ADD LOGO =====
    logo_added = False
    logo_x = 2*cm
    logo_y = height - 2.2*cm
    logo_width = 2*cm
    logo_height = 1.5*cm
    
    # Try multiple logo paths
    logo_paths = [
        os.path.join(current_app.root_path, 'static', 'images', 'logo.png'),
        os.path.join(current_app.root_path, 'static', 'images', 'logo.jpg'),
        os.path.join(current_app.root_path, 'static', 'images', 'logo.jpeg'),
        os.path.join(current_app.root_path, 'static', 'logo.png'),
        'static/images/logo.png',
        'static/logo.png',
    ]
    
    for logo_path in logo_paths:
        if os.path.exists(logo_path):
            try:
                c.drawImage(logo_path, logo_x, logo_y, 
                           width=logo_width, height=logo_height, 
                           preserveAspectRatio=True, mask='auto')
                logo_added = True
                print(f"✅ Logo added from: {logo_path}")
                break
            except Exception as e:
                print(f"⚠️ Could not load logo from {logo_path}: {e}")
                continue
        else:
            # Try relative path from current directory
            rel_path = os.path.join(os.path.dirname(__file__), '..', logo_path)
            if os.path.exists(rel_path):
                try:
                    c.drawImage(rel_path, logo_x, logo_y, 
                               width=logo_width, height=logo_height, 
                               preserveAspectRatio=True, mask='auto')
                    logo_added = True
                    print(f"✅ Logo added from relative path: {rel_path}")
                    break
                except Exception as e:
                    print(f"⚠️ Could not load logo from relative path {rel_path}: {e}")
    
    # If no logo found, use text logo
    if not logo_added:
        print("⚠️ Logo not found, using text logo")
        c.setFillColor(white)
        c.setFont("Helvetica-Bold", 14)
        c.drawString(logo_x, logo_y + 0.5*cm, "AEF")
        c.setFont("Helvetica-Bold", 10)
        c.drawString(logo_x, logo_y, "ALIEN EMERGENCY")
        c.drawString(logo_x, logo_y - 0.3*cm, "FUND")
    
    # ===== COMPANY INFO (ADJUSTED FOR LOGO) =====
    # White text on orange
    c.setFillColor(white)
    c.setFont("Helvetica-Bold", 16)
    
    # Adjust company name position based on logo
    company_x = 4.5*cm if logo_added else 2*cm
    c.drawString(company_x, height - 1.5*cm, "Alien Emergency Fund (Pty) Ltd")
    
    # NCR Registration in white
    c.setFont("Helvetica-Bold", 10)
    c.drawString(company_x, height - 2.1*cm, "NCR Registration: NCRCP12345")
    
    # Company info on right (white)
    c.setFont("Helvetica", 9)
    company_info = [
        "123 Main Road, Elliotdale, Eastern Cape",
        "South Africa, 5070",
        "Tel: 043 123 4567 | Email: alienemergencyfund@gmail.com",
        "Reg No: 2023/123456/07"
    ]
    
    y_info = height - 1.6*cm
    for line in company_info:
        c.drawRightString(width - 2*cm, y_info, line)
        y_info -= 0.4*cm
    
    # Bottom border
    c.setStrokeColor(ORANGE_DARK)
    c.setLineWidth(3)
    c.line(0, height - 2.5*cm, width, height - 2.5*cm)
    
    # Reset y position
    y = height - 4*cm
    
    # ===== DOCUMENT TITLE =====
    c.setFont("Helvetica-Bold", 24)
    c.setFillColor(black)
    c.drawCentredString(width/2, y, "LOAN AGREEMENT")
    y -= 0.8*cm
    
    c.setFont("Helvetica", 14)
    c.setFillColor(ORANGE_DARK)
    c.drawCentredString(width/2, y, "in terms of the National Credit Act 34 of 2005")
    y -= 1.2*cm
    
    # ===== AGREEMENT INFO =====
    c.setFont("Helvetica", 10)
    c.setFillColor(black)
    
    agreement_num = f"AEF-{application.id}-{application.date_signed.strftime('%Y')}"
    date_issued = application.date_signed.strftime('%d %B %Y')
    
    # Center both pieces of info
    left_text = f"Agreement Number: {agreement_num}"
    right_text = f"Date Issued: {date_issued}"
    
    c.drawString(2*cm, y, left_text)
    c.drawRightString(width - 2*cm, y, right_text)
    y -= 1*cm
    
    # Separator line
    c.setStrokeColor(gray)
    c.setLineWidth(0.5)
    c.line(2*cm, y, width - 2*cm, y)
    y -= 1*cm
    
    # ===== SECTION 1: CONSUMER DETAILS =====
    c.setFont("Helvetica-Bold", 14)
    c.setFillColor(black)
    c.drawString(2*cm, y, "1. CONSUMER DETAILS")
    
    # Underline
    c.setStrokeColor(ORANGE_PRIMARY)
    c.setLineWidth(2)
    c.line(2*cm, y - 0.2*cm, 6*cm, y - 0.2*cm)
    
    y -= 0.8*cm
    
    # Consumer details table
    c.setFont("Helvetica", 10)
    
    consumer_data = [
        ("Full Name", application.full_name),
        ("ID Number", application.id_number),
        ("Email Address", application.email),
        ("Contact Number", application.phone),
        ("Residential Address", application.full_address),
        ("Employment", f"{application.employer} ({application.job_title or 'Not specified'})")
    ]
    
    row_height = 0.6*cm
    for i, (label, value) in enumerate(consumer_data):
        # Alternate row background
        if i % 2 == 0:
            c.setFillColor(ORANGE_LIGHT)
            c.rect(2.5*cm, y - row_height + 0.1*cm, width - 5*cm, row_height, fill=1, stroke=0)
        
        # Label (bold)
        c.setFillColor(black)
        c.setFont("Helvetica-Bold", 10)
        c.drawString(2.5*cm, y, f"{label}:")
        
        # Value
        c.setFont("Helvetica", 10)
        
        # Wrap long values
        max_width = 70  # characters
        if len(str(value)) > max_width:
            wrapped = textwrap.wrap(str(value), width=max_width)
            for j, line in enumerate(wrapped):
                c.drawString(6*cm, y - (j * 0.4*cm), line)
            y -= (len(wrapped) - 1) * 0.4*cm
        else:
            c.drawString(6*cm, y, str(value))
        
        y -= row_height
    
    y -= 0.5*cm
    
    # ===== SECTION 2: CREDIT PROVIDER DISCLOSURE =====
    if y < 10*cm:
        c.showPage()
        current_page += 1
        # Add watermark to new page before header
        add_current_page_watermark()
        draw_page_header(c, width, height, application.id, logo_added, ORANGE_DARK, ORANGE_PRIMARY)
        y = height - 3*cm
    
    c.setFont("Helvetica-Bold", 14)
    c.setFillColor(black)
    c.drawString(2*cm, y, "2. CREDIT PROVIDER DISCLOSURE")
    c.setStrokeColor(ORANGE_PRIMARY)
    c.line(2*cm, y - 0.2*cm, 8*cm, y - 0.2*cm)
    
    y -= 0.8*cm
    
    disclosure_text = [
        "Alien Emergency Fund (Pty) Ltd (Registration Number: 2023/123456/07) is a registered",
        "credit provider in terms of the National Credit Act 34 of 2005 (NCRCP12345) and conducts",
        "its business in accordance with all applicable South African legislation, including the",
        "Consumer Protection Act 68 of 2008 and the Protection of Personal Information Act 4 of 2013."
    ]
    
    c.setFont("Helvetica", 10)
    c.setFillColor(black)
    
    for line in disclosure_text:
        c.drawString(2.5*cm, y, line)
        y -= 0.4*cm
    
    y -= 0.5*cm
    
        # ===== SECTION 3: LOAN SUMMARY =====
    if y < 15*cm:
        c.showPage()
        current_page += 1
        # Add watermark to new page before header
        add_current_page_watermark()
        draw_page_header(c, width, height, application.id, logo_added, ORANGE_DARK, ORANGE_PRIMARY)
        y = height - 3*cm
    
    c.setFont("Helvetica-Bold", 14)
    c.setFillColor(black)
    c.drawString(2*cm, y, "3. LOAN SUMMARY")
    c.setStrokeColor(ORANGE_PRIMARY)
    c.line(2*cm, y - 0.2*cm, 5.5*cm, y - 0.2*cm)
    
    y -= 0.8*cm
    
    # Important note box - FIXED: Adjusted height and position
    note_box_height = 1.4*cm  # Increased height for better spacing
    note_box_width = width - 4*cm
    c.setFillColor(HexColor('#FFF3E0'))  # Light orange background
    c.setStrokeColor(ORANGE_DARK)
    c.setLineWidth(1)
    c.roundRect(2*cm, y - note_box_height, note_box_width, note_box_height, 5, fill=1, stroke=1)
    
    c.setFont("Helvetica-Bold", 9)  # Reduced font size to fit text
    c.setFillColor(ORANGE_DARK)
    
    # Split the note into two lines to prevent cutoff
    note_text_line1 = "⚠️ This agreement constitutes a short-term credit transaction"
    note_text_line2 = "with a maximum repayment period of six (6) months"
    
    # Adjusted vertical positioning within the box
    c.drawString(2.5*cm, y - 0.8*cm, note_text_line1)
    c.drawString(2.5*cm, y - 1.3*cm, note_text_line2)
    
    y -= note_box_height + 0.5*cm  # Added more spacing after box
    
    # Calculate values
    total_interest = total_payment - loan_amount
    interest_percent = (total_interest / total_payment) * 100 if total_payment > 0 else 0
    
    # Loan details table
    loan_data = [
        ("Principal Loan Amount", f"R{loan_amount:,.2f}"),
        ("Interest Rate", f"{interest_rate * 100:.2f}% per month"),
        ("Loan Term", f"{loan_term} months"),
        ("Total Amount Payable", f"R{total_payment:,.2f}"),
        ("Monthly Instalment", f"R{monthly_payment:,.2f} ({loan_term} payments)"),
        ("Total Interest Payable", f"R{total_interest:,.2f}")
    ]
    
    for i, (label, value) in enumerate(loan_data):
        # Highlight important amounts
        if label in ["Principal Loan Amount", "Total Amount Payable", "Monthly Instalment"]:
            c.setFillColor(ORANGE_LIGHT)
            c.rect(2.5*cm, y - 0.6*cm + 0.1*cm, width - 5*cm, 0.6*cm, fill=1, stroke=0)
        
        # Label
        c.setFillColor(black)
        c.setFont("Helvetica-Bold", 10)
        c.drawString(2.5*cm, y, f"{label}:")
        
        # Value (bold for important amounts)
        if label in ["Principal Loan Amount", "Total Amount Payable", "Monthly Instalment"]:
            c.setFont("Helvetica-Bold", 10)
            c.setFillColor(ORANGE_DARK)
        else:
            c.setFont("Helvetica", 10)
            c.setFillColor(black)
        
        c.drawString(7*cm, y, value)
        y -= 0.6*cm
    
    y -= 0.3*cm
    
    # Interest calculation note
    c.setFont("Helvetica", 9)
    c.setFillColor(gray)
    calc_note = [
        "Interest Calculation: Interest is calculated monthly on the principal loan amount at the agreed",
        "rate for the full loan term. The total repayment amount shown above represents the full cost",
        "of credit excluding any default charges."
    ]
    
    for line in calc_note:
        c.drawString(2.5*cm, y, line)
        y -= 0.4*cm
    
    y -= 0.5*cm
    
    # ===== SECTION 4: DISBURSEMENT OF FUNDS =====
    if y < 10*cm:
        c.showPage()
        current_page += 1
        # Add watermark to new page before header
        add_current_page_watermark()
        draw_page_header(c, width, height, application.id, logo_added, ORANGE_DARK, ORANGE_PRIMARY)
        y = height - 3*cm
    
    c.setFont("Helvetica-Bold", 14)
    c.setFillColor(black)
    c.drawString(2*cm, y, "4. DISBURSEMENT OF FUNDS")
    c.setStrokeColor(ORANGE_PRIMARY)
    c.line(2*cm, y - 0.2*cm, 7.5*cm, y - 0.2*cm)
    
    y -= 0.8*cm
    
    disbursement_text = [
        "Loan proceeds will be paid into the Consumer's nominated bank account following successful",
        "verification and acceptance of this agreement. Disbursement occurs within 1–2 business days",
        "of approval."
    ]
    
    c.setFont("Helvetica", 10)
    c.setFillColor(black)
    
    for line in disbursement_text:
        c.drawString(2.5*cm, y, line)
        y -= 0.4*cm
    
    y -= 0.5*cm
    
    # ===== SECTION 5: CONSUMER RIGHTS =====
    c.setFont("Helvetica-Bold", 14)
    c.setFillColor(black)
    c.drawString(2*cm, y, "5. CONSUMER RIGHTS")
    c.setStrokeColor(ORANGE_PRIMARY)
    c.line(2*cm, y - 0.2*cm, 6.5*cm, y - 0.2*cm)
    
    y -= 0.8*cm
    
    rights = [
        "✓ Right to receive a copy of this agreement free of charge",
        "✓ Right to early settlement without penalty (National Credit Act, Section 125)",
        "✓ Right to request statements of account at any time",
        "✓ Right to apply for debt review if over-indebted",
        "✓ Right to lodge complaints with the National Credit Regulator (NCR)"
    ]
    
    c.setFont("Helvetica", 10)
    for right in rights:
        c.drawString(2.5*cm, y, right)
        y -= 0.5*cm
    
    y -= 0.3*cm
    
    # ===== SECTION 6: DEFAULT, ENFORCEMENT AND LEGAL COSTS =====
    if y < 10*cm:
        c.showPage()
        current_page += 1
        # Add watermark to new page before header
        add_current_page_watermark()
        draw_page_header(c, width, height, application.id, logo_added, ORANGE_DARK, ORANGE_PRIMARY)
        y = height - 3*cm
    
    c.setFont("Helvetica-Bold", 14)
    c.setFillColor(black)
    c.drawString(2*cm, y, "6. DEFAULT, ENFORCEMENT AND LEGAL COSTS")
    c.setStrokeColor(ORANGE_PRIMARY)
    c.line(2*cm, y - 0.2*cm, 10*cm, y - 0.2*cm)
    
    y -= 0.8*cm
    
    default_text = [
        "Failure to make payment on the due date may result in interest, collection costs, legal action,",
        "and adverse credit bureau listings, in accordance with the National Credit Act. Legal costs",
        "will be on an attorney-client scale."
    ]
    
    c.setFont("Helvetica", 10)
    for line in default_text:
        c.drawString(2.5*cm, y, line)
        y -= 0.4*cm
    
    y -= 0.5*cm
    
    # ===== SECTION 7: PROTECTION OF PERSONAL INFORMATION (POPIA) =====
    c.setFont("Helvetica-Bold", 14)
    c.setFillColor(black)
    c.drawString(2*cm, y, "7. PROTECTION OF PERSONAL INFORMATION (POPIA)")
    c.setStrokeColor(ORANGE_PRIMARY)
    c.line(2*cm, y - 0.2*cm, 12*cm, y - 0.2*cm)
    
    y -= 0.8*cm
    
    popia_text = [
        "All personal information is processed lawfully, securely, and transparently in accordance",
        "with the Protection of Personal Information Act 4 of 2013. Information is used solely for",
        "credit assessment, administration, statutory reporting, and as required by law."
    ]
    
    c.setFont("Helvetica", 10)
    for line in popia_text:
        c.drawString(2.5*cm, y, line)
        y -= 0.4*cm
    
    y -= 0.5*cm
    
    # ===== SECTION 8: REPAYMENT BANKING DETAILS =====
    if y < 8*cm:
        c.showPage()
        current_page += 1
        # Add watermark to new page before header
        add_current_page_watermark()
        draw_page_header(c, width, height, application.id, logo_added, ORANGE_DARK, ORANGE_PRIMARY)
        y = height - 3*cm
    
    c.setFont("Helvetica-Bold", 14)
    c.setFillColor(black)
    c.drawString(2*cm, y, "8. REPAYMENT BANKING DETAILS")
    c.setStrokeColor(ORANGE_PRIMARY)
    c.line(2*cm, y - 0.2*cm, 9.5*cm, y - 0.2*cm)
    
    y -= 0.8*cm
    
    banking_data = [
        ("Bank Name", "_______________________________"),
        ("Account Holder", "_______________________________"),
        ("Account Number", "_______________________________"),
        ("Branch Code", "_______________________________"),
        ("Reference", f"AEF-{application.id}")
    ]
    
    for i, (label, value) in enumerate(banking_data):
        # Highlight reference
        if label == "Reference":
            c.setFillColor(ORANGE_LIGHT)
            c.rect(2.5*cm, y - 0.6*cm + 0.1*cm, width - 5*cm, 0.6*cm, fill=1, stroke=0)
        
        # Label
        c.setFillColor(black)
        c.setFont("Helvetica-Bold", 10)
        c.drawString(2.5*cm, y, f"{label}:")
        
        # Value (orange for reference)
        if label == "Reference":
            c.setFont("Helvetica-Bold", 10)
            c.setFillColor(ORANGE_DARK)
        else:
            c.setFont("Helvetica", 10)
            c.setFillColor(black)
        
        c.drawString(6*cm, y, value)
        y -= 0.6*cm
    
    y -= 0.5*cm
    
    # ===== SECTION 9: ELECTRONIC SIGNATURE & ACCEPTANCE =====
    if y < 10*cm:
        c.showPage()
        current_page += 1
        # Add watermark to new page before header (this will be the last page with watermark)
        add_current_page_watermark()
        draw_page_header(c, width, height, application.id, logo_added, ORANGE_DARK, ORANGE_PRIMARY)
        y = height - 3*cm
    
    c.setFont("Helvetica-Bold", 14)
    c.setFillColor(black)
    c.drawString(2*cm, y, "9. ELECTRONIC SIGNATURE & ACCEPTANCE")
    c.setStrokeColor(ORANGE_PRIMARY)
    c.line(2*cm, y - 0.2*cm, 12*cm, y - 0.2*cm)
    
    y -= 0.8*cm
    
    esign_text = [
        "By electronically accepting this agreement, the Consumer acknowledges that this constitutes",
        "a legally binding electronic signature in terms of the Electronic Communications and",
        "Transactions Act 25 of 2002."
    ]
    
    c.setFont("Helvetica", 10)
    for line in esign_text:
        c.drawString(2.5*cm, y, line)
        y -= 0.4*cm
    
    y -= 0.5*cm
    
    # ===== SIGNATURE SECTION =====
    # Signature box with orange border
    c.setStrokeColor(ORANGE_DARK)
    c.setLineWidth(2)
    c.roundRect(2*cm, y - 4*cm, width - 4*cm, 3.5*cm, 8, stroke=1, fill=0)
    
    # Signature title
    c.setFont("Helvetica-Bold", 16)
    c.setFillColor(ORANGE_DARK)
    c.drawCentredString(width/2, y - 0.8*cm, "SIGNED BY CONSUMER")
    
    # Signature details box
    c.setFillColor(HexColor('#F8F9FA'))
    c.setStrokeColor(gray)
    c.setLineWidth(0.5)
    c.roundRect(3*cm, y - 3.8*cm, width - 6*cm, 2.5*cm, 5, fill=1, stroke=1)
    
    # Signature details
    sig_y = y - 1.8*cm
    signature_details = [
        ("Full Name:", application.full_name),
        ("Date & Time:", application.date_signed.strftime('%d %B %Y at %H:%M')),
        ("IP Address:", application.signed_ip),
        ("Document ID:", f"AEF-{application.id}-SIGNED")
    ]
    
    c.setFont("Helvetica", 10)
    for label, value in signature_details:
        c.setFillColor(black)
        c.setFont("Helvetica-Bold", 10)
        c.drawString(3.5*cm, sig_y, label)
        
        c.setFont("Helvetica", 10)
        c.setFillColor(black)
        c.drawString(6*cm, sig_y, value)
        
        sig_y -= 0.6*cm
    
    y = y - 5*cm
    
    # ===== FOOTER =====
    footer_y = 2*cm
    
    # Footer separator
    c.setStrokeColor(gray)
    c.setLineWidth(0.5)
    c.line(2*cm, footer_y + 1*cm, width - 2*cm, footer_y + 1*cm)
    
    # Footer text
    c.setFont("Helvetica", 8)
    c.setFillColor(ORANGE_DARK)
    
    footer_lines = [
        "Alien Emergency Fund (Pty) Ltd • NCR Registered Credit Provider (NCRCP12345) • POPIA Compliant",
        f"This document is electronically generated and requires no physical signature. A copy has been emailed to {application.email}",
        f"Generated on {datetime.now().strftime('%Y-%m-%d at %H:%M:%S')}"
    ]
    
    for i, line in enumerate(footer_lines):
        c.drawCentredString(width/2, footer_y - (i * 0.4*cm), line)
    
    # ===== FINALIZE PDF (NO WATERMARK ON LAST PAGE) =====
    # DO NOT add watermark to the last page
    c.showPage()
    c.save()
    
    # Verify PDF was created
    if not os.path.exists(pdf_path):
        raise RuntimeError(f"PDF generation failed - file not created")
    
    file_size = os.path.getsize(pdf_path)
    print(f"✅ PDF successfully generated: {pdf_path} ({file_size} bytes)")
    print(f"📄 Total pages with watermark: {current_page}")
    
    return pdf_path

def draw_page_header(c, width, height, app_id, logo_added, orange_dark, orange_primary):
    """Draw header on subsequent pages - FIXED VERSION"""
    # Light orange header for subsequent pages
    c.setFillColor(HexColor('#FFF3E0'))
    c.rect(0, height - 1.5*cm, width, 1.5*cm, fill=1, stroke=0)
    
    # Add small logo if available
    if logo_added:
        try:
            from flask import current_app
            import os
            logo_paths = [
                os.path.join(current_app.root_path, 'static', 'images', 'logo.png'),
                os.path.join(current_app.root_path, 'static', 'images', 'logo.jpg'),
                os.path.join(current_app.root_path, 'static', 'images', 'logo.jpeg'),
            ]
            for logo_path in logo_paths:
                if os.path.exists(logo_path):
                    c.drawImage(logo_path, 2*cm, height - 1.3*cm, 
                               width=1.2*cm, height=0.9*cm, 
                               preserveAspectRatio=True, mask='auto')
                    break
        except:
            pass
    
    # Page header text
    c.setFillColor(orange_dark)
    c.setFont("Helvetica-Bold", 10)
    c.drawString(4*cm, height - 1.1*cm, f"Loan Agreement - AEF-{app_id}")
    
    # Separator line
    c.setStrokeColor(orange_primary)
    c.setLineWidth(0.5)
    c.line(2*cm, height - 1.5*cm, width - 2*cm, height - 1.5*cm)

# ===== KEEP THE REST OF YOUR FUNCTIONS UNCHANGED =====
def send_contract_email(application, pdf_path):
    """Send contract PDF via email - ORANGE THEME"""
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
            subject=f"🚀 Your Loan Agreement - AEF-{application.id}",
            recipients=[application.email],
            sender=current_app.config['MAIL_DEFAULT_SENDER'],
            html=f"""
            <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; border: 2px solid #FF8C00; border-radius: 10px; overflow: hidden;">
                <div style="background-color: #FF8C00; color: white; padding: 20px; text-align: center;">
                    <h1 style="margin: 0; font-size: 24px;">Alien Emergency Fund</h1>
                    <p style="margin: 5px 0 0 0; font-size: 14px;">NCR Registered Credit Provider</p>
                </div>
                
                <div style="padding: 25px;">
                    <h2 style="color: #FF8C00; margin-top: 0;">Loan Agreement Signed Successfully</h2>
                    
                    <p>Dear <strong>{application.full_name}</strong>,</p>
                    
                    <p>Your loan agreement has been successfully signed and is attached to this email.</p>
                    
                    <div style="background-color: #FFF3E0; padding: 15px; border-left: 4px solid #FF8C00; margin: 20px 0;">
                        <h3 style="color: #FF8C00; margin-top: 0;">Loan Summary</h3>
                        <table style="width: 100%;">
                            <tr>
                                <td><strong>Loan Amount:</strong></td>
                                <td>R{loan_amount:,.2f}</td>
                            </tr>
                            <tr>
                                <td><strong>Loan Term:</strong></td>
                                <td>{loan_term} months</td>
                            </tr>
                            <tr>
                                <td><strong>Monthly Payment:</strong></td>
                                <td>R{monthly_payment:,.2f}</td>
                            </tr>
                            <tr>
                                <td><strong>Total Repayment:</strong></td>
                                <td>R{total_payment:,.2f}</td>
                            </tr>
                            <tr>
                                <td><strong>Agreement Number:</strong></td>
                                <td>AEF-{application.id}</td>
                            </tr>
                        </table>
                    </div>
                    
                    <p><strong>Important:</strong> Please use reference <strong style="color: #FF8C00;">AEF-{application.id}</strong> for all payments.</p>
                    
                    <p>Keep this agreement for your records. If you have any questions, contact us at <a href="mailto:alienemergencyfund@gmail.com" style="color: #FF8C00;">alienemergencyfund@gmail.com</a>.</p>
                    
                    <div style="margin-top: 30px; padding-top: 20px; border-top: 1px solid #eee;">
                        <p style="font-size: 12px; color: #666;">
                            Alien Emergency Fund (Pty) Ltd • NCRCP12345<br>
                            123 Main Road, Elliotdale, Eastern Cape<br>
                            POPIA Compliant • Consumer Protection Act Compliant
                        </p>
                    </div>
                </div>
            </div>
            """
        )
        
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

# ===== UTILITY FUNCTION TO CHECK LOGO =====
def check_logo_exists():
    """Check if logo file exists and return path"""
    logo_paths = [
        os.path.join(current_app.root_path, 'static', 'images', 'logo.png'),
        os.path.join(current_app.root_path, 'static', 'images', 'logo.jpg'),
        os.path.join(current_app.root_path, 'static', 'images', 'logo.jpeg'),
        os.path.join(current_app.root_path, 'static', 'logo.png'),
    ]
    
    for path in logo_paths:
        if os.path.exists(path):
            return path
    return None

def get_logo_base64():
    """Get logo as base64 string"""
    logo_path = check_logo_exists()
    if logo_path:
        try:
            with open(logo_path, 'rb') as f:
                return base64.b64encode(f.read()).decode('utf-8')
        except:
            return None
    return None
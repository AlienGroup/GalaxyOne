import os
import base64
from datetime import datetime
from flask import current_app, render_template
from weasyprint import HTML


def generate_contract_pdf(application, monthly_payment, total_payment):
    """
    Generates a PDF from loan_contract.html using WeasyPrint.
    This is the ONLY correct way to support complex HTML/CSS contracts.
    """

    # ================= SAFETY CHECKS =================
    if not application.date_signed:
        raise RuntimeError("Application must be signed before generating contract PDF")

    # Ensure numeric safety (Decimal → float)
    monthly_payment = float(monthly_payment)
    total_payment = float(total_payment)

    # ================= FILE LOCATION =================
    upload_root = current_app.config["UPLOAD_FOLDER"]
    app_dir = os.path.join(upload_root, str(application.id))
    os.makedirs(app_dir, exist_ok=True)

    pdf_path = os.path.join(app_dir, f"Loan_Contract_{application.id}.pdf")

    # ================= LOGO (BASE64) =================
    logo_path = os.path.join(
        current_app.root_path,
        "static",
        "images",
        "logo.png"
    )

    logo_base64 = None
    if os.path.exists(logo_path):
        with open(logo_path, "rb") as img:
            logo_base64 = base64.b64encode(img.read()).decode("utf-8")

    # ================= RENDER HTML =================
    html_content = render_template(
        "loan_contract.html",
        application=application,
        monthly_payment=monthly_payment,
        total_payment=total_payment,
        logo_base64=logo_base64,
        now=datetime.utcnow()
    )

    # ================= GENERATE PDF =================
    HTML(
        string=html_content,
        base_url=current_app.root_path  # allows static/assets resolution
    ).write_pdf(pdf_path)

    # ================= FINAL CHECK =================
    if not os.path.exists(pdf_path):
        raise RuntimeError("PDF generation failed (file not created)")

    return pdf_path

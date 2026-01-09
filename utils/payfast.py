import hashlib
from flask import current_app, url_for
from urllib.parse import urlencode

def generate_payfast_url(user):
    amount = user.amount_due or 0

    if amount <= 0:
        raise ValueError("Invalid payment amount")

    payfast_data = {
        # 🔐 PayFast credentials
        "merchant_id": current_app.config["PAYFAST_MERCHANT_ID"],
        "merchant_key": current_app.config["PAYFAST_MERCHANT_KEY"],

        # 🔁 Redirect URLs
        "return_url": url_for("main.payment_success", _external=True),
        "cancel_url": url_for("main.payment_cancel", _external=True),

        # ✅ THIS IS THE IPN URL (ADD HERE)
        "notify_url": url_for("main.payfast_ipn", _external=True),

        # 💳 Payment details
        "amount": f"{amount:.2f}",
        "item_name": "Loan Payment",

        # 👤 Customer details
        "name_first": user.first_name or "",
        "name_last": user.last_name or "",
        "email_address": user.email,

        # 🧾 Internal reference (VERY IMPORTANT FOR IPN)
        "m_payment_id": f"user-{user.id}-loan",
    }

    # Remove empty values (PayFast requirement)
    payfast_data = {k: v for k, v in payfast_data.items() if v}

    # 🔐 Generate signature
    signature_string = urlencode(payfast_data)
    signature = hashlib.md5(signature_string.encode()).hexdigest()
    payfast_data["signature"] = signature

    # Sandbox URL (switch to live later)
    payfast_base_url = "https://sandbox.payfast.co.za/eng/process"

    return f"{payfast_base_url}?{urlencode(payfast_data)}"

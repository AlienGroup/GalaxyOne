import hashlib
import requests
from urllib.parse import urlencode
from flask import current_app

def verify_payfast_ipn(data):
    # 1️⃣ Verify merchant ID
    if data.get("merchant_id") != current_app.config["PAYFAST_MERCHANT_ID"]:
        return False, "Invalid merchant ID"

    # 2️⃣ Verify signature
    received_signature = data.pop("signature", None)
    signature_string = urlencode(sorted(data.items()))
    calculated_signature = hashlib.md5(signature_string.encode()).hexdigest()

    if calculated_signature != received_signature:
        return False, "Invalid signature"

    # 3️⃣ Validate with PayFast server
    verify_url = "https://sandbox.payfast.co.za/eng/query/validate"
    response = requests.post(
        verify_url,
        data=signature_string,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        timeout=10
    )

    if response.text != "VALID":
        return False, "PayFast validation failed"

    return True, "VALID"

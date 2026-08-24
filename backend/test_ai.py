from app.services.ai_matcher import analyze_match


gateway = {
    "transaction_id": "TXN_TEST",
    "amount": 799,
    "timestamp": "2026-08-24T09:03:00",
    "customer_name": "Aditi Rao",
    "description": "UPI payment #0001",
}


bank = {
    "utr": "UTR_TEST",
    "amount": 799,
    "timestamp": "2026-08-24T09:06:00",
    "payer_name": "Aditi Rao",
    "description": "UPI payment #0001",
}


result = analyze_match(
    gateway,
    bank,
    "bank",
)

print(result)
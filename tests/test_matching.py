from app.services.matching import (
    normalize_text,
    text_similarity,
    timestamp_difference_minutes,
    calculate_match_score,
)


def test_normalize_text():
    assert normalize_text(" Rahul-Kumar!! ") == "rahul kumar"


def test_timestamp_difference():
    difference = timestamp_difference_minutes(
        "2026-08-24T09:03:00",
        "2026-08-24T09:06:00",
    )

    assert difference == 3


def test_identical_text_similarity():
    similarity = text_similarity(
        "Rahul Kumar",
        "Rahul Kumar",
    )

    assert similarity == 1.0


def test_match_score():
    gateway = {
        "transaction_id": "TXN_00001",
        "amount": 799,
        "timestamp": "2026-08-24T09:03:00",
        "customer_name": "Aditi Rao",
        "email": "aditi.rao@example.com",
        "description": "UPI payment #0001",
    }

    bank = {
        "utr": "UTR_42868828",
        "amount": 799,
        "timestamp": "2026-08-24T09:06:00",
        "payer_name": "Aditi Rao",
        "description": "UPI payment #0001",
    }

    result = calculate_match_score(
        gateway,
        bank,
    )

    assert result["amount_match"] is True
    assert result["time_difference_minutes"] == 3
    assert result["score"] > 0.8
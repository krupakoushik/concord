import re
from datetime import datetime

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def normalize_text(text: str) -> str:
    if not text:
        return ""

    text = text.lower().strip()
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    text = re.sub(r"\s+", " ", text)

    return text


def normalize_name(name: str) -> str:
    return normalize_text(name)


def parse_timestamp(timestamp: str) -> datetime:
    return datetime.fromisoformat(timestamp)


def timestamp_difference_minutes(
    timestamp_a: str,
    timestamp_b: str,
) -> float:

    time_a = parse_timestamp(timestamp_a)
    time_b = parse_timestamp(timestamp_b)

    difference = abs(time_a - time_b)

    return difference.total_seconds() / 60


def amounts_match(
    amount_a: float,
    amount_b: float,
) -> bool:

    return abs(float(amount_a) - float(amount_b)) < 0.01


def text_similarity(
    text_a: str,
    text_b: str,
) -> float:

    text_a = normalize_text(text_a)
    text_b = normalize_text(text_b)

    if not text_a or not text_b:
        return 0.0

    if text_a == text_b:
        return 1.0

    vectorizer = TfidfVectorizer(
        analyzer="char",
        ngram_range=(2, 4),
    )

    vectors = vectorizer.fit_transform(
        [text_a, text_b]
    )

    similarity = cosine_similarity(
        vectors[0],
        vectors[1],
    )[0][0]

    return float(similarity)


def calculate_match_score(
    gateway_record: dict,
    other_record: dict,
) -> dict:

    amount_match = amounts_match(
        gateway_record["amount"],
        other_record["amount"],
    )

    name_similarity = text_similarity(
        gateway_record["customer_name"],
        other_record["payer_name"],
    )

    description_similarity = text_similarity(
        gateway_record["description"],
        other_record["description"],
    )

    time_difference = timestamp_difference_minutes(
        gateway_record["timestamp"],
        other_record["timestamp"],
    )

    time_score = max(
        0.0,
        1.0 - (time_difference / 15.0),
    )

    amount_score = 1.0 if amount_match else 0.0

    score = (
        amount_score * 0.40
        + name_similarity * 0.25
        + time_score * 0.20
        + description_similarity * 0.15
    )

    return {
        "score": round(score, 4),
        "amount_match": amount_match,
        "name_similarity": round(name_similarity, 4),
        "description_similarity": round(
            description_similarity,
            4,
        ),
        "time_difference_minutes": round(
            time_difference,
            2,
        ),
        "time_score": round(
            time_score,
            4,
        ),
    }
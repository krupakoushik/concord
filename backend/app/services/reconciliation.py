import csv
from pathlib import Path

from .matching import calculate_match_score

from .ai_matcher import analyze_match

BASE_DIR = Path(__file__).resolve().parents[3]

GATEWAY_FILE = BASE_DIR / "data" / "generated" / "gateway.csv"
BANK_FILE = BASE_DIR / "data" / "generated" / "bank.csv"
LEDGER_FILE = BASE_DIR / "data" / "generated" / "ledger.csv"


def load_csv(path: Path) -> list[dict]:
    with open(path, "r", encoding="utf-8") as file:
        return list(csv.DictReader(file))


def convert_amount(record: dict, field: str = "amount") -> dict:
    record[field] = float(record[field])
    return record


def load_data():
    gateway = load_csv(GATEWAY_FILE)
    bank = load_csv(BANK_FILE)
    ledger = load_csv(LEDGER_FILE)

    gateway = [convert_amount(r) for r in gateway]
    bank = [convert_amount(r) for r in bank]
    ledger = [convert_amount(r) for r in ledger]

    return gateway, bank, ledger


def find_best_candidate(
    source_record: dict,
    candidates: list[dict],
    source_type: str,
):
    best_candidate = None
    best_result = None

    for candidate in candidates:

        if source_type == "bank":
            result = calculate_match_score(
                source_record,
                candidate,
            )

        elif source_type == "ledger":
            # Ledger has the same customer_name field as gateway.
            ledger_as_bank_shape = {
                "amount": candidate["amount"],
                "timestamp": candidate["timestamp"],
                "payer_name": candidate["customer_name"],
                "description": candidate["description"],
            }

            result = calculate_match_score(
                source_record,
                ledger_as_bank_shape,
            )

        else:
            raise ValueError(f"Unknown source type: {source_type}")

        if best_result is None or result["score"] > best_result["score"]:
            best_candidate = candidate
            best_result = result

    return best_candidate, best_result


def determine_status(
    bank_result: dict | None,
    ledger_result: dict | None,
) -> str:

    if bank_result is None or ledger_result is None:
        return "MISSING"

    bank_score = bank_result["score"]
    ledger_score = ledger_result["score"]

    # Strong financial contradiction.
    if not bank_result["amount_match"]:
        return "EXCEPTION"

    if not ledger_result["amount_match"]:
        return "EXCEPTION"

    # Strong match.
    if bank_score >= 0.85 and ledger_score >= 0.85:
        return "MATCHED"

    # Possible match, but not confident enough.
    if bank_score >= 0.60 or ledger_score >= 0.60:
        return "REVIEW"

    return "UNRESOLVED"


def reconcile():
    gateway_records, bank_records, ledger_records = load_data()

    results = []

    for gateway in gateway_records:

        best_bank, bank_result = find_best_candidate(
            gateway,
            bank_records,
            "bank",
        )

        best_ledger, ledger_result = find_best_candidate(
            gateway,
            ledger_records,
            "ledger",
        )

        status = determine_status(
            bank_result,
            ledger_result,
        )

        ai_result = None

        if status in {"REVIEW", "UNRESOLVED"}:

            if best_bank and bank_result:
                try:
                    ai_result = analyze_match(
                        gateway,
                        best_bank,
                        "bank",
                    )
                except Exception as error:
                    ai_result = {
                        "decision": "REVIEW",
                        "confidence": 0.0,
                        "reasons": [
                            f"AI analysis unavailable: {error}"
                        ],
                    }

        if ai_result:
            ai_decision = ai_result.get("decision")
            ai_confidence = ai_result.get("confidence", 0)

            if (
                ai_decision == "MATCH"
                and ai_confidence >= 0.90
                and bank_result["amount_match"]
            ):
                status = "AI_MATCH"

            elif ai_decision == "NO_MATCH":
                status = "EXCEPTION"

            else:
                status = "REVIEW"

        results.append({
            "transaction_id": gateway["transaction_id"],
            "gateway_amount": gateway["amount"],
            "gateway_timestamp": gateway["timestamp"],
            "customer_name": gateway["customer_name"],

            "bank_utr": (
                best_bank["utr"]
                if best_bank
                else None
            ),

            "bank_amount": (
                best_bank["amount"]
                if best_bank
                else None
            ),

            "bank_score": (
                bank_result["score"]
                if bank_result
                else 0
            ),

            "ledger_invoice_id": (
                best_ledger["invoice_id"]
                if best_ledger
                else None
            ),

            "ledger_amount": (
                best_ledger["amount"]
                if best_ledger
                else None
            ),

            "ledger_score": (
                ledger_result["score"]
                if ledger_result
                else 0
            ),

            "ai_decision": (
                ai_result.get("decision")
                if ai_result
                else None
            ),

            "ai_confidence": (
                ai_result.get("confidence")
                if ai_result
                else None
            ),

            "ai_reasons": (
                ai_result.get("reasons")
                if ai_result
                else []
            ),

            "status": status,
        })

    return results

def get_reconciliation_results():
    return reconcile()

if __name__ == "__main__":
    results = reconcile()

    for result in results[:10]:
        print(result)
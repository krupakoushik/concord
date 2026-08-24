import csv
import random
from datetime import datetime, timedelta
from pathlib import Path


# ============================================================
# Configuration
# ============================================================

NUM_TRANSACTIONS = 100
SEED = 42

BASE_TIME = datetime(2026, 8, 24, 9, 0, 0)

PROJECT_ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = PROJECT_ROOT / "data/generated"
GROUND_TRUTH_DIR = PROJECT_ROOT / "data/ground_truth"


# ============================================================
# Synthetic customer data
# ============================================================

CUSTOMERS = [
    ("Rahul Kumar", "rahul.kumar@example.com"),
    ("Priya Sharma", "priya.sharma@example.com"),
    ("Arjun Mehta", "arjun.mehta@example.com"),
    ("Sneha Reddy", "sneha.reddy@example.com"),
    ("Karthik Iyer", "karthik.iyer@example.com"),
    ("Ananya Gupta", "ananya.gupta@example.com"),
    ("Vikram Singh", "vikram.singh@example.com"),
    ("Neha Patel", "neha.patel@example.com"),
    ("Rohan Das", "rohan.das@example.com"),
    ("Meera Nair", "meera.nair@example.com"),
    ("Aditi Rao", "aditi.rao@example.com"),
    ("Siddharth Jain", "siddharth.jain@example.com"),
    ("Pooja Menon", "pooja.menon@example.com"),
    ("Aman Verma", "aman.verma@example.com"),
    ("Divya Krishnan", "divya.krishnan@example.com"),
]


DESCRIPTIONS = [
    "Order",
    "Subscription",
    "Invoice",
    "Purchase",
    "Online payment",
    "UPI payment",
    "Merchant payment",
]


SCENARIO_DISTRIBUTION = {
    "clean": 50,
    "noisy": 20,
    "ambiguous": 10,
    "amount_discrepancy": 10,
    "missing_or_duplicate": 10,
}


# ============================================================
# Utility functions
# ============================================================

def random_amount():
    """
    Generate realistic-looking transaction amounts.
    """
    return random.choice([
        499,
        799,
        999,
        1299,
        1499,
        1999,
        2499,
        2999,
        3499,
        4999,
        5999,
        7999,
        9999,
    ])


def random_timestamp(index):
    """
    Generate a deterministic timestamp based on transaction index.
    """
    return BASE_TIME + timedelta(
        minutes=index * random.randint(3, 8)
    )


def write_csv(path, rows, fieldnames):
    """
    Write a list of dictionaries to CSV.
    """
    path.parent.mkdir(parents=True, exist_ok=True)

    with open(path, "w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


# ============================================================
# Record generators
# ============================================================

def create_gateway_record(
    canonical_id,
    transaction_number,
    amount,
    timestamp,
    customer_name,
    email,
    description,
):
    return {
        "transaction_id": f"TXN_{transaction_number:05d}",
        "amount": amount,
        "timestamp": timestamp.isoformat(),
        "customer_name": customer_name,
        "email": email,
        "description": description,
    }


def create_bank_record(
    transaction_number,
    amount,
    timestamp,
    payer_name,
    description,
):
    return {
        "utr": f"UTR_{random.randint(10000000, 99999999)}",
        "amount": amount,
        "timestamp": timestamp.isoformat(),
        "payer_name": payer_name,
        "description": description,
    }


def create_ledger_record(
    transaction_number,
    amount,
    timestamp,
    customer_name,
    email,
    description,
):
    return {
        "invoice_id": f"INV_{transaction_number:05d}",
        "amount": amount,
        "timestamp": timestamp.isoformat(),
        "customer_name": customer_name,
        "email": email,
        "description": description,
    }


# ============================================================
# Scenario generation
# ============================================================

def generate_clean_transaction(
    transaction_number,
    canonical_id,
):
    customer_name, email = random.choice(CUSTOMERS)
    amount = random_amount()
    timestamp = random_timestamp(transaction_number)

    description_type = random.choice(DESCRIPTIONS)
    description = f"{description_type} #{transaction_number:04d}"

    gateway = create_gateway_record(
        canonical_id,
        transaction_number,
        amount,
        timestamp,
        customer_name,
        email,
        description,
    )

    bank = create_bank_record(
        transaction_number,
        amount,
        timestamp + timedelta(minutes=random.randint(1, 4)),
        customer_name,
        description,
    )

    ledger = create_ledger_record(
        transaction_number,
        amount,
        timestamp + timedelta(minutes=random.randint(0, 2)),
        customer_name,
        email,
        description,
    )

    return gateway, bank, ledger


def generate_noisy_transaction(
    transaction_number,
    canonical_id,
):
    customer_name, email = random.choice(CUSTOMERS)
    amount = random_amount()
    timestamp = random_timestamp(transaction_number)

    first_name = customer_name.split()[0]
    last_name = customer_name.split()[-1]

    noisy_name = f"{first_name[0]}. {last_name}"

    description = f"Order #{transaction_number:04d}"
    noisy_description = f"UPI/{transaction_number:04d}"

    gateway = create_gateway_record(
        canonical_id,
        transaction_number,
        amount,
        timestamp,
        customer_name,
        email,
        description,
    )

    bank = create_bank_record(
        transaction_number,
        amount,
        timestamp + timedelta(minutes=random.randint(5, 10)),
        noisy_name,
        noisy_description,
    )

    ledger = create_ledger_record(
        transaction_number,
        amount,
        timestamp + timedelta(minutes=random.randint(2, 5)),
        customer_name,
        email,
        description,
    )

    return gateway, bank, ledger


def generate_ambiguous_transaction(
    transaction_number,
    canonical_id,
):
    customer_name, email = random.choice(CUSTOMERS)
    amount = random_amount()
    timestamp = random_timestamp(transaction_number)

    first_name = customer_name.split()[0]
    last_name = customer_name.split()[-1]

    ambiguous_name = f"{first_name} {last_name[0]}."

    gateway = create_gateway_record(
        canonical_id,
        transaction_number,
        amount,
        timestamp,
        customer_name,
        email,
        f"Order #{transaction_number:04d}",
    )

    bank = create_bank_record(
        transaction_number,
        amount,
        timestamp + timedelta(minutes=random.randint(8, 15)),
        ambiguous_name,
        f"Payment ref {transaction_number:04d}",
    )

    ledger = create_ledger_record(
        transaction_number,
        amount,
        timestamp + timedelta(minutes=random.randint(5, 10)),
        customer_name,
        email,
        f"Order {transaction_number:04d}",
    )

    return gateway, bank, ledger


def generate_amount_discrepancy_transaction(
    transaction_number,
    canonical_id,
):
    customer_name, email = random.choice(CUSTOMERS)
    amount = random_amount()

    discrepancy = random.choice([50, 100, 150, 200, 250])
    bank_amount = amount - discrepancy

    timestamp = random_timestamp(transaction_number)

    description = f"Order #{transaction_number:04d}"

    gateway = create_gateway_record(
        canonical_id,
        transaction_number,
        amount,
        timestamp,
        customer_name,
        email,
        description,
    )

    bank = create_bank_record(
        transaction_number,
        bank_amount,
        timestamp + timedelta(minutes=random.randint(1, 5)),
        customer_name,
        description,
    )

    ledger = create_ledger_record(
        transaction_number,
        amount,
        timestamp + timedelta(minutes=random.randint(1, 3)),
        customer_name,
        email,
        description,
    )

    return gateway, bank, ledger


# ============================================================
# Main dataset generation
# ============================================================

def generate_dataset():
    random.seed(SEED)

    gateway_records = []
    bank_records = []
    ledger_records = []

    ground_truth = []

    transaction_number = 1

    for scenario, count in SCENARIO_DISTRIBUTION.items():

        for _ in range(count):

            canonical_id = f"CAN_{transaction_number:05d}"

            if scenario == "clean":
                gateway, bank, ledger = generate_clean_transaction(
                    transaction_number,
                    canonical_id,
                )

            elif scenario == "noisy":
                gateway, bank, ledger = generate_noisy_transaction(
                    transaction_number,
                    canonical_id,
                )

            elif scenario == "ambiguous":
                gateway, bank, ledger = generate_ambiguous_transaction(
                    transaction_number,
                    canonical_id,
                )

            elif scenario == "amount_discrepancy":
                gateway, bank, ledger = generate_amount_discrepancy_transaction(
                    transaction_number,
                    canonical_id,
                )

            elif scenario == "missing_or_duplicate":
                # Start with a clean transaction.
                gateway, bank, ledger = generate_clean_transaction(
                    transaction_number,
                    canonical_id,
                )

                # Split this group between genuinely missing records and
                # duplicate-looking candidates that must be reviewed.
                if random.choice([True, False]):
                    case_detail = "missing_record"
                    # Randomly remove either the bank or ledger record.
                    if random.choice([True, False]):
                        bank = None
                    else:
                        ledger = None
                else:
                    case_detail = "duplicate_candidate"
                    duplicate_bank = bank.copy()
                    duplicate_bank["utr"] = (
                        f"UTR_{random.randint(10000000, 99999999)}"
                    )
                    duplicate_bank["timestamp"] = (
                        datetime.fromisoformat(bank["timestamp"])
                        + timedelta(minutes=random.randint(1, 3))
                    ).isoformat()
                    bank_records.append(duplicate_bank)

            else:
                raise ValueError(f"Unknown scenario: {scenario}")

            # Add available records.
            if gateway:
                gateway_records.append(gateway)

            if bank:
                bank_records.append(bank)

            if ledger:
                ledger_records.append(ledger)

            if scenario == "clean":
                expected_outcome = "AUTO_MATCH"
            elif scenario in {"noisy", "ambiguous"}:
                expected_outcome = "REVIEW"
            elif scenario == "amount_discrepancy":
                expected_outcome = "EXCEPTION"
            elif case_detail == "duplicate_candidate":
                expected_outcome = "REVIEW"
            else:
                expected_outcome = "INCOMPLETE"

            # Ground truth describes the underlying relationship separately
            # from the safe operational outcome.  An amount discrepancy can
            # refer to the same transaction but must still be an exception.
            ground_truth.append({
                "canonical_id": canonical_id,
                "scenario": scenario,
                "case_detail": (
                    case_detail if scenario == "missing_or_duplicate" else ""
                ),
                "gateway_transaction_id": (
                    gateway["transaction_id"]
                    if gateway else ""
                ),
                "bank_utr": (
                    bank["utr"]
                    if bank else ""
                ),
                "ledger_invoice_id": (
                    ledger["invoice_id"]
                    if ledger else ""
                ),
                "expected_relationship": (
                    "MATCH"
                    if scenario in {
                        "clean",
                        "noisy",
                        "ambiguous",
                        "amount_discrepancy",
                    }
                    else "INCOMPLETE"
                ),
                "expected_outcome": expected_outcome,
            })

            transaction_number += 1

    # --------------------------------------------------------
    # Save generated data
    # --------------------------------------------------------

    write_csv(
        OUTPUT_DIR / "gateway.csv",
        gateway_records,
        [
            "transaction_id",
            "amount",
            "timestamp",
            "customer_name",
            "email",
            "description",
        ],
    )

    write_csv(
        OUTPUT_DIR / "bank.csv",
        bank_records,
        [
            "utr",
            "amount",
            "timestamp",
            "payer_name",
            "description",
        ],
    )

    write_csv(
        OUTPUT_DIR / "ledger.csv",
        ledger_records,
        [
            "invoice_id",
            "amount",
            "timestamp",
            "customer_name",
            "email",
            "description",
        ],
    )

    write_csv(
        GROUND_TRUTH_DIR / "ground_truth.csv",
        ground_truth,
        [
            "canonical_id",
            "scenario",
            "case_detail",
            "gateway_transaction_id",
            "bank_utr",
            "ledger_invoice_id",
            "expected_relationship",
            "expected_outcome",
        ],
    )

    print("Dataset generated successfully.")
    print(f"Gateway records: {len(gateway_records)}")
    print(f"Bank records:    {len(bank_records)}")
    print(f"Ledger records:  {len(ledger_records)}")
    print(f"Ground truth:    {len(ground_truth)}")


if __name__ == "__main__":
    generate_dataset()

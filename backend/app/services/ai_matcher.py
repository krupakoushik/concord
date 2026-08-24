import json
import os

from dotenv import load_dotenv
from google import genai

load_dotenv()

def get_client():
    api_key = os.getenv("GEMINI")

    if not api_key:
        raise RuntimeError(
            "GEMINI environment variable is not set."
        )

    return genai.Client(api_key=api_key)


def analyze_match(
    gateway_record: dict,
    candidate_record: dict,
    candidate_type: str,
) -> dict:

    client = get_client()

    prompt = f"""
You are an AI financial reconciliation assistant.

Your job is to determine whether two financial records
represent the same underlying transaction.

Gateway record:
{json.dumps(gateway_record, indent=2)}

Candidate {candidate_type} record:
{json.dumps(candidate_record, indent=2)}

Carefully compare:

1. Amount
2. Customer/payer identity
3. Timestamp
4. Description
5. Transaction/reference information
6. Missing or contradictory information

Return ONLY valid JSON:

{{
    "decision": "MATCH",
    "confidence": 0.95,
    "reasons": [
        "The amounts match exactly.",
        "The customer names refer to the same person.",
        "The timestamps are within a few minutes."
    ]
}}

Rules:

- decision must be one of:
  MATCH
  NO_MATCH
  REVIEW

- confidence must be a number from 0 to 1.

- Never ignore an amount discrepancy.

- Do not invent missing information.

- If the evidence is ambiguous, choose REVIEW.

- Keep the reasons short and specific.
"""

    response = client.models.generate_content(
        model="gemini-3.5-flash-lite",
        contents=prompt,
    )

    text = response.text.strip()

    # Handle accidental markdown code fences.
    if text.startswith("```"):
        text = text.replace("```json", "")
        text = text.replace("```", "")
        text = text.strip()

    return json.loads(text)
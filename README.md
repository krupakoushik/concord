# AI Finance Controller

An in-progress Razorpay Track 04 project for reconciling synthetic payment
gateway, bank, and merchant-ledger records. The intended workflow uses
deterministic matching for clear cases, assisted reasoning for ambiguity, hard
financial safety rules, and a human-review path for anything uncertain.

## Current implementation

- A deterministic, reproducible generator creates 100 canonical transactions
  across three data sources and keeps hidden ground truth for evaluation.
- Matching utilities normalize text, compare timestamps and amounts, and
  calculate explainable baseline pair scores.
- Unit tests cover the current matching utilities.
- A React/Vite frontend scaffold exists, but it is not yet the reconciliation
  dashboard described in `INFO.md`.

The API, persistence layer, reconciliation orchestration, metrics endpoint,
audit trail, review actions, and dashboard data integration are still to be
built. The project should not yet be represented as a finished finance tool.

## Run locally

From the repository root, create and activate a Python virtual environment,
then install the backend dependencies:

```powershell
py -m venv backend/venv
backend/venv/Scripts/python.exe -m pip install -r backend/requirements.txt
backend/venv/Scripts/python.exe scripts/generate_dataset.py
backend/venv/Scripts/python.exe -m pytest tests -q
```

To run the backend scaffold:

```powershell
backend/venv/Scripts/python.exe -m uvicorn app.main:app --app-dir backend --reload
```

To run the frontend scaffold:

```powershell
cd frontend
npm install
npm run dev
```

## Dataset semantics

`data/ground_truth/ground_truth.csv` intentionally keeps two separate labels:

- `expected_relationship`: whether available source rows refer to the same
  underlying transaction.
- `expected_outcome`: the safe action the reconciliation pipeline should take.

For example, amount discrepancies have a `MATCH` relationship but an
`EXCEPTION` outcome; they must never be automatically reconciled. Duplicate
candidates are labelled `REVIEW`.

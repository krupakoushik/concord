# AI Finance Controller --- Project Blueprint

## 0. Project Status

**Project:** AI Finance Controller --- Multi-Source Financial
Reconciliation Agent\
**Razorpay Track:** Track 04 --- AI Finance Controller\
**Deadline:** 25 August 2026, 12:00 PM IST\
**Current stage:** Foundation implemented: synthetic dataset generator,
baseline deterministic matching utilities, unit tests, FastAPI scaffold, and
React scaffold. The end-to-end reconciliation workflow and dashboard remain
to be built.

> **IMPORTANT CONTEXT FILE**
>
> This document is the source of truth for the project plan. If project
> context is lost, reread this file before making architectural,
> technical, or scope decisions.
>
> Do not silently change the project's core objective, scope,
> architecture, or technology choices. If a change becomes necessary,
> explicitly discuss the change first.

------------------------------------------------------------------------

# 1. Why We Are Building This

Razorpay's Track 04 problem statement is:

> **AI Finance Controller --- Run the books and the cash position**
>
> Build an agent that closes one finance-ops loop across a 50+ record
> batch of synthetic data, reporting its match rate and the exceptions
> it could not resolve.

Razorpay gives these example directions:

-   Multi-source reconciliation
-   Settlement Q&A agent
-   Forward cash forecaster
-   Tax-line matcher

Its stated evaluation bar is:

> **Throughput + measured accuracy + an honest exception list. One
> cherry-picked match proves nothing.**

The project therefore focuses on one concrete finance-operations
workflow:

## Multi-source financial reconciliation

Financial records can arrive from multiple systems such as:

-   payment gateways
-   bank/settlement records
-   merchant ledgers

These systems may describe the same underlying transaction differently.

For example:

``` text
Payment Gateway
TXN_48291
₹2,499
10:32
Rahul Kumar
"Order #8821"

Bank
UTR_99128
₹2,499
10:36
Rahul K
"UPI/8821"

Ledger
INV_8821
₹2,499
10:33
Rahul Kumar
"Order 8821"
```

A human can recognize that these probably represent the same
transaction, but naïve exact matching cannot because the identifiers and
text are not identical.

The system will automate the easy cases, use AI only for ambiguous
cases, and send uncertain or financially unsafe cases to human review.

------------------------------------------------------------------------

# 2. The Core Problem

The system answers:

> **"Which records from different financial sources refer to the same
> underlying transaction, and is it safe to reconcile them
> automatically?"**

The important distinction is that the AI is **not** responsible for
blindly making every decision.

The system will use:

1.  deterministic rules for obvious matches,
2.  AI/ML-assisted reasoning for ambiguous matches,
3.  deterministic safety rules to prevent unsafe automatic
    reconciliation,
4.  human review for unresolved exceptions.

The objective is to reduce manual reconciliation work without pretending
that every AI prediction is trustworthy.

------------------------------------------------------------------------

# 3. What We Are NOT Building

This is deliberately a focused MVP.

We are NOT building:

-   a complete accounting platform,
-   a payment gateway,
-   a production banking integration,
-   a real Razorpay payment system,
-   a consumer finance application,
-   a generic finance chatbot,
-   an autonomous accountant,
-   a tax filing system,
-   a production-grade fraud detection platform,
-   a mobile application,
-   a multi-agent AI framework,
-   a vector database/RAG system unless a concrete requirement emerges,
-   model fine-tuning,
-   unnecessary microservices,
-   Kubernetes or other infrastructure complexity,
-   authentication/user management unless required for the demo,
-   real financial/customer data.

The goal is to demonstrate **one complete, measurable finance-ops
loop**.

------------------------------------------------------------------------

# 4. Product Concept

## Working name

**AI Finance Controller**

The internal feature/project name can later be changed if a stronger
product name is chosen.

## One-line description

> An AI-assisted financial reconciliation system that automatically
> matches high-confidence records across multiple sources and routes
> ambiguous transactions to human review.

## Core workflow

``` text
Multiple Financial Sources
        |
        v
Data Normalization
        |
        v
Deterministic Matching
        |
        +----------------------+
        |                      |
    Obvious Match          Ambiguous Case
        |                      |
        |                      v
        |                 AI Analysis
        |                      |
        |                      v
        |                Confidence Score
        |                      |
        +----------+-----------+
                   |
                   v
          Safety / Business Rules
                   |
          +--------+--------+
          |                 |
       Reconcile        Exception
          |                 |
          |                 v
          |            Human Review
          |                 |
          +--------+--------+
                   |
                   v
             Audit Record
                   |
                   v
              Dashboard
```

------------------------------------------------------------------------

# 5. Example

## Case A --- Easy deterministic match

Gateway:

``` text
ID: TXN_1001
Amount: ₹1,499
Time: 10:31
Customer: rahul@example.com
Description: Order 8821
```

Bank:

``` text
ID: UTR_7821
Amount: ₹1,499
Time: 10:34
Customer: rahul@example.com
Description: UPI Order 8821
```

Ledger:

``` text
ID: INV_8821
Amount: ₹1,499
Time: 10:32
Customer: rahul@example.com
Description: Order #8821
```

The deterministic layer can identify the match using structured fields
and tolerances.

Result:

``` text
RECONCILED
Confidence: High
Method: Deterministic
```

No AI call is necessary.

------------------------------------------------------------------------

## Case B --- Ambiguous match requiring AI

Gateway:

``` text
ID: TXN_1002
Amount: ₹2,499
Time: 11:04
Customer: Rahul Kumar
Description: Order 8842
```

Bank:

``` text
ID: UTR_7822
Amount: ₹2,499
Time: 11:11
Customer: R Kumar
Description: UPI/8842
```

The identifiers and names are not identical.

The AI receives the relevant candidate records and evaluates the
evidence.

Possible result:

``` text
LIKELY MATCH
Confidence: 96%

Evidence:
- Amount matches
- Customer identity is highly similar
- Transaction time is within the allowed window
- Order reference is consistent
```

The system then applies safety rules before automatically reconciling.

------------------------------------------------------------------------

## Case C --- Financial discrepancy

Gateway:

``` text
Amount: ₹5,000
```

Bank:

``` text
Amount: ₹4,750
```

Ledger:

``` text
Amount: ₹5,000
```

Even if the AI believes the records represent the same transaction, the
system should NOT silently reconcile them.

Result:

``` text
EXCEPTION
Reason: Amount discrepancy of ₹250
Action: Manual review required
```

This is a core design principle.

------------------------------------------------------------------------

# 6. AI Philosophy

The project must demonstrate **AI judgment**, not merely AI usage.

The central principle is:

> **Use AI where interpretation is difficult; use deterministic code
> where deterministic code is better.**

For example:

### Do NOT use AI for:

-   exact amount equality,
-   obvious timestamp matching,
-   exact identifier matching,
-   straightforward database operations,
-   calculating totals,
-   calculating percentages,
-   enforcing monetary safety rules.

### Use AI/ML for:

-   ambiguous identity matching,
-   messy descriptions,
-   inconsistent names,
-   semantically similar transaction references,
-   evaluating multiple pieces of weak evidence,
-   explaining why two records appear related.

This allows the project to demonstrate the exact judgment Razorpay says
it cares about.

------------------------------------------------------------------------

# 7. AI/ML Approach

The exact AI implementation will be chosen during development based on
what can be made reliable within the deadline.

The project should prefer a simple, explainable architecture over
unnecessary AI complexity.

Potential approaches include:

### Option A --- Embedding/similarity-based matching

Convert relevant text fields into embeddings and compare semantic
similarity.

Useful for:

-   customer names,
-   merchant descriptions,
-   transaction descriptions,
-   references.

### Option B --- LLM-assisted structured judgment

Provide candidate records to an LLM and require a structured response
such as:

``` json
{
  "decision": "MATCH",
  "confidence": 0.96,
  "reasons": [
    "amount matches",
    "customer identity is highly similar",
    "timestamps are within tolerance"
  ]
}
```

The application then validates this output rather than blindly trusting
it.

### Option C --- Hybrid approach

Use deterministic features + similarity/ML + AI reasoning.

This is the preferred conceptual direction if practical.

The system should not depend on a single AI output without validation.

------------------------------------------------------------------------

# 8. Candidate Matching Strategy

The system should avoid comparing every record against every other
record when unnecessary.

A high-level matching pipeline:

``` text
1. Normalize records
2. Generate candidate pairs
3. Apply deterministic filters
4. Automatically resolve obvious matches
5. Send ambiguous candidates to AI/ML
6. Receive structured decision
7. Apply safety rules
8. Store result and evidence
```

## Candidate features

Potential features include:

-   amount difference,
-   timestamp difference,
-   normalized customer name similarity,
-   email similarity,
-   phone similarity if included in synthetic data,
-   transaction/reference similarity,
-   description similarity,
-   merchant similarity,
-   source information,
-   presence/absence of fields.

------------------------------------------------------------------------

# 9. Confidence and Decision Policy

The project should have explicit decision boundaries.

Example:

``` text
High confidence
    +
No safety-rule violation
        ↓
AUTO-RECONCILE
```

``` text
Medium confidence
        ↓
MANUAL REVIEW
```

``` text
Conflicting financial evidence
        ↓
EXCEPTION
```

The exact thresholds will be determined during testing rather than
arbitrarily presented as scientifically valid.

Example conceptual thresholds:

``` text
>= 0.90  → candidate for automatic reconciliation
0.70-0.90 → review
< 0.70   → unresolved
```

These numbers are placeholders until evaluated against the generated
test data.

------------------------------------------------------------------------

# 10. Synthetic Dataset

Razorpay explicitly requires a 50+ record batch of synthetic data.

We will create a larger dataset than the minimum so that the evaluation
is meaningful.

Target:

``` text
100–200 transaction records
```

Potential sources:

``` text
payment_gateway.csv
bank_records.csv
merchant_ledger.csv
```

The synthetic generator should deliberately introduce realistic
messiness.

## Clean cases

-   exact customer name
-   exact amount
-   close timestamp
-   matching references

## Noisy cases

-   abbreviated names,
-   different capitalization,
-   punctuation changes,
-   small timestamp differences,
-   different reference formats,
-   description variations.

## Exception cases

-   amount discrepancy,
-   missing bank record,
-   missing gateway record,
-   duplicate-looking records,
-   conflicting customer information,
-   records outside acceptable time windows.

The dataset should contain known ground truth so that the system can be
evaluated objectively.

------------------------------------------------------------------------

# 11. Ground Truth

Because the data is synthetic, we control the ground truth.

Each generated underlying transaction can have a canonical internal ID:

``` text
canonical_transaction_id
```

Each source record can reference that hidden ID during dataset
generation, while the application itself does not expose the ground
truth to the matching algorithm.

Example:

``` text
Canonical transaction:
CAN_00042

Gateway:
TXN_83921

Bank:
UTR_11928

Ledger:
INV_4921
```

The evaluator knows these belong together.

The matching algorithm only sees the observable financial records.

This lets us calculate real performance metrics.

------------------------------------------------------------------------

# 12. Evaluation Metrics

The project must report measurable performance.

At minimum:

## Match accuracy

How many reconciliation decisions were correct?

``` text
correct decisions / total evaluated decisions
```

## Precision

Among records predicted as matches, how many were actually matches?

``` text
TP / (TP + FP)
```

## Recall

Among actual matching records, how many did the system identify?

``` text
TP / (TP + FN)
```

## False-positive rate

Important because incorrectly merging two different financial records is
more dangerous than failing to automatically match one.

## Exception rate

Percentage of records routed to human review.

## Automatic reconciliation rate

Percentage of records resolved without human intervention.

## Throughput

Number of records processed per unit of time.

Example final dashboard:

``` text
Records processed:             150
Automatic matches:             121
AI-assisted matches:           18
Exceptions:                     11

Precision:                    96.1%
Recall:                       93.4%
Automatic resolution:         80.7%
Exceptions requiring review:   7.3%
Processing time:              2.8 sec
```

These values are examples only. The final project must display actual
measured values.

------------------------------------------------------------------------

# 13. Error Analysis

The project should not hide failures.

After testing, identify cases such as:

-   false positive,
-   false negative,
-   ambiguous identity,
-   conflicting amount,
-   missing source record,
-   duplicate candidate,
-   malformed data.

For each important failure, explain:

``` text
What happened?
Why did the system fail?
What was changed?
How did the change affect performance?
```

This directly supports Razorpay's:

> "What broke, and how you got out."

------------------------------------------------------------------------

# 14. Human-in-the-Loop Design

The system is not fully autonomous.

Human review is an intentional safety mechanism.

The reviewer should be able to see:

``` text
Transaction
Source A
Source B
Source C

AI decision
Confidence
Evidence/reasons

Conflict
Recommended action
```

The human can then:

``` text
Confirm Match
Reject Match
Mark as Exception
```

This makes the product more realistic and reduces the risk of an AI
model silently creating incorrect financial records.

------------------------------------------------------------------------

# 15. Audit Trail

Every reconciliation decision should produce an audit record.

Potential fields:

``` text
decision_id
transaction/candidate IDs
decision
confidence
decision_method
reasoning/evidence
timestamp
human_review_status
```

Example:

``` text
Decision: MATCH
Method: AI-assisted
Confidence: 0.96

Evidence:
- Amount matched
- Customer similarity: 0.94
- Timestamp difference: 7 minutes
- Reference similarity: high

Status:
Automatically reconciled
```

The audit trail is important because financial systems require
explainability and traceability.

------------------------------------------------------------------------

# 16. Application Architecture

Initial architecture:

``` text
                    ┌─────────────────────┐
                    │      React UI       │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │     FastAPI API     │
                    └──────────┬──────────┘
                               │
              ┌────────────────┼────────────────┐
              │                │                │
              ▼                ▼                ▼
       Data ingestion     Reconciliation     Metrics
                              engine
                               │
                    ┌──────────┴──────────┐
                    │                     │
                    ▼                     ▼
             Deterministic           AI/ML layer
               matching
                    │                     │
                    └──────────┬──────────┘
                               ▼
                       Safety / Rules
                               │
                               ▼
                         SQLite database
```

This is intentionally a monolithic application for speed and clarity.

No microservices unless there is a compelling reason.

------------------------------------------------------------------------

# 17. Technology Stack

## Backend

**Python + FastAPI**

Reasons:

-   already familiar,
-   fast to build,
-   good API structure,
-   easy integration with Python ML/AI tooling,
-   easy demonstration.

## Frontend

**React**

Reasons:

-   already familiar,
-   suitable for a dashboard,
-   enough flexibility for a clean demo.

## Styling

**Tailwind CSS**

Use only enough styling to make the dashboard clear and professional.

Do not spend hours polishing animations.

## Database

**SQLite**

Reasons:

-   zero infrastructure,
-   easy local development,
-   enough for synthetic demo data,
-   easy to inspect,
-   simple deployment.

If necessary, the schema can later be migrated to PostgreSQL.

## Data processing

Python.

Potential libraries:

-   pandas
-   NumPy
-   scikit-learn

Only add libraries when they serve a concrete purpose.

## AI

An external AI/LLM API or suitable local/model-based approach depending
on availability and reliability.

The AI provider is intentionally not hard-coded in this blueprint so the
implementation can choose the most practical option during development.

## Version control

Git + GitHub.

The repository must be public for the Razorpay submission.

------------------------------------------------------------------------

# 18. Suggested Project Structure

Initial structure:

``` text
ai-finance-controller/
│
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── api/
│   │   ├── models/
│   │   ├── schemas/
│   │   ├── services/
│   │   │   ├── ingestion.py
│   │   │   ├── normalization.py
│   │   │   ├── matching.py
│   │   │   ├── ai_matching.py
│   │   │   ├── reconciliation.py
│   │   │   └── metrics.py
│   │   └── database/
│   │
│   └── requirements.txt
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   └── services/
│   └── package.json
│
├── data/
│   ├── raw/
│   ├── generated/
│   └── ground_truth/
│
├── tests/
│
├── scripts/
│   └── generate_dataset.py
│
├── README.md
├── .gitignore
└── LICENSE
```

The exact structure can be simplified if implementation speed requires
it.

------------------------------------------------------------------------

# 19. API Responsibilities

Potential endpoints:

``` text
POST /api/dataset/generate
POST /api/reconciliation/run
GET  /api/reconciliation/results
GET  /api/reconciliation/results/{id}
GET  /api/metrics
POST /api/reconciliation/{id}/review
```

These are conceptual endpoints, not mandatory final names.

------------------------------------------------------------------------

# 20. Dashboard Requirements

The dashboard should show:

## Overview

-   total records
-   reconciled records
-   AI-assisted records
-   exceptions
-   match rate
-   precision/accuracy
-   processing time

## Reconciliation table

Columns:

``` text
Transaction
Status
Amount
Source comparison
Confidence
Method
Action
```

Statuses:

``` text
MATCHED
AI MATCH
EXCEPTION
MISSING
REVIEW
```

## Detail view

For a selected reconciliation:

-   source records,
-   matching evidence,
-   confidence,
-   decision,
-   reason,
-   discrepancy,
-   audit trail,
-   human review action.

The UI exists to demonstrate the system clearly, not to become the main
project.

------------------------------------------------------------------------

# 21. Dataset Generation Strategy

The synthetic generator should create controlled examples.

For example:

``` text
100 canonical transactions
```

Then generate:

``` text
100 gateway records
100 bank records
100 ledger records
```

Some percentage will be:

-   clean,
-   noisy,
-   ambiguous,
-   missing,
-   conflicting.

The exact distribution should be recorded.

Example:

``` text
60% easy matches
20% noisy matches
10% ambiguous matches
5% amount discrepancies
5% missing/duplicate cases
```

These values are starting points, not final scientific assumptions.

------------------------------------------------------------------------

# 22. Testing Strategy

We need tests at several levels.

## Unit tests

Test:

-   normalization,
-   amount comparison,
-   timestamp tolerance,
-   name normalization,
-   deterministic matching,
-   safety rules,
-   metric calculations.

## AI evaluation

Use a held-out subset where the correct answer is known.

Measure:

-   precision,
-   recall,
-   false positives,
-   false negatives.

## End-to-end test

Run the entire pipeline:

``` text
synthetic data
→ ingestion
→ normalization
→ matching
→ AI
→ safety rules
→ database
→ metrics
→ UI
```

------------------------------------------------------------------------

# 23. Failure Cases We Intentionally Want

The system should encounter failures during development.

Examples:

### Failure 1 --- AI overmatches

Two customers have similar names.

Solution:

Increase the importance of stronger identifiers and require additional
evidence.

### Failure 2 --- AI ignores amount discrepancy

Solution:

Add deterministic financial safety rules that override AI decisions.

### Failure 3 --- AI output is malformed

Solution:

Validate structured output and route invalid responses to manual review.

### Failure 4 --- Missing records

Solution:

Classify as unresolved rather than forcing a match.

### Failure 5 --- Duplicate candidates

Solution:

Present multiple candidates and require human review.

These failures can become part of the final video.

------------------------------------------------------------------------

# 24. Security / Safety Principles

Even though this is synthetic data, the architecture should demonstrate
financial-system discipline.

Principles:

-   never expose real financial data,
-   never allow AI to override hard monetary constraints,
-   never silently reconcile conflicting amounts,
-   validate AI output,
-   maintain an audit trail,
-   route uncertain decisions to humans,
-   make confidence visible,
-   do not claim production readiness.

------------------------------------------------------------------------

# 25. Demo Strategy

The five-minute video should not be a slide-heavy presentation.

It should demonstrate the actual product.

## Target structure

### 0:00--0:30 --- Problem

Explain:

> Financial data arrives from multiple systems using different
> identifiers and inconsistent descriptions. Humans have to reconcile
> these records manually.

### 0:30--1:00 --- Architecture

Show:

``` text
Sources
→ normalization
→ deterministic matching
→ AI for ambiguity
→ safety rules
→ human review
```

### 1:00--3:15 --- Live demo

Run the system on the dataset.

Show:

-   easy match,
-   AI-assisted match,
-   discrepancy,
-   unresolved record,
-   dashboard metrics.

### 3:15--4:00 --- AI judgment

Explain:

> AI is intentionally not used for deterministic cases. It is used only
> where records are ambiguous.

Show one example.

### 4:00--4:30 --- Metrics

Show actual:

-   precision,
-   recall,
-   match rate,
-   exception rate,
-   throughput.

### 4:30--5:00 --- Failure recovery

Explain one meaningful failure encountered during development and how
the system was changed.

------------------------------------------------------------------------

# 26. What We Want Razorpay to Take Away

After watching the demo, the evaluator should think:

> "This person understands that AI is a component of a software system,
> not the product itself."

They should see:

-   real problem selection,
-   sensible AI usage,
-   deterministic engineering,
-   measurable performance,
-   safety boundaries,
-   human-in-the-loop design,
-   clean implementation,
-   honest reporting of failures.

------------------------------------------------------------------------

# 27. Development Principles

## Principle 1 --- Ship the core first

The reconciliation pipeline must work before UI polish.

## Principle 2 --- No feature creep

If a feature does not directly improve the reconciliation workflow or
demo, it probably does not belong in the MVP.

## Principle 3 --- Measure everything important

Do not invent impressive numbers.

Run the system and report actual measurements.

## Principle 4 --- AI must earn its place

Every AI component must have a reason for existing.

## Principle 5 --- Never hide failures

Exceptions are a feature, not an embarrassment.

## Principle 6 --- Prefer simple architecture

A simple working system is better than a sophisticated broken system.

## Principle 7 --- Keep the project explainable

The developer should understand every major component well enough to
explain it in an interview.

------------------------------------------------------------------------

# 28. Current Scope Lock

Unless explicitly discussed and changed, the following is the agreed
scope:

### Core product

**AI-assisted multi-source financial reconciliation.**

### Data

Synthetic financial records, minimum 50; target 100--200.

### Sources

Payment gateway + bank/settlement + merchant ledger.

### AI role

Resolve ambiguous cross-source matches and provide structured reasoning
/ confidence.

### Non-AI role

Normalization, deterministic matching, financial safety rules, database
operations, metrics, and final validation.

### Human role

Review uncertain/conflicting cases.

### Output

Matched records, AI-assisted matches, unresolved exceptions, audit
trail, metrics.

### UI

A focused reconciliation dashboard.

### Tech

Python + FastAPI + React + Tailwind + SQLite + pandas/scikit-learn as
needed + selected AI API/model.

### Submission

Public GitHub repository + working application + approximately
five-minute unlisted video + Razorpay form.

------------------------------------------------------------------------

# 29. Definition of Done

The project is done when all of the following are true:

-   [ ] Public GitHub repository exists.
-   [ ] Synthetic dataset contains 50+ records.
-   [ ] Dataset has known ground truth.
-   [ ] Multiple financial sources are represented.
-   [ ] Records are normalized.
-   [ ] Deterministic matching works.
-   [ ] AI-assisted matching works for ambiguous cases.
-   [ ] AI output is validated.
-   [ ] Monetary safety rules exist.
-   [ ] Exceptions are generated rather than forcibly resolved.
-   [ ] Human review path exists.
-   [ ] Audit trail exists.
-   [ ] Metrics are calculated from actual test results.
-   [ ] Dashboard displays reconciliation results.
-   [ ] At least one meaningful failure has been tested and documented.
-   [ ] README explains architecture and setup.
-   [ ] Application can be run from a clean environment.
-   [ ] Five-minute demo video is recorded.
-   [ ] Razorpay application form is submitted before the deadline.

------------------------------------------------------------------------

# 30. What We Do NOT Change Casually

Do not change the project into:

-   a generic finance chatbot,
-   a generic fraud detector,
-   an expense tracker,
-   a full accounting platform,
-   a generic RAG application,
-   an autonomous agent that blindly performs financial actions.

If a new idea appears, compare it against this question:

> **Does this make multi-source financial reconciliation materially
> better, safer, more measurable, or easier for a human?**

If not, it is probably scope creep.

------------------------------------------------------------------------

# 31. Implementation Order

We will build in this order:

``` text
1. Project setup
        ↓
2. Data model
        ↓
3. Synthetic dataset generator
        ↓
4. Data normalization
        ↓
5. Deterministic reconciliation
        ↓
6. Ground-truth evaluation
        ↓
7. AI-assisted matching
        ↓
8. Safety rules
        ↓
9. Exception handling
        ↓
10. Metrics
        ↓
11. Database persistence
        ↓
12. FastAPI endpoints
        ↓
13. React dashboard
        ↓
14. Testing / failure injection
        ↓
15. README / architecture
        ↓
16. 5-minute video
        ↓
17. Final submission
```

Do not jump directly to the frontend.

Do not start by randomly integrating an AI API.

Build the underlying system first.

------------------------------------------------------------------------

# 32. Context Recovery Instructions

If project context is lost, the first thing to do is read this document.

The assistant should then preserve these facts:

1.  The project is for Razorpay's AI Intern selection process.
2.  The selected track is Track 04 --- AI Finance Controller.
3.  The project is an AI-assisted multi-source financial reconciliation
    system.
4.  The project uses synthetic data.
5.  The minimum batch size is 50+ records; target is 100--200.
6.  AI is deliberately used only for ambiguous interpretation/matching.
7.  Deterministic code handles obvious matches and financial safety
    rules.
8.  Uncertain cases go to human review.
9.  The project must report real metrics and exceptions.
10. The system must have an audit trail.
11. The application should remain focused and demoable.
12. The deadline is 25 August 2026 at 12:00 PM IST.
13. The public GitHub repository and five-minute demo are submission
    requirements.
14. The goal is not to build the biggest AI system; the goal is to build
    a reliable, measurable, explainable finance-ops workflow.

**When uncertain, prioritize this document over assumptions.**

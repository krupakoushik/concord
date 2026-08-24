from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.services.reconciliation import get_reconciliation_results

app = FastAPI(title="RECON API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {
        "name": "RECON",
        "status": "online"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }


@app.get("/reconcile")
def reconcile_transactions():
    results = get_reconciliation_results()

    return {
        "status": "success",
        "count": len(results),
        "results": results
    }
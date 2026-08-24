import { useEffect, useMemo, useState } from "react";
import {
  ArrowUpRight,
  ChevronRight,
  RefreshCw,
  Search,
  ShieldCheck,
  Sparkles,
  TriangleAlert,
  X,
} from "lucide-react";

import "./index.css";

type ReconciliationResult = {
  transaction_id: string;
  gateway_amount: number;
  gateway_timestamp: string;
  customer_name: string;

  bank_utr: string | null;
  bank_amount: number | null;
  bank_score: number;

  ledger_invoice_id: string | null;
  ledger_amount: number | null;
  ledger_score: number;

  ai_decision?: string | null;
  ai_confidence?: number | null;
  ai_reasons?: string[];

  status: string;
};

const API_URL = "http://127.0.0.1:8000";

function formatCurrency(amount: number | null) {
  if (amount === null || amount === undefined) return "—";

  return new Intl.NumberFormat("en-IN", {
    style: "currency",
    currency: "INR",
    maximumFractionDigits: 0,
  }).format(amount);
}

function formatTime(timestamp: string) {
  return new Date(timestamp).toLocaleTimeString("en-IN", {
    hour: "2-digit",
    minute: "2-digit",
  });
}

function App() {
  const [transactions, setTransactions] = useState<ReconciliationResult[]>([]);
  const [loading, setLoading] = useState(true);
  const [selected, setSelected] = useState<ReconciliationResult | null>(null);
  const [search, setSearch] = useState("");
  const [activeFilter, setActiveFilter] = useState<
    "all" | "matched" | "ai" | "review" | "exceptions"
  >("all");

  async function loadTransactions() {
    try {
      setLoading(true);

      const response = await fetch(`${API_URL}/reconcile`);

      if (!response.ok) {
        throw new Error("Failed to fetch reconciliation data");
      }

      const data = await response.json();

      setTransactions(data.results ?? []);
    } catch (error) {
      console.error(error);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadTransactions();
  }, []);

  function handleFilter(filter: typeof activeFilter) {
    setActiveFilter((current) =>
      current === filter ? "all" : filter,
    );
  }

  const filteredTransactions = useMemo(() => {
    const query = search.toLowerCase().trim();

    return transactions.filter((transaction) => {
      const matchesFilter =
        activeFilter === "all" ||
        (activeFilter === "matched" &&
          transaction.status === "MATCHED") ||
        (activeFilter === "ai" &&
          (transaction.ai_decision === "MATCH" ||
            transaction.ai_decision === "MATCHED")) ||
        (activeFilter === "review" &&
          (transaction.status === "REVIEW" ||
            transaction.status === "NEEDS_REVIEW")) ||
        (activeFilter === "exceptions" &&
          (transaction.status === "EXCEPTION" ||
            transaction.status === "UNMATCHED"));

      const matchesSearch =
        !query ||
        [
          transaction.transaction_id,
          transaction.customer_name,
          transaction.bank_utr,
          transaction.ledger_invoice_id,
        ]
          .filter(Boolean)
          .some((value) =>
            String(value).toLowerCase().includes(query),
          );

      return matchesFilter && matchesSearch;
    });
  }, [transactions, search, activeFilter]);

  const stats = useMemo(() => {
    const matched = transactions.filter(
      (transaction) => transaction.status === "MATCHED",
    ).length;

    const review = transactions.filter(
      (transaction) =>
        transaction.status === "REVIEW" ||
        transaction.status === "NEEDS_REVIEW",
    ).length;

    const exceptions = transactions.filter(
      (transaction) =>
        transaction.status === "EXCEPTION" ||
        transaction.status === "UNMATCHED",
    ).length;

    const aiMatched = transactions.filter(
      (transaction) =>
        transaction.ai_decision === "MATCH" ||
        transaction.ai_decision === "MATCHED",
    ).length;

    return {
      total: transactions.length,
      matched,
      aiMatched,
      review,
      exceptions,
    };
  }, [transactions]);

  return (
    <div className="app-shell">


      {/* MAIN */}

      <main className="main-content">
        <header className="topbar">
          <div>
            <div className="eyebrow">FINANCIAL INTELLIGENCE</div>

            <h1>
              CONCORD
            </h1>
          </div>

          <button className="refresh-button" onClick={loadTransactions}>
            <RefreshCw size={15} className={loading ? "spin" : ""} />
            Refresh
          </button>
        </header>

        {/* HERO METRICS */}

        <section className="metrics">
          <Metric
            number={stats.total}
            label="TRANSACTIONS"
            description="Processed"
            active={activeFilter === "all"}
            onClick={() => handleFilter("all")}
          />

          <Metric
            number={stats.matched}
            label="AUTO-MATCHED"
            description="Deterministic matches"
            accent
            active={activeFilter === "matched"}
            onClick={() => handleFilter("matched")}
          />

          <Metric
            number={stats.aiMatched}
            label="AI-MATCHED"
            description="Resolved by intelligence"
            ai
            active={activeFilter === "ai"}
            onClick={() => handleFilter("ai")}
          />

          <Metric
            number={stats.review}
            label="REVIEW"
            description="Needs attention"
            active={activeFilter === "review"}
            onClick={() => handleFilter("review")}
          />

          <Metric
            number={stats.exceptions}
            label="EXCEPTIONS"
            description="Discrepancies"
            warning
            active={activeFilter === "exceptions"}
            onClick={() => handleFilter("exceptions")}
          />
        </section>

        {/* TRANSACTIONS */}

        <section className="transaction-section">
          <div className="section-header">
            <div>
              <div className="section-kicker">LIVE LEDGER</div>

              <h2>Transactions</h2>

              <p>
                Gateway <span>→</span> Bank <span>→</span> Ledger
              </p>
            </div>

            {activeFilter !== "all" && (
              <div className="active-filter">
                FILTER:{" "}
                <strong>
                  {activeFilter === "matched"
                    ? "AUTO-MATCHED"
                    : activeFilter === "ai"
                      ? "AI-MATCHED"
                      : activeFilter === "review"
                        ? "REVIEW"
                        : "EXCEPTIONS"}
                </strong>

                <button onClick={() => setActiveFilter("all")}>
                  <X size={12} />
                </button>
              </div>
            )}

            <div className="search-box">
              <Search size={15} />

              <input
                placeholder="Search transaction..."
                value={search}
                onChange={(event) => setSearch(event.target.value)}
              />
            </div>
          </div>

          <div className="table-header">
            <span>TRANSACTION</span>
            <span>CUSTOMER</span>
            <span>AMOUNT</span>
            <span>FLOW</span>
            <span>STATUS</span>
            <span />
          </div>

          <div className="transaction-list">
            {loading ? (
              <div className="loading-state">
                <RefreshCw className="spin" size={20} />
                Loading reconciliation engine...
              </div>
            ) : filteredTransactions.length === 0 ? (
              <div className="loading-state">No transactions found.</div>
            ) : (
              filteredTransactions.map((transaction) => (
                <button
                  className="transaction-row"
                  key={transaction.transaction_id}
                  onClick={() => setSelected(transaction)}
                >
                  <div className="transaction-id">
                    {transaction.transaction_id}
                    <small>
                      {formatTime(transaction.gateway_timestamp)}
                    </small>
                  </div>

                  <div className="customer">
                    {transaction.customer_name}
                  </div>

                  <div className="amount">
                    {formatCurrency(transaction.gateway_amount)}
                  </div>

                  <div className="flow">
                    <span className="flow-node">G</span>
                    <span className="flow-line" />
                    <span className="flow-node">B</span>
                    <span className="flow-line" />
                    <span className="flow-node">L</span>
                  </div>

                  <StatusBadge status={transaction.status} />

                  <ChevronRight size={17} className="row-arrow" />
                </button>
              ))
            )}
          </div>
        </section>

        <footer className="page-footer">
          <span>RECONCILIATION ENGINE</span>
          <span>BUILT FOR FINANCIAL OPERATIONS</span>
          <span>2026</span>
        </footer>
      </main>

      {/* DETAIL PANEL */}

      {selected && (
        <div className="overlay" onClick={() => setSelected(null)}>
          <aside
            className="detail-panel"
            onClick={(event) => event.stopPropagation()}
          >
            <button
              className="close-button"
              onClick={() => setSelected(null)}
            >
              <X size={18} />
            </button>

            <div className="eyebrow">TRANSACTION DOSSIER</div>

            <h2>{selected.transaction_id}</h2>

            <div className="detail-customer">
              {selected.customer_name}
            </div>

            <div className="detail-status">
              <StatusBadge status={selected.status} />
            </div>

            <div className="detail-amount">
              {formatCurrency(selected.gateway_amount)}
            </div>

            <div className="detail-divider" />

            <DetailRecord
              title="GATEWAY"
              id={selected.transaction_id}
              amount={selected.gateway_amount}
              timestamp={selected.gateway_timestamp}
            />

            <DetailRecord
              title="BANK"
              id={selected.bank_utr}
              amount={selected.bank_amount}
              score={selected.bank_score}
            />

            <DetailRecord
              title="LEDGER"
              id={selected.ledger_invoice_id}
              amount={selected.ledger_amount}
              score={selected.ledger_score}
            />

            {(selected.ai_decision || selected.ai_reasons?.length) && (
              <>
                <div className="detail-divider" />

                <div className="ai-heading">
                  <Sparkles size={15} />
                  AI ANALYSIS
                </div>

                <div className="ai-decision">
                  <span>{selected.ai_decision ?? "ANALYZED"}</span>

                  {selected.ai_confidence !== null &&
                    selected.ai_confidence !== undefined && (
                      <strong>
                        {Math.round(selected.ai_confidence * 100)}%
                      </strong>
                    )}
                </div>

                <div className="ai-reasons">
                  {(selected.ai_reasons ?? []).map((reason, index) => (
                    <div key={index}>
                      <span>+</span>
                      {reason}
                    </div>
                  ))}
                </div>
              </>
            )}
          </aside>
        </div>
      )}
    </div>
  );
}

function Metric({
  number,
  label,
  description,
  accent,
  ai,
  warning,
  active,
  onClick,
}: {
  number: number;
  label: string;
  description: string;
  accent?: boolean;
  ai?: boolean;
  warning?: boolean;
  active?: boolean;
  onClick?: () => void;
}) {
  return (
      <button
        className={`metric ${accent ? "accent" : ""} ${ai ? "ai" : ""} ${
          warning ? "warning" : ""
        } ${active ? "active" : ""}`}
        onClick={onClick}
      >
      <div className="metric-number">{number}</div>
      <div className="metric-label">{label}</div>
      <div className="metric-description">{description}</div>
    </button>
  );
}

function StatusBadge({ status }: { status: string }) {
  const normalized = status.toUpperCase();

  let type = "neutral";

  if (normalized === "MATCHED" || normalized === "MATCH") {
    type = "success";
  } else if (
    normalized === "REVIEW" ||
    normalized === "NEEDS_REVIEW"
  ) {
    type = "review";
  } else if (
    normalized === "EXCEPTION" ||
    normalized === "UNMATCHED"
  ) {
    type = "exception";
  }

  return (
    <div className={`status-badge ${type}`}>
      {type === "success" ? (
        <ShieldCheck size={13} />
      ) : type === "exception" ? (
        <TriangleAlert size={13} />
      ) : null}

      {normalized.replace("_", " ")}
    </div>
  );
}

function DetailRecord({
  title,
  id,
  amount,
  timestamp,
  score,
}: {
  title: string;
  id: string | null;
  amount: number | null;
  timestamp?: string;
  score?: number;
}) {
  return (
    <div className="detail-record">
      <div className="record-heading">
        <span>{title}</span>

        {score !== undefined && (
          <span>{Math.round(score * 100)}% confidence</span>
        )}
      </div>

      <div className="record-main">
        <strong>{id ?? "NO MATCH"}</strong>

        <span>{formatCurrency(amount)}</span>
      </div>

      {timestamp && (
        <div className="record-time">
          {new Date(timestamp).toLocaleString("en-IN")}
        </div>
      )}
    </div>
  );
}

export default App;
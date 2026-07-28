import { StatsCard } from '../components/dashboard/StatsCard';

export function Analytics() {
  return (
    <div>
      <div className="page-heading">
        <div>
          <p className="eyebrow">METRICS & HEALTH</p>
          <h2>System Performance & Token Analytics</h2>
          <p>Real-time telemetry tracking vector search latency, LLM response timing, and token consumption.</p>
        </div>
      </div>

      <div className="stats-grid">
        <StatsCard label="Retrieval latency" value="142 ms" icon="⚡" detail="Avg vector + sparse search" />
        <StatsCard label="Embedding latency" value="18 ms" icon="◴" detail="BAAI/bge-small-en-v1.5" />
        <StatsCard label="Tokens used (24h)" value="42.8k" icon="⌁" detail="Groq / Llama-3.3 70B" />
        <StatsCard label="Vector DB Status" value="Healthy" icon="✓" detail="Qdrant collection connected" />
      </div>

      <div className="dashboard-grid analytics-grid">
        <div className="card">
          <div className="card-heading">
            <h3>Latency Breakdown</h3>
          </div>
          <div className="row">
            <span>BM25 Keyword Index Search</span>
            <strong>12 ms</strong>
          </div>
          <div className="row">
            <span>Qdrant Vector Similarity Search</span>
            <strong>28 ms</strong>
          </div>
          <div className="row">
            <span>Cross-Encoder Reranking</span>
            <strong>102 ms</strong>
          </div>
          <div className="row">
            <span>LLM Generation (First Token)</span>
            <strong>180 ms</strong>
          </div>
        </div>

        <div className="card">
          <div className="card-heading">
            <h3>Top Queried Documents</h3>
          </div>
          <div className="row">
            <span>Marketing.pdf</span>
            <small>148 queries</small>
          </div>
          <div className="row">
            <span>Enterprise_Architecture_Overview.pdf</span>
            <small>96 queries</small>
          </div>
          <div className="row">
            <span>Q3_Financial_Analysis.xlsx</span>
            <small>52 queries</small>
          </div>
        </div>
      </div>
    </div>
  );
}

export function RetrievalChart() {
  return (
    <div className="card chart">
      <div className="card-heading">
        <h3>Retrieval latency</h3>
        <span>Last 7 days</span>
      </div>
      <div className="chart-bars">
        <i style={{ height: '40%' }}></i>
        <i style={{ height: '65%' }}></i>
        <i style={{ height: '50%' }}></i>
        <i style={{ height: '85%' }}></i>
        <i style={{ height: '60%' }}></i>
        <i style={{ height: '75%' }}></i>
      </div>
      <small className="muted">Connect an analytics endpoint to view measured retrieval timings.</small>
    </div>
  );
}

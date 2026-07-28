export function ProviderCard({ name, status }: { name: string; status: string }) {
  return (
    <div className="card" style={{ padding: '16px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
      <strong>{name}</strong>
      <span className="badge success">{status}</span>
    </div>
  );
}

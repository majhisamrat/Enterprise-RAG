interface StatsCardProps {
  label: string;
  value: string | number;
  icon: string;
  detail: string;
}

export function StatsCard({ label, value, icon, detail }: StatsCardProps) {
  return (
    <div className="stat-card">
      <p>{label}</p>
      <strong>{value}</strong>
      <small>{detail}</small>
      <span className="stat-icon">{icon}</span>
    </div>
  );
}

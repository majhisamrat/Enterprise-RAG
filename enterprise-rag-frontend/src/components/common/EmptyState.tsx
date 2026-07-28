interface EmptyStateProps {
  title: string;
  description: string;
}

export function EmptyState({ title, description }: EmptyStateProps) {
  return (
    <div className="empty">
      <strong>{title}</strong>
      <p>{description}</p>
    </div>
  );
}

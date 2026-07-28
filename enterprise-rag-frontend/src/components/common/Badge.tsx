import { ReactNode } from 'react';

interface BadgeProps {
  children: ReactNode;
  variant?: 'success' | 'warning' | 'danger' | 'info';
}

export function Badge({ children, variant = 'success' }: BadgeProps) {
  return <span className={`badge ${variant}`}>{children}</span>;
}

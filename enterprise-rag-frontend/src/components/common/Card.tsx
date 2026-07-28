import { ReactNode } from 'react';

interface CardProps {
  children: ReactNode;
  className?: string;
  title?: string;
}

export function Card({ children, className = '', title }: CardProps) {
  return (
    <div className={`card ${className}`}>
      {title && (
        <div className="card-heading">
          <h3>{title}</h3>
        </div>
      )}
      {children}
    </div>
  );
}

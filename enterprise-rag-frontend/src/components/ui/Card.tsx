import { ReactNode, HTMLAttributes } from 'react';
import clsx from 'clsx';

interface CardProps extends HTMLAttributes<HTMLDivElement> {
  children: ReactNode;
  variant?: 'default' | 'elevated' | 'outlined';
  hover?: boolean;
}

export function Card({
  children,
  variant = 'default',
  hover = false,
  className,
  ...props
}: CardProps) {
  const baseStyles = 'rounded-xl transition-all duration-200';

  const variants = {
    default: 'bg-white border border-brand-line shadow-sm',
    elevated: 'bg-white shadow-lg',
    outlined: 'bg-transparent border-2 border-brand-line',
  };

  const hoverStyles = hover ? 'hover:shadow-lg hover:border-brand-cyan' : '';

  return (
    <div
      className={clsx(baseStyles, variants[variant], hoverStyles, className)}
      {...props}
    >
      {children}
    </div>
  );
}

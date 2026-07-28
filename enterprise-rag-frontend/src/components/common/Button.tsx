import { ButtonHTMLAttributes, ReactNode } from 'react';

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  children: ReactNode;
  variant?: 'primary' | 'secondary' | 'danger' | 'ghost';
  size?: 'sm' | 'md' | 'lg';
}

export function Button({ children, variant = 'primary', size = 'md', className = '', ...props }: ButtonProps) {
  const baseClass = 'button';
  const variantClass = variant === 'primary' ? 'primary' : variant;
  return (
    <button className={`${baseClass} ${variantClass} ${size} ${className}`} {...props}>
      {children}
    </button>
  );
}

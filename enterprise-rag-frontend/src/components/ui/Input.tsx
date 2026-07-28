import { InputHTMLAttributes, ReactNode, forwardRef } from 'react';
import clsx from 'clsx';

interface InputProps extends InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
  icon?: ReactNode;
  iconPosition?: 'left' | 'right';
}

export const Input = forwardRef<HTMLInputElement, InputProps>(
  ({ label, error, icon, iconPosition = 'left', className, ...props }, ref) => {
    return (
      <div className="w-full">
        {label && (
          <label className="block text-sm font-semibold text-brand-ink mb-2">
            {label}
          </label>
        )}
        <div className="relative">
          {icon && iconPosition === 'left' && (
            <div className="absolute left-3 top-1/2 -translate-y-1/2 text-brand-muted">
              {icon}
            </div>
          )}
          <input
            ref={ref}
            className={clsx(
              'w-full px-4 py-2.5 rounded-lg border border-brand-line bg-white text-brand-ink transition-all duration-200',
              'focus:outline-none focus:ring-2 focus:ring-brand-cyan focus:border-transparent',
              'placeholder-brand-muted',
              icon && iconPosition === 'left' && 'pl-10',
              icon && iconPosition === 'right' && 'pr-10',
              error && 'border-semantic-danger focus:ring-semantic-danger',
              className
            )}
            {...props}
          />
          {icon && iconPosition === 'right' && (
            <div className="absolute right-3 top-1/2 -translate-y-1/2 text-brand-muted">
              {icon}
            </div>
          )}
        </div>
        {error && (
          <p className="mt-1 text-xs text-semantic-danger">{error}</p>
        )}
      </div>
    );
  }
);

Input.displayName = 'Input';

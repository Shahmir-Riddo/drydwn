import React from 'react';
import { clsx } from 'clsx';

export interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'outline' | 'accent' | 'ghost' | 'danger';
  size?: 'sm' | 'md' | 'lg';
  isLoading?: boolean;
}

export const Button: React.FC<ButtonProps> = ({
  children,
  variant = 'outline',
  size = 'md',
  isLoading = false,
  className,
  disabled,
  ...props
}) => {
  const baseClasses =
    'inline-flex items-center justify-center gap-2 font-label uppercase tracking-widest transition-all duration-200 focus:outline-none disabled:opacity-50 disabled:pointer-events-none rounded-sm';

  const sizeClasses = {
    sm: 'px-3 py-1.5 text-[10px] font-semibold',
    md: 'px-4 py-2 text-xs font-semibold',
    lg: 'px-6 py-2.5 text-xs font-semibold',
  };

  const variantClasses = {
    outline:
      'border border-border text-text-primary bg-transparent hover:border-accent hover:text-accent',
    accent:
      'border border-accent bg-accent text-white hover:bg-accent-hover hover:border-accent-hover',
    ghost:
      'border border-transparent text-text-secondary hover:text-text-primary hover:bg-surface',
    danger:
      'border border-rose-200 text-rose-700 bg-rose-50/50 hover:bg-rose-100 hover:border-rose-300',
  };

  return (
    <button
      className={clsx(baseClasses, sizeClasses[size], variantClasses[variant], className)}
      disabled={disabled || isLoading}
      {...props}
    >
      {isLoading && (
        <svg
          className="animate-spin -ml-1 mr-1.5 h-3.5 w-3.5 text-current"
          xmlns="http://www.w3.org/2000/svg"
          fill="none"
          viewBox="0 0 24 24"
        >
          <circle
            className="opacity-25"
            cx="12"
            cy="12"
            r="10"
            stroke="currentColor"
            strokeWidth="4"
          />
          <path
            className="opacity-75"
            fill="currentColor"
            d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
          />
        </svg>
      )}
      {children}
    </button>
  );
};

import { forwardRef, type ButtonHTMLAttributes } from 'react';
import { cn } from '@/lib/utils';

export interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'ghost' | 'danger' | 'outline';
  size?: 'sm' | 'md' | 'lg';
}

export const Button = forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant = 'primary', size = 'md', children, ...props }, ref) => {
    return (
      <button
        ref={ref}
        className={cn(
          'inline-flex items-center justify-center gap-2 font-body font-semibold transition-all rounded-lg disabled:opacity-50 disabled:pointer-events-none active:scale-[0.98]',
          {
            'bg-primary-container text-on-primary hover:bg-primary shadow-sm': variant === 'primary',
            'bg-surface-container-low border border-surface-container-highest text-on-surface hover:bg-surface-container-high shadow-sm': variant === 'secondary',
            'text-on-surface-variant hover:bg-surface-container-high hover:text-on-surface': variant === 'ghost',
            'bg-error text-on-error hover:bg-on-error-container shadow-sm': variant === 'danger',
            'border border-outline-variant text-on-surface hover:bg-surface-container-high': variant === 'outline',
          },
          {
            'h-8 px-2.5 text-label-sm': size === 'sm',
            'h-10 px-4 text-label-md': size === 'md',
            'h-11 px-5 text-body-md': size === 'lg',
          },
          className
        )}
        {...props}
      >
        {children}
      </button>
    );
  }
);
Button.displayName = 'Button';

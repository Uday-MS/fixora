import { cn } from '@/lib/utils';
import type { ReactNode } from 'react';

interface BadgeProps {
  variant?: 'default' | 'critical' | 'warning' | 'success' | 'accent' | 'outline' | 'info';
  size?: 'sm' | 'md';
  dot?: boolean;
  pulse?: boolean;
  children: ReactNode;
  className?: string;
}

export function Badge({ variant = 'default', size = 'sm', dot, pulse, children, className }: BadgeProps) {
  return (
    <span
      className={cn(
        'inline-flex items-center gap-1.5 font-mono rounded tracking-wider uppercase',
        {
          'bg-surface-container-high text-on-surface': variant === 'default',
          'bg-error-container text-on-error-container font-semibold': variant === 'critical',
          'bg-primary-fixed text-on-primary-fixed-variant font-semibold': variant === 'warning',
          'bg-success-container text-success font-semibold': variant === 'success',
          'bg-primary-container text-on-primary font-semibold': variant === 'accent',
          'bg-surface-container-low text-primary border border-primary-fixed': variant === 'info',
          'border border-surface-container-highest text-on-surface-variant': variant === 'outline',
        },
        {
          'px-1.5 py-0.5 text-mono-tag': size === 'sm',
          'px-2 py-1 text-label-sm': size === 'md',
        },
        className
      )}
    >
      {dot && (
        <span
          className={cn(
            'w-1.5 h-1.5 rounded-full shrink-0',
            {
              'bg-on-surface-variant': variant === 'default',
              'bg-error': variant === 'critical',
              'bg-primary-container': variant === 'warning' || variant === 'info',
              'bg-success': variant === 'success',
              'bg-on-primary': variant === 'accent',
              'bg-outline': variant === 'outline',
            },
            pulse && 'animate-ping'
          )}
        />
      )}
      {children}
    </span>
  );
}

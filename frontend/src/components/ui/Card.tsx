import { cn } from '@/lib/utils';
import type { ReactNode, HTMLAttributes } from 'react';

interface CardProps extends HTMLAttributes<HTMLDivElement> {
  children: ReactNode;
  hover?: boolean;
  padding?: 'none' | 'sm' | 'md' | 'lg';
}

export function Card({ children, hover = true, padding = 'md', className, ...props }: CardProps) {
  return (
    <div
      className={cn(
        'bg-surface-container-lowest rounded-xl shadow-card border border-surface-container-highest/60',
        hover && 'hover:shadow-card-hover transition-shadow',
        {
          'p-0': padding === 'none',
          'p-space-sm': padding === 'sm',
          'p-space-md': padding === 'md',
          'p-space-lg': padding === 'lg',
        },
        className
      )}
      {...props}
    >
      {children}
    </div>
  );
}

export function CardHeader({ children, className }: { children: ReactNode; className?: string }) {
  return (
    <div className={cn('flex items-center justify-between pb-space-md border-b border-surface-container-highest/40 mb-space-md', className)}>
      {children}
    </div>
  );
}

export function CardTitle({ icon, children, badge }: { icon?: ReactNode; children: ReactNode; badge?: ReactNode }) {
  return (
    <div className="flex items-center gap-space-sm">
      {icon}
      <h2 className="font-headline text-headline-sm font-bold text-on-surface tracking-tight">{children}</h2>
      {badge}
    </div>
  );
}

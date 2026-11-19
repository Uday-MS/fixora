import type { ReactNode } from 'react';
import { cn } from '@/lib/utils';
import { Card } from './Card';

interface MetricCardProps {
  label: string;
  value: string | number;
  icon?: ReactNode;
  change?: ReactNode;
  footer?: ReactNode;
  className?: string;
  onClick?: () => void;
}

export function MetricCard({ label, value, icon, change, footer, className, onClick }: MetricCardProps) {
  return (
    <Card className={cn('flex flex-col justify-between p-space-md', className)} onClick={onClick}>
      <div className="flex items-center justify-between pb-space-xs">
        <span className="font-mono text-mono-tag text-on-surface-variant uppercase tracking-wider">
          {label}
        </span>
        {icon}
      </div>
      <div className="flex items-baseline gap-space-xs my-space-xs">
        <span className="font-mono text-headline-xl font-bold text-on-surface leading-none tracking-tight">
          {value}
        </span>
        {change}
      </div>
      {footer && (
        <div className="pt-space-xs flex items-center justify-between font-mono text-mono-tag text-on-surface-variant border-t border-surface-container-highest/30 mt-1">
          {footer}
        </div>
      )}
    </Card>
  );
}

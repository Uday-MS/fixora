import { cn } from '@/lib/utils';

interface StatusDotProps {
  status: 'healthy' | 'warning' | 'critical' | 'unknown' | 'active' | 'idle';
  pulse?: boolean;
  size?: 'sm' | 'md' | 'lg';
  className?: string;
}

export function StatusDot({ status, pulse, size = 'sm', className }: StatusDotProps) {
  return (
    <span
      className={cn(
        'rounded-full inline-block shrink-0',
        {
          'bg-success': status === 'healthy' || status === 'active',
          'bg-primary-container': status === 'warning',
          'bg-error': status === 'critical',
          'bg-secondary': status === 'unknown' || status === 'idle',
        },
        {
          'w-1.5 h-1.5': size === 'sm',
          'w-2 h-2': size === 'md',
          'w-3 h-3': size === 'lg',
        },
        pulse && 'animate-ping',
        className
      )}
    />
  );
}

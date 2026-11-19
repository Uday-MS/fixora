import { cn } from '@/lib/utils';

interface LoadingStateProps {
  message?: string;
  className?: string;
}

export function LoadingState({ message = 'Loading FIXORA Intelligence...', className }: LoadingStateProps) {
  return (
    <div className={cn('flex flex-col items-center justify-center py-16', className)}>
      <div className="w-8 h-8 border-2 border-surface-container-highest border-t-primary-container rounded-full animate-spin mb-3" />
      <p className="font-mono text-mono-tag text-on-surface-variant uppercase tracking-wider">{message}</p>
    </div>
  );
}

export function TableSkeleton({ rows = 4, cols = 5 }: { rows?: number; cols?: number }) {
  return (
    <div className="space-y-2 p-3">
      <div className="h-9 bg-surface-container-low rounded animate-pulse" />
      {Array.from({ length: rows }).map((_, i) => (
        <div key={i} className="flex gap-3 h-10">
          {Array.from({ length: cols }).map((_, j) => (
            <div key={j} className="flex-1 bg-surface-container-high rounded animate-pulse" />
          ))}
        </div>
      ))}
    </div>
  );
}

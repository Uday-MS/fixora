import type { ReactNode } from 'react';
import { Inbox } from 'lucide-react';
import { cn } from '@/lib/utils';

interface EmptyStateProps {
  icon?: ReactNode;
  title: string;
  description: string;
  action?: ReactNode;
  className?: string;
}

export function EmptyState({ icon, title, description, action, className }: EmptyStateProps) {
  return (
    <div className={cn('flex flex-col items-center justify-center py-12 px-4 text-center', className)}>
      <div className="w-12 h-12 rounded-xl bg-surface-container-high flex items-center justify-center text-on-surface-variant mb-3">
        {icon || <Inbox className="w-6 h-6" />}
      </div>
      <h3 className="font-headline text-headline-sm font-semibold text-on-surface mb-1">{title}</h3>
      <p className="font-body text-body-sm text-on-surface-variant max-w-md mb-4">{description}</p>
      {action}
    </div>
  );
}

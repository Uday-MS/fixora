import { AlertTriangle } from 'lucide-react';
import { Button } from './Button';

interface ErrorStateProps {
  title?: string;
  message: string;
  onRetry?: () => void;
}

export function ErrorState({ title = 'Backend Service Disconnected', message, onRetry }: ErrorStateProps) {
  return (
    <div className="flex flex-col items-center justify-center py-12 px-4 text-center bg-surface-container-low/50 rounded-xl border border-error-container/50">
      <div className="w-12 h-12 rounded-xl bg-error-container flex items-center justify-center text-error mb-3">
        <AlertTriangle className="w-6 h-6" />
      </div>
      <h3 className="font-headline text-headline-sm font-bold text-on-surface mb-1">{title}</h3>
      <p className="font-body text-body-sm text-on-surface-variant max-w-md mb-4">{message}</p>
      {onRetry && (
        <Button variant="secondary" size="sm" onClick={onRetry}>
          Retry Connection
        </Button>
      )}
    </div>
  );
}

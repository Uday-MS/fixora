import { cn } from '@/lib/utils';

interface DiffViewerProps {
  diff: string;
  filePath?: string;
  className?: string;
}

export function DiffViewer({ diff, filePath, className }: DiffViewerProps) {
  const lines = diff.split('\n');

  return (
    <div className={cn('bg-inverse-surface rounded-xl overflow-hidden font-mono text-mono-code text-xs text-inverse-on-surface shadow-md', className)}>
      {filePath && (
        <div className="flex items-center justify-between px-space-md py-2.5 bg-surface-container-highest/10 border-b border-surface-container-highest/20 font-mono text-mono-tag">
          <span className="text-primary-fixed">{filePath}</span>
          <span className="text-on-surface-variant">AST-LEVEL MUTATION</span>
        </div>
      )}
      <div className="overflow-x-auto p-space-md space-y-1">
        {lines.map((line, i) => {
          const isRemoved = line.startsWith('-') && !line.startsWith('---');
          const isAdded = line.startsWith('+') && !line.startsWith('+++');
          const isHeader = line.startsWith('@@');

          return (
            <div
              key={i}
              className={cn(
                'px-2 py-0.5 rounded flex items-center gap-2 font-mono',
                isRemoved && 'bg-error-container/20 text-error-container',
                isAdded && 'bg-primary-container/20 text-primary-fixed font-semibold',
                isHeader && 'text-primary-fixed-dim bg-primary-container/10 my-1 py-1 font-bold',
                !isRemoved && !isAdded && !isHeader && 'text-inverse-on-surface/70'
              )}
            >
              <span className="select-none w-8 text-right text-inverse-on-surface/40 text-[11px]">{i + 1}</span>
              <span className="whitespace-pre">{line}</span>
            </div>
          );
        })}
      </div>
    </div>
  );
}

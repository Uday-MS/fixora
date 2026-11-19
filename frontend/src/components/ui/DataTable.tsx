import { cn } from '@/lib/utils';
import type { ReactNode } from 'react';

export interface Column<T> {
  key: string;
  header: string;
  render: (item: T) => ReactNode;
  className?: string;
  headerClassName?: string;
}

interface DataTableProps<T> {
  columns: Column<T>[];
  data: T[];
  keyExtractor: (item: T) => string;
  onRowClick?: (item: T) => void;
  emptyMessage?: string;
  className?: string;
}

export function DataTable<T>({
  columns,
  data,
  keyExtractor,
  onRowClick,
  emptyMessage = 'No records found',
  className,
}: DataTableProps<T>) {
  if (data.length === 0) {
    return (
      <div className="py-10 text-center">
        <p className="font-mono text-mono-tag text-on-surface-variant uppercase tracking-wider">
          {emptyMessage}
        </p>
      </div>
    );
  }

  return (
    <div className={cn('overflow-x-auto w-full', className)}>
      <table className="w-full text-left font-body text-body-sm">
        <thead>
          <tr className="bg-surface-container-low font-mono text-mono-tag uppercase tracking-wider text-on-surface-variant">
            {columns.map((col) => (
              <th
                key={col.key}
                className={cn('py-2.5 px-3 first:rounded-l last:rounded-r font-semibold', col.headerClassName)}
              >
                {col.header}
              </th>
            ))}
          </tr>
        </thead>
        <tbody className="divide-y divide-surface-container-highest/40">
          {data.map((item) => (
            <tr
              key={keyExtractor(item)}
              className={cn(
                'hover:bg-surface-container-low/70 transition-colors',
                onRowClick && 'cursor-pointer'
              )}
              onClick={() => onRowClick?.(item)}
            >
              {columns.map((col) => (
                <td key={col.key} className={cn('py-3 px-3', col.className)}>
                  {col.render(item)}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

import { useState, useEffect } from 'react';
import { FileText, Search, RefreshCw, Terminal, AlertCircle, ChevronDown, ChevronRight } from 'lucide-react';
import { AppLayout } from '@/components/layout/AppLayout';
import { Card } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { LoadingState } from '@/components/ui/LoadingState';
import { EmptyState } from '@/components/ui/EmptyState';
import { telemetryService, type TelemetryLog } from '@/services/telemetry';

export function LogsPage() {
  const [logs, setLogs] = useState<TelemetryLog[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [query, setQuery] = useState('');
  const [selectedLevel, setSelectedLevel] = useState('ALL');
  const [expandedId, setExpandedId] = useState<string | null>(null);

  const fetchLogs = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const data = await telemetryService.getLogs('proj_demo_001');
      setLogs(data || []);
    } catch (err: any) {
      console.error('Failed to fetch logs:', err);
      setError(err.message || 'Failed to fetch telemetry logs');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchLogs();
  }, []);

  const filtered = logs.filter((log) => {
    const matchesQuery =
      !query ||
      (log.message || '').toLowerCase().includes(query.toLowerCase()) ||
      (log.serviceName || '').toLowerCase().includes(query.toLowerCase());
    const matchesLevel = selectedLevel === 'ALL' || log.level.toUpperCase() === selectedLevel;
    return matchesQuery && matchesLevel;
  });

  return (
    <AppLayout breadcrumbs={[{ label: 'Observability' }, { label: 'Logs' }]}>
      <div className="flex flex-col gap-space-md">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-space-sm pb-space-sm border-b border-surface-container-highest">
          <div>
            <h1 className="font-headline text-headline-lg font-bold text-on-surface">Application Logs (Grafana Loki)</h1>
            <p className="font-body text-body-sm text-on-surface-variant">Live streaming correlated logs ingested via OpenTelemetry.</p>
          </div>
          <Button variant="secondary" size="md" onClick={fetchLogs} disabled={isLoading}>
            <RefreshCw className={`w-4 h-4 mr-1 text-on-surface-variant ${isLoading ? 'animate-spin' : ''}`} />
            Refresh Logs
          </Button>
        </div>

        <div className="flex flex-wrap items-center gap-space-sm">
          <div className="relative flex-1 min-w-[240px]">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-on-surface-variant w-4 h-4" />
            <input
              type="text"
              placeholder="Search log messages, service name..."
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              className="fixora-input pl-9 font-mono text-xs"
            />
          </div>
          <select
            value={selectedLevel}
            onChange={(e) => setSelectedLevel(e.target.value)}
            className="h-10 px-3 rounded-lg bg-surface-container-low text-on-surface font-mono text-xs border border-surface-container-highest"
          >
            <option value="ALL">ALL LEVELS</option>
            <option value="ERROR">ERROR</option>
            <option value="WARN">WARN</option>
            <option value="INFO">INFO</option>
          </select>
        </div>

        {isLoading ? (
          <LoadingState message="Streaming correlated logs from telemetry engine..." />
        ) : error ? (
          <div className="p-space-lg bg-error-container/20 border border-error/30 rounded-xl text-center">
            <p className="font-bold text-on-surface">{error}</p>
            <Button variant="secondary" size="sm" className="mt-4" onClick={fetchLogs}>
              Retry
            </Button>
          </div>
        ) : filtered.length === 0 ? (
          <EmptyState
            title="No telemetry logs found"
            description="Ingest logs via the Telemetry API or GitHub webhooks to populate Loki stream."
          />
        ) : (
          <div className="bg-inverse-surface rounded-xl p-space-md font-mono text-xs text-inverse-on-surface shadow-md overflow-x-auto space-y-2">
            {filtered.map((log) => (
              <div
                key={log.id}
                className="hover:bg-surface-container-high/10 p-2 rounded cursor-pointer transition-colors"
                onClick={() => setExpandedId(expandedId === log.id ? null : log.id)}
              >
                <div className="flex items-start gap-2">
                  <span className="text-inverse-on-surface/50 text-[11px] shrink-0">
                    {new Date(log.timestamp).toLocaleTimeString()}
                  </span>
                  <span
                    className={
                      log.level.toUpperCase() === 'ERROR'
                        ? 'text-error font-bold'
                        : log.level.toUpperCase() === 'WARN'
                        ? 'text-primary-container font-bold'
                        : 'text-primary-fixed'
                    }
                  >
                    [{log.level.toUpperCase()}]
                  </span>
                  <span className="text-primary-fixed-dim">[{log.serviceName}]</span>
                  <span className="text-inverse-on-surface/90 flex-1">{log.message}</span>
                  {log.stackTrace && (
                    <span className="text-[10px] text-primary underline shrink-0">
                      {expandedId === log.id ? 'Hide Trace' : 'View Trace'}
                    </span>
                  )}
                </div>
                {expandedId === log.id && log.stackTrace && (
                  <div className="mt-2 p-3 bg-black/40 rounded border border-inverse-on-surface/20 text-[11px] text-error-container whitespace-pre-wrap overflow-x-auto">
                    {log.stackTrace}
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </AppLayout>
  );
}

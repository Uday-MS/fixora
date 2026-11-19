import { useState, useEffect } from 'react';
import { Activity, TrendingDown, RefreshCw, AlertTriangle } from 'lucide-react';
import { AppLayout } from '@/components/layout/AppLayout';
import { Card, CardHeader, CardTitle } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';
import { LoadingState } from '@/components/ui/LoadingState';
import { telemetryService, type TelemetryMetric } from '@/services/telemetry';

export function MetricsPage() {
  const [metrics, setMetrics] = useState<TelemetryMetric[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  const fetchMetrics = async () => {
    setIsLoading(true);
    try {
      const data = await telemetryService.getMetrics('proj_demo_001');
      setMetrics(data || []);
    } catch (err) {
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchMetrics();
  }, []);

  return (
    <AppLayout breadcrumbs={[{ label: 'Observability' }, { label: 'Metrics' }]}>
      <div className="flex flex-col gap-space-md">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-space-sm pb-space-sm border-b border-surface-container-highest">
          <div>
            <h1 className="font-headline text-headline-lg font-bold text-on-surface">Prometheus Telemetry Metrics</h1>
            <p className="font-body text-body-sm text-on-surface-variant">Real-time p95/p99 latency, HTTP error budgets, and pool saturations.</p>
          </div>
          <Button variant="secondary" size="md" onClick={fetchMetrics} disabled={isLoading}>
            <RefreshCw className={`w-4 h-4 mr-1 ${isLoading ? 'animate-spin' : ''}`} />
            Refresh
          </Button>
        </div>

        {isLoading ? (
          <LoadingState message="Fetching time-series metrics from Prometheus pipeline..." />
        ) : metrics.length === 0 ? (
          <div className="p-space-lg bg-surface-container-lowest border border-surface-container-highest rounded-xl text-center space-y-2">
            <Activity className="w-8 h-8 text-on-surface-variant mx-auto mb-2" />
            <h3 className="font-headline text-headline-sm font-bold text-on-surface">No Telemetry Metrics Ingested</h3>
            <p className="font-body text-body-sm text-on-surface-variant max-w-md mx-auto">
              Configure Prometheus push gateways or OpenTelemetry metric exporters pointing to <code className="font-mono text-xs bg-surface-container-high px-1.5 py-0.5 rounded">/api/telemetry/:projectId/metrics</code> to record real-time latency, error budgets, and saturation indices.
            </p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-space-md">
            {metrics.map((m) => (
              <Card key={m.id} className="p-space-md">
                <div className="flex items-center justify-between mb-1">
                  <span className="font-mono text-mono-tag uppercase text-on-surface-variant">{m.serviceName}</span>
                  {m.isAnomaly && <Badge variant="critical">ANOMALY DETECTED</Badge>}
                </div>
                <h4 className="font-headline text-label-md font-bold text-on-surface truncate">{m.metricName}</h4>
                <div className="text-headline-xl font-bold font-mono text-primary mt-2">
                  {m.value} <span className="text-sm font-normal text-on-surface-variant">{m.unit}</span>
                </div>
                <div className="text-[11px] font-mono text-on-surface-variant mt-2 pt-2 border-t border-surface-container-highest/30">
                  Recorded: {new Date(m.timestamp).toLocaleTimeString()}
                </div>
              </Card>
            ))}
          </div>
        )}
      </div>
    </AppLayout>
  );
}

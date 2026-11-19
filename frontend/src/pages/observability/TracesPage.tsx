import { useState, useEffect } from 'react';
import { Layers, RefreshCw, AlertCircle } from 'lucide-react';
import { AppLayout } from '@/components/layout/AppLayout';
import { Card } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';
import { LoadingState } from '@/components/ui/LoadingState';
import { telemetryService, type TelemetryTrace } from '@/services/telemetry';

export function TracesPage() {
  const [traces, setTraces] = useState<TelemetryTrace[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  const fetchTraces = async () => {
    setIsLoading(true);
    try {
      const data = await telemetryService.getTraces('proj_demo_001');
      setTraces(data || []);
    } catch (err) {
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchTraces();
  }, []);

  return (
    <AppLayout breadcrumbs={[{ label: 'Observability' }, { label: 'Distributed Traces' }]}>
      <div className="flex flex-col gap-space-md">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-space-sm pb-space-sm border-b border-surface-container-highest">
          <div>
            <h1 className="font-headline text-headline-lg font-bold text-on-surface">Distributed Traces (Grafana Tempo)</h1>
            <p className="font-body text-body-sm text-on-surface-variant">Trace request journeys across microservices and database drivers.</p>
          </div>
          <Button variant="secondary" size="md" onClick={fetchTraces} disabled={isLoading}>
            <RefreshCw className={`w-4 h-4 mr-1 ${isLoading ? 'animate-spin' : ''}`} />
            Refresh
          </Button>
        </div>

        {isLoading ? (
          <LoadingState message="Fetching OpenTelemetry distributed spans..." />
        ) : traces.length === 0 ? (
          <div className="p-space-lg bg-surface-container-lowest border border-surface-container-highest rounded-xl text-center space-y-2">
            <Layers className="w-8 h-8 text-on-surface-variant mx-auto mb-2" />
            <h3 className="font-headline text-headline-sm font-bold text-on-surface">No Distributed Traces Ingested</h3>
            <p className="font-body text-body-sm text-on-surface-variant max-w-md mx-auto">
              Configure OpenTelemetry tracing SDKs or Tempo exporters pointing to <code className="font-mono text-xs bg-surface-container-high px-1.5 py-0.5 rounded">/api/telemetry/:projectId/traces</code> to inspect span waterfalls and cross-service call latencies.
            </p>
          </div>
        ) : (
          <div className="space-y-space-md font-mono text-xs">
            {traces.map((tr) => (
              <Card key={tr.id} className="p-space-md">
                <div className="flex items-center justify-between mb-2">
                  <div className="font-bold text-on-surface">
                    Trace ID: <span className="text-primary">{tr.traceId}</span> ({tr.operationName})
                  </div>
                  <Badge variant={tr.statusCode === 'ERROR' ? 'critical' : 'success'}>
                    {tr.statusCode}
                  </Badge>
                </div>
                <div className="p-2.5 bg-surface-container-low rounded flex items-center justify-between">
                  <div>
                    <span className="font-bold text-on-surface">{tr.serviceName}</span>: {tr.operationName}
                    {tr.errorMessage && (
                      <span className="text-error ml-2 font-normal">({tr.errorMessage})</span>
                    )}
                  </div>
                  <div className="font-semibold text-on-surface">
                    {tr.durationMs}ms
                  </div>
                </div>
              </Card>
            ))}
          </div>
        )}
      </div>
    </AppLayout>
  );
}

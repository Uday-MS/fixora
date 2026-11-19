import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { AlertOctagon, ArrowRight, ShieldAlert, RefreshCw, CheckCircle2 } from 'lucide-react';
import { AppLayout } from '@/components/layout/AppLayout';
import { Card } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';
import { LoadingState } from '@/components/ui/LoadingState';
import { EmptyState } from '@/components/ui/EmptyState';
import { incidentService } from '@/services/incidents';
import { investigationService } from '@/services/investigations';
import type { Incident } from '@/types';

export function IncidentsPage() {
  const navigate = useNavigate();
  const [incidents, setIncidents] = useState<Incident[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [resolvingId, setResolvingId] = useState<string | null>(null);
  const [investigatingId, setInvestigatingId] = useState<string | null>(null);

  const fetchIncidents = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const res = await incidentService.list();
      setIncidents(res?.data || []);
    } catch (err: any) {
      console.error('Failed to fetch incidents:', err);
      setError(err.message || 'Failed to load incidents');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchIncidents();
  }, []);

  const handleResolve = async (e: React.MouseEvent, id: string) => {
    e.stopPropagation();
    setResolvingId(id);
    try {
      await incidentService.resolve(id);
      await fetchIncidents();
    } catch (err) {
      console.error(err);
    } finally {
      setResolvingId(null);
    }
  };

  const handleInvestigateIncident = async (e: React.MouseEvent, inc: Incident) => {
    e.stopPropagation();
    setInvestigatingId(inc.id);
    try {
      const res = await investigationService.create({
        question: `Investigate root cause and remediation for ${inc.title}: ${inc.errorMessage || inc.description}`,
        projectId: inc.projectId || 'proj_demo_001',
        incidentId: inc.id,
      });
      if (res?.data?.id) {
        navigate(`/investigations/${res.data.id}`);
      } else {
        navigate('/investigations');
      }
    } catch (err: any) {
      alert(`Failed to launch investigation: ${err.message}`);
    } finally {
      setInvestigatingId(null);
    }
  };

  return (
    <AppLayout breadcrumbs={[{ label: 'Engineering' }, { label: 'Incidents' }]}>
      <div className="flex flex-col gap-space-md">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-space-sm pb-space-sm border-b border-surface-container-highest">
          <div>
            <h1 className="font-headline text-headline-lg font-bold text-on-surface">Incident Intelligence</h1>
            <p className="font-body text-body-sm text-on-surface-variant">
              Active production incidents correlated with git commits and automated patch generation.
            </p>
          </div>
          <Button variant="secondary" size="md" onClick={fetchIncidents} disabled={isLoading}>
            <RefreshCw className={`w-4 h-4 mr-1 text-on-surface-variant ${isLoading ? 'animate-spin' : ''}`} />
            Refresh
          </Button>
        </div>

        {isLoading ? (
          <LoadingState message="Loading incidents from database..." />
        ) : error ? (
          <div className="p-space-lg bg-error-container/20 border border-error/30 rounded-xl text-center">
            <p className="font-bold text-on-surface">{error}</p>
            <Button variant="secondary" size="sm" className="mt-4" onClick={fetchIncidents}>
              Retry
            </Button>
          </div>
        ) : incidents.length === 0 ? (
          <EmptyState
            title="No incidents detected"
            description="All services are operating normally with zero active outages or threshold alerts."
          />
        ) : (
          <div className="space-y-space-md">
            {incidents.map((inc) => (
              <Card
                key={inc.id}
                className="p-space-md hover:border-primary-container transition-all cursor-pointer"
                onClick={() => navigate('/investigations')}
              >
                <div className="flex flex-col md:flex-row md:items-center justify-between gap-space-sm">
                  <div>
                    <div className="flex items-center gap-2 mb-1 flex-wrap">
                      <span className="font-mono text-mono-tag font-bold text-primary">{inc.id}</span>
                      <span className="font-mono text-xs text-on-surface-variant">{inc.affectedService}</span>
                      <Badge variant={inc.severity === 'sev1' ? 'critical' : inc.severity === 'sev2' ? 'warning' : 'default'}>
                        {inc.severity.toUpperCase()}
                      </Badge>
                      <Badge variant={inc.status === 'active' ? 'critical' : 'success'} dot>
                        {inc.status.toUpperCase()}
                      </Badge>
                    </div>
                    <h3 className="font-headline text-headline-sm font-bold text-on-surface">{inc.title}</h3>
                    <p className="font-body text-xs text-on-surface-variant mt-1">{inc.description}</p>
                    {inc.errorMessage && (
                      <div className="font-mono text-[11px] text-error mt-1 bg-error-container/10 p-1.5 rounded">
                        {inc.errorMessage}
                      </div>
                    )}
                  </div>
                  <div className="flex items-center gap-space-sm self-end md:self-center shrink-0">
                    {inc.status === 'active' && (
                      <Button
                        size="sm"
                        variant="ghost"
                        disabled={resolvingId === inc.id}
                        onClick={(e) => handleResolve(e, inc.id)}
                      >
                        <CheckCircle2 className="w-3.5 h-3.5 mr-1 text-success" />
                        Resolve
                      </Button>
                    )}
                    <Button
                      size="sm"
                      disabled={investigatingId === inc.id}
                      onClick={(e) => handleInvestigateIncident(e, inc)}
                    >
                      {investigatingId === inc.id ? 'Starting Agents...' : 'Investigate →'}
                    </Button>
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

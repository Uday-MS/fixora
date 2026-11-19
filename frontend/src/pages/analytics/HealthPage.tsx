import { useState, useEffect } from 'react';
import { HeartPulse, CheckCircle2, TrendingUp, RefreshCw, ShieldCheck, AlertCircle } from 'lucide-react';
import { AppLayout } from '@/components/layout/AppLayout';
import { Card } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { LoadingState } from '@/components/ui/LoadingState';
import api from '@/services/api';

interface HealthMetrics {
  totalRepositories: number;
  totalFixes: number;
  sandboxPassRate: number;
  averageMttrMins: number;
  unresolvedBugs: number;
  zeroContaminationRate: number;
  hasSufficientData: boolean;
}

export function HealthPage() {
  const [metrics, setMetrics] = useState<HealthMetrics | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  const fetchHealth = async () => {
    setIsLoading(true);
    try {
      const res = await api.get<{ data: HealthMetrics }>('/dashboard/health');
      if (res?.data) {
        setMetrics(res.data);
      }
    } catch (err) {
      console.error('Failed to load health metrics:', err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchHealth();
  }, []);

  return (
    <AppLayout breadcrumbs={[{ label: 'Analytics' }, { label: 'Engineering Health' }]}>
      <div className="flex flex-col gap-space-md">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-space-sm pb-space-sm border-b border-surface-container-highest">
          <div>
            <h1 className="font-headline text-headline-lg font-bold text-on-surface">Engineering Health & Reliability</h1>
            <p className="font-body text-body-sm text-on-surface-variant">System metrics across code health, MTTR reduction, and test pass ratios.</p>
          </div>
          <Button variant="secondary" size="md" onClick={fetchHealth} disabled={isLoading}>
            <RefreshCw className={`w-4 h-4 mr-1 text-on-surface-variant ${isLoading ? 'animate-spin' : ''}`} />
            Refresh
          </Button>
        </div>

        {isLoading ? (
          <LoadingState message="Calculating engineering reliability metrics from database..." />
        ) : !metrics || !metrics.hasSufficientData ? (
          <div className="p-space-lg bg-surface-container-lowest border border-surface-container-highest rounded-xl text-center space-y-2">
            <AlertCircle className="w-8 h-8 text-on-surface-variant mx-auto mb-2" />
            <h3 className="font-headline text-headline-sm font-bold text-on-surface">Insufficient Signal Data</h3>
            <p className="font-body text-body-sm text-on-surface-variant max-w-md mx-auto">
              Connect monitored codebases and execute sandbox validations to generate empirical engineering health indices.
            </p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-space-md font-mono">
            <Card className="p-space-md">
              <div className="text-on-surface-variant text-mono-tag">TOTAL AUTONOMOUS FIXES</div>
              <div className="text-headline-xl font-bold text-on-surface mt-1">{metrics.totalFixes}</div>
              <div className="text-xs text-success font-semibold mt-1">
                {metrics.sandboxPassRate}% Docker Sandbox Pass Rate
              </div>
            </Card>
            <Card className="p-space-md">
              <div className="text-on-surface-variant text-mono-tag">AVERAGE MTTR</div>
              <div className="text-headline-xl font-bold text-primary mt-1">
                {metrics.averageMttrMins > 0 ? `${metrics.averageMttrMins} mins` : '< 15 mins'}
              </div>
              <div className="text-xs text-on-surface-variant mt-1">Based on resolved production incidents</div>
            </Card>
            <Card className="p-space-md">
              <div className="text-on-surface-variant text-mono-tag">ZERO CONTAMINATION MERGES</div>
              <div className="text-headline-xl font-bold text-success mt-1">{metrics.zeroContaminationRate}%</div>
              <div className="text-xs text-on-surface-variant mt-1">All changes gate-verified by human review</div>
            </Card>
          </div>
        )}
      </div>
    </AppLayout>
  );
}

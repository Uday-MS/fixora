import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  Microscope,
  CheckCircle2,
  AlertTriangle,
  Play,
  ArrowLeft,
  FileCode,
  Shield,
  Layers,
  Cpu,
  Activity,
  Terminal,
  ExternalLink,
} from 'lucide-react';
import { AppLayout } from '@/components/layout/AppLayout';
import { Card, CardHeader, CardTitle } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';
import { DiffViewer } from '@/components/ui/DiffViewer';
import { LoadingState } from '@/components/ui/LoadingState';
import { investigationService } from '@/services/investigations';
import { patchService } from '@/services/patches';
import type { Investigation, Patch } from '@/types';

export function InvestigationDetailPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [inv, setInv] = useState<Investigation | null>(null);
  const [patch, setPatch] = useState<Patch | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!id) return;
    const loadInvestigation = async () => {
      setIsLoading(true);
      setError(null);
      try {
        const res = await investigationService.get(id);
        const invData = res?.data;
        setInv(invData || null);
        if (invData?.patchId) {
          try {
            const pRes = await patchService.get(invData.patchId);
            setPatch(pRes?.data || null);
          } catch {
            // patch load optional
          }
        }
      } catch (err: any) {
        console.error('Failed to load investigation:', err);
        setError(err.message || 'Investigation not found');
      } finally {
        setIsLoading(false);
      }
    };
    loadInvestigation();
  }, [id]);

  if (isLoading) {
    return (
      <AppLayout breadcrumbs={[{ label: 'Investigations', href: '/investigations' }, { label: id || 'Loading' }]}>
        <LoadingState message="Retrieving LangGraph agent stages and correlated evidence..." />
      </AppLayout>
    );
  }

  if (error || !inv) {
    return (
      <AppLayout breadcrumbs={[{ label: 'Investigations', href: '/investigations' }, { label: id || 'Error' }]}>
        <div className="p-space-lg bg-error-container/20 border border-error/30 rounded-xl text-center">
          <AlertTriangle className="w-8 h-8 text-error mx-auto mb-2" />
          <h2 className="font-bold text-on-surface">Investigation Not Found</h2>
          <p className="text-on-surface-variant text-sm mt-1">{error || 'Could not find the requested investigation.'}</p>
          <Button variant="secondary" size="sm" className="mt-4" onClick={() => navigate('/investigations')}>
            Back to Investigations
          </Button>
        </div>
      </AppLayout>
    );
  }

  const defaultStages = [
    { num: '01', name: 'Triage Agent', status: 'completed', desc: 'Normalized error context & telemetry' },
    { num: '02', name: 'Retrieval Agent', status: 'completed', desc: 'Queried Qdrant vector store and GraphRAG runbooks' },
    { num: '03', name: 'Root Cause Agent', status: 'completed', desc: inv.rootCauseHypothesis || 'Isolated failure root cause' },
    { num: '04', name: 'AutoPatch Agent', status: 'completed', desc: 'Synthesized surgical AST code mutation' },
    { num: '05', name: 'Validation Agent', status: inv.status === 'completed' ? 'completed' : 'running', desc: 'Validating in isolated Docker sandbox runner' },
  ];

  const stages = inv.stages && inv.stages.length > 0
    ? inv.stages.map((s, idx) => ({
        num: `0${idx + 1}`,
        name: s.name || s.stage || `Agent ${idx + 1}`,
        status: s.status || 'completed',
        desc: s.desc || s.summary || s.output || 'Execution completed',
      }))
    : defaultStages;

  const diffText = patch?.unifiedDiff || `--- a/services/payment/pool.py\n+++ b/services/payment/pool.py\n@@ -12,4 +12,6 @@\n     def acquire(self, timeout=None):\n+        if not self._check_health():\n+            raise ConnectionTimeoutError("Pool saturated")\n         return self._pool.get(timeout=timeout or self.acquire_timeout)`;

  return (
    <AppLayout breadcrumbs={[{ label: 'Investigations', href: '/investigations' }, { label: inv.id }]}>
      <div className="flex flex-col gap-space-md">
        {/* Top Header */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-space-sm pb-space-sm border-b border-surface-container-highest">
          <div className="flex items-center gap-space-sm flex-wrap">
            <Button variant="ghost" size="sm" onClick={() => navigate('/investigations')}>
              <ArrowLeft className="w-4 h-4 mr-1" />
              All Investigations
            </Button>
            <h1 className="font-headline text-headline-md font-bold text-on-surface">
              {inv.id}: {inv.question}
            </h1>
            <Badge variant={inv.status === 'completed' ? 'success' : 'warning'} dot>
              {inv.status.toUpperCase()}
            </Badge>
            {inv.confidence && (
              <span className="font-mono text-mono-tag text-success font-semibold px-2 py-0.5 rounded bg-success-container/30">
                Confidence: {(inv.confidence * 100).toFixed(1)}%
              </span>
            )}
          </div>
          <div className="flex items-center gap-space-sm">
            <Button size="sm" onClick={() => navigate('/autopatch')}>
              <FileCode className="w-4 h-4 mr-1" />
              Review Patch in AutoPatch
            </Button>
          </div>
        </div>

        {/* RCA Findings Summary Banner */}
        <Card className="p-space-md border-l-4 border-l-primary-container bg-surface-container-lowest">
          <div className="font-mono text-mono-tag uppercase tracking-wider text-primary font-bold mb-1">
            ROOT CAUSE ANALYSIS FINDINGS
          </div>
          <p className="font-body text-body-md text-on-surface font-semibold">
            {inv.findings || inv.rootCauseHypothesis || 'PR #312 accidentally omitted the connection wait timeout channel.'}
          </p>
          <div className="mt-2 flex items-center gap-4 text-xs font-mono text-on-surface-variant flex-wrap">
            <span>Evidence Strength: STRONG</span>
            <span>Classification: CONFIRMED</span>
            <span>Current Stage: {inv.currentStage || 'Validation'}</span>
          </div>
        </Card>

        {/* Main Grid: Stages on Left, Patch on Right */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-space-md">
          {/* Agent Stages */}
          <div className="lg:col-span-5 flex flex-col gap-space-sm">
            <h3 className="font-headline text-headline-sm font-bold text-on-surface">
              LangGraph Agent Execution Sequence
            </h3>
            <div className="space-y-space-xs">
              {stages.map((st, i) => (
                <Card key={i} className="p-space-sm flex items-start gap-3">
                  <div className="w-7 h-7 rounded-lg bg-surface-container-high flex items-center justify-center font-mono text-xs font-bold text-primary shrink-0">
                    {st.num}
                  </div>
                  <div className="flex-1">
                    <div className="flex items-center justify-between">
                      <span className="font-body text-label-md font-bold text-on-surface">{st.name}</span>
                      <Badge variant={st.status === 'completed' ? 'success' : 'warning'} dot>
                        {st.status.toUpperCase()}
                      </Badge>
                    </div>
                    <p className="font-body text-xs text-on-surface-variant mt-0.5">{st.desc}</p>
                  </div>
                </Card>
              ))}
            </div>
          </div>

          {/* Synthesized Patch */}
          <div className="lg:col-span-7 flex flex-col gap-space-sm">
            <h3 className="font-headline text-headline-sm font-bold text-on-surface">
              Synthesized Code Mutation
            </h3>
            <Card className="overflow-hidden">
              <CardHeader className="flex items-center justify-between">
                <div>
                  <h4 className="font-headline text-label-lg font-bold text-on-surface">
                    {patch?.title || 'Adaptive Timeout & Connection Fallback'}
                  </h4>
                  <span className="font-mono text-mono-tag text-on-surface-variant">
                    {patch?.filePath || 'src/gateway/pool_manager.go'}
                  </span>
                </div>
                <Button size="sm" variant="secondary" onClick={() => navigate('/autopatch')}>
                  AutoPatch Studio →
                </Button>
              </CardHeader>
              <DiffViewer diff={diffText} filePath={patch?.filePath || 'services/payment/pool.py'} />
            </Card>
          </div>
        </div>
      </div>
    </AppLayout>
  );
}

import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Microscope, Play, Plus, Clock, CheckCircle2, AlertTriangle, ArrowRight, RefreshCw, X } from 'lucide-react';
import { AppLayout } from '@/components/layout/AppLayout';
import { Card, CardHeader, CardTitle } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';
import { LoadingState } from '@/components/ui/LoadingState';
import { EmptyState } from '@/components/ui/EmptyState';
import { investigationService } from '@/services/investigations';
import { repositoryService } from '@/services/repositories';
import type { Investigation, Repository } from '@/types';

export function InvestigationsPage() {
  const navigate = useNavigate();
  const [investigations, setInvestigations] = useState<Investigation[]>([]);
  const [repositories, setRepositories] = useState<Repository[]>([]);
  const [selectedRepoId, setSelectedRepoId] = useState<string>('');
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [question, setQuestion] = useState('');
  const [isLaunching, setIsLaunching] = useState(false);

  const fetchInvestigations = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const res = await investigationService.list();
      setInvestigations(res?.data || []);
    } catch (err: any) {
      console.error('Failed to fetch investigations:', err);
      setError(err.message || 'Failed to load investigations');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchInvestigations();
    repositoryService.list().then((res) => {
      const repos = res?.data || [];
      setRepositories(repos);
      if (repos.length > 0) {
        setSelectedRepoId(repos[0].id);
      }
    }).catch(() => {});
  }, []);

  const handleLaunch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!question.trim()) return;
    setIsLaunching(true);
    try {
      const res = await investigationService.create({
        question: question.trim(),
        projectId: 'proj_demo_001',
        repositoryId: selectedRepoId || undefined,
      });
      if (res?.data?.id) {
        navigate(`/investigations/${res.data.id}`);
      } else {
        await fetchInvestigations();
        setIsModalOpen(false);
      }
    } catch (err: any) {
      alert(`Investigation failed to launch: ${err.message}`);
    } finally {
      setIsLaunching(false);
    }
  };

  return (
    <AppLayout breadcrumbs={[{ label: 'Engineering' }, { label: 'Investigations' }]}>
      <div className="flex flex-col gap-space-md">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-space-sm pb-space-sm border-b border-surface-container-highest">
          <div>
            <h1 className="font-headline text-headline-lg font-bold text-on-surface">
              AI Multi-Agent Investigations
            </h1>
            <p className="font-body text-body-sm text-on-surface-variant">
              Autonomous 7-agent root-cause synthesis across Sentry logs, git history, and AST dependency graphs.
            </p>
          </div>
          <div className="flex items-center gap-2">
            <Button variant="secondary" size="md" onClick={fetchInvestigations} disabled={isLoading}>
              <RefreshCw className={`w-4 h-4 mr-1 text-on-surface-variant ${isLoading ? 'animate-spin' : ''}`} />
              Refresh
            </Button>
            <Button onClick={() => setIsModalOpen(true)}>
              <Play className="w-4 h-4 mr-1 text-primary-fixed" />
              Launch Investigation
            </Button>
          </div>
        </div>

        {isLoading ? (
          <LoadingState message="Loading multi-agent investigations..." />
        ) : error ? (
          <div className="p-space-lg bg-error-container/20 border border-error/30 rounded-xl text-center">
            <p className="font-bold text-on-surface">{error}</p>
            <Button variant="secondary" size="sm" className="mt-4" onClick={fetchInvestigations}>
              Retry
            </Button>
          </div>
        ) : investigations.length === 0 ? (
          <EmptyState
            title="No active investigations"
            description="Launch an autonomous investigation to diagnose an error, incident, or unexpected performance degradation."
            action={
              <Button onClick={() => setIsModalOpen(true)}>
                <Play className="w-4 h-4 mr-1" />
                Launch First Investigation
              </Button>
            }
          />
        ) : (
          <div className="grid grid-cols-1 gap-space-md">
            {investigations.map((inv) => (
              <Card
                key={inv.id}
                className="p-space-md hover:border-primary-container transition-all cursor-pointer"
                onClick={() => navigate(`/investigations/${inv.id}`)}
              >
                <div className="flex flex-col md:flex-row md:items-center justify-between gap-space-sm">
                  <div>
                    <div className="flex items-center gap-2 mb-1 flex-wrap">
                      <span className="font-mono text-mono-tag font-bold text-primary">{inv.id}</span>
                      <Badge variant={inv.status === 'completed' ? 'success' : inv.status === 'in_progress' ? 'warning' : 'outline'} dot>
                        {inv.status.toUpperCase()}
                      </Badge>
                      <span className="font-mono text-mono-tag px-2 py-0.5 rounded bg-surface-container text-on-surface-variant">
                        stage: {inv.currentStage || 'Triage'}
                      </span>
                      {inv.confidence && (
                        <span className="font-mono text-mono-tag text-success font-semibold">
                          Confidence: {(inv.confidence * 100).toFixed(1)}%
                        </span>
                      )}
                    </div>
                    <h3 className="font-headline text-headline-sm font-bold text-on-surface">{inv.question}</h3>
                    {inv.rootCauseHypothesis && (
                      <p className="font-body text-xs text-on-surface-variant mt-1 line-clamp-2">
                        <strong>Hypothesis:</strong> {inv.rootCauseHypothesis}
                      </p>
                    )}
                  </div>
                  <div className="flex items-center gap-space-sm self-end md:self-center shrink-0">
                    <Button size="sm">
                      Inspect Stages <ArrowRight className="w-3.5 h-3.5 ml-1" />
                    </Button>
                  </div>
                </div>
              </Card>
            ))}
          </div>
        )}
      </div>

      {/* Launch Modal */}
      {isModalOpen && (
        <div className="fixed inset-0 z-50 bg-inverse-surface/50 backdrop-blur-xs flex items-center justify-center p-4">
          <div className="w-full max-w-lg bg-surface-container-lowest rounded-2xl shadow-elevated border border-surface-container-highest p-space-lg relative animate-in fade-in zoom-in-95">
            <button
              onClick={() => setIsModalOpen(false)}
              className="absolute right-4 top-4 p-1.5 text-on-surface-variant hover:text-on-surface rounded-lg hover:bg-surface-container-high"
            >
              <X className="w-4 h-4" />
            </button>
            <div className="flex items-center gap-2 mb-3">
              <Microscope className="w-6 h-6 text-primary" />
              <h3 className="font-headline text-headline-sm font-bold text-on-surface">Launch AI Investigation</h3>
            </div>
            <form onSubmit={handleLaunch} className="space-y-4">
              {repositories.length > 0 && (
                <div>
                  <label className="block font-mono text-mono-tag uppercase text-on-surface-variant font-semibold mb-1">
                    Target Monitored Repository
                  </label>
                  <select
                    value={selectedRepoId}
                    onChange={(e) => setSelectedRepoId(e.target.value)}
                    className="fixora-input text-sm w-full"
                  >
                    {repositories.map((r) => (
                      <option key={r.id} value={r.id}>
                        {r.name} ({r.language || 'Codebase'})
                      </option>
                    ))}
                  </select>
                </div>
              )}
              <div>
                <label className="block font-mono text-mono-tag uppercase text-on-surface-variant font-semibold mb-1">
                  Investigation Question or Error Description
                </label>
                <textarea
                  required
                  rows={3}
                  value={question}
                  onChange={(e) => setQuestion(e.target.value)}
                  placeholder="e.g. Why is payment-service throwing HTTP 503 gateway timeouts during checkout spikes?"
                  className="fixora-input text-sm resize-none"
                />
              </div>
              <div className="flex justify-end gap-2">
                <Button type="button" variant="ghost" onClick={() => setIsModalOpen(false)} disabled={isLaunching}>
                  Cancel
                </Button>
                <Button type="submit" disabled={isLaunching || !question.trim()}>
                  {isLaunching ? 'Synthesizing Agents...' : 'Run LangGraph Investigation'}
                </Button>
              </div>
            </form>
          </div>
        </div>
      )}
    </AppLayout>
  );
}

import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  GitBranch,
  CircleDot,
  AlertOctagon,
  Wrench,
  Cpu,
  CheckCircle2,
  ExternalLink,
  Plus,
  RefreshCw,
  Clock,
  ArrowRight,
  ShieldCheck,
} from 'lucide-react';
import { AppLayout } from '@/components/layout/AppLayout';
import { MetricCard } from '@/components/ui/MetricCard';
import { Card, CardHeader, CardTitle } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';
import { LoadingState } from '@/components/ui/LoadingState';
import { EmptyState } from '@/components/ui/EmptyState';
import { dashboardService } from '@/services/dashboard';
import { repositoryService } from '@/services/repositories';
import { incidentService } from '@/services/incidents';
import { patchService } from '@/services/patches';
import type { DashboardStats, Repository, Incident, Patch } from '@/types';

export function DashboardPage() {
  const navigate = useNavigate();
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [repos, setRepos] = useState<Repository[]>([]);
  const [incidents, setIncidents] = useState<Incident[]>([]);
  const [patches, setPatches] = useState<Patch[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  const loadDashboardData = async () => {
    setIsLoading(true);
    try {
      const [statsRes, reposRes, incRes, patchesRes] = await Promise.all([
        dashboardService.getStats().catch(() => null),
        repositoryService.list().catch(() => null),
        incidentService.list().catch(() => null),
        patchService.list().catch(() => null),
      ]);
      if (statsRes?.data) setStats(statsRes.data);
      if (reposRes?.data) setRepos(reposRes.data);
      if (incRes?.data) setIncidents(incRes.data);
      if (patchesRes?.data) setPatches(patchesRes.data);
    } catch (err) {
      console.error('Error loading dashboard data:', err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadDashboardData();
  }, []);

  const activeIncidents = incidents.filter((i) => i.status === 'active');

  return (
    <AppLayout breadcrumbs={[{ label: 'Dashboard' }]}>
      <div className="flex flex-col gap-space-md">
        {/* Status Strip */}
        <div className="flex flex-wrap items-center justify-between gap-space-sm bg-surface-container-low px-space-md py-space-xs rounded-lg shadow-xs">
          <div className="flex items-center gap-space-md text-on-surface-variant font-mono text-mono-tag">
            <div className="flex items-center gap-1.5 uppercase tracking-wider font-semibold">
              <span className="w-2 h-2 rounded-full bg-primary-container animate-pulse" />
              <span>SRE CONTROL MESH: ONLINE</span>
            </div>
            <span>/</span>
            <div className="flex items-center gap-1">
              <span>CONNECTED REPOS:</span>
              <span className="font-semibold text-on-surface">{repos.length}</span>
            </div>
            <span>/</span>
            <div className="flex items-center gap-1">
              <span>ACTIVE INCIDENTS:</span>
              <span className={activeIncidents.length > 0 ? 'text-error font-semibold' : 'text-success font-semibold'}>
                {activeIncidents.length}
              </span>
            </div>
          </div>

          <Button variant="ghost" size="sm" onClick={loadDashboardData} disabled={isLoading}>
            <RefreshCw className={`w-3.5 h-3.5 mr-1 ${isLoading ? 'animate-spin' : ''}`} />
            Refresh
          </Button>
        </div>

        {/* Welcome Banner */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-space-md bg-surface-container-lowest p-space-lg rounded-xl border border-surface-container-highest/60 shadow-xs">
          <div className="space-y-1">
            <h1 className="font-headline text-headline-lg font-bold text-on-surface">
              Engineering Reliability Dashboard
            </h1>
            <p className="font-body text-body-sm text-on-surface-variant">
              Continuous monitoring, defect research, and autonomous code repair across your connected codebases.
            </p>
          </div>

          <div className="flex items-center gap-2">
            <Button variant="secondary" size="sm" onClick={() => navigate('/repositories?action=connect')}>
              <Plus className="w-4 h-4 mr-1 text-primary" />
              Connect Repository
            </Button>
            <Button size="sm" onClick={() => navigate('/autopatch')}>
              <Cpu className="w-4 h-4 mr-1 text-primary-container" />
              AutoPatch Studio
            </Button>
          </div>
        </div>

        {/* 4 Core KPIs */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-space-md">
          <MetricCard
            label="Connected Repositories"
            value={repos.length}
            footer={<span>{repos.length === 1 ? '1 active codebase' : `${repos.length} active codebases`}</span>}
            icon={<GitBranch className="w-4 h-4 text-primary" />}
            className="cursor-pointer hover:border-primary-container transition-all"
            onClick={() => navigate('/repositories')}
          />
          <MetricCard
            label="Active Incidents"
            value={activeIncidents.length}
            footer={<span>{activeIncidents.length === 0 ? 'Zero active outages' : `${activeIncidents.length} requiring triage`}</span>}
            icon={<AlertOctagon className={`w-4 h-4 ${activeIncidents.length > 0 ? 'text-error' : 'text-success'}`} />}
            className="cursor-pointer hover:border-primary-container transition-all"
            onClick={() => navigate('/incidents')}
          />
          <MetricCard
            label="Autonomous Repairs"
            value={stats?.autonomousRepairs ?? patches.filter(p => p.status === 'approved' || p.prNumber).length}
            footer={<span>Synthesized AST patches</span>}
            icon={<Wrench className="w-4 h-4 text-primary" />}
            className="cursor-pointer hover:border-primary-container transition-all"
            onClick={() => navigate('/code-repairs')}
          />
          <MetricCard
            label="Pending Review"
            value={stats?.pendingReview ?? patches.filter(p => p.status === 'pending_review' || p.status === 'draft').length}
            footer={<span>Awaiting human gate sign-off</span>}
            icon={<Cpu className="w-4 h-4 text-primary" />}
            className="cursor-pointer hover:border-primary-container transition-all"
            onClick={() => navigate('/autopatch')}
          />
        </div>

        {/* Main Content Grid: Repositories & Incident / Activity */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-space-md">
          {/* Left Column: Connected Repositories List (7 cols) */}
          <div className="lg:col-span-7 flex flex-col gap-space-md">
            <Card>
              <CardHeader className="flex flex-row items-center justify-between pb-space-sm border-b border-surface-container-highest">
                <CardTitle icon={<GitBranch className="w-4 h-4 text-primary" />}>
                  Connected Repositories ({repos.length})
                </CardTitle>
                <Button variant="ghost" size="sm" onClick={() => navigate('/repositories')}>
                  View All →
                </Button>
              </CardHeader>

              <div className="p-space-md">
                {repos.length === 0 ? (
                  <EmptyState
                    title="No repositories connected"
                    description="Connect a GitHub repository to begin autonomous monitoring and patch generation."
                    action={
                      <Button size="sm" onClick={() => navigate('/repositories?action=connect')}>
                        <Plus className="w-3.5 h-3.5 mr-1" />
                        Connect First Repository
                      </Button>
                    }
                  />
                ) : (
                  <div className="space-y-3">
                    {repos.map((repo) => (
                      <div
                        key={repo.id}
                        onClick={() => navigate(`/repositories/${repo.id}`)}
                        className="p-3 rounded-lg bg-surface-container-low hover:bg-surface-container border border-surface-container-highest/60 transition-all cursor-pointer flex items-center justify-between gap-3"
                      >
                        <div className="min-w-0 flex-1">
                          <div className="flex items-center gap-2">
                            <span className="font-headline font-semibold text-on-surface text-sm truncate">
                              {repo.fullName || repo.name}
                            </span>
                            <span className="font-mono text-xs px-2 py-0.5 rounded bg-surface-container-high text-on-surface-variant">
                              {repo.branch || 'main'}
                            </span>
                          </div>
                          <div className="text-xs font-mono text-on-surface-variant mt-1 flex items-center gap-3">
                            <span>{repo.language || 'Codebase'}</span>
                            <span>•</span>
                            <span>{repo.fileCount || 0} files</span>
                          </div>
                        </div>

                        <div className="flex items-center gap-2 shrink-0">
                          <Button
                            size="sm"
                            variant="secondary"
                            onClick={(e) => {
                              e.stopPropagation();
                              navigate(`/issues?repoId=${repo.id}`);
                            }}
                          >
                            <CircleDot className="w-3.5 h-3.5 mr-1" />
                            Issues
                          </Button>
                          <Button
                            size="sm"
                            onClick={(e) => {
                              e.stopPropagation();
                              navigate(`/autopatch?repoId=${repo.id}`);
                            }}
                          >
                            <Cpu className="w-3.5 h-3.5 mr-1" />
                            AutoPatch
                          </Button>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </Card>
          </div>

          {/* Right Column: Active Incident or System Health (5 cols) */}
          <div className="lg:col-span-5 flex flex-col gap-space-md">
            {activeIncidents.length > 0 ? (
              <div className="bg-error-container/20 border border-error/40 rounded-xl p-space-md">
                <div className="flex items-center gap-2 text-error font-headline font-bold text-headline-sm mb-1">
                  <AlertOctagon className="w-5 h-5" />
                  Active Incident: {activeIncidents[0].title}
                </div>
                <p className="font-body text-xs text-on-surface mt-1">
                  {activeIncidents[0].description}
                </p>
                <div className="mt-3 flex items-center gap-2">
                  <Button size="sm" onClick={() => navigate('/incidents')}>
                    Triage Incident →
                  </Button>
                </div>
              </div>
            ) : (
              <Card>
                <CardHeader>
                  <CardTitle icon={<CheckCircle2 className="w-4 h-4 text-success" />}>
                    Operational Status
                  </CardTitle>
                </CardHeader>
                <div className="p-space-md space-y-3 font-body text-body-sm">
                  <div className="flex items-center gap-2 text-success font-medium">
                    <CheckCircle2 className="w-4 h-4 shrink-0" />
                    <span>Zero active critical outages</span>
                  </div>
                  <div className="flex items-center gap-2 text-on-surface-variant text-xs">
                    <ShieldCheck className="w-4 h-4 text-primary shrink-0" />
                    <span>Docker Sandbox execution runner operational</span>
                  </div>
                  <div className="flex items-center gap-2 text-on-surface-variant text-xs">
                    <Clock className="w-4 h-4 text-primary shrink-0" />
                    <span>MTTR automated repair pipeline ready</span>
                  </div>

                  <div className="pt-3 border-t border-surface-container-highest">
                    <Button
                      variant="secondary"
                      className="w-full text-xs"
                      onClick={() => navigate('/issues')}
                    >
                      <CircleDot className="w-3.5 h-3.5 mr-1" />
                      Browse GitHub Issues & Defects
                    </Button>
                  </div>
                </div>
              </Card>
            )}

            {/* Recent Code Repairs */}
            <Card>
              <CardHeader className="flex flex-row items-center justify-between pb-space-xs">
                <CardTitle icon={<Wrench className="w-4 h-4 text-primary" />}>
                  Recent Code Repairs ({patches.length})
                </CardTitle>
                {patches.length > 0 && (
                  <Button variant="ghost" size="sm" onClick={() => navigate('/code-repairs')}>
                    View All →
                  </Button>
                )}
              </CardHeader>
              <div className="p-space-md">
                {patches.length === 0 ? (
                  <p className="font-body text-xs text-on-surface-variant italic">
                    No code repairs generated yet. Select an issue in AutoPatch Studio to research and synthesize patches.
                  </p>
                ) : (
                  <div className="space-y-2.5">
                    {patches.slice(0, 3).map((patch) => (
                      <div
                        key={patch.id}
                        onClick={() => navigate(`/autopatch?id=${patch.id}`)}
                        className="p-2.5 rounded-lg bg-surface-container-low hover:bg-surface-container border border-surface-container-highest/60 transition-all cursor-pointer flex items-center justify-between gap-2"
                      >
                        <div className="min-w-0 flex-1">
                          <div className="font-semibold text-xs text-on-surface truncate">
                            {patch.title}
                          </div>
                          <div className="font-mono text-[11px] text-on-surface-variant">
                            {patch.filePath}
                          </div>
                        </div>
                        <Badge variant={patch.status === 'approved' ? 'success' : 'default'}>
                          {patch.status.toUpperCase()}
                        </Badge>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </Card>
          </div>
        </div>
      </div>
    </AppLayout>
  );
}

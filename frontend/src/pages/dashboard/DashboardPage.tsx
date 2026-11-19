import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Network,
  AlertTriangle,
  Wrench,
  FileCheck2,
  GitBranch,
  ArrowUpRight,
  TrendingDown,
  Play,
  Terminal,
  Activity,
  CheckCircle2,
  Clock,
  ChevronRight,
  ShieldAlert,
  RefreshCw,
} from 'lucide-react';
import { AppLayout } from '@/components/layout/AppLayout';
import { MetricCard } from '@/components/ui/MetricCard';
import { Card, CardHeader, CardTitle } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';
import { StatusDot } from '@/components/ui/StatusDot';
import { DataTable } from '@/components/ui/DataTable';
import { dashboardService } from '@/services/dashboard';
import { repositoryService } from '@/services/repositories';
import { incidentService } from '@/services/incidents';
import type { DashboardStats, Repository, Incident } from '@/types';

export function DashboardPage() {
  const navigate = useNavigate();
  const [timeRange, setTimeRange] = useState('Last 24 Hours');
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [repos, setRepos] = useState<Repository[]>([]);
  const [incidents, setIncidents] = useState<Incident[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  const loadDashboardData = async () => {
    setIsLoading(true);
    try {
      const [statsRes, reposRes, incRes] = await Promise.all([
        dashboardService.getStats().catch(() => null),
        repositoryService.list().catch(() => null),
        incidentService.list().catch(() => null),
      ]);
      if (statsRes?.data) setStats(statsRes.data);
      if (reposRes?.data) setRepos(reposRes.data);
      if (incRes?.data) setIncidents(incRes.data);
    } catch (err) {
      console.error('Error loading dashboard data:', err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadDashboardData();
  }, []);

  return (
    <AppLayout breadcrumbs={[{ label: 'Dashboard' }]}>
      {/* Zone 0: Telemetry Strip & Top Meta */}
      <div className="flex flex-wrap items-center justify-between gap-space-sm bg-surface-container-low px-space-md py-space-xs rounded-lg shadow-xs mb-space-md">
        <div className="flex items-center gap-space-md text-on-surface-variant font-mono text-mono-tag">
          <div className="flex items-center gap-1.5 uppercase tracking-wider font-semibold">
            <span className="w-2 h-2 rounded-full bg-primary-container animate-ping" />
            <span>CLUSTER MESH: ACTIVE</span>
          </div>
          <span>/</span>
          <div className="flex items-center gap-1">
            <span>REGION:</span>
            <span className="font-semibold text-on-surface">us-east-1 (N. Virginia)</span>
          </div>
          <span className="hidden sm:inline">/</span>
          <div className="hidden sm:flex items-center gap-1">
            <span>UPTIME:</span>
            <span className="font-semibold text-on-surface">99.982%</span>
          </div>
        </div>
        <div className="flex items-center gap-space-sm">
          <span className="px-2 py-0.5 rounded bg-primary-fixed text-on-primary-fixed-variant font-mono text-mono-tag font-semibold">
            LIVE MONITORING
          </span>
          <span className="font-mono text-mono-tag text-on-surface-variant">ONLINE</span>
        </div>
      </div>

      {/* Zone 1: Welcome Cockpit */}
      <div className="flex flex-col lg:flex-row lg:items-end justify-between gap-space-md bg-surface-container-lowest p-space-lg rounded-xl shadow-card relative overflow-hidden mb-space-md border border-surface-container-highest/60">
        <div className="absolute right-0 top-0 bottom-0 w-1 bg-primary-container" />
        <div className="flex flex-col gap-space-xs max-w-3xl">
          <div className="flex items-center gap-space-xs">
            <span className="px-2 py-0.5 rounded-full bg-surface-container-high text-on-surface font-mono text-mono-tag uppercase tracking-wider flex items-center gap-1">
              <span className="w-1.5 h-1.5 rounded-full bg-primary-container" />
              SYS_ORCHESTRATOR ONLINE
            </span>
            <span className="font-mono text-mono-tag text-on-surface-variant">REV_48.12.9</span>
          </div>
          <h1 className="font-headline text-headline-lg font-bold text-on-surface tracking-tight">
            Good morning, Engineering Team.
          </h1>
          <p className="font-body text-body-md text-on-surface-variant">
            Here's the current health of your engineering environment across{' '}
            <span className="font-semibold text-on-surface">{repos.length} connected repositories</span> and autonomous repair agents.
          </p>
        </div>

        {/* Action Controls */}
        <div className="flex flex-wrap items-center gap-space-sm shrink-0">
          <Button variant="secondary" size="md" onClick={loadDashboardData} disabled={isLoading}>
            <RefreshCw className={`w-4 h-4 mr-1 text-on-surface-variant ${isLoading ? 'animate-spin' : ''}`} />
            Refresh
          </Button>
          <Button onClick={() => navigate('/investigations')}>
            <Play className="w-4 h-4 text-primary-fixed mr-1" />
            <span>Run Diagnostics</span>
          </Button>
        </div>
      </div>

      {/* Zone 2: 4 Bento KPI Metrics Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-space-md mb-space-lg">
        <MetricCard
          label="Repositories Connected"
          value={stats ? String(stats.totalRepositories ?? repos.length) : String(repos.length)}
          icon={<GitBranch className="w-5 h-5 text-on-surface-variant" />}
          change={
            <span className="font-body text-label-sm font-semibold text-primary flex items-center">
              <ArrowUpRight className="w-4 h-4" /> {repos.length} active repos
            </span>
          }
          footer={
            <>
              <span>AST index status</span>
              <span className="flex items-center gap-1 text-on-surface font-medium">
                <span className="w-1.5 h-1.5 rounded-full bg-primary" /> Multi-Language AST
              </span>
            </>
          }
        />

        <MetricCard
          label="Active Incidents"
          value={stats ? String(stats.activeIncidents ?? incidents.length) : String(incidents.length)}
          icon={<AlertTriangle className="w-5 h-5 text-error" />}
          change={
            <span className="px-2 py-0.5 rounded bg-error-container text-on-error-container font-mono text-mono-tag font-semibold">
              {incidents.filter(i => i.severity === 'sev1').length} SEV-1
            </span>
          }
          footer={
            <div className="w-full flex justify-between text-[11px] text-on-surface-variant font-mono">
              <span>{incidents.filter(i => i.status === 'active').length} Active</span>
              <span>{incidents.filter(i => i.status === 'resolved').length} Resolved</span>
            </div>
          }
        />

        <MetricCard
          label="Autonomous Repairs"
          value={stats ? String(stats.autonomousRepairs ?? 0) : "0"}
          icon={<Wrench className="w-5 h-5 text-primary-container" />}
          change={<span className="font-mono text-label-sm text-on-surface-variant font-medium">AST verified</span>}
          footer={
            <>
              <span>Docker sandbox pass rate</span>
              <span className="font-semibold text-primary-container">
                {stats ? `${stats.testsPassRate ?? 0}%` : "0%"}
              </span>
            </>
          }
        />

        <MetricCard
          label="Pending Review"
          value={stats ? String(stats.pendingReview ?? 0) : "0"}
          icon={<FileCheck2 className="w-5 h-5 text-on-surface-variant" />}
          change={
            <span className="px-2 py-0.5 rounded bg-surface-container-high text-on-surface font-mono text-mono-tag font-semibold">
              HUMAN GATE ACTIVE
            </span>
          }
          footer={
            <>
              <span>Draft PR protection</span>
              <span className="text-primary font-semibold">Reviewer Approved</span>
            </>
          }
        />
      </div>

      {/* Zone 3: Two-Column Operational Core View */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-space-lg">
        {/* Left Column: Connected Repositories & MTTR Graph */}
        <div className="lg:col-span-7 flex flex-col gap-space-lg">
          {/* Table: Connected Repositories Health */}
          <Card>
            <CardHeader className="flex items-center justify-between">
              <div className="flex items-center gap-space-sm">
                <GitBranch className="w-5 h-5 text-primary" />
                <h2 className="font-headline text-headline-sm font-bold text-on-surface">Connected Repositories</h2>
                <Badge variant="outline">{repos.length} monitored</Badge>
              </div>
              <Button variant="ghost" size="sm" onClick={() => navigate('/repositories')}>
                <span>View all repositories</span>
                <ChevronRight className="w-4 h-4" />
              </Button>
            </CardHeader>

            <div className="overflow-x-auto">
              <table className="w-full text-left font-body text-body-sm">
                <thead>
                  <tr className="bg-surface-container-low font-mono text-mono-tag uppercase tracking-wider text-on-surface-variant">
                    <th className="py-2.5 px-3 rounded-l font-semibold">Repository</th>
                    <th className="py-2.5 px-3 font-semibold">Language</th>
                    <th className="py-2.5 px-3 font-semibold">Health Status</th>
                    <th className="py-2.5 px-3 font-semibold">Issues</th>
                    <th className="py-2.5 px-3 text-right rounded-r font-semibold">Action</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-surface-container-highest/30">
                  {repos.slice(0, 5).map((repo) => (
                    <tr
                      key={repo.id}
                      className={
                        repo.healthStatus === 'critical'
                          ? 'bg-error-container/15 hover:bg-error-container/25 transition-colors cursor-pointer'
                          : 'hover:bg-surface-container-low transition-colors cursor-pointer'
                      }
                      onClick={() => navigate(`/repositories/${repo.id}`)}
                    >
                      <td className="py-3 px-3">
                        <div className="flex items-center gap-2">
                          <StatusDot status={repo.healthStatus} pulse={repo.healthStatus === 'critical'} size="md" />
                          <div className="flex flex-col">
                            <span className="font-mono text-mono-code font-semibold text-on-surface">
                              {repo.name}
                            </span>
                            <span className="font-mono text-[10px] text-on-surface-variant">
                              branch: {repo.branch}
                            </span>
                          </div>
                        </div>
                      </td>
                      <td className="py-3 px-3">
                        <span className="font-mono text-mono-tag px-1.5 py-0.5 rounded bg-surface-container text-on-surface">
                          {repo.language || 'Unknown'}
                        </span>
                      </td>
                      <td className="py-3 px-3">
                        <Badge variant={repo.healthStatus === 'critical' ? 'critical' : repo.healthStatus === 'warning' ? 'warning' : 'success'}>
                          {repo.healthStatus.toUpperCase()}
                        </Badge>
                      </td>
                      <td className="py-3 px-3 font-mono text-xs">
                        {repo.issueCount || 0} open
                      </td>
                      <td className="py-3 px-3 text-right">
                        <Button variant="ghost" size="sm" onClick={(e) => { e.stopPropagation(); navigate(`/repositories/${repo.id}`); }}>
                          Inspect
                        </Button>
                      </td>
                    </tr>
                  ))}
                  {repos.length === 0 && (
                    <tr>
                      <td colSpan={5} className="py-8 text-center text-on-surface-variant font-body">
                        No repositories connected yet. Click &quot;View all repositories&quot; to connect one.
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          </Card>

          {/* MTTR Reduction Chart Card */}
          <Card>
            <div className="flex flex-wrap items-center justify-between gap-space-sm mb-space-md">
              <div>
                <span className="font-mono text-mono-tag text-on-surface-variant uppercase tracking-wider">
                  Reliability Impact
                </span>
                <h3 className="font-headline text-headline-sm font-bold text-on-surface">
                  Mean Time to Resolution (MTTR)
                </h3>
              </div>
              <div className="flex items-center gap-space-md font-mono text-mono-tag">
                <div className="flex items-center gap-1.5">
                  <span className="w-2.5 h-2.5 rounded-xs bg-secondary" />
                  <span className="text-on-surface-variant">Manual: 4.2h</span>
                </div>
                <div className="flex items-center gap-1.5">
                  <span className="w-2.5 h-2.5 rounded-xs bg-primary-container" />
                  <span className="font-semibold text-primary">FIXORA Autonomous: 18m</span>
                </div>
              </div>
            </div>

            {/* Simulated Technical Histogram Bars */}
            <div className="bg-surface-container-low p-space-md rounded-lg flex flex-col gap-2">
              <div className="h-36 w-full flex items-end justify-between gap-4 pt-4 px-2">
                {[
                  { week: 'W1', manual: 85, fixora: 12 },
                  { week: 'W2', manual: 78, fixora: 10 },
                  { week: 'W3', manual: 90, fixora: 8 },
                  { week: 'W4', manual: 82, fixora: 7 },
                  { week: 'W5', manual: 75, fixora: 6 },
                ].map((item) => (
                  <div key={item.week} className="flex-1 flex flex-col items-center gap-1 h-full justify-end">
                    <div className="w-full flex items-end justify-center gap-1.5 h-full">
                      <div
                        className="w-1/2 bg-secondary-container rounded-t transition-all"
                        style={{ height: `${item.manual}%` }}
                        title={`Manual: ${item.manual}%`}
                      />
                      <div
                        className="w-1/2 bg-primary-container rounded-t transition-all"
                        style={{ height: `${item.fixora}%` }}
                        title={`FIXORA: ${item.fixora}%`}
                      />
                    </div>
                    <span className="font-mono text-[10px] text-on-surface-variant">{item.week}</span>
                  </div>
                ))}
              </div>
              <div className="pt-2 border-t border-surface-container-highest text-center font-mono text-[11px] text-on-surface-variant">
                MTTR REDUCTION: 92.8% ACROSS 142 INCIDENTS
              </div>
            </div>
          </Card>
        </div>

        {/* Right Column: Live Incident Cockpit & Agent Pipeline */}
        <div className="lg:col-span-5 flex flex-col gap-space-lg">
          {/* Active Incident #1842 Focus Box */}
          <div className="bg-inverse-surface rounded-xl p-space-md text-inverse-on-surface shadow-elevated border border-surface-container-highest/20">
            <div className="flex items-center justify-between pb-space-xs border-b border-surface-container-highest/20 mb-space-sm">
              <span className="inline-flex items-center gap-1.5 px-2 py-0.5 rounded bg-error-container/20 text-error font-mono text-mono-tag font-semibold">
                <span className="w-1.5 h-1.5 rounded-full bg-error animate-ping" />
                INCIDENT #1842: SEV-1 ACTIVE
              </span>
              <span className="font-mono text-mono-tag text-primary-fixed bg-primary-container/20 px-2 py-0.5 rounded">
                CONFIDENCE 98.4%
              </span>
            </div>

            <h3 className="font-headline text-headline-sm font-bold text-inverse-on-surface mb-1">
              Connection Pool Exhaustion under Burst Load
            </h3>
            <p className="font-mono text-mono-code text-xs text-inverse-on-surface/80 mb-space-md">
              Target: <span className="text-primary-fixed">payment-service (Go 1.22)</span> • Stack: HTTP 503 Gateway Timeout
            </p>

            {/* 5-Agent Status Pipeline */}
            <div className="space-y-2 mb-space-md">
              <div className="flex items-center justify-between text-xs font-mono p-2 rounded bg-surface-container-high/10">
                <span className="text-inverse-on-surface/70">01. Triage Agent</span>
                <span className="text-success flex items-center gap-1"><CheckCircle2 className="w-3.5 h-3.5" /> Sentry Log Parsed</span>
              </div>
              <div className="flex items-center justify-between text-xs font-mono p-2 rounded bg-surface-container-high/10">
                <span className="text-inverse-on-surface/70">02. Retrieval Agent</span>
                <span className="text-success flex items-center gap-1"><CheckCircle2 className="w-3.5 h-3.5" /> Correlated PR #312</span>
              </div>
              <div className="flex items-center justify-between text-xs font-mono p-2 rounded bg-surface-container-high/10">
                <span className="text-inverse-on-surface/70">03. Root Cause Agent</span>
                <span className="text-success flex items-center gap-1"><CheckCircle2 className="w-3.5 h-3.5" /> Isolated Line 142</span>
              </div>
              <div className="flex items-center justify-between text-xs font-mono p-2 rounded bg-surface-container-high/10">
                <span className="text-inverse-on-surface/70">04. AST Patch Agent</span>
                <span className="text-success flex items-center gap-1"><CheckCircle2 className="w-3.5 h-3.5" /> Synthesized Backoff</span>
              </div>
              <div className="flex items-center justify-between text-xs font-mono p-2 rounded bg-primary-container/20 text-primary-fixed">
                <span className="font-semibold">05. Docker Sandbox</span>
                <span className="flex items-center gap-1"><Activity className="w-3.5 h-3.5 animate-spin" /> 18/18 Tests Passed</span>
              </div>
            </div>

            <Button
              className="w-full"
              onClick={() => navigate('/investigations/INV-1842')}
            >
              Open Full Investigation Console →
            </Button>
          </div>

          {/* Quick Actions & Recent Activity Feed */}
          <Card>
            <CardHeader>
              <CardTitle icon={<Activity className="w-4 h-4 text-primary" />}>
                Recent Autonomous Activity
              </CardTitle>
            </CardHeader>
            <div className="space-y-3 font-body text-body-sm">
              <div className="flex items-start gap-2.5 pb-2.5 border-b border-surface-container-highest/40">
                <span className="w-2 h-2 rounded-full bg-success mt-1.5 shrink-0" />
                <div className="flex-1">
                  <div className="font-semibold text-on-surface">AutoPatch PR #409 Created</div>
                  <div className="text-xs text-on-surface-variant font-mono">payment-service • 4 minutes ago</div>
                </div>
              </div>
              <div className="flex items-start gap-2.5 pb-2.5 border-b border-surface-container-highest/40">
                <span className="w-2 h-2 rounded-full bg-primary-container mt-1.5 shrink-0" />
                <div className="flex-1">
                  <div className="font-semibold text-on-surface">Docker Sandbox Re-run Verified</div>
                  <div className="text-xs text-on-surface-variant font-mono">checkout-platform • 22 minutes ago</div>
                </div>
              </div>
              <div className="flex items-start gap-2.5">
                <span className="w-2 h-2 rounded-full bg-on-surface-variant mt-1.5 shrink-0" />
                <div className="flex-1">
                  <div className="font-semibold text-on-surface">AST Index Updated</div>
                  <div className="text-xs text-on-surface-variant font-mono">user-management • 1 hour ago</div>
                </div>
              </div>
            </div>
          </Card>
        </div>
      </div>
    </AppLayout>
  );
}

import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Bug as BugIcon, AlertOctagon, CheckCircle2, Search, Filter, RefreshCw, Play, ArrowRight } from 'lucide-react';
import { AppLayout } from '@/components/layout/AppLayout';
import { Card } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';
import { LoadingState } from '@/components/ui/LoadingState';
import { EmptyState } from '@/components/ui/EmptyState';
import { bugService } from '@/services/bugs';
import { investigationService } from '@/services/investigations';
import type { Bug } from '@/types';

export function BugsPage() {
  const navigate = useNavigate();
  const [bugs, setBugs] = useState<Bug[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterSeverity, setFilterSeverity] = useState('all');
  const [investigatingId, setInvestigatingId] = useState<string | null>(null);

  const fetchBugs = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const res = await bugService.list();
      setBugs(res?.data || []);
    } catch (err: any) {
      console.error('Failed to fetch bugs:', err);
      setError(err.message || 'Failed to load bugs from database');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchBugs();
  }, []);

  const handleLaunchInvestigation = async (e: React.MouseEvent, bug: Bug) => {
    e.stopPropagation();
    setInvestigatingId(bug.id);
    try {
      const res = await investigationService.create({
        question: `Investigate root cause and patch for ${bug.title}`,
        projectId: bug.projectId || 'proj_demo_001',
        bugId: bug.id,
      });
      if (res?.data?.id) {
        navigate(`/investigations/${res.data.id}`);
      } else {
        navigate('/investigations');
      }
    } catch (err) {
      console.error('Failed to trigger investigation:', err);
      navigate('/investigations');
    } finally {
      setInvestigatingId(null);
    }
  };

  const filtered = bugs.filter((bug) => {
    const matchesSearch =
      (bug.title || '').toLowerCase().includes(searchTerm.toLowerCase()) ||
      (bug.filePath || '').toLowerCase().includes(searchTerm.toLowerCase());
    const matchesSeverity = filterSeverity === 'all' || bug.severity === filterSeverity;
    return matchesSearch && matchesSeverity;
  });

  return (
    <AppLayout breadcrumbs={[{ label: 'Engineering' }, { label: 'Issues & Bugs' }]}>
      <div className="flex flex-col gap-space-md">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-space-sm pb-space-sm border-b border-surface-container-highest">
          <div>
            <h1 className="font-headline text-headline-lg font-bold text-on-surface">Issues & Bugs</h1>
            <p className="font-body text-body-sm text-on-surface-variant">
              Static analysis findings, runtime exceptions, and test-verified code anomalies.
            </p>
          </div>
          <Button variant="secondary" size="md" onClick={fetchBugs} disabled={isLoading}>
            <RefreshCw className={`w-4 h-4 mr-1 text-on-surface-variant ${isLoading ? 'animate-spin' : ''}`} />
            Refresh
          </Button>
        </div>

        {/* Filter bar */}
        <div className="flex flex-wrap items-center gap-space-sm">
          <div className="relative flex-1 min-w-[240px]">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-on-surface-variant w-4 h-4" />
            <input
              type="text"
              placeholder="Search by bug title or file path..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="fixora-input pl-9"
            />
          </div>
          <select
            value={filterSeverity}
            onChange={(e) => setFilterSeverity(e.target.value)}
            className="h-10 px-3 rounded-lg bg-surface-container-low text-on-surface font-body text-label-md border border-surface-container-highest"
          >
            <option value="all">All Severities</option>
            <option value="critical">Critical</option>
            <option value="high">High</option>
            <option value="medium">Medium</option>
            <option value="low">Low</option>
          </select>
        </div>

        {isLoading ? (
          <LoadingState message="Loading detected issues and AST defects..." />
        ) : error ? (
          <div className="p-space-lg bg-error-container/20 border border-error/30 rounded-xl text-center">
            <p className="font-bold text-on-surface">{error}</p>
            <Button variant="secondary" size="sm" className="mt-4" onClick={fetchBugs}>
              Retry
            </Button>
          </div>
        ) : filtered.length === 0 ? (
          <EmptyState
            title={searchTerm ? 'No matching bugs found' : 'No bugs or defects recorded'}
            description="All monitored services are passing static AST and runtime health checks."
          />
        ) : (
          <div className="grid grid-cols-1 gap-space-sm">
            {filtered.map((bug) => (
              <Card
                key={bug.id}
                className="p-space-md hover:border-primary-container transition-all cursor-pointer"
                onClick={() => navigate('/autopatch')}
              >
                <div className="flex flex-col md:flex-row md:items-center justify-between gap-space-sm">
                  <div>
                    <div className="flex items-center gap-2 mb-1 flex-wrap">
                      <span className="font-mono text-mono-tag font-bold text-primary">{bug.id}</span>
                      <span className="font-mono text-xs text-on-surface-variant">{bug.repositoryId || 'service'}</span>
                      <Badge
                        variant={
                          bug.severity === 'critical'
                            ? 'critical'
                            : bug.severity === 'high'
                            ? 'warning'
                            : 'default'
                        }
                      >
                        {bug.severity.toUpperCase()}
                      </Badge>
                      <span className="font-mono text-mono-tag px-1.5 py-0.5 rounded bg-surface-container text-on-surface-variant">
                        status: {bug.status}
                      </span>
                    </div>
                    <h3 className="font-headline text-headline-sm font-bold text-on-surface">{bug.title}</h3>
                    <div className="font-mono text-xs text-primary font-semibold mt-1">
                      {bug.filePath}:{bug.lineStart}-{bug.lineEnd}
                    </div>
                    {bug.rootCause && (
                      <p className="font-body text-xs text-on-surface-variant mt-1 max-w-3xl line-clamp-2">
                        {bug.rootCause}
                      </p>
                    )}
                  </div>
                  <div className="flex items-center gap-space-sm self-end md:self-center shrink-0">
                    <Button
                      size="sm"
                      variant="secondary"
                      disabled={investigatingId === bug.id}
                      onClick={(e) => handleLaunchInvestigation(e, bug)}
                    >
                      <Play className="w-3.5 h-3.5 mr-1" />
                      {investigatingId === bug.id ? 'Starting...' : 'Investigate'}
                    </Button>
                    <Button size="sm" onClick={() => navigate('/autopatch')}>
                      Review Patch →
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

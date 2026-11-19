import { useState, useEffect } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import {
  Wrench,
  Search,
  RefreshCw,
  GitPullRequest,
  GitBranch,
  ChevronDown,
  Cpu,
  Plus,
} from 'lucide-react';
import { AppLayout } from '@/components/layout/AppLayout';
import { Card } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';
import { LoadingState } from '@/components/ui/LoadingState';
import { EmptyState } from '@/components/ui/EmptyState';
import { patchService } from '@/services/patches';
import { repositoryService } from '@/services/repositories';
import type { Patch, Repository } from '@/types';

export function CodeRepairsPage() {
  const navigate = useNavigate();
  const [searchParams, setSearchParams] = useSearchParams();
  const repoIdParam = searchParams.get('repoId');

  const [repositories, setRepositories] = useState<Repository[]>([]);
  const [selectedRepo, setSelectedRepo] = useState<Repository | null>(null);
  const [patches, setPatches] = useState<Patch[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');

  // Load repositories
  useEffect(() => {
    async function loadRepos() {
      try {
        const res = await repositoryService.list();
        const repoList = res?.data || [];
        setRepositories(repoList);
        if (repoList.length > 0) {
          const matched = repoIdParam ? repoList.find((r) => r.id === repoIdParam) : null;
          setSelectedRepo(matched || repoList[0]);
        }
      } catch (err) {
        console.error('Failed to load repositories for Code Repairs:', err);
      }
    }
    loadRepos();
  }, []);

  const fetchRepairs = async (repoId?: string) => {
    setIsLoading(true);
    setError(null);
    try {
      const targetId = repoId || selectedRepo?.id;
      const res = await patchService.list(targetId ? { repositoryId: targetId } : undefined);
      setPatches(res?.data || []);
    } catch (err: any) {
      console.error('Failed to fetch repairs history:', err);
      setError(err.message || 'Failed to load code repairs from database');
      setPatches([]);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    if (selectedRepo) {
      setSearchParams({ repoId: selectedRepo.id });
      fetchRepairs(selectedRepo.id);
    } else {
      setIsLoading(false);
    }
  }, [selectedRepo]);

  const filteredPatches = patches.filter((p) => {
    const matchesSearch =
      (p.title || '').toLowerCase().includes(searchTerm.toLowerCase()) ||
      (p.filePath || '').toLowerCase().includes(searchTerm.toLowerCase()) ||
      (p.repositoryId || '').toLowerCase().includes(searchTerm.toLowerCase());
    const matchesStatus =
      statusFilter === 'all' ||
      (statusFilter === 'pending_review' && (p.status === 'pending_review' || p.status === 'draft')) ||
      (statusFilter === 'approved' && p.status === 'approved') ||
      (statusFilter === 'pr_created' && Boolean(p.prNumber));
    return matchesSearch && matchesStatus;
  });

  return (
    <AppLayout breadcrumbs={[{ label: 'Engineering' }, { label: 'Code Repairs' }]}>
      <div className="flex flex-col gap-space-md">
        {/* Header */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-space-sm pb-space-sm border-b border-surface-container-highest">
          <div>
            <h1 className="font-headline text-headline-lg font-bold text-on-surface">Code Repairs History</h1>
            <p className="font-body text-body-sm text-on-surface-variant">
              Audit log of synthesized AST code repairs, sandbox verification outcomes, and GitHub PR staging.
            </p>
          </div>

          <div className="flex items-center gap-2 flex-wrap">
            {/* Repository Selector */}
            {repositories.length > 0 && (
              <div className="relative">
                <select
                  value={selectedRepo?.id || ''}
                  onChange={(e) => {
                    const r = repositories.find((x) => x.id === e.target.value);
                    if (r) setSelectedRepo(r);
                  }}
                  className="h-10 pl-9 pr-8 rounded-lg bg-surface-container-low text-on-surface font-body text-label-md border border-surface-container-highest appearance-none cursor-pointer focus:outline-none focus:border-primary-container"
                >
                  {repositories.map((repo) => (
                    <option key={repo.id} value={repo.id}>
                      {repo.fullName || repo.name}
                    </option>
                  ))}
                </select>
                <GitBranch className="w-4 h-4 text-on-surface-variant absolute left-3 top-1/2 -translate-y-1/2 pointer-events-none" />
                <ChevronDown className="w-4 h-4 text-on-surface-variant absolute right-2.5 top-1/2 -translate-y-1/2 pointer-events-none" />
              </div>
            )}

            <Button variant="secondary" size="md" onClick={() => fetchRepairs()} disabled={isLoading}>
              <RefreshCw className={`w-4 h-4 mr-1 text-on-surface-variant ${isLoading ? 'animate-spin' : ''}`} />
              Refresh
            </Button>

            <Button onClick={() => navigate(`/autopatch?repoId=${selectedRepo?.id || ''}`)}>
              <Cpu className="w-4 h-4 mr-1.5 text-primary-container" />
              AutoPatch Studio
            </Button>
          </div>
        </div>

        {/* Filter Toolbar */}
        <div className="flex flex-col sm:flex-row items-center justify-between gap-space-sm">
          <div className="relative flex-1 max-w-md w-full">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-on-surface-variant w-4 h-4" />
            <input
              type="text"
              placeholder="Search repairs by title, file, or id..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="fixora-input pl-9 w-full text-sm"
            />
          </div>

          <div className="flex items-center gap-2 self-start sm:self-auto">
            <span className="text-xs text-on-surface-variant font-mono uppercase">Filter:</span>
            {['all', 'pending_review', 'approved', 'pr_created'].map((st) => (
              <button
                key={st}
                onClick={() => setStatusFilter(st)}
                className={`px-2.5 py-1 text-xs rounded-full font-mono transition-colors ${
                  statusFilter === st
                    ? 'bg-primary text-on-primary font-semibold'
                    : 'bg-surface-container-high text-on-surface-variant hover:text-on-surface'
                }`}
              >
                {st.replace('_', ' ').toUpperCase()}
              </button>
            ))}
          </div>
        </div>

        {/* Content */}
        {isLoading ? (
          <LoadingState message="Loading code repair audit records..." />
        ) : error ? (
          <div className="p-space-lg bg-error-container/20 border border-error/30 rounded-xl text-center">
            <p className="font-bold text-on-surface">{error}</p>
            <Button variant="secondary" size="sm" className="mt-4" onClick={() => fetchRepairs()}>
              Retry
            </Button>
          </div>
        ) : filteredPatches.length === 0 ? (
          <EmptyState
            title="No Code Repairs Found"
            description={
              selectedRepo
                ? `No code repairs have been generated for '${selectedRepo.fullName || selectedRepo.name}' yet.`
                : 'Connect a repository and use AutoPatch Studio to research defects and synthesize patches.'
            }
            action={
              <Button onClick={() => navigate(`/autopatch?repoId=${selectedRepo?.id || ''}`)}>
                <Cpu className="w-4 h-4 mr-1.5" />
                Open AutoPatch Studio
              </Button>
            }
          />
        ) : (
          <div className="space-y-space-sm">
            {filteredPatches.map((patch) => (
              <Card
                key={patch.id}
                className="p-space-md hover:border-primary-container transition-all cursor-pointer"
                onClick={() => navigate(`/autopatch?id=${patch.id}&repoId=${selectedRepo?.id || ''}`)}
              >
                <div className="flex flex-col md:flex-row md:items-center justify-between gap-space-sm">
                  <div className="space-y-1">
                    <div className="flex items-center gap-2 flex-wrap">
                      <span className="font-mono text-mono-tag font-bold text-primary">{patch.id}</span>
                      <span className="font-mono text-xs text-on-surface-variant bg-surface-container-high px-2 py-0.5 rounded">
                        {patch.repositoryId}
                      </span>
                      <Badge
                        variant={
                          patch.status === 'approved' || Boolean(patch.prNumber)
                            ? 'success'
                            : patch.status === 'rejected' || patch.status === 'failed'
                            ? 'critical'
                            : 'warning'
                        }
                        dot
                      >
                        {patch.status.replace('_', ' ').toUpperCase()}
                      </Badge>
                      {patch.prNumber && (
                        <span className="font-mono text-xs text-primary flex items-center gap-1 font-semibold">
                          <GitPullRequest className="w-3.5 h-3.5" />
                          PR #{patch.prNumber}
                        </span>
                      )}
                    </div>
                    <h3 className="font-headline text-headline-sm font-bold text-on-surface">{patch.title}</h3>
                    <p className="font-mono text-xs text-on-surface-variant flex items-center gap-1">
                      Target File: <span className="text-on-surface font-medium">{patch.filePath}</span>
                    </p>
                    {patch.explanation && (
                      <p className="font-body text-xs text-on-surface-variant line-clamp-2 mt-1">
                        {patch.explanation}
                      </p>
                    )}
                  </div>

                  <div className="flex items-center gap-space-sm self-end md:self-center shrink-0">
                    <Button
                      size="sm"
                      variant="secondary"
                      onClick={(e) => {
                        e.stopPropagation();
                        navigate(`/autopatch?id=${patch.id}&repoId=${selectedRepo?.id || ''}`);
                      }}
                    >
                      Open in Studio →
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

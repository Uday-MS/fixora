import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { GitBranch, Plus, Search, RefreshCw, Trash2, ExternalLink, AlertTriangle, ShieldCheck } from 'lucide-react';
import { AppLayout } from '@/components/layout/AppLayout';
import { Card } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';
import { StatusDot } from '@/components/ui/StatusDot';
import { LoadingState } from '@/components/ui/LoadingState';
import { EmptyState } from '@/components/ui/EmptyState';
import { ConnectRepoModal } from '@/components/shared/ConnectRepoModal';
import { repositoryService } from '@/services/repositories';
import type { Repository } from '@/types';

export function RepositoriesPage() {
  const navigate = useNavigate();
  const [repositories, setRepositories] = useState<Repository[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isConnectOpen, setIsConnectOpen] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [syncingId, setSyncingId] = useState<string | null>(null);

  const fetchRepositories = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const res = await repositoryService.list();
      setRepositories(res?.data || []);
    } catch (err: any) {
      console.error('Failed to fetch repositories:', err);
      setError(err.message || 'Failed to communicate with FIXORA backend');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchRepositories();
  }, []);

  const handleSyncRepo = async (e: React.MouseEvent, id: string) => {
    e.stopPropagation();
    setSyncingId(id);
    try {
      await repositoryService.sync(id);
      await fetchRepositories();
    } catch (err) {
      console.error('Failed to sync repository:', err);
    } finally {
      setSyncingId(null);
    }
  };

  const handleDeleteRepo = async (e: React.MouseEvent, id: string, name: string) => {
    e.stopPropagation();
    if (!window.confirm(`Are you sure you want to remove '${name}' from FIXORA monitoring?`)) return;
    try {
      await repositoryService.delete(id);
      setRepositories((prev) => prev.filter((r) => r.id !== id));
    } catch (err: any) {
      alert(`Failed to delete repository: ${err.message}`);
    }
  };

  const filtered = repositories.filter(
    (r) =>
      (r.name || '').toLowerCase().includes(searchTerm.toLowerCase()) ||
      (r.fullName || '').toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <AppLayout breadcrumbs={[{ label: 'Engineering' }, { label: 'Repositories' }]}>
      <div className="flex flex-col gap-space-md">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-space-sm pb-space-sm border-b border-surface-container-highest">
          <div>
            <h1 className="font-headline text-headline-lg font-bold text-on-surface">Connected Repositories</h1>
            <p className="font-body text-body-sm text-on-surface-variant">
              Monitored codebases, AST dependency graphs, and test execution configs.
            </p>
          </div>
          <Button onClick={() => setIsConnectOpen(true)}>
            <Plus className="w-4 h-4 mr-1" />
            Connect Repository
          </Button>
        </div>

        {/* Filter bar */}
        <div className="flex items-center gap-space-sm">
          <div className="relative flex-1 max-w-md">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-on-surface-variant w-4 h-4" />
            <input
              type="text"
              placeholder="Filter repositories..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="fixora-input pl-9"
            />
          </div>
          <Button variant="secondary" size="md" onClick={fetchRepositories} disabled={isLoading}>
            <RefreshCw className={`w-4 h-4 mr-1 text-on-surface-variant ${isLoading ? 'animate-spin' : ''}`} />
            Refresh
          </Button>
        </div>

        {isLoading ? (
          <LoadingState message="Loading repositories from FIXORA database..." />
        ) : error ? (
          <div className="p-space-lg bg-error-container/20 border border-error/30 rounded-xl text-center">
            <AlertTriangle className="w-8 h-8 text-error mx-auto mb-2" />
            <p className="font-bold text-on-surface">{error}</p>
            <Button variant="secondary" size="sm" className="mt-4" onClick={fetchRepositories}>
              Retry Connection
            </Button>
          </div>
        ) : filtered.length === 0 ? (
          <EmptyState
            title={searchTerm ? 'No matching repositories found' : 'No repositories connected yet'}
            description={
              searchTerm
                ? 'Try adjusting your search filter.'
                : 'Connect a public or private GitHub repository, or upload a ZIP archive of your source code.'
            }
            action={
              !searchTerm ? (
                <Button onClick={() => setIsConnectOpen(true)}>
                  <Plus className="w-4 h-4 mr-1" />
                  Connect Repository
                </Button>
              ) : undefined
            }
          />
        ) : (
          <div className="grid grid-cols-1 gap-space-md">
            {filtered.map((repo) => (
              <Card
                key={repo.id}
                className="p-space-md hover:border-primary-container transition-all cursor-pointer"
                onClick={() => navigate(`/repositories/${repo.id}`)}
              >
                <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-space-md">
                  <div className="flex items-start gap-space-sm">
                    <div className="w-10 h-10 rounded-xl bg-surface-container-high flex items-center justify-center text-on-surface shrink-0 mt-0.5">
                      <GitBranch className="w-5 h-5 text-primary" />
                    </div>
                    <div>
                      <div className="flex items-center gap-2 mb-1 flex-wrap">
                        <h3 className="font-headline text-headline-sm font-bold text-on-surface">
                          {repo.name}
                        </h3>
                        <Badge
                          variant={
                            repo.healthStatus === 'critical'
                              ? 'critical'
                              : repo.healthStatus === 'warning'
                              ? 'warning'
                              : 'success'
                          }
                          dot
                        >
                          {repo.healthStatus.toUpperCase()}
                        </Badge>
                        <span className="font-mono text-mono-tag px-2 py-0.5 rounded bg-surface-container-high text-on-surface-variant">
                          {repo.language || 'Unknown'}
                        </span>
                        <span className="font-mono text-mono-tag px-2 py-0.5 rounded bg-surface-container-low text-on-surface-variant">
                          branch: {repo.branch}
                        </span>
                      </div>
                      <p className="font-mono text-mono-tag text-on-surface-variant">
                        {repo.fullName || repo.url}
                      </p>
                    </div>
                  </div>

                  <div className="flex items-center gap-space-lg self-end lg:self-center font-mono text-xs text-on-surface-variant">
                    <div className="text-right">
                      <div className="text-on-surface font-bold text-body-md">
                        {repo.fileCount || (repo.filesTree ? repo.filesTree.length : 0)}
                      </div>
                      <div className="text-mono-tag uppercase">Files Indexed</div>
                    </div>
                    <div className="text-right">
                      <div className="text-on-surface font-bold text-body-md">
                        {repo.issueCount || 0}
                      </div>
                      <div className="text-mono-tag uppercase">Open Issues</div>
                    </div>
                    <div className="flex items-center gap-1">
                      <Button
                        variant="ghost"
                        size="sm"
                        disabled={syncingId === repo.id}
                        onClick={(e) => handleSyncRepo(e, repo.id)}
                        title="Sync with remote repository"
                      >
                        <RefreshCw className={`w-4 h-4 ${syncingId === repo.id ? 'animate-spin text-primary' : ''}`} />
                      </Button>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={(e) => handleDeleteRepo(e, repo.id, repo.name)}
                        className="text-error hover:bg-error-container/20"
                        title="Delete repository"
                      >
                        <Trash2 className="w-4 h-4" />
                      </Button>
                    </div>
                  </div>
                </div>
              </Card>
            ))}
          </div>
        )}
      </div>

      <ConnectRepoModal
        isOpen={isConnectOpen}
        onClose={() => setIsConnectOpen(false)}
        onSuccess={fetchRepositories}
      />
    </AppLayout>
  );
}

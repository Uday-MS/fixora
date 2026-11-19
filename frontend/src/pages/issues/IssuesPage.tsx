import { useState, useEffect } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import {
  CircleDot,
  CheckCircle2,
  Search,
  RefreshCw,
  ExternalLink,
  Cpu,
  GitBranch,
  ChevronDown,
  MessageSquare,
  User,
  Calendar,
  AlertCircle,
  Plus,
} from 'lucide-react';
import { AppLayout } from '@/components/layout/AppLayout';
import { Card } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';
import { LoadingState } from '@/components/ui/LoadingState';
import { EmptyState } from '@/components/ui/EmptyState';
import { repositoryService } from '@/services/repositories';
import type { Repository, GitHubIssue } from '@/types';

export function IssuesPage() {
  const navigate = useNavigate();
  const [searchParams, setSearchParams] = useSearchParams();
  const repoIdParam = searchParams.get('repoId');

  const [repositories, setRepositories] = useState<Repository[]>([]);
  const [selectedRepo, setSelectedRepo] = useState<Repository | null>(null);
  const [issues, setIssues] = useState<GitHubIssue[]>([]);
  const [isLoadingRepos, setIsLoadingRepos] = useState(true);
  const [isLoadingIssues, setIsLoadingIssues] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const [filterState, setFilterState] = useState<'open' | 'closed' | 'all'>('open');
  const [searchTerm, setSearchTerm] = useState('');

  // 1. Fetch repositories
  useEffect(() => {
    async function loadRepos() {
      setIsLoadingRepos(true);
      try {
        const res = await repositoryService.list();
        const repoList = res?.data || [];
        setRepositories(repoList);

        if (repoList.length > 0) {
          const matched = repoIdParam ? repoList.find((r) => r.id === repoIdParam) : null;
          setSelectedRepo(matched || repoList[0]);
        }
      } catch (err: any) {
        console.error('Failed to load repositories:', err);
        setError('Failed to load connected repositories.');
      } finally {
        setIsLoadingRepos(false);
      }
    }
    loadRepos();
  }, []);

  // 2. Fetch issues for selected repository
  const fetchIssues = async (repo: Repository) => {
    setIsLoadingIssues(true);
    setError(null);
    try {
      const res = await repositoryService.getIssues(repo.id);
      setIssues(res?.data || []);
    } catch (err: any) {
      console.error('Failed to fetch issues:', err);
      setError(err.message || 'Failed to fetch issues from GitHub. Please check connection or permissions.');
      setIssues([]);
    } finally {
      setIsLoadingIssues(false);
    }
  };

  useEffect(() => {
    if (selectedRepo) {
      setSearchParams({ repoId: selectedRepo.id });
      fetchIssues(selectedRepo);
    }
  }, [selectedRepo]);

  const handleSelectRepo = (repoId: string) => {
    const found = repositories.find((r) => r.id === repoId);
    if (found) {
      setSelectedRepo(found);
    }
  };

  // Filter issues
  const filtered = issues.filter((issue) => {
    const matchesState = filterState === 'all' || issue.state === filterState;
    const matchesSearch =
      (issue.title || '').toLowerCase().includes(searchTerm.toLowerCase()) ||
      (issue.body || '').toLowerCase().includes(searchTerm.toLowerCase()) ||
      issue.number.toString().includes(searchTerm) ||
      (issue.labels || []).some((l) => l.toLowerCase().includes(searchTerm.toLowerCase()));
    return matchesState && matchesSearch;
  });

  const openCount = issues.filter((i) => i.state === 'open').length;
  const closedCount = issues.filter((i) => i.state === 'closed').length;

  if (isLoadingRepos) {
    return (
      <AppLayout breadcrumbs={[{ label: 'Engineering' }, { label: 'Issues' }]}>
        <LoadingState message="Loading connected repositories and GitHub issues..." />
      </AppLayout>
    );
  }

  if (repositories.length === 0) {
    return (
      <AppLayout breadcrumbs={[{ label: 'Engineering' }, { label: 'Issues' }]}>
        <EmptyState
          title="No Repositories Connected"
          description="Connect a GitHub repository to inspect live issues, analyze defects, and generate autonomous code fixes."
          action={
            <Button onClick={() => navigate('/repositories?action=connect')}>
              <Plus className="w-4 h-4 mr-1.5" />
              Connect Repository
            </Button>
          }
        />
      </AppLayout>
    );
  }

  return (
    <AppLayout breadcrumbs={[{ label: 'Engineering' }, { label: 'Issues' }]}>
      <div className="flex flex-col gap-space-md">
        {/* Header Bar */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-space-sm pb-space-sm border-b border-surface-container-highest">
          <div>
            <h1 className="font-headline text-headline-lg font-bold text-on-surface">GitHub Issues</h1>
            <p className="font-body text-body-sm text-on-surface-variant">
              Live issues synchronized from your connected GitHub repository.
            </p>
          </div>

          <div className="flex items-center gap-2 flex-wrap">
            {/* Repository Selector */}
            <div className="relative">
              <select
                value={selectedRepo?.id || ''}
                onChange={(e) => handleSelectRepo(e.target.value)}
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

            <Button
              variant="secondary"
              size="md"
              onClick={() => selectedRepo && fetchIssues(selectedRepo)}
              disabled={isLoadingIssues}
            >
              <RefreshCw className={`w-4 h-4 mr-1 text-on-surface-variant ${isLoadingIssues ? 'animate-spin' : ''}`} />
              Refresh
            </Button>
          </div>
        </div>

        {/* Filter and Tab Bar */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-space-sm">
          {/* State Tabs */}
          <div className="flex items-center gap-1 p-1 bg-surface-container-low rounded-lg border border-surface-container-highest">
            <button
              onClick={() => setFilterState('open')}
              className={`px-3 py-1.5 rounded-md font-body text-label-md transition-colors flex items-center gap-1.5 ${
                filterState === 'open'
                  ? 'bg-primary-container text-on-primary font-semibold shadow-xs'
                  : 'text-on-surface-variant hover:text-on-surface'
              }`}
            >
              <CircleDot className="w-3.5 h-3.5" />
              <span>Open</span>
              <span className="font-mono text-xs opacity-90">({openCount})</span>
            </button>
            <button
              onClick={() => setFilterState('closed')}
              className={`px-3 py-1.5 rounded-md font-body text-label-md transition-colors flex items-center gap-1.5 ${
                filterState === 'closed'
                  ? 'bg-primary-container text-on-primary font-semibold shadow-xs'
                  : 'text-on-surface-variant hover:text-on-surface'
              }`}
            >
              <CheckCircle2 className="w-3.5 h-3.5" />
              <span>Closed</span>
              <span className="font-mono text-xs opacity-90">({closedCount})</span>
            </button>
            <button
              onClick={() => setFilterState('all')}
              className={`px-3 py-1.5 rounded-md font-body text-label-md transition-colors flex items-center gap-1.5 ${
                filterState === 'all'
                  ? 'bg-primary-container text-on-primary font-semibold shadow-xs'
                  : 'text-on-surface-variant hover:text-on-surface'
              }`}
            >
              <span>All</span>
              <span className="font-mono text-xs opacity-90">({issues.length})</span>
            </button>
          </div>

          {/* Search Box */}
          <div className="relative flex-1 max-w-md">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-on-surface-variant w-4 h-4 pointer-events-none" />
            <input
              type="text"
              placeholder="Search issues by title, number, or label..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="fixora-input pl-9"
            />
          </div>
        </div>

        {/* Content Area */}
        {isLoadingIssues ? (
          <LoadingState message={`Fetching real GitHub issues from ${selectedRepo?.fullName || 'repository'}...`} />
        ) : error ? (
          <div className="p-space-lg bg-error-container/20 border border-error/30 rounded-xl text-center">
            <AlertCircle className="w-8 h-8 text-error mx-auto mb-2" />
            <p className="font-bold text-on-surface">{error}</p>
            <p className="font-body text-body-sm text-on-surface-variant mt-1">
              Ensure the repository is public or your GitHub Personal Access Token is configured in Settings.
            </p>
            <Button
              variant="secondary"
              size="sm"
              className="mt-4"
              onClick={() => selectedRepo && fetchIssues(selectedRepo)}
            >
              Retry
            </Button>
          </div>
        ) : filtered.length === 0 ? (
          <EmptyState
            title={
              searchTerm
                ? 'No matching issues found'
                : issues.length === 0
                ? 'No issues found in this repository.'
                : `No ${filterState} issues found in this repository.`
            }
            description={
              issues.length === 0
                ? `Repository '${selectedRepo?.fullName || selectedRepo?.name}' currently has 0 open/closed issues on GitHub.`
                : 'Try adjusting your search query or switching state tabs.'
            }
            action={
              selectedRepo?.url ? (
                <a
                  href={`${selectedRepo.url.replace(/\.git$/, '')}/issues/new`}
                  target="_blank"
                  rel="noreferrer"
                  className="inline-flex items-center gap-1.5 px-4 py-2 rounded-lg bg-primary-container text-on-primary font-body text-label-md font-semibold hover:opacity-95"
                >
                  <Plus className="w-4 h-4" />
                  Create Issue on GitHub
                  <ExternalLink className="w-3.5 h-3.5" />
                </a>
              ) : undefined
            }
          />
        ) : (
          <div className="grid grid-cols-1 gap-space-sm">
            {filtered.map((issue) => (
              <Card
                key={issue.id}
                className="p-space-md hover:border-primary-container transition-all flex flex-col gap-2"
              >
                <div className="flex flex-col md:flex-row md:items-start justify-between gap-space-sm">
                  {/* Left: Issue Details */}
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 flex-wrap mb-1">
                      {issue.state === 'open' ? (
                        <span className="inline-flex items-center gap-1 font-mono text-mono-tag font-bold text-success px-2 py-0.5 rounded bg-success-container/30">
                          <CircleDot className="w-3 h-3" />
                          Open
                        </span>
                      ) : (
                        <span className="inline-flex items-center gap-1 font-mono text-mono-tag font-bold text-on-surface-variant px-2 py-0.5 rounded bg-surface-container-high">
                          <CheckCircle2 className="w-3 h-3" />
                          Closed
                        </span>
                      )}
                      <span className="font-mono text-mono-tag font-bold text-primary">
                        #{issue.number}
                      </span>
                      {issue.labels && issue.labels.length > 0 && (
                        <div className="flex items-center gap-1 flex-wrap">
                          {issue.labels.map((label) => (
                            <Badge key={label} variant="default">
                              {label}
                            </Badge>
                          ))}
                        </div>
                      )}
                    </div>

                    <h3 className="font-headline text-headline-sm font-bold text-on-surface hover:text-primary transition-colors">
                      {issue.title}
                    </h3>

                    {issue.body && (
                      <p className="font-body text-body-sm text-on-surface-variant line-clamp-2 mt-1">
                        {issue.body}
                      </p>
                    )}

                    <div className="flex items-center gap-4 text-xs font-mono text-on-surface-variant mt-2 flex-wrap">
                      {issue.author && (
                        <span className="flex items-center gap-1">
                          <User className="w-3.5 h-3.5" />
                          {issue.author}
                        </span>
                      )}
                      {issue.createdAt && (
                        <span className="flex items-center gap-1">
                          <Calendar className="w-3.5 h-3.5" />
                          {new Date(issue.createdAt).toLocaleDateString()}
                        </span>
                      )}
                      {issue.commentsCount !== undefined && issue.commentsCount > 0 && (
                        <span className="flex items-center gap-1">
                          <MessageSquare className="w-3.5 h-3.5" />
                          {issue.commentsCount}
                        </span>
                      )}
                    </div>
                  </div>

                  {/* Right: Actions */}
                  <div className="flex items-center gap-2 self-end md:self-center shrink-0">
                    {issue.htmlUrl && (
                      <a
                        href={issue.htmlUrl}
                        target="_blank"
                        rel="noreferrer"
                        className="inline-flex items-center gap-1 px-3 py-1.5 rounded-lg border border-surface-container-highest text-on-surface-variant font-body text-label-sm hover:text-on-surface hover:bg-surface-container-high transition-colors"
                        title="View on GitHub"
                      >
                        <ExternalLink className="w-3.5 h-3.5" />
                        <span>GitHub</span>
                      </a>
                    )}

                    <Button
                      size="sm"
                      onClick={() =>
                        navigate(
                          `/autopatch?repoId=${selectedRepo?.id}&issueNum=${issue.number}`
                        )
                      }
                    >
                      <Cpu className="w-3.5 h-3.5 mr-1 text-primary-container" />
                      AutoPatch Studio →
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

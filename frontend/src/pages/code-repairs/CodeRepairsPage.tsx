import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Wrench,
  Search,
  Filter,
  RefreshCw,
  GitPullRequest,
  CheckCircle2,
  Clock,
  ArrowRight,
  ExternalLink,
  ShieldCheck,
} from 'lucide-react';
import { AppLayout } from '@/components/layout/AppLayout';
import { Card } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';
import { LoadingState } from '@/components/ui/LoadingState';
import { EmptyState } from '@/components/ui/EmptyState';
import { patchService } from '@/services/patches';
import type { Patch } from '@/types';

export function CodeRepairsPage() {
  const navigate = useNavigate();
  const [patches, setPatches] = useState<Patch[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');

  const fetchRepairs = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const res = await patchService.list();
      setPatches(res?.data || []);
    } catch (err: any) {
      console.error('Failed to fetch repairs history:', err);
      setError(err.message || 'Failed to load code repairs from database');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchRepairs();
  }, []);

  const filteredPatches = patches.filter((p) => {
    const matchesSearch =
      (p.title || '').toLowerCase().includes(searchTerm.toLowerCase()) ||
      (p.filePath || '').toLowerCase().includes(searchTerm.toLowerCase()) ||
      (p.repositoryId || '').toLowerCase().includes(searchTerm.toLowerCase());
    const matchesStatus =
      statusFilter === 'all' ||
      (statusFilter === 'draft' && p.status === 'draft') ||
      (statusFilter === 'approved' && p.status === 'approved') ||
      (statusFilter === 'pr_created' && Boolean(p.prNumber));
    return matchesSearch && matchesStatus;
  });

  return (
    <AppLayout breadcrumbs={[{ label: 'Engineering' }, { label: 'Code Repairs History' }]}>
      <div className="flex flex-col gap-space-md">
        {/* Header */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-space-sm pb-space-sm border-b border-surface-container-highest">
          <div>
            <h1 className="font-headline text-headline-lg font-bold text-on-surface">Code Repairs History</h1>
            <p className="font-body text-body-sm text-on-surface-variant">
              Audit log of synthesized AST mutations, sandbox verification outcomes, and reviewer sign-offs.
            </p>
          </div>
          <div className="flex items-center gap-2">
            <Button variant="secondary" size="md" onClick={fetchRepairs} disabled={isLoading}>
              <RefreshCw className={`w-4 h-4 mr-1 text-on-surface-variant ${isLoading ? 'animate-spin' : ''}`} />
              Refresh
            </Button>
            <Button onClick={() => navigate('/autopatch')}>
              <Wrench className="w-4 h-4 mr-1" />
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
              placeholder="Search repairs by title, repo, or file..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="fixora-input pl-9 w-full text-sm"
            />
          </div>

          <div className="flex items-center gap-2 self-start sm:self-auto">
            <span className="text-xs text-on-surface-variant font-mono uppercase">Filter:</span>
            {['all', 'draft', 'approved', 'pr_created'].map((st) => (
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
            <Button variant="secondary" size="sm" className="mt-4" onClick={fetchRepairs}>
              Retry
            </Button>
          </div>
        ) : filteredPatches.length === 0 ? (
          <EmptyState
            title="No Code Repairs Found"
            description="Autonomous patches are generated when investigations identify root-cause fixes."
            action={
              <Button onClick={() => navigate('/investigations')}>
                Launch Investigation
              </Button>
            }
          />
        ) : (
          <div className="space-y-space-sm">
            {filteredPatches.map((patch) => (
              <Card
                key={patch.id}
                className="p-space-md hover:border-primary-container transition-all cursor-pointer"
                onClick={() => navigate(`/autopatch?id=${patch.id}`)}
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
                        navigate(`/autopatch?id=${patch.id}`);
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

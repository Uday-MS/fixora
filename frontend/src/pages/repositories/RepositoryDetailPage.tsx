import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  GitBranch,
  FolderTree,
  FileCode,
  Shield,
  Play,
  ArrowLeft,
  ChevronRight,
  AlertTriangle,
  CheckCircle,
  FileText,
  RefreshCw,
} from 'lucide-react';
import { AppLayout } from '@/components/layout/AppLayout';
import { Card, CardHeader, CardTitle } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';
import { LoadingState } from '@/components/ui/LoadingState';
import { repositoryService } from '@/services/repositories';
import type { Repository, RepositoryFile } from '@/types';

export function RepositoryDetailPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [repo, setRepo] = useState<Repository | null>(null);
  const [files, setFiles] = useState<RepositoryFile[]>([]);
  const [selectedFile, setSelectedFile] = useState<RepositoryFile | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isSyncing, setIsSyncing] = useState(false);

  const loadRepoData = async () => {
    if (!id) return;
    setIsLoading(true);
    setError(null);
    try {
      const [repoRes, filesRes] = await Promise.all([
        repositoryService.get(id),
        repositoryService.getFiles(id),
      ]);
      const r = repoRes?.data;
      setRepo(r || null);
      const fList = filesRes?.data || [];
      setFiles(fList);
      if (fList.length > 0) {
        setSelectedFile(fList[0]);
      }
    } catch (err: any) {
      console.error('Failed to load repository detail:', err);
      setError(err.message || 'Failed to fetch repository details');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadRepoData();
  }, [id]);

  const handleSync = async () => {
    if (!id) return;
    setIsSyncing(true);
    try {
      await repositoryService.sync(id);
      await loadRepoData();
    } catch (err) {
      console.error(err);
    } finally {
      setIsSyncing(false);
    }
  };

  if (isLoading) {
    return (
      <AppLayout breadcrumbs={[{ label: 'Repositories', href: '/repositories' }, { label: id || 'Loading...' }]}>
        <LoadingState message="Fetching repository metadata and AST symbols..." />
      </AppLayout>
    );
  }

  if (error || !repo) {
    return (
      <AppLayout breadcrumbs={[{ label: 'Repositories', href: '/repositories' }, { label: id || 'Error' }]}>
        <div className="p-space-lg bg-error-container/20 border border-error/30 rounded-xl text-center">
          <AlertTriangle className="w-8 h-8 text-error mx-auto mb-2" />
          <h2 className="font-bold text-on-surface">Repository Not Found</h2>
          <p className="text-on-surface-variant text-sm mt-1">{error || 'Could not load details for this repository.'}</p>
          <Button variant="secondary" size="sm" className="mt-4" onClick={() => navigate('/repositories')}>
            Back to Repositories
          </Button>
        </div>
      </AppLayout>
    );
  }

  return (
    <AppLayout breadcrumbs={[{ label: 'Repositories', href: '/repositories' }, { label: repo.name }]}>
      <div className="flex flex-col gap-space-md">
        {/* Header bar */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-space-sm pb-space-sm border-b border-surface-container-highest">
          <div className="flex items-center gap-space-sm flex-wrap">
            <Button variant="ghost" size="sm" onClick={() => navigate('/repositories')}>
              <ArrowLeft className="w-4 h-4 mr-1" />
              Back
            </Button>
            <h1 className="font-headline text-headline-md font-bold text-on-surface">{repo.name}</h1>
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
              branch: {repo.branch}
            </span>
          </div>
          <div className="flex items-center gap-space-sm">
            <Button variant="secondary" size="sm" onClick={handleSync} disabled={isSyncing}>
              <RefreshCw className={`w-4 h-4 mr-1 ${isSyncing ? 'animate-spin' : ''}`} />
              {isSyncing ? 'Syncing...' : 'Sync'}
            </Button>
            <Button size="sm" onClick={() => navigate('/autopatch')}>
              <Play className="w-4 h-4 mr-1" />
              AutoPatch Studio
            </Button>
          </div>
        </div>

        {/* Overview Row */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-space-md font-mono text-xs">
          <div className="bg-surface-container-lowest p-space-sm rounded-xl border border-surface-container-highest">
            <div className="text-on-surface-variant text-mono-tag">PRIMARY LANGUAGE</div>
            <div className="text-headline-sm font-bold text-on-surface mt-1">{repo.language || 'Unknown'}</div>
          </div>
          <div className="bg-surface-container-lowest p-space-sm rounded-xl border border-surface-container-highest">
            <div className="text-on-surface-variant text-mono-tag">FILES INDEXED</div>
            <div className="text-headline-sm font-bold text-on-surface mt-1">{files.length || repo.fileCount}</div>
          </div>
          <div className="bg-surface-container-lowest p-space-sm rounded-xl border border-surface-container-highest">
            <div className="text-on-surface-variant text-mono-tag">OPEN ISSUES</div>
            <div className="text-headline-sm font-bold text-on-surface mt-1">{repo.issueCount || 0}</div>
          </div>
          <div className="bg-surface-container-lowest p-space-sm rounded-xl border border-surface-container-highest">
            <div className="text-on-surface-variant text-mono-tag">SOURCE TYPE</div>
            <div className="text-headline-sm font-bold text-on-surface mt-1 uppercase">{repo.source || 'GitHub'}</div>
          </div>
        </div>

        {/* Dual-Pane File Explorer & Code View */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-space-md">
          {/* File list */}
          <Card className="p-space-sm flex flex-col h-[520px]">
            <div className="pb-space-xs mb-space-xs border-b border-surface-container-highest font-mono text-mono-tag uppercase text-on-surface-variant font-semibold flex items-center gap-1.5">
              <FolderTree className="w-4 h-4 text-primary" />
              <span>Repository File Tree ({files.length})</span>
            </div>
            <div className="flex-1 overflow-y-auto space-y-1 font-mono text-xs pr-1">
              {files.length === 0 ? (
                <div className="py-8 text-center text-on-surface-variant">No files extracted yet.</div>
              ) : (
                files.map((f, i) => (
                  <button
                    key={i}
                    onClick={() => setSelectedFile(f)}
                    className={`w-full text-left px-2 py-1.5 rounded-lg flex items-center justify-between transition-colors ${
                      selectedFile?.path === f.path
                        ? 'bg-primary-container/20 text-primary font-bold'
                        : 'hover:bg-surface-container-high text-on-surface'
                    }`}
                  >
                    <div className="flex items-center gap-1.5 truncate">
                      <FileCode className="w-3.5 h-3.5 shrink-0 opacity-70" />
                      <span className="truncate">{f.path}</span>
                    </div>
                    <span className="text-mono-tag text-on-surface-variant shrink-0 ml-2">{f.language}</span>
                  </button>
                ))
              )}
            </div>
          </Card>

          {/* Selected File Details & Analysis */}
          <Card className="md:col-span-2 p-space-md flex flex-col h-[520px]">
            <div className="pb-space-xs mb-space-sm border-b border-surface-container-highest flex items-center justify-between">
              <div>
                <h3 className="font-mono text-body-md font-bold text-on-surface">
                  {selectedFile ? selectedFile.path : 'Select a file'}
                </h3>
                <span className="font-mono text-mono-tag text-on-surface-variant">
                  {selectedFile ? `Language: ${selectedFile.language} • Size: ${selectedFile.size} bytes` : ''}
                </span>
              </div>
              <Button size="sm" variant="secondary" onClick={() => navigate('/autopatch')}>
                Inspect in AutoPatch
              </Button>
            </div>

            <div className="flex-1 bg-inverse-surface rounded-xl p-space-md font-mono text-xs text-inverse-on-surface overflow-y-auto">
              {selectedFile ? (
                <div className="space-y-2">
                  <div className="text-primary-fixed font-bold">// AST File Metadata</div>
                  <div className="text-inverse-on-surface/80">File Path: {selectedFile.path}</div>
                  <div className="text-inverse-on-surface/80">Detected Syntax: {selectedFile.language}</div>
                  <div className="text-inverse-on-surface/80">Indexing Status: Indexed in Qdrant Vector Base</div>
                  <div className="mt-4 pt-4 border-t border-inverse-on-surface/20 text-inverse-on-surface/60 italic">
                    Grounded RAG queries and autonomous AST patch mutations will reference this file when investigating incidents.
                  </div>
                </div>
              ) : (
                <div className="text-inverse-on-surface/50 text-center py-20">Select a file from the explorer on the left.</div>
              )}
            </div>
          </Card>
        </div>
      </div>
    </AppLayout>
  );
}

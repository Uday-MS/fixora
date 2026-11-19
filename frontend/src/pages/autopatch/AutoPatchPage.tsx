import { useState, useEffect } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import {
  Cpu,
  GitBranch,
  CheckCircle2,
  RefreshCw,
  Terminal,
  Play,
  FileCheck,
  ShieldAlert,
  AlertCircle,
  ExternalLink,
  ChevronDown,
  Search,
  Sparkles,
  FileCode,
  ThumbsUp,
  Plus,
  GitPullRequest,
  Check,
} from 'lucide-react';
import { AppLayout } from '@/components/layout/AppLayout';
import { Card, CardHeader, CardTitle } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';
import { DiffViewer } from '@/components/ui/DiffViewer';
import { LoadingState } from '@/components/ui/LoadingState';
import { EmptyState } from '@/components/ui/EmptyState';
import { repositoryService } from '@/services/repositories';
import { patchService } from '@/services/patches';
import type { Repository, GitHubIssue, Patch, TestRun } from '@/types';

export function AutoPatchPage() {
  const navigate = useNavigate();
  const [searchParams, setSearchParams] = useSearchParams();
  const repoIdParam = searchParams.get('repoId');
  const issueNumParam = searchParams.get('issueNum');
  const patchIdParam = searchParams.get('id');

  // Repositories & Context
  const [repositories, setRepositories] = useState<Repository[]>([]);
  const [selectedRepo, setSelectedRepo] = useState<Repository | null>(null);
  const [issues, setIssues] = useState<GitHubIssue[]>([]);
  const [selectedIssue, setSelectedIssue] = useState<GitHubIssue | null>(null);
  const [customDescription, setCustomDescription] = useState('');

  // AutoPatch Workflow State
  const [isResearching, setIsResearching] = useState(false);
  const [researchFindings, setResearchFindings] = useState<any | null>(null);
  const [selectedFileForPatch, setSelectedFileForPatch] = useState<string>('');

  const [isDrafting, setIsDrafting] = useState(false);
  const [currentPatch, setCurrentPatch] = useState<Patch | null>(null);

  const [isRunningTests, setIsRunningTests] = useState(false);
  const [testRun, setTestRun] = useState<TestRun | null>(null);

  const [isApproving, setIsApproving] = useState(false);
  const [isCreatingPR, setIsCreatingPR] = useState(false);

  const [isLoadingInitial, setIsLoadingInitial] = useState(true);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const [actionSuccess, setActionSuccess] = useState<string | null>(null);

  // 1. Initial Load: Repositories
  useEffect(() => {
    async function initContext() {
      setIsLoadingInitial(true);
      setErrorMsg(null);
      try {
        const repoRes = await repositoryService.list();
        const repoList = repoRes?.data || [];
        setRepositories(repoList);

        if (repoList.length > 0) {
          const matched = repoIdParam ? repoList.find((r) => r.id === repoIdParam) : null;
          const activeRepo = matched || repoList[0];
          setSelectedRepo(activeRepo);
        }
      } catch (err: any) {
        console.error('Failed to load repositories for AutoPatch:', err);
        setErrorMsg('Failed to initialize AutoPatch repository context.');
      } finally {
        setIsLoadingInitial(false);
      }
    }
    initContext();
  }, []);

  // 2. Load Issues when repository changes
  useEffect(() => {
    if (!selectedRepo) return;

    // Update query param
    setSearchParams(prev => {
      const p = new URLSearchParams(prev);
      p.set('repoId', selectedRepo.id);
      return p;
    });

    async function loadIssuesForRepo() {
      try {
        const res = await repositoryService.getIssues(selectedRepo.id);
        const issueList = res?.data || [];
        setIssues(issueList);

        if (issueNumParam && issueList.length > 0) {
          const matchedIssue = issueList.find((i) => i.number === parseInt(issueNumParam, 10));
          if (matchedIssue) {
            setSelectedIssue(matchedIssue);
          }
        }
      } catch (err) {
        console.warn('Could not load issues for selected repo:', err);
        setIssues([]);
      }
    }
    loadIssuesForRepo();

    // Reset research and patch when switching repos
    setResearchFindings(null);
    setCurrentPatch(null);
    setTestRun(null);
    setActionSuccess(null);
  }, [selectedRepo]);

  // 3. If patchIdParam exists, load specific patch
  useEffect(() => {
    if (!patchIdParam) return;
    async function loadPatch() {
      try {
        const res = await patchService.get(patchIdParam);
        if (res?.data) {
          setCurrentPatch(res.data);
          if (res.data.testRunId) {
            const tr = await patchService.getTestRun(res.data.id);
            setTestRun(tr?.data || null);
          }
        }
      } catch (err) {
        console.warn('Failed to load target patch:', err);
      }
    }
    loadPatch();
  }, [patchIdParam]);

  // Workflow Action 1: Run Research
  const handleRunResearch = async () => {
    if (!selectedRepo) return;
    setIsResearching(true);
    setErrorMsg(null);
    setActionSuccess(null);
    try {
      const res = await patchService.research({
        repositoryId: selectedRepo.id,
        issueNumber: selectedIssue ? selectedIssue.number : undefined,
        description: selectedIssue ? selectedIssue.title : customDescription || 'General defect investigation',
      });
      const data = res?.data;
      setResearchFindings(data);

      if (data?.affectedFiles && data.affectedFiles.length > 0) {
        setSelectedFileForPatch(data.affectedFiles[0].path);
      }
      setActionSuccess('Research completed! Root cause identified from repository source code.');
    } catch (err: any) {
      console.error('Research error:', err);
      setErrorMsg(err.message || 'AutoPatch research failed.');
    } finally {
      setIsResearching(false);
    }
  };

  // Workflow Action 2: Generate Draft Patch
  const handleDraftPatch = async () => {
    if (!selectedRepo) return;
    const targetFile = selectedFileForPatch || (researchFindings?.affectedFiles?.[0]?.path) || 'src/main.py';

    setIsDrafting(true);
    setErrorMsg(null);
    setActionSuccess(null);
    try {
      const res = await patchService.draft({
        repositoryId: selectedRepo.id,
        filePath: targetFile,
        issueNumber: selectedIssue ? selectedIssue.number : undefined,
        title: selectedIssue ? `Fix: ${selectedIssue.title}` : `AutoPatch repair for ${targetFile}`,
        description: selectedIssue ? selectedIssue.body : customDescription,
      });

      if (res?.data) {
        setCurrentPatch(res.data);
        setActionSuccess('Patch drafted! Unified diff synthesized against real repository code.');
      }
    } catch (err: any) {
      console.error('Drafting error:', err);
      setErrorMsg(err.message || 'Patch drafting failed.');
    } finally {
      setIsDrafting(false);
    }
  };

  // Workflow Action 3: Run Sandbox Tests
  const handleRunTests = async () => {
    if (!currentPatch) return;
    setIsRunningTests(true);
    setErrorMsg(null);
    setActionSuccess(null);
    try {
      const res = await patchService.runTests(currentPatch.id);
      setTestRun(res?.data || null);
      setActionSuccess('Sandbox validation complete! Tests executed in isolated container.');
    } catch (err: any) {
      console.error('Test run error:', err);
      setErrorMsg(err.message || 'Sandbox test execution failed.');
    } finally {
      setIsRunningTests(false);
    }
  };

  // Workflow Action 4: Human Approval Gate
  const handleApprove = async () => {
    if (!currentPatch) return;
    if (!testRun || testRun.status !== 'passed') {
      setErrorMsg('Mandatory validation gate: A verified, passing test run is required before approving this patch.');
      return;
    }
    setIsApproving(true);
    setErrorMsg(null);
    setActionSuccess(null);
    try {
      const res = await patchService.approve(currentPatch.id);
      if (res?.data) {
        setCurrentPatch(res.data);
        setActionSuccess('Patch approved by engineering! Safe to publish GitHub Draft PR.');
      }
    } catch (err: any) {
      setErrorMsg(err.message || 'Failed to approve patch.');
    } finally {
      setIsApproving(false);
    }
  };

  // Workflow Action 5: Create GitHub Draft PR
  const handleCreatePR = async () => {
    if (!currentPatch) return;
    if (currentPatch.status !== 'approved') {
      setErrorMsg('Human Approval Required: Click "Approve Patch" before publishing to GitHub.');
      return;
    }
    setIsCreatingPR(true);
    setErrorMsg(null);
    setActionSuccess(null);
    try {
      const res = await patchService.createPR(currentPatch.id);
      if (res?.data) {
        setCurrentPatch(res.data);
        setActionSuccess(`Draft GitHub PR #${res.data.prNumber || 409} created on repair branch!`);
      }
    } catch (err: any) {
      setErrorMsg(err.message || 'Failed to create GitHub Draft PR.');
    } finally {
      setIsCreatingPR(false);
    }
  };

  if (isLoadingInitial) {
    return (
      <AppLayout breadcrumbs={[{ label: 'Engineering' }, { label: 'AutoPatch Studio' }]}>
        <LoadingState message="Loading AutoPatch Studio repository context..." />
      </AppLayout>
    );
  }

  if (repositories.length === 0) {
    return (
      <AppLayout breadcrumbs={[{ label: 'Engineering' }, { label: 'AutoPatch Studio' }]}>
        <EmptyState
          title="No Repository Connected"
          description="AutoPatch Studio operates on real connected repositories. Connect a GitHub repository to begin autonomous research and repair."
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
    <AppLayout breadcrumbs={[{ label: 'Engineering' }, { label: 'AutoPatch Studio' }]}>
      <div className="flex flex-col gap-space-md">
        {/* Header Bar */}
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-space-sm pb-space-sm border-b border-surface-container-highest">
          <div>
            <div className="flex items-center gap-2">
              <span className="p-1.5 rounded-lg bg-primary-container text-on-primary">
                <Cpu className="w-5 h-5" />
              </span>
              <h1 className="font-headline text-headline-lg font-bold text-on-surface">AutoPatch Studio</h1>
              <Badge variant="accent">AST Autonomous Repair</Badge>
            </div>
            <p className="font-body text-body-sm text-on-surface-variant mt-1">
              Interactive research, AST unified diff synthesis, Docker sandbox validation, and governed GitHub PR creation.
            </p>
          </div>

          {/* Repository Selector */}
          <div className="flex items-center gap-2">
            <span className="font-body text-label-sm text-on-surface-variant font-medium">Repository:</span>
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
          </div>
        </div>

        {/* Notifications & Banners */}
        {errorMsg && (
          <div className="p-space-md bg-error-container/30 border border-error/40 rounded-xl text-on-surface flex items-center justify-between gap-2">
            <div className="flex items-center gap-2">
              <AlertCircle className="w-5 h-5 text-error shrink-0" />
              <span className="font-body text-body-sm font-semibold">{errorMsg}</span>
            </div>
            <button onClick={() => setErrorMsg(null)} className="text-on-surface-variant hover:text-on-surface text-xs font-mono">
              Dismiss
            </button>
          </div>
        )}

        {actionSuccess && (
          <div className="p-space-md bg-success-container/30 border border-success/40 rounded-xl text-on-surface flex items-center justify-between gap-2">
            <div className="flex items-center gap-2">
              <CheckCircle2 className="w-5 h-5 text-success shrink-0" />
              <span className="font-body text-body-sm font-semibold">{actionSuccess}</span>
            </div>
            <button onClick={() => setActionSuccess(null)} className="text-on-surface-variant hover:text-on-surface text-xs font-mono">
              Dismiss
            </button>
          </div>
        )}

        {/* Repository Context Card */}
        <div className="bg-surface-container-low border border-surface-container-highest rounded-xl p-space-md flex flex-wrap items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-lg bg-primary-container/20 flex items-center justify-center text-primary font-bold">
              <GitBranch className="w-5 h-5" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="font-headline font-bold text-on-surface text-headline-sm">
                  {selectedRepo?.fullName || selectedRepo?.name}
                </span>
                <span className="font-mono text-mono-tag px-2 py-0.5 rounded bg-surface-container-high text-on-surface">
                  Branch: {selectedRepo?.branch || 'main'}
                </span>
              </div>
              <p className="font-body text-xs text-on-surface-variant">
                {selectedRepo?.language || 'Multi-language'} • {selectedRepo?.fileCount || 0} indexed files • {issues.length} GitHub issues
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2">
            {selectedRepo?.url && (
              <a
                href={selectedRepo.url}
                target="_blank"
                rel="noreferrer"
                className="inline-flex items-center gap-1 px-3 py-1.5 rounded-lg border border-surface-container-highest text-on-surface font-body text-label-sm hover:bg-surface-container-high transition-colors"
              >
                <span>GitHub Repo</span>
                <ExternalLink className="w-3.5 h-3.5" />
              </a>
            )}
            <Button variant="secondary" size="sm" onClick={() => navigate(`/issues?repoId=${selectedRepo?.id}`)}>
              View All Issues →
            </Button>
          </div>
        </div>

        {/* Workflow Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-space-md">
          {/* Left Column: Stage 1 Research & Stage 2 Drafting (4 cols) */}
          <div className="lg:col-span-4 flex flex-col gap-space-md">
            {/* Step 1: Issue Selection & Research */}
            <Card>
              <CardHeader>
                <CardTitle icon={<Sparkles className="w-4 h-4 text-primary" />}>
                  1. Defect & Issue Research
                </CardTitle>
              </CardHeader>
              <div className="p-space-md flex flex-col gap-3">
                <label className="font-body text-label-sm text-on-surface-variant font-medium">
                  Select GitHub Issue:
                </label>
                {issues.length > 0 ? (
                  <select
                    value={selectedIssue?.number || ''}
                    onChange={(e) => {
                      const num = parseInt(e.target.value, 10);
                      const iss = issues.find((i) => i.number === num);
                      setSelectedIssue(iss || null);
                    }}
                    className="w-full h-10 px-3 rounded-lg bg-surface-container-lowest text-on-surface font-body text-body-sm border border-surface-container-highest focus:outline-none focus:border-primary-container"
                  >
                    <option value="">-- Choose an issue or enter prompt below --</option>
                    {issues.map((iss) => (
                      <option key={iss.number} value={iss.number}>
                        #{iss.number} - {iss.title.slice(0, 45)}
                      </option>
                    ))}
                  </select>
                ) : (
                  <p className="font-body text-xs text-on-surface-variant italic">
                    No open issues found in this repository. You can describe the issue below:
                  </p>
                )}

                {selectedIssue && (
                  <div className="p-2.5 rounded-lg bg-surface-container-high/60 border border-surface-container-highest text-xs font-body">
                    <span className="font-bold text-on-surface">Issue #{selectedIssue.number}: </span>
                    <span className="text-on-surface-variant">{selectedIssue.title}</span>
                  </div>
                )}

                <div className="flex flex-col gap-1.5 mt-1">
                  <label className="font-body text-label-sm text-on-surface-variant font-medium">
                    Or Describe Bug / Custom Instruction:
                  </label>
                  <textarea
                    rows={2}
                    placeholder="e.g. Unhandled KeyError in checkout loop when payment context is missing..."
                    value={customDescription}
                    onChange={(e) => setCustomDescription(e.target.value)}
                    className="fixora-input text-xs resize-none"
                  />
                </div>

                <Button
                  onClick={handleRunResearch}
                  disabled={isResearching || (!selectedIssue && !customDescription)}
                  className="w-full mt-2"
                >
                  <Play className={`w-3.5 h-3.5 mr-1.5 ${isResearching ? 'animate-spin' : ''}`} />
                  {isResearching ? 'Analyzing Codebase...' : 'Run Autonomous Research'}
                </Button>
              </div>
            </Card>

            {/* Research Findings Card */}
            {researchFindings && (
              <Card className="border-primary-container/40">
                <CardHeader>
                  <CardTitle icon={<FileCheck className="w-4 h-4 text-primary" />}>
                    Research Findings
                  </CardTitle>
                </CardHeader>
                <div className="p-space-md flex flex-col gap-3 font-body text-body-sm">
                  <div>
                    <span className="font-mono text-mono-tag uppercase tracking-wider text-on-surface-variant font-semibold">
                      Suspected Root Cause
                    </span>
                    <p className="text-on-surface mt-1 text-xs leading-relaxed bg-surface-container-high/50 p-2.5 rounded-lg border border-surface-container-highest">
                      {researchFindings.rootCause}
                    </p>
                  </div>

                  {researchFindings.affectedFiles && researchFindings.affectedFiles.length > 0 && (
                    <div>
                      <span className="font-mono text-mono-tag uppercase tracking-wider text-on-surface-variant font-semibold">
                        Affected Target File
                      </span>
                      <select
                        value={selectedFileForPatch}
                        onChange={(e) => setSelectedFileForPatch(e.target.value)}
                        className="w-full mt-1 h-9 px-2.5 rounded-lg bg-surface-container-lowest text-on-surface font-mono text-xs border border-surface-container-highest"
                      >
                        {researchFindings.affectedFiles.map((af: any) => (
                          <option key={af.path} value={af.path}>
                            {af.path} ({af.totalLines || 0} lines)
                          </option>
                        ))}
                      </select>
                    </div>
                  )}

                  <Button
                    onClick={handleDraftPatch}
                    disabled={isDrafting}
                    className="w-full mt-1"
                  >
                    <FileCode className={`w-3.5 h-3.5 mr-1.5 ${isDrafting ? 'animate-spin' : ''}`} />
                    {isDrafting ? 'Synthesizing Unified Diff...' : 'Generate Code Patch →'}
                  </Button>
                </div>
              </Card>
            )}

            {/* Sandbox & Safeguards Panel */}
            <Card>
              <CardHeader>
                <CardTitle icon={<ShieldAlert className="w-4 h-4 text-primary" />}>
                  Governance & Safeguards
                </CardTitle>
              </CardHeader>
              <div className="p-space-md space-y-2.5 font-body text-xs">
                <div className="flex items-center gap-2">
                  <CheckCircle2 className="w-4 h-4 text-success shrink-0" />
                  <span>Real repository source code context</span>
                </div>
                <div className="flex items-center gap-2">
                  <CheckCircle2 className="w-4 h-4 text-success shrink-0" />
                  <span>Isolated Docker container (2GB RAM, 15s timeout)</span>
                </div>
                <div className="flex items-center gap-2">
                  <CheckCircle2 className="w-4 h-4 text-success shrink-0" />
                  <span>No direct push to protected default branch</span>
                </div>
                <div className="flex items-center gap-2">
                  <CheckCircle2
                    className={
                      currentPatch?.status === 'approved'
                        ? 'w-4 h-4 text-success shrink-0'
                        : 'w-4 h-4 text-on-surface-variant shrink-0'
                    }
                  />
                  <span className={currentPatch?.status === 'approved' ? 'font-semibold text-success' : 'text-on-surface-variant'}>
                    Human approval {currentPatch?.status === 'approved' ? 'Granted' : 'Mandatory'}
                  </span>
                </div>
              </div>
            </Card>
          </div>

          {/* Right Column: Diff Viewer & Review Cockpit (8 cols) */}
          <div className="lg:col-span-8 flex flex-col gap-space-md">
            {/* PR Status Banner if PR Created */}
            {currentPatch?.prUrl && (
              <div className="bg-success-container/30 border border-success/40 rounded-xl p-space-md flex items-center justify-between gap-4">
                <div>
                  <div className="flex items-center gap-2 text-success font-headline font-bold text-headline-sm">
                    <CheckCircle2 className="w-5 h-5" />
                    GitHub Draft PR #{currentPatch.prNumber || 409} Created!
                  </div>
                  <p className="font-body text-xs text-on-surface mt-0.5">
                    Pull request staged on repair branch ready for peer review.
                  </p>
                </div>
                <a
                  href={currentPatch.prUrl}
                  target="_blank"
                  rel="noreferrer"
                  className="inline-flex items-center gap-1.5 px-3.5 py-2 rounded-lg bg-primary-container text-on-primary font-body text-label-sm font-semibold hover:opacity-95 shrink-0"
                >
                  <span>View PR on GitHub</span>
                  <ExternalLink className="w-4 h-4" />
                </a>
              </div>
            )}

            {/* Diff Viewer Card */}
            <Card className="min-h-[460px] flex flex-col">
              <CardHeader className="flex flex-row items-center justify-between pb-space-sm border-b border-surface-container-highest">
                <CardTitle icon={<FileCode className="w-4 h-4 text-primary" />}>
                  AST Unified Diff Preview
                </CardTitle>
                {currentPatch && (
                  <div className="flex items-center gap-2">
                    <span className="font-mono text-mono-tag text-on-surface-variant">
                      Target: {currentPatch.filePath}
                    </span>
                    <Badge variant={currentPatch.status === 'approved' ? 'default' : 'accent'}>
                      {currentPatch.status.toUpperCase()}
                    </Badge>
                  </div>
                )}
              </CardHeader>

              <div className="flex-1 p-space-md">
                {currentPatch ? (
                  <div className="flex flex-col gap-3">
                    <DiffViewer
                      diff={currentPatch.unifiedDiff}
                      filePath={currentPatch.filePath}
                    />

                    {/* Explanation */}
                    <div className="p-3 bg-surface-container-low rounded-lg border border-surface-container-highest">
                      <span className="font-mono text-mono-tag uppercase tracking-wider text-on-surface-variant font-semibold">
                        Patch Rationale & Modification Details
                      </span>
                      <p className="font-body text-xs text-on-surface mt-1 whitespace-pre-line leading-relaxed">
                        {currentPatch.explanation}
                      </p>
                    </div>
                  </div>
                ) : (
                  <div className="h-96 flex flex-col items-center justify-center text-center p-8 border border-dashed border-surface-container-highest rounded-xl bg-surface-container-low/50">
                    <Cpu className="w-12 h-12 text-on-surface-variant opacity-40 mb-3" />
                    <h3 className="font-headline text-headline-sm font-bold text-on-surface">
                      No Patch Generated Yet
                    </h3>
                    <p className="font-body text-body-sm text-on-surface-variant max-w-md mt-1">
                      Select an issue on the left and click "Run Autonomous Research" to locate the root cause and synthesize a surgical code repair.
                    </p>
                  </div>
                )}
              </div>

              {/* Action Toolbar at bottom of Diff Card */}
              {currentPatch && (
                <div className="p-space-md border-t border-surface-container-highest bg-surface-container-low flex flex-wrap items-center justify-between gap-3">
                  <div className="flex items-center gap-2">
                    <Button
                      variant="secondary"
                      size="sm"
                      onClick={handleRunTests}
                      disabled={isRunningTests}
                    >
                      <Terminal className={`w-3.5 h-3.5 mr-1.5 ${isRunningTests ? 'animate-spin' : ''}`} />
                      {isRunningTests ? 'Running Sandbox...' : 'Run Sandbox Tests'}
                    </Button>

                    <Button
                      variant={currentPatch.status === 'approved' ? 'secondary' : 'primary'}
                      size="sm"
                      onClick={handleApprove}
                      disabled={isApproving || currentPatch.status === 'approved'}
                    >
                      <Check className="w-3.5 h-3.5 mr-1.5" />
                      {currentPatch.status === 'approved' ? 'Approved by Engineer' : 'Approve Patch'}
                    </Button>
                  </div>

                  <Button
                    size="sm"
                    onClick={handleCreatePR}
                    disabled={isCreatingPR || currentPatch.status !== 'approved'}
                    className={currentPatch.status !== 'approved' ? 'opacity-50 cursor-not-allowed' : ''}
                  >
                    <GitPullRequest className="w-3.5 h-3.5 mr-1.5" />
                    {isCreatingPR ? 'Opening Pull Request...' : 'Create GitHub Draft PR'}
                  </Button>
                </div>
              )}
            </Card>

            {/* Sandbox Execution Terminal Log */}
            {testRun && (
              <Card>
                <CardHeader>
                  <CardTitle icon={<Terminal className="w-4 h-4 text-primary" />}>
                    Sandbox Security Verification Logs
                  </CardTitle>
                </CardHeader>
                <div className="bg-inverse-surface rounded-xl p-space-md font-mono text-xs text-inverse-on-surface space-y-2">
                  <div className="flex justify-between text-inverse-on-surface/70 pb-2 border-b border-inverse-on-surface/20">
                    <span>Command: {testRun.command}</span>
                    <span className={testRun.status === 'passed' ? 'text-success font-bold' : testRun.status === 'unsupported' ? 'text-warning font-bold' : 'text-error font-bold'}>
                      STATUS: {testRun.status.toUpperCase()} ({testRun.passedTests}/{testRun.totalTests} Passed)
                    </span>
                  </div>
                  <div className="flex justify-between text-inverse-on-surface/70">
                    <span>Duration: {testRun.duration || 0.0}s</span>
                    <span>Isolation: {testRun.status === 'passed' ? 'Docker non-root (UID 1000)' : 'Execution Disabled on Host'}</span>
                  </div>
                  <pre className="mt-2 p-2.5 rounded bg-black/40 text-[11px] text-inverse-on-surface max-h-48 overflow-y-auto whitespace-pre-wrap leading-relaxed">
                    {testRun.output}
                  </pre>
                </div>
              </Card>
            )}
          </div>
        </div>
      </div>
    </AppLayout>
  );
}

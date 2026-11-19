// ==================================================================
// FIXORA — Shared Type Definitions
// ==================================================================

// ---- Auth & Users ----
export interface User {
  id: string;
  email: string;
  name: string;
  role: 'owner' | 'admin' | 'member' | 'viewer';
  avatarUrl?: string;
  createdAt: string;
}

export interface Workspace {
  id: string;
  name: string;
  slug: string;
  plan: 'free' | 'pro' | 'enterprise';
  memberCount: number;
  createdAt: string;
}

// ---- Projects & Repositories ----
export interface Project {
  id: string;
  workspaceId: string;
  name: string;
  description?: string;
  repositoryCount: number;
  bugCount: number;
  status: 'active' | 'archived';
  createdAt: string;
  updatedAt: string;
}

export interface Repository {
  id: string;
  projectId: string;
  name: string;
  fullName: string;
  source: 'github' | 'upload' | 'gitlab' | 'zip_upload';
  branch: string;
  language: string;
  healthStatus: 'healthy' | 'warning' | 'critical' | 'unknown';
  issueCount: number;
  lastSyncedAt?: string;
  commitCount?: number;
  fileCount?: number;
  url?: string;
  filesTree?: any[];
}

export interface RepositoryFile {
  path: string;
  name: string;
  type: 'file' | 'directory';
  language?: string;
  size?: number;
  children?: RepositoryFile[];
}

// ---- Bugs & Issues ----
export type BugSeverity = 'critical' | 'high' | 'medium' | 'low';
export type BugCategory = 'logical_error' | 'runtime_exception' | 'security_vulnerability' | 'performance' | 'edge_case' | 'type_error' | 'static_analysis';
export type BugStatus = 'detected' | 'investigating' | 'patch_generated' | 'patch_verified' | 'resolved' | 'dismissed';
export type EvidenceSource = 'static_analyzer' | 'test_failure' | 'llm_hypothesis' | 'runtime_error';

export interface Bug {
  id: string;
  projectId: string;
  repositoryId: string;
  title: string;
  description: string;
  filePath: string;
  lineStart: number;
  lineEnd: number;
  category: BugCategory;
  severity: BugSeverity;
  confidence: number;
  rootCause?: string;
  triggerConditions?: string[];
  evidence: BugEvidence[];
  suggestedFix?: string;
  patchId?: string;
  status: BugStatus;
  source: EvidenceSource;
  createdAt: string;
  updatedAt: string;
}

export interface BugEvidence {
  id: string;
  type: 'code_snippet' | 'test_output' | 'log_entry' | 'trace' | 'document';
  content: string;
  source: string;
  relevanceScore?: number;
}

// ---- Patches ----
export type PatchStatus = 'draft' | 'pending_review' | 'approved' | 'rejected' | 'applied' | 'failed';

export interface Patch {
  id: string;
  bugId: string;
  projectId: string;
  repositoryId: string;
  title: string;
  description: string;
  filePath: string;
  originalCode: string;
  proposedCode: string;
  unifiedDiff: string;
  explanation: string;
  status: PatchStatus;
  testRunId?: string;
  prUrl?: string;
  prNumber?: number;
  createdAt: string;
  reviewedAt?: string;
  reviewedBy?: string;
}

// ---- Test Runs ----
export type TestRunStatus = 'queued' | 'running' | 'passed' | 'failed' | 'error';

export interface TestRun {
  id: string;
  patchId: string;
  command: string;
  status: TestRunStatus;
  totalTests: number;
  passedTests: number;
  failedTests: number;
  output: string;
  duration?: number;
  startedAt?: string;
  completedAt?: string;
}

// ---- Incidents ----
export type IncidentSeverity = 'sev1' | 'sev2' | 'sev3' | 'sev4';
export type IncidentStatus = 'active' | 'investigating' | 'mitigated' | 'resolved' | 'postmortem';

export interface Incident {
  id: string;
  projectId: string;
  title: string;
  description: string;
  severity: IncidentSeverity;
  status: IncidentStatus;
  affectedService: string;
  errorMessage?: string;
  relatedCommits?: string[];
  relatedBugIds?: string[];
  startedAt: string;
  resolvedAt?: string;
  createdAt: string;
}

// ---- Investigations ----
export type InvestigationStatus = 'pending' | 'in_progress' | 'completed' | 'failed';
export type AgentStage = 'triage' | 'retrieval' | 'root_cause' | 'patch' | 'validation' | 'report';

export interface Investigation {
  id: string;
  projectId: string;
  bugId?: string;
  incidentId?: string;
  question: string;
  status: InvestigationStatus;
  currentStage: AgentStage;
  stages: InvestigationStage[];
  findings?: string;
  rootCauseHypothesis?: string;
  confidence?: number;
  patchId?: string;
  createdAt: string;
  completedAt?: string;
}

export interface InvestigationStage {
  name: string;
  status: string;
  output?: string;
  desc?: string;
  summary?: string;
  stage?: string;
  evidence?: BugEvidence[];
  duration?: number;
  startedAt?: string;
  completedAt?: string;
}

// ---- Knowledge Base ----
export interface KnowledgeDocument {
  id: string;
  projectId: string;
  title: string;
  sourceType: 'readme' | 'documentation' | 'runbook' | 'incident_report' | 'architecture' | 'code';
  content: string;
  filePath?: string;
  chunkCount: number;
  indexedAt: string;
  status: 'indexed' | 'pending' | 'failed';
}

export interface RAGSearchResult {
  id: string;
  content: string;
  source: string;
  sourceType: string;
  relevanceScore: number;
  metadata: Record<string, any>;
}

export interface CitationItem {
  label: string;
  chunkId: string;
  title: string;
  filePath: string;
  sourceType: string;
  relevanceScore: number;
}

export interface RAGAskResponse {
  query: string;
  queryIntent: string;
  detectedEntities: string[];
  answer: string;
  evidence: string[];
  citations: CitationItem[];
  graphContext: string[];
  confidenceScore: number;
  isFaithful: boolean;
  faithfulnessDetails: string;
  recommendedNextSteps: string[];
}

// ---- Analytics ----
export interface DashboardStats {
  totalRepositories: number;
  activeAnomalies?: number;
  criticalIssues?: number;
  autonomousRepairs?: number;
  resolvedBugs?: number;
  totalPatches?: number;
  pendingReview?: number;
  draftPRs?: number;
  testsPassRate: number;
  mttrMinutes?: number;
  activeIncidents: number;
  activeInvestigations?: number;
}

// ---- API ----
export interface ApiResponse<T> {
  data: T;
  message?: string;
  error?: string;
}

export interface PaginatedResponse<T> {
  data: T[];
  total: number;
  page: number;
  pageSize: number;
  totalPages: number;
}

export interface ApiError {
  message: string;
  code: string;
  statusCode: number;
  details?: Record<string, string>;
}

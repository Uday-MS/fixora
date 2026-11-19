import { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { BookOpen, Search, Upload, Plus, FileText, CheckCircle2, RefreshCw, X, AlertCircle } from 'lucide-react';
import { AppLayout } from '@/components/layout/AppLayout';
import { Card } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';
import { LoadingState } from '@/components/ui/LoadingState';
import { EmptyState } from '@/components/ui/EmptyState';
import { knowledgeService } from '@/services/knowledge';
import type { KnowledgeDocument } from '@/types';

export function KnowledgePage() {
  const navigate = useNavigate();
  const [documents, setDocuments] = useState<KnowledgeDocument[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [isUploadModalOpen, setIsUploadModalOpen] = useState(false);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [docType, setDocType] = useState('documentation');
  const [isUploading, setIsUploading] = useState(false);
  const [uploadError, setUploadError] = useState<string | null>(null);

  const fileInputRef = useRef<HTMLInputElement>(null);

  const fetchDocuments = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const res = await knowledgeService.listDocuments();
      setDocuments(res?.data || []);
    } catch (err: any) {
      console.error('Failed to load knowledge documents:', err);
      setError(err.message || 'Failed to connect to Knowledge API');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchDocuments();
  }, []);

  const handleUploadSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedFile) return;
    setIsUploading(true);
    setUploadError(null);
    try {
      await knowledgeService.uploadDocument(selectedFile, 'proj_demo_001', docType);
      await fetchDocuments();
      setIsUploadModalOpen(false);
      setSelectedFile(null);
    } catch (err: any) {
      setUploadError(err.message || 'Document upload and indexing failed');
    } finally {
      setIsUploading(false);
    }
  };

  const filtered = documents.filter((d) =>
    (d.title || '').toLowerCase().includes(searchTerm.toLowerCase()) ||
    (d.sourceType || '').toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <AppLayout breadcrumbs={[{ label: 'Knowledge', href: '/knowledge' }, { label: 'Knowledge Base' }]}>
      <div className="flex flex-col gap-space-md">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-space-sm pb-space-sm border-b border-surface-container-highest">
          <div>
            <h1 className="font-headline text-headline-lg font-bold text-on-surface">RAG Knowledge Base (Qdrant)</h1>
            <p className="font-body text-body-sm text-on-surface-variant">
              Embeddings and semantic vectors indexing technical documentation, runbooks, and historical incident postmortems.
            </p>
          </div>
          <div className="flex items-center gap-space-sm">
            <Button variant="secondary" size="md" onClick={() => navigate('/rag-search')}>
              <Search className="w-4 h-4 mr-1 text-on-surface-variant" />
              Semantic Search
            </Button>
            <Button onClick={() => setIsUploadModalOpen(true)}>
              <Upload className="w-4 h-4 mr-1" />
              Upload Document
            </Button>
          </div>
        </div>

        {/* Search & Filter */}
        <div className="flex items-center gap-space-sm">
          <div className="relative flex-1 max-w-md">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-on-surface-variant w-4 h-4" />
            <input
              type="text"
              placeholder="Filter indexed documents..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="fixora-input pl-9"
            />
          </div>
          <Button variant="ghost" size="md" onClick={fetchDocuments} disabled={isLoading}>
            <RefreshCw className={`w-4 h-4 ${isLoading ? 'animate-spin' : ''}`} />
          </Button>
        </div>

        {isLoading ? (
          <LoadingState message="Retrieving indexed knowledge documents from Qdrant vector store..." />
        ) : error ? (
          <div className="p-space-lg bg-error-container/20 border border-error/30 rounded-xl text-center">
            <p className="font-bold text-on-surface">{error}</p>
            <Button variant="secondary" size="sm" className="mt-4" onClick={fetchDocuments}>
              Retry
            </Button>
          </div>
        ) : filtered.length === 0 ? (
          <EmptyState
            title={searchTerm ? 'No matching documents found' : 'No documents indexed in Knowledge Base'}
            description="Upload PDF, DOCX, Markdown, or runbooks to ground autonomous investigations and RAG search."
            action={
              <Button onClick={() => setIsUploadModalOpen(true)}>
                <Upload className="w-4 h-4 mr-1" />
                Upload First Document
              </Button>
            }
          />
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-space-md">
            {filtered.map((doc) => (
              <Card key={doc.id} className="p-space-md flex flex-col justify-between hover:border-primary-container transition-all">
                <div>
                  <div className="flex items-center gap-2 mb-1">
                    <Badge variant="outline">{doc.sourceType.toUpperCase()}</Badge>
                    <span className="font-mono text-mono-tag text-on-surface-variant">{doc.chunkCount || 1} chunks</span>
                    {doc.filePath && (
                      <span className="font-mono text-[11px] text-on-surface-variant truncate max-w-[200px]">
                        {doc.filePath}
                      </span>
                    )}
                  </div>
                  <h3 className="font-headline text-headline-sm font-bold text-on-surface">{doc.title}</h3>
                  {doc.content && (
                    <p className="font-body text-xs text-on-surface-variant mt-2 line-clamp-3">
                      {doc.content}
                    </p>
                  )}
                </div>
                <div className="mt-4 pt-2 border-t border-surface-container-highest/40 flex items-center justify-between font-mono text-mono-tag">
                  <span className="text-success flex items-center gap-1 font-semibold">
                    <CheckCircle2 className="w-3.5 h-3.5" /> Vector Indexed
                  </span>
                  <Button variant="ghost" size="sm" onClick={() => navigate('/rag-search')}>
                    Ask RAG →
                  </Button>
                </div>
              </Card>
            ))}
          </div>
        )}
      </div>

      {/* Upload Document Modal */}
      {isUploadModalOpen && (
        <div className="fixed inset-0 z-50 bg-inverse-surface/50 backdrop-blur-xs flex items-center justify-center p-4">
          <div className="w-full max-w-lg bg-surface-container-lowest rounded-2xl shadow-elevated border border-surface-container-highest p-space-lg relative animate-in fade-in zoom-in-95">
            <button
              onClick={() => setIsUploadModalOpen(false)}
              className="absolute right-4 top-4 p-1.5 text-on-surface-variant hover:text-on-surface rounded-lg hover:bg-surface-container-high"
            >
              <X className="w-4 h-4" />
            </button>
            <div className="flex items-center gap-2 mb-3">
              <Upload className="w-6 h-6 text-primary" />
              <h3 className="font-headline text-headline-sm font-bold text-on-surface">Upload Knowledge Document</h3>
            </div>
            <form onSubmit={handleUploadSubmit} className="space-y-4">
              <input
                type="file"
                ref={fileInputRef}
                accept=".pdf,.docx,.md,.txt,.py,.go,.ts,.js,.rs"
                onChange={(e) => {
                  if (e.target.files?.[0]) setSelectedFile(e.target.files[0]);
                }}
                className="hidden"
              />
              <div
                onClick={() => fileInputRef.current?.click()}
                className="border-2 border-dashed border-surface-container-highest rounded-xl p-6 text-center hover:bg-surface-container-low cursor-pointer"
              >
                {selectedFile ? (
                  <div>
                    <FileText className="w-8 h-8 text-primary mx-auto mb-1" />
                    <p className="font-bold text-on-surface">{selectedFile.name}</p>
                    <p className="text-xs text-on-surface-variant font-mono mt-0.5">
                      {(selectedFile.size / 1024).toFixed(1)} KB
                    </p>
                  </div>
                ) : (
                  <div>
                    <Upload className="w-8 h-8 text-on-surface-variant mx-auto mb-1" />
                    <p className="font-medium text-on-surface">Select Markdown, PDF, DOCX, TXT, or Code</p>
                    <p className="text-xs text-on-surface-variant mt-0.5 font-mono">Max 25MB • SHA-256 Deduplication</p>
                  </div>
                )}
              </div>

              <div>
                <label className="block font-mono text-mono-tag uppercase text-on-surface-variant font-semibold mb-1">
                  Document Classification
                </label>
                <select
                  value={docType}
                  onChange={(e) => setDocType(e.target.value)}
                  className="fixora-input text-sm"
                >
                  <option value="documentation">Technical Documentation</option>
                  <option value="runbook">Runbook & SOP</option>
                  <option value="architecture">Architecture RFC</option>
                  <option value="incident_report">Historical Incident Postmortem</option>
                </select>
              </div>

              {uploadError && (
                <div className="p-space-sm bg-error-container/20 border border-error/30 rounded-lg text-xs text-error font-medium flex items-center gap-2">
                  <AlertCircle className="w-4 h-4 shrink-0" />
                  <span>{uploadError}</span>
                </div>
              )}

              <div className="flex justify-end gap-2 pt-2">
                <Button type="button" variant="ghost" onClick={() => setIsUploadModalOpen(false)} disabled={isUploading}>
                  Cancel
                </Button>
                <Button type="submit" disabled={isUploading || !selectedFile}>
                  {isUploading ? 'Chunking & Embedding...' : 'Upload & Index'}
                </Button>
              </div>
            </form>
          </div>
        </div>
      )}
    </AppLayout>
  );
}

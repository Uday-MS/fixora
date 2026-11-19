import { useState, useRef } from 'react';
import { X, GitBranch, Upload, Check, AlertCircle, FileArchive, Loader2 } from 'lucide-react';
import { Button } from '@/components/ui/Button';
import { repositoryService } from '@/services/repositories';

interface ConnectRepoModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess?: () => void;
}

export function ConnectRepoModal({ isOpen, onClose, onSuccess }: ConnectRepoModalProps) {
  const [tab, setTab] = useState<'github' | 'upload'>('github');
  const [repoUrl, setRepoUrl] = useState('');
  const [branch, setBranch] = useState('main');
  const [githubToken, setGithubToken] = useState('');
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [customRepoName, setCustomRepoName] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [success, setSuccess] = useState(false);
  const [successMsg, setSuccessMsg] = useState('Repository connected and AST indexed.');
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  const fileInputRef = useRef<HTMLInputElement>(null);

  if (!isOpen) return null;

  const handleGithubSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!repoUrl.trim()) return;
    setIsSubmitting(true);
    setErrorMsg(null);
    try {
      await repositoryService.connect({
        url: repoUrl.trim(),
        branch: branch.trim() || 'main',
        token: githubToken.trim() || undefined,
      });
      setSuccessMsg('GitHub repository connected and AST tree indexed!');
      setSuccess(true);
      setTimeout(() => {
        onSuccess?.();
        onClose();
      }, 1200);
    } catch (err: any) {
      console.error('Repository connect failed:', err);
      setErrorMsg(err.message || 'Failed to connect to GitHub repository. Please verify the URL.');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleZipFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0];
      if (!file.name.endsWith('.zip')) {
        setErrorMsg('Please select a valid .zip archive file.');
        return;
      }
      setSelectedFile(file);
      setErrorMsg(null);
      if (!customRepoName) {
        setCustomRepoName(file.name.replace(/\.zip$/i, ''));
      }
    }
  };

  const handleZipDrop = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const file = e.dataTransfer.files[0];
      if (!file.name.endsWith('.zip')) {
        setErrorMsg('Please select a valid .zip archive file.');
        return;
      }
      setSelectedFile(file);
      setErrorMsg(null);
      if (!customRepoName) {
        setCustomRepoName(file.name.replace(/\.zip$/i, ''));
      }
    }
  };

  const handleZipSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedFile) {
      setErrorMsg('Please select a ZIP file to upload.');
      return;
    }
    setIsSubmitting(true);
    setErrorMsg(null);
    try {
      const res = await repositoryService.uploadStandaloneZip(
        selectedFile,
        customRepoName.trim() || undefined,
      );
      const analysis = res?.data?.analysis;
      setSuccessMsg(
        analysis
          ? `Ingested '${analysis.repositoryName}' with ${analysis.fileCount} files (Health: ${analysis.healthScore}/100)`
          : 'Repository ZIP uploaded and indexed successfully!'
      );
      setSuccess(true);
      setTimeout(() => {
        onSuccess?.();
        onClose();
      }, 1400);
    } catch (err: any) {
      console.error('ZIP upload failed:', err);
      setErrorMsg(err.message || 'Failed to upload and ingest repository ZIP.');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 bg-inverse-surface/50 backdrop-blur-xs flex items-center justify-center p-4">
      <div className="w-full max-w-lg bg-surface-container-lowest rounded-2xl shadow-elevated border border-surface-container-highest p-space-lg relative animate-in fade-in zoom-in-95 duration-150">
        <button
          onClick={onClose}
          className="absolute right-4 top-4 p-1.5 text-on-surface-variant hover:text-on-surface rounded-lg hover:bg-surface-container-high transition-colors"
        >
          <X className="w-4 h-4" />
        </button>

        <div className="flex items-center gap-2 mb-1">
          <div className="w-8 h-8 rounded-lg bg-primary-fixed flex items-center justify-center text-primary">
            <GitBranch className="w-4 h-4" />
          </div>
          <div>
            <h2 className="font-headline text-headline-sm font-bold text-on-surface">Connect Repository</h2>
            <p className="font-body text-body-sm text-on-surface-variant">
              Ingest AST symbols, commit history, and configure sandbox testing.
            </p>
          </div>
        </div>

        {/* Ingestion Mode Tabs */}
        <div className="flex border-b border-surface-container-highest my-space-md">
          <button
            onClick={() => { setTab('github'); setErrorMsg(null); }}
            className={`flex-1 py-2 font-body text-label-md font-semibold border-b-2 transition-colors ${
              tab === 'github'
                ? 'border-primary-container text-primary'
                : 'border-transparent text-on-surface-variant hover:text-on-surface'
            }`}
          >
            GitHub Repository
          </button>
          <button
            onClick={() => { setTab('upload'); setErrorMsg(null); }}
            className={`flex-1 py-2 font-body text-label-md font-semibold border-b-2 transition-colors ${
              tab === 'upload'
                ? 'border-primary-container text-primary'
                : 'border-transparent text-on-surface-variant hover:text-on-surface'
            }`}
          >
            Source Code ZIP Upload
          </button>
        </div>

        {success ? (
          <div className="py-8 text-center flex flex-col items-center">
            <div className="w-12 h-12 rounded-full bg-success-container text-success flex items-center justify-center mb-2">
              <Check className="w-6 h-6" />
            </div>
            <h3 className="font-headline text-headline-sm font-bold text-on-surface">Repository Connected!</h3>
            <p className="font-body text-body-sm text-on-surface-variant mt-1">
              {successMsg}
            </p>
          </div>
        ) : tab === 'github' ? (
          <form onSubmit={handleGithubSubmit} className="space-y-space-md">
            <div>
              <label className="block font-mono text-mono-tag uppercase text-on-surface-variant font-semibold mb-1">
                Repository URL or Owner/Repo
              </label>
              <input
                type="text"
                required
                placeholder="https://github.com/org/repo-name or owner/repo"
                value={repoUrl}
                onChange={(e) => setRepoUrl(e.target.value)}
                className="fixora-input"
              />
            </div>
            <div className="grid grid-cols-2 gap-space-sm">
              <div>
                <label className="block font-mono text-mono-tag uppercase text-on-surface-variant font-semibold mb-1">
                  Default Branch
                </label>
                <input
                  type="text"
                  value={branch}
                  onChange={(e) => setBranch(e.target.value)}
                  className="fixora-input"
                />
              </div>
              <div>
                <label className="block font-mono text-mono-tag uppercase text-on-surface-variant font-semibold mb-1">
                  Personal Access Token (Optional)
                </label>
                <input
                  type="password"
                  placeholder="ghp_..."
                  value={githubToken}
                  onChange={(e) => setGithubToken(e.target.value)}
                  className="fixora-input"
                />
              </div>
            </div>

            {errorMsg && (
              <div className="p-space-sm bg-error-container/20 border border-error/30 rounded-lg text-xs text-error font-medium flex items-center gap-2">
                <AlertCircle className="w-4 h-4 shrink-0" />
                <span>{errorMsg}</span>
              </div>
            )}

            <div className="p-space-sm bg-surface-container-low rounded-lg flex items-start gap-2 text-on-surface-variant font-body text-body-sm">
              <AlertCircle className="w-4 h-4 text-primary shrink-0 mt-0.5" />
              <span>
                FIXORA uses isolated ephemeral read copies. Patches are never pushed directly without pull request approval.
              </span>
            </div>
            <div className="flex justify-end gap-space-sm pt-space-xs">
              <Button type="button" variant="ghost" onClick={onClose} disabled={isSubmitting}>
                Cancel
              </Button>
              <Button type="submit" disabled={isSubmitting || !repoUrl.trim()}>
                {isSubmitting ? (
                  <>
                    <Loader2 className="w-4 h-4 mr-1 animate-spin" />
                    Fetching & Indexing...
                  </>
                ) : (
                  'Connect & Scan'
                )}
              </Button>
            </div>
          </form>
        ) : (
          <form onSubmit={handleZipSubmit} className="space-y-space-md">
            <input
              type="file"
              ref={fileInputRef}
              accept=".zip"
              onChange={handleZipFileChange}
              className="hidden"
            />
            <div
              onClick={() => fileInputRef.current?.click()}
              onDragOver={(e) => e.preventDefault()}
              onDrop={handleZipDrop}
              className="border-2 border-dashed border-surface-container-highest rounded-xl p-8 text-center hover:bg-surface-container-low/50 transition-colors cursor-pointer flex flex-col items-center"
            >
              {selectedFile ? (
                <>
                  <FileArchive className="w-10 h-10 text-primary mb-2" />
                  <p className="font-body text-label-md font-semibold text-on-surface">
                    {selectedFile.name}
                  </p>
                  <p className="font-mono text-mono-tag text-on-surface-variant mt-1">
                    {(selectedFile.size / (1024 * 1024)).toFixed(2)} MB • Ready to upload
                  </p>
                </>
              ) : (
                <>
                  <Upload className="w-8 h-8 text-primary mb-2" />
                  <p className="font-body text-label-md font-semibold text-on-surface">
                    Drop your repository ZIP archive here, or click to browse
                  </p>
                  <p className="font-mono text-mono-tag text-on-surface-variant mt-1">
                    MAX 50MB (.zip) • SAFE PATH TRAVERSAL VERIFIED
                  </p>
                </>
              )}
            </div>

            <div>
              <label className="block font-mono text-mono-tag uppercase text-on-surface-variant font-semibold mb-1">
                Repository Name
              </label>
              <input
                type="text"
                placeholder="cart-service"
                value={customRepoName}
                onChange={(e) => setCustomRepoName(e.target.value)}
                className="fixora-input"
              />
            </div>

            {errorMsg && (
              <div className="p-space-sm bg-error-container/20 border border-error/30 rounded-lg text-xs text-error font-medium flex items-center gap-2">
                <AlertCircle className="w-4 h-4 shrink-0" />
                <span>{errorMsg}</span>
              </div>
            )}

            <div className="flex justify-end gap-space-sm">
              <Button type="button" variant="ghost" onClick={onClose} disabled={isSubmitting}>
                Cancel
              </Button>
              <Button type="submit" disabled={isSubmitting || !selectedFile}>
                {isSubmitting ? (
                  <>
                    <Loader2 className="w-4 h-4 mr-1 animate-spin" />
                    Extracting & Indexing...
                  </>
                ) : (
                  'Upload & Ingest'
                )}
              </Button>
            </div>
          </form>
        )}
      </div>
    </div>
  );
}

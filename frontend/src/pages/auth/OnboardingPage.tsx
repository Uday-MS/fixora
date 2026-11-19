import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '@/context/AuthContext';
import { Button } from '@/components/ui/Button';
import { Check, ArrowRight, GitBranch, AlertCircle } from 'lucide-react';
import api from '@/services/api';
import type { Workspace } from '@/types';

export function OnboardingPage() {
  const [orgName, setOrgName] = useState('');
  const [defaultRepo, setDefaultRepo] = useState('');
  const [step, setStep] = useState(1);
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const navigate = useNavigate();
  const { setWorkspace, isAuthenticated } = useAuth();

  const handleStep1Submit = (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    if (!orgName.trim()) {
      setError('Please provide an organization or workspace name to proceed.');
      return;
    }
    setStep(2);
  };

  const handleComplete = async () => {
    if (!orgName.trim()) {
      setError('Organization name is required.');
      setStep(1);
      return;
    }

    setIsSubmitting(true);
    setError(null);

    try {
      // Real backend workspace creation
      const res = await api.post<{ data: Workspace }>('/workspaces', {
        name: orgName.trim(),
        plan: 'pro',
      });

      if (!res?.data) {
        throw new Error('Server returned an empty response while creating workspace.');
      }

      setWorkspace(res.data);

      // Connect first repository if provided
      if (defaultRepo.trim()) {
        try {
          await api.post('/repositories', {
            url: defaultRepo.trim(),
            branch: 'main',
          });
        } catch (repoErr) {
          console.warn('First repository registration deferred:', repoErr);
        }
      }

      navigate('/dashboard');
    } catch (err: any) {
      console.error('Workspace creation error:', err);
      setError(
        err?.message ||
        'Failed to create workspace on the server. Please ensure you are signed in and the backend API is online.'
      );
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="min-h-screen bg-background flex items-center justify-center p-4">
      <div className="w-full max-w-lg bg-surface-container-lowest border border-surface-container-highest rounded-2xl shadow-elevated p-space-xl">
        <div className="flex items-center justify-between mb-space-lg pb-space-sm border-b border-surface-container-highest">
          <div className="flex items-center gap-2">
            <span className="font-mono text-mono-tag font-bold px-2 py-0.5 rounded bg-primary-fixed text-primary">
              STEP {step} OF 2
            </span>
            <span className="font-headline text-headline-sm font-bold text-on-surface">Organization Setup</span>
          </div>
          {!isAuthenticated && (
            <button
              onClick={() => navigate('/login')}
              className="text-xs text-primary hover:underline font-mono"
            >
              Sign In First
            </button>
          )}
        </div>

        {error && (
          <div className="mb-4 p-3 bg-red-500/10 border border-red-500/30 rounded-lg flex items-center gap-2 text-red-400 font-body text-body-sm">
            <AlertCircle className="w-4 h-4 shrink-0 text-red-400" />
            <span>{error}</span>
          </div>
        )}

        {step === 1 ? (
          <form onSubmit={handleStep1Submit} className="space-y-space-md">
            <div>
              <label className="block font-mono text-mono-tag uppercase text-on-surface-variant font-semibold mb-1">
                Organization / Workspace Name
              </label>
              <input
                type="text"
                required
                placeholder="e.g. Acme Corp or Core Engineering"
                value={orgName}
                onChange={(e) => setOrgName(e.target.value)}
                className="fixora-input"
              />
            </div>
            <div className="p-3 bg-surface-container-low rounded-lg text-body-sm text-on-surface-variant">
              Workspaces isolate telemetry data, AST indexes, and automated patch histories.
            </div>
            <Button type="submit" size="lg" className="w-full">
              Continue to Repository Connect
              <ArrowRight className="w-4 h-4 ml-1" />
            </Button>
          </form>
        ) : (
          <div className="space-y-space-md">
            <div>
              <label className="block font-mono text-mono-tag uppercase text-on-surface-variant font-semibold mb-1">
                First Monitored Repository URL (Optional)
              </label>
              <input
                type="text"
                placeholder="https://github.com/owner/repo"
                value={defaultRepo}
                onChange={(e) => setDefaultRepo(e.target.value)}
                className="fixora-input"
              />
            </div>
            <div className="p-3 bg-surface-container-low rounded-lg flex items-center gap-2 text-body-sm text-on-surface-variant">
              <GitBranch className="w-4 h-4 text-primary shrink-0" />
              <span>We'll configure read-only scanning and prepare your isolated test runner.</span>
            </div>
            <div className="flex gap-space-sm">
              <Button variant="ghost" onClick={() => setStep(1)} disabled={isSubmitting}>
                Back
              </Button>
              <Button size="lg" className="flex-1" onClick={handleComplete} disabled={isSubmitting}>
                {isSubmitting ? 'Creating Workspace...' : 'Initialize FIXORA Platform'}
                <Check className="w-4 h-4 ml-1" />
              </Button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

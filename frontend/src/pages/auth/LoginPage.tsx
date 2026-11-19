import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '@/context/AuthContext';
import { Button } from '@/components/ui/Button';
import { Shield, ArrowRight } from 'lucide-react';

export function LoginPage() {
  const [email, setEmail] = useState('alex.vance@fixora.dev');
  const [password, setPassword] = useState('••••••••••••');
  const [isLoading, setIsLoading] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    await login(email, password);
    setIsLoading(false);
    navigate('/dashboard');
  };

  return (
    <div className="min-h-screen bg-background flex items-center justify-center p-4">
      <div className="w-full max-w-md bg-surface-container-lowest border border-surface-container-highest rounded-2xl shadow-elevated p-space-xl">
        <div className="flex flex-col items-center text-center mb-space-lg">
          <div className="w-12 h-12 rounded-xl bg-primary-container text-on-primary flex items-center justify-center font-headline font-bold text-2xl shadow-sm mb-3">
            F
          </div>
          <h1 className="font-headline text-headline-md font-bold text-on-surface">Welcome to FIXORA</h1>
          <p className="font-body text-body-sm text-on-surface-variant mt-1">
            Sign in to your autonomous engineering workspace.
          </p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-space-md">
          <div>
            <label className="block font-mono text-mono-tag uppercase text-on-surface-variant font-semibold mb-1">
              Engineering Work Email
            </label>
            <input
              type="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="fixora-input"
            />
          </div>

          <div>
            <label className="block font-mono text-mono-tag uppercase text-on-surface-variant font-semibold mb-1">
              Password
            </label>
            <input
              type="password"
              required
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="fixora-input"
            />
          </div>

          <div className="p-3 bg-surface-container-low rounded-lg flex items-center gap-2 text-on-surface-variant font-body text-body-sm">
            <Shield className="w-4 h-4 text-primary shrink-0" />
            <span className="text-xs">Single Sign-On (SSO) & GitHub OAuth verified.</span>
          </div>

          <Button type="submit" size="lg" className="w-full" disabled={isLoading}>
            {isLoading ? 'Authenticating...' : 'Sign In to Workspace'}
            <ArrowRight className="w-4 h-4 ml-1" />
          </Button>
        </form>

        <div className="mt-space-lg pt-space-md border-t border-surface-container-highest text-center font-body text-body-sm text-on-surface-variant">
          <span>Need a new organization? </span>
          <button onClick={() => navigate('/onboarding')} className="text-primary font-semibold hover:underline">
            Create Workspace
          </button>
        </div>
      </div>
    </div>
  );
}

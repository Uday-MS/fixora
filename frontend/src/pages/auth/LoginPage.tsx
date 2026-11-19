import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '@/context/AuthContext';
import { Button } from '@/components/ui/Button';
import { Shield, ArrowRight, AlertCircle, UserPlus, LogIn } from 'lucide-react';

export function LoginPage() {
  const [isRegisterMode, setIsRegisterMode] = useState(false);
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const { login, register } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setIsLoading(true);

    try {
      if (isRegisterMode) {
        if (!name.trim()) {
          throw new Error('Please enter your full name.');
        }
        await register(name, email, password);
      } else {
        await login(email, password);
      }
      navigate('/dashboard');
    } catch (err: any) {
      console.error('Authentication error:', err);
      setError(
        err?.message ||
        (isRegisterMode
          ? 'Registration failed. Please check your details and try again.'
          : 'Invalid email or password. Please verify your credentials.')
      );
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-background flex items-center justify-center p-4">
      <div className="w-full max-w-md bg-surface-container-lowest border border-surface-container-highest rounded-2xl shadow-elevated p-space-xl">
        <div className="flex flex-col items-center text-center mb-space-lg">
          <div className="w-12 h-12 rounded-xl bg-primary-container text-on-primary flex items-center justify-center font-headline font-bold text-2xl shadow-sm mb-3">
            F
          </div>
          <h1 className="font-headline text-headline-md font-bold text-on-surface">
            {isRegisterMode ? 'Create FIXORA Account' : 'Welcome to FIXORA'}
          </h1>
          <p className="font-body text-body-sm text-on-surface-variant mt-1">
            {isRegisterMode
              ? 'Set up your administrator profile and initial workspace.'
              : 'Sign in to your autonomous engineering workspace.'}
          </p>
        </div>

        {error && (
          <div className="mb-4 p-3 bg-red-500/10 border border-red-500/30 rounded-lg flex items-center gap-2 text-red-400 font-body text-body-sm">
            <AlertCircle className="w-4 h-4 shrink-0 text-red-400" />
            <span>{error}</span>
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-space-md">
          {isRegisterMode && (
            <div>
              <label className="block font-mono text-mono-tag uppercase text-on-surface-variant font-semibold mb-1">
                Full Name
              </label>
              <input
                type="text"
                required
                placeholder="e.g. Jane Doe"
                value={name}
                onChange={(e) => setName(e.target.value)}
                className="fixora-input"
              />
            </div>
          )}

          <div>
            <label className="block font-mono text-mono-tag uppercase text-on-surface-variant font-semibold mb-1">
              Engineering Work Email
            </label>
            <input
              type="email"
              required
              placeholder="name@company.com"
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
              placeholder="••••••••••••"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="fixora-input"
            />
          </div>

          <div className="p-3 bg-surface-container-low rounded-lg flex items-center gap-2 text-on-surface-variant font-body text-body-sm">
            <Shield className="w-4 h-4 text-primary shrink-0" />
            <span className="text-xs">Zero-trust JWT authentication & role-based access.</span>
          </div>

          <Button type="submit" size="lg" className="w-full" disabled={isLoading}>
            {isLoading
              ? 'Processing...'
              : isRegisterMode
              ? 'Create Workspace Admin Account'
              : 'Sign In to Workspace'}
            {isRegisterMode ? <UserPlus className="w-4 h-4 ml-1" /> : <ArrowRight className="w-4 h-4 ml-1" />}
          </Button>
        </form>

        <div className="mt-space-lg pt-space-md border-t border-surface-container-highest text-center font-body text-body-sm text-on-surface-variant space-y-2">
          <div>
            <span>{isRegisterMode ? 'Already have an account? ' : "Need an account? "}</span>
            <button
              type="button"
              onClick={() => {
                setIsRegisterMode(!isRegisterMode);
                setError(null);
              }}
              className="text-primary font-semibold hover:underline"
            >
              {isRegisterMode ? 'Sign In' : 'Register Here'}
            </button>
          </div>
          <div>
            <button
              type="button"
              onClick={() => navigate('/onboarding')}
              className="text-on-surface-variant hover:text-on-surface text-xs underline"
            >
              Set up dedicated organization & repository
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

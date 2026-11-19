import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Terminal,
  Shield,
  Zap,
  CheckCircle2,
  ArrowRight,
  GitPullRequest,
  Cpu,
  Layers,
  FileCheck,
  Play,
  Copy,
  Check,
} from 'lucide-react';
import { Button } from '@/components/ui/Button';

export function LandingPage() {
  const navigate = useNavigate();
  const [copied, setCopied] = useState(false);

  const copyInstall = () => {
    navigator.clipboard.writeText('curl -fsSL https://fixora.dev/install | sh');
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="min-h-screen bg-background font-body text-on-surface">
      {/* Top Bar */}
      <header className="sticky top-0 z-50 bg-surface-container-lowest/90 backdrop-blur-md border-b border-surface-container-highest px-space-lg py-3">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-space-sm">
            <div className="w-8 h-8 rounded-lg bg-primary-container flex items-center justify-center text-on-primary font-headline font-bold text-lg shadow-sm">
              F
            </div>
            <div className="flex flex-col">
              <span className="font-headline text-headline-sm font-bold tracking-tight text-on-surface">FIXORA</span>
              <span className="font-mono text-mono-tag text-on-surface-variant uppercase">v2.4 Autonomous Engine</span>
            </div>
          </div>
          <nav className="hidden md:flex items-center gap-space-lg font-body text-label-md text-on-surface-variant font-medium">
            <a href="#platform" className="hover:text-primary transition-colors">Platform</a>
            <a href="#pipeline" className="hover:text-primary transition-colors">Architecture</a>
            <a href="#security" className="hover:text-primary transition-colors">Security & Isolation</a>
            <a href="#postmortem" className="hover:text-primary transition-colors">Incident #1842 Case Study</a>
          </nav>
          <div className="flex items-center gap-space-sm">
            <Button variant="ghost" size="sm" onClick={() => navigate('/login')}>
              Sign In
            </Button>
            <Button size="sm" onClick={() => navigate('/dashboard')}>
              Open Dashboard
              <ArrowRight className="w-4 h-4 ml-1" />
            </Button>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <section className="py-space-xl px-space-lg max-w-7xl mx-auto text-center flex flex-col items-center">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-surface-container-high text-on-surface font-mono text-mono-tag uppercase tracking-wider mb-space-md shadow-xs">
          <span className="w-2 h-2 rounded-full bg-primary-container animate-pulse" />
          AUTONOMOUS REPAIR INTELLIGENCE FOR ENGINEERING TEAMS
        </div>

        <h1 className="font-headline text-headline-xl md:text-5xl lg:text-6xl font-extrabold tracking-tight text-on-surface max-w-4xl mb-space-md">
          Your code deserves more than another{' '}
          <span className="text-primary-container underline decoration-primary-fixed decoration-4 underline-offset-4">
            debugging tool
          </span>
          .
        </h1>

        <p className="font-body text-body-lg text-on-surface-variant max-w-2xl mb-space-lg">
          FIXORA investigates software failures across repositories, telemetry, and documentation — isolating root causes, synthesizing precision AST patches, and validating repairs in isolated Docker sandboxes.
        </p>

        <div className="flex flex-col sm:flex-row items-center gap-space-sm mb-space-md">
          <Button size="lg" onClick={() => navigate('/dashboard')}>
            <Zap className="w-5 h-5 mr-1" />
            Start Repairing Free
          </Button>
          <Button variant="secondary" size="lg" onClick={() => navigate('/autopatch')}>
            <Cpu className="w-5 h-5 mr-1 text-primary" />
            Explore AutoPatch Studio
          </Button>
        </div>

        {/* CLI Helper Strip */}
        <div className="inline-flex items-center gap-3 bg-inverse-surface text-inverse-on-surface px-4 py-2 rounded-lg font-mono text-mono-code text-xs mb-space-lg shadow-sm">
          <span className="text-primary-container font-bold">$</span>
          <span>curl -fsSL https://fixora.dev/install | sh</span>
          <button onClick={copyInstall} className="text-on-surface-variant hover:text-on-primary">
            {copied ? <Check className="w-4 h-4 text-success" /> : <Copy className="w-4 h-4" />}
          </button>
        </div>

        <p className="font-body text-label-sm text-on-surface-variant flex items-center gap-1.5">
          <CheckCircle2 className="w-4 h-4 text-primary" />
          100% human-in-the-loop verified • Read-only production safety • Zero unintended commits
        </p>
      </section>

      {/* Case Study Feature Preview */}
      <section id="postmortem" className="py-space-xl px-space-lg bg-surface-container-low border-y border-surface-container-highest">
        <div className="max-w-7xl mx-auto">
          <div className="flex flex-col md:flex-row items-start justify-between gap-space-lg bg-inverse-surface text-inverse-on-surface rounded-2xl p-space-xl shadow-elevated">
            <div className="flex-1">
              <span className="px-2 py-0.5 rounded bg-primary-container/20 text-primary-fixed font-mono text-mono-tag uppercase">
                Live Case Study: Incident #1842
              </span>
              <h2 className="font-headline text-headline-lg font-bold mt-2 mb-3">
                From 503 Outage to Validated Hotfix in 3.4 Minutes
              </h2>
              <p className="font-body text-body-md text-inverse-on-surface/80 mb-6">
                A database connection pool starvation knocked down <code className="text-primary-fixed bg-surface-container-high/10 px-1.5 py-0.5 rounded font-mono">payment-service</code>. FIXORA isolated the regression to PR #312, synthesized a graceful timeout fallback, and ran 18 integration tests with 0 regressions.
              </p>
              <div className="grid grid-cols-3 gap-4 font-mono mb-6">
                <div className="p-3 bg-surface-container-high/10 rounded-lg">
                  <div className="text-mono-tag text-inverse-on-surface/60">TTR Before</div>
                  <div className="text-headline-sm font-bold text-error">86 mins</div>
                </div>
                <div className="p-3 bg-surface-container-high/10 rounded-lg">
                  <div className="text-mono-tag text-inverse-on-surface/60">TTR FIXORA</div>
                  <div className="text-headline-sm font-bold text-primary-fixed">3.4 mins</div>
                </div>
                <div className="p-3 bg-surface-container-high/10 rounded-lg">
                  <div className="text-mono-tag text-inverse-on-surface/60">Human Step</div>
                  <div className="text-headline-sm font-bold text-success">1-Click PR</div>
                </div>
              </div>
              <Button onClick={() => navigate('/investigations/INV-1842')}>
                Inspect Live Investigation
                <ArrowRight className="w-4 h-4 ml-1" />
              </Button>
            </div>
            <div className="flex-1 w-full font-mono text-xs bg-surface-container-high/10 rounded-xl p-4 border border-surface-container-highest/20">
              <div className="text-primary-fixed mb-2 font-semibold">AST PATCH DIFF — src/gateway/pool_manager.go:142</div>
              <div className="space-y-1">
                <div className="text-error bg-error-container/20 px-2 py-0.5 rounded">- case conn := &lt;-p.idlePool: // no timeout under burst load</div>
                <div className="text-primary-fixed bg-primary-container/20 px-2 py-0.5 rounded">+ case conn := &lt;-p.idlePool: return p.verifyHealth(ctx, conn)</div>
                <div className="text-primary-fixed bg-primary-container/20 px-2 py-0.5 rounded">+ case &lt;-time.After(p.acquireTimeout): return p.spawnDynamicFallback(ctx)</div>
              </div>
              <div className="mt-4 pt-3 border-t border-surface-container-highest/20 flex items-center justify-between text-mono-tag text-inverse-on-surface/60">
                <span>DOCKER SUITE: 18/18 PASSED</span>
                <span className="text-primary-fixed font-semibold">P99 LATENCY: 41MS</span>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="py-space-lg px-space-lg border-t border-surface-container-highest text-center font-body text-body-sm text-on-surface-variant">
        <p>© 2026 FIXORA Autonomous Code Repair & Incident Intelligence Platform. Designed for safe, test-backed engineering.</p>
      </footer>
    </div>
  );
}

import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Search,
  Bell,
  Plus,
  Terminal,
  User as UserIcon,
} from 'lucide-react';
import { Button } from '@/components/ui/Button';
import api from '@/services/api';

interface HeaderProps {
  breadcrumbs?: { label: string; href?: string }[];
  onConnectRepo?: () => void;
}

export function Header({ breadcrumbs, onConnectRepo }: HeaderProps) {
  const [searchVal, setSearchVal] = useState('');
  const [sandboxInfo, setSandboxInfo] = useState<{
    status: string;
    mode: string;
    isolated: boolean;
  }>({
    status: 'checking',
    mode: 'checking',
    isolated: false,
  });
  const navigate = useNavigate();

  useEffect(() => {
    let isMounted = true;
    api
      .get<{ sandbox_status?: string; sandbox_mode?: string }>('/health')
      .then((res: any) => {
        if (!isMounted) return;
        const status = res.sandbox_status || 'blocked_by_configuration';
        const mode = res.sandbox_mode || 'unavailable';
        const isolated = status === 'ready' && (mode === 'isolated_docker' || mode === 'remote_container_worker');
        setSandboxInfo({ status, mode, isolated });
      })
      .catch(() => {
        if (!isMounted) return;
        setSandboxInfo({ status: 'unavailable', mode: 'unavailable', isolated: false });
      });
    return () => {
      isMounted = false;
    };
  }, []);

  return (
    <header className="fixed top-0 left-72 right-0 h-16 bg-surface-container-lowest/90 backdrop-blur-md border-b border-surface-container-highest z-40 px-space-lg flex items-center justify-between gap-space-md">
      {/* Left: Breadcrumbs & Global Search */}
      <div className="flex items-center gap-space-md min-w-0 flex-1">
        <div className="flex items-center gap-1.5 font-mono text-mono-code text-on-surface-variant truncate">
          {breadcrumbs && breadcrumbs.length > 0 ? (
            breadcrumbs.map((bc, idx) => (
              <span key={idx} className="flex items-center gap-1.5">
                {idx > 0 && <span className="text-outline">/</span>}
                <span
                  onClick={() => bc.href && navigate(bc.href)}
                  className={
                    idx === breadcrumbs.length - 1
                      ? 'px-1.5 py-0.5 rounded bg-surface-container-high font-mono text-mono-tag text-primary font-semibold'
                      : 'font-body text-label-md font-medium text-on-surface cursor-pointer hover:underline'
                  }
                >
                  {bc.label}
                </span>
              </span>
            ))
          ) : (
            <div className="flex items-center gap-1.5">
              <span className="font-body text-label-md font-medium text-on-surface">Engineering Control</span>
              <span className="text-outline">/</span>
              <span className="px-1.5 py-0.5 rounded bg-surface-container font-mono text-mono-tag text-on-surface">
                production-mesh
              </span>
            </div>
          )}
        </div>

        {/* Global Search Bar */}
        <div className="relative max-w-md w-full hidden lg:block">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-on-surface-variant w-4 h-4 pointer-events-none" />
          <input
            type="text"
            value={searchVal}
            onChange={(e) => setSearchVal(e.target.value)}
            placeholder="Ask FIXORA knowledge or jump to symbol [⌘K]..."
            className="w-full h-10 pl-9 pr-12 rounded-lg bg-surface-container-low border border-surface-container-highest font-body text-body-sm text-on-surface placeholder:text-on-surface-variant focus:outline-none focus:border-primary-container focus:ring-1 focus:ring-primary-container"
          />
          <div className="absolute right-2.5 top-1/2 -translate-y-1/2 px-1.5 py-0.5 rounded bg-surface-container-high border border-outline-variant font-mono text-mono-tag text-on-surface-variant">
            ⌘K
          </div>
        </div>
      </div>

      {/* Right Controls */}
      <div className="flex items-center gap-space-md shrink-0">
        {/* Sandbox Status Indicator */}
        <div
          className="hidden xl:flex items-center gap-1.5 px-2.5 py-1 rounded-md bg-surface-container-low border border-surface-container-highest"
          title={
            sandboxInfo.isolated
              ? 'Docker container sandbox is operational and isolated.'
              : 'Container isolation not configured. Untrusted host execution blocked by security policy.'
          }
        >
          <span
            className={`w-2 h-2 rounded-full ${
              sandboxInfo.isolated ? 'bg-emerald-500 animate-pulse' : 'bg-amber-500'
            }`}
          />
          <Terminal className="w-3.5 h-3.5 text-on-surface-variant" />
          <span className="font-mono text-mono-tag text-on-surface">
            {sandboxInfo.isolated
              ? 'Docker Sandbox: Ready (Isolated)'
              : 'Sandbox: Container Worker Required'}
          </span>
        </div>

        {/* Connect Repository Action Button */}
        <Button
          variant="secondary"
          size="sm"
          onClick={onConnectRepo || (() => navigate('/repositories?action=connect'))}
          className="shadow-sm"
        >
          <Plus className="w-4 h-4 text-primary" />
          <span>Connect Repository</span>
        </Button>

        {/* Notification Bell */}
        <div className="relative">
          <button
            onClick={() => navigate('/incidents')}
            className="p-2 rounded-lg text-on-surface-variant hover:bg-surface-container-high hover:text-on-surface transition-colors relative"
            title="Active Incidents"
          >
            <Bell className="w-4 h-4" />
            <span className="absolute top-1.5 right-1.5 w-4 h-4 rounded-full bg-error text-on-error font-mono text-[9px] flex items-center justify-center font-bold">
              3
            </span>
          </button>
        </div>

        {/* User Icon Avatar */}
        <div
          onClick={() => navigate('/settings')}
          className="w-8 h-8 rounded-full bg-primary flex items-center justify-center text-on-primary cursor-pointer hover:opacity-90"
          title="Account Settings"
        >
          <UserIcon className="w-4 h-4" />
        </div>
      </div>
    </header>
  );
}

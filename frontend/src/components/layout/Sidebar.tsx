import { NavLink } from 'react-router-dom';
import {
  LayoutDashboard,
  GitBranch,
  CircleDot,
  AlertOctagon,
  Microscope,
  Wrench,
  FileText,
  Activity,
  Layers,
  Settings,
  ChevronDown,
  Cpu,
  User,
  SlidersHorizontal,
} from 'lucide-react';
import { cn } from '@/lib/utils';
import { useAuth } from '@/context/AuthContext';

interface NavItem {
  name: string;
  path: string;
  icon: any;
  badge?: string | number;
  badgeVariant?: 'default' | 'critical' | 'accent' | 'warning';
}

interface NavSection {
  title: string;
  items: NavItem[];
}

const NAV_SECTIONS: NavSection[] = [
  {
    title: 'Overview',
    items: [
      { name: 'Dashboard', path: '/dashboard', icon: LayoutDashboard },
    ],
  },
  {
    title: 'Engineering',
    items: [
      { name: 'Repositories', path: '/repositories', icon: GitBranch },
      { name: 'Issues', path: '/issues', icon: CircleDot },
      { name: 'Incidents', path: '/incidents', icon: AlertOctagon },
      { name: 'Investigations', path: '/investigations', icon: Microscope },
      { name: 'AutoPatch Studio', path: '/autopatch', icon: Cpu },
      { name: 'Code Repairs', path: '/code-repairs', icon: Wrench },
    ],
  },
  {
    title: 'Observability',
    items: [
      { name: 'Logs', path: '/observability/logs', icon: FileText },
      { name: 'Metrics', path: '/observability/metrics', icon: Activity },
      { name: 'Traces', path: '/observability/traces', icon: Layers },
    ],
  },
  {
    title: 'Configuration',
    items: [
      { name: 'Settings', path: '/settings', icon: Settings },
    ],
  },
];

export function Sidebar() {
  const { user, workspace } = useAuth();

  return (
    <aside className="fixed left-0 top-0 h-full w-72 bg-surface-container-lowest border-r border-surface-container-highest z-50 flex flex-col justify-between overflow-y-auto">
      <div className="flex flex-col">
        {/* Brand Header */}
        <div className="h-16 px-space-md border-b border-surface-container-highest flex items-center justify-between gap-space-sm shrink-0">
          <div className="flex items-center gap-space-sm">
            <div className="w-8 h-8 rounded-lg bg-primary-container flex items-center justify-center text-on-primary font-headline font-bold text-lg shadow-sm">
              F
            </div>
            <div className="flex flex-col">
              <span className="font-headline text-headline-sm font-bold tracking-tight text-on-surface leading-none">
                FIXORA
              </span>
              <span className="font-mono text-mono-tag text-on-surface-variant uppercase tracking-wider mt-0.5">
                Autonomous SRE
              </span>
            </div>
          </div>
          <div className="flex items-center gap-1.5" title="Cluster Online">
            <span className="w-2 h-2 rounded-full bg-primary-container animate-pulse" />
          </div>
        </div>

        {/* Workspace Selector */}
        <div className="p-space-md border-b border-surface-container-highest bg-surface-container-low/70">
          <div className="flex items-center justify-between gap-space-xs text-left w-full cursor-pointer hover:opacity-90">
            <div className="flex flex-col truncate">
              <span className="font-body text-label-sm text-on-surface-variant truncate">Workspace</span>
              <span className="font-body text-label-md font-semibold text-on-surface truncate">
                {workspace?.name || 'Core Infra / Prod'}
              </span>
            </div>
            <ChevronDown className="w-4 h-4 text-on-surface-variant shrink-0" />
          </div>
          <div className="mt-space-xs flex items-center gap-space-xs">
            <span className="inline-flex items-center gap-1.5 px-2 py-0.5 rounded-full bg-surface-container-highest text-on-surface font-mono text-mono-tag">
              <span className="w-1.5 h-1.5 rounded-full bg-primary-container" />
              CONNECTED REPO
            </span>
          </div>
        </div>

        {/* Navigation Sections */}
        <nav className="flex-1 px-space-sm py-space-md space-y-space-md">
          {NAV_SECTIONS.map((section) => (
            <div key={section.title} className="space-y-space-xxs">
              <div className="px-space-sm pb-space-xxs font-mono text-mono-tag uppercase tracking-wider text-on-surface-variant font-semibold">
                {section.title}
              </div>
              {section.items.map((item) => {
                const Icon = item.icon;
                return (
                  <NavLink
                    key={item.path}
                    to={item.path}
                    className={({ isActive }) =>
                      cn(
                        'flex items-center justify-between px-space-sm py-2 rounded-lg transition-colors font-body text-label-md',
                        isActive
                          ? 'bg-primary-fixed text-on-primary-fixed-variant font-semibold border-l-2 border-primary-container shadow-xs'
                          : 'text-on-surface-variant hover:bg-surface-container-high hover:text-on-surface'
                      )
                    }
                  >
                    <div className="flex items-center gap-space-sm">
                      <Icon className="w-4 h-4 shrink-0" />
                      <span>{item.name}</span>
                    </div>
                    {item.badge !== undefined && (
                      <span
                        className={cn(
                          'font-mono text-mono-tag px-1.5 py-0.5 rounded',
                          item.badgeVariant === 'critical'
                            ? 'bg-error-container text-on-error-container font-semibold'
                            : item.badgeVariant === 'accent'
                            ? 'bg-primary-container text-on-primary font-semibold'
                            : item.badgeVariant === 'warning'
                            ? 'bg-primary-fixed text-on-primary-fixed-variant font-semibold'
                            : 'bg-surface-container text-on-surface-variant'
                        )}
                      >
                        {item.badge}
                      </span>
                    )}
                  </NavLink>
                );
              })}
            </div>
          ))}
        </nav>
      </div>

      {/* Footer / User Profile */}
      <div className="border-t border-surface-container-highest p-space-sm bg-surface-container-lowest shrink-0">
        <div className="pt-space-xs flex items-center justify-between gap-space-xs px-space-sm py-1.5">
          <div className="flex items-center gap-space-sm min-w-0">
            <div className="w-8 h-8 rounded-full bg-primary flex items-center justify-center text-on-primary shrink-0">
              <User className="w-4 h-4" />
            </div>
            <div className="flex flex-col min-w-0">
              <span className="font-body text-label-md font-semibold text-on-surface truncate">
                {user?.name || 'Alex Vance'}
              </span>
              <span className="font-body text-label-sm text-on-surface-variant truncate">
                Staff Infra Engineer
              </span>
            </div>
          </div>
          <NavLink
            to="/settings"
            className="text-on-surface-variant hover:text-on-surface p-1 rounded hover:bg-surface-container-high transition-colors"
          >
            <SlidersHorizontal className="w-4 h-4" />
          </NavLink>
        </div>
      </div>
    </aside>
  );
}

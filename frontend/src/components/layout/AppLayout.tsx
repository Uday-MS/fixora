import { useState, type ReactNode } from 'react';
import { Sidebar } from './Sidebar';
import { Header } from './Header';
import { ConnectRepoModal } from '@/components/shared/ConnectRepoModal';

interface AppLayoutProps {
  children: ReactNode;
  breadcrumbs?: { label: string; href?: string }[];
}

export function AppLayout({ children, breadcrumbs }: AppLayoutProps) {
  const [isConnectModalOpen, setIsConnectModalOpen] = useState(false);

  return (
    <div className="min-h-screen bg-background font-body text-on-surface antialiased">
      <Sidebar />
      <div className="pl-72 flex flex-col min-h-screen">
        <Header breadcrumbs={breadcrumbs} onConnectRepo={() => setIsConnectModalOpen(true)} />
        <main className="relative pt-16 w-full flex-1 bg-background">
          <div className="w-full px-space-lg py-space-lg max-w-[1600px] mx-auto">
            {children}
          </div>
        </main>
      </div>

      {isConnectModalOpen && (
        <ConnectRepoModal isOpen={isConnectModalOpen} onClose={() => setIsConnectModalOpen(false)} />
      )}
    </div>
  );
}

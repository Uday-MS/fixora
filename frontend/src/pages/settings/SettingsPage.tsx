import { useState, useEffect } from 'react';
import { Settings, Shield, Sliders, Database, Key, Check } from 'lucide-react';
import { AppLayout } from '@/components/layout/AppLayout';
import { Card, CardHeader, CardTitle } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import api from '@/services/api';

export function SettingsPage() {
  const [apiKey, setApiKey] = useState('••••••••••••••••••••••••');
  const [dockerMemory, setDockerMemory] = useState('2048 MB');
  const [cpuLimit, setCpuLimit] = useState('2.0 cores');
  const [timeout, setTimeoutVal] = useState('15s');
  const [saved, setSaved] = useState(false);

  useEffect(() => {
    api.get<any>('/settings').then(res => {
      const data = res?.data;
      if (data) {
        if (data.dockerMemoryLimit) setDockerMemory(data.dockerMemoryLimit);
        if (data.dockerCpuLimit) setCpuLimit(data.dockerCpuLimit);
        if (data.executionTimeoutSeconds) setTimeoutVal(`${data.executionTimeoutSeconds}s`);
      }
    }).catch(() => {});
  }, []);

  const handleSave = () => {
    setSaved(true);
    setTimeout(() => setSaved(false), 2000);
  };

  return (
    <AppLayout breadcrumbs={[{ label: 'Configuration' }, { label: 'Settings' }]}>
      <div className="flex flex-col gap-space-md max-w-4xl">
        <div className="pb-space-sm border-b border-surface-container-highest">
          <h1 className="font-headline text-headline-lg font-bold text-on-surface">Workspace Settings</h1>
          <p className="font-body text-body-sm text-on-surface-variant">Configure sandbox execution limits, telemetry endpoints, and LLM providers.</p>
        </div>

        <Card>
          <CardHeader>
            <CardTitle icon={<Key className="w-4 h-4 text-primary" />}>API & Model Keys</CardTitle>
          </CardHeader>
          <div className="space-y-space-md font-body text-body-sm">
            <div>
              <label className="block font-mono text-mono-tag uppercase text-on-surface-variant font-semibold mb-1">
                OpenAI / Gemini Model Key
              </label>
              <input
                type="password"
                value={apiKey}
                onChange={(e) => setApiKey(e.target.value)}
                className="fixora-input font-mono text-xs"
              />
            </div>
            <div className="p-3 bg-surface-container-low rounded-lg text-xs text-on-surface-variant">
              Keys are encrypted at rest and never exposed to client-side frontend code.
            </div>
            <Button size="sm" onClick={handleSave}>
              {saved ? 'Saved!' : 'Save Keys'}
            </Button>
          </div>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle icon={<Shield className="w-4 h-4 text-primary" />}>Docker Sandbox Execution Limits</CardTitle>
          </CardHeader>
          <div className="space-y-space-md font-body text-body-sm">
            <div className="grid grid-cols-2 gap-space-sm">
              <div>
                <label className="block font-mono text-mono-tag uppercase text-on-surface-variant font-semibold mb-1">
                  Container Memory Limit
                </label>
                <input
                  type="text"
                  value={dockerMemory}
                  onChange={(e) => setDockerMemory(e.target.value)}
                  className="fixora-input"
                />
              </div>
              <div>
                <label className="block font-mono text-mono-tag uppercase text-on-surface-variant font-semibold mb-1">
                  Egress Network Mode
                </label>
                <div className="h-10 px-3 rounded-lg bg-surface-container-high border border-surface-container-highest flex items-center font-mono text-mono-tag text-on-surface">
                  RESTRICTED ISOLATED
                </div>
              </div>
            </div>
          </div>
        </Card>
      </div>
    </AppLayout>
  );
}

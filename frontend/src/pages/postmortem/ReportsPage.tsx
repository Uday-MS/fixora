import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { FileCheck, ArrowRight, Download, RefreshCw, AlertCircle } from 'lucide-react';
import { AppLayout } from '@/components/layout/AppLayout';
import { Card } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';
import { LoadingState } from '@/components/ui/LoadingState';
import { EmptyState } from '@/components/ui/EmptyState';
import api from '@/services/api';

interface PostmortemReport {
  id: string;
  incidentId: string;
  title: string;
  affectedService: string;
  severity: string;
  status: string;
  durationStr: string;
  summary: string;
  rootCause: string;
  remediation: string;
  patchId?: string;
  createdAt: string;
}

export function ReportsPage() {
  const navigate = useNavigate();
  const [reports, setReports] = useState<PostmortemReport[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [exportingId, setExportingId] = useState<string | null>(null);

  const fetchReports = async () => {
    setIsLoading(true);
    try {
      const res = await api.get<{ data: PostmortemReport[] }>('/reports');
      setReports(res?.data || []);
    } catch (err) {
      console.error('Failed to load postmortem reports:', err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchReports();
  }, []);

  const handleExportPdf = (e: React.MouseEvent, reportId: string) => {
    e.stopPropagation();
    setExportingId(reportId);
    try {
      // Trigger browser download via direct API URL
      const downloadUrl = `/api/reports/${reportId}/export-pdf`;
      const link = document.createElement('a');
      link.href = downloadUrl;
      link.setAttribute('download', `FIXORA_Postmortem_${reportId}.pdf`);
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    } catch (err) {
      console.error('Failed to download PDF report:', err);
    } finally {
      setTimeout(() => setExportingId(null), 1000);
    }
  };

  return (
    <AppLayout breadcrumbs={[{ label: 'Analytics' }, { label: 'Postmortems & Reports' }]}>
      <div className="flex flex-col gap-space-md">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-space-sm pb-space-sm border-b border-surface-container-highest">
          <div>
            <h1 className="font-headline text-headline-lg font-bold text-on-surface">Incident Postmortems</h1>
            <p className="font-body text-body-sm text-on-surface-variant">
              Automated, evidence-backed post-incident reports generated for team reviews.
            </p>
          </div>
          <Button variant="secondary" size="md" onClick={fetchReports} disabled={isLoading}>
            <RefreshCw className={`w-4 h-4 mr-1 text-on-surface-variant ${isLoading ? 'animate-spin' : ''}`} />
            Refresh
          </Button>
        </div>

        {isLoading ? (
          <LoadingState message="Loading incident postmortems from database..." />
        ) : reports.length === 0 ? (
          <EmptyState
            title="No Postmortem Reports Available"
            description="Postmortems are automatically compiled when production incidents are diagnosed and resolved."
          />
        ) : (
          <div className="space-y-space-md">
            {reports.map((report) => (
              <Card key={report.id} className="p-space-md">
                <div className="flex flex-col md:flex-row md:items-center justify-between gap-space-md">
                  <div className="space-y-1">
                    <div className="flex items-center gap-2 flex-wrap">
                      <span className="font-mono text-mono-tag font-bold text-primary">
                        {report.incidentId} POSTMORTEM REPORT
                      </span>
                      <span className="font-mono text-xs text-on-surface-variant bg-surface-container-high px-2 py-0.5 rounded">
                        {report.affectedService}
                      </span>
                      <Badge variant={report.severity === 'sev1' ? 'critical' : 'warning'}>
                        {report.severity.toUpperCase()}
                      </Badge>
                      <Badge variant={report.status === 'resolved' ? 'success' : 'critical'} dot>
                        {report.status.toUpperCase()}
                      </Badge>
                    </div>
                    <h3 className="font-headline text-headline-sm font-bold text-on-surface">
                      {report.title}
                    </h3>
                    <p className="font-body text-xs text-on-surface-variant">
                      Duration: <span className="font-semibold">{report.durationStr}</span> • Root Cause:{' '}
                      <span className="text-on-surface">{report.rootCause}</span>
                    </p>
                    <p className="font-body text-xs text-on-surface-variant">
                      Remediation: <span className="text-on-surface">{report.remediation}</span>
                    </p>
                  </div>
                  <div className="flex items-center gap-2 shrink-0 self-end md:self-center">
                    <Button
                      size="sm"
                      variant="secondary"
                      disabled={exportingId === report.id}
                      onClick={(e) => handleExportPdf(e, report.id)}
                    >
                      <Download className="w-4 h-4 mr-1" />
                      {exportingId === report.id ? 'Generating PDF...' : 'Export PDF'}
                    </Button>
                    <Button size="sm" onClick={() => navigate('/investigations')}>
                      Inspect Evidence →
                    </Button>
                  </div>
                </div>
              </Card>
            ))}
          </div>
        )}
      </div>
    </AppLayout>
  );
}

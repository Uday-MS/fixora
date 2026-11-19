import { Routes, Route, Navigate } from 'react-router-dom';
import { useAuth } from '@/context/AuthContext';

// Pages
import { LandingPage } from '@/pages/landing/LandingPage';
import { LoginPage } from '@/pages/auth/LoginPage';
import { OnboardingPage } from '@/pages/auth/OnboardingPage';
import { DashboardPage } from '@/pages/dashboard/DashboardPage';
import { RepositoriesPage } from '@/pages/repositories/RepositoriesPage';
import { RepositoryDetailPage } from '@/pages/repositories/RepositoryDetailPage';
import { IssuesPage } from '@/pages/issues/IssuesPage';
import { CodeRepairsPage } from '@/pages/code-repairs/CodeRepairsPage';
import { IncidentsPage } from '@/pages/incidents/IncidentsPage';
import { InvestigationsPage } from '@/pages/investigations/InvestigationsPage';
import { InvestigationDetailPage } from '@/pages/investigations/InvestigationDetailPage';
import { AutoPatchPage } from '@/pages/autopatch/AutoPatchPage';
import { LogsPage } from '@/pages/observability/LogsPage';
import { MetricsPage } from '@/pages/observability/MetricsPage';
import { TracesPage } from '@/pages/observability/TracesPage';
import { SettingsPage } from '@/pages/settings/SettingsPage';

function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { isAuthenticated } = useAuth();
  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }
  return <>{children}</>;
}

export function App() {
  const { isAuthenticated } = useAuth();

  return (
    <Routes>
      {/* Public routes */}
      <Route path="/" element={isAuthenticated ? <Navigate to="/dashboard" replace /> : <LandingPage />} />
      <Route path="/landing" element={<LandingPage />} />
      <Route path="/login" element={<LoginPage />} />
      <Route path="/onboarding" element={<OnboardingPage />} />

      {/* Authenticated Application routes */}
      <Route
        path="/dashboard"
        element={
          <ProtectedRoute>
            <DashboardPage />
          </ProtectedRoute>
        }
      />
      <Route
        path="/repositories"
        element={
          <ProtectedRoute>
            <RepositoriesPage />
          </ProtectedRoute>
        }
      />
      <Route
        path="/repositories/:id"
        element={
          <ProtectedRoute>
            <RepositoryDetailPage />
          </ProtectedRoute>
        }
      />
      <Route
        path="/issues"
        element={
          <ProtectedRoute>
            <IssuesPage />
          </ProtectedRoute>
        }
      />
      <Route
        path="/bugs"
        element={
          <ProtectedRoute>
            <Navigate to="/issues" replace />
          </ProtectedRoute>
        }
      />
      <Route
        path="/incidents"
        element={
          <ProtectedRoute>
            <IncidentsPage />
          </ProtectedRoute>
        }
      />
      <Route
        path="/incidents/:id"
        element={
          <ProtectedRoute>
            <InvestigationDetailPage />
          </ProtectedRoute>
        }
      />
      <Route
        path="/investigations"
        element={
          <ProtectedRoute>
            <InvestigationsPage />
          </ProtectedRoute>
        }
      />
      <Route
        path="/investigations/:id"
        element={
          <ProtectedRoute>
            <InvestigationDetailPage />
          </ProtectedRoute>
        }
      />
      <Route
        path="/code-repairs"
        element={
          <ProtectedRoute>
            <CodeRepairsPage />
          </ProtectedRoute>
        }
      />
      <Route
        path="/autopatch"
        element={
          <ProtectedRoute>
            <AutoPatchPage />
          </ProtectedRoute>
        }
      />
      <Route
        path="/observability/logs"
        element={
          <ProtectedRoute>
            <LogsPage />
          </ProtectedRoute>
        }
      />
      <Route
        path="/observability/metrics"
        element={
          <ProtectedRoute>
            <MetricsPage />
          </ProtectedRoute>
        }
      />
      <Route
        path="/observability/traces"
        element={
          <ProtectedRoute>
            <TracesPage />
          </ProtectedRoute>
        }
      />
      <Route
        path="/settings"
        element={
          <ProtectedRoute>
            <SettingsPage />
          </ProtectedRoute>
        }
      />

      {/* Fallback */}
      <Route path="*" element={<Navigate to="/dashboard" replace />} />
    </Routes>
  );
}

export default App;

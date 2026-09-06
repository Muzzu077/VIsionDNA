import { useEffect } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { Layout } from './components/layout/Layout';
import { LoginPage } from './components/auth/LoginPage';
import { ProtectedRoute } from './components/auth/ProtectedRoute';
import { useAuthStore } from './stores/authStore';

// import pages
import { OverviewPage } from './pages/OverviewPage';
import { LiveMonitoringPage } from './pages/LiveMonitoringPage';
import { DigitalTwinPage } from './pages/DigitalTwinPage';
import { RiskCenterPage } from './pages/RiskCenterPage';
import { ActivityAnalyticsPage } from './pages/ActivityAnalyticsPage';
import { PredictionAnalyticsPage } from './pages/PredictionAnalyticsPage';
import { CameraManagementPage } from './pages/CameraManagementPage';
import { ZoneManagementPage } from './pages/ZoneManagementPage';
import { SettingsPage } from './pages/SettingsPage';
import { PersonDetailPage } from './pages/PersonDetailPage';

const queryClient = new QueryClient();

export default function App() {
  const { checkAuth } = useAuthStore();

  useEffect(() => {
    checkAuth();
  }, [checkAuth]);

  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          
          <Route element={<ProtectedRoute />}>
            <Route path="/" element={<Layout />}>
              <Route index element={<OverviewPage />} />
              <Route path="live" element={<LiveMonitoringPage />} />
              <Route path="twin" element={<DigitalTwinPage />} />
              <Route path="risks" element={<RiskCenterPage />} />
              <Route path="analytics/activity" element={<ActivityAnalyticsPage />} />
              <Route path="analytics/prediction" element={<PredictionAnalyticsPage />} />
              <Route path="cameras" element={<CameraManagementPage />} />
              <Route path="zones" element={<ZoneManagementPage />} />
              <Route path="settings" element={<SettingsPage />} />
              <Route path="persons/:id" element={<PersonDetailPage />} />
            </Route>
          </Route>
          
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </BrowserRouter>
    </QueryClientProvider>
  );
}

import { useLocation } from 'react-router-dom';
import { Bell, User, LogOut, Cpu, Clock } from 'lucide-react';
import { useAppStore } from '../../stores/appStore';
import { useAuthStore } from '../../stores/authStore';

export function Header() {
  const location = useLocation();
  const { systemMetrics, activeAlerts } = useAppStore();
  const { user, logout } = useAuthStore();

  const getPageTitle = () => {
    switch (location.pathname) {
      case '/': return 'Overview';
      case '/live': return 'Live Monitoring';
      case '/twin': return 'Digital Twin';
      case '/risks': return 'Risk Center';
      case '/analytics/activity': return 'Activity Analytics';
      case '/analytics/prediction': return 'Prediction Analytics';
      case '/cameras': return 'Camera Management';
      case '/zones': return 'Zone Management';
      case '/settings': return 'Settings';
      default: return 'VisionDNA';
    }
  };

  const fps = systemMetrics?.fps || 0;
  const latency = systemMetrics?.latencyMs || 0;

  return (
    <header className="h-16 flex items-center justify-between px-6 bg-slate-900 border-b border-slate-700/50">
      <h1 className="text-xl font-semibold text-slate-100">
        {getPageTitle()}
      </h1>

      <div className="flex items-center space-x-6">
        {/* System Stats Pipeline */}
        <div className="hidden md:flex items-center space-x-4 bg-slate-800 px-3 py-1.5 rounded-full border border-slate-700 text-xs">
          <div className="flex items-center text-slate-400" title="Processing FPS">
            <Cpu className="w-4 h-4 mr-1 text-blue-400" />
            <span className="font-mono">{fps.toFixed(1)} FPS</span>
          </div>
          <div className="w-px h-4 bg-slate-700"></div>
          <div className="flex items-center text-slate-400" title="System Latency">
            <Clock className="w-4 h-4 mr-1 text-green-400" />
            <span className="font-mono">{latency} ms</span>
          </div>
        </div>

        {/* Alerts Bell */}
        <button className="relative p-2 text-slate-400 hover:text-slate-100 transition-colors">
          <Bell className="w-5 h-5" />
          {activeAlerts.length > 0 && (
            <span className="absolute top-1 right-1 flex h-4 w-4 items-center justify-center rounded-full bg-red-500 text-[10px] font-bold text-white">
              {activeAlerts.length}
            </span>
          )}
        </button>

        {/* User Menu Mockup */}
        <div className="flex items-center space-x-3 pl-4 border-l border-slate-700">
          <div className="flex flex-col items-end">
            <span className="text-sm font-medium text-slate-200">{user?.name || 'Administrator'}</span>
            <span className="text-xs text-slate-500">{user?.role || 'Super Admin'}</span>
          </div>
          <div className="h-8 w-8 rounded-full bg-slate-700 flex items-center justify-center cursor-pointer">
            <User className="w-4 h-4 text-slate-300" />
          </div>
          <button onClick={logout} className="p-1 text-slate-400 hover:text-red-400 transition-colors ml-2" title="Logout">
            <LogOut className="w-4 h-4" />
          </button>
        </div>
      </div>
    </header>
  );
}

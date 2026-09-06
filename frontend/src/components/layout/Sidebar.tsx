import { NavLink } from 'react-router-dom';
import { 
  LayoutDashboard, Monitor, Users, ShieldAlert, Activity, 
  TrendingUp, Camera, Map, Settings, ChevronLeft, ChevronRight 
} from 'lucide-react';
import { useAppStore } from '../../stores/appStore';
import { classNames } from '../../utils/format';

const navigation = [
  { name: 'Overview', to: '/', icon: LayoutDashboard },
  { name: 'Live Monitoring', to: '/live', icon: Monitor },
  { name: 'Digital Twin', to: '/twin', icon: Users },
  { name: 'Risk Center', to: '/risks', icon: ShieldAlert },
  { name: 'Activity Analytics', to: '/analytics/activity', icon: Activity },
  { name: 'Prediction Analytics', to: '/analytics/prediction', icon: TrendingUp },
  { name: 'Cameras', to: '/cameras', icon: Camera },
  { name: 'Zones', to: '/zones', icon: Map },
  { name: 'Settings', to: '/settings', icon: Settings },
];

export function Sidebar() {
  const { sidebarOpen, toggleSidebar, demoMode, simulationMode } = useAppStore();

  return (
    <div className={classNames(
      "flex flex-col bg-slate-900 border-r border-slate-700/50 transition-all duration-300 relative",
      sidebarOpen ? "w-64" : "w-20"
    )}>
      {/* Brand */}
      <div className="h-16 flex items-center justify-between px-4 border-b border-slate-700/50">
        {sidebarOpen ? (
          <span className="text-xl font-bold bg-gradient-to-r from-blue-400 to-blue-200 bg-clip-text text-transparent truncate flex-1">
            VisionDNA
          </span>
        ) : (
          <span className="text-xl font-bold text-blue-500 mx-auto">V</span>
        )}
      </div>
      
      <button 
        onClick={toggleSidebar}
        className="absolute -right-3 top-20 bg-slate-800 border border-slate-600 rounded-full p-1 text-slate-400 hover:text-white"
      >
        {sidebarOpen ? <ChevronLeft size={16} /> : <ChevronRight size={16} />}
      </button>

      {/* Nav */}
      <nav className="flex-1 overflow-y-auto py-4 scrollbar-thin">
        <ul className="space-y-1 px-2">
          {navigation.map((item) => (
            <li key={item.name}>
              <NavLink
                to={item.to}
                className={({ isActive }) => classNames(
                  "flex items-center rounded-md px-3 py-2 text-sm font-medium transition-colors",
                  isActive 
                    ? "bg-blue-500/10 text-blue-400 border border-blue-500/20" 
                    : "text-slate-400 hover:bg-slate-800 hover:text-slate-100 border border-transparent"
                )}
                title={!sidebarOpen ? item.name : undefined}
              >
                <item.icon className={classNames("shrink-0", sidebarOpen ? "mr-3 h-5 w-5" : "mx-auto h-6 w-6")} aria-hidden="true" />
                {sidebarOpen && <span>{item.name}</span>}
              </NavLink>
            </li>
          ))}
        </ul>
      </nav>

      {/* Status / Badges */}
      <div className="p-4 border-t border-slate-700/50 space-y-2">
        {demoMode && (
          <div className="px-2 py-1 bg-purple-500/20 text-purple-400 text-xs text-center rounded border border-purple-500/30">
            {sidebarOpen ? "Demo Mode Active" : "D"}
          </div>
        )}
        {simulationMode && (
          <div className="px-2 py-1 bg-orange-500/20 text-orange-400 text-xs text-center rounded border border-orange-500/30">
            {sidebarOpen ? "Simulation Active" : "S"}
          </div>
        )}
        <div className="flex items-center justify-center space-x-2">
           <span className="relative flex h-3 w-3">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-75"></span>
            <span className="relative inline-flex rounded-full h-3 w-3 bg-green-500"></span>
          </span>
          {sidebarOpen && <span className="text-xs text-slate-400">System Online</span>}
        </div>
      </div>
    </div>
  );
}

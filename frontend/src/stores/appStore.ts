import { create } from 'zustand';
import type { SystemHealth, SystemMetrics, Alert } from '../types';

interface AppState {
  systemHealth: SystemHealth | null;
  systemMetrics: SystemMetrics | null;
  activeAlerts: Alert[];
  notifications: any[];
  sidebarOpen: boolean;
  currentEnvironment: string;
  demoMode: boolean;
  simulationMode: boolean;

  setSystemHealth: (health: SystemHealth) => void;
  setSystemMetrics: (metrics: SystemMetrics) => void;
  addAlert: (alert: Alert) => void;
  removeAlert: (id: string) => void;
  toggleSidebar: () => void;
  setEnvironment: (env: string) => void;
  toggleDemoMode: () => void;
  toggleSimulationMode: () => void;
}

export const useAppStore = create<AppState>((set) => ({
  systemHealth: null,
  systemMetrics: null,
  activeAlerts: [],
  notifications: [],
  sidebarOpen: true,
  currentEnvironment: 'default',
  demoMode: false,
  simulationMode: false,

  setSystemHealth: (health) => set({ systemHealth: health }),
  setSystemMetrics: (metrics) => set({ systemMetrics: metrics }),
  addAlert: (alert) => set((state) => ({ activeAlerts: [alert, ...state.activeAlerts].slice(0, 50) })),
  removeAlert: (id) => set((state) => ({ activeAlerts: state.activeAlerts.filter(a => a.id !== id) })),
  toggleSidebar: () => set((state) => ({ sidebarOpen: !state.sidebarOpen })),
  setEnvironment: (env) => set({ currentEnvironment: env }),
  toggleDemoMode: () => set((state) => ({ demoMode: !state.demoMode })),
  toggleSimulationMode: () => set((state) => ({ simulationMode: !state.simulationMode })),
}));

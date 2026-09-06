import axios from 'axios';
import { useAuthStore } from '../stores/authStore';
import type { 
  User, Camera, CameraCreate, Person, PersonState, ActivityEvent,
  RiskEvent, Prediction, Alert, Zone, DigitalTwinState, SystemHealth,
  SystemMetrics, OverviewStats 
} from '../types';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api',
});

api.interceptors.request.use((config) => {
  const token = useAuthStore.getState().token;
  if (token && config.headers) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      useAuthStore.getState().logout();
    }
    return Promise.reject(error);
  }
);

export const authService = {
  login: (data: any) => api.post<{ token: string, user: User }>('/auth/login', data),
  register: (data: any) => api.post<{ token: string, user: User }>('/auth/register', data),
  me: () => api.get<User>('/auth/me'),
};

export const cameraService = {
  getAll: () => api.get<Camera[]>('/cameras'),
  getById: (id: string) => api.get<Camera>(`/cameras/${id}`),
  create: (data: CameraCreate) => api.post<Camera>('/cameras', data),
  update: (id: string, data: Partial<CameraCreate>) => api.put<Camera>(`/cameras/${id}`, data),
  delete: (id: string) => api.delete(`/cameras/${id}`),
  test: (id: string) => api.post(`/cameras/${id}/test-connection`),
  start: (id: string) => api.post(`/cameras/${id}/start`),
  stop: (id: string) => api.post(`/cameras/${id}/stop`),
  streamUrl: (id: string) => `/api/cameras/${id}/stream`,
};

export const personService = {
  getAll: () => api.get<Person[]>('/persons'),
  getById: (id: string) => api.get<{person: Person, state: PersonState}>(`/persons/${id}`),
};

export const activityService = {
  getAll: () => api.get<ActivityEvent[]>('/activities'),
  getByPersonId: (personId: string) => api.get<ActivityEvent[]>(`/activities?personId=${personId}`),
};

export const riskService = {
  getAll: (params?: any) => api.get<RiskEvent[]>('/risks', { params }),
  acknowledge: (id: string) => api.post(`/risks/${id}/acknowledge`),
};

export const predictionService = {
  getAll: () => api.get<Prediction[]>('/predictions'),
};

export const alertService = {
  getAll: () => api.get<Alert[]>('/alerts'),
  markRead: (id: string) => api.put(`/alerts/${id}/read`),
};

export const zoneService = {
  getAll: () => api.get<Zone[]>('/zones'),
  create: (data: Partial<Zone>) => api.post<Zone>('/zones', data),
  update: (id: string, data: Partial<Zone>) => api.put<Zone>(`/zones/${id}`, data),
  delete: (id: string) => api.delete(`/zones/${id}`),
};

export const twinService = {
  getState: () => api.get<DigitalTwinState>('/twin/state'),
};

export const analyticsService = {
  getOverview: () => api.get<OverviewStats>('/analytics/overview'),
  getActivities: () => api.get('/analytics/activities'),
  getRisks: () => api.get('/analytics/risks'),
  getPredictions: () => api.get('/analytics/predictions'),
};

export const systemService = {
  getHealth: () => api.get<SystemHealth>('/system/health'),
  getMetrics: () => api.get<SystemMetrics>('/system/metrics'),
};

export default api;

export interface User {
  id: string;
  email: string;
  name: string;
  role: string;
}

export interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
}

export type CameraSourceType = 'WEBCAM' | 'UPLOAD' | 'RTSP' | 'HTTP';

export interface Camera {
  id: string;
  name: string;
  sourceType: CameraSourceType;
  sourceUrl: string;
  status: 'ONLINE' | 'OFFLINE' | 'ERROR';
  environment: string;
  resolution?: string;
  fps?: number;
}

export interface CameraCreate {
  name: string;
  sourceType: CameraSourceType;
  sourceUrl: string;
  environment: string;
}

export interface Person {
  id: string;
  trackingId: string;
  firstSeen: string;
  lastSeen: string;
}

export interface PersonState {
  activity: string;
  position: [number, number];
  riskLevel: RiskSeverity;
  posture: string;
}

export interface ActivityEvent {
  id: string;
  personId: string;
  activityType: string;
  timestamp: string;
  confidence: number;
}

export interface DigitalTwinState {
  environment: string;
  timestamp: string;
  persons: Record<string, PersonState>;
  cameras: Record<string, any>;
  zones: Record<string, any>;
}

export type RiskSeverity = 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';

export type RiskStatus = 'ACTIVE' | 'ACKNOWLEDGED' | 'RESOLVED';

export interface RiskExplanation {
  primary_reason: string;
  contributing_factors: string[];
}

export interface RiskEvent {
  id: string;
  personId: string | null;
  severity: RiskSeverity;
  status: RiskStatus;
  type: string;
  explanation: RiskExplanation;
  timestamp: string;
  score: number;
}

export interface Prediction {
  id: string;
  predictedEvent: string;
  probability: number;
  horizonSeconds: number;
  timestamp: string;
  actualOutcome?: boolean;
  correctness?: boolean;
}

export interface Alert {
  id: string;
  riskEventId: string;
  message: string;
  severity: RiskSeverity;
  timestamp: string;
  isRead: boolean;
}

export type ZoneType = 'RESTRICTED' | 'WARNING' | 'SAFE';

export interface Zone {
  id: string;
  name: string;
  type: ZoneType;
  riskLevel: RiskSeverity;
  points: [number, number][];
  color: string;
}

export interface MonitoredObject {
  id: string;
  type: string;
  status: string;
  position: [number, number];
}

export interface SystemHealth {
  cameraService: 'UP' | 'DOWN' | 'DEGRADED';
  inferenceEngine: 'UP' | 'DOWN' | 'DEGRADED';
  database: 'UP' | 'DOWN' | 'DEGRADED';
  digitalTwin: 'UP' | 'DOWN' | 'DEGRADED';
}

export interface SystemMetrics {
  fps: number;
  latencyMs: number;
  queueSize: number;
  cpuUsage: number;
  memoryUsage: number;
}

export interface EventMessage {
  type: string;
  payload: any;
  timestamp: string;
}

export interface OverviewStats {
  activeCameras: number;
  peopleDetected: number;
  activeAlerts: number;
  averageRiskScore: number;
  processingFps: number;
  systemLatencyMs: number;
}

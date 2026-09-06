import { useEffect, useRef, useState } from 'react';
import { AlertTriangle, Camera, Crosshair, Hexagon, Layers, Maximize, ShieldAlert } from 'lucide-react';
import { StatusBadge } from '../components/common/StatusBadge';
import { useWebSocket } from '../hooks/useWebSocket';

type DemoState = {
  person_id: string;
  activity: string;
  velocity: number;
  risk_score: number;
  risk_level: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  prediction: string;
  prediction_probability?: number | null;
  prediction_horizon_seconds?: number | null;
  explanation: string;
  alert_triggered: boolean;
  x_pos: number;
  y_pos: number;
  zone: string;
};

const initialState: DemoState = {
  person_id: 'P001', activity: 'standing', velocity: 0, risk_score: 10,
  risk_level: 'LOW', prediction: 'Awaiting simulation data', explanation: 'Simulation mode is starting.',
  alert_triggered: false, x_pos: 100, y_pos: 500, zone: 'Main Hall',
};

export function LiveMonitoringPage() {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const { connected, lastMessage } = useWebSocket('live');
  const [showBBoxes, setShowBBoxes] = useState(true);
  const [showZones, setShowZones] = useState(true);
  const [demoState, setDemoState] = useState<DemoState>(initialState);

  useEffect(() => {
    const state = lastMessage?.data?.state;
    if (state?.simulation_mode) setDemoState(state as DemoState);
  }, [lastMessage]);

  // Mock rendering
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    let frameId: number;

    const render = () => {
      // Clear
      ctx.fillStyle = '#0f172a';
      ctx.fillRect(0, 0, canvas.width, canvas.height);

      // Grid background pattern
      ctx.strokeStyle = '#1e293b';
      ctx.lineWidth = 1;
      for(let i=0; i<canvas.width; i+=40) {
        ctx.beginPath(); ctx.moveTo(i, 0); ctx.lineTo(i, canvas.height); ctx.stroke();
      }
      for(let i=0; i<canvas.height; i+=40) {
        ctx.beginPath(); ctx.moveTo(0, i); ctx.lineTo(canvas.width, i); ctx.stroke();
      }

      // Restricted zone used by the explicit demo scenario.
      if (showZones) {
        ctx.fillStyle = 'rgba(239, 68, 68, 0.1)';
        ctx.strokeStyle = '#ef4444';
        ctx.lineWidth = 2;
        ctx.setLineDash([5, 5]);
        ctx.beginPath();
        ctx.moveTo(590, 55);
        ctx.lineTo(770, 55);
        ctx.lineTo(770, 205);
        ctx.lineTo(590, 205);
        ctx.closePath();
        ctx.fill();
        ctx.stroke();
        ctx.setLineDash([]);
        ctx.fillStyle = '#ef4444';
        ctx.font = '12px sans-serif';
        ctx.fillText('RESTRICTED AREA', 605, 80);
      }

      ctx.strokeStyle = '#334155';
      ctx.lineWidth = 2;
      ctx.beginPath();
      ctx.moveTo(100, 500);
      ctx.lineTo(demoState.x_pos + 30, demoState.y_pos + 180);
      ctx.stroke();

      if (showBBoxes) {
        const p1x = Math.min(730, Math.max(0, demoState.x_pos));
        const p1y = Math.min(260, Math.max(0, demoState.y_pos));
        const color = demoState.risk_level === 'CRITICAL' ? '#ef4444' : demoState.risk_level === 'HIGH' ? '#f97316' : demoState.risk_level === 'MEDIUM' ? '#eab308' : '#22c55e';
        ctx.strokeStyle = color;
        ctx.lineWidth = 2;
        ctx.strokeRect(p1x, p1y, 60, 180);
        ctx.fillStyle = color;
        ctx.fillRect(p1x, p1y - 40, 154, 38);
        ctx.fillStyle = '#0f172a';
        ctx.font = '12px sans-serif';
        ctx.fillText(`P001 | ${demoState.activity.toUpperCase()}`, p1x + 5, p1y - 23);
        ctx.fillText(`RISK ${Math.round(demoState.risk_score)}%`, p1x + 5, p1y - 8);
      }

      frameId = requestAnimationFrame(render);
    };

    render();
    return () => cancelAnimationFrame(frameId);
  }, [demoState, showBBoxes, showZones]);

  return (
    <div className="h-[calc(100vh-8rem)] flex space-x-6">
      
      {/* Video Feed Area */}
      <div className="flex-1 flex flex-col bg-slate-900 border border-slate-800 rounded-xl overflow-hidden shadow-sm">
        <div className="h-12 flex items-center justify-between px-4 border-b border-slate-800 bg-slate-900/50">
          <div className="flex items-center space-x-3">
            <div className="flex items-center gap-2 text-sm font-medium text-slate-200"><Camera size={16} /> Demo Camera: Main Hall</div>
            <span className="flex items-center text-xs text-cyan-300">
              <span className="h-2 w-2 rounded-full bg-cyan-400 mr-2 animate-pulse"></span>
              {connected ? 'REAL-TIME TELEMETRY' : 'CONNECTING...'}
            </span>
          </div>
          <div className="flex items-center space-x-2">
            <button onClick={() => setShowBBoxes(!showBBoxes)} className={`p-1.5 rounded ${showBBoxes ? 'bg-blue-500/20 text-blue-400' : 'text-slate-400 hover:bg-slate-800'}`} title="Toggle Bounding Boxes">
              <Crosshair size={18} />
            </button>
            <button onClick={() => setShowZones(!showZones)} className={`p-1.5 rounded ${showZones ? 'bg-blue-500/20 text-blue-400' : 'text-slate-400 hover:bg-slate-800'}`} title="Toggle Zones">
              <Hexagon size={18} />
            </button>
            <button className="p-1.5 rounded text-slate-400 hover:bg-slate-800" title="Fullscreen">
              <Maximize size={18} />
            </button>
          </div>
        </div>
        <div className="flex-1 bg-black relative flex items-center justify-center">
          <div className="absolute left-4 top-4 z-10 flex items-center gap-2 rounded bg-amber-400/15 px-3 py-1.5 text-xs font-bold tracking-wide text-amber-300 ring-1 ring-amber-400/30"><AlertTriangle size={14} /> SIMULATION MODE</div>
          <div className="absolute right-4 top-4 z-10 rounded bg-slate-950/80 px-3 py-1.5 font-mono text-xs text-slate-300">DEMO-CAM-01 | 2 FPS</div>
          <canvas 
            ref={canvasRef} 
            width={800} 
            height={450} 
            className="w-full h-full object-contain"
          />
        </div>
      </div>

      {/* Right Sidebar (Tracking) */}
      <div className="w-80 flex flex-col bg-slate-900 border border-slate-800 rounded-xl overflow-hidden shadow-sm">
        <div className="h-12 flex items-center px-4 border-b border-slate-800 bg-slate-900/50">
          <Layers className="w-4 h-4 mr-2 text-slate-400" />
          <span className="font-medium text-slate-200">Tracked Entities</span>
        </div>
        <div className="flex-1 overflow-y-auto p-2 scrollbar-thin">
          <div className="p-3 mb-3 border border-amber-500/30 bg-amber-500/5 rounded-lg text-xs text-amber-200 leading-5">
            This feed is a deterministic test scenario. It is not camera-derived and does not present synthetic output as AI inference.
          </div>
          <div className="p-3 mb-2 bg-slate-800/50 border border-slate-700/50 rounded-lg transition-colors">
               <div className="flex justify-between items-start mb-2">
                <span className="font-mono text-sm font-semibold text-blue-400">{demoState.person_id}</span>
                <StatusBadge severity={demoState.risk_level} />
               </div>
               <div className="text-sm text-slate-400">
                Activity: <span className="text-slate-200">{demoState.activity}</span>
                </div>
               <div className="mt-1 text-sm text-slate-400">Velocity: <span className="text-slate-200">{demoState.velocity.toFixed(1)} m/s</span></div>
               <div className="mt-1 text-sm text-slate-400">Zone: <span className="text-slate-200">{demoState.zone}</span></div>
             </div>
          <div className="mt-3 rounded-lg border border-slate-700/60 bg-slate-950/50 p-3">
            <div className="mb-2 flex items-center gap-2 text-sm font-medium text-slate-200"><ShieldAlert size={16} className="text-cyan-400" /> Predictive insight</div>
            <p className="text-sm text-slate-300">{demoState.prediction}</p>
            {demoState.prediction_probability && <p className="mt-1 text-xs text-slate-400">Probability: {Math.round(demoState.prediction_probability * 100)}% | Horizon: ~{demoState.prediction_horizon_seconds}s</p>}
            <p className="mt-2 text-xs leading-5 text-slate-500">{demoState.explanation}</p>
          </div>
        </div>
      </div>

    </div>
  );
}

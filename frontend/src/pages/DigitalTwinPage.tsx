import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Layers } from 'lucide-react';
import { useWebSocket } from '../hooks/useWebSocket';

export function DigitalTwinPage() {
  const navigate = useNavigate();
  useWebSocket('digital-twin');
  const [time, setTime] = useState(Date.now());

  // Force re-render for animation
  useEffect(() => {
    const id = setInterval(() => setTime(Date.now()), 50);
    return () => clearInterval(id);
  }, []);

  // Mock Twin logic
  const t = time / 1000;
  const p1x = 400 + Math.sin(t * 0.5) * 150;
  const p1y = 300 + Math.cos(t * 0.5) * 100;
  
  const p2x = 600 + Math.cos(t * 0.8) * 120;
  const p2y = 400 + Math.sin(t * 0.8) * 80;

  return (
    <div className="h-[calc(100vh-8rem)] flex flex-col bg-slate-900 border border-slate-800 rounded-xl overflow-hidden shadow-sm">
      <div className="h-12 flex items-center px-4 border-b border-slate-800 bg-slate-900/50">
        <Layers className="w-4 h-4 mr-2 text-blue-400" />
        <span className="font-medium text-slate-200">2D Environment View - Top Down</span>
        <div className="ml-auto flex items-center space-x-4 text-xs text-slate-400">
          <div className="flex items-center"><span className="w-3 h-3 rounded-full bg-blue-500 mr-2"></span> Person</div>
          <div className="flex items-center"><span className="w-3 h-3 border-2 border-slate-500 mr-2"></span> Camera FOV</div>
          <div className="flex items-center"><span className="w-3 h-3 bg-red-500/20 border border-red-500 mr-2"></span> Restricted Zone</div>
        </div>
      </div>
      
      <div className="flex-1 relative bg-[#020617] overflow-hidden">
        {/* SVG Grid and map */}
        <svg width="100%" height="100%" xmlns="http://www.w3.org/2000/svg">
          <defs>
            <pattern id="grid" width="40" height="40" patternUnits="userSpaceOnUse">
              <path d="M 40 0 L 0 0 0 40" fill="none" stroke="#1e293b" strokeWidth="1"/>
            </pattern>
          </defs>
          <rect width="100%" height="100%" fill="url(#grid)" />
          
          {/* Walls / Structure */}
          <path d="M 100 100 L 900 100 L 900 600 L 500 600 L 500 400 L 100 400 Z" fill="none" stroke="#475569" strokeWidth="4" />
          <text x="120" y="130" fill="#64748b" fontFamily="sans-serif" fontSize="14">Main Sector 1</text>
          
          {/* Restriced Zone */}
          <polygon points="700,100 900,100 900,300 700,300" fill="rgba(239, 68, 68, 0.1)" stroke="#ef4444" strokeWidth="2" strokeDasharray="5,5" />
          <text x="710" y="130" fill="#ef4444" fontFamily="sans-serif" fontSize="12">Restricted Area</text>
          
          {/* Cameras */}
          <circle cx="100" cy="100" r="10" fill="#334155" />
          <polygon points="100,100 250,50 250,250" fill="rgba(255,255,255,0.02)" stroke="#334155" strokeWidth="1" />
          <circle cx="900" cy="600" r="10" fill="#334155" />
          <polygon points="900,600 700,450 700,750" fill="rgba(255,255,255,0.02)" stroke="#334155" strokeWidth="1" />

          {/* Persons */}
          <g transform={`translate(${p1x}, ${p1y})`} className="cursor-pointer" onClick={() => navigate('/persons/p-101')}>
            <circle cx="0" cy="0" r="12" fill="#3b82f6" />
            <circle cx="0" cy="0" r="16" fill="none" stroke="#3b82f6" strokeWidth="1" opacity="0.5" />
            <text x="18" y="4" fill="#94a3b8" fontSize="12">T-801</text>
          </g>

          <g transform={`translate(${p2x}, ${p2y})`} className="cursor-pointer" onClick={() => navigate('/persons/p-102')}>
            <circle cx="0" cy="0" r="12" fill="#f97316" />
            <circle cx="0" cy="0" r="24" fill="rgba(249, 115, 22, 0.2)" />
            <text x="18" y="4" fill="#f97316" fontSize="12">T-802 (High Risk)</text>
          </g>

        </svg>
      </div>
    </div>
  );
}

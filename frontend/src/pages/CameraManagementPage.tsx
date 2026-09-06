import { Plus, Video, Trash2, Edit2, PlayCircle } from 'lucide-react';
import type { Camera } from '../types';

const mockCameras: Camera[] = [
  { id: '1', name: 'Main Hall', sourceType: 'RTSP' as any, sourceUrl: 'rtsp://192.168.1.100:554/stream1', status: 'ONLINE', environment: 'default' },
  { id: '2', name: 'Server Room', sourceType: 'RTSP' as any, sourceUrl: 'rtsp://192.168.1.101:554/stream1', status: 'ONLINE', environment: 'default' },
  { id: '3', name: 'Loading Dock', sourceType: 'HTTP' as any, sourceUrl: 'http://192.168.1.102/video', status: 'OFFLINE', environment: 'default' },
];

export function CameraManagementPage() {
  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center bg-slate-900 border border-slate-800 rounded-xl p-4 shadow-sm">
        <h2 className="text-lg font-medium text-slate-100">Connected Cameras</h2>
        <button 
          className="flex items-center px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors text-sm font-medium"
        >
          <Plus className="w-4 h-4 mr-2" />
          Add Camera
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {mockCameras.map(cam => (
          <div key={cam.id} className="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden shadow-sm hover:border-slate-700 transition-colors">
            <div className="h-32 bg-slate-950 border-b border-slate-800 flex items-center justify-center relative">
              {cam.status === 'ONLINE' ? (
                <div className="text-slate-500 flex flex-col items-center">
                  <PlayCircle className="w-8 h-8 mb-2 opacity-50" />
                  <span className="text-xs uppercase tracking-wider">Preview Feed</span>
                </div>
              ) : (
                <div className="text-red-500/50 flex flex-col items-center">
                  <Video className="w-8 h-8 mb-2" />
                  <span className="text-xs uppercase tracking-wider">Offline</span>
                </div>
              )}
              <div className={`absolute top-3 right-3 px-2 py-1 rounded text-[10px] font-bold tracking-wider ${cam.status === 'ONLINE' ? 'bg-green-500/20 text-green-400 border border-green-500/30' : 'bg-red-500/20 text-red-500 border border-red-500/30'}`}>
                {cam.status}
              </div>
            </div>
            <div className="p-4">
              <h3 className="font-semibold text-slate-100 mb-1">{cam.name}</h3>
              <p className="text-xs text-slate-400 font-mono truncate mb-4">{cam.sourceUrl}</p>
              
              <div className="flex justify-between items-center border-t border-slate-800 pt-4">
                <span className="text-xs font-medium px-2 py-1 bg-slate-800 text-slate-300 rounded">{cam.sourceType}</span>
                <div className="flex space-x-2">
                  <button className="p-1.5 text-slate-400 hover:text-blue-400 transition-colors"><Edit2 size={16} /></button>
                  <button className="p-1.5 text-slate-400 hover:text-red-400 transition-colors"><Trash2 size={16} /></button>
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

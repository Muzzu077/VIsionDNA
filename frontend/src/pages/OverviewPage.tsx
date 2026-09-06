import { Camera, Users, ShieldAlert, Cpu, Activity, Clock } from 'lucide-react';
import { PieChart, Pie, Cell, BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts';
import { StatCard } from '../components/common/StatCard';
import { StatusBadge } from '../components/common/StatusBadge';
import { DataTable } from '../components/common/DataTable';
import { useWebSocket } from '../hooks/useWebSocket';

const mockRiskData = [
  { name: 'Low', value: 400, color: '#22c55e' },
  { name: 'Medium', value: 300, color: '#eab308' },
  { name: 'High', value: 100, color: '#f97316' },
  { name: 'Critical', value: 15, color: '#ef4444' },
];

const mockActivityData = [
  { name: 'Walking', count: 45 },
  { name: 'Standing', count: 25 },
  { name: 'Running', count: 10 },
  { name: 'Sitting', count: 8 },
  { name: 'Loitering', count: 5 },
];

const mockAlerts = [
  { id: '1', personId: 'p-101', severity: 'CRITICAL', message: 'Unauthorized access in Server Room', timestamp: new Date().toISOString() },
  { id: '2', personId: 'p-102', severity: 'HIGH', message: 'Running in hallway', timestamp: new Date(Date.now() - 50000).toISOString() },
];

export function OverviewPage() {
  // Using wsLive to listen for real-time generic events if needed
  useWebSocket('live');

  return (
    <div className="space-y-6 pb-8">
      {/* Stat Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6 gap-4">
        <StatCard title="Active Cameras" value="12" icon={Camera} iconColorClass="text-blue-500" />
        <StatCard title="People Detected" value="48" icon={Users} iconColorClass="text-purple-500" change={12} />
        <StatCard title="Active Alerts" value="3" icon={ShieldAlert} iconColorClass="text-red-500" change={-5} />
        <StatCard title="Average Risk" value="14%" icon={Activity} iconColorClass="text-orange-500" />
        <StatCard title="Processing FPS" value="28.4" icon={Cpu} iconColorClass="text-green-500" />
        <StatCard title="System Latency" value="112ms" icon={Clock} iconColorClass="text-indigo-500" />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mt-6">
        {/* Charts */}
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 col-span-1 lg:col-span-2 shadow-sm">
          <h3 className="text-lg font-medium text-slate-100 mb-4">Activity Distribution</h3>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={mockActivityData}>
                <XAxis dataKey="name" stroke="#94a3b8" fontSize={12} tickLine={false} axisLine={false} />
                <YAxis stroke="#94a3b8" fontSize={12} tickLine={false} axisLine={false} />
                <Tooltip 
                  cursor={{ fill: '#1e293b' }}
                  contentStyle={{ backgroundColor: '#0f172a', border: '1px solid #334155', borderRadius: '8px' }} 
                />
                <Bar dataKey="count" fill="#3b82f6" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 col-span-1 shadow-sm">
          <h3 className="text-lg font-medium text-slate-100 mb-4">Risk Level Distribution</h3>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={mockRiskData}
                  cx="50%"
                  cy="50%"
                  innerRadius={60}
                  outerRadius={80}
                  paddingAngle={5}
                  dataKey="value"
                >
                  {mockRiskData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip contentStyle={{ backgroundColor: '#0f172a', border: '1px solid #334155', borderRadius: '8px' }} />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* Tables */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mt-6">
        <div className="bg-slate-900 border border-slate-800 rounded-xl shadow-sm overflow-hidden flex flex-col">
          <div className="p-5 border-b border-slate-800">
            <h3 className="text-lg font-medium text-slate-100">Recent Alerts</h3>
          </div>
          <div className="p-0 flex-1">
            <DataTable 
              data={mockAlerts}
              columns={[
                { header: 'Severity', accessor: (row) => <StatusBadge severity={row.severity} /> },
                { header: 'Message', accessor: 'message' },
                { header: 'Time', accessor: (row) => new Date(row.timestamp).toLocaleTimeString() }
              ]}
            />
          </div>
        </div>

        <div className="bg-slate-900 border border-slate-800 rounded-xl shadow-sm overflow-hidden flex flex-col">
          <div className="p-5 border-b border-slate-800">
            <h3 className="text-lg font-medium text-slate-100">System Health Overview</h3>
          </div>
          <div className="p-5 flex-1 grid grid-cols-2 gap-4">
             <div className="p-4 bg-slate-800 rounded-lg flex items-center justify-between">
                <span className="text-slate-300">Camera Service</span>
                <span className="h-3 w-3 rounded-full bg-green-500 shadow-[0_0_8px_rgba(34,197,94,0.8)]"></span>
             </div>
             <div className="p-4 bg-slate-800 rounded-lg flex items-center justify-between">
                <span className="text-slate-300">Inference Engine</span>
                <span className="h-3 w-3 rounded-full bg-green-500 shadow-[0_0_8px_rgba(34,197,94,0.8)]"></span>
             </div>
             <div className="p-4 bg-slate-800 rounded-lg flex items-center justify-between">
                <span className="text-slate-300">Database</span>
                <span className="h-3 w-3 rounded-full bg-green-500 shadow-[0_0_8px_rgba(34,197,94,0.8)]"></span>
             </div>
             <div className="p-4 bg-slate-800 rounded-lg flex items-center justify-between">
                <span className="text-slate-300">Digital Twin Sync</span>
                <span className="h-3 w-3 rounded-full bg-yellow-500 shadow-[0_0_8px_rgba(234,179,8,0.8)]"></span>
             </div>
          </div>
        </div>
      </div>
    </div>
  );
}

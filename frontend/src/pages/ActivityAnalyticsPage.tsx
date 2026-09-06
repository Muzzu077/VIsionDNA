import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip, AreaChart, Area, XAxis, YAxis } from 'recharts';
import { Activity } from 'lucide-react';

const mockActivityData = [
  { name: 'Walking', value: 400, color: '#3b82f6' },
  { name: 'Standing', value: 300, color: '#8b5cf6' },
  { name: 'Running', value: 100, color: '#f97316' },
  { name: 'Sitting', value: 200, color: '#10b981' },
];

const mockTimelineData = [
  { time: '08:00', Walking: 20, Standing: 10, Running: 0 },
  { time: '10:00', Walking: 40, Standing: 15, Running: 5 },
  { time: '12:00', Walking: 10, Standing: 40, Running: 2 },
  { time: '14:00', Walking: 30, Standing: 20, Running: 10 },
  { time: '16:00', Walking: 15, Standing: 5, Running: 0 },
];

export function ActivityAnalyticsPage() {
  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-sm">
          <h3 className="text-lg font-medium text-slate-100 mb-4 flex items-center">
            <Activity className="w-5 h-5 mr-2 text-blue-500" />
            Activity Distribution
          </h3>
          <div className="h-72">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie data={mockActivityData} innerRadius={80} outerRadius={110} paddingAngle={5} dataKey="value">
                  {mockActivityData.map((entry, index) => <Cell key={`cell-${index}`} fill={entry.color} />)}
                </Pie>
                <Tooltip contentStyle={{ backgroundColor: '#0f172a', border: '1px solid #334155', borderRadius: '8px' }} />
              </PieChart>
            </ResponsiveContainer>
          </div>
          <div className="flex flex-wrap justify-center gap-4 mt-4">
            {mockActivityData.map(item => (
               <div key={item.name} className="flex items-center text-sm text-slate-300">
                  <span className="w-3 h-3 rounded-full mr-2" style={{ backgroundColor: item.color }}></span>
                  {item.name} ({item.value})
               </div>
            ))}
          </div>
        </div>

        <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-sm">
          <h3 className="text-lg font-medium text-slate-100 mb-4">Activity Over Time</h3>
          <div className="h-72">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={mockTimelineData}>
                <XAxis dataKey="time" stroke="#94a3b8" fontSize={12} tickLine={false} axisLine={false} />
                <YAxis stroke="#94a3b8" fontSize={12} tickLine={false} axisLine={false} />
                <Tooltip contentStyle={{ backgroundColor: '#0f172a', border: '1px solid #334155', borderRadius: '8px' }} />
                <Area type="monotone" dataKey="Walking" stackId="1" stroke="#3b82f6" fill="#3b82f6" fillOpacity={0.6} />
                <Area type="monotone" dataKey="Standing" stackId="1" stroke="#8b5cf6" fill="#8b5cf6" fillOpacity={0.6} />
                <Area type="monotone" dataKey="Running" stackId="1" stroke="#f97316" fill="#f97316" fillOpacity={0.6} />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
    </div>
  );
}

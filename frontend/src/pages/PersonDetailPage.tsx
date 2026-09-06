import { useParams, useNavigate } from 'react-router-dom';
import { ArrowLeft, User, Activity, MapPin, Clock } from 'lucide-react';
import { StatusBadge } from '../components/common/StatusBadge';
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts';

const mockRiskHistory = [
  { time: '10:00', risk: 10 },
  { time: '10:05', risk: 15 },
  { time: '10:10', risk: 12 },
  { time: '10:15', risk: 80 },
  { time: '10:20', risk: 75 },
];

export function PersonDetailPage() {
  const { id } = useParams();
  const navigate = useNavigate();

  return (
    <div className="space-y-6 pb-8">
      <div className="flex items-center space-x-4">
        <button onClick={() => navigate(-1)} className="p-2 bg-slate-900 border border-slate-800 rounded-lg hover:bg-slate-800 transition-colors">
          <ArrowLeft className="w-5 h-5 text-slate-400" />
        </button>
        <div>
          <h2 className="text-2xl font-semibold text-slate-100 flex items-center">
            Entity Details <span className="ml-3 text-sm font-mono bg-slate-800 px-2 py-1 rounded text-blue-400">{id}</span>
          </h2>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column: State Card */}
        <div className="space-y-6">
          <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-sm">
            <h3 className="text-lg font-medium text-slate-100 mb-4 flex items-center">
              <User className="w-5 h-5 mr-2 text-blue-500" />
              Current State
            </h3>
            
            <div className="space-y-4">
              <div className="flex justify-between items-center py-2 border-b border-slate-800">
                <span className="text-slate-400">Risk Level</span>
                <StatusBadge severity="HIGH" />
              </div>
              <div className="flex justify-between items-center py-2 border-b border-slate-800">
                <span className="text-slate-400">Current Activity</span>
                <span className="text-slate-200 flex items-center"><Activity className="w-4 h-4 mr-1 text-slate-500" /> Running</span>
              </div>
              <div className="flex justify-between items-center py-2 border-b border-slate-800">
                <span className="text-slate-400">Location (x, y)</span>
                <span className="text-slate-200 flex items-center font-mono"><MapPin className="w-4 h-4 mr-1 text-slate-500" /> [12.4, 45.1]</span>
              </div>
              <div className="flex justify-between items-center py-2">
                <span className="text-slate-400">Zone</span>
                <span className="text-red-400 text-sm font-semibold">RESTRICTED AREA</span>
              </div>
            </div>
          </div>

          <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-sm">
            <h3 className="text-lg font-medium text-slate-100 mb-4 flex items-center">
              <Clock className="w-5 h-5 mr-2 text-purple-500" />
              Predictions
            </h3>
            <div className="p-3 bg-red-500/10 border border-red-500/20 rounded-lg">
              <div className="text-red-400 font-medium mb-1">High Probability of Collision</div>
              <div className="text-sm text-slate-400">Horizon: 15 seconds</div>
              <div className="mt-2 w-full bg-slate-800 rounded-full h-2">
                <div className="bg-red-500 h-2 rounded-full" style={{ width: '85%' }}></div>
              </div>
              <div className="text-right text-xs mt-1 text-slate-500">85% Confidence</div>
            </div>
          </div>
        </div>

        {/* Right Column: Charts & Logs */}
        <div className="col-span-1 lg:col-span-2 space-y-6">
          <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-sm">
            <h3 className="text-lg font-medium text-slate-100 mb-4">Risk History</h3>
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={mockRiskHistory}>
                  <XAxis dataKey="time" stroke="#94a3b8" fontSize={12} tickLine={false} axisLine={false} />
                  <YAxis stroke="#94a3b8" fontSize={12} tickLine={false} axisLine={false} />
                  <Tooltip 
                    contentStyle={{ backgroundColor: '#0f172a', border: '1px solid #334155', borderRadius: '8px' }} 
                  />
                  <Line type="monotone" dataKey="risk" stroke="#f97316" strokeWidth={3} dot={{ r: 4, fill: '#f97316' }} />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </div>
          
          <div className="bg-slate-900 border border-slate-800 rounded-xl shadow-sm overflow-hidden flex flex-col">
            <div className="p-5 border-b border-slate-800">
              <h3 className="text-lg font-medium text-slate-100">Activity Logs</h3>
            </div>
            <div className="p-0">
              <table className="min-w-full divide-y divide-slate-800">
                <tbody className="bg-slate-900 divide-y divide-slate-800">
                  <tr className="px-6 py-4">
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-400">10:15:23</td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-200">Entered Restricted Zone</td>
                  </tr>
                  <tr className="px-6 py-4">
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-400">10:15:20</td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-200">Activity change: Walking &rarr; Running</td>
                  </tr>
                  <tr className="px-6 py-4">
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-400">10:12:00</td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-200">Appeared in Main Hall Camera</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

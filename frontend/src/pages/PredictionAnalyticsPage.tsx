import { TrendingUp, CheckCircle, XCircle, HelpCircle } from 'lucide-react';
import { DataTable } from '../components/common/DataTable';

const mockPredictions = [
  { id: '1', predictedEvent: 'Collision in loading dock', probability: 0.85, horizonSeconds: 15, actualOutcome: true, correctness: true },
  { id: '2', predictedEvent: 'Unauthorized zone entry', probability: 0.65, horizonSeconds: 30, actualOutcome: false, correctness: false },
  { id: '3', predictedEvent: 'Crowd formation', probability: 0.90, horizonSeconds: 60, actualOutcome: undefined, correctness: undefined },
];

export function PredictionAnalyticsPage() {
  const columns = [
    { header: 'Event Predicted', accessor: 'predictedEvent' },
    { 
      header: 'Probability', 
      accessor: (row: any) => (
        <div className="flex items-center">
          <div className="w-16 bg-slate-800 rounded-full h-2 mr-2">
            <div className="bg-blue-500 h-2 rounded-full" style={{ width: `${row.probability * 100}%` }}></div>
          </div>
          <span className="text-xs text-slate-400">{(row.probability * 100).toFixed(0)}%</span>
        </div>
      ) 
    },
    { header: 'Horizon', accessor: (row: any) => `${row.horizonSeconds}s` },
    { 
      header: 'Result (Accuracy)', 
      accessor: (row: any) => {
        if (row.correctness === true) return <span className="text-green-400 flex items-center"><CheckCircle className="w-4 h-4 mr-1" /> Accurate</span>;
        if (row.correctness === false) return <span className="text-red-400 flex items-center"><XCircle className="w-4 h-4 mr-1" /> False Alarm</span>;
        return <span className="text-slate-500 flex items-center"><HelpCircle className="w-4 h-4 mr-1" /> Pending Evaluate</span>;
      } 
    },
  ];

  return (
    <div className="space-y-6">
      
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
         <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-sm flex items-center">
            <div className="p-3 rounded-lg bg-blue-500/10 text-blue-500 mr-4"><TrendingUp className="w-6 h-6" /></div>
            <div>
              <p className="text-sm font-medium text-slate-400">Total Predictions</p>
              <p className="text-2xl font-semibold text-slate-100">1,248</p>
            </div>
         </div>
         <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-sm flex items-center">
            <div className="p-3 rounded-lg bg-green-500/10 text-green-500 mr-4"><CheckCircle className="w-6 h-6" /></div>
            <div>
              <p className="text-sm font-medium text-slate-400">Model Accuracy</p>
              <p className="text-2xl font-semibold text-slate-100">92.4%</p>
            </div>
         </div>
         <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-sm flex items-center">
            <div className="p-3 rounded-lg bg-orange-500/10 text-orange-500 mr-4"><HelpCircle className="w-6 h-6" /></div>
            <div>
              <p className="text-sm font-medium text-slate-400">Average Horizon</p>
              <p className="text-2xl font-semibold text-slate-100">24.5s</p>
            </div>
         </div>
      </div>

      <div className="bg-slate-900 border border-slate-800 rounded-xl shadow-sm overflow-hidden flex flex-col">
          <div className="p-5 border-b border-slate-800 flex justify-between items-center">
            <h3 className="text-lg font-medium text-slate-100">Prediction Logs</h3>
          </div>
          <div className="p-0">
            <DataTable data={mockPredictions} columns={columns} />
          </div>
      </div>
    </div>
  );
}

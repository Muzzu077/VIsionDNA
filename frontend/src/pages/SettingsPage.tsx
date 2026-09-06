import { Save } from 'lucide-react';

export function SettingsPage() {
  return (
    <div className="max-w-4xl space-y-8">
      
      {/* Risk Configuration */}
      <section className="bg-slate-900 border border-slate-800 rounded-xl shadow-sm overflow-hidden">
        <div className="px-6 py-4 border-b border-slate-800">
          <h2 className="text-lg font-medium text-slate-100">Risk Calculation Weights</h2>
          <p className="text-sm text-slate-400">Adjust how much each factor contributes to the final risk score.</p>
        </div>
        <div className="p-6 space-y-6">
          
          <div>
            <div className="flex justify-between mb-1">
              <label className="text-sm font-medium text-slate-300">Activity Severity</label>
              <span className="text-sm text-slate-400">40%</span>
            </div>
            <input type="range" min="0" max="100" defaultValue="40" className="w-full h-2 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-blue-500" />
          </div>

          <div>
            <div className="flex justify-between mb-1">
              <label className="text-sm font-medium text-slate-300">Zone Violation</label>
              <span className="text-sm text-slate-400">30%</span>
            </div>
            <input type="range" min="0" max="100" defaultValue="30" className="w-full h-2 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-blue-500" />
          </div>

          <div>
            <div className="flex justify-between mb-1">
              <label className="text-sm font-medium text-slate-300">Proximity Risk</label>
              <span className="text-sm text-slate-400">20%</span>
            </div>
            <input type="range" min="0" max="100" defaultValue="20" className="w-full h-2 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-blue-500" />
          </div>
          
          <div>
            <div className="flex justify-between mb-1">
              <label className="text-sm font-medium text-slate-300">Anomaly/Behavior Score</label>
              <span className="text-sm text-slate-400">10%</span>
            </div>
            <input type="range" min="0" max="100" defaultValue="10" className="w-full h-2 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-blue-500" />
          </div>

        </div>
      </section>

      {/* Inference & Predictions */}
      <section className="bg-slate-900 border border-slate-800 rounded-xl shadow-sm overflow-hidden">
         <div className="px-6 py-4 border-b border-slate-800">
          <h2 className="text-lg font-medium text-slate-100">Inference & Prediction</h2>
        </div>
        <div className="p-6 grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <label className="block text-sm font-medium text-slate-300 mb-2">Detection Confidence Threshold</label>
            <input type="number" defaultValue="0.65" step="0.05" className="px-3 py-2 bg-slate-800 border border-slate-700 rounded-lg w-full text-slate-100 focus:outline-none focus:border-blue-500" />
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-300 mb-2">Prediction Horizon (seconds)</label>
            <input type="number" defaultValue="30" className="px-3 py-2 bg-slate-800 border border-slate-700 rounded-lg w-full text-slate-100 focus:outline-none focus:border-blue-500" />
          </div>
        </div>
      </section>

      <div className="flex justify-end">
        <button className="flex items-center px-6 py-2.5 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors font-medium">
          <Save className="w-4 h-4 mr-2" />
          Save Settings
        </button>
      </div>

    </div>
  );
}

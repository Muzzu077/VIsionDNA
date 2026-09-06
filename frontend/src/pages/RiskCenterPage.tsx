import { useState } from 'react';
import { Search, Filter } from 'lucide-react';
import { DataTable } from '../components/common/DataTable';
import { StatusBadge } from '../components/common/StatusBadge';
import { formatDate } from '../utils/format';

const mockRisks = [
  { id: '1', personId: 'p-101', severity: 'CRITICAL', type: 'Zone Violation', timestamp: new Date().toISOString(), status: 'ACTIVE', explanation: { primary_reason: 'Person entered Server Room' } },
  { id: '2', personId: 'p-102', severity: 'HIGH', type: 'Abnormal Behavior', timestamp: new Date(Date.now() - 3600000).toISOString(), status: 'ACTIVE', explanation: { primary_reason: 'Running in corridor' } },
  { id: '3', personId: 'p-105', severity: 'MEDIUM', type: 'Proximity', timestamp: new Date(Date.now() - 7200000).toISOString(), status: 'ACKNOWLEDGED', explanation: { primary_reason: 'Too close to machinery' } },
];

export function RiskCenterPage() {
  const [searchTerm, setSearchTerm] = useState('');

  const columns = [
    { header: 'Severity', accessor: (row: any) => <StatusBadge severity={row.severity} /> },
    { header: 'Risk Type', accessor: 'type' },
    { header: 'Explanation', accessor: (row: any) => <span className="text-slate-300">{row.explanation.primary_reason}</span> },
    { header: 'Person ID', accessor: (row: any) => <span className="font-mono text-blue-400">{row.personId}</span> },
    { header: 'Time', accessor: (row: any) => <span className="text-slate-400">{formatDate(row.timestamp)}</span> },
    { 
      header: 'Actions', 
      accessor: (row: any) => (
        <button 
          className="px-3 py-1 bg-blue-500/10 text-blue-400 border border-blue-500/20 rounded hover:bg-blue-500/20 transition-colors text-xs"
          disabled={row.status === 'ACKNOWLEDGED'}
        >
          {row.status === 'ACKNOWLEDGED' ? 'Acked' : 'Acknowledge'}
        </button>
      ) 
    },
  ];

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center bg-slate-900 border border-slate-800 rounded-xl p-4 shadow-sm">
        <div className="flex items-center space-x-4">
          <div className="relative">
            <Search className="w-5 h-5 absolute left-3 top-2.5 text-slate-500" />
            <input 
              type="text" 
              placeholder="Search risks..." 
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="pl-10 pr-4 py-2 bg-slate-800 border border-slate-700 rounded-lg text-sm focus:outline-none focus:border-blue-500 text-slate-100 w-64"
            />
          </div>
          <button className="flex items-center px-4 py-2 bg-slate-800 border border-slate-700 rounded-lg text-sm text-slate-300 hover:bg-slate-700 transition-colors">
            <Filter className="w-4 h-4 mr-2" /> Filter
          </button>
        </div>
      </div>

      <div className="bg-slate-900 border border-slate-800 rounded-xl shadow-sm overflow-hidden">
        <DataTable data={mockRisks} columns={columns} />
      </div>
    </div>
  );
}

import { Plus, Hexagon, Trash2, Edit2 } from 'lucide-react';
import { DataTable } from '../components/common/DataTable';
import { StatusBadge } from '../components/common/StatusBadge';

const mockZones = [
  { id: '1', name: 'Server Room', type: 'RESTRICTED', riskLevel: 'CRITICAL', color: '#ef4444', points: [[10, 10], [10, 20], [20, 20]] },
  { id: '2', name: 'Lobby', type: 'SAFE', riskLevel: 'LOW', color: '#22c55e', points: [[10, 10], [10, 20], [20, 20]] },
];

export function ZoneManagementPage() {
  const columns = [
    { 
      header: 'Color', 
      accessor: (row: any) => (
        <span className="w-4 h-4 rounded block" style={{ backgroundColor: row.color }}></span>
      ) 
    },
    { header: 'Zone Name', accessor: 'name' },
    { 
      header: 'Type', 
      accessor: (row: any) => (
        <span className="px-2 py-1 bg-slate-800 text-slate-300 rounded text-xs">{row.type}</span>
      ) 
    },
    { header: 'Associated Risk', accessor: (row: any) => <StatusBadge severity={row.riskLevel} /> },
    { 
      header: 'Actions', 
      accessor: () => (
        <div className="flex space-x-2">
          <button className="p-1.5 text-slate-400 hover:text-blue-400 transition-colors"><Edit2 size={16} /></button>
          <button className="p-1.5 text-slate-400 hover:text-red-400 transition-colors"><Trash2 size={16} /></button>
        </div>
      ) 
    },
  ];

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center bg-slate-900 border border-slate-800 rounded-xl p-4 shadow-sm">
        <h2 className="text-lg font-medium text-slate-100 flex items-center">
          <Hexagon className="w-5 h-5 mr-2 text-indigo-500" />
          Defined Zones
        </h2>
        <button className="flex items-center px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors text-sm font-medium">
          <Plus className="w-4 h-4 mr-2" />
          Create Zone
        </button>
      </div>

      <div className="bg-slate-900 border border-slate-800 rounded-xl shadow-sm overflow-hidden">
        <DataTable data={mockZones} columns={columns} />
      </div>
    </div>
  );
}

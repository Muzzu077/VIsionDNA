import { Shield, AlertTriangle, AlertCircle, AlertOctagon } from 'lucide-react';
import type { RiskSeverity } from '../../types';
import { classNames } from '../../utils/format';

interface Props {
  severity: RiskSeverity | string;
  className?: string;
  showIcon?: boolean;
}

export function StatusBadge({ severity, className, showIcon = true }: Props) {
  const upperSev = severity.toUpperCase() as RiskSeverity;

  let colorClass = 'bg-slate-800 text-slate-300 border-slate-600';
  let Icon = Shield;

  switch (upperSev) {
    case 'LOW':
      colorClass = 'bg-green-500/10 text-green-400 border-green-500/20';
      Icon = Shield;
      break;
    case 'MEDIUM':
      colorClass = 'bg-yellow-500/10 text-yellow-400 border-yellow-500/20';
      Icon = AlertTriangle;
      break;
    case 'HIGH':
      colorClass = 'bg-orange-500/10 text-orange-400 border-orange-500/20';
      Icon = AlertCircle;
      break;
    case 'CRITICAL':
      colorClass = 'bg-red-500/10 text-red-500 border-red-500/20';
      Icon = AlertOctagon;
      break;
  }

  return (
    <span className={classNames("inline-flex items-center px-2 py-1 rounded-md border text-xs font-medium uppercase", colorClass, className)}>
      {showIcon && <Icon className="w-3 h-3 mr-1.5" />}
      {upperSev}
    </span>
  );
}

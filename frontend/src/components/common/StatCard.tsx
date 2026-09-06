import type { LucideIcon } from 'lucide-react';
import { classNames } from '../../utils/format';

interface Props {
  title: string;
  value: string | number;
  icon: LucideIcon;
  change?: number;
  changeLabel?: string;
  className?: string;
  iconColorClass?: string;
}

export function StatCard({ title, value, icon: Icon, change, changeLabel, className, iconColorClass = "text-blue-500" }: Props) {
  return (
    <div className={classNames("bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-sm", className)}>
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-medium text-slate-400">{title}</h3>
        <div className={classNames("p-2 rounded-lg bg-slate-800/50", iconColorClass)}>
          <Icon className="w-5 h-5" />
        </div>
      </div>
      
      <div className="mt-4 flex items-baseline">
        <p className="text-2xl font-semibold text-slate-100">{value}</p>
        
        {change !== undefined && (
          <p className={classNames(
            "ml-2 flex items-baseline text-sm font-medium",
            change > 0 ? "text-green-400" : change < 0 ? "text-red-400" : "text-slate-500"
          )}>
            {change > 0 ? '+' : ''}{change}%
            {changeLabel && <span className="text-slate-500 ml-1 font-normal">{changeLabel}</span>}
          </p>
        )}
      </div>
    </div>
  );
}

import { classNames } from '../../utils/format';

interface Column<T> {
  header: string;
  accessor: Extract<keyof T, string> | string | ((row: T) => React.ReactNode);
  className?: string;
}

interface Props<T> {
  data: T[];
  columns: Column<T>[];
  onRowClick?: (row: T) => void;
  isLoading?: boolean;
}

export function DataTable<T extends { id: string | number }>({ data, columns, onRowClick, isLoading }: Props<T>) {
  if (isLoading) {
    return (
      <div className="w-full h-48 flex items-center justify-center border border-slate-800 rounded-lg bg-slate-900/50">
        <div className="animate-spin rounded-full h-8 w-8 border-t-2 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  if (data.length === 0) {
    return (
      <div className="w-full text-center py-10 border border-slate-800 rounded-lg bg-slate-900/50 text-slate-400">
        No data available
      </div>
    );
  }

  return (
    <div className="overflow-x-auto rounded-lg border border-slate-800">
      <table className="min-w-full divide-y divide-slate-800">
        <thead className="bg-slate-800/50">
          <tr>
            {columns.map((col, i) => (
              <th
                key={i}
                className={classNames(
                  "px-6 py-3 text-left text-xs font-medium text-slate-400 uppercase tracking-wider",
                  col.className
                )}
              >
                {col.header}
              </th>
            ))}
          </tr>
        </thead>
        <tbody className="bg-slate-900 divide-y divide-slate-800">
          {data.map((row) => (
            <tr
              key={row.id}
              onClick={() => onRowClick && onRowClick(row)}
              className={classNames(
                "transition-colors",
                onRowClick ? "cursor-pointer hover:bg-slate-800/70" : ""
              )}
            >
              {columns.map((col, i) => (
                <td key={i} className={classNames("px-6 py-4 whitespace-nowrap text-sm text-slate-300", col.className)}>
                  {typeof col.accessor === 'function' ? col.accessor(row) : (row[col.accessor as keyof T] as any)}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

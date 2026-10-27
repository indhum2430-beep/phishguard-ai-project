import React from 'react';
import { History, Trash2 } from 'lucide-react';

export default function ScanHistory({ history, onClear }) {
  if (history.length === 0) return null;

  return (
    <div className="bg-slate-900/60 border border-slate-800/80 rounded-2xl p-6 space-y-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <History className="w-4 h-4 text-cyan-400" />
          <h3 className="text-sm font-bold text-slate-200 uppercase tracking-wider font-mono">Session Audit Log</h3>
        </div>
        <button
          onClick={onClear}
          className="text-xs text-slate-500 hover:text-rose-400 flex items-center gap-1 font-mono transition-colors cursor-pointer"
        >
          <Trash2 className="w-3.5 h-3.5" /> CLEAR
        </button>
      </div>

      <div className="space-y-2 max-h-52 overflow-y-auto pr-1">
        {history.map((item, idx) => (
          <div key={idx} className="flex items-center justify-between bg-slate-950/80 p-3 rounded-xl border border-slate-800/50 text-xs font-mono">
            <span className="text-slate-300 truncate max-w-[220px] sm:max-w-md">{item.target}</span>
            <div className="flex items-center gap-3">
              <span className="text-[10px] text-slate-500">{item.timestamp}</span>
              <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                item.status === 'CRITICAL' ? 'bg-rose-500/20 text-rose-400' :
                item.status === 'SUSPICIOUS' ? 'bg-amber-500/20 text-amber-400' : 'bg-emerald-500/20 text-emerald-400'
              }`}>
                {item.status}
              </span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
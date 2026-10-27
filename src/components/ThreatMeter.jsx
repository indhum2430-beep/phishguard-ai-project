import React from 'react';

export default function ThreatMeter({ score, status }) {
  const getColors = () => {
    if (status === 'CRITICAL') return { text: 'text-rose-400', stroke: '#f43f5e', bg: 'bg-rose-500/10', border: 'border-rose-500/30' };
    if (status === 'SUSPICIOUS') return { text: 'text-amber-400', stroke: '#f59e0b', bg: 'bg-amber-500/10', border: 'border-amber-500/30' };
    return { text: 'text-emerald-400', stroke: '#10b981', bg: 'bg-emerald-500/10', border: 'border-emerald-500/30' };
  };

  const colors = getColors();
  const strokeDashoffset = 283 - (283 * score) / 100;

  return (
    <div className={`p-6 rounded-2xl bg-slate-900/90 border ${colors.border} flex flex-col items-center justify-center relative overflow-hidden`}>
      <div className="relative w-36 h-36 flex items-center justify-center">
        <svg className="w-full h-full transform -rotate-90">
          <circle cx="72" cy="72" r="45" stroke="currentColor" strokeWidth="8" className="text-slate-800" fill="transparent" />
          <circle
            cx="72"
            cy="72"
            r="45"
            stroke={colors.stroke}
            strokeWidth="8"
            strokeDasharray="283"
            strokeDashoffset={strokeDashoffset}
            strokeLinecap="round"
            fill="transparent"
            className="transition-all duration-1000 ease-out"
          />
        </svg>
        <div className="absolute flex flex-col items-center">
          <span className={`text-3xl font-black font-mono ${colors.text}`}>{score}</span>
          <span className="text-[10px] text-slate-500 font-mono tracking-widest">INDEX</span>
        </div>
      </div>

      <div className={`mt-4 px-4 py-1 rounded-full border font-mono text-xs font-bold tracking-widest uppercase ${colors.bg} ${colors.text} ${colors.border}`}>
        {status}
      </div>
    </div>
  );
}
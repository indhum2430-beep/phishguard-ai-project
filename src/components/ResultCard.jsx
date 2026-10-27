import React from 'react';
import ThreatMeter from './ThreatMeter';
import { ShieldCheck, ShieldAlert, Cpu, Activity, CheckCircle2, AlertTriangle } from 'lucide-react';

export default function ResultCard({ result, url }) {
  if (!result) {
    return (
      <div className="bg-slate-900/40 border border-slate-800/60 rounded-2xl p-8 text-center backdrop-blur-md">
        <Cpu className="w-10 h-10 text-cyan-500/40 mx-auto mb-3 animate-pulse" />
        <h3 className="text-slate-300 font-semibold text-sm">ML Classifier Standby</h3>
        <p className="text-slate-500 text-xs mt-1 max-w-sm mx-auto">
          Enter a URL above and hit scan to trigger real-time feature extraction and Random Forest prediction.
        </p>
      </div>
    );
  }

  return (
    <div className="bg-slate-900/90 border border-slate-800 rounded-2xl p-6 shadow-2xl space-y-6 animate-fade-in">
      <div className="flex items-center justify-between border-b border-slate-800/80 pb-4">
        <div className="flex items-center gap-2">
          <Activity className="w-4 h-4 text-cyan-400" />
          <span className="text-xs font-mono font-bold text-slate-300 uppercase tracking-widest">
            ML Prediction Breakdown
          </span>
        </div>
        <div className="flex items-center gap-2 bg-cyan-950/50 border border-cyan-500/30 px-3 py-1 rounded-full text-[11px] font-mono text-cyan-400">
          <span>Model Accuracy: {result.mlConfidence}%</span>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 items-center">
        <ThreatMeter score={result.score} status={result.status} />

        <div className="md:col-span-2 space-y-4">
          <div>
            <span className="text-[10px] font-mono text-slate-500 uppercase tracking-widest block">Scanned Target URL</span>
            <div className="font-mono text-xs text-cyan-300 break-all bg-slate-950 p-3 rounded-xl border border-slate-800/80 mt-1 flex items-center justify-between">
              <span>{url}</span>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-3 font-mono text-xs">
            <div className="bg-slate-950/60 p-3 rounded-xl border border-slate-800/60">
              <span className="text-[10px] text-slate-500 uppercase block">Classifier Engine</span>
              <span className="text-slate-200 font-bold text-[11px]">{result.algorithm}</span>
            </div>
            <div className="bg-slate-950/60 p-3 rounded-xl border border-slate-800/60">
              <span className="text-[10px] text-slate-500 uppercase block">Threat Index</span>
              <span className={`font-bold ${result.score > 50 ? 'text-rose-400' : 'text-emerald-400'}`}>
                {result.score} / 100
              </span>
            </div>
          </div>
        </div>
      </div>

      <div className="space-y-3 pt-2 border-t border-slate-800/80">
        <span className="text-[10px] font-mono text-slate-500 uppercase tracking-widest block">Extracted ML Feature Vectors</span>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
          {result.features.map((feat, idx) => (
            <div key={idx} className="p-3 bg-slate-950/80 rounded-xl border border-slate-800/60 flex items-center justify-between text-xs">
              <div className="flex items-center gap-2">
                {feat.weight !== "0%" ? (
                  <AlertTriangle className="w-4 h-4 text-amber-400 shrink-0" />
                ) : (
                  <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
                )}
                <div>
                  <div className="text-slate-200 font-medium text-[11px]">{feat.name}</div>
                  <div className="text-[10px] text-slate-400">{feat.status}</div>
                </div>
              </div>
              <span className="font-mono text-[10px] px-2 py-0.5 rounded bg-slate-900 border border-slate-800 text-slate-400">
                {feat.weight}
              </span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
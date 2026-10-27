import React from 'react';
import { Cpu, ShieldCheck } from 'lucide-react';

export default function Hero() {
  return (
    <div className="text-center space-y-4 py-4">
      <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-cyan-950/60 border border-cyan-500/30 text-cyan-400 text-xs font-mono shadow-[0_0_12px_rgba(6,182,212,0.15)]">
        <Cpu className="w-3.5 h-3.5 animate-pulse" />
        <span>ML CLASSIFIER & HEURISTIC ENGINE</span>
      </div>
      
      <h2 className="text-3xl sm:text-4xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-slate-100 via-slate-200 to-slate-400 tracking-tight max-w-2xl mx-auto leading-tight">
        Intelligent Phishing Website Detection Using Machine Learning
      </h2>
      
      <p className="text-slate-400 text-xs sm:text-sm max-w-xl mx-auto leading-relaxed">
        Real-time URL feature extraction combined with Random Forest classification to detect zero-day phishing attacks instantly.
      </p>
    </div>
  );
}
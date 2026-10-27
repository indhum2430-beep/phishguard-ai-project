import React, { useState } from 'react';
import { Search, Radar, Zap } from 'lucide-react';

export default function UrlScanner({ onScan, isScanning }) {
  const [url, setUrl] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    if (url.trim()) onScan(url);
  };

  return (
    <div className="relative group">
      <div className="absolute -inset-0.5 bg-gradient-to-r from-cyan-500 to-blue-600 rounded-2xl blur opacity-25 group-hover:opacity-50 transition duration-500"></div>
      
      <form onSubmit={handleSubmit} className="relative bg-slate-900 border border-slate-800 rounded-2xl p-4 sm:p-6 space-y-4 shadow-2xl">
        <div className="relative">
          <input
            type="text"
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            placeholder="Paste suspicious target URL (e.g. http://paypal-security-update.xyz/login)"
            className="w-full bg-slate-950/80 border border-slate-800 rounded-xl px-4 py-4 pr-12 text-slate-100 placeholder-slate-600 font-mono text-sm focus:outline-none focus:ring-2 focus:ring-cyan-500/50 focus:border-cyan-500 transition-all shadow-inner"
          />
          <Search className="absolute right-4 top-4 w-5 h-5 text-slate-600" />
        </div>

        <button
          type="submit"
          disabled={isScanning || !url.trim()}
          className="w-full py-3.5 px-6 rounded-xl font-bold text-sm tracking-wide bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-slate-950 transition-all duration-200 shadow-[0_0_20px_rgba(6,182,212,0.3)] disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2 cursor-pointer"
        >
          {isScanning ? (
            <>
              <Radar className="w-5 h-5 animate-spin" />
              INSPECTING PAYLOAD...
            </>
          ) : (
            <>
              <Zap className="w-5 h-5 fill-slate-950" />
              RUN HEURISTIC SCAN
            </>
          )}
        </button>
      </form>
    </div>
  );
}
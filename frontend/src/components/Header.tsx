import React from "react";
import { ShieldCheck, Lock, FileSpreadsheet, Building2 } from "lucide-react";

export function Header() {
  return (
    <header className="h-16 border-b border-slate-800 bg-slate-900/80 backdrop-blur-md px-6 flex items-center justify-between sticky top-0 z-50">
      {/* Left: Brand & Title */}
      <div className="flex items-center gap-3">
        <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-blue-600 via-indigo-600 to-cyan-400 flex items-center justify-center shadow-lg shadow-indigo-500/20">
          <ShieldCheck className="w-6 h-6 text-white" />
        </div>
        <div>
          <div className="flex items-center gap-2">
            <span className="font-bold text-lg tracking-tight text-white">
              DocuNorm <span className="text-cyan-400 font-extrabold">AI</span>
            </span>
            <span className="text-[10px] font-semibold uppercase tracking-wider bg-indigo-950 text-indigo-300 border border-indigo-700/50 px-2 py-0.5 rounded-full">
              Enterprise DE
            </span>
          </div>
          <p className="text-xs text-slate-400">
            Privacy-First Regulatory Document Intelligence
          </p>
        </div>
      </div>

      {/* Middle: European Regulatory Badges */}
      <div className="hidden lg:flex items-center gap-2">
        <div className="flex items-center gap-1.5 px-3 py-1 rounded-md bg-slate-800/60 border border-slate-700/60 text-xs text-slate-300">
          <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
          <span className="font-medium text-emerald-300">DORA</span>
          <span className="text-slate-500">|</span>
          <span className="text-slate-400">Art. 30</span>
        </div>
        <div className="flex items-center gap-1.5 px-3 py-1 rounded-md bg-slate-800/60 border border-slate-700/60 text-xs text-slate-300">
          <FileSpreadsheet className="w-3.5 h-3.5 text-amber-400" />
          <span className="font-medium text-amber-300">ZUGFeRD 2.3</span>
          <span className="text-slate-500">|</span>
          <span className="text-slate-400">EN 16931</span>
        </div>
        <div className="flex items-center gap-1.5 px-3 py-1 rounded-md bg-slate-800/60 border border-slate-700/60 text-xs text-slate-300">
          <Lock className="w-3.5 h-3.5 text-blue-400" />
          <span className="font-medium text-blue-300">GDPR Masking</span>
        </div>
      </div>

      {/* Right: Tenant Context */}
      <div className="flex items-center gap-3">
        <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-slate-800 border border-slate-700 text-xs">
          <Building2 className="w-4 h-4 text-cyan-400" />
          <span className="text-slate-300 font-medium">Siemens AG</span>
          <span className="text-[10px] bg-slate-700 text-slate-300 px-1.5 py-0.5 rounded">
            DE-Tenant
          </span>
        </div>
      </div>
    </header>
  );
}

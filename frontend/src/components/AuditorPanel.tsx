"use client";

import React, { useState } from "react";
import { Shield, Sparkles, Send, CheckCircle, ExternalLink, Scale, FileSpreadsheet } from "lucide-react";

export interface CitationItem {
  id: string;
  source_tag: string;
  page_number: number;
  box: [number, number, number, number];
  snippet: string;
}

interface AuditPanelProps {
  onSelectCitation: (citation: CitationItem) => void;
}

export function AuditPanel({ onSelectCitation }: AuditPanelProps) {
  const [mode, setMode] = useState<"DORA" | "LkSG" | "ZUGFeRD">("DORA");
  const [query, setQuery] = useState("");
  const [loading, setLoading] = useState(false);

  // Sample grounded finding for demonstration
  const sampleCitation: CitationItem = {
    id: "cit-1",
    source_tag: "[SOURCE_1]",
    page_number: 1,
    box: [40, 160, 560, 220],
    snippet: "Section 4.1: Vendor guarantees minimum exit transition period of 6 months...",
  };

  return (
    <div className="w-[480px] flex flex-col h-full bg-slate-950">
      {/* Panel Header & Mode Selector */}
      <div className="p-4 border-b border-slate-800 bg-slate-900/40">
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center gap-2">
            <Scale className="w-4 h-4 text-cyan-400" />
            <h3 className="font-semibold text-xs tracking-wider uppercase text-slate-200">
              Regulatory Audit Engine
            </h3>
          </div>
          <span className="text-[10px] bg-slate-800 text-slate-400 px-2 py-0.5 rounded border border-slate-700">
            Zero-Hallucination
          </span>
        </div>

        {/* Framework Tabs */}
        <div className="grid grid-cols-3 gap-1 bg-slate-900 p-1 rounded-lg border border-slate-800">
          <button
            onClick={() => setMode("DORA")}
            className={`py-1.5 text-xs font-medium rounded-md transition-all ${
              mode === "DORA"
                ? "bg-indigo-600 text-white shadow"
                : "text-slate-400 hover:text-slate-200"
            }`}
          >
            DORA (ICT)
          </button>
          <button
            onClick={() => setMode("LkSG")}
            className={`py-1.5 text-xs font-medium rounded-md transition-all ${
              mode === "LkSG"
                ? "bg-indigo-600 text-white shadow"
                : "text-slate-400 hover:text-slate-200"
            }`}
          >
            LkSG (Supply)
          </button>
          <button
            onClick={() => setMode("ZUGFeRD")}
            className={`py-1.5 text-xs font-medium rounded-md transition-all ${
              mode === "ZUGFeRD"
                ? "bg-indigo-600 text-white shadow"
                : "text-slate-400 hover:text-slate-200"
            }`}
          >
            ZUGFeRD (XML)
          </button>
        </div>
      </div>

      {/* Audit Findings Trail */}
      <div className="flex-1 overflow-auto p-4 space-y-4">
        {/* Compliance Status Card */}
        <div className="p-3.5 rounded-xl bg-slate-900/80 border border-slate-800 space-y-2">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-emerald-400 flex items-center gap-1.5">
              <CheckCircle className="w-3.5 h-3.5" /> DORA Art. 30 Compliant
            </span>
            <span className="text-[10px] font-mono text-slate-500">RRF Score: 0.0325</span>
          </div>
          <p className="text-xs text-slate-300 leading-relaxed">
            The agreement complies with ICT exit transition mandates under EU 2022/2554. Clause 4.1 specifies a mandatory 6-month uninterrupted support window.
          </p>

          {/* Interactive Citation Tag */}
          <div className="pt-2">
            <button
              onClick={() => onSelectCitation(sampleCitation)}
              className="group flex items-center gap-2 px-2.5 py-1.5 rounded-lg bg-amber-500/10 border border-amber-500/30 hover:border-amber-500/70 text-amber-300 text-xs transition-all w-full text-left"
            >
              <span className="font-bold font-mono text-[10px] bg-amber-500 text-slate-950 px-1 py-0.5 rounded">
                [SOURCE_1]
              </span>
              <span className="truncate flex-1 text-[11px] text-slate-300 group-hover:text-amber-200">
                Page 1 • Section 4.1 (Exit Strategy)
              </span>
              <ExternalLink className="w-3 h-3 text-amber-400 opacity-60 group-hover:opacity-100" />
            </button>
          </div>
        </div>

        {/* Quick Audit Prompt Suggestions */}
        <div className="space-y-1.5">
          <p className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider">
            Suggested BaFin/DORA Checks:
          </p>
          <div className="flex flex-wrap gap-1.5">
            {[
              "Are exit clauses defined under Art 30?",
              "What is the maximum delay penalty rate?",
              "Are sub-outsourcing approvals required?",
            ].map((suggested, idx) => (
              <button
                key={idx}
                onClick={() => setQuery(suggested)}
                className="text-[11px] text-slate-400 hover:text-cyan-300 bg-slate-900 hover:bg-slate-800 border border-slate-800 rounded-md px-2.5 py-1 text-left transition-colors"
              >
                {suggested}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Query Input Box */}
      <div className="p-4 border-t border-slate-800 bg-slate-900/60">
        <div className="relative">
          <textarea
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Ask compliance query (e.g. 'Audit exit penalty terms')..."
            rows={3}
            className="w-full bg-slate-950 border border-slate-800 focus:border-cyan-500 rounded-xl px-3 py-2 text-xs text-slate-200 placeholder-slate-500 focus:outline-none resize-none transition-colors"
          />
          <button
            disabled={!query.trim()}
            className="absolute right-2.5 bottom-3.5 p-1.5 rounded-lg bg-cyan-500 hover:bg-cyan-400 disabled:opacity-40 text-slate-950 transition-colors"
          >
            <Send className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>
    </div>
  );
}
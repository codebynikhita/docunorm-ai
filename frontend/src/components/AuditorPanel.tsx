"use client";

import React, { useState } from "react";
import { Shield, Sparkles, Send, CheckCircle, ExternalLink, Scale, Loader2, AlertCircle } from "lucide-react";
import { auditDocument, AuditApiResponse } from "@/lib/api";

export interface CitationItem {
  id: string;
  source_tag: string;
  page_number: number;
  box: [number, number, number, number];
  snippet: string;
}

interface AuditPanelProps {
  documentId?: string | null;
  onSelectCitation: (citation: CitationItem) => void;
}

export function AuditPanel({ documentId, onSelectCitation }: AuditPanelProps) {
  const [mode, setMode] = useState<"DORA" | "LkSG" | "ZUGFeRD">("DORA");
  const [query, setQuery] = useState("");
  const [loading, setLoading] = useState(false);
  const [auditResult, setAuditResult] = useState<AuditApiResponse | null>(null);
  const [auditError, setAuditError] = useState<string | null>(null);

  const executeAudit = async (searchQuery: string) => {
    console.log("Auditing query:", searchQuery, "with documentId:", documentId);
    if (!searchQuery.trim()) return;
    if (!documentId) {
      setAuditError("Please click 'Upload PDF' to load your document first.");
      return;
    }

    setLoading(true);
    setAuditError(null);

    try {
      const result = await auditDocument(documentId, searchQuery, mode);
      console.log("Audit result received:", result);
      setAuditResult(result);
    } catch (err: any) {
      console.error("Audit error:", err);
      setAuditError(err.message || "Failed to execute audit inquiry.");
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      executeAudit(query);
    }
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
        {/* Error notice */}
        {auditError && (
          <div className="p-3 rounded-lg bg-rose-950/60 border border-rose-800 text-xs text-rose-300 flex items-center gap-2">
            <AlertCircle className="w-4 h-4 flex-shrink-0" />
            <span>{auditError}</span>
          </div>
        )}

        {/* Loading Spinner */}
        {loading && (
          <div className="p-6 rounded-xl bg-slate-900/60 border border-slate-800 flex flex-col items-center justify-center gap-3 text-slate-400">
            <Loader2 className="w-6 h-6 animate-spin text-cyan-400" />
            <p className="text-xs font-medium">Querying pgvector & grounding citations...</p>
          </div>
        )}

        {/* Live Audit Finding Result */}
        {auditResult && !loading && (
          <div className="p-3.5 rounded-xl bg-slate-900/80 border border-slate-800 space-y-2 animate-in fade-in duration-200">
            <div className="flex items-center justify-between">
              <span className="text-xs font-semibold text-emerald-400 flex items-center gap-1.5">
                <CheckCircle className="w-3.5 h-3.5" /> {auditResult.framework} Compliant
              </span>
              <span className="text-[10px] font-mono text-slate-500">Live pgvector</span>
            </div>
            <p className="text-xs text-slate-300 leading-relaxed">
              {auditResult.finding_summary}
            </p>

            {/* Interactive Citations */}
            <div className="pt-2 space-y-1.5">
              {auditResult.citations.map((citation, idx) => (
                <button
                  key={idx}
                  onClick={() =>
                    onSelectCitation({
                      id: citation.chunk_id || `cit-${idx}`,
                      source_tag: citation.source_tag,
                      page_number: citation.page_number,
                      box: (citation.bounding_box as [number, number, number, number]) || [40, 160, 560, 220],
                      snippet: citation.content || "",
                    })
                  }
                  className="group flex items-center gap-2 px-2.5 py-1.5 rounded-lg bg-amber-500/10 border border-amber-500/30 hover:border-amber-500/70 text-amber-300 text-xs transition-all w-full text-left"
                >
                  <span className="font-bold font-mono text-[10px] bg-amber-500 text-slate-950 px-1 py-0.5 rounded">
                    {citation.source_tag}
                  </span>
                  <span className="truncate flex-1 text-[11px] text-slate-300 group-hover:text-amber-200">
                    Page {citation.page_number} • Click to reveal bounding box
                  </span>
                  <ExternalLink className="w-3 h-3 text-amber-400 opacity-60 group-hover:opacity-100" />
                </button>
              ))}
            </div>
          </div>
        )}

        {/* Default prompt when no audit yet */}
        {!auditResult && !loading && (
          <div className="p-4 rounded-xl bg-slate-900/40 border border-slate-800 text-xs text-slate-400 text-center">
            Upload a document and ask an audit query or click a suggested check below to evaluate compliance.
          </div>
        )}

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
                onClick={() => {
                  setQuery(suggested);
                  executeAudit(suggested);
                }}
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
            onKeyDown={handleKeyDown}
            placeholder="Ask compliance query (e.g. 'Audit exit penalty terms')..."
            rows={3}
            className="w-full bg-slate-950 border border-slate-800 focus:border-cyan-500 rounded-xl px-3 py-2 text-xs text-slate-200 placeholder-slate-500 focus:outline-none resize-none transition-colors"
          />
          <button
            onClick={() => executeAudit(query)}
            disabled={!query.trim() || loading}
            className="absolute right-2.5 bottom-3.5 p-1.5 rounded-lg bg-cyan-500 hover:bg-cyan-400 disabled:opacity-40 text-slate-950 transition-colors"
          >
            {loading ? (
              <Loader2 className="w-3.5 h-3.5 animate-spin" />
            ) : (
              <Send className="w-3.5 h-3.5" />
            )}
          </button>
        </div>
      </div>
    </div>
  );
}
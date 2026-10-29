"use client";

import React, { useState, useEffect } from "react";
import {
  Flame,
  ShieldAlert,
  ShieldCheck,
  AlertTriangle,
  ArrowRight,
  Sparkles,
  ChevronRight,
  FileCheck2,
} from "lucide-react";
import { DocumentRiskHeatmap, getClauseRiskHeatmap } from "@/lib/api";
import { Language } from "@/lib/i18n";

interface ClauseRiskHeatmapBarProps {
  documentId?: string | null;
  currentPage: number;
  totalPages: number;
  lang: Language;
  onPageSelect: (page: number) => void;
  onOpenRemediation: () => void;
  onFocusRiskClause?: (chunkId: string, page: number, bbox: [number, number, number, number]) => void;
}

export function ClauseRiskHeatmapBar({
  documentId,
  currentPage,
  totalPages,
  lang,
  onPageSelect,
  onOpenRemediation,
  onFocusRiskClause,
}: ClauseRiskHeatmapBarProps) {
  const [heatmap, setHeatmap] = useState<DocumentRiskHeatmap | null>(null);
  const [loading, setLoading] = useState(false);
  const isDe = lang === "DE";

  useEffect(() => {
    if (!documentId) {
      setHeatmap(null);
      return;
    }
    let isCancelled = false;
    setLoading(true);

    getClauseRiskHeatmap(documentId)
      .then((data) => {
        if (!isCancelled) {
          setHeatmap(data);
          setLoading(false);
        }
      })
      .catch((err) => {
        console.warn("Failed to load clause risk heatmap:", err);
        if (!isCancelled) setLoading(false);
      });

    return () => {
      isCancelled = true;
    };
  }, [documentId]);

  if (!documentId || !heatmap) return null;

  const ratingColors = {
    AAA: "bg-emerald-500/15 text-emerald-700 dark:text-emerald-400 border-emerald-500/40",
    AA: "bg-emerald-500/15 text-emerald-700 dark:text-emerald-400 border-emerald-500/40",
    A: "bg-blue-500/15 text-blue-700 dark:text-blue-400 border-blue-500/40",
    BBB: "bg-amber-500/15 text-amber-700 dark:text-amber-400 border-amber-500/40",
    BB: "bg-amber-500/15 text-amber-700 dark:text-amber-400 border-amber-500/40",
    B: "bg-rose-500/15 text-rose-700 dark:text-rose-400 border-rose-500/40",
    CCC: "bg-rose-600/20 text-rose-700 dark:text-rose-400 border-rose-500/50 animate-pulse",
  }[heatmap.risk_rating] || "bg-slate-500/15 text-slate-700 dark:text-slate-400 border-slate-500/40";

  return (
    <div className="w-full bg-[var(--surface-dark)] border-b border-[var(--surface-border)] px-4 py-2 flex flex-wrap items-center justify-between gap-3 text-xs font-mono shadow-sm">
      {/* Left: Overall Risk Score & Rating Badge */}
      <div className="flex items-center gap-3">
        <div className="flex items-center gap-1.5 text-rose-500 font-bold">
          <Flame className="w-4 h-4 animate-bounce" />
          <span className="hidden sm:inline uppercase tracking-wider text-[11px] text-[var(--foreground)] opacity-80">
            {isDe ? "Klausel-Risiko-Heatmap:" : "Clause Risk Heatmap:"}
          </span>
        </div>

        <div className={`px-2 py-0.5 rounded border text-[11px] font-black ${ratingColors}`}>
          {heatmap.risk_rating} • {heatmap.overall_risk_score}/100
        </div>

        {heatmap.critical_count > 0 && (
          <span className="px-2 py-0.5 rounded bg-rose-500/10 text-rose-400 border border-rose-500/30 text-[10.5px] font-bold flex items-center gap-1">
            <ShieldAlert className="w-3.5 h-3.5 text-rose-500" />
            <span>
              {heatmap.critical_count} {isDe ? "Kritische Mängel" : "Critical Deficiencies"}
            </span>
          </span>
        )}
      </div>

      {/* Center: Page-by-Page Risk Timeline Bar */}
      <div className="flex items-center gap-1 overflow-x-auto max-w-[380px] py-0.5">
        {Array.from({ length: totalPages || 1 }).map((_, idx) => {
          const page = idx + 1;
          const score = heatmap.page_scores[page] ?? 10;
          const isCurrent = currentPage === page;

          let dotBg = "bg-emerald-500/25 border-emerald-500/60 text-emerald-700 dark:text-emerald-300 font-bold";
          if (score >= 80) {
            dotBg = "bg-rose-500/25 border-rose-500/60 text-rose-700 dark:text-rose-300 font-bold";
          } else if (score >= 50) {
            dotBg = "bg-amber-500/25 border-amber-500/60 text-amber-700 dark:text-amber-300 font-bold";
          }

          return (
            <button
              key={page}
              onClick={() => onPageSelect(page)}
              title={`${isDe ? "Seite" : "Page"} ${page}: ${isDe ? "Risiko" : "Risk"} ${score}/100`}
              className={`px-2 py-0.5 rounded border text-[10px] transition-all cursor-pointer flex items-center gap-1 ${dotBg} ${
                isCurrent ? "ring-2 ring-[var(--accent-tangerine)] scale-105" : "hover:opacity-80"
              }`}
            >
              <span>P{page}</span>
              {score >= 80 && <span className="w-1.5 h-1.5 rounded-full bg-rose-500 animate-ping" />}
            </button>
          );
        })}
      </div>

      {/* Right: AI Remediation Amendment Action */}
      <div className="flex items-center gap-2">
        <button
          onClick={onOpenRemediation}
          className="flex items-center gap-1.5 bg-gradient-to-r from-[var(--accent-tangerine)] to-amber-500 text-[var(--accent-contrast)] hover:opacity-95 font-mono font-bold text-[11px] px-3 py-1.5 rounded-md shadow transition-all cursor-pointer uppercase tracking-wider"
          title="Synthesize BGB & DORA Compliant Legal Amendments with Redline Diffs"
        >
          <Sparkles className="w-3.5 h-3.5" />
          <span>{isDe ? "BGB-Musterklauseln & Redline" : "BGB Amendments & Redline"}</span>
        </button>
      </div>
    </div>
  );
}

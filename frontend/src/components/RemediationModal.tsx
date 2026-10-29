"use client";

import React, { useState, useEffect } from "react";
import {
  X,
  Sparkles,
  ShieldAlert,
  ShieldCheck,
  FileText,
  Copy,
  Check,
  Download,
  Scale,
  ArrowRight,
  GitCompare,
  FileCheck2,
  AlertTriangle,
  Loader2,
  Columns,
  AlignLeft,
} from "lucide-react";
import {
  DocumentRiskHeatmap,
  AmendmentProposal,
  getClauseRiskHeatmap,
  generateAmendmentProposal,
  downloadAmendmentPdf,
} from "@/lib/api";
import { Language } from "@/lib/i18n";

interface RemediationModalProps {
  isOpen: boolean;
  onClose: () => void;
  documentId?: string | null;
  documentName?: string;
  lang: Language;
}

export function RemediationModal({
  isOpen,
  onClose,
  documentId,
  documentName = "",
  lang,
}: RemediationModalProps) {
  const isDe = lang === "DE";
  const [heatmap, setHeatmap] = useState<DocumentRiskHeatmap | null>(null);
  const [selectedRuleId, setSelectedRuleId] = useState<string>("");
  const [proposal, setProposal] = useState<AmendmentProposal | null>(null);
  const [loading, setLoading] = useState(false);
  const [generating, setGenerating] = useState(false);
  const [downloading, setDownloading] = useState(false);
  const [copied, setCopied] = useState(false);
  const [viewMode, setViewMode] = useState<"split" | "inline">("split");

  useEffect(() => {
    if (!isOpen || !documentId) return;
    setLoading(true);

    getClauseRiskHeatmap(documentId)
      .then((data) => {
        setHeatmap(data);
        if (data.risk_items.length > 0) {
          const first = data.risk_items[0];
          setSelectedRuleId(first.statutory_ref);
          loadProposal(documentId, first.statutory_ref, first.snippet);
        } else {
          loadProposal(documentId, "BAFIN-DORA-GENERIC", "Allgemeine Vertragsklausel ohne explizite Regelung");
        }
        setLoading(false);
      })
      .catch((err) => {
        console.error("Failed to load risk heatmap for remediation:", err);
        setLoading(false);
      });
  }, [isOpen, documentId]);

  const loadProposal = async (docId: string, ruleId: string, clause: string) => {
    setGenerating(true);
    try {
      const p = await generateAmendmentProposal(docId, ruleId, clause);
      setProposal(p);
    } catch (err) {
      console.error("Failed to generate amendment:", err);
    } finally {
      setGenerating(false);
    }
  };

  const handleCopy = () => {
    if (!proposal) return;
    navigator.clipboard.writeText(proposal.compliant_replacement_de);
    setCopied(true);
    setTimeout(() => setCopied(false), 2500);
  };

  const handleDownloadPdf = async () => {
    if (!documentId) return;
    setDownloading(true);
    try {
      await downloadAmendmentPdf(documentId, proposal ? [proposal] : undefined);
    } catch (err) {
      console.error("Failed to download amendment contract PDF:", err);
    } finally {
      setDownloading(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm animate-in fade-in duration-150">
      <div className="w-full max-w-5xl bg-[var(--surface-dark)] border border-[var(--surface-border)] rounded-2xl shadow-2xl flex flex-col max-h-[90vh] overflow-hidden">
        {/* Modal Header */}
        <div className="p-4 px-6 border-b border-[var(--surface-border)] flex items-center justify-between bg-[var(--surface-card)]">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-[var(--accent-tangerine)]/20 to-amber-500/20 border border-[var(--accent-tangerine)]/40 flex items-center justify-center text-[var(--accent-tangerine)]">
              <Sparkles className="w-5 h-5" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h3 className="font-mono font-bold text-sm text-[var(--foreground)] uppercase tracking-wider">
                  {isDe
                    ? "BGB-Vertragsnachbesserung & Redline-Diff"
                    : "Contract Amendment Synthesizer & Redline Diff"}
                </h3>
                <span className="px-2 py-0.5 rounded text-[10px] font-mono bg-blue-500/15 text-blue-400 border border-blue-500/30 font-bold">
                  BGB § 311 • DORA Art. 30
                </span>
              </div>
              <p className="text-[11px] font-mono text-[var(--foreground)] opacity-60">
                {documentName} • {isDe ? "Aufsichtsrechtliche Musterklausel-Generierung" : "Regulatory Remediation Matrix"}
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={handleDownloadPdf}
              disabled={downloading}
              className="flex items-center gap-1.5 bg-[var(--foreground)] text-[var(--background)] hover:opacity-90 font-mono font-bold text-xs px-3.5 py-1.5 rounded-lg shadow transition-all cursor-pointer uppercase tracking-wider disabled:opacity-50"
            >
              {downloading ? (
                <Loader2 className="w-3.5 h-3.5 animate-spin" />
              ) : (
                <Download className="w-3.5 h-3.5" />
              )}
              <span>{isDe ? "Nachtragsvereinbarung PDF" : "Addendum Contract PDF"}</span>
            </button>
            <button
              onClick={onClose}
              className="p-1.5 rounded-lg text-[var(--foreground)] opacity-60 hover:opacity-100 hover:bg-[var(--surface-card)] cursor-pointer"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* Modal Body */}
        <div className="flex-1 overflow-y-auto p-6 space-y-6">
          {loading ? (
            <div className="flex flex-col items-center justify-center p-16 text-center text-xs font-mono space-y-3">
              <Loader2 className="w-8 h-8 animate-spin text-[var(--accent-tangerine)]" />
              <p>{isDe ? "Analysiere Klauselmängel und generiere BGB-Musterklauseln..." : "Analyzing clause defects and generating BGB amendments..."}</p>
            </div>
          ) : (
            <>
              {/* Deficiencies Selector Grid */}
              {heatmap && heatmap.risk_items.length > 0 && (
                <div className="space-y-2">
                  <span className="text-[11px] font-mono font-bold uppercase tracking-wider text-[var(--foreground)] opacity-70">
                    {isDe ? "Identifizierte Klauselmängel zum Nachbessern:" : "Identified Contractual Gaps to Remediate:"}
                  </span>
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-2.5">
                    {heatmap.risk_items.map((item, i) => {
                      const isSelected = selectedRuleId === item.statutory_ref;
                      return (
                        <button
                          key={i}
                          onClick={() => {
                            setSelectedRuleId(item.statutory_ref);
                            if (documentId) {
                              loadProposal(documentId, item.statutory_ref, item.snippet);
                            }
                          }}
                          className={`p-3 rounded-xl border text-left font-mono transition-all cursor-pointer ${
                            isSelected
                              ? "bg-[var(--surface-card)] border-2 border-[var(--accent-tangerine)] shadow-md"
                              : "bg-[var(--surface-card)]/50 border-[var(--surface-border)] hover:border-[var(--accent-tangerine)]/40"
                          }`}
                        >
                          <div className="flex items-center justify-between text-[10px] mb-1">
                            <span className="px-1.5 py-0.5 rounded bg-rose-500/15 text-rose-500 dark:text-rose-400 font-bold border border-rose-500/30">
                              {item.severity}
                            </span>
                            <span className="opacity-60">{isDe ? `Seite ${item.page_number}` : `Page ${item.page_number}`}</span>
                          </div>
                          <div className="text-xs font-bold text-[var(--foreground)] truncate">{item.title}</div>
                          <div className="text-[10px] text-[var(--foreground)] opacity-60 mt-1 line-clamp-2">
                            {isDe ? item.deficiency_summary_de : item.deficiency_summary_en}
                          </div>
                        </button>
                      );
                    })}
                  </div>
                </div>
              )}

              {/* Redline Diff & Proposed Amendment */}
              {generating ? (
                <div className="p-12 text-center text-xs font-mono opacity-70 space-y-2">
                  <Loader2 className="w-6 h-6 animate-spin mx-auto text-[var(--accent-tangerine)]" />
                  <p>{isDe ? "Synthetisiere rechtssicheren Redline-Diff..." : "Synthesizing legal redline diff..."}</p>
                </div>
              ) : proposal ? (
                <div className="space-y-4">
                  {/* Title & Statutory Basis Banner */}
                  <div className="p-4 rounded-xl bg-blue-500/10 border border-blue-500/25 flex flex-wrap items-center justify-between gap-3 font-mono text-xs">
                    <div>
                      <div className="font-bold text-blue-500 dark:text-blue-400">{isDe ? proposal.title_de : proposal.title_en}</div>
                      <div className="text-[11px] opacity-75 mt-0.5">
                        {isDe ? "Rechtsgrundlage:" : "Statutory Basis:"} {proposal.bgb_statutory_basis} • {proposal.dora_statutory_basis}
                      </div>
                    </div>
                    <button
                      onClick={handleCopy}
                      className="flex items-center gap-1.5 bg-blue-500/20 hover:bg-blue-500/30 text-blue-600 dark:text-blue-300 border border-blue-500/40 px-3 py-1.5 rounded-lg transition-all cursor-pointer font-bold text-[11px]"
                    >
                      {copied ? <Check className="w-3.5 h-3.5 text-emerald-500" /> : <Copy className="w-3.5 h-3.5" />}
                      <span>{copied ? (isDe ? "Kopiert!" : "Copied!") : (isDe ? "Klausel kopieren" : "Copy Clause")}</span>
                    </button>
                  </div>

                  {/* Redline Diff Comparison Container */}
                  <div className="p-4 rounded-xl bg-[var(--surface-card)] border border-[var(--surface-border)] space-y-3 shadow-md">
                    <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-[var(--surface-border)] pb-2.5">
                      <div className="flex items-center gap-2">
                        <GitCompare className="w-4 h-4 text-[var(--accent-tangerine)]" />
                        <span className="font-mono text-xs font-bold text-[var(--foreground)]">
                          {isDe ? "Klausel-Nachbesserung & Redline-Diff:" : "Clause Remediation & Redline Diff:"}
                        </span>
                      </div>

                      {/* View Mode Switcher (Split vs Inline) & High-Contrast Legend */}
                      <div className="flex flex-wrap items-center gap-3">
                        {/* High-Contrast Legend */}
                        <div className="flex items-center gap-2 text-[10px] font-mono">
                          <span className="inline-flex items-center gap-1.5 px-2 py-0.5 rounded-md bg-red-100 text-red-700 dark:bg-red-950/70 dark:text-red-300 border border-red-300 dark:border-red-700 font-bold">
                            <span className="w-2 h-2 rounded-full bg-red-600 dark:bg-red-500"></span>
                            <span>{isDe ? "Gestrichen (Defizitär)" : "Removed (Deficient)"}</span>
                          </span>
                          <span className="inline-flex items-center gap-1.5 px-2 py-0.5 rounded-md bg-emerald-100 text-emerald-800 dark:bg-emerald-950/70 dark:text-emerald-300 border border-emerald-300 dark:border-emerald-700 font-bold">
                            <span className="w-2 h-2 rounded-full bg-emerald-600 dark:bg-emerald-500"></span>
                            <span>{isDe ? "Eingefügt (Rechtskonform)" : "Added (Compliant)"}</span>
                          </span>
                        </div>

                        {/* View Mode Switcher */}
                        <div className="flex items-center gap-1 bg-[var(--surface-dark)] p-0.5 rounded-lg border border-[var(--surface-border)] text-[10px] font-mono">
                          <button
                            onClick={() => setViewMode("split")}
                            className={`flex items-center gap-1 px-2 py-1 rounded cursor-pointer font-bold ${
                              viewMode === "split"
                                ? "bg-[var(--accent-tangerine)] text-[var(--accent-contrast)]"
                                : "text-[var(--foreground)] opacity-60 hover:opacity-100"
                            }`}
                          >
                            <Columns className="w-3 h-3" />
                            <span>{isDe ? "Nebeneinander" : "Side-by-Side"}</span>
                          </button>
                          <button
                            onClick={() => setViewMode("inline")}
                            className={`flex items-center gap-1 px-2 py-1 rounded cursor-pointer font-bold ${
                              viewMode === "inline"
                                ? "bg-[var(--accent-tangerine)] text-[var(--accent-contrast)]"
                                : "text-[var(--foreground)] opacity-60 hover:opacity-100"
                            }`}
                          >
                            <AlignLeft className="w-3 h-3" />
                            <span>{isDe ? "Fließtext" : "Inline Diff"}</span>
                          </button>
                        </div>
                      </div>
                    </div>

                    {/* VIEW 1: SIDE-BY-SIDE (SPLIT VIEW) - CLEAR VIVID RED & GREEN */}
                    {viewMode === "split" ? (
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        {/* Red Column: Original Deficient Clause */}
                        <div className="p-4 rounded-xl border-2 border-red-500/40 bg-red-50/60 dark:bg-red-950/30 space-y-2 shadow-sm">
                          <div className="flex items-center justify-between">
                            <span className="inline-flex items-center gap-1.5 px-2 py-0.5 rounded bg-red-600 text-white font-mono font-bold text-[10px] uppercase tracking-wider shadow-sm">
                              <span>✕</span>
                              <span>{isDe ? "GESTRICHEN (RECHTSWIDRIG)" : "REMOVED (DEFICIENT)"}</span>
                            </span>
                            <span className="text-[10px] font-mono text-red-600 dark:text-red-400 font-semibold">
                              {isDe ? "Originaler Vertragstext" : "Original Contract Clause"}
                            </span>
                          </div>
                          <div className="p-3 rounded-lg bg-white/80 dark:bg-black/30 border border-red-300 dark:border-red-800 text-xs font-mono leading-relaxed text-red-800 dark:text-red-200 line-through decoration-red-600 decoration-2">
                            {proposal.original_text || (isDe ? "Allgemeine Vertragsklausel ohne explizite Regelung" : "Generic clause lacking explicit statutory governance")}
                          </div>
                        </div>

                        {/* Green Column: Compliant Replacement Clause */}
                        <div className="p-4 rounded-xl border-2 border-emerald-500/40 bg-emerald-50/60 dark:bg-emerald-950/30 space-y-2 shadow-sm">
                          <div className="flex items-center justify-between">
                            <span className="inline-flex items-center gap-1.5 px-2 py-0.5 rounded bg-emerald-600 text-white font-mono font-bold text-[10px] uppercase tracking-wider shadow-sm">
                              <span>✓</span>
                              <span>{isDe ? "EINGEFÜGT (RECHTSKONFORM)" : "ADDED (COMPLIANT)"}</span>
                            </span>
                            <span className="text-[10px] font-mono text-emerald-700 dark:text-emerald-400 font-semibold">
                              {isDe ? "BGB § 311 / DORA Muster" : "BGB § 311 / DORA Model"}
                            </span>
                          </div>
                          <div className="p-3 rounded-lg bg-white/80 dark:bg-black/30 border border-emerald-300 dark:border-emerald-800 text-xs font-mono leading-relaxed text-emerald-900 dark:text-emerald-100 font-semibold">
                            {proposal.compliant_replacement_de}
                          </div>
                        </div>
                      </div>
                    ) : (
                      /* VIEW 2: INLINE REDLINE DIFF - HIGH CONTRAST RED & GREEN TOKENS */
                      <div className="p-4 rounded-xl bg-[var(--surface-dark)] font-mono text-xs leading-loose border border-[var(--surface-border)]">
                        {proposal.diff_tokens.map((token, idx) => {
                          if (token.type === "delete") {
                            return (
                              <span
                                key={idx}
                                className="inline-block bg-red-100 text-red-800 dark:bg-red-950/80 dark:text-red-200 border-2 border-red-500 dark:border-red-600 font-bold line-through decoration-red-600 decoration-2 px-1.5 py-0.5 rounded mx-1 shadow-sm"
                              >
                                {token.text}
                              </span>
                            );
                          } else if (token.type === "insert") {
                            return (
                              <span
                                key={idx}
                                className="inline-block bg-emerald-100 text-emerald-900 dark:bg-emerald-950/80 dark:text-emerald-100 border-2 border-emerald-500 dark:border-emerald-600 font-bold underline decoration-emerald-600 decoration-2 px-1.5 py-0.5 rounded mx-1 shadow-sm"
                              >
                                {token.text}
                              </span>
                            );
                          }
                          return (
                            <span key={idx} className="text-[var(--foreground)] opacity-90 mx-0.5">
                              {token.text}
                            </span>
                          );
                        })}
                      </div>
                    )}
                  </div>

                  {/* Clean Proposed German Replacement Clause */}
                  <div className="p-4 rounded-xl bg-emerald-50/70 dark:bg-emerald-950/30 border-2 border-emerald-500/40 space-y-2 shadow-sm">
                    <span className="text-[11px] font-mono font-bold text-emerald-700 dark:text-emerald-400 uppercase tracking-wider flex items-center gap-1.5">
                      <FileCheck2 className="w-4 h-4 text-emerald-600 dark:text-emerald-400" />
                      <span>{isDe ? "Vollständige rechtssichere Musterklausel (Deutsch):" : "Compliant German Legal Replacement Clause:"}</span>
                    </span>
                    <p className="text-xs font-mono text-emerald-950 dark:text-emerald-100 leading-relaxed bg-white/80 dark:bg-black/30 p-3.5 rounded-lg border border-emerald-400 dark:border-emerald-700 font-medium">
                      {proposal.compliant_replacement_de}
                    </p>
                  </div>

                  {/* Legal Justification */}
                  <div className="p-3.5 rounded-xl bg-[var(--surface-card)] border border-[var(--surface-border)] text-xs font-mono space-y-1">
                    <span className="text-[10px] font-bold opacity-60 uppercase tracking-wider">
                      {isDe ? "Aufsichtsrechtliche Begründung & BGB-Würdigung:" : "Legal Justification & BGB Assessment:"}
                    </span>
                    <p className="opacity-80 text-[11px] leading-relaxed text-[var(--foreground)]">
                      {isDe ? proposal.legal_justification_de : proposal.legal_justification_en}
                    </p>
                  </div>
                </div>
              ) : null}
            </>
          )}
        </div>
      </div>
    </div>
  );
}

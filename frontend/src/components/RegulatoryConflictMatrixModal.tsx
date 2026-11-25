"use client";

import React, { useState, useEffect } from "react";
import {
  X,
  Scale,
  ShieldAlert,
  AlertTriangle,
  CheckCircle2,
  Download,
  Copy,
  Check,
  Globe2,
  FileText,
  Loader2,
  BookOpen,
  ArrowRight,
  Gavel,
} from "lucide-react";
import {
  DocumentConflictMatrix,
  NormativeConflict,
  getDocumentConflictMatrix,
  downloadConflictMatrixPdf,
} from "@/lib/api";
import { Language } from "@/lib/i18n";

interface RegulatoryConflictMatrixModalProps {
  isOpen: boolean;
  onClose: () => void;
  documentId?: string | null;
  documentName?: string;
  lang: Language;
}

export function RegulatoryConflictMatrixModal({
  isOpen,
  onClose,
  documentId,
  documentName = "Vertragsdokument",
  lang,
}: RegulatoryConflictMatrixModalProps) {
  const isDe = lang === "DE";
  const [matrix, setMatrix] = useState<DocumentConflictMatrix | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [downloading, setDownloading] = useState<boolean>(false);
  const [selectedConflict, setSelectedConflict] = useState<NormativeConflict | null>(null);
  const [copiedConflictId, setCopiedConflictId] = useState<string | null>(null);

  useEffect(() => {
    if (!isOpen || !documentId) return;
    setLoading(true);

    getDocumentConflictMatrix(documentId)
      .then((data) => {
        setMatrix(data);
        if (data.conflicts.length > 0) {
          setSelectedConflict(data.conflicts[0]);
        }
        setLoading(false);
      })
      .catch((err) => {
        console.error("Failed to load conflict matrix:", err);
        setLoading(false);
      });
  }, [isOpen, documentId]);

  const handleDownloadPdf = async () => {
    if (!documentId) return;
    setDownloading(true);
    try {
      await downloadConflictMatrixPdf(documentId);
    } catch (err) {
      console.error("PDF download failed:", err);
    } finally {
      setDownloading(false);
    }
  };

  const handleCopyClause = (confId: string, text: string) => {
    navigator.clipboard.writeText(text);
    setCopiedConflictId(confId);
    setTimeout(() => setCopiedConflictId(null), 2500);
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm animate-in fade-in duration-150">
      <div className="w-full max-w-5xl bg-[var(--surface-dark)] border border-[var(--surface-border)] rounded-2xl shadow-2xl flex flex-col max-h-[90vh] overflow-hidden">
        {/* Modal Header */}
        <div className="p-4 px-6 border-b border-[var(--surface-border)] flex items-center justify-between bg-[var(--surface-card)]">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-amber-500/20 to-red-500/20 border border-amber-500/40 flex items-center justify-center text-amber-500">
              <Scale className="w-5 h-5" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h3 className="font-mono font-bold text-sm text-[var(--foreground)] uppercase tracking-wider">
                  {isDe
                    ? "Aufsichtsrechtliche Normenkollisionsprüfung"
                    : "Cross-Regulatory Conflict & Incompatibility Matrix"}
                </h3>
                <span className="px-2 py-0.5 rounded text-[10px] font-mono bg-rose-500/15 text-rose-400 border border-rose-500/30 font-bold">
                  Lex Superior • Schrems II • DORA
                </span>
              </div>
              <p className="text-[11px] font-mono text-[var(--foreground)] opacity-60">
                {documentName} • {isDe ? "Inter-Regulatorische Spannungsverhältnisse & Kollisionsauflösung" : "Normative Clashing & Resolution Engine"}
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={handleDownloadPdf}
              disabled={downloading || !matrix}
              className="flex items-center gap-1.5 bg-gradient-to-r from-amber-600 to-rose-600 hover:from-amber-500 hover:to-rose-500 text-white font-mono font-bold text-xs px-3.5 py-1.5 rounded-lg shadow transition-all cursor-pointer uppercase tracking-wider disabled:opacity-50"
            >
              {downloading ? (
                <Loader2 className="w-3.5 h-3.5 animate-spin" />
              ) : (
                <Download className="w-3.5 h-3.5" />
              )}
              <span>{isDe ? "Rechtsgutachten PDF" : "Legal Opinion PDF"}</span>
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
              <Loader2 className="w-8 h-8 animate-spin text-amber-500" />
              <p>{isDe ? "Führe aufsichtsrechtliche Kollisionsprüfung über 8 Normensysteme durch..." : "Running cross-regulatory collision analysis across 8 statutory regimes..."}</p>
            </div>
          ) : matrix ? (
            <>
              {/* Executive Scorecard */}
              <div className="grid grid-cols-1 md:grid-cols-4 gap-3">
                {/* Overall Collision Gauge */}
                <div className={`p-4 rounded-xl border flex flex-col justify-between ${
                  matrix.compliance_verdict === "INCOMPATIBLE_BLOCKER"
                    ? "bg-rose-500/10 border-rose-500/30 text-rose-400"
                    : matrix.compliance_verdict === "CONDITIONALLY_RECONCILABLE"
                    ? "bg-amber-500/10 border-amber-500/30 text-amber-400"
                    : "bg-emerald-500/10 border-emerald-500/30 text-emerald-400"
                }`}>
                  <span className="text-[10px] font-mono font-bold uppercase tracking-wider opacity-70">
                    {isDe ? "Kollisions-Index" : "Collision Index"}
                  </span>
                  <div className="my-2">
                    <div className="text-2xl font-mono font-extrabold">{matrix.overall_collision_index} / 100</div>
                    <div className="text-[10px] font-mono font-bold uppercase tracking-wider mt-0.5">
                      {matrix.compliance_verdict === "INCOMPATIBLE_BLOCKER"
                        ? isDe ? "🔴 Inkompatibel (Blocker)" : "🔴 Incompatible Blocker"
                        : matrix.compliance_verdict === "CONDITIONALLY_RECONCILABLE"
                        ? isDe ? "🟡 Bedingt Vereinbar" : "🟡 Conditionally Reconcilable"
                        : isDe ? "🟢 Vollständig Vereinbar" : "🟢 Fully Harmonized"}
                    </div>
                  </div>
                  <span className="text-[9px] font-mono opacity-60">
                    {matrix.conflicts_detected} {isDe ? "Kollisionen identifiziert" : "conflicts identified"}
                  </span>
                </div>

                {/* Critical Blockers */}
                <div className="p-4 rounded-xl bg-[var(--surface-card)] border border-[var(--surface-border)] flex flex-col justify-between">
                  <div className="flex items-center justify-between">
                    <span className="text-[10px] font-mono font-bold uppercase tracking-wider opacity-60">
                      {isDe ? "Kritische Blocker" : "Critical Blockers"}
                    </span>
                    <ShieldAlert className="w-4 h-4 text-rose-500" />
                  </div>
                  <div className="text-2xl font-mono font-bold text-rose-500 my-1">{matrix.critical_blockers}</div>
                  <span className="text-[9px] font-mono opacity-50">
                    {isDe ? "Zwingende Nichtigkeit nach BGB § 134" : "Mandatory nullity under statutory law"}
                  </span>
                </div>

                {/* High / Medium Risks */}
                <div className="p-4 rounded-xl bg-[var(--surface-card)] border border-[var(--surface-border)] flex flex-col justify-between">
                  <div className="flex items-center justify-between">
                    <span className="text-[10px] font-mono font-bold uppercase tracking-wider opacity-60">
                      {isDe ? "Aufsichtsrisiken" : "Supervisory Risks"}
                    </span>
                    <AlertTriangle className="w-4 h-4 text-amber-500" />
                  </div>
                  <div className="text-2xl font-mono font-bold text-amber-500 my-1">
                    {matrix.high_risks + matrix.medium_risks}
                  </div>
                  <span className="text-[9px] font-mono opacity-50">
                    {matrix.high_risks} {isDe ? "Hoch" : "High"} • {matrix.medium_risks} {isDe ? "Mittel" : "Medium"}
                  </span>
                </div>

                {/* Jurisdictional Exposure */}
                <div className="p-4 rounded-xl bg-[var(--surface-card)] border border-[var(--surface-border)] flex flex-col justify-between">
                  <div className="flex items-center justify-between">
                    <span className="text-[10px] font-mono font-bold uppercase tracking-wider opacity-60">
                      {isDe ? "US-Extraterritorialität" : "US Extraterritoriality"}
                    </span>
                    <Globe2 className="w-4 h-4 text-blue-400" />
                  </div>
                  <div className="text-2xl font-mono font-bold text-blue-400 my-1">
                    {matrix.jurisdictional_exposure_map["US_EXTRATERRITORIAL"] || 0}
                  </div>
                  <span className="text-[9px] font-mono opacity-50">
                    {isDe ? "Klauseln mit CLOUD Act Exponierung" : "Clauses with CLOUD Act exposure"}
                  </span>
                </div>
              </div>

              {/* Conflict Master-Detail Workbench */}
              <div className="grid grid-cols-1 lg:grid-cols-12 gap-5">
                {/* Left Column: Conflict List Selector */}
                <div className="lg:col-span-5 space-y-2">
                  <div className="flex items-center justify-between px-1">
                    <span className="text-[11px] font-mono font-bold uppercase tracking-wider text-[var(--foreground)] opacity-70 flex items-center gap-1.5">
                      <Gavel className="w-3.5 h-3.5 text-amber-500" />
                      <span>{isDe ? "Kollisions-Register:" : "Conflict Registry:"}</span>
                    </span>
                    <span className="text-[10px] font-mono text-[var(--foreground)] opacity-50">
                      {matrix.conflicts.length} {isDe ? "Fälle" : "cases"}
                    </span>
                  </div>

                  <div className="space-y-2 max-h-[500px] overflow-y-auto pr-1">
                    {matrix.conflicts.map((conf) => {
                      const isSelected = selectedConflict?.conflict_id === conf.conflict_id;
                      const isCritical = conf.severity === "CRITICAL_BLOCKER";
                      return (
                        <button
                          key={conf.conflict_id}
                          onClick={() => setSelectedConflict(conf)}
                          className={`w-full p-3 rounded-xl border text-left font-mono transition-all cursor-pointer ${
                            isSelected
                              ? "bg-[var(--surface-card)] border-2 border-amber-500 shadow-md"
                              : "bg-[var(--surface-card)]/50 border-[var(--surface-border)] hover:border-amber-500/40"
                          }`}
                        >
                          <div className="flex items-center justify-between text-[10px] mb-1">
                            <span className={`px-1.5 py-0.5 rounded font-bold border ${
                              isCritical
                                ? "bg-rose-500/15 text-rose-400 border-rose-500/30"
                                : "bg-amber-500/15 text-amber-400 border-amber-500/30"
                            }`}>
                              {conf.conflict_id}
                            </span>
                            <span className="text-xs font-bold text-amber-500">
                              {conf.legal_risk_score}/100
                            </span>
                          </div>
                          <div className="text-xs font-bold text-[var(--foreground)] truncate">
                            {isDe ? conf.title_de : conf.title_en}
                          </div>
                          <div className="text-[10px] text-[var(--foreground)] opacity-60 mt-1 flex items-center gap-1">
                            <span>{conf.standard_a}</span>
                            <ArrowRight className="w-2.5 h-2.5" />
                            <span>{conf.standard_b}</span>
                            <span className="opacity-40">•</span>
                            <span>{isDe ? `Seite ${conf.page_number}` : `p. ${conf.page_number}`}</span>
                          </div>
                        </button>
                      );
                    })}
                  </div>
                </div>

                {/* Right Column: Detailed Forensic Analysis & Harmonization */}
                <div className="lg:col-span-7">
                  {selectedConflict ? (
                    <div className="p-5 rounded-2xl bg-[var(--surface-card)] border border-[var(--surface-border)] space-y-4">
                      {/* Conflict Header Banner */}
                      <div className="flex items-start justify-between gap-3">
                        <div>
                          <div className="flex items-center gap-2">
                            <span className="px-2 py-0.5 rounded text-[10px] font-mono font-bold bg-amber-500/20 text-amber-400 border border-amber-500/40">
                              {selectedConflict.conflict_id}
                            </span>
                            <span className="text-[10px] font-mono font-bold opacity-60 uppercase">
                              {selectedConflict.severity}
                            </span>
                          </div>
                          <h4 className="font-mono font-bold text-sm text-[var(--foreground)] mt-1">
                            {isDe ? selectedConflict.title_de : selectedConflict.title_en}
                          </h4>
                          <p className="text-[10px] font-mono text-[var(--foreground)] opacity-60">
                            {selectedConflict.jurisdiction_clash}
                          </p>
                        </div>
                        <div className="text-right">
                          <div className="text-xs font-mono font-bold text-amber-500">
                            {selectedConflict.legal_risk_score} / 100
                          </div>
                          <span className="text-[9px] font-mono opacity-50">Risiko-Score</span>
                        </div>
                      </div>

                      {/* Source Clause Extract */}
                      <div className="space-y-1.5">
                        <span className="text-[10px] font-mono font-bold uppercase tracking-wider text-rose-400 flex items-center gap-1">
                          <FileText className="w-3 h-3" />
                          <span>{isDe ? "Beanstandeter Klausel-Auszug (Vertragstext):" : "Disputed Contract Clause:"}</span>
                        </span>
                        <div className="p-3 rounded-xl bg-rose-500/5 border border-rose-500/20 text-xs font-mono text-rose-200 leading-relaxed line-through decoration-rose-500 decoration-1">
                          &ldquo;{selectedConflict.source_clause_text}&rdquo;
                        </div>
                      </div>

                      {/* Normative Clash Analysis */}
                      <div className="space-y-1.5">
                        <span className="text-[10px] font-mono font-bold uppercase tracking-wider opacity-70">
                          {isDe ? "Aufsichtsrechtliche Würdigung & Normenkollision:" : "Statutory Conflict Assessment:"}
                        </span>
                        <p className="p-3 rounded-xl bg-[var(--surface-dark)] border border-[var(--surface-border)] text-xs font-mono leading-relaxed opacity-90">
                          {isDe ? selectedConflict.statutory_clash_summary_de : selectedConflict.statutory_clash_summary_en}
                        </p>
                      </div>

                      {/* Statutory Precedence Rule Banner */}
                      <div className="p-3 rounded-xl bg-blue-500/10 border border-blue-500/25 flex items-center gap-2.5 text-xs font-mono">
                        <BookOpen className="w-4 h-4 text-blue-400 flex-shrink-0" />
                        <div>
                          <span className="font-bold text-blue-400 block text-[10px] uppercase">
                            {isDe ? "Kollisionsregel & Geltungsvorrang:" : "Statutory Precedence Rule:"}
                          </span>
                          <span className="text-[11px] text-blue-200">
                            {selectedConflict.statutory_precedence_rule}
                          </span>
                        </div>
                      </div>

                      {/* Authoritative Harmonization Covenant (Musterklausel) */}
                      <div className="space-y-2 pt-1">
                        <div className="flex items-center justify-between">
                          <span className="text-[10px] font-mono font-bold uppercase tracking-wider text-emerald-400 flex items-center gap-1.5">
                            <CheckCircle2 className="w-3.5 h-3.5" />
                            <span>{isDe ? "Statutarische Harmonisierungsklausel (Ersatztext):" : "Statutory Harmonization Covenant:"}</span>
                          </span>
                          <button
                            onClick={() => handleCopyClause(selectedConflict.conflict_id, selectedConflict.resolution_covenant_de)}
                            className="flex items-center gap-1 text-[10px] font-mono font-semibold px-2 py-1 rounded bg-emerald-500/15 hover:bg-emerald-500/25 text-emerald-400 border border-emerald-500/30 transition-all cursor-pointer"
                          >
                            {copiedConflictId === selectedConflict.conflict_id ? (
                              <>
                                <Check className="w-3 h-3 text-emerald-300" />
                                <span>{isDe ? "Kopiert!" : "Copied!"}</span>
                              </>
                            ) : (
                              <>
                                <Copy className="w-3 h-3" />
                                <span>{isDe ? "Klausel kopieren" : "Copy Clause"}</span>
                              </>
                            )}
                          </button>
                        </div>
                        <div className="p-3.5 rounded-xl bg-emerald-500/10 border-2 border-emerald-500/30 text-xs font-mono text-emerald-100 leading-relaxed font-medium">
                          {selectedConflict.resolution_covenant_de}
                        </div>
                      </div>
                    </div>
                  ) : null}
                </div>
              </div>

              {/* Cryptographic SHA-256 Ledger Seal */}
              <div className="p-3 rounded-xl bg-[var(--surface-card)] border border-[var(--surface-border)] flex items-center justify-between font-mono text-[10px] opacity-60">
                <span>{isDe ? "Kryptografischer Prüf-Hash (SHA-256):" : "Cryptographic Audit Seal (SHA-256):"}</span>
                <span className="font-mono text-[9px] text-amber-500">{matrix.sha256_hash}</span>
              </div>
            </>
          ) : (
            <div className="text-center p-12 text-xs font-mono opacity-60">
              {isDe ? "Keine Daten zur Kollisionsprüfung verfügbar." : "No conflict matrix data available."}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

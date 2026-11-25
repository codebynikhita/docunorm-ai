"use client";

import React, { useEffect, useState } from "react";
import {
  ContractDriftItem,
  ContractDriftReport,
  RegulatoryUpdate,
  downloadContractDriftPdf,
  getContractDriftAnalysis,
  getRegulatoryUpdates,
} from "@/lib/api";

interface RegTechHorizonModalProps {
  isOpen: boolean;
  onClose: () => void;
  documentId?: string;
  documentFilename?: string;
}

export const RegTechHorizonModal: React.FC<RegTechHorizonModalProps> = ({
  isOpen,
  onClose,
  documentId,
  documentFilename,
}) => {
  const [activeTab, setActiveTab] = useState<"drift" | "horizon">("drift");
  const [report, setReport] = useState<ContractDriftReport | null>(null);
  const [updates, setUpdates] = useState<RegulatoryUpdate[]>([]);
  const [authorityFilter, setAuthorityFilter] = useState<string>("ALL");
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [isExporting, setIsExporting] = useState<boolean>(false);
  const [copiedClauseId, setCopiedClauseId] = useState<string | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  useEffect(() => {
    if (!isOpen) return;

    let isMounted = true;
    setIsLoading(true);
    setErrorMessage(null);

    const loadData = async () => {
      try {
        const statutoryUpdates = await getRegulatoryUpdates();
        if (isMounted) setUpdates(statutoryUpdates);

        if (documentId) {
          const driftReport = await getContractDriftAnalysis(documentId);
          if (isMounted) setReport(driftReport);
        } else {
          setActiveTab("horizon");
        }
      } catch (err: unknown) {
        if (isMounted) {
          const msg = err instanceof Error ? err.message : "Fehler beim Laden des Horizon-Scanners";
          setErrorMessage(msg);
        }
      } finally {
        if (isMounted) setIsLoading(false);
      }
    };

    loadData();

    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === "Escape") onClose();
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => {
      isMounted = false;
      window.removeEventListener("keydown", handleKeyDown);
    };
  }, [isOpen, documentId, onClose]);

  if (!isOpen) return null;

  const handleDownloadPdf = async () => {
    if (!documentId) return;
    try {
      setIsExporting(true);
      await downloadContractDriftPdf(documentId);
    } catch (err: unknown) {
      alert(err instanceof Error ? err.message : "Export fehlgeschlagen.");
    } finally {
      setIsExporting(false);
    }
  };

  const handleCopyAction = (clauseId: string, actionText: string) => {
    navigator.clipboard.writeText(actionText);
    setCopiedClauseId(clauseId);
    setTimeout(() => setCopiedClauseId(null), 2500);
  };

  const filteredUpdates = updates.filter((u) => {
    if (authorityFilter === "ALL") return true;
    return u.issuing_authority === authorityFilter;
  });

  const getUrgencyBadge = (urgency: string) => {
    switch (urgency) {
      case "IMMEDIATE":
        return <span className="px-2 py-0.5 rounded text-xs font-bold bg-red-950/80 text-red-300 border border-red-700/60 animate-pulse">SOFORT (IMMEDIATE)</span>;
      case "HIGH":
        return <span className="px-2 py-0.5 rounded text-xs font-semibold bg-amber-950/70 text-amber-300 border border-amber-700/50">HOCH (HIGH)</span>;
      case "SCHEDULED":
        return <span className="px-2 py-0.5 rounded text-xs font-medium bg-blue-950/70 text-blue-300 border border-blue-700/50">GEPLANT</span>;
      default:
        return <span className="px-2 py-0.5 rounded text-xs font-medium bg-slate-800 text-slate-300 border border-slate-700">INFORMATIV</span>;
    }
  };

  const getSeverityBadge = (severity: string) => {
    switch (severity) {
      case "CRITICAL_DRIFT":
        return <span className="px-2 py-0.5 rounded text-xs font-bold bg-red-900/60 text-red-200 border border-red-600/60">KRITISCHER DRIFT</span>;
      case "HIGH_RISK":
        return <span className="px-2 py-0.5 rounded text-xs font-semibold bg-amber-900/60 text-amber-200 border border-amber-600/60">HOHES RISIKO</span>;
      case "MODERATE_GAP":
        return <span className="px-2 py-0.5 rounded text-xs font-medium bg-yellow-900/40 text-yellow-200 border border-yellow-700/40">LÜCKE (MODERATE)</span>;
      default:
        return <span className="px-2 py-0.5 rounded text-xs font-medium bg-emerald-900/40 text-emerald-300 border border-emerald-600/50">KONFORM</span>;
    }
  };

  const getStatusBadge = (status?: string) => {
    switch (status) {
      case "UP_TO_DATE":
        return <span className="px-3 py-1 rounded-full text-xs font-bold bg-emerald-950 text-emerald-300 border border-emerald-500 shadow-sm">AUF DEM NEUESTEN STAND</span>;
      case "ACTION_REQUIRED":
        return <span className="px-3 py-1 rounded-full text-xs font-bold bg-amber-950 text-amber-300 border border-amber-500 shadow-sm">NACHRÜSTUNG ERFORDERLICH</span>;
      case "NON_COMPLIANT_EXPIRED":
        return <span className="px-3 py-1 rounded-full text-xs font-bold bg-red-950 text-red-300 border border-red-500 shadow-sm animate-pulse">FRIST ABGELAUFEN (NON-COMPLIANT)</span>;
      default:
        return null;
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-3 sm:p-5 bg-black/80 backdrop-blur-md animate-in fade-in duration-200">
      <div className="relative w-full max-w-6xl max-h-[92vh] flex flex-col bg-slate-900 border border-cyan-800/60 rounded-xl shadow-2xl overflow-hidden text-slate-100">
        
        {/* Top Header Banner */}
        <div className="flex items-center justify-between px-6 py-4 bg-gradient-to-r from-slate-950 via-slate-900 to-cyan-950/80 border-b border-cyan-800/40">
          <div className="flex items-center gap-3">
            <span className="p-2.5 rounded-lg bg-cyan-950/80 border border-cyan-500/40 text-xl shadow-inner text-cyan-300">
              📡
            </span>
            <div>
              <div className="flex items-center gap-2">
                <h2 className="text-lg font-bold tracking-tight text-white">
                  RegTech Horizon Scanner &amp; Vertragsdrift-Auditor
                </h2>
                <span className="text-[10px] uppercase font-mono px-2 py-0.5 rounded bg-cyan-900/50 text-cyan-300 border border-cyan-700/50">
                  DAY 39 • 2026/2027
                </span>
              </div>
              <p className="text-xs text-slate-400 mt-0.5">
                Aufsichtsrechtliche Frühwarnung &amp; Delta-Analyse (DORA RTS 2026, BaFin RS 10/2026, EU AI Act, EDPB)
                {documentFilename && (
                  <span className="ml-2 font-mono text-cyan-300 text-xs">
                    • {documentFilename}
                  </span>
                )}
              </p>
            </div>
          </div>

          <div className="flex items-center gap-3">
            {documentId && report && (
              <button
                onClick={handleDownloadPdf}
                disabled={isExporting}
                className="flex items-center gap-2 px-3.5 py-1.5 rounded-lg text-xs font-semibold bg-cyan-700 hover:bg-cyan-600 active:bg-cyan-800 text-white transition-all shadow-md disabled:opacity-50"
              >
                {isExporting ? (
                  <>
                    <svg className="animate-spin h-3.5 w-3.5 text-white" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z" />
                    </svg>
                    Erzeuge DIN 5008 PDF...
                  </>
                ) : (
                  <>
                    <span>⬇️</span>
                    <span>Vertragsdrift-Gutachten PDF</span>
                  </>
                )}
              </button>
            )}

            <button
              onClick={onClose}
              className="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800/80 transition-colors"
              aria-label="Schließen"
            >
              ✕
            </button>
          </div>
        </div>

        {/* Navigation Tabs */}
        <div className="flex items-center justify-between px-6 py-2.5 bg-slate-950/60 border-b border-slate-800 text-xs">
          <div className="flex items-center gap-2">
            <button
              onClick={() => setActiveTab("drift")}
              disabled={!documentId}
              className={`px-3 py-1.5 rounded-md font-medium transition-all ${
                activeTab === "drift"
                  ? "bg-cyan-900/60 text-cyan-200 border border-cyan-500/50 shadow-sm"
                  : "text-slate-400 hover:text-slate-200 hover:bg-slate-800/50 disabled:opacity-30 disabled:cursor-not-allowed"
              }`}
            >
              📊 Vertragsdrift-Analyse {report ? `(${report.drifting_clauses_count})` : ""}
            </button>
            <button
              onClick={() => setActiveTab("horizon")}
              className={`px-3 py-1.5 rounded-md font-medium transition-all ${
                activeTab === "horizon"
                  ? "bg-cyan-900/60 text-cyan-200 border border-cyan-500/50 shadow-sm"
                  : "text-slate-400 hover:text-slate-200 hover:bg-slate-800/50"
              }`}
            >
              🗓️ Aufsichtsrechtlicher Horizont ({updates.length})
            </button>
          </div>

          {activeTab === "horizon" && (
            <div className="flex items-center gap-1.5">
              <span className="text-slate-500 text-[11px]">Behörde:</span>
              {["ALL", "BAFIN", "EBA", "EU_COMMISSION", "EDPB", "BAFA"].map((auth) => (
                <button
                  key={auth}
                  onClick={() => setAuthorityFilter(auth)}
                  className={`px-2 py-0.5 rounded text-[11px] font-mono transition-colors ${
                    authorityFilter === auth
                      ? "bg-cyan-700 text-white font-bold"
                      : "bg-slate-800/80 text-slate-400 hover:text-slate-200"
                  }`}
                >
                  {auth}
                </button>
              ))}
            </div>
          )}
        </div>

        {/* Content Body */}
        <div className="flex-1 overflow-y-auto p-6 space-y-6">
          {isLoading ? (
            <div className="flex flex-col items-center justify-center py-20 gap-3 text-slate-400">
              <div className="w-9 h-9 border-2 border-cyan-500 border-t-transparent rounded-full animate-spin" />
              <p className="text-xs font-mono">Scanne europäischen Normen-Horizont &amp; Vertragsklauseln...</p>
            </div>
          ) : errorMessage ? (
            <div className="p-4 rounded-lg bg-red-950/50 border border-red-800/60 text-red-300 text-xs">
              ⚠️ {errorMessage}
            </div>
          ) : activeTab === "drift" && report ? (
            <>
              {/* Scorecard Hero */}
              <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                <div className="p-4 rounded-xl bg-slate-950/80 border border-slate-800/90 shadow-sm flex flex-col justify-between">
                  <span className="text-[11px] font-semibold uppercase tracking-wider text-slate-400">
                    Vertragsdrift-Score
                  </span>
                  <div className="flex items-baseline gap-2 mt-2">
                    <span
                      className={`text-3xl font-extrabold font-mono ${
                        report.overall_drift_score > 60
                          ? "text-red-400"
                          : report.overall_drift_score > 20
                          ? "text-amber-400"
                          : "text-emerald-400"
                      }`}
                    >
                      {report.overall_drift_score}
                    </span>
                    <span className="text-xs text-slate-500 font-mono">/ 100</span>
                  </div>
                  <div className="w-full bg-slate-800 h-1.5 rounded-full mt-2 overflow-hidden">
                    <div
                      className={`h-full ${
                        report.overall_drift_score > 60
                          ? "bg-red-500"
                          : report.overall_drift_score > 20
                          ? "bg-amber-500"
                          : "bg-emerald-500"
                      }`}
                      style={{ width: `${Math.min(100, report.overall_drift_score)}%` }}
                    />
                  </div>
                </div>

                <div className="p-4 rounded-xl bg-slate-950/80 border border-slate-800/90 shadow-sm flex flex-col justify-between">
                  <span className="text-[11px] font-semibold uppercase tracking-wider text-slate-400">
                    Umsetzungsstatus
                  </span>
                  <div className="mt-2">{getStatusBadge(report.retrofitting_status)}</div>
                  <span className="text-[10px] text-slate-500 mt-2 font-mono">
                    Art. 28 DORA / KWG § 25b
                  </span>
                </div>

                <div className="p-4 rounded-xl bg-slate-950/80 border border-slate-800/90 shadow-sm flex flex-col justify-between">
                  <span className="text-[11px] font-semibold uppercase tracking-wider text-slate-400">
                    Driftende Klauseln
                  </span>
                  <div className="flex items-baseline gap-2 mt-2">
                    <span className="text-3xl font-extrabold font-mono text-cyan-300">
                      {report.drifting_clauses_count}
                    </span>
                    <span className="text-xs text-slate-500 font-mono">
                      von {report.total_clauses_analyzed} geprüft
                    </span>
                  </div>
                  <span className="text-[10px] text-slate-500 mt-2">
                    {report.critical_enforcement_items} mit Priorität 1 (Kritisch)
                  </span>
                </div>

                <div className="p-4 rounded-xl bg-slate-950/80 border border-slate-800/90 shadow-sm flex flex-col justify-between">
                  <span className="text-[11px] font-semibold uppercase tracking-wider text-slate-400">
                    Nächste Durchsetzungsfrist
                  </span>
                  <div className="mt-2 text-sm font-bold text-white font-mono">
                    {report.earliest_enforcement_deadline || "Keine Frist anhängig"}
                  </div>
                  <span className="text-[10px] text-slate-500 mt-2 font-mono truncate">
                    Hash: {report.sha256_seal.slice(0, 16)}...
                  </span>
                </div>
              </div>

              {/* Drift Clause List */}
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <h3 className="text-sm font-bold text-slate-200 tracking-wide uppercase">
                    Identifizierte Klauseldrifts &amp; Anpassungsbedarf ({report.drift_items.length})
                  </h3>
                  <span className="text-xs text-slate-500">
                    Klick auf &bdquo;Kopieren&ldquo; überträgt die Nachrüstungsklausel in die Zwischenablage
                  </span>
                </div>

                {report.drift_items.length === 0 ? (
                  <div className="p-8 rounded-xl bg-slate-950/60 border border-emerald-900/40 text-center space-y-2">
                    <span className="text-2xl">✅</span>
                    <h4 className="text-sm font-bold text-emerald-300">Kein regulatorischer Drift festgestellt</h4>
                    <p className="text-xs text-slate-400 max-w-lg mx-auto">
                      Alle geprüften Vertragsklauseln entsprechen den ab 2026 geltenden Standards von DORA RTS,
                      BaFin RS 10/2026 und dem EU AI Act.
                    </p>
                  </div>
                ) : (
                  report.drift_items.map((item: ContractDriftItem, idx: number) => (
                    <div
                      key={item.clause_id + idx}
                      className="p-5 rounded-xl bg-slate-950/90 border border-slate-800 hover:border-cyan-800/70 transition-all shadow-md space-y-3"
                    >
                      <div className="flex flex-wrap items-center justify-between gap-2 border-b border-slate-800/80 pb-2.5">
                        <div className="flex items-center gap-2">
                          <span className="font-mono text-xs font-bold text-cyan-400">
                            § {idx + 1}. {item.associated_update_id}
                          </span>
                          <span className="text-xs text-slate-500 font-mono">
                            • Seite {item.page_number}
                          </span>
                        </div>
                        <div className="flex items-center gap-2">
                          <span className="px-2 py-0.5 rounded text-xs font-mono bg-slate-900 text-slate-300 border border-slate-700">
                            Frist: noch {item.days_until_deadline} Tage
                          </span>
                          {getSeverityBadge(item.drift_severity)}
                        </div>
                      </div>

                      {/* Current Clause Excerpt */}
                      <div className="space-y-1">
                        <span className="text-[10px] font-semibold uppercase tracking-wider text-slate-400">
                          Aktueller Vertragstext (Auszug):
                        </span>
                        <p className="p-2.5 rounded-lg bg-slate-900/90 border border-slate-800 text-xs font-mono text-slate-300 italic">
                          &bdquo;{item.current_clause_text}&ldquo;
                        </p>
                      </div>

                      {/* Gap Analysis */}
                      <div className="space-y-1">
                        <span className="text-[10px] font-semibold uppercase tracking-wider text-amber-400">
                          Regulatorische Lücke (Compliance Gap):
                        </span>
                        <p className="text-xs text-slate-200 leading-relaxed">
                          {item.compliance_gap_de}
                        </p>
                      </div>

                      {/* Retrofitting Action Box */}
                      <div className="p-3.5 rounded-lg bg-cyan-950/40 border border-cyan-800/60 flex items-start justify-between gap-4">
                        <div className="space-y-1 flex-1">
                          <span className="text-[10px] font-bold uppercase tracking-wider text-cyan-300">
                            Empfohlene Nachrüstungsmaßnahme:
                          </span>
                          <p className="text-xs text-cyan-100 font-medium">
                            {item.retrofitting_action_required}
                          </p>
                        </div>
                        <button
                          onClick={() => handleCopyAction(item.clause_id, item.retrofitting_action_required)}
                          className="px-3 py-1.5 rounded-md text-xs font-semibold bg-cyan-800/80 hover:bg-cyan-700 text-white transition-colors shrink-0 flex items-center gap-1.5 shadow-sm"
                        >
                          {copiedClauseId === item.clause_id ? (
                            <>
                              <span>✓</span> Kopiert!
                            </>
                          ) : (
                            <>
                              <span>📋</span> Kopieren
                            </>
                          )}
                        </button>
                      </div>
                    </div>
                  ))
                )}
              </div>
            </>
          ) : (
            /* Horizon Timeline View */
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="text-sm font-bold text-slate-200 tracking-wide uppercase">
                    Aufsichtsrechtlicher Horizont &amp; Fristen-Radar (2026/2027)
                  </h3>
                  <p className="text-xs text-slate-400 mt-0.5">
                    Maßgebliche Richtlinien und Verordnungen der europäischen und deutschen Finanzaufsicht.
                  </p>
                </div>
                <span className="text-xs text-slate-500 font-mono">
                  {filteredUpdates.length} von {updates.length} Normen angezeigt
                </span>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {filteredUpdates.map((upd: RegulatoryUpdate) => (
                  <div
                    key={upd.update_id}
                    className="p-5 rounded-xl bg-slate-950/90 border border-slate-800 hover:border-cyan-800/70 transition-all shadow-md flex flex-col justify-between space-y-3"
                  >
                    <div className="space-y-2">
                      <div className="flex items-start justify-between gap-2">
                        <span className="font-mono text-xs font-bold text-cyan-400">
                          {upd.update_id}
                        </span>
                        {getUrgencyBadge(upd.urgency)}
                      </div>

                      <h4 className="text-xs font-bold text-white leading-snug">
                        {upd.title_de}
                      </h4>

                      <div className="flex flex-wrap items-center gap-1.5 pt-1">
                        <span className="px-2 py-0.5 rounded text-[10px] font-mono font-bold bg-slate-800 text-slate-200 border border-slate-700">
                          {upd.issuing_authority}
                        </span>
                        {upd.impacted_frameworks.map((fw: string) => (
                          <span
                            key={fw}
                            className="px-2 py-0.5 rounded text-[10px] font-mono bg-cyan-950/80 text-cyan-300 border border-cyan-800/60"
                          >
                            {fw}
                          </span>
                        ))}
                      </div>

                      <p className="text-xs text-slate-300 leading-relaxed pt-1">
                        {upd.summary_de}
                      </p>
                    </div>

                    <div className="border-t border-slate-800/80 pt-3 flex items-center justify-between text-xs">
                      <div className="flex items-center gap-2">
                        <span className="text-slate-500 text-[11px]">Frist:</span>
                        <span className="font-mono text-amber-300 font-semibold text-[11px]">
                          {upd.enforcement_deadline}
                        </span>
                        <span className="font-mono text-[11px] px-1.5 py-0.2 rounded bg-slate-900 text-slate-400">
                          (noch {upd.days_until_enforcement} Tage)
                        </span>
                      </div>

                      <a
                        href={upd.statutory_source_url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-cyan-400 hover:text-cyan-300 text-[11px] font-semibold underline flex items-center gap-1"
                      >
                        Offizielle Quelle ↗
                      </a>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Modal Footer */}
        <div className="px-6 py-3 bg-slate-950 border-t border-slate-800 flex items-center justify-between text-xs text-slate-500">
          <div className="flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-emerald-500" />
            <span>Horizon-Radar aktiv • EBA / BaFin / EIOPA / EU-Kommission</span>
          </div>
          <span className="font-mono text-[11px]">
            DocuNorm AI • Enterprise Audit Engine v39.0
          </span>
        </div>
      </div>
    </div>
  );
};

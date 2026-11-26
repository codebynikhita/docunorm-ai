"use client";

import React, { useEffect, useState } from "react";
import {
  BatchRemediationResult,
  DoraInformationRegister,
  DoraRegisterEntry,
  downloadDoraRegisterJson,
  downloadDoraRegisterPdf,
  executePortfolioBatchRemediation,
  getDoraInformationRegister,
} from "@/lib/api";

interface DoraRegisterRemediationModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export const DoraRegisterRemediationModal: React.FC<DoraRegisterRemediationModalProps> = ({
  isOpen,
  onClose,
}) => {
  const [activeTab, setActiveTab] = useState<"register" | "batch">("register");
  const [register, setRegister] = useState<DoraInformationRegister | null>(null);
  const [batchResult, setBatchResult] = useState<BatchRemediationResult | null>(null);
  const [criticalityFilter, setCriticalityFilter] = useState<string>("ALL");
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [isRemediating, setIsRemediating] = useState<boolean>(false);
  const [isExportingPdf, setIsExportingPdf] = useState<boolean>(false);
  const [isExportingJson, setIsExportingJson] = useState<boolean>(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  useEffect(() => {
    if (!isOpen) return;

    let isMounted = true;
    setIsLoading(true);
    setErrorMessage(null);

    getDoraInformationRegister()
      .then((data) => {
        if (isMounted) setRegister(data);
      })
      .catch((err) => {
        if (isMounted) {
          setErrorMessage(err instanceof Error ? err.message : "Fehler beim Laden des Informationsregisters");
        }
      })
      .finally(() => {
        if (isMounted) setIsLoading(false);
      });

    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === "Escape") onClose();
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => {
      isMounted = false;
      window.removeEventListener("keydown", handleKeyDown);
    };
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  const handleRunBatchRemediation = async () => {
    try {
      setIsRemediating(true);
      const res = await executePortfolioBatchRemediation();
      setBatchResult(res);
      setActiveTab("batch");
      // Refresh register to reflect remediated states
      const refreshed = await getDoraInformationRegister();
      setRegister(refreshed);
    } catch (err) {
      alert(err instanceof Error ? err.message : "Massensanierung fehlgeschlagen.");
    } finally {
      setIsRemediating(false);
    }
  };

  const handleDownloadPdf = async () => {
    try {
      setIsExportingPdf(true);
      await downloadDoraRegisterPdf();
    } catch (err) {
      alert(err instanceof Error ? err.message : "PDF-Download fehlgeschlagen.");
    } finally {
      setIsExportingPdf(false);
    }
  };

  const handleDownloadJson = async () => {
    try {
      setIsExportingJson(true);
      await downloadDoraRegisterJson();
    } catch (err) {
      alert(err instanceof Error ? err.message : "JSON-Export fehlgeschlagen.");
    } finally {
      setIsExportingJson(false);
    }
  };

  const filteredEntries = register?.entries.filter((e) => {
    if (criticalityFilter === "ALL") return true;
    return e.criticality === criticalityFilter;
  }) || [];

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-3 sm:p-5 bg-black/80 backdrop-blur-md animate-in fade-in duration-200">
      <div className="relative w-full max-w-6xl max-h-[92vh] flex flex-col bg-slate-900 border border-indigo-800/60 rounded-xl shadow-2xl overflow-hidden text-slate-100">
        
        {/* Header Banner */}
        <div className="flex items-center justify-between px-6 py-4 bg-gradient-to-r from-slate-950 via-slate-900 to-indigo-950/80 border-b border-indigo-800/40">
          <div className="flex items-center gap-3">
            <span className="p-2.5 rounded-lg bg-indigo-950/80 border border-indigo-500/40 text-xl shadow-inner text-indigo-300">
              📋
            </span>
            <div>
              <div className="flex items-center gap-2">
                <h2 className="text-lg font-bold tracking-tight text-white">
                  DORA Art. 28(3) Informationsregister &amp; Portfolio-Sanierung
                </h2>
                <span className="text-[10px] uppercase font-mono px-2 py-0.5 rounded bg-indigo-900/50 text-indigo-300 border border-indigo-700/50">
                  DAY 40 • ESA JC 2024 05
                </span>
              </div>
              <p className="text-xs text-slate-400 mt-0.5">
                Statutory Register of Information (BaFin / EZB) &amp; Automatisierte Multi-Vertrags-Harmonisierung
                {register && (
                  <span className="ml-2 font-mono text-indigo-300 text-xs">
                    • LEI: {register.reporting_lei}
                  </span>
                )}
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2.5">
            <button
              onClick={handleDownloadJson}
              disabled={isExportingJson || !register}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold bg-slate-800 hover:bg-slate-700 text-indigo-200 border border-slate-700 transition-all disabled:opacity-50"
              title="ESA JC 2024 05 JSON Export"
            >
              {isExportingJson ? "..." : "⬇️ ESA JSON"}
            </button>

            <button
              onClick={handleDownloadPdf}
              disabled={isExportingPdf || !register}
              className="flex items-center gap-1.5 px-3.5 py-1.5 rounded-lg text-xs font-semibold bg-indigo-700 hover:bg-indigo-600 text-white transition-all shadow-md disabled:opacity-50"
              title="BaFin DORA Informationsregister 3-Seiten DIN 5008 PDF"
            >
              {isExportingPdf ? (
                <>
                  <svg className="animate-spin h-3.5 w-3.5 text-white" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z" />
                  </svg>
                  Erzeuge PDF...
                </>
              ) : (
                <>
                  <span>⬇️</span>
                  <span>BaFin Register PDF</span>
                </>
              )}
            </button>

            <button
              onClick={onClose}
              className="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition-colors ml-1"
              aria-label="Schließen"
            >
              ✕
            </button>
          </div>
        </div>

        {/* Navigation Tabs & Actions */}
        <div className="flex items-center justify-between px-6 py-2.5 bg-slate-950/70 border-b border-slate-800 text-xs">
          <div className="flex items-center gap-2">
            <button
              onClick={() => setActiveTab("register")}
              className={`px-3 py-1.5 rounded-md font-medium transition-all ${
                activeTab === "register"
                  ? "bg-indigo-900/60 text-indigo-200 border border-indigo-500/50 shadow-sm"
                  : "text-slate-400 hover:text-slate-200 hover:bg-slate-800/50"
              }`}
            >
              📋 Gesetzliches Register ({register?.total_ict_contracts || 0} Verträge)
            </button>
            <button
              onClick={() => setActiveTab("batch")}
              className={`px-3 py-1.5 rounded-md font-medium transition-all ${
                activeTab === "batch"
                  ? "bg-indigo-900/60 text-indigo-200 border border-indigo-500/50 shadow-sm"
                  : "text-slate-400 hover:text-slate-200 hover:bg-slate-800/50"
              }`}
            >
              ⚡ Portfolio-Massensanierung {batchResult ? "(Erfolgreich)" : ""}
            </button>
          </div>

          <div className="flex items-center gap-2">
            {activeTab === "register" ? (
              <div className="flex items-center gap-1.5">
                <span className="text-slate-500 text-[11px]">Kritizität:</span>
                {["ALL", "CRITICAL_IMPORTANT", "NON_CRITICAL"].map((crit) => (
                  <button
                    key={crit}
                    onClick={() => setCriticalityFilter(crit)}
                    className={`px-2 py-0.5 rounded text-[11px] font-mono transition-colors ${
                      criticalityFilter === crit
                        ? "bg-indigo-700 text-white font-bold"
                        : "bg-slate-800/80 text-slate-400 hover:text-slate-200"
                    }`}
                  >
                    {crit === "ALL" ? "ALLE" : crit === "CRITICAL_IMPORTANT" ? "KRITISCH" : "STANDARD"}
                  </button>
                ))}
              </div>
            ) : (
              <button
                onClick={handleRunBatchRemediation}
                disabled={isRemediating}
                className="flex items-center gap-1.5 px-3 py-1 rounded bg-emerald-700 hover:bg-emerald-600 text-white text-xs font-bold transition-all shadow-sm disabled:opacity-50"
              >
                {isRemediating ? "Sanierung läuft..." : "⚡ Portfolio-Sanierung starten"}
              </button>
            )}
          </div>
        </div>

        {/* Content Body */}
        <div className="flex-1 overflow-y-auto p-6 space-y-6">
          {isLoading ? (
            <div className="flex flex-col items-center justify-center py-20 gap-3 text-slate-400">
              <div className="w-9 h-9 border-2 border-indigo-500 border-t-transparent rounded-full animate-spin" />
              <p className="text-xs font-mono">Aggregiere IKT-Verträge für DORA Art. 28(3) Informationsregister...</p>
            </div>
          ) : errorMessage ? (
            <div className="p-4 rounded-lg bg-red-950/50 border border-red-800/60 text-red-300 text-xs">
              ⚠️ {errorMessage}
            </div>
          ) : (
            <>
              {/* Scorecard Hero */}
              {register && (
                <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                  <div className="p-4 rounded-xl bg-slate-950/80 border border-slate-800/90 shadow-sm flex flex-col justify-between">
                    <span className="text-[11px] font-semibold uppercase tracking-wider text-slate-400">
                      Erfasste IKT-Verträge
                    </span>
                    <div className="flex items-baseline gap-2 mt-2">
                      <span className="text-3xl font-extrabold font-mono text-indigo-300">
                        {register.total_ict_contracts}
                      </span>
                      <span className="text-xs text-slate-500 font-mono">Dienstleister</span>
                    </div>
                    <span className="text-[10px] text-slate-500 mt-2 font-mono">
                      ESA JC 2024 05 konform
                    </span>
                  </div>

                  <div className="p-4 rounded-xl bg-slate-950/80 border border-slate-800/90 shadow-sm flex flex-col justify-between">
                    <span className="text-[11px] font-semibold uppercase tracking-wider text-slate-400">
                      Kritische / Wichtige Funktionen
                    </span>
                    <div className="flex items-baseline gap-2 mt-2">
                      <span className="text-3xl font-extrabold font-mono text-red-400">
                        {register.critical_ict_contracts}
                      </span>
                      <span className="text-xs text-slate-500 font-mono">
                        von {register.total_ict_contracts}
                      </span>
                    </div>
                    <span className="text-[10px] text-red-400/80 mt-2 font-mono">
                      Art. 28(3) Satz 2 DORA
                    </span>
                  </div>

                  <div className="p-4 rounded-xl bg-slate-950/80 border border-slate-800/90 shadow-sm flex flex-col justify-between">
                    <span className="text-[11px] font-semibold uppercase tracking-wider text-slate-400">
                      Gesamt-Konformitätsquote
                    </span>
                    <div className="flex items-baseline gap-2 mt-2">
                      <span
                        className={`text-3xl font-extrabold font-mono ${
                          register.overall_compliance_rate >= 80
                            ? "text-emerald-400"
                            : register.overall_compliance_rate >= 50
                            ? "text-amber-400"
                            : "text-red-400"
                        }`}
                      >
                        {register.overall_compliance_rate}%
                      </span>
                    </div>
                    <div className="w-full bg-slate-800 h-1.5 rounded-full mt-2 overflow-hidden">
                      <div
                        className={`h-full ${
                          register.overall_compliance_rate >= 80
                            ? "bg-emerald-500"
                            : register.overall_compliance_rate >= 50
                            ? "bg-amber-500"
                            : "bg-red-500"
                        }`}
                        style={{ width: `${register.overall_compliance_rate}%` }}
                      />
                    </div>
                  </div>

                  <div className="p-4 rounded-xl bg-slate-950/80 border border-slate-800/90 shadow-sm flex flex-col justify-between">
                    <span className="text-[11px] font-semibold uppercase tracking-wider text-slate-400">
                      Kryptografisches Revisionssiegel
                    </span>
                    <div className="mt-2 text-xs font-mono text-cyan-300 truncate">
                      {register.sha256_register_seal.slice(0, 20)}...
                    </div>
                    <span className="text-[10px] text-slate-500 mt-2 font-mono">
                      SHA-256 DIN EN ISO/IEC 10118-3
                    </span>
                  </div>
                </div>
              )}

              {/* View 1: Register of Information Table */}
              {activeTab === "register" && (
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <h3 className="text-sm font-bold text-slate-200 tracking-wide uppercase">
                      Tabelle B_01 &amp; B_04: IKT-Dienstleister &amp; Vertragsvereinbarungen ({filteredEntries.length})
                    </h3>
                    <span className="text-xs text-slate-500">
                      Gemäß Durchführungsstandard der Europäischen Bankenaufsichtsbehörde (EBA)
                    </span>
                  </div>

                  <div className="overflow-x-auto rounded-xl border border-slate-800 bg-slate-950/60 shadow-md">
                    <table className="w-full text-left text-xs border-collapse">
                      <thead>
                        <tr className="bg-slate-900/90 border-b border-slate-800 text-[11px] text-slate-400 uppercase font-mono">
                          <th className="py-3 px-4">Dienstleister &amp; LEI</th>
                          <th className="py-3 px-3">Kategorie</th>
                          <th className="py-3 px-3">Kritizität</th>
                          <th className="py-3 px-3">Kaskade</th>
                          <th className="py-3 px-3">Prüfrechte</th>
                          <th className="py-3 px-3">Kündigung</th>
                          <th className="py-3 px-3 text-right">Status</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-slate-800/60">
                        {filteredEntries.map((entry: DoraRegisterEntry) => (
                          <tr key={entry.contract_id} className="hover:bg-slate-900/50 transition-colors">
                            <td className="py-3 px-4">
                              <div className="font-semibold text-white">{entry.vendor_legal_name}</div>
                              <div className="text-[10px] font-mono text-slate-400 mt-0.5">
                                LEI: {entry.vendor_lei} ({entry.vendor_country}) • {entry.contract_filename}
                              </div>
                            </td>
                            <td className="py-3 px-3">
                              <span className="px-2 py-0.5 rounded text-[10px] font-mono bg-slate-800 text-slate-300">
                                {entry.service_category.replace("_", " ")}
                              </span>
                            </td>
                            <td className="py-3 px-3">
                              {entry.criticality === "CRITICAL_IMPORTANT" ? (
                                <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-red-950 text-red-300 border border-red-700/60">
                                  KRITISCH
                                </span>
                              ) : (
                                <span className="px-2 py-0.5 rounded text-[10px] font-medium bg-slate-800 text-slate-400">
                                  STANDARD
                                </span>
                              )}
                            </td>
                            <td className="py-3 px-3 font-mono">
                              <span
                                className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                                  entry.subcontractor_depth >= 4
                                    ? "bg-emerald-950 text-emerald-300 border border-emerald-700/60"
                                    : "bg-amber-950 text-amber-300 border border-amber-700/60"
                                }`}
                              >
                                Tier-{entry.subcontractor_depth}
                              </span>
                            </td>
                            <td className="py-3 px-3 font-mono text-[11px]">
                              {entry.audit_rights_compliant ? (
                                <span className="text-emerald-400 font-semibold">✓ KWG § 25b</span>
                              ) : (
                                <span className="text-red-400 font-semibold">✗ Lücke</span>
                              )}
                            </td>
                            <td className="py-3 px-3 font-mono text-[11px] text-slate-300">
                              {entry.exit_notice_period_days} Tage
                            </td>
                            <td className="py-3 px-3 text-right">
                              {entry.remediation_status === "CLEAN" ? (
                                <span className="px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-emerald-950 text-emerald-300 border border-emerald-600/60">
                                  KONFORM
                                </span>
                              ) : entry.remediation_status === "REMEDIATED_AUTOMATED" ? (
                                <span className="px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-cyan-950 text-cyan-300 border border-cyan-600/60">
                                  SANIERT
                                </span>
                              ) : (
                                <span className="px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-amber-950 text-amber-300 border border-amber-600/60">
                                  SANIERUNG NÖTIG
                                </span>
                              )}
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              )}

              {/* View 2: Portfolio Batch Remediation Results */}
              {activeTab === "batch" && (
                <div className="space-y-5">
                  <div className="p-5 rounded-xl bg-slate-950/80 border border-indigo-800/70 shadow-md space-y-4">
                    <div className="flex flex-wrap items-center justify-between gap-3">
                      <div>
                        <h3 className="text-sm font-bold text-white uppercase tracking-wide">
                          Automatisierte Portfolio-Massensanierung (Batch Remediation)
                        </h3>
                        <p className="text-xs text-slate-400 mt-0.5">
                          Synthetisiert verbindliche DORA Art. 30, BaFin RS 10/2026 und DSGVO Art. 28 Nachtragsklauseln
                          über alle mangelhaften Verträge im Mandantenbestand.
                        </p>
                      </div>
                      <button
                        onClick={handleRunBatchRemediation}
                        disabled={isRemediating}
                        className="px-4 py-2 rounded-lg text-xs font-bold bg-emerald-600 hover:bg-emerald-500 text-white transition-all shadow-md disabled:opacity-50"
                      >
                        {isRemediating ? "Sanierung wird durchgeführt..." : "⚡ Jetzt alle Verträge sanieren"}
                      </button>
                    </div>

                    {batchResult && (
                      <div className="pt-3 border-t border-slate-800 grid grid-cols-1 md:grid-cols-4 gap-4">
                        <div className="p-3 rounded-lg bg-slate-900 border border-slate-800">
                          <span className="text-[10px] text-slate-400 uppercase font-mono">Verträge bearbeitet</span>
                          <div className="text-xl font-bold font-mono text-white mt-1">
                            {batchResult.total_contracts_processed} Verträge
                          </div>
                        </div>

                        <div className="p-3 rounded-lg bg-slate-900 border border-slate-800">
                          <span className="text-[10px] text-slate-400 uppercase font-mono">Klauseln synthetisiert</span>
                          <div className="text-xl font-bold font-mono text-indigo-300 mt-1">
                            {batchResult.total_clauses_synthesized} Klauseln
                          </div>
                        </div>

                        <div className="p-3 rounded-lg bg-slate-900 border border-slate-800">
                          <span className="text-[10px] text-slate-400 uppercase font-mono">Portfolio-Risiko (Vorher → Nachher)</span>
                          <div className="text-xl font-bold font-mono text-amber-300 mt-1">
                            {batchResult.pre_risk_portfolio_average}% →{" "}
                            <span className="text-emerald-400">{batchResult.post_risk_portfolio_average}%</span>
                          </div>
                        </div>

                        <div className="p-3 rounded-lg bg-slate-900 border border-slate-800">
                          <span className="text-[10px] text-slate-400 uppercase font-mono">Risikoreduktion</span>
                          <div className="text-xl font-bold font-mono text-emerald-400 mt-1">
                            -{batchResult.risk_reduction_percentage}%
                          </div>
                        </div>
                      </div>
                    )}
                  </div>

                  {batchResult && (
                    <div className="space-y-3">
                      <h4 className="text-xs font-bold text-slate-300 uppercase tracking-wide">
                        Sanierte Vertragsdokumente ({batchResult.remediation_items.length})
                      </h4>

                      <div className="space-y-3">
                        {batchResult.remediation_items.map((item) => (
                          <div
                            key={item.document_id}
                            className="p-4 rounded-xl bg-slate-950/90 border border-slate-800 space-y-2.5 shadow-sm"
                          >
                            <div className="flex flex-wrap items-center justify-between gap-2 border-b border-slate-800/80 pb-2">
                              <div>
                                <span className="font-bold text-xs text-white">{item.document_filename}</span>
                                <span className="text-xs text-slate-400 ml-2">({item.vendor_name})</span>
                              </div>
                              <div className="flex items-center gap-2">
                                <span className="text-xs font-mono text-amber-300">
                                  Risiko: {item.pre_remediation_risk_score}% →{" "}
                                  <span className="text-emerald-400 font-bold">{item.post_remediation_risk_score}%</span>
                                </span>
                                <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-cyan-950 text-cyan-300 border border-cyan-700/60">
                                  {item.clauses_remediated_count} Klauseln generiert
                                </span>
                              </div>
                            </div>

                            <div className="text-xs font-semibold text-slate-300">
                              {item.synthesized_amendment_title}
                            </div>

                            <div className="flex flex-wrap gap-1.5 pt-1">
                              {item.remediated_clause_types.map((type) => (
                                <span
                                  key={type}
                                  className="px-2 py-0.5 rounded text-[10px] font-mono bg-indigo-950/80 text-indigo-300 border border-indigo-800/50"
                                >
                                  ✓ {type}
                                </span>
                              ))}
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              )}
            </>
          )}
        </div>

        {/* Modal Footer */}
        <div className="px-6 py-3 bg-slate-950 border-t border-slate-800 flex items-center justify-between text-xs text-slate-500">
          <div className="flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-emerald-500" />
            <span>Informationsregister revisionssicher archiviert • DORA Art. 28(3) &amp; BaFin RS 10/2026</span>
          </div>
          <span className="font-mono text-[11px]">DocuNorm AI • Enterprise Portfolio Engine v40.0</span>
        </div>
      </div>
    </div>
  );
};

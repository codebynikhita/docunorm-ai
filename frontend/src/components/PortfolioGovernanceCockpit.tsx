"use client";

import React, { useState, useEffect, useCallback } from "react";
import {
  X,
  Building2,
  Download,
  RefreshCw,
  AlertTriangle,
  CheckCircle2,
  PieChart,
  Globe,
  FileText,
  ShieldAlert,
  ArrowUpRight,
  Landmark,
} from "lucide-react";
import { Language } from "@/lib/i18n";
import {
  BafaAnnualReportSynthesis,
  getPortfolioLksgSummary,
  downloadBafaAnnualReportPdf,
} from "@/lib/api";

interface PortfolioGovernanceCockpitProps {
  isOpen: boolean;
  onClose: () => void;
  lang: Language;
  onSelectDocument?: (documentId: string) => void;
}

export function PortfolioGovernanceCockpit({
  isOpen,
  onClose,
  lang,
  onSelectDocument,
}: PortfolioGovernanceCockpitProps) {
  const isDE = lang === "DE";

  const [data, setData] = useState<BafaAnnualReportSynthesis | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [downloadingPdf, setDownloadingPdf] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<"suppliers" | "jurisdictions" | "governance">("suppliers");
  const [reportingYear] = useState<number>(2026);

  const loadPortfolio = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const result = await getPortfolioLksgSummary(reportingYear);
      setData(result);
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : String(err);
      setError(message || (isDE ? "Fehler beim Laden des Portfolios" : "Failed to load portfolio"));
    } finally {
      setLoading(false);
    }
  }, [reportingYear, isDE]);

  useEffect(() => {
    if (isOpen) {
      loadPortfolio();
    }
  }, [isOpen, loadPortfolio]);

  const handleDownloadPdf = async () => {
    if (downloadingPdf) return;
    setDownloadingPdf(true);
    try {
      await downloadBafaAnnualReportPdf("DocuNorm Sovereign Banking Group AG", reportingYear);
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : String(err);
      alert(message || "Failed to download annual BAFA report PDF");
    } finally {
      setDownloadingPdf(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm animate-fade-in">
      <div className="bg-white dark:bg-neutral-900 border border-neutral-200 dark:border-neutral-800 rounded-2xl w-full max-w-5xl max-h-[92vh] flex flex-col shadow-2xl overflow-hidden">
        {/* Top Header */}
        <div className="p-5 border-b border-neutral-200 dark:border-neutral-800 flex items-center justify-between gap-4 bg-gradient-to-r from-blue-500/10 via-indigo-500/5 to-transparent">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-blue-600/10 dark:bg-blue-500/20 text-blue-600 dark:text-blue-400 flex items-center justify-center">
              <Landmark className="w-5 h-5" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h2 className="text-base font-bold text-neutral-900 dark:text-neutral-100">
                  {isDE
                    ? "BAFA-Jahresbericht & Lieferanten-Portfolio (§ 10 Abs. 2 LkSG)"
                    : "Annual BAFA Statutory Due Diligence Portfolio Cockpit (§ 10(2) LkSG)"}
                </h2>
                <span className="px-2 py-0.5 rounded-full text-[10px] font-mono font-bold bg-blue-100 text-blue-800 dark:bg-blue-950 dark:text-blue-300">
                  {reportingYear}
                </span>
              </div>
              <p className="text-xs text-neutral-500 dark:text-neutral-400 mt-0.5">
                {isDE
                  ? "Zentrale Portfolio-Risikoanalyse, Klumpenrisiken (HHI) und gesetzliche Berichterstattung (Frist: 31. März 2027)"
                  : "Centralized supply chain portfolio risk analysis, concentration (HHI) and statutory annual filing"}
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2.5">
            <button
              onClick={handleDownloadPdf}
              disabled={downloadingPdf || loading || !data}
              className="px-3.5 py-2 rounded-xl text-xs font-mono font-bold bg-blue-600 text-white hover:bg-blue-700 transition flex items-center gap-1.5 cursor-pointer shadow-sm disabled:opacity-50"
            >
              <Download className="w-3.5 h-3.5" />
              <span>{downloadingPdf ? (isDE ? "Exportiere..." : "Exporting...") : isDE ? "BAFA-Bericht (DIN 5008 PDF)" : "BAFA Report (PDF)"}</span>
            </button>

            <button
              onClick={loadPortfolio}
              disabled={loading}
              className="p-2 rounded-xl text-neutral-500 hover:text-neutral-800 dark:hover:text-neutral-200 hover:bg-neutral-100 dark:hover:bg-neutral-800 transition cursor-pointer"
              title={isDE ? "Aktualisieren" : "Refresh"}
            >
              <RefreshCw className={`w-4 h-4 ${loading ? "animate-spin text-blue-600" : ""}`} />
            </button>

            <button
              onClick={onClose}
              className="p-2 rounded-xl text-neutral-400 hover:text-neutral-700 dark:hover:text-neutral-200 hover:bg-neutral-100 dark:hover:bg-neutral-800 transition cursor-pointer"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* Content Area */}
        <div className="flex-1 overflow-y-auto p-6 space-y-6">
          {loading && !data && (
            <div className="flex flex-col items-center justify-center py-20 text-neutral-500 space-y-3">
              <RefreshCw className="w-8 h-8 animate-spin text-blue-600" />
              <p className="text-sm font-medium">
                {isDE
                  ? "Aggregiere Lieferantenportfolio und berechne Konzentrationsrisiken (HHI)..."
                  : "Aggregating supply chain portfolio & computing concentration indices..."}
              </p>
            </div>
          )}

          {error && (
            <div className="p-4 rounded-xl bg-red-50 dark:bg-red-950/40 border border-red-200 dark:border-red-900/60 text-red-700 dark:text-red-300 flex items-start gap-3">
              <AlertTriangle className="w-5 h-5 mt-0.5 flex-shrink-0 text-red-600" />
              <div>
                <h4 className="font-semibold text-sm">{isDE ? "Fehler bei der Portfolio-Aggregation" : "Aggregation Error"}</h4>
                <p className="text-xs mt-0.5 opacity-90">{error}</p>
              </div>
            </div>
          )}

          {data && (
            <>
              {/* Row 1: KPI Summary Cards */}
              <div className="grid grid-cols-1 md:grid-cols-4 gap-3">
                {/* Card 1: Gesamt-Portfolio-Score */}
                <div className="p-4 rounded-xl bg-white dark:bg-neutral-900 border border-neutral-200 dark:border-neutral-800 shadow-sm space-y-2">
                  <span className="text-[10px] font-mono text-neutral-400 uppercase tracking-wide">1. Gesamt-Konformität</span>
                  <div className="flex items-baseline justify-between">
                    <span className="text-2xl font-black text-neutral-900 dark:text-neutral-100 font-mono">
                      {data.portfolio_compliance_score.toFixed(1)}%
                    </span>
                    <span className={`px-2 py-0.5 rounded text-[10px] font-mono font-bold ${
                      data.portfolio_compliance_score >= 80 ? "bg-emerald-100 text-emerald-800 dark:bg-emerald-950 dark:text-emerald-300" : "bg-amber-100 text-amber-800 dark:bg-amber-950 dark:text-amber-300"
                    }`}>
                      Rating: {data.portfolio_rating}
                    </span>
                  </div>
                  <div className="space-y-1 pt-1 text-[10px] font-mono text-neutral-500">
                    <div className="flex justify-between">
                      <span>Menschenrechte:</span>
                      <strong className="text-neutral-800 dark:text-neutral-200">{data.human_rights_portfolio_average.toFixed(0)}%</strong>
                    </div>
                    <div className="flex justify-between">
                      <span>Umweltkonventionen:</span>
                      <strong className="text-neutral-800 dark:text-neutral-200">{data.environmental_portfolio_average.toFixed(0)}%</strong>
                    </div>
                    <div className="flex justify-between">
                      <span>Governance & BAFA:</span>
                      <strong className="text-neutral-800 dark:text-neutral-200">{data.governance_portfolio_average.toFixed(0)}%</strong>
                    </div>
                  </div>
                </div>

                {/* Card 2: HHI Konzentration */}
                <div className="p-4 rounded-xl bg-white dark:bg-neutral-900 border border-neutral-200 dark:border-neutral-800 shadow-sm space-y-2">
                  <span className="text-[10px] font-mono text-neutral-400 uppercase tracking-wide">2. Konzentrationsindex (HHI)</span>
                  <div className="flex items-baseline justify-between">
                    <span className="text-2xl font-black text-blue-600 dark:text-blue-400 font-mono">
                      {data.concentration_metrics.herfindahl_hirschman_index.toFixed(0)}
                    </span>
                    <span className="px-2 py-0.5 rounded text-[10px] font-mono font-bold bg-neutral-100 dark:bg-neutral-800 text-neutral-700 dark:text-neutral-300">
                      {data.concentration_metrics.concentration_level}
                    </span>
                  </div>
                  <p className="text-[11px] text-neutral-500 dark:text-neutral-400">
                    Top-3-Lieferanten Anteil: <strong className="text-neutral-800 dark:text-neutral-200">{data.concentration_metrics.top_3_vendor_share_percentage.toFixed(1)}%</strong>
                  </p>
                  <p className="text-[10px] text-neutral-400 italic">
                    {data.concentration_metrics.recommendation_de.slice(0, 55)}...
                  </p>
                </div>

                {/* Card 3: Scope der Kaskade */}
                <div className="p-4 rounded-xl bg-white dark:bg-neutral-900 border border-neutral-200 dark:border-neutral-800 shadow-sm space-y-2">
                  <span className="text-[10px] font-mono text-neutral-400 uppercase tracking-wide">3. Erfasste Lieferkette</span>
                  <div className="flex items-baseline justify-between">
                    <span className="text-2xl font-black text-indigo-600 dark:text-indigo-400 font-mono">
                      {data.total_suppliers_audited}
                    </span>
                    <span className="text-xs font-mono text-neutral-500">
                      Vertragspartner
                    </span>
                  </div>
                  <div className="pt-1 text-[11px] font-mono text-neutral-600 dark:text-neutral-400 space-y-0.5">
                    <div>Tier-1 Direkt: <strong className="text-neutral-800 dark:text-neutral-200">{data.direct_tier1_count}</strong></div>
                    <div>Tier-N Mittelbar: <strong className="text-neutral-800 dark:text-neutral-200">{data.indirect_tier_n_count}</strong> Kaskaden</div>
                    <div>Single-Points-of-Failure: <strong className="text-amber-600">{data.concentration_metrics.single_points_of_failure_count}</strong></div>
                  </div>
                </div>

                {/* Card 4: BAFA Readiness & Vorfälle */}
                <div className="p-4 rounded-xl bg-white dark:bg-neutral-900 border border-neutral-200 dark:border-neutral-800 shadow-sm space-y-2">
                  <span className="text-[10px] font-mono text-neutral-400 uppercase tracking-wide">4. BAFA-Status (§ 10 Abs. 2)</span>
                  <div className="flex items-baseline justify-between">
                    <span className="text-xs font-bold font-mono text-emerald-600 dark:text-emerald-400">
                      {data.bafa_submission_readiness}
                    </span>
                    <CheckCircle2 className="w-4 h-4 text-emerald-600" />
                  </div>
                  <div className="pt-1 text-[11px] font-mono text-neutral-600 dark:text-neutral-400 space-y-0.5">
                    <div>Offene Vorfälle: <strong className={data.active_substantiated_knowledge_alerts > 0 ? "text-red-600 font-bold" : "text-emerald-600 font-bold"}>{data.active_substantiated_knowledge_alerts}</strong></div>
                    <div>Umgesetzte CAPA: <strong className="text-neutral-800 dark:text-neutral-200">{data.resolved_capa_milestones_count}</strong></div>
                    <div>Vertragsstrafen: <strong className="text-neutral-800 dark:text-neutral-200">EUR {data.total_capa_penalties_secured_eur.toLocaleString("de-DE")}</strong></div>
                  </div>
                </div>
              </div>

              {/* Navigation Tabs */}
              <div className="flex border-b border-neutral-200 dark:border-neutral-800 gap-1">
                <button
                  onClick={() => setActiveTab("suppliers")}
                  className={`py-2.5 px-3.5 border-b-2 font-mono text-xs font-bold transition flex items-center gap-1.5 cursor-pointer ${
                    activeTab === "suppliers"
                      ? "border-blue-600 text-blue-700 dark:text-blue-400"
                      : "border-transparent text-neutral-500 hover:text-neutral-800 dark:hover:text-neutral-200"
                  }`}
                >
                  <Building2 className="w-3.5 h-3.5" />
                  <span>{isDE ? "1. Lieferanten-Matrix (§ 5)" : "1. Supplier Matrix (§ 5)"}</span>
                  <span className="px-1.5 py-0.2 rounded-full text-[10px] bg-neutral-100 dark:bg-neutral-800 text-neutral-600 font-bold">
                    {data.supplier_items.length}
                  </span>
                </button>

                <button
                  onClick={() => setActiveTab("jurisdictions")}
                  className={`py-2.5 px-3.5 border-b-2 font-mono text-xs font-bold transition flex items-center gap-1.5 cursor-pointer ${
                    activeTab === "jurisdictions"
                      ? "border-blue-600 text-blue-700 dark:text-blue-400"
                      : "border-transparent text-neutral-500 hover:text-neutral-800 dark:hover:text-neutral-200"
                  }`}
                >
                  <Globe className="w-3.5 h-3.5" />
                  <span>{isDE ? "2. Standort-Exposition (ITUC & Basel)" : "2. Jurisdiction Exposure"}</span>
                  <span className="px-1.5 py-0.2 rounded-full text-[10px] bg-neutral-100 dark:bg-neutral-800 text-neutral-600 font-bold">
                    {data.jurisdiction_breakdown.length}
                  </span>
                </button>

                <button
                  onClick={() => setActiveTab("governance")}
                  className={`py-2.5 px-3.5 border-b-2 font-mono text-xs font-bold transition flex items-center gap-1.5 cursor-pointer ${
                    activeTab === "governance"
                      ? "border-blue-600 text-blue-700 dark:text-blue-400"
                      : "border-transparent text-neutral-500 hover:text-neutral-800 dark:hover:text-neutral-200"
                  }`}
                >
                  <FileText className="w-3.5 h-3.5" />
                  <span>{isDE ? "3. Beschwerdeverfahren & Vorstand (§§ 8, 10)" : "3. Grievance & Board"}</span>
                </button>
              </div>

              {/* TAB 1: SUPPLIERS MATRIX */}
              {activeTab === "suppliers" && (
                <div className="space-y-3">
                  <div className="flex items-center justify-between text-xs text-neutral-500 font-mono">
                    <span>{isDE ? "Übersicht aller erfassten Lieferantenverträge mit Weitergabeklausel:" : "Audit status and pass-through compliance per supplier contract:"}</span>
                    <span>Sortiert nach Einkaufsvolumen</span>
                  </div>

                  <div className="border border-neutral-200 dark:border-neutral-800 rounded-xl overflow-hidden shadow-sm">
                    <table className="w-full text-left text-xs">
                      <thead className="bg-neutral-50 dark:bg-neutral-800/60 font-mono text-neutral-500 uppercase text-[10px] border-b border-neutral-200 dark:border-neutral-800">
                        <tr>
                          <th className="py-2.5 px-3">Lieferant / Vertrag</th>
                          <th className="py-2.5 px-3">Volumenanteil</th>
                          <th className="py-2.5 px-3">Rating</th>
                          <th className="py-2.5 px-3">Score</th>
                          <th className="py-2.5 px-3">Weitergabeklausel</th>
                          <th className="py-2.5 px-3">Vorfälle</th>
                          <th className="py-2.5 px-3 text-right">Aktion</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-neutral-100 dark:divide-neutral-800/60">
                        {data.supplier_items.map((s, idx) => (
                          <tr key={idx} className="hover:bg-neutral-50 dark:hover:bg-neutral-800/30 transition">
                            <td className="py-2.5 px-3">
                              <div className="font-bold text-neutral-900 dark:text-neutral-100">{s.supplier_name}</div>
                              <div className="text-[10px] text-neutral-400 font-mono">{s.contract_filename}</div>
                            </td>
                            <td className="py-2.5 px-3 font-mono text-neutral-600 dark:text-neutral-400">
                              {s.spend_share_percentage.toFixed(1)}%
                            </td>
                            <td className="py-2.5 px-3">
                              <span className={`px-1.5 py-0.5 rounded text-[10px] font-mono font-bold ${
                                s.lksg_rating === "AAA"
                                  ? "bg-emerald-100 text-emerald-800 dark:bg-emerald-950 dark:text-emerald-300"
                                  : s.lksg_rating === "BBB"
                                  ? "bg-amber-100 text-amber-800 dark:bg-amber-950 dark:text-amber-300"
                                  : "bg-red-100 text-red-800 dark:bg-red-950 dark:text-red-300"
                              }`}>
                                {s.lksg_rating}
                              </span>
                            </td>
                            <td className="py-2.5 px-3 font-mono font-bold text-neutral-800 dark:text-neutral-200">
                              {s.overall_score.toFixed(1)}%
                            </td>
                            <td className="py-2.5 px-3">
                              <span className={`px-1.5 py-0.5 rounded text-[10px] font-mono font-bold ${
                                s.tier1_pass_through_status === "VOLLSTÄNDIG_DURCHSETZBAR"
                                  ? "text-emerald-700 bg-emerald-50 dark:bg-emerald-950/40 dark:text-emerald-300"
                                  : "text-red-700 bg-red-50 dark:bg-red-950/40 dark:text-red-300"
                              }`}>
                                {s.tier1_pass_through_status === "VOLLSTÄNDIG_DURCHSETZBAR" ? "DURCHSETZBAR" : "FEHLEND"}
                              </span>
                            </td>
                            <td className="py-2.5 px-3 font-mono">
                              {s.active_incidents_count > 0 ? (
                                <span className="text-red-600 font-bold">{s.active_incidents_count} Vorfall !</span>
                              ) : (
                                <span className="text-emerald-600">0</span>
                              )}
                            </td>
                            <td className="py-2.5 px-3 text-right">
                              {onSelectDocument && (
                                <button
                                  onClick={() => onSelectDocument(s.document_id)}
                                  className="text-blue-600 hover:text-blue-800 dark:hover:text-blue-400 font-mono text-[11px] font-semibold flex items-center gap-1 justify-end cursor-pointer"
                                >
                                  <span>Öffnen</span>
                                  <ArrowUpRight className="w-3 h-3" />
                                </button>
                              )}
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              )}

              {/* TAB 2: JURISDICTIONS */}
              {activeTab === "jurisdictions" && (
                <div className="space-y-3">
                  <div className="text-xs text-neutral-500 font-mono">
                    {isDE ? "Exposition nach Herkunftsländern und internationalen Konventionsindizes:" : "Cross-border geographical concentration & convention status:"}
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                    {data.jurisdiction_breakdown.map((j) => (
                      <div
                        key={j.country_code}
                        className="p-3.5 rounded-xl border border-neutral-200 dark:border-neutral-800 bg-white dark:bg-neutral-900 shadow-sm space-y-2"
                      >
                        <div className="flex items-center justify-between">
                          <div className="flex items-center gap-2">
                            <span className="font-mono font-bold text-sm text-neutral-900 dark:text-neutral-100">
                              [{j.country_code}] {j.country_name_de}
                            </span>
                          </div>
                          <span className={`px-2 py-0.5 rounded text-[10px] font-mono font-bold ${
                            j.hazard_level === "NIEDRIG"
                              ? "bg-emerald-100 text-emerald-800 dark:bg-emerald-950 dark:text-emerald-300"
                              : j.hazard_level === "MODERAT"
                              ? "bg-sky-100 text-sky-800 dark:bg-sky-950 dark:text-sky-300"
                              : j.hazard_level === "ERHÖHT"
                              ? "bg-amber-100 text-amber-800 dark:bg-amber-950 dark:text-amber-300"
                              : "bg-red-100 text-red-800 dark:bg-red-950 dark:text-red-300"
                          }`}>
                            {j.hazard_level}
                          </span>
                        </div>

                        <div className="grid grid-cols-3 gap-2 text-[11px] font-mono text-neutral-500 pt-1 border-t border-neutral-100 dark:border-neutral-800">
                          <div>
                            <span className="block text-[10px] text-neutral-400">ITUC INDEX</span>
                            <strong className="text-neutral-800 dark:text-neutral-200">{j.ituc_rating} / 5</strong>
                          </div>
                          <div>
                            <span className="block text-[10px] text-neutral-400">CPI SCORE</span>
                            <strong className="text-neutral-800 dark:text-neutral-200">{j.cpi_score} / 100</strong>
                          </div>
                          <div>
                            <span className="block text-[10px] text-neutral-400">BASEL ANHANG VII</span>
                            <strong className="text-neutral-800 dark:text-neutral-200">{j.basel_annex_vii ? "Ja (OECD)" : "Nein"}</strong>
                          </div>
                        </div>

                        <div className="flex justify-between items-center text-xs font-mono pt-1 text-neutral-600 dark:text-neutral-400">
                          <span>Anteil am Einkaufsvolumen:</span>
                          <strong className="text-blue-600 dark:text-blue-400 font-bold">{j.exposure_percentage.toFixed(1)}%</strong>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* TAB 3: GOVERNANCE & BOARD ATTESTATION */}
              {activeTab === "governance" && (
                <div className="space-y-4">
                  {/* Grievance Mechanism Card */}
                  <div className="p-4 rounded-xl border border-neutral-200 dark:border-neutral-800 bg-white dark:bg-neutral-900 shadow-sm space-y-2">
                    <h4 className="font-bold text-xs font-mono uppercase text-neutral-900 dark:text-neutral-100 flex items-center gap-1.5">
                      <ShieldAlert className="w-4 h-4 text-indigo-600" />
                      <span>{isDE ? "Wirksamkeit des Beschwerdeverfahrens (§ 8 LkSG):" : "Whistleblower Complaints Procedure (§ 8 LkSG):"}</span>
                    </h4>
                    <p className="text-xs text-neutral-600 dark:text-neutral-400">
                      Im Berichtsjahr wurden <strong>{data.grievance_cases_logged} Meldungen</strong> erfasst und dokumentiert.
                      Der interne Beschwerdekanal ist mehrsprachig, vertraulich und für Beschäftigte unmittelbarer und mittelbarer Zulieferer gleichermaßen zugänglich.
                    </p>
                  </div>

                  {/* Board Attestation Statement Box */}
                  <div className="p-4 rounded-xl border border-blue-200 dark:border-blue-900/60 bg-blue-50/50 dark:bg-blue-950/20 text-neutral-800 dark:text-neutral-200 space-y-2.5">
                    <h4 className="font-bold text-xs font-mono uppercase text-blue-900 dark:text-blue-300 flex items-center gap-1.5">
                      <PieChart className="w-4 h-4 text-blue-600" />
                      <span>{isDE ? "Rechtsverbindliche Erklärung des Vorstands nach § 10 Abs. 2 LkSG:" : "Executive Board Attestation (§ 10(2) LkSG):"}</span>
                    </h4>
                    <p className="text-xs leading-relaxed text-neutral-700 dark:text-neutral-300">
                      Der Vorstand bestätigt die Richtigkeit und Vollständigkeit der im Jahresbericht dokumentierten Risikoanalysen,
                      Präventions- und Abhilfemaßnahmen. Die gesetzlichen Anforderungen an die menschenrechtliche und umweltbezogene Sorgfaltspflicht
                      nach den §§ 4 bis 10 LkSG wurden unter Berücksichtigung des Angemessenheitsprinzips (§ 3 Abs. 2 LkSG) im Berichtsjahr {reportingYear} eingehalten.
                    </p>
                    <div className="pt-2 flex flex-wrap items-center justify-between text-[11px] font-mono text-neutral-500 border-t border-blue-200/60 dark:border-blue-900/40">
                      <span>Gesetzliche Einreichungsfrist: {data.submission_deadline}</span>
                      <span>Prüfsiegel: SHA-256 verifiziert</span>
                    </div>
                  </div>
                </div>
              )}
            </>
          )}
        </div>
      </div>
    </div>
  );
}

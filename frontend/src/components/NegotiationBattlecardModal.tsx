"use client";

import React, { useState, useEffect, useCallback } from "react";
import {
  ShieldAlert,
  ShieldCheck,
  Scale,
  Download,
  X,
  AlertTriangle,
  Copy,
  Check,
  Sparkles,
  ExternalLink,
  Flame,
  Globe2,
  Lock,
  Cpu,
  Clock,
  Building2,
  AlertOctagon,
  ChevronDown,
  ChevronUp,
  FileText,
  Sliders,
} from "lucide-react";
import {
  BattlecardItem,
  NegotiationBattlecardResponse,
  SlaSimulationResponse,
  downloadBattlecardPdf,
  getNegotiationBattlecard,
  simulateSlaOutage,
} from "@/lib/api";
import { Language } from "@/lib/i18n";

interface NegotiationBattlecardModalProps {
  isOpen: boolean;
  onClose: () => void;
  documentId?: string;
  lang?: Language;
  onJumpToCitation?: (citation: { page_number: number; bounding_box?: [number, number, number, number] }) => void;
}

export function NegotiationBattlecardModal({
  isOpen,
  onClose,
  documentId,
  lang = "DE",
  onJumpToCitation,
}: NegotiationBattlecardModalProps) {
  const isDE = lang === "DE";

  const [activeTab, setActiveTab] = useState<"battlecards" | "schrems_tia" | "sla_simulator">("battlecards");
  const [loading, setLoading] = useState<boolean>(false);
  const [downloadingPdf, setDownloadingPdf] = useState<boolean>(false);
  const [data, setData] = useState<NegotiationBattlecardResponse | null>(null);
  const [filterSeverity, setFilterSeverity] = useState<string>("ALL");
  const [expandedCards, setExpandedCards] = useState<Record<string, boolean>>({});
  const [copiedKey, setCopiedKey] = useState<string | null>(null);

  // SLA Outage Simulator State
  const [simDowntime, setSimDowntime] = useState<number>(12.0);
  const [simContractValue, setSimContractValue] = useState<number>(500000);
  const [simAvailability, setSimAvailability] = useState<number>(99.95);
  const [simResult, setSimResult] = useState<SlaSimulationResponse | null>(null);
  const [simulating, setSimulating] = useState<boolean>(false);

  const loadData = useCallback(async () => {
    if (!documentId) return;
    setLoading(true);
    try {
      const res = await getNegotiationBattlecard(documentId);
      setData(res);
      // Auto-expand first 2 battlecards
      if (res.battlecards.length > 0) {
        const initial: Record<string, boolean> = {};
        res.battlecards.slice(0, 2).forEach((b) => {
          initial[b.id] = true;
        });
        setExpandedCards(initial);
      }
    } catch (err) {
      console.error("Failed to load battlecard data:", err);
    } finally {
      setLoading(false);
    }
  }, [documentId]);

  const runSimulation = useCallback(
    async (downtime: number, val: number, avail: number) => {
      setSimulating(true);
      try {
        const res = await simulateSlaOutage({
          downtime_hours: downtime,
          contract_value_eur: val,
          availability_target_pct: avail,
        });
        setSimResult(res);
      } catch (err) {
        console.error("Failed to run SLA simulation:", err);
      } finally {
        setSimulating(false);
      }
    },
    []
  );

  useEffect(() => {
    if (isOpen && documentId) {
      loadData();
      runSimulation(simDowntime, simContractValue, simAvailability);
    }
  }, [isOpen, documentId, loadData, runSimulation, simDowntime, simContractValue, simAvailability]);

  const toggleExpand = (id: string) => {
    setExpandedCards((prev) => ({ ...prev, [id]: !prev[id] }));
  };

  const copyToClipboard = (text: string, key: string) => {
    navigator.clipboard.writeText(text);
    setCopiedKey(key);
    setTimeout(() => setCopiedKey(null), 2000);
  };

  const handleDownloadPdf = async () => {
    if (!documentId || downloadingPdf) return;
    setDownloadingPdf(true);
    try {
      await downloadBattlecardPdf(documentId, "Dr. Michael Weber, Leitender DORA- & BaFin-Prüfer");
    } catch (err: any) {
      alert(err?.message || "Failed to download battlecard PDF");
    } finally {
      setDownloadingPdf(false);
    }
  };

  if (!isOpen) return null;

  const filteredBattlecards =
    data?.battlecards.filter((b) => {
      if (filterSeverity === "ALL") return true;
      return b.severity === filterSeverity;
    }) || [];

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-md animate-in fade-in duration-200">
      <div className="relative w-full max-w-5xl max-h-[92vh] flex flex-col rounded-2xl bg-white dark:bg-neutral-900 border border-neutral-200 dark:border-neutral-800 shadow-2xl overflow-hidden font-sans">
        {/* MODAL HEADER */}
        <div className="p-6 border-b border-neutral-200 dark:border-neutral-800 bg-gradient-to-r from-red-500/10 via-amber-500/5 to-transparent flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-red-600 to-amber-600 text-white flex items-center justify-center shadow-lg shadow-red-500/20">
              <Flame className="w-6 h-6 animate-pulse" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h2 className="text-xl font-bold tracking-tight text-neutral-900 dark:text-neutral-100">
                  {isDE ? "Aufsichtsrechtliche Verhandlungs-Battlecard & TIA" : "Procurement Negotiation Battlecard & Schrems II TIA"}
                </h2>
                <span className="px-2.5 py-0.5 rounded-full text-[10px] font-mono font-bold bg-red-100 text-red-700 dark:bg-red-950/80 dark:text-red-300 border border-red-300 dark:border-red-800">
                  DORA · CLOUD ACT · BGB
                </span>
              </div>
              <p className="text-xs text-neutral-500 dark:text-neutral-400 mt-0.5">
                {isDE
                  ? "Unwiderlegbare Banken-Gegenargumente, Musterklauseln und Schrems II Transfer Impact Assessment für Hyperscaler-Verhandlungen"
                  : "Unassailable statutory counter-arguments, Musterklauseln and Schrems II TIA for hyperscaler negotiations"}
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={handleDownloadPdf}
              disabled={downloadingPdf || !data}
              className="px-3.5 py-2 rounded-xl text-xs font-semibold bg-neutral-900 text-white dark:bg-neutral-100 dark:text-neutral-900 hover:opacity-90 transition flex items-center gap-2 disabled:opacity-50 cursor-pointer shadow-sm"
            >
              <Download className="w-3.5 h-3.5" />
              <span>{downloadingPdf ? (isDE ? "Exportiere..." : "Exporting...") : isDE ? "DIN 5008 Dossier (PDF)" : "DIN 5008 Dossier (PDF)"}</span>
            </button>
            <button
              onClick={onClose}
              className="p-2 rounded-xl hover:bg-neutral-100 dark:hover:bg-neutral-800 text-neutral-400 hover:text-neutral-600 dark:hover:text-neutral-200 transition cursor-pointer"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* POSTURE & METRICS BANNER */}
        {data && (
          <div className="px-6 py-3 border-b border-neutral-200 dark:border-neutral-800 bg-neutral-50 dark:bg-neutral-950/40 flex flex-wrap items-center justify-between gap-4 text-xs">
            <div className="flex items-center gap-4">
              <div className="flex items-center gap-1.5 font-mono">
                <span className="text-neutral-400">{isDE ? "Verhandlungsposition:" : "Posture:"}</span>
                <span
                  className={`font-bold px-2 py-0.5 rounded ${
                    data.overall_negotiation_posture === "UNACCEPTABLE_HIGH_RISK"
                      ? "bg-red-100 text-red-700 dark:bg-red-950/80 dark:text-red-300 border border-red-300 dark:border-red-800"
                      : "bg-emerald-100 text-emerald-700 dark:bg-emerald-950/80 dark:text-emerald-300"
                  }`}
                >
                  {data.overall_negotiation_posture === "UNACCEPTABLE_HIGH_RISK"
                    ? isDE
                      ? "NICHT FREIGABEFÄHIG (ROTE LINIE)"
                      : "UNACCEPTABLE HIGH RISK"
                    : isDE
                    ? "BEDINGT FREIGABEFÄHIG"
                    : "CONDITIONAL"}
                </span>
              </div>

              <div className="flex items-center gap-2 font-mono text-[11px] text-neutral-500">
                <span className="text-red-600 font-bold">{data.critical_count} Kritische Blocker</span>
                <span>•</span>
                <span className="text-amber-600 font-bold">{data.high_count} Wesentliche Risiken</span>
              </div>
            </div>

            <div className="flex items-center gap-3">
              <span className="text-neutral-400">{isDE ? "Schrems II Risiko:" : "Schrems II Risk:"}</span>
              <span className="px-2 py-0.5 font-mono font-bold rounded bg-neutral-200 dark:bg-neutral-800 text-neutral-800 dark:text-neutral-200">
                {data.tia_assessment.overall_transfer_risk} ({data.tia_assessment.transfer_risk_score}%)
              </span>
            </div>
          </div>
        )}

        {/* TABS SELECTOR */}
        <div className="px-6 border-b border-neutral-200 dark:border-neutral-800 flex items-center gap-1 bg-white dark:bg-neutral-900">
          <button
            onClick={() => setActiveTab("battlecards")}
            className={`px-4 py-3 text-xs font-bold border-b-2 transition flex items-center gap-2 cursor-pointer ${
              activeTab === "battlecards"
                ? "border-red-600 text-red-600 dark:text-red-400"
                : "border-transparent text-neutral-500 hover:text-neutral-700 dark:hover:text-neutral-300"
            }`}
          >
            <Flame className="w-4 h-4" />
            <span>{isDE ? "1. Verhandlungs-Battlecards & Musterklauseln" : "1. Negotiation Battlecards & Fallbacks"}</span>
            {data && (
              <span className="px-1.5 py-0.2 rounded-full text-[10px] bg-red-100 text-red-700 dark:bg-red-950/80 dark:text-red-300 font-mono">
                {data.total_battlecards}
              </span>
            )}
          </button>

          <button
            onClick={() => setActiveTab("schrems_tia")}
            className={`px-4 py-3 text-xs font-bold border-b-2 transition flex items-center gap-2 cursor-pointer ${
              activeTab === "schrems_tia"
                ? "border-red-600 text-red-600 dark:text-red-400"
                : "border-transparent text-neutral-500 hover:text-neutral-700 dark:hover:text-neutral-300"
            }`}
          >
            <Globe2 className="w-4 h-4" />
            <span>{isDE ? "2. Schrems II & US CLOUD Act Konflikt-Radar" : "2. Schrems II & US CLOUD Act Radar"}</span>
          </button>

          <button
            onClick={() => setActiveTab("sla_simulator")}
            className={`px-4 py-3 text-xs font-bold border-b-2 transition flex items-center gap-2 cursor-pointer ${
              activeTab === "sla_simulator"
                ? "border-red-600 text-red-600 dark:text-red-400"
                : "border-transparent text-neutral-500 hover:text-neutral-700 dark:hover:text-neutral-300"
            }`}
          >
            <Sliders className="w-4 h-4" />
            <span>{isDE ? "3. Was-Wäre-Wenn SLA-Ausfallsimulator" : "3. What-If SLA Outage Simulator"}</span>
          </button>
        </div>

        {/* TAB CONTENT CONTAINER */}
        <div className="flex-1 overflow-y-auto p-6 space-y-4">
          {loading && (
            <div className="py-20 text-center text-neutral-400">
              <div className="w-8 h-8 mx-auto border-2 border-red-500 border-t-transparent rounded-full animate-spin mb-3" />
              <p className="text-xs font-mono">{isDE ? "Analysiere US CLOUD Act, Schrems II und DORA-Klauseln..." : "Analyzing US CLOUD Act, Schrems II and DORA clauses..."}</p>
            </div>
          )}

          {/* TAB 1: BATTLECARDS */}
          {!loading && activeTab === "battlecards" && (
            <div className="space-y-4">
              {/* Filter Row */}
              <div className="flex items-center justify-between pb-2">
                <span className="text-xs text-neutral-500">
                  {isDE ? "Filtere nach Verhandlungsdringlichkeit:" : "Filter by negotiation priority:"}
                </span>
                <div className="flex items-center gap-1.5">
                  {["ALL", "CRITICAL", "HIGH", "MEDIUM"].map((lvl) => (
                    <button
                      key={lvl}
                      onClick={() => setFilterSeverity(lvl)}
                      className={`px-2.5 py-1 rounded-lg text-xs font-mono font-bold transition cursor-pointer ${
                        filterSeverity === lvl
                          ? "bg-neutral-900 text-white dark:bg-neutral-100 dark:text-neutral-900"
                          : "bg-neutral-100 dark:bg-neutral-800 text-neutral-500 hover:text-neutral-900 dark:hover:text-neutral-100"
                      }`}
                    >
                      {lvl}
                    </button>
                  ))}
                </div>
              </div>

              {filteredBattlecards.map((bc, idx) => {
                const isExpanded = !!expandedCards[bc.id];
                return (
                  <div
                    key={bc.id}
                    className="rounded-xl border border-neutral-200 dark:border-neutral-800 bg-white dark:bg-neutral-900 overflow-hidden shadow-sm transition"
                  >
                    {/* Header Strip */}
                    <div
                      onClick={() => toggleExpand(bc.id)}
                      className="p-4 flex items-center justify-between cursor-pointer hover:bg-neutral-50 dark:hover:bg-neutral-950/40 transition"
                    >
                      <div className="flex items-center gap-3 min-w-0">
                        <span
                          className={`w-7 h-7 rounded-lg font-mono text-xs font-bold flex items-center justify-center shrink-0 ${
                            bc.severity === "CRITICAL"
                              ? "bg-red-100 text-red-700 dark:bg-red-950/80 dark:text-red-300"
                              : "bg-amber-100 text-amber-700 dark:bg-amber-950/80 dark:text-amber-300"
                          }`}
                        >
                          {idx + 1}
                        </span>
                        <div className="min-w-0">
                          <div className="flex items-center gap-2">
                            <h4 className="text-sm font-bold text-neutral-900 dark:text-neutral-100 truncate">
                              {isDE ? bc.title_de : bc.title_en}
                            </h4>
                            <span
                              className={`px-2 py-0.5 rounded text-[10px] font-mono font-bold ${
                                bc.severity === "CRITICAL"
                                  ? "bg-red-500/10 text-red-600 dark:text-red-400 border border-red-500/20"
                                  : "bg-amber-500/10 text-amber-600 dark:text-amber-400 border border-amber-500/20"
                              }`}
                            >
                              {bc.severity}
                            </span>
                          </div>
                          <span className="text-[11px] font-mono text-neutral-400">{bc.statutory_reference}</span>
                        </div>
                      </div>

                      <div className="flex items-center gap-3 shrink-0">
                        {onJumpToCitation && (
                          <button
                            onClick={(e) => {
                              e.stopPropagation();
                              onJumpToCitation({ page_number: bc.page_number });
                            }}
                            className="px-2 py-1 rounded text-[11px] font-mono bg-neutral-100 dark:bg-neutral-800 text-neutral-600 dark:text-neutral-300 hover:bg-neutral-200 transition flex items-center gap-1"
                          >
                            <span>S. {bc.page_number}</span>
                            <ExternalLink className="w-3 h-3" />
                          </button>
                        )}
                        {isExpanded ? <ChevronUp className="w-4 h-4 text-neutral-400" /> : <ChevronDown className="w-4 h-4 text-neutral-400" />}
                      </div>
                    </div>

                    {/* Expandable Body */}
                    {isExpanded && (
                      <div className="p-4 pt-0 space-y-3.5 border-t border-neutral-100 dark:border-neutral-800/60 bg-neutral-50/50 dark:bg-neutral-950/20 text-xs">
                        {/* 1. Vendor Clause */}
                        <div className="p-3 rounded-lg bg-red-50/60 dark:bg-red-950/20 border border-red-200/60 dark:border-red-900/40">
                          <span className="text-[10px] font-mono uppercase font-bold text-red-600 dark:text-red-400 flex items-center gap-1.5">
                            🚩 {isDE ? "Anbieter-Originalklausel (Vertragstext):" : "Vendor Clause (Original Text):"}
                          </span>
                          <p className="mt-1 font-serif text-neutral-800 dark:text-neutral-200 italic leading-relaxed">
                            &ldquo;{bc.vendor_clause_quote}&rdquo;
                          </p>
                        </div>

                        {/* 2. Vendor Defense vs Bank Counter */}
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                          <div className="p-3 rounded-lg bg-neutral-100/70 dark:bg-neutral-800/50 border border-neutral-200 dark:border-neutral-800">
                            <span className="text-[10px] font-mono uppercase font-bold text-neutral-500 flex items-center gap-1.5">
                              🛡️ {isDE ? "Typische Hyperscaler-Verteidigung:" : "Vendor Typical Defense:"}
                            </span>
                            <p className="mt-1 text-neutral-700 dark:text-neutral-300 leading-relaxed">
                              {bc.vendor_common_defense}
                            </p>
                          </div>

                          <div className="p-3 rounded-lg bg-emerald-50/70 dark:bg-emerald-950/20 border border-emerald-200/70 dark:border-emerald-900/40">
                            <div className="flex items-center justify-between">
                              <span className="text-[10px] font-mono uppercase font-bold text-emerald-700 dark:text-emerald-400 flex items-center gap-1.5">
                                ⚡ {isDE ? "Unwiderlegbares Banken-Gegenargument:" : "Bank Unassailable Counter-Argument:"}
                              </span>
                              <button
                                onClick={() => copyToClipboard(bc.bank_counter_argument, `arg-${bc.id}`)}
                                className="text-[10px] font-mono text-emerald-600 hover:underline flex items-center gap-1 cursor-pointer"
                              >
                                {copiedKey === `arg-${bc.id}` ? <Check className="w-3 h-3" /> : <Copy className="w-3 h-3" />}
                                <span>{copiedKey === `arg-${bc.id}` ? "Kopiert" : "Kopieren"}</span>
                              </button>
                            </div>
                            <p className="mt-1 text-neutral-900 dark:text-neutral-100 font-medium leading-relaxed">
                              {bc.bank_counter_argument}
                            </p>
                          </div>
                        </div>

                        {/* 3. Non-Negotiable Musterklausel */}
                        <div className="p-3 rounded-lg bg-white dark:bg-neutral-900 border border-neutral-200 dark:border-neutral-800">
                          <div className="flex items-center justify-between">
                            <span className="text-[10px] font-mono uppercase font-bold text-neutral-700 dark:text-neutral-300 flex items-center gap-1.5">
                              ✍️ {isDE ? "Nicht verhandelbare Musterklausel (Nachtragsvereinbarung):" : "Non-Negotiable Fallback Clause:"}
                            </span>
                            <button
                              onClick={() => copyToClipboard(bc.non_negotiable_clause_de, `clause-${bc.id}`)}
                              className="text-[10px] font-mono text-blue-600 dark:text-blue-400 hover:underline flex items-center gap-1 cursor-pointer"
                            >
                              {copiedKey === `clause-${bc.id}` ? <Check className="w-3 h-3" /> : <Copy className="w-3 h-3" />}
                              <span>{copiedKey === `clause-${bc.id}` ? "Kopiert" : "Musterklausel kopieren"}</span>
                            </button>
                          </div>
                          <p className="mt-1 font-mono text-[11px] text-neutral-800 dark:text-neutral-200 bg-neutral-50 dark:bg-neutral-950 p-2.5 rounded border border-neutral-200/60 dark:border-neutral-800 leading-relaxed">
                            {bc.non_negotiable_clause_de}
                          </p>
                        </div>

                        {/* 4. BaFin Escalation Statement */}
                        <div className="p-2.5 rounded-lg bg-neutral-200/50 dark:bg-neutral-800/40 text-[11px] text-neutral-600 dark:text-neutral-400 flex items-center gap-2">
                          <Building2 className="w-4 h-4 text-neutral-500 shrink-0" />
                          <span>
                            <strong>{isDE ? "BaFin-Eskalationsspruch:" : "BaFin Escalation Statement:"}</strong> {bc.bafin_escalation_script}
                          </span>
                        </div>
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          )}

          {/* TAB 2: SCHREMS II & CLOUD ACT RADAR */}
          {!loading && activeTab === "schrems_tia" && data && (
            <div className="space-y-4">
              <div className="p-5 rounded-xl border border-neutral-200 dark:border-neutral-800 bg-gradient-to-br from-blue-500/10 via-transparent to-purple-500/10">
                <div className="flex items-center gap-2">
                  <Globe2 className="w-5 h-5 text-blue-600" />
                  <h3 className="text-sm font-bold text-neutral-900 dark:text-neutral-100">
                    {isDE ? "Schrems II Transfer Impact Assessment (TIA) & CLOUD Act Konfliktmatrix" : "Schrems II TIA & CLOUD Act Conflict Matrix"}
                  </h3>
                </div>
                <p className="text-xs text-neutral-500 dark:text-neutral-400 mt-1 max-w-3xl leading-relaxed">
                  {isDE
                    ? "Rechtliche Kollisionsanalyse zwischen dem US CLOUD Act (Section 105), Art. 48 DSGVO (Drittstaatenübermittlung ohne MLAT) und dem deutschen Bankgeheimnis (§ 25a KWG / § 203 StGB)."
                    : "Legal collision analysis between US CLOUD Act (Section 105), GDPR Art. 48, and German banking secrecy laws."}
                </p>

                {/* 4 Gauges */}
                <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mt-4">
                  <div className="p-3.5 rounded-xl bg-white dark:bg-neutral-900 border border-neutral-200 dark:border-neutral-800 text-center">
                    <span className="text-[10px] font-mono text-neutral-400 uppercase">TIA Risiko-Score</span>
                    <div className="text-2xl font-black font-mono text-red-600 mt-1">{data.tia_assessment.transfer_risk_score}%</div>
                    <span className="text-[10px] font-bold text-red-600">{data.tia_assessment.overall_transfer_risk}</span>
                  </div>

                  <div className="p-3.5 rounded-xl bg-white dark:bg-neutral-900 border border-neutral-200 dark:border-neutral-800 text-center">
                    <span className="text-[10px] font-mono text-neutral-400 uppercase">US CLOUD Act</span>
                    <div className="text-sm font-bold mt-2 text-neutral-800 dark:text-neutral-200">
                      {data.tia_assessment.cloud_act_exposure ? "⚠️ EXPOSITION" : "✅ ABGESCHIRMT"}
                    </div>
                    <span className="text-[10px] text-neutral-400">US-Gerichtsbarkeit</span>
                  </div>

                  <div className="p-3.5 rounded-xl bg-white dark:bg-neutral-900 border border-neutral-200 dark:border-neutral-800 text-center">
                    <span className="text-[10px] font-mono text-neutral-400 uppercase">HYOK Verschlüsselung</span>
                    <div className="text-sm font-bold mt-2 text-neutral-800 dark:text-neutral-200">
                      {data.tia_assessment.encryption_hyok_verified ? "✅ ZERTIFIZIERT" : "❌ FEHLT (RISIKO)"}
                    </div>
                    <span className="text-[10px] text-neutral-400">Bank-owned HSM</span>
                  </div>

                  <div className="p-3.5 rounded-xl bg-white dark:bg-neutral-900 border border-neutral-200 dark:border-neutral-800 text-center">
                    <span className="text-[10px] font-mono text-neutral-400 uppercase">EWR-Residenz</span>
                    <div className="text-sm font-bold mt-2 text-neutral-800 dark:text-neutral-200">
                      {data.tia_assessment.eu_data_residency_guaranteed ? "✅ FRANKFURT/EWR" : "⚠️ OFFSHORE-TRANSFER"}
                    </div>
                    <span className="text-[10px] text-neutral-400">Server-Standort</span>
                  </div>
                </div>
              </div>

              {/* Legal Collision Explainer */}
              <div className="p-4 rounded-xl border border-neutral-200 dark:border-neutral-800 bg-white dark:bg-neutral-900 space-y-3">
                <h4 className="text-xs font-bold text-neutral-900 dark:text-neutral-100 flex items-center gap-2">
                  <Scale className="w-4 h-4 text-amber-600" />
                  <span>{isDE ? "Aufsichtsrechtliches BaFin-Prüfvotum:" : "Regulatory BaFin Audit Verdict:"}</span>
                </h4>
                <div className="p-3 rounded-lg bg-neutral-100 dark:bg-neutral-950 font-mono text-xs text-neutral-800 dark:text-neutral-200 leading-relaxed">
                  {data.tia_assessment.bafin_audit_clearance}
                </div>

                <div className="p-3 rounded-lg bg-blue-50/60 dark:bg-blue-950/20 border border-blue-200/60 dark:border-blue-900/40 text-xs text-blue-900 dark:text-blue-200">
                  <strong>{isDE ? "Zwingende Abhilfemaßnahme:" : "Required Mitigation Action:"}</strong> {data.tia_assessment.mitigation_recommendation}
                </div>
              </div>
            </div>
          )}

          {/* TAB 3: SLA OUTAGE STRESS SIMULATOR */}
          {activeTab === "sla_simulator" && (
            <div className="space-y-4">
              <div className="p-5 rounded-xl border border-neutral-200 dark:border-neutral-800 bg-gradient-to-br from-amber-500/10 via-transparent to-red-500/10">
                <div className="flex items-center gap-2">
                  <Clock className="w-5 h-5 text-amber-600" />
                  <h3 className="text-sm font-bold text-neutral-900 dark:text-neutral-100">
                    {isDE ? "Interaktiver 'Was-Wäre-Wenn' SLA-Ausfallstress-Simulator" : "Interactive What-If SLA Outage Stress Simulator"}
                  </h3>
                </div>
                <p className="text-xs text-neutral-500 dark:text-neutral-400 mt-1">
                  {isDE
                    ? "Verschieben Sie den Regler, um die vertraglichen Pönalen, DORA-Meldepflichten und gesetzlichen Kündigungsrechte bei Serverausfall in Echtzeit zu berechnen."
                    : "Slide the controller to calculate contract penalties, DORA notification triggers, and termination thresholds."}
                </p>

                {/* SLIDER CONTROLS */}
                <div className="mt-5 space-y-4">
                  <div>
                    <div className="flex justify-between items-center mb-1 text-xs">
                      <span className="font-bold text-neutral-800 dark:text-neutral-200">
                        {isDE ? "Hypothetische Ausfalldauer:" : "Hypothetical Outage Duration:"}
                      </span>
                      <span className="font-mono text-base font-black text-red-600">{simDowntime} Stunden</span>
                    </div>
                    <input
                      type="range"
                      min="0.5"
                      max="72"
                      step="0.5"
                      value={simDowntime}
                      onChange={(e) => {
                        const val = parseFloat(e.target.value);
                        setSimDowntime(val);
                        runSimulation(val, simContractValue, simAvailability);
                      }}
                      className="w-full accent-red-600 h-2 bg-neutral-200 dark:bg-neutral-800 rounded-lg cursor-pointer"
                    />
                    <div className="flex justify-between text-[10px] font-mono text-neutral-400 mt-1">
                      <span>0.5h (Toleriert)</span>
                      <span>4.38h (Jahresgrenze)</span>
                      <span>8h (DORA Major)</span>
                      <span>24h (Systemkrise)</span>
                      <span>72h (Kündigung)</span>
                    </div>
                  </div>

                  {/* Input parameters */}
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-3 pt-2">
                    <div className="p-3 rounded-lg bg-white dark:bg-neutral-900 border border-neutral-200 dark:border-neutral-800">
                      <label className="text-[10px] font-mono uppercase text-neutral-400">{isDE ? "Jahresvertragswert (EUR)" : "Contract Value (EUR)"}</label>
                      <input
                        type="number"
                        value={simContractValue}
                        onChange={(e) => {
                          const val = parseFloat(e.target.value) || 0;
                          setSimContractValue(val);
                          runSimulation(simDowntime, val, simAvailability);
                        }}
                        className="w-full mt-1 bg-transparent font-mono text-sm font-bold text-neutral-900 dark:text-neutral-100 outline-none"
                      />
                    </div>

                    <div className="p-3 rounded-lg bg-white dark:bg-neutral-900 border border-neutral-200 dark:border-neutral-800">
                      <label className="text-[10px] font-mono uppercase text-neutral-400">{isDE ? "Vereinbarte Verfügbarkeit (%)" : "Agreed SLA Target (%)"}</label>
                      <input
                        type="number"
                        step="0.01"
                        value={simAvailability}
                        onChange={(e) => {
                          const val = parseFloat(e.target.value) || 99.0;
                          setSimAvailability(val);
                          runSimulation(simDowntime, simContractValue, val);
                        }}
                        className="w-full mt-1 bg-transparent font-mono text-sm font-bold text-neutral-900 dark:text-neutral-100 outline-none"
                      />
                    </div>
                  </div>
                </div>
              </div>

              {/* SIMULATION RESULTS GAUGES */}
              {simResult && (
                <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                  <div className="p-4 rounded-xl border border-neutral-200 dark:border-neutral-800 bg-white dark:bg-neutral-900 text-center">
                    <span className="text-[10px] font-mono text-neutral-400 uppercase">Vertragliche Pönale</span>
                    <div className="text-2xl font-black font-mono text-neutral-900 dark:text-neutral-100 mt-1">
                      EUR {simResult.penalty_eur.toLocaleString("de-DE")}
                    </div>
                    <span className="text-[11px] font-mono text-neutral-500">
                      ({simResult.penalty_pct_of_annual_contract}% des Jahresvolumens)
                    </span>
                  </div>

                  <div className="p-4 rounded-xl border border-neutral-200 dark:border-neutral-800 bg-white dark:bg-neutral-900 text-center">
                    <span className="text-[10px] font-mono text-neutral-400 uppercase">DORA Vorfallsklasse</span>
                    <div
                      className={`text-sm font-bold mt-2 ${
                        simResult.dora_incident_classification === "CRITICAL_SYSTEMIC_INCIDENT"
                          ? "text-red-600 animate-pulse"
                          : simResult.dora_incident_classification === "MAJOR_INCIDENT"
                          ? "text-amber-600"
                          : "text-emerald-600"
                      }`}
                    >
                      {simResult.dora_incident_classification}
                    </div>
                    <span className="text-[10px] text-neutral-400">DORA Art. 19 Einstufung</span>
                  </div>

                  <div className="p-4 rounded-xl border border-neutral-200 dark:border-neutral-800 bg-white dark:bg-neutral-900 text-center">
                    <span className="text-[10px] font-mono text-neutral-400 uppercase">Gesetzliche Kündigung</span>
                    <div
                      className={`text-sm font-bold mt-2 ${
                        simResult.statutory_extraordinary_termination_triggered ? "text-red-600 font-black" : "text-neutral-400"
                      }`}
                    >
                      {simResult.statutory_extraordinary_termination_triggered
                        ? "🚨 KÜNDIGUNGSRECHT AKTIV"
                        : "Nicht ausgelöst"}
                    </div>
                    <span className="text-[10px] text-neutral-400">DORA Art. 28 Abs. 7</span>
                  </div>
                </div>
              )}

              {/* NOTIFICATION TIMELINE */}
              {simResult && (
                <div className="p-4 rounded-xl border border-neutral-200 dark:border-neutral-800 bg-white dark:bg-neutral-900 space-y-2 text-xs">
                  <h4 className="font-bold text-neutral-900 dark:text-neutral-100 flex items-center gap-2">
                    <AlertOctagon className="w-4 h-4 text-red-600" />
                    <span>{isDE ? "Aufsichtsrechtliche BaFin-Meldepflichten:" : "Supervisory BaFin Reporting Deadlines:"}</span>
                  </h4>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-2 text-[11px] font-mono">
                    <div className="p-2.5 rounded bg-neutral-100 dark:bg-neutral-950">
                      <span className="text-neutral-500">Ad-hoc Erstmeldung:</span>
                      <p className="font-bold text-red-600 mt-0.5">{simResult.bafin_initial_notification_deadline}</p>
                    </div>
                    <div className="p-2.5 rounded bg-neutral-100 dark:bg-neutral-950">
                      <span className="text-neutral-500">Zwischenbericht:</span>
                      <p className="font-bold text-neutral-800 dark:text-neutral-200 mt-0.5">{simResult.bafin_intermediate_report_deadline}</p>
                    </div>
                  </div>
                  <p className="text-[11px] text-neutral-500 italic mt-2">{simResult.rationale}</p>
                </div>
              )}
            </div>
          )}
        </div>

        {/* MODAL FOOTER */}
        <div className="p-4 border-t border-neutral-200 dark:border-neutral-800 bg-neutral-50 dark:bg-neutral-950 flex items-center justify-between text-xs text-neutral-500">
          <div className="flex items-center gap-2">
            <Lock className="w-3.5 h-3.5 text-emerald-600" />
            <span>{isDE ? "Souveräne lokale Berechnung (Zero-Cloud-Leak)" : "Sovereign Local Computation (Zero-Cloud-Leak)"}</span>
          </div>
          <button
            onClick={onClose}
            className="px-4 py-2 rounded-xl text-xs font-semibold bg-neutral-200 dark:bg-neutral-800 hover:bg-neutral-300 dark:hover:bg-neutral-700 text-neutral-800 dark:text-neutral-200 transition cursor-pointer"
          >
            {isDE ? "Schließen" : "Close"}
          </button>
        </div>
      </div>
    </div>
  );
}

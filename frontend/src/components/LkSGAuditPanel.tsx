"use client";

import React, { useState, useEffect, useCallback } from "react";
import {
  Shield,
  ShieldCheck,
  ShieldAlert,
  AlertTriangle,
  FileText,
  X,
  ExternalLink,
  ChevronRight,
  ChevronDown,
  Building2,
  Users,
  Leaf,
  Scale,
  Download,
  Filter,
  CheckCircle2,
  AlertOctagon,
  RefreshCw,
  Sparkles,
  ClipboardCheck,
  Loader2,
  Check,
  HelpCircle,
  CalendarCheck,
  Clock,
  Coins,
  Network,
  Globe,
  Workflow,
  AlertCircle,
} from "lucide-react";
import { Language } from "@/lib/i18n";
import {
  LkSGAuditResponse,
  LkSGRiskItem,
  getLkSGAudit,
  BafaQuestionnaireResponse,
  BafaQuestionnaireSection,
  getBafaQuestionnaire,
  downloadBafaReportPdf,
  SupplierCapaPlan,
  getSupplierCapaPlan,
  downloadCapaPlanPdf,
  EnvironmentalAuditReport,
  getEnvironmentalAudit,
  downloadEnvironmentalCertificatePdf,
  TierNCascadeAuditReport,
  getTierNCascadeAudit,
  downloadTierNCascadePdf,
} from "@/lib/api";

interface LkSGAuditPanelProps {
  isOpen: boolean;
  onClose: () => void;
  lang: Language;
  documentId?: string | null;
  documentName?: string;
  onJumpToCitation?: (page: number, bbox?: [number, number, number, number]) => void;
}

export function LkSGAuditPanel({
  isOpen,
  onClose,
  lang,
  documentId,
  documentName,
  onJumpToCitation,
}: LkSGAuditPanelProps) {
  const isDE = lang === "DE";

  const [auditData, setAuditData] = useState<LkSGAuditResponse | null>(null);
  const [bafaData, setBafaData] = useState<BafaQuestionnaireResponse | null>(null);
  const [capaData, setCapaData] = useState<SupplierCapaPlan | null>(null);
  const [envData, setEnvData] = useState<EnvironmentalAuditReport | null>(null);
  const [cascadeData, setCascadeData] = useState<TierNCascadeAuditReport | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [loadingBafa, setLoadingBafa] = useState<boolean>(false);
  const [loadingCapa, setLoadingCapa] = useState<boolean>(false);
  const [loadingEnv, setLoadingEnv] = useState<boolean>(false);
  const [loadingCascade, setLoadingCascade] = useState<boolean>(false);
  const [downloadingPdf, setDownloadingPdf] = useState<boolean>(false);
  const [downloadingCapaPdf, setDownloadingCapaPdf] = useState<boolean>(false);
  const [downloadingEnvPdf, setDownloadingEnvPdf] = useState<boolean>(false);
  const [downloadingCascadePdf, setDownloadingCascadePdf] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [filterSeverity, setFilterSeverity] = useState<string>("ALL");
  const [activeTab, setActiveTab] = useState<"overview" | "bafa_questionnaire" | "risks" | "capa_plan" | "environmental" | "cascade">("overview");
  const [expandedSections, setExpandedSections] = useState<Record<number, boolean>>({ 1: true, 2: true });

  const loadAudit = useCallback(async () => {
    if (!documentId) return;
    setLoading(true);
    setError(null);
    try {
      const data = await getLkSGAudit(documentId);
      setAuditData(data);
    } catch (err: any) {
      setError(err?.message || (isDE ? "Fehler beim Laden des LkSG-Audits" : "Failed to load LkSG audit"));
    } finally {
      setLoading(false);
    }
  }, [documentId, isDE]);

  const loadBafaQuestionnaire = useCallback(async () => {
    if (!documentId) return;
    setLoadingBafa(true);
    try {
      const bData = await getBafaQuestionnaire(documentId);
      setBafaData(bData);
    } catch (err: any) {
      console.error("Failed to load BAFA questionnaire:", err);
    } finally {
      setLoadingBafa(false);
    }
  }, [documentId]);

  const loadCapaPlan = useCallback(async () => {
    if (!documentId) return;
    setLoadingCapa(true);
    try {
      const cData = await getSupplierCapaPlan(documentId);
      setCapaData(cData);
    } catch (err: any) {
      console.error("Failed to load CAPA plan:", err);
    } finally {
      setLoadingCapa(false);
    }
  }, [documentId]);

  const loadEnvironmentalAudit = useCallback(async () => {
    if (!documentId) return;
    setLoadingEnv(true);
    try {
      const eData = await getEnvironmentalAudit(documentId);
      setEnvData(eData);
    } catch (err: any) {
      console.error("Failed to load environmental audit:", err);
    } finally {
      setLoadingEnv(false);
    }
  }, [documentId]);

  const loadCascadeAudit = useCallback(async () => {
    if (!documentId) return;
    setLoadingCascade(true);
    try {
      const cData = await getTierNCascadeAudit(documentId);
      setCascadeData(cData);
    } catch (err: any) {
      console.error("Failed to load Tier-N cascade audit:", err);
    } finally {
      setLoadingCascade(false);
    }
  }, [documentId]);

  useEffect(() => {
    if (isOpen && documentId) {
      loadAudit();
      loadBafaQuestionnaire();
      loadCapaPlan();
      loadEnvironmentalAudit();
      loadCascadeAudit();
    }
  }, [isOpen, documentId, loadAudit, loadBafaQuestionnaire, loadCapaPlan, loadEnvironmentalAudit, loadCascadeAudit]);

  const handleDownloadCascadePdf = async () => {
    if (!documentId || downloadingCascadePdf) return;
    setDownloadingCascadePdf(true);
    try {
      await downloadTierNCascadePdf(documentId, "Dr. Michael Weber, Leitender LkSG- & BaFin-Prüfer");
    } catch (err: any) {
      alert(err?.message || "Failed to download cascade dossier PDF");
    } finally {
      setDownloadingCascadePdf(false);
    }
  };

  const handleDownloadEnvPdf = async () => {
    if (!documentId || downloadingEnvPdf) return;
    setDownloadingEnvPdf(true);
    try {
      await downloadEnvironmentalCertificatePdf(documentId, "Dr. Michael Weber, Leitender LkSG- & BaFin-Prüfer");
    } catch (err: any) {
      alert(err?.message || "Failed to download environmental certificate PDF");
    } finally {
      setDownloadingEnvPdf(false);
    }
  };

  const handleDownloadCapaPdf = async () => {
    if (!documentId || downloadingCapaPdf) return;
    setDownloadingCapaPdf(true);
    try {
      await downloadCapaPlanPdf(documentId, "Dr. Michael Weber, Leitender LkSG- & BaFin-Prüfer");
    } catch (err: any) {
      alert(err?.message || "Failed to download CAPA plan PDF");
    } finally {
      setDownloadingCapaPdf(false);
    }
  };

  const handleDownloadPdf = async () => {
    if (!documentId || downloadingPdf) return;
    setDownloadingPdf(true);
    try {
      await downloadBafaReportPdf(documentId, "Dr. Michael Weber, Leitender LkSG- & BaFin-Prüfer");
    } catch (err: any) {
      alert(err?.message || "Failed to download BAFA report PDF");
    } finally {
      setDownloadingPdf(false);
    }
  };

  const toggleSection = (secNum: number) => {
    setExpandedSections((prev) => ({
      ...prev,
      [secNum]: !prev[secNum],
    }));
  };

  if (!isOpen) return null;

  const assessment = auditData?.assessment;
  const risks = assessment?.identified_risks || [];

  const filteredRisks = risks.filter((r) => {
    if (filterSeverity === "ALL") return true;
    return r.severity === filterSeverity;
  });

  const getRatingBadge = (rating: string) => {
    switch (rating) {
      case "AAA":
      case "AA":
        return "bg-emerald-100 text-emerald-800 border-2 border-emerald-500 dark:bg-emerald-950/80 dark:text-emerald-200 dark:border-emerald-600";
      case "A":
      case "BBB":
      case "BB":
        return "bg-amber-100 text-amber-800 border-2 border-amber-500 dark:bg-amber-950/80 dark:text-amber-200 dark:border-amber-600";
      default:
        return "bg-red-100 text-red-800 border-2 border-red-500 dark:bg-red-950/80 dark:text-red-200 dark:border-red-600";
    }
  };

  const getSeverityBadge = (severity: string) => {
    switch (severity) {
      case "CRITICAL":
        return "bg-red-100 text-red-800 border border-red-500 dark:bg-red-950/80 dark:text-red-200";
      case "HIGH":
        return "bg-amber-100 text-amber-800 border border-amber-500 dark:bg-amber-950/80 dark:text-amber-200";
      case "MEDIUM":
        return "bg-blue-100 text-blue-800 border border-blue-400 dark:bg-blue-950/80 dark:text-blue-200";
      default:
        return "bg-emerald-100 text-emerald-800 border border-emerald-500 dark:bg-emerald-950/80 dark:text-emerald-200";
    }
  };

  const getBafaStatusBadge = (status: string) => {
    switch (status) {
      case "COMPLIANT":
        return "bg-emerald-100 text-emerald-800 border border-emerald-500 dark:bg-emerald-950/80 dark:text-emerald-200";
      case "PARTIALLY_COMPLIANT":
        return "bg-amber-100 text-amber-800 border border-amber-500 dark:bg-amber-950/80 dark:text-amber-200";
      default:
        return "bg-red-100 text-red-800 border border-red-500 dark:bg-red-950/80 dark:text-red-200";
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4">
      <div className="relative w-full max-w-5xl max-h-[90vh] bg-white dark:bg-neutral-900 border border-neutral-200 dark:border-neutral-800 rounded-2xl shadow-2xl flex flex-col overflow-hidden">
        {/* Header Bar */}
        <div className="px-6 py-4 border-b border-neutral-200 dark:border-neutral-800 bg-neutral-50 dark:bg-neutral-950/60 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="p-2.5 rounded-xl bg-emerald-600/10 text-emerald-700 dark:text-emerald-400 border border-emerald-500/20">
              <Scale className="w-6 h-6" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h2 className="text-lg font-bold text-neutral-900 dark:text-neutral-100">
                  {isDE ? "LkSG-Lieferkettenprüfung & BAFA-Konformität" : "LkSG Supply Chain Due Diligence & BAFA Audit"}
                </h2>
                <span className="px-2 py-0.5 text-xs font-semibold rounded bg-neutral-200 dark:bg-neutral-800 text-neutral-700 dark:text-neutral-300">
                  §§ 2–10 LkSG
                </span>
              </div>
              <p className="text-xs text-neutral-500 dark:text-neutral-400">
                {documentName || (isDE ? "Zulieferer-Vertragsprüfung" : "Supplier Contract Assessment")}
              </p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={handleDownloadPdf}
              disabled={downloadingPdf || !documentId}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-emerald-600 hover:bg-emerald-700 text-white font-mono text-xs font-bold transition shadow-sm cursor-pointer disabled:opacity-50"
              title={isDE ? "Offiziellen BAFA-Prüfbericht herunterladen" : "Download official BAFA audit report PDF"}
            >
              {downloadingPdf ? (
                <Loader2 className="w-3.5 h-3.5 animate-spin" />
              ) : (
                <Download className="w-3.5 h-3.5" />
              )}
              <span className="hidden sm:inline">
                {isDE ? "BAFA-Prüfbericht (PDF)" : "BAFA Audit PDF"}
              </span>
            </button>
            <button
              onClick={() => {
                loadAudit();
                loadBafaQuestionnaire();
              }}
              disabled={loading || loadingBafa}
              className="p-2 text-neutral-500 hover:text-neutral-900 dark:hover:text-neutral-100 rounded-lg hover:bg-neutral-100 dark:hover:bg-neutral-800 transition"
              title={isDE ? "Neu laden" : "Reload"}
            >
              <RefreshCw className={`w-4 h-4 ${loading || loadingBafa ? "animate-spin" : ""}`} />
            </button>
            <button
              onClick={onClose}
              className="p-2 text-neutral-500 hover:text-neutral-900 dark:hover:text-neutral-100 rounded-lg hover:bg-neutral-100 dark:hover:bg-neutral-800 transition"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* Tab Navigation */}
        <div className="px-6 border-b border-neutral-200 dark:border-neutral-800 bg-neutral-100/50 dark:bg-neutral-950/30 flex items-center gap-2">
          <button
            onClick={() => setActiveTab("overview")}
            className={`py-3 px-3 border-b-2 font-mono text-xs font-bold transition flex items-center gap-1.5 cursor-pointer ${
              activeTab === "overview"
                ? "border-emerald-600 text-emerald-700 dark:text-emerald-400"
                : "border-transparent text-neutral-500 hover:text-neutral-800 dark:hover:text-neutral-200"
            }`}
          >
            <Scale className="w-3.5 h-3.5" />
            <span>{isDE ? "Übersicht & Säulen-Score" : "Overview & 3 Pillars"}</span>
          </button>
          <button
            onClick={() => setActiveTab("bafa_questionnaire")}
            className={`py-3 px-3 border-b-2 font-mono text-xs font-bold transition flex items-center gap-1.5 cursor-pointer ${
              activeTab === "bafa_questionnaire"
                ? "border-emerald-600 text-emerald-700 dark:text-emerald-400"
                : "border-transparent text-neutral-500 hover:text-neutral-800 dark:hover:text-neutral-200"
            }`}
          >
            <ClipboardCheck className="w-3.5 h-3.5" />
            <span>{isDE ? "BAFA-Fragebogen (§ 5 LkSG)" : "BAFA Questionnaire (§ 5 LkSG)"}</span>
            {bafaData && (
              <span className="px-1.5 py-0.2 rounded-full text-[10px] bg-emerald-500/15 text-emerald-700 dark:text-emerald-300 font-bold">
                12
              </span>
            )}
          </button>
          <button
            onClick={() => setActiveTab("risks")}
            className={`py-3 px-3 border-b-2 font-mono text-xs font-bold transition flex items-center gap-1.5 cursor-pointer ${
              activeTab === "risks"
                ? "border-emerald-600 text-emerald-700 dark:text-emerald-400"
                : "border-transparent text-neutral-500 hover:text-neutral-800 dark:hover:text-neutral-200"
            }`}
          >
            <AlertTriangle className="w-3.5 h-3.5 text-amber-500" />
            <span>{isDE ? "Identifizierte Risiken" : "Identified Risks"}</span>
            <span className="px-1.5 py-0.2 rounded-full text-[10px] bg-neutral-200 dark:bg-neutral-800 text-neutral-700 dark:text-neutral-300 font-bold">
              {risks.length}
            </span>
          </button>
          <button
            onClick={() => setActiveTab("capa_plan")}
            className={`py-3 px-3 border-b-2 font-mono text-xs font-bold transition flex items-center gap-1.5 cursor-pointer ${
              activeTab === "capa_plan"
                ? "border-emerald-600 text-emerald-700 dark:text-emerald-400"
                : "border-transparent text-neutral-500 hover:text-neutral-800 dark:hover:text-neutral-200"
            }`}
          >
            <CalendarCheck className="w-3.5 h-3.5 text-emerald-600 dark:text-emerald-400" />
            <span>{isDE ? "Korrektur-Aktionsplan (CAPA § 7)" : "CAPA Action Plan (§ 7)"}</span>
            {capaData && (
              <span className="px-1.5 py-0.2 rounded-full text-[10px] bg-emerald-100 text-emerald-700 dark:bg-emerald-950/80 dark:text-emerald-300 font-bold">
                {capaData.total_milestones}
              </span>
            )}
          </button>
          <button
            onClick={() => setActiveTab("environmental")}
            className={`py-3 px-3 border-b-2 font-mono text-xs font-bold transition flex items-center gap-1.5 cursor-pointer ${
              activeTab === "environmental"
                ? "border-emerald-600 text-emerald-700 dark:text-emerald-400"
                : "border-transparent text-neutral-500 hover:text-neutral-800 dark:hover:text-neutral-200"
            }`}
          >
            <Leaf className="w-3.5 h-3.5 text-emerald-600 dark:text-emerald-400" />
            <span>{isDE ? "Umwelt (§ 2 Abs. 3)" : "Environment"}</span>
            {envData && (
              <span className="px-1.5 py-0.2 rounded-full text-[10px] bg-emerald-100 text-emerald-700 dark:bg-emerald-950/80 dark:text-emerald-300 font-bold">
                {envData.environmental_rating}
              </span>
            )}
          </button>
          <button
            onClick={() => setActiveTab("cascade")}
            className={`py-3 px-3 border-b-2 font-mono text-xs font-bold transition flex items-center gap-1.5 cursor-pointer ${
              activeTab === "cascade"
                ? "border-emerald-600 text-emerald-700 dark:text-emerald-400"
                : "border-transparent text-neutral-500 hover:text-neutral-800 dark:hover:text-neutral-200"
            }`}
          >
            <Network className="w-3.5 h-3.5 text-emerald-600 dark:text-emerald-400" />
            <span>{isDE ? "Kaskade (§ 9)" : "Cascade (§ 9)"}</span>
            {cascadeData && (
              <span className={`px-1.5 py-0.2 rounded-full text-[10px] font-bold ${
                cascadeData.substantiated_knowledge_active
                  ? "bg-red-100 text-red-700 dark:bg-red-950/80 dark:text-red-300"
                  : "bg-emerald-100 text-emerald-700 dark:bg-emerald-950/80 dark:text-emerald-300"
              }`}>
                {cascadeData.overall_cascade_score.toFixed(0)}%
              </span>
            )}
          </button>
        </div>

        {/* Content Area */}
        <div className="flex-1 overflow-y-auto p-6 space-y-6">
          {(loading || loadingBafa) && !assessment && (
            <div className="flex flex-col items-center justify-center py-20 text-neutral-500 space-y-3">
              <RefreshCw className="w-8 h-8 animate-spin text-emerald-600" />
              <p className="text-sm font-medium">
                {isDE
                  ? "Analysiere Lieferantenvertrag auf LkSG- und BAFA-Sorgfaltspflichten..."
                  : "Auditing supplier contract against LkSG & BAFA statutory mandates..."}
              </p>
            </div>
          )}

          {error && (
            <div className="p-4 rounded-xl bg-red-50 dark:bg-red-950/40 border border-red-200 dark:border-red-900/60 text-red-700 dark:text-red-300 flex items-start gap-3">
              <AlertOctagon className="w-5 h-5 mt-0.5 flex-shrink-0 text-red-600" />
              <div>
                <h4 className="font-semibold text-sm">{isDE ? "Prüfungsfehler" : "Audit Error"}</h4>
                <p className="text-xs mt-1">{error}</p>
              </div>
            </div>
          )}

          {/* TAB 1: OVERVIEW */}
          {activeTab === "overview" && assessment && (
            <>
              {/* Executive Scorecard Box */}
              <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                {/* Overall Rating Card */}
                <div className="p-4 rounded-xl border border-neutral-200 dark:border-neutral-800 bg-neutral-50/50 dark:bg-neutral-950/30 flex flex-col justify-between">
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-semibold text-neutral-500 uppercase tracking-wider">
                      {isDE ? "Gesamturteil" : "Overall Rating"}
                    </span>
                    <span className="text-xs font-mono text-neutral-400">
                      {assessment.supplier_tier === "TIER_1_DIRECT" ? "Tier-1 Direkt" : "Tier-N Kaskade"}
                    </span>
                  </div>
                  <div className="my-3 flex items-baseline gap-3">
                    <div className={`px-3 py-1 rounded-xl font-black text-2xl ${getRatingBadge(assessment.compliance_rating)}`}>
                      {assessment.compliance_rating}
                    </div>
                    <div>
                      <div className="text-2xl font-bold text-neutral-900 dark:text-neutral-100">
                        {assessment.overall_compliance_score.toFixed(0)}%
                      </div>
                      <div className="text-[10px] text-neutral-400 font-mono">
                        {isDE ? "BAFA Risikoindex" : "BAFA Risk Index"}
                      </div>
                    </div>
                  </div>
                  <span className="text-xs text-neutral-500">
                    {assessment.critical_risk_count === 0
                      ? isDE ? "Keine kritischen Bußgeldrisiken" : "Zero critical statutory risks"
                      : isDE ? `${assessment.critical_risk_count} kritische Verstöße` : `${assessment.critical_risk_count} critical breaches`}
                  </span>
                </div>

                {/* Pillar 1: Human Rights */}
                <div className="p-4 rounded-xl border border-neutral-200 dark:border-neutral-800 bg-neutral-50/50 dark:bg-neutral-950/30 flex flex-col justify-between">
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-semibold text-neutral-500 uppercase tracking-wider flex items-center gap-1.5">
                      <Users className="w-3.5 h-3.5 text-blue-600" />
                      {isDE ? "Menschenrechte" : "Human Rights"}
                    </span>
                    <span className="text-xs font-bold text-neutral-700 dark:text-neutral-300">
                      § 2 Abs. 2
                    </span>
                  </div>
                  <div className="my-3">
                    <div className="text-2xl font-bold text-neutral-900 dark:text-neutral-100">
                      {assessment.human_rights_score.toFixed(0)} / 100
                    </div>
                    <div className="w-full bg-neutral-200 dark:bg-neutral-800 h-1.5 rounded-full overflow-hidden mt-2">
                      <div
                        className="bg-blue-600 h-full rounded-full transition-all"
                        style={{ width: `${Math.min(100, assessment.human_rights_score)}%` }}
                      />
                    </div>
                  </div>
                  <span className="text-xs text-neutral-500">
                    {isDE ? "Kinderarbeit, Zwangsarbeit & Lohn" : "Child/Forced Labor & Wages"}
                  </span>
                </div>

                {/* Pillar 2: Environment */}
                <div className="p-4 rounded-xl border border-neutral-200 dark:border-neutral-800 bg-neutral-50/50 dark:bg-neutral-950/30 flex flex-col justify-between">
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-semibold text-neutral-500 uppercase tracking-wider flex items-center gap-1.5">
                      <Leaf className="w-3.5 h-3.5 text-emerald-600" />
                      {isDE ? "Umweltschutz" : "Environment"}
                    </span>
                    <span className="text-xs font-bold text-neutral-700 dark:text-neutral-300">
                      § 2 Abs. 3
                    </span>
                  </div>
                  <div className="my-3">
                    <div className="text-2xl font-bold text-neutral-900 dark:text-neutral-100">
                      {assessment.environmental_score.toFixed(0)} / 100
                    </div>
                    <div className="w-full bg-neutral-200 dark:bg-neutral-800 h-1.5 rounded-full overflow-hidden mt-2">
                      <div
                        className="bg-emerald-600 h-full rounded-full transition-all"
                        style={{ width: `${Math.min(100, assessment.environmental_score)}%` }}
                      />
                    </div>
                  </div>
                  <span className="text-xs text-neutral-500">
                    {isDE ? "Minamata, POPs & Basler Konv." : "Minamata, POPs & Basel Conv."}
                  </span>
                </div>

                {/* Pillar 3: Governance & BAFA */}
                <div className="p-4 rounded-xl border border-neutral-200 dark:border-neutral-800 bg-neutral-50/50 dark:bg-neutral-950/30 flex flex-col justify-between">
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-semibold text-neutral-500 uppercase tracking-wider flex items-center gap-1.5">
                      <Building2 className="w-3.5 h-3.5 text-purple-600" />
                      {isDE ? "Governance & BAFA" : "Governance / BAFA"}
                    </span>
                    <span className="text-xs font-bold text-neutral-700 dark:text-neutral-300">
                      §§ 8–10
                    </span>
                  </div>
                  <div className="my-3">
                    <div className="text-2xl font-bold text-neutral-900 dark:text-neutral-100">
                      {assessment.governance_score.toFixed(0)} / 100
                    </div>
                    <div className="w-full bg-neutral-200 dark:bg-neutral-800 h-1.5 rounded-full overflow-hidden mt-2">
                      <div
                        className="bg-purple-600 h-full rounded-full transition-all"
                        style={{ width: `${Math.min(100, assessment.governance_score)}%` }}
                      />
                    </div>
                  </div>
                  <span className="text-xs text-neutral-500">
                    {isDE ? "Whistleblower & BAFA-Bericht" : "Whistleblower & BAFA Filing"}
                  </span>
                </div>
              </div>

              {/* Statutory Checks Badges */}
              <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                <div className="flex items-center gap-2 p-2.5 rounded-lg border border-neutral-200 dark:border-neutral-800 bg-white dark:bg-neutral-900 text-xs">
                  {assessment.complaints_procedure_present ? (
                    <CheckCircle2 className="w-4 h-4 text-emerald-600 flex-shrink-0" />
                  ) : (
                    <AlertTriangle className="w-4 h-4 text-amber-500 flex-shrink-0" />
                  )}
                  <div>
                    <span className="font-semibold">{isDE ? "Beschwerdekanal (§ 8)" : "Complaints (§ 8)"}</span>
                    <p className="text-[10px] text-neutral-500">
                      {assessment.complaints_procedure_present
                        ? isDE ? "Gegenstand geregelt" : "Active & Verified"
                        : isDE ? "Nicht verankert" : "Missing / Non-Compliant"}
                    </p>
                  </div>
                </div>

                <div className="flex items-center gap-2 p-2.5 rounded-lg border border-neutral-200 dark:border-neutral-800 bg-white dark:bg-neutral-900 text-xs">
                  {assessment.bafa_report_compliant ? (
                    <CheckCircle2 className="w-4 h-4 text-emerald-600 flex-shrink-0" />
                  ) : (
                    <AlertTriangle className="w-4 h-4 text-amber-500 flex-shrink-0" />
                  )}
                  <div>
                    <span className="font-semibold">{isDE ? "BAFA-Bericht (§ 10)" : "BAFA Filing (§ 10)"}</span>
                    <p className="text-[10px] text-neutral-500">
                      {assessment.bafa_report_compliant
                        ? isDE ? "Jährlich bis 31.03." : "Annual March 31"
                        : isDE ? "Keine Zusage" : "No Commitment"}
                    </p>
                  </div>
                </div>

                <div className="flex items-center gap-2 p-2.5 rounded-lg border border-neutral-200 dark:border-neutral-800 bg-white dark:bg-neutral-900 text-xs">
                  {assessment.code_of_conduct_mandated ? (
                    <CheckCircle2 className="w-4 h-4 text-emerald-600 flex-shrink-0" />
                  ) : (
                    <AlertTriangle className="w-4 h-4 text-neutral-400 flex-shrink-0" />
                  )}
                  <div>
                    <span className="font-semibold">{isDE ? "Verhaltenskodex (§ 6)" : "Code of Conduct (§ 6)"}</span>
                    <p className="text-[10px] text-neutral-500">
                      {assessment.code_of_conduct_mandated
                        ? isDE ? "Vertraglich bindend" : "Contractually Binding"
                        : isDE ? "Nicht referenziert" : "Not Referenced"}
                    </p>
                  </div>
                </div>

                <div className="flex items-center gap-2 p-2.5 rounded-lg border border-neutral-200 dark:border-neutral-800 bg-white dark:bg-neutral-900 text-xs">
                  {assessment.audit_rights_granted ? (
                    <CheckCircle2 className="w-4 h-4 text-emerald-600 flex-shrink-0" />
                  ) : (
                    <AlertTriangle className="w-4 h-4 text-neutral-400 flex-shrink-0" />
                  )}
                  <div>
                    <span className="font-semibold">{isDE ? "Vor-Ort-Audits" : "On-Site Audits"}</span>
                    <p className="text-[10px] text-neutral-500">
                      {assessment.audit_rights_granted
                        ? isDE ? "Prüfrecht gesichert" : "Inspection Rights OK"
                        : isDE ? "Eingeschränkt" : "Restricted"}
                    </p>
                  </div>
                </div>
              </div>

              {/* Executive Summary Narrative */}
              <div className="p-4 rounded-xl border border-neutral-200 dark:border-neutral-800 bg-neutral-50 dark:bg-neutral-950/40">
                <h4 className="text-xs font-bold text-neutral-700 dark:text-neutral-300 uppercase tracking-wider mb-2 flex items-center gap-2">
                  <Sparkles className="w-4 h-4 text-emerald-600" />
                  {isDE ? "Revisionsvermerk der Prüfinstanz" : "Auditor Executive Verdict"}
                </h4>
                <p className="text-xs text-neutral-600 dark:text-neutral-400 leading-relaxed font-sans">
                  {isDE ? assessment.executive_summary_de : assessment.executive_summary_en}
                </p>
              </div>
            </>
          )}

          {/* TAB 2: BAFA QUESTIONNAIRE */}
          {activeTab === "bafa_questionnaire" && (
            <div className="space-y-4">
              {/* Questionnaire Header Card */}
              <div className="p-4 rounded-xl border border-neutral-200 dark:border-neutral-800 bg-gradient-to-r from-emerald-500/10 via-emerald-500/5 to-transparent flex flex-wrap items-center justify-between gap-4">
                <div>
                  <div className="flex items-center gap-2">
                    <ClipboardCheck className="w-5 h-5 text-emerald-600" />
                    <h3 className="text-sm font-bold text-neutral-900 dark:text-neutral-100">
                      {isDE ? "Offizieller BAFA-Fragenkatalog nach § 5 LkSG" : "Official BAFA Due Diligence Audit Questionnaire (§ 5 LkSG)"}
                    </h3>
                  </div>
                  <p className="text-xs text-neutral-500 dark:text-neutral-400 mt-1 max-w-2xl">
                    {isDE
                      ? "Handreichung zur Durchführung einer Risikoanalyse nach dem Lieferkettensorgfaltspflichtengesetz. Bewertet alle 12 Kernfragen zu Menschenrechten, ILO-Normen, Umweltübereinkommen und Beschwerdemechanismen."
                      : "Administrative guidance for supply chain risk analysis by the Federal Office for Economic Affairs and Export Control (BAFA). Covers all 12 core sections."}
                  </p>
                </div>

                {bafaData && (
                  <div className="flex items-center gap-3">
                    <div className="text-right">
                      <div className="text-xs font-mono text-neutral-500">
                        {isDE ? "Vorgaben erfüllt" : "Criteria met"}
                      </div>
                      <div className="text-sm font-bold text-emerald-600">
                        {bafaData.compliant_count} / {bafaData.total_questions}
                      </div>
                    </div>
                    <div className={`px-3 py-1.5 rounded-xl font-mono font-black text-lg ${getRatingBadge(bafaData.compliance_rating)}`}>
                      {bafaData.compliance_rating} • {bafaData.overall_score}%
                    </div>
                  </div>
                )}
              </div>

              {/* 12 Sections Accordion List */}
              {bafaData && bafaData.sections.map((section) => {
                const isExpanded = !!expandedSections[section.section_number];
                const item = section.items[0];

                return (
                  <div
                    key={section.section_number}
                    className="border border-neutral-200 dark:border-neutral-800 rounded-xl overflow-hidden bg-white dark:bg-neutral-900 transition shadow-sm"
                  >
                    {/* Section Header Button */}
                    <button
                      onClick={() => toggleSection(section.section_number)}
                      className="w-full px-4 py-3.5 flex items-center justify-between text-left hover:bg-neutral-50 dark:hover:bg-neutral-950/50 transition cursor-pointer"
                    >
                      <div className="flex items-center gap-3 min-w-0">
                        <span className="w-6 h-6 rounded-lg bg-neutral-100 dark:bg-neutral-800 text-neutral-700 dark:text-neutral-300 font-mono text-xs font-bold flex items-center justify-center shrink-0">
                          {section.section_number}
                        </span>
                        <div className="min-w-0">
                          <h4 className="text-xs sm:text-sm font-bold text-neutral-900 dark:text-neutral-100 truncate">
                            {isDE ? section.title_de : section.title_en}
                          </h4>
                          <span className="text-[11px] font-mono text-neutral-400">
                            {section.statutory_article}
                          </span>
                        </div>
                      </div>

                      <div className="flex items-center gap-2.5 shrink-0">
                        <span className={`px-2 py-0.5 text-[10px] font-mono font-bold rounded ${getBafaStatusBadge(section.compliance_status)}`}>
                          {section.compliance_status === "COMPLIANT"
                            ? isDE ? "VOLLSTÄNDIG" : "COMPLIANT"
                            : section.compliance_status === "PARTIALLY_COMPLIANT"
                            ? isDE ? "TEILWEISE" : "PARTIAL"
                            : isDE ? "NICHT KONFORM" : "NON-COMPLIANT"}
                        </span>
                        <ChevronDown className={`w-4 h-4 text-neutral-400 transition-transform ${isExpanded ? "rotate-180" : ""}`} />
                      </div>
                    </button>

                    {/* Section Content Details */}
                    {isExpanded && item && (
                      <div className="p-4 border-t border-neutral-100 dark:border-neutral-800 bg-neutral-50/50 dark:bg-neutral-950/40 space-y-3 text-xs">
                        {/* BAFA Official Question */}
                        <div>
                          <span className="text-[10px] font-mono font-bold uppercase text-neutral-400 tracking-wider">
                            {isDE ? "Offizielle BAFA-Prüffrage" : "Official BAFA Statutory Question"}
                          </span>
                          <p className="font-semibold text-neutral-900 dark:text-neutral-100 mt-0.5">
                            {isDE ? item.question_de : item.question_en}
                          </p>
                        </div>

                        {/* Automated Assessment / Finding */}
                        <div>
                          <span className="text-[10px] font-mono font-bold uppercase text-neutral-400 tracking-wider">
                            {isDE ? "Prüfungsbefund (DocuNorm AI)" : "Automated Finding (DocuNorm AI)"}
                          </span>
                          <p className="text-neutral-700 dark:text-neutral-300 mt-0.5 leading-relaxed">
                            {isDE ? item.answer_de : item.answer_en}
                          </p>
                        </div>

                        {/* Contract Evidence Snippet */}
                        {item.evidence_quote && (
                          <div className="p-2.5 rounded-lg bg-neutral-100 dark:bg-neutral-900 border border-neutral-200 dark:border-neutral-800 font-mono text-[11px] text-neutral-600 dark:text-neutral-400">
                            <div className="flex items-center justify-between text-[10px] text-neutral-400 mb-1">
                              <span>{isDE ? "Vertragszitat (Evidence)" : "Contract Evidence Quote"}</span>
                              {item.page_number && onJumpToCitation && (
                                <button
                                  onClick={() => onJumpToCitation(item.page_number!)}
                                  className="text-emerald-600 hover:underline flex items-center gap-1 font-semibold cursor-pointer"
                                >
                                  <span>{isDE ? `Seite ${item.page_number}` : `Page ${item.page_number}`}</span>
                                  <ExternalLink className="w-3 h-3" />
                                </button>
                              )}
                            </div>
                            &ldquo;{item.evidence_quote}&rdquo;
                          </div>
                        )}

                        {/* BAFA Recommendation / Remediation */}
                        <div className="p-2.5 rounded-lg bg-emerald-500/10 border border-emerald-500/20 text-emerald-800 dark:text-emerald-300">
                          <span className="font-bold text-[10.5px] uppercase tracking-wide block mb-0.5">
                            {isDE ? "Empfohlene BAFA-Präventionsmaßnahme (§ 6 LkSG):" : "Statutory BAFA Prevention Measure (§ 6 LkSG):"}
                          </span>
                          <p className="text-[11px] leading-relaxed">
                            {isDE ? item.bafa_recommendation_de : item.bafa_recommendation_en}
                          </p>
                        </div>
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          )}

          {/* TAB 3: IDENTIFIED RISKS */}
          {activeTab === "risks" && (
            <div>
              <div className="flex items-center justify-between mb-3">
                <h3 className="text-sm font-bold text-neutral-900 dark:text-neutral-100 flex items-center gap-2">
                  <AlertTriangle className="w-4 h-4 text-amber-500" />
                  {isDE ? "Identifizierte LkSG-Risiken & Handlungsbedarfe" : "Identified LkSG Risks & Required Actions"}
                  <span className="ml-1 px-2 py-0.5 text-xs rounded-full bg-neutral-200 dark:bg-neutral-800 text-neutral-700 dark:text-neutral-300 font-bold">
                    {filteredRisks.length}
                  </span>
                </h3>

                {/* Filter Pills */}
                <div className="flex items-center gap-1.5 text-xs">
                  {["ALL", "CRITICAL", "HIGH", "MEDIUM"].map((lvl) => (
                    <button
                      key={lvl}
                      onClick={() => setFilterSeverity(lvl)}
                      className={`px-2.5 py-1 rounded-lg font-medium transition cursor-pointer ${
                        filterSeverity === lvl
                          ? "bg-neutral-900 text-white dark:bg-neutral-100 dark:text-neutral-900 shadow-sm"
                          : "bg-neutral-100 dark:bg-neutral-800 text-neutral-600 dark:text-neutral-400 hover:bg-neutral-200 dark:hover:bg-neutral-700"
                      }`}
                    >
                      {lvl}
                    </button>
                  ))}
                </div>
              </div>

              {filteredRisks.length === 0 ? (
                <div className="p-8 text-center border border-dashed border-neutral-300 dark:border-neutral-700 rounded-xl">
                  <CheckCircle2 className="w-8 h-8 text-emerald-600 mx-auto mb-2" />
                  <p className="text-sm font-semibold text-neutral-800 dark:text-neutral-200">
                    {isDE ? "Keine Risiken in dieser Filterkategorie" : "No risks in this filter category"}
                  </p>
                  <p className="text-xs text-neutral-500 mt-1">
                    {isDE
                      ? "Alle gesetzlichen Vorgaben dieser Kategorie sind vertraglich abgesichert."
                      : "All statutory requirements in this category are contractually secured."}
                  </p>
                </div>
              ) : (
                <div className="space-y-3">
                  {filteredRisks.map((item, idx) => (
                    <div
                      key={idx}
                      className="p-4 rounded-xl border border-neutral-200 dark:border-neutral-800 bg-white dark:bg-neutral-900 hover:border-neutral-300 dark:hover:border-neutral-700 transition space-y-3"
                    >
                      <div className="flex items-start justify-between gap-3">
                        <div className="flex items-center gap-2">
                          <span className={`px-2 py-0.5 text-xs font-black rounded ${getSeverityBadge(item.severity)}`}>
                            {item.severity}
                          </span>
                          <h4 className="text-sm font-bold text-neutral-900 dark:text-neutral-100">
                            {isDE ? item.title_de : item.title_en}
                          </h4>
                        </div>
                        {onJumpToCitation && (
                          <button
                            onClick={() => onJumpToCitation(item.page_number)}
                            className="inline-flex items-center gap-1 text-xs text-emerald-700 dark:text-emerald-400 hover:underline font-semibold cursor-pointer"
                          >
                            <span>{isDE ? `Seite ${item.page_number}` : `Page ${item.page_number}`}</span>
                            <ExternalLink className="w-3 h-3" />
                          </button>
                        )}
                      </div>

                      <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-xs">
                        <div>
                          <span className="text-[10px] font-mono text-neutral-400 uppercase tracking-wide">
                            {isDE ? "Gesetzliche Referenz" : "Statutory Article"}
                          </span>
                          <p className="font-mono text-neutral-700 dark:text-neutral-300">{item.statutory_reference}</p>
                        </div>
                        <div>
                          <span className="text-[10px] font-mono text-neutral-400 uppercase tracking-wide">
                            {isDE ? "BAFA-Verwaltungsvorschrift" : "BAFA Guidance Ref"}
                          </span>
                          <p className="font-mono text-neutral-700 dark:text-neutral-300">{item.bafa_guideline_ref}</p>
                        </div>
                      </div>

                      <div className="text-xs text-neutral-600 dark:text-neutral-400">
                        <p>{isDE ? item.finding_de : item.finding_en}</p>
                      </div>

                      {item.evidence_snippet && (
                        <div className="p-2.5 rounded-lg bg-neutral-100 dark:bg-neutral-950 border border-neutral-200 dark:border-neutral-800 text-xs font-mono text-neutral-600 dark:text-neutral-400">
                          &ldquo;{item.evidence_snippet}&rdquo;
                        </div>
                      )}

                      <div className="p-2.5 rounded-lg bg-emerald-50 dark:bg-emerald-950/30 border border-emerald-200 dark:border-emerald-800/40 text-xs text-emerald-900 dark:text-emerald-200">
                        <span className="font-semibold">{isDE ? "Verbindliche BAFA-Abhilfe:" : "BAFA Remediation:"} </span>
                        {isDE ? item.remediation_action_de : item.remediation_action_en}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}

          {/* TAB 4: CAPA REMEDIATION ACTION PLAN (§ 7 LkSG) */}
          {activeTab === "capa_plan" && (
            <div className="space-y-4">
              {/* CAPA Header Banner */}
              <div className="p-4 rounded-xl border border-neutral-200 dark:border-neutral-800 bg-gradient-to-r from-emerald-500/10 via-emerald-500/5 to-transparent flex flex-wrap items-center justify-between gap-4">
                <div>
                  <div className="flex items-center gap-2">
                    <CalendarCheck className="w-5 h-5 text-emerald-600" />
                    <h3 className="text-sm font-bold text-neutral-900 dark:text-neutral-100">
                      {isDE
                        ? "Gesetzlicher Korrekturmaßnahmenplan (CAPA) nach § 7 LkSG"
                        : "Statutory Corrective Action Plan (CAPA) under § 7 LkSG"}
                    </h3>
                  </div>
                  <p className="text-xs text-neutral-500 dark:text-neutral-400 mt-1 max-w-2xl">
                    {isDE
                      ? "Verbindlicher Abhilfeplan für festgestellte menschenrechtliche oder umweltbezogene Verletzungen mit Fristen, Nachweisprüfungen und Pönalen vor einer Beendigung der Geschäftsbeziehung."
                      : "Binding remediation roadmap for human rights or environmental violations with deadlines, verification audits, and contractual penalties."}
                  </p>
                </div>

                {capaData && (
                  <div className="flex items-center gap-2">
                    <button
                      onClick={handleDownloadCapaPdf}
                      disabled={downloadingCapaPdf}
                      className="px-3 py-1.5 rounded-lg text-xs font-mono font-bold bg-neutral-900 text-white dark:bg-neutral-100 dark:text-neutral-900 hover:opacity-90 transition flex items-center gap-1.5 cursor-pointer shadow-sm disabled:opacity-50"
                    >
                      <Download className="w-3.5 h-3.5" />
                      <span>{downloadingCapaPdf ? (isDE ? "Exportiere..." : "Exporting...") : isDE ? "CAPA-Aktionsplan (PDF)" : "CAPA Action Plan (PDF)"}</span>
                    </button>
                  </div>
                )}
              </div>

              {/* CAPA Posture & Stats Strip */}
              {capaData && (
                <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                  <div className="p-3 rounded-xl bg-white dark:bg-neutral-900 border border-neutral-200 dark:border-neutral-800 text-center">
                    <span className="text-[10px] font-mono text-neutral-400 uppercase">Status Abhilfeplan</span>
                    <div className="text-xs font-bold font-mono mt-1 text-emerald-600 truncate">
                      {capaData.overall_compliance_posture}
                    </div>
                  </div>
                  <div className="p-3 rounded-xl bg-white dark:bg-neutral-900 border border-neutral-200 dark:border-neutral-800 text-center">
                    <span className="text-[10px] font-mono text-neutral-400 uppercase">Kritische Meilensteine</span>
                    <div className="text-xl font-bold font-mono text-red-600 mt-0.5">
                      {capaData.critical_milestones_count} / {capaData.total_milestones}
                    </div>
                  </div>
                  <div className="p-3 rounded-xl bg-white dark:bg-neutral-900 border border-neutral-200 dark:border-neutral-800 text-center">
                    <span className="text-[10px] font-mono text-neutral-400 uppercase">Maximale Umsetzungsfrist</span>
                    <div className="text-xl font-bold font-mono text-neutral-800 dark:text-neutral-200 mt-0.5">
                      {capaData.max_remediation_timeline_days} Tage
                    </div>
                  </div>
                  <div className="p-3 rounded-xl bg-white dark:bg-neutral-900 border border-neutral-200 dark:border-neutral-800 text-center">
                    <span className="text-[10px] font-mono text-neutral-400 uppercase">Geschätztes Budget</span>
                    <div className="text-sm font-bold font-mono text-neutral-800 dark:text-neutral-200 mt-1">
                      EUR {capaData.estimated_remediation_cost_eur.toLocaleString("de-DE")}
                    </div>
                  </div>
                </div>
              )}

              {/* Milestones Timeline Cards */}
              {capaData && capaData.milestones.map((m, idx) => (
                <div
                  key={m.id}
                  className="p-4 rounded-xl border border-neutral-200 dark:border-neutral-800 bg-white dark:bg-neutral-900 shadow-sm space-y-3"
                >
                  <div className="flex flex-wrap items-center justify-between gap-2">
                    <div className="flex items-center gap-2.5">
                      <span className="w-6 h-6 rounded-lg bg-emerald-100 dark:bg-emerald-950/80 text-emerald-700 dark:text-emerald-300 font-mono text-xs font-bold flex items-center justify-center shrink-0">
                        {idx + 1}
                      </span>
                      <div>
                        <h4 className="text-xs sm:text-sm font-bold text-neutral-900 dark:text-neutral-100">
                          {isDE ? m.title_de : m.title_en}
                        </h4>
                        <span className="text-[11px] font-mono text-neutral-400">
                          {m.statutory_basis} • {m.category}
                        </span>
                      </div>
                    </div>

                    <div className="flex items-center gap-2">
                      <span className="px-2 py-0.5 text-[10px] font-mono font-bold rounded bg-neutral-100 dark:bg-neutral-800 text-neutral-700 dark:text-neutral-300 flex items-center gap-1">
                        <Clock className="w-3 h-3 text-neutral-400" />
                        <span>Frist: {m.deadline_days} Tage</span>
                      </span>
                      <span
                        className={`px-2 py-0.5 text-[10px] font-mono font-bold rounded ${
                          m.severity === "CRITICAL"
                            ? "bg-red-500/10 text-red-600 dark:text-red-400 border border-red-500/20"
                            : "bg-amber-500/10 text-amber-600 dark:text-amber-400 border border-amber-500/20"
                        }`}
                      >
                        {m.severity}
                      </span>
                    </div>
                  </div>

                  <div className="p-2.5 rounded-lg bg-red-50/50 dark:bg-red-950/20 border border-red-200/50 dark:border-red-900/30 text-xs">
                    <span className="text-[10px] font-mono uppercase font-bold text-red-600 dark:text-red-400">
                      Identifiziertes Defizit:
                    </span>
                    <p className="mt-0.5 text-neutral-800 dark:text-neutral-200">{m.deficiency_description}</p>
                  </div>

                  <div className="p-2.5 rounded-lg bg-emerald-50/60 dark:bg-emerald-950/20 border border-emerald-200/60 dark:border-emerald-900/40 text-xs">
                    <span className="text-[10px] font-mono uppercase font-bold text-emerald-700 dark:text-emerald-400">
                      Verbindlich geforderte Maßnahme (§ 7 LkSG):
                    </span>
                    <p className="mt-0.5 text-neutral-900 dark:text-neutral-100 font-medium">
                      {isDE ? m.required_action_de : m.required_action_en}
                    </p>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-2 text-xs">
                    <div className="p-2 rounded bg-neutral-100 dark:bg-neutral-950 font-mono text-[11px] text-neutral-600 dark:text-neutral-400">
                      <span className="font-bold text-neutral-700 dark:text-neutral-300">Prüfmethode: </span>
                      {m.verification_method}
                    </div>
                    <div className="p-2 rounded bg-neutral-100 dark:bg-neutral-950 font-mono text-[11px] text-neutral-600 dark:text-neutral-400 flex items-center justify-between">
                      <span className="font-bold text-neutral-700 dark:text-neutral-300">Pönale bei Verzug: </span>
                      <span className="text-red-600 font-bold">EUR {m.penalty_upon_default_eur.toLocaleString("de-DE")}</span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}

          {/* TAB 5: ENVIRONMENTAL CONVENTIONS & HAZARDOUS WASTE (§ 2 ABS. 3 LkSG) */}
          {activeTab === "environmental" && (
            <div className="space-y-4">
              {/* Environmental Header Banner */}
              <div className="p-4 rounded-xl border border-neutral-200 dark:border-neutral-800 bg-gradient-to-r from-emerald-500/10 via-emerald-500/5 to-transparent flex flex-wrap items-center justify-between gap-4">
                <div>
                  <div className="flex items-center gap-2">
                    <Leaf className="w-5 h-5 text-emerald-600" />
                    <h3 className="text-sm font-bold text-neutral-900 dark:text-neutral-100">
                      {isDE
                        ? "Umweltübereinkommen & Gefahrgutüberwachung nach § 2 Abs. 3 LkSG"
                        : "Environmental Conventions & Hazardous Substances (§ 2 Abs. 3 LkSG)"}
                    </h3>
                  </div>
                  <p className="text-xs text-neutral-500 dark:text-neutral-400 mt-1 max-w-2xl">
                    {isDE
                      ? "Verbindliche Prüfung der drei internationalen Umweltübereinkommen: Minamata (Quecksilber), Stockholm (Persistente organische Schadstoffe / POPs) und Basel (Grenzüberschreitende Sonderabfallverbringung)."
                      : "Statutory compliance audit against the Minamata (Mercury), Stockholm (POPs), and Basel (Hazardous Waste PIC) conventions."}
                  </p>
                </div>

                {envData && (
                  <div className="flex items-center gap-2">
                    <button
                      onClick={handleDownloadEnvPdf}
                      disabled={downloadingEnvPdf}
                      className="px-3 py-1.5 rounded-lg text-xs font-mono font-bold bg-neutral-900 text-white dark:bg-neutral-100 dark:text-neutral-900 hover:opacity-90 transition flex items-center gap-1.5 cursor-pointer shadow-sm disabled:opacity-50"
                    >
                      <Download className="w-3.5 h-3.5" />
                      <span>{downloadingEnvPdf ? (isDE ? "Exportiere..." : "Exporting...") : isDE ? "Umweltzertifikat (PDF)" : "Environmental Cert (PDF)"}</span>
                    </button>
                  </div>
                )}
              </div>

              {/* Convention Gauges */}
              {envData && (
                <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                  <div className="p-3.5 rounded-xl bg-white dark:bg-neutral-900 border border-neutral-200 dark:border-neutral-800">
                    <span className="text-[10px] font-mono text-neutral-400 uppercase">1. Minamata (Quecksilber)</span>
                    <div className="text-sm font-bold mt-1 text-neutral-900 dark:text-neutral-100 flex items-center justify-between">
                      <span>Quecksilberfreie Fertigung</span>
                      <span
                        className={`px-2 py-0.5 rounded text-[10px] font-mono font-bold ${
                          envData.minamata_mercury_status === "COMPLIANT"
                            ? "bg-emerald-100 text-emerald-700 dark:bg-emerald-950/80 dark:text-emerald-300"
                            : "bg-red-100 text-red-700 dark:bg-red-950/80 dark:text-red-300"
                        }`}
                      >
                        {envData.minamata_mercury_status}
                      </span>
                    </div>
                    <p className="text-[11px] text-neutral-500 mt-1">§ 2 Abs. 3 Nr. 1 LkSG · Verbot in Schaltern, Lampen & Chlor-Alkali</p>
                  </div>

                  <div className="p-3.5 rounded-xl bg-white dark:bg-neutral-900 border border-neutral-200 dark:border-neutral-800">
                    <span className="text-[10px] font-mono text-neutral-400 uppercase">2. Stockholm (POPs)</span>
                    <div className="text-sm font-bold mt-1 text-neutral-900 dark:text-neutral-100 flex items-center justify-between">
                      <span>PCB & PFAS Überwachung</span>
                      <span
                        className={`px-2 py-0.5 rounded text-[10px] font-mono font-bold ${
                          envData.stockholm_pops_status === "COMPLIANT"
                            ? "bg-emerald-100 text-emerald-700 dark:bg-emerald-950/80 dark:text-emerald-300"
                            : "bg-amber-100 text-amber-700 dark:bg-amber-950/80 dark:text-amber-300"
                        }`}
                      >
                        {envData.stockholm_pops_status}
                      </span>
                    </div>
                    <p className="text-[11px] text-neutral-500 mt-1">§ 2 Abs. 3 Nr. 2 LkSG · Verbot persistenter Schadstoffe (Annex A/B)</p>
                  </div>

                  <div className="p-3.5 rounded-xl bg-white dark:bg-neutral-900 border border-neutral-200 dark:border-neutral-800">
                    <span className="text-[10px] font-mono text-neutral-400 uppercase">3. Basler Übereinkommen</span>
                    <div className="text-sm font-bold mt-1 text-neutral-900 dark:text-neutral-100 flex items-center justify-between">
                      <span>PIC-Exportzustimmung</span>
                      <span
                        className={`px-2 py-0.5 rounded text-[10px] font-mono font-bold ${
                          envData.basel_waste_status === "VERIFIED_APPROVED"
                            ? "bg-emerald-100 text-emerald-700 dark:bg-emerald-950/80 dark:text-emerald-300"
                            : "bg-red-100 text-red-700 dark:bg-red-950/80 dark:text-red-300"
                        }`}
                      >
                        {envData.basel_waste_status}
                      </span>
                    </div>
                    <p className="text-[11px] text-neutral-500 mt-1">§ 2 Abs. 3 Nr. 3 LkSG · Notifizierungspflicht für Sonderabfall-Exporte</p>
                  </div>
                </div>
              )}

              {/* Chemical Substance Inventory List */}
              {envData && (
                <div className="space-y-3">
                  <h4 className="text-xs font-bold text-neutral-900 dark:text-neutral-100 font-mono uppercase tracking-wide">
                    {isDE ? "Chemische Stoffe & Konventions-Inventar:" : "Chemical Substances Inventory:"}
                  </h4>
                  {envData.substances.map((s) => (
                    <div
                      key={s.id}
                      className="p-3.5 rounded-xl border border-neutral-200 dark:border-neutral-800 bg-white dark:bg-neutral-900 shadow-sm space-y-2 text-xs"
                    >
                      <div className="flex flex-wrap items-center justify-between gap-2">
                        <div className="flex items-center gap-2">
                          <span className="font-bold text-neutral-900 dark:text-neutral-100 text-xs sm:text-sm">
                            {s.substance_name}
                          </span>
                          <span className="font-mono text-[10px] px-1.5 py-0.5 rounded bg-neutral-100 dark:bg-neutral-800 text-neutral-600 dark:text-neutral-300">
                            CAS: {s.cas_number}
                          </span>
                        </div>
                        <span
                          className={`px-2 py-0.5 text-[10px] font-mono font-bold rounded ${
                            s.status === "COMPLIANT"
                              ? "bg-emerald-100 text-emerald-700 dark:bg-emerald-950/80 dark:text-emerald-300"
                              : s.status === "PROHIBITED"
                              ? "bg-red-100 text-red-700 dark:bg-red-950/80 dark:text-red-300"
                              : "bg-amber-100 text-amber-700 dark:bg-amber-950/80 dark:text-amber-300"
                          }`}
                        >
                          {s.status}
                        </span>
                      </div>

                      <div className="text-[11px] font-mono text-neutral-500 flex flex-wrap gap-x-4 gap-y-1">
                        <span>Grenzwert: <strong className="text-neutral-700 dark:text-neutral-300">{s.threshold_limit}</strong></span>
                        <span>Norm: <strong className="text-neutral-700 dark:text-neutral-300">{s.statutory_article}</strong></span>
                      </div>

                      <div className="p-2 rounded bg-neutral-50 dark:bg-neutral-950 border border-neutral-200/60 dark:border-neutral-800 text-[11px] font-mono text-neutral-600 dark:text-neutral-400">
                        {s.remediation_guidance}
                      </div>
                    </div>
                  ))}
                </div>
              )}

              {/* Basel Transboundary Waste Manifests */}
              {envData && (
                <div className="space-y-3 pt-2">
                  <h4 className="text-xs font-bold text-neutral-900 dark:text-neutral-100 font-mono uppercase tracking-wide">
                    {isDE ? "Basler Sonderabfall-Begleitscheine (Transboundary Waste):" : "Basel Waste Shipment Manifests:"}
                  </h4>
                  {envData.waste_manifests.map((w) => (
                    <div
                      key={w.manifest_id}
                      className="p-3.5 rounded-xl border border-neutral-200 dark:border-neutral-800 bg-white dark:bg-neutral-900 shadow-sm space-y-2 text-xs"
                    >
                      <div className="flex flex-wrap items-center justify-between gap-2">
                        <div className="flex items-center gap-2">
                          <span className="font-mono font-bold text-xs text-neutral-900 dark:text-neutral-100">
                            {w.manifest_id}
                          </span>
                          <span className="font-mono text-[10px] px-1.5 py-0.5 rounded bg-neutral-100 dark:bg-neutral-800 text-neutral-600 dark:text-neutral-300">
                            {w.waste_code}
                          </span>
                        </div>
                        <span
                          className={`px-2 py-0.5 text-[10px] font-mono font-bold rounded ${
                            w.pic_status === "VERIFIED_APPROVED"
                              ? "bg-emerald-100 text-emerald-700 dark:bg-emerald-950/80 dark:text-emerald-300"
                              : "bg-red-100 text-red-700 dark:bg-red-950/80 dark:text-red-300"
                          }`}
                        >
                          {w.pic_status}
                        </span>
                      </div>

                      <p className="text-neutral-700 dark:text-neutral-300 font-medium text-xs">{w.waste_description}</p>

                      <div className="grid grid-cols-1 md:grid-cols-2 gap-2 text-[11px] font-mono text-neutral-500 pt-1">
                        <div>
                          <span>Route: </span>
                          <strong className="text-neutral-800 dark:text-neutral-200">{w.origin_country} ➔ {w.destination_country}</strong>
                        </div>
                        <div>
                          <span>Anlage: </span>
                          <strong className="text-neutral-800 dark:text-neutral-200">{w.disposal_or_recycling_facility}</strong>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}

          {/* TAB 6: MULTI-TIER SUPPLY CHAIN CASCADE & CROSS-BORDER VENDOR TRACKER (§ 9 LkSG) */}
          {activeTab === "cascade" && (
            <div className="space-y-4">
              {/* Cascade Header Banner */}
              <div className="p-4 rounded-xl border border-neutral-200 dark:border-neutral-800 bg-gradient-to-r from-blue-500/10 via-indigo-500/5 to-transparent flex flex-wrap items-center justify-between gap-4">
                <div>
                  <div className="flex items-center gap-2">
                    <Network className="w-5 h-5 text-indigo-600 dark:text-indigo-400" />
                    <h3 className="text-sm font-bold text-neutral-900 dark:text-neutral-100">
                      {isDE
                        ? "Multilaterale Lieferketten-Kaskadenprüfung (§ 9 LkSG)"
                        : "Multi-Tier Supply Chain Cascade & Cross-Border Governance (§ 9 LkSG)"}
                    </h3>
                  </div>
                  <p className="text-xs text-neutral-500 dark:text-neutral-400 mt-1 max-w-2xl">
                    {isDE
                      ? "Prüfung mittelbarer Zulieferer (Tier-2 bis Tier-N): Durchsetzung von vertraglichen Weitergabeklauseln, vorgelagerten Kontrollrechten, standortspezifischen Risiken und anlassbezogener Eskalation bei substantiierter Kenntnis."
                      : "Governance of indirect suppliers (Tier-2 to Tier-N): Pass-through covenant enforcement, upstream audit rights, cross-border hazard indices, and statutory ad-hoc escalation."}
                  </p>
                </div>

                {cascadeData && (
                  <div className="flex items-center gap-2">
                    <button
                      onClick={handleDownloadCascadePdf}
                      disabled={downloadingCascadePdf}
                      className="px-3 py-1.5 rounded-lg text-xs font-mono font-bold bg-neutral-900 text-white dark:bg-neutral-100 dark:text-neutral-900 hover:opacity-90 transition flex items-center gap-1.5 cursor-pointer shadow-sm disabled:opacity-50"
                    >
                      <Download className="w-3.5 h-3.5" />
                      <span>{downloadingCascadePdf ? (isDE ? "Exportiere..." : "Exporting...") : isDE ? "Kaskadendossier (DIN 5008 PDF)" : "Cascade Dossier (PDF)"}</span>
                    </button>
                  </div>
                )}
              </div>

              {/* Cascade Top Metrics */}
              {cascadeData && (
                <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                  <div className="p-3.5 rounded-xl bg-white dark:bg-neutral-900 border border-neutral-200 dark:border-neutral-800">
                    <span className="text-[10px] font-mono text-neutral-400 uppercase">1. Kaskaden-Konformität</span>
                    <div className="text-sm font-bold mt-1 text-neutral-900 dark:text-neutral-100 flex items-center justify-between">
                      <span>{cascadeData.compliance_rating}</span>
                      <span className={`font-mono text-base font-extrabold ${
                        cascadeData.overall_cascade_score >= 80 ? "text-emerald-600" : cascadeData.overall_cascade_score >= 50 ? "text-amber-600" : "text-red-600"
                      }`}>
                        {cascadeData.overall_cascade_score.toFixed(1)}%
                      </span>
                    </div>
                    <div className="w-full bg-neutral-100 dark:bg-neutral-800 rounded-full h-1.5 mt-2 overflow-hidden">
                      <div
                        className={`h-full ${
                          cascadeData.overall_cascade_score >= 80 ? "bg-emerald-500" : cascadeData.overall_cascade_score >= 50 ? "bg-amber-500" : "bg-red-500"
                        }`}
                        style={{ width: `${cascadeData.overall_cascade_score}%` }}
                      />
                    </div>
                  </div>

                  <div className="p-3.5 rounded-xl bg-white dark:bg-neutral-900 border border-neutral-200 dark:border-neutral-800">
                    <span className="text-[10px] font-mono text-neutral-400 uppercase">2. Vertragliche Weitergabe</span>
                    <div className="text-sm font-bold mt-1 text-neutral-900 dark:text-neutral-100 flex items-center justify-between">
                      <span>{isDE ? "Weitergabeklausel" : "Pass-Through"}</span>
                      <span className="font-mono text-base font-extrabold text-indigo-600 dark:text-indigo-400">
                        {cascadeData.pass_through_enforceable_rate.toFixed(1)}%
                      </span>
                    </div>
                    <p className="text-[11px] text-neutral-500 dark:text-neutral-400 mt-1 font-mono">
                      {isDE ? `Direkt: ${cascadeData.direct_suppliers_count} | Mittelbar: ${cascadeData.indirect_suppliers_count} Stufen` : `Direct: ${cascadeData.direct_suppliers_count} | Indirect: ${cascadeData.indirect_suppliers_count}`}
                    </p>
                  </div>

                  <div className="p-3.5 rounded-xl bg-white dark:bg-neutral-900 border border-neutral-200 dark:border-neutral-800">
                    <span className="text-[10px] font-mono text-neutral-400 uppercase">3. Substantiierte Kenntnis (§ 9 Abs. 2)</span>
                    <div className="text-sm font-bold mt-1 flex items-center justify-between">
                      <span className={cascadeData.substantiated_knowledge_active ? "text-red-600" : "text-emerald-600"}>
                        {cascadeData.substantiated_knowledge_active
                          ? `${cascadeData.active_incidents.length} ${isDE ? "Vorfälle aktiv" : "Active Incidents"}`
                          : isDE ? "Keine Vorfälle" : "Zero Alerts"}
                      </span>
                      <span className={`px-2 py-0.5 rounded text-[10px] font-mono font-bold ${
                        cascadeData.bafa_adhoc_filing_recommended
                          ? "bg-red-100 text-red-800 dark:bg-red-950 dark:text-red-300"
                          : "bg-emerald-100 text-emerald-800 dark:bg-emerald-950 dark:text-emerald-300"
                      }`}>
                        {cascadeData.bafa_adhoc_filing_recommended ? (isDE ? "BAFA-Meldung erforderlich" : "BAFA Notice Req.") : (isDE ? "Regelkonform" : "Compliant")}
                      </span>
                    </div>
                    <p className="text-[11px] text-neutral-500 dark:text-neutral-400 mt-1">
                      {cascadeData.bafa_adhoc_filing_recommended
                        ? (isDE ? "Sofortige anlassbezogene Risikoanalyse erforderlich" : "Immediate ad-hoc analysis required")
                        : (isDE ? "Reguläre jährliche Berichterstattung" : "Regular annual reporting cycle")}
                    </p>
                  </div>
                </div>
              )}

              {/* Supply Chain Cascade Hierarchy Tree */}
              {cascadeData && (
                <div className="space-y-3 pt-2">
                  <div className="flex items-center justify-between">
                    <h4 className="text-xs font-bold text-neutral-900 dark:text-neutral-100 font-mono uppercase tracking-wide flex items-center gap-2">
                      <Workflow className="w-4 h-4 text-indigo-600" />
                      <span>{isDE ? "Multilaterale Lieferantenkaskade (Tier-1 bis Tier-3):" : "Multilateral Supplier Hierarchy (Tier-1 to Tier-3):"}</span>
                    </h4>
                    <span className="text-[11px] font-mono text-neutral-500">
                      {cascadeData.supplier_nodes.length} {isDE ? "erfasste Entitäten" : "entities audited"}
                    </span>
                  </div>

                  <div className="space-y-2.5">
                    {cascadeData.supplier_nodes.map((node) => {
                      const isTier1 = node.tier === "TIER_1_DIREKT";
                      const isTier2 = node.tier === "TIER_2_KOMPONENTEN";
                      return (
                        <div
                          key={node.node_id}
                          className={`p-4 rounded-xl border transition shadow-sm ${
                            isTier1
                              ? "bg-white dark:bg-neutral-900 border-indigo-200 dark:border-indigo-950/70 pl-4"
                              : isTier2
                              ? "bg-neutral-50/70 dark:bg-neutral-900/60 border-neutral-200 dark:border-neutral-800 ml-4 md:ml-6"
                              : "bg-neutral-100/60 dark:bg-neutral-950 border-neutral-300 dark:border-neutral-800 ml-8 md:ml-12"
                          }`}
                        >
                          <div className="flex flex-wrap items-center justify-between gap-2">
                            <div className="flex items-center gap-2.5">
                              <span className={`px-2 py-0.5 rounded text-[10px] font-mono font-bold uppercase tracking-wider ${
                                isTier1
                                  ? "bg-indigo-100 text-indigo-800 dark:bg-indigo-950 dark:text-indigo-300"
                                  : isTier2
                                  ? "bg-sky-100 text-sky-800 dark:bg-sky-950 dark:text-sky-300"
                                  : "bg-amber-100 text-amber-800 dark:bg-amber-950 dark:text-amber-300"
                              }`}>
                                {isTier1 ? "Tier 1: Direkt" : isTier2 ? "Tier 2: Komponenten" : "Tier 3: Rohstoffe"}
                              </span>
                              <h5 className="font-bold text-xs text-neutral-900 dark:text-neutral-100 flex items-center gap-1.5">
                                <Building2 className="w-3.5 h-3.5 text-neutral-400" />
                                <span>{node.name}</span>
                              </h5>
                              <span className="text-[10px] font-mono text-neutral-400">
                                ({node.node_id})
                              </span>
                            </div>

                            <div className="flex items-center gap-1.5">
                              {/* Country Hazard Badge */}
                              <span className={`px-2 py-0.5 rounded-full text-[10px] font-mono font-bold flex items-center gap-1 ${
                                node.country.hazard_level === "NIEDRIG"
                                  ? "bg-emerald-100 text-emerald-800 dark:bg-emerald-950/80 dark:text-emerald-300"
                                  : node.country.hazard_level === "MODERAT"
                                  ? "bg-sky-100 text-sky-800 dark:bg-sky-950/80 dark:text-sky-300"
                                  : node.country.hazard_level === "ERHÖHT"
                                  ? "bg-amber-100 text-amber-800 dark:bg-amber-950/80 dark:text-amber-300"
                                  : "bg-red-100 text-red-800 dark:bg-red-950/80 dark:text-red-300"
                              }`}>
                                <Globe className="w-3 h-3" />
                                <span>{node.country.country_code} ({node.country.hazard_level})</span>
                              </span>

                              {/* Substantiated Knowledge Incident Tag */}
                              {node.has_substantiated_knowledge ? (
                                <span className="px-2 py-0.5 rounded-full text-[10px] font-mono font-bold bg-red-100 text-red-800 dark:bg-red-950 dark:text-red-300 flex items-center gap-1">
                                  <AlertCircle className="w-3 h-3" />
                                  <span>VORFALL AKTIV</span>
                                </span>
                              ) : (
                                <span className="px-2 py-0.5 rounded-full text-[10px] font-mono font-bold bg-emerald-50 text-emerald-700 dark:bg-emerald-950/40 dark:text-emerald-400">
                                  UNAUFFÄLLIG
                                </span>
                              )}
                            </div>
                          </div>

                          <div className="grid grid-cols-1 md:grid-cols-3 gap-2 mt-2 pt-2 border-t border-neutral-100 dark:border-neutral-800/60 text-neutral-600 dark:text-neutral-400 text-xs">
                            <div>
                              <span className="text-[10px] font-mono text-neutral-400 block">{isDE ? "LEISTUNG / KOMPONENTE" : "COMPONENT / ROLE"}</span>
                              <span className="font-medium text-neutral-800 dark:text-neutral-200">{node.component_or_service}</span>
                            </div>

                            <div>
                              <span className="text-[10px] font-mono text-neutral-400 block">{isDE ? "VERTRAGLICHE WEITERGABE" : "PASS-THROUGH COVENANT"}</span>
                              <span className={`font-mono text-[11px] font-bold ${
                                node.pass_through_status === "VOLLSTÄNDIG_DURCHSETZBAR"
                                  ? "text-emerald-600"
                                  : node.pass_through_status === "TEILWEISE_UNVOLLSTÄNDIG"
                                  ? "text-amber-600"
                                  : "text-red-600"
                              }`}>
                                {node.pass_through_status}
                              </span>
                            </div>

                            <div>
                              <span className="text-[10px] font-mono text-neutral-400 block">{isDE ? "AUDIT- & PRÜFRECHTE" : "AUDIT RIGHTS CASCADE"}</span>
                              <span className="font-mono text-[11px] text-neutral-800 dark:text-neutral-200 font-semibold">
                                {node.audit_rights}
                              </span>
                            </div>
                          </div>
                        </div>
                      );
                    })}
                  </div>
                </div>
              )}

              {/* Cross-Border Jurisdictions Hazard Matrix */}
              {cascadeData && (
                <div className="space-y-3 pt-3">
                  <h4 className="text-xs font-bold text-neutral-900 dark:text-neutral-100 font-mono uppercase tracking-wide flex items-center gap-2">
                    <Globe className="w-4 h-4 text-neutral-500" />
                    <span>{isDE ? "Grenzüberschreitende Standort-Risikoprofile (ITUC & Basel Index):" : "Cross-Border Jurisdiction Risk Matrix:"}</span>
                  </h4>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                    {cascadeData.jurisdiction_breakdown.map((j) => (
                      <div
                        key={j.country_code}
                        className="p-3 rounded-xl border border-neutral-200 dark:border-neutral-800 bg-white dark:bg-neutral-900 shadow-sm space-y-1.5 text-xs"
                      >
                        <div className="flex items-center justify-between">
                          <span className="font-bold text-neutral-900 dark:text-neutral-100">
                            [{j.country_code}] {j.country_name_de}
                          </span>
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
                        <div className="flex items-center gap-3 text-[11px] font-mono text-neutral-500">
                          <span>ITUC: {j.ituc_rating}/5</span>
                          <span>CPI Score: {j.cpi_score}/100</span>
                          <span>Basel Anhang VII: {j.basel_annex_vii ? "Ja (OECD)" : "Nein"}</span>
                        </div>
                        <p className="text-[11px] text-neutral-600 dark:text-neutral-400">
                          {j.risk_summary_de}
                        </p>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Substantiated Knowledge Incidents & Escalation Schedule */}
              {cascadeData && (
                <div className="space-y-3 pt-3">
                  <h4 className="text-xs font-bold text-neutral-900 dark:text-neutral-100 font-mono uppercase tracking-wide flex items-center gap-2">
                    <AlertTriangle className="w-4 h-4 text-red-600" />
                    <span>{isDE ? "Substantiierte Kenntnis & Gesetzliche Eskalationskaskade (§ 9 Abs. 2):" : "Substantiated Knowledge Incidents (§ 9(2) LkSG):"}</span>
                  </h4>

                  {cascadeData.active_incidents.length === 0 ? (
                    <div className="p-4 rounded-xl border border-emerald-200 dark:border-emerald-950/60 bg-emerald-50/50 dark:bg-emerald-950/20 text-emerald-800 dark:text-emerald-300 text-xs">
                      {isDE
                        ? "Aktuell liegen keine offenen Vorfälle substantiierter Kenntnis bezüglich mittelbarer Vorlieferanten vor. Die gesetzlichen Anforderungen nach § 9 Abs. 1 LkSG sind formal erfüllt."
                        : "No active substantiated knowledge alerts reported for indirect suppliers. Regular audit cycle active."}
                    </div>
                  ) : (
                    <div className="space-y-3">
                      {cascadeData.active_incidents.map((inc) => (
                        <div
                          key={inc.incident_id}
                          className="p-4 rounded-xl border border-red-200 dark:border-red-900/60 bg-white dark:bg-neutral-900 shadow-sm space-y-2.5 text-xs"
                        >
                          <div className="flex flex-wrap items-center justify-between gap-2">
                            <div className="flex items-center gap-2">
                              <span className="font-mono font-bold text-red-600 dark:text-red-400">
                                [{inc.incident_id}]
                              </span>
                              <h5 className="font-bold text-neutral-900 dark:text-neutral-100">
                                {inc.violation_title_de}
                              </h5>
                            </div>
                            <span className="px-2 py-0.5 rounded-full text-[10px] font-mono font-bold bg-red-100 text-red-800 dark:bg-red-950 dark:text-red-300">
                              {inc.severity}
                            </span>
                          </div>

                          <div className="grid grid-cols-1 md:grid-cols-3 gap-2 text-[11px] text-neutral-600 dark:text-neutral-400 bg-neutral-50 dark:bg-neutral-800/40 p-2.5 rounded-lg font-mono">
                            <div>
                              <span>Betroffene Entität: </span>
                              <strong className="text-neutral-900 dark:text-neutral-100">{inc.supplier_name}</strong>
                            </div>
                            <div>
                              <span>Rechtsgrundlage: </span>
                              <strong className="text-neutral-900 dark:text-neutral-100">{inc.statutory_basis}</strong>
                            </div>
                            <div>
                              <span>Quelle: </span>
                              <strong className="text-neutral-900 dark:text-neutral-100">{inc.source_of_knowledge}</strong>
                            </div>
                          </div>

                          {/* Escalation Stage & Countdown */}
                          <div className="p-2.5 rounded-lg bg-indigo-50/70 dark:bg-indigo-950/30 border border-indigo-100 dark:border-indigo-900/40 flex flex-wrap items-center justify-between gap-2">
                            <div className="flex items-center gap-2">
                              <Clock className="w-4 h-4 text-indigo-600 dark:text-indigo-400" />
                              <span className="font-mono font-bold text-[11px] text-indigo-900 dark:text-indigo-200">
                                {inc.escalation_stage}
                              </span>
                            </div>
                            <span className="font-mono text-[11px] font-bold text-amber-700 dark:text-amber-300">
                              {isDE ? `Gesetzliche Frist: ${inc.statutory_deadline_days} Tage (${inc.days_remaining} Tage verbleibend)` : `Deadline: ${inc.statutory_deadline_days}d (${inc.days_remaining}d left)`}
                            </span>
                          </div>

                          <div>
                            <span className="text-[10px] font-mono text-neutral-400 block mb-1">
                              {isDE ? "ERFORDERLICHE ABHILFEMASSNAHMEN (BAFA-LEITFADEN):" : "REQUIRED STATUTORY ACTIONS:"}
                            </span>
                            <pre className="text-[11px] text-neutral-700 dark:text-neutral-300 whitespace-pre-wrap font-sans bg-neutral-50 dark:bg-neutral-800/60 p-2.5 rounded-lg border border-neutral-200 dark:border-neutral-800">
                              {inc.required_remediation_de}
                            </pre>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

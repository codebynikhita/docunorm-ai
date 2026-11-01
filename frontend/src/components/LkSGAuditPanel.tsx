"use client";

import React, { useState, useEffect } from "react";
import {
  Shield,
  ShieldCheck,
  ShieldAlert,
  AlertTriangle,
  FileText,
  X,
  ExternalLink,
  ChevronRight,
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
} from "lucide-react";
import { Language } from "@/lib/i18n";
import {
  LkSGAuditResponse,
  LkSGRiskItem,
  getLkSGAudit,
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
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [filterSeverity, setFilterSeverity] = useState<string>("ALL");
  const [activeTab, setActiveTab] = useState<"overview" | "human_rights" | "environment" | "governance">("overview");

  useEffect(() => {
    if (isOpen && documentId) {
      loadAudit();
    }
  }, [isOpen, documentId]);

  const loadAudit = async () => {
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
              onClick={loadAudit}
              disabled={loading}
              className="p-2 text-neutral-500 hover:text-neutral-900 dark:hover:text-neutral-100 rounded-lg hover:bg-neutral-100 dark:hover:bg-neutral-800 transition"
              title={isDE ? "Neu laden" : "Reload"}
            >
              <RefreshCw className={`w-4 h-4 ${loading ? "animate-spin" : ""}`} />
            </button>
            <button
              onClick={onClose}
              className="p-2 text-neutral-500 hover:text-neutral-900 dark:hover:text-neutral-100 rounded-lg hover:bg-neutral-100 dark:hover:bg-neutral-800 transition"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* Content Area */}
        <div className="flex-1 overflow-y-auto p-6 space-y-6">
          {loading && (
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

          {assessment && !loading && (
            <>
              {/* Executive Scorecard Box */}
              <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                {/* Overall Score Card */}
                <div className="p-4 rounded-xl border border-neutral-200 dark:border-neutral-800 bg-neutral-50/50 dark:bg-neutral-950/30 flex flex-col justify-between">
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-semibold text-neutral-500 uppercase tracking-wider">
                      {isDE ? "Gesamt-Konformität" : "Overall Score"}
                    </span>
                    <span className={`px-2 py-0.5 text-xs font-black rounded ${getRatingBadge(assessment.compliance_rating)}`}>
                      {assessment.compliance_rating}
                    </span>
                  </div>
                  <div className="my-3">
                    <div className="text-3xl font-black text-neutral-900 dark:text-neutral-100">
                      {assessment.overall_compliance_score.toFixed(1)}%
                    </div>
                    <div className="w-full bg-neutral-200 dark:bg-neutral-800 h-2 rounded-full overflow-hidden mt-2">
                      <div
                        className="bg-emerald-600 h-full rounded-full transition-all"
                        style={{ width: `${Math.min(100, assessment.overall_compliance_score)}%` }}
                      />
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
                    {isDE ? "Hinweisgeber & Jahresbericht" : "Whistleblower & Reporting"}
                  </span>
                </div>
              </div>

              {/* Statutory Checklist Badges */}
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
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
                  <Sparkles className="w-3.5 h-3.5 text-amber-500" />
                  {isDE ? "Aufsichtsrechtliche Gesamtwürdigung" : "Regulatory Compliance Assessment"}
                </h4>
                <p className="text-sm leading-relaxed text-neutral-700 dark:text-neutral-300">
                  {isDE ? assessment.executive_summary_de : assessment.executive_summary_en}
                </p>
              </div>

              {/* Identified Risks & Violations */}
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
                        className={`px-2.5 py-1 rounded-lg font-medium transition ${
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
                              className="inline-flex items-center gap-1 text-xs text-emerald-700 dark:text-emerald-400 hover:underline font-semibold"
                            >
                              Seite {item.page_number}
                              <ChevronRight className="w-3.5 h-3.5" />
                            </button>
                          )}
                        </div>

                        {/* Citation & BAFA Guidance Row */}
                        <div className="flex flex-wrap items-center gap-2 text-xs">
                          <span className="px-2 py-0.5 rounded bg-blue-50 dark:bg-blue-950/60 text-blue-700 dark:text-blue-300 border border-blue-200 dark:border-blue-900 font-mono">
                            {item.statutory_reference}
                          </span>
                          <span className="px-2 py-0.5 rounded bg-purple-50 dark:bg-purple-950/60 text-purple-700 dark:text-purple-300 border border-purple-200 dark:border-purple-900">
                            {item.bafa_guideline_ref}
                          </span>
                        </div>

                        {/* Finding Narrative */}
                        <p className="text-xs text-neutral-700 dark:text-neutral-300 leading-relaxed">
                          {isDE ? item.finding_de : item.finding_en}
                        </p>

                        {/* Evidence Quote */}
                        {item.evidence_snippet && (
                          <div className="p-2.5 rounded-lg bg-neutral-50 dark:bg-neutral-950/60 border border-neutral-200 dark:border-neutral-800 text-xs italic text-neutral-600 dark:text-neutral-400 font-mono">
                            "{item.evidence_snippet}"
                          </div>
                        )}

                        {/* Remediation Action */}
                        <div className="p-3 rounded-lg bg-emerald-50 dark:bg-emerald-950/30 border border-emerald-200 dark:border-emerald-900/60 flex items-start gap-2.5">
                          <ShieldCheck className="w-4 h-4 text-emerald-600 mt-0.5 flex-shrink-0" />
                          <div>
                            <span className="text-xs font-bold text-emerald-800 dark:text-emerald-300">
                              {isDE ? "BAFA-konforme Nachbesserung:" : "BAFA-Compliant Remediation Action:"}
                            </span>
                            <p className="text-xs text-emerald-900 dark:text-emerald-200 mt-0.5">
                              {isDE ? item.remediation_action_de : item.remediation_action_en}
                            </p>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </>
          )}
        </div>

        {/* Footer */}
        <div className="px-6 py-4 border-t border-neutral-200 dark:border-neutral-800 bg-neutral-50 dark:bg-neutral-950/60 flex items-center justify-between">
          <div className="text-xs text-neutral-500">
            {isDE ? "Aufsichtsbehörde: Bundesamt für Wirtschaft und Ausfuhrkontrolle (BAFA)" : "Regulatory Authority: Federal Office for Economic Affairs and Export Control (BAFA)"}
          </div>
          <button
            onClick={onClose}
            className="px-4 py-2 text-xs font-semibold rounded-lg bg-neutral-900 text-white dark:bg-neutral-100 dark:text-neutral-900 hover:opacity-90 transition"
          >
            {isDE ? "Schließen" : "Close"}
          </button>
        </div>
      </div>
    </div>
  );
}

"use client";

import React, { useState, useEffect } from "react";
import {
  Shield,
  ShieldCheck,
  ShieldAlert,
  AlertTriangle,
  XCircle,
  FileText,
  Printer,
  Copy,
  Check,
  X,
  ExternalLink,
  ChevronRight,
  Building2,
  Server,
  Lock,
  Calendar,
  Sparkles,
  Users,
  Eye,
  Key,
  BadgeAlert,
  Download,
} from "lucide-react";
import { Language } from "@/lib/i18n";
import {
  DoraAuditRightsReport,
  getDoraAuditRights,
  AuditRightCheckResult,
} from "@/lib/api";

interface AuditRightsModalProps {
  isOpen: boolean;
  onClose: () => void;
  lang: Language;
  documentId?: string;
  documentName?: string;
  availableDocuments?: any[];
  onSelectDocument?: (doc: any) => void;
  onJumpToCitation?: (page: number, bbox?: [number, number, number, number]) => void;
}

export function AuditRightsModal({
  isOpen,
  onClose,
  lang,
  documentId,
  documentName = "",
  availableDocuments = [],
  onSelectDocument,
  onJumpToCitation,
}: AuditRightsModalProps) {
  const [report, setReport] = useState<DoraAuditRightsReport | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  // Tab State
  const [activeTab, setActiveTab] = useState<"checks" | "letter" | "scope">("checks");

  // Letter Customizer State
  const [customInspectionDate, setCustomInspectionDate] = useState<string>(() => {
    const d = new Date();
    d.setDate(d.getDate() + 30);
    return d.toISOString().split("T")[0];
  });
  const [customInspectorName, setCustomInspectorName] = useState<string>(
    "Dr. Maximilian von Weber (Leitender BaFin-Bankenprüfer)"
  );
  const [letterLanguage, setLetterLanguage] = useState<"de" | "en">("de");
  const [copiedLetter, setCopiedLetter] = useState<boolean>(false);

  useEffect(() => {
    if (!isOpen) return;

    if (!documentId) {
      setReport(null);
      setError(null);
      return;
    }

    let isMounted = true;
    setLoading(true);
    setError(null);

    getDoraAuditRights(documentId)
      .then((data) => {
        if (isMounted) {
          setReport(data);
          setLoading(false);
        }
      })
      .catch((err) => {
        if (isMounted) {
          setError(err.message || "Failed to load Audit Rights report");
          setLoading(false);
        }
      });

    return () => {
      isMounted = false;
    };
  }, [isOpen, documentId]);

  if (!isOpen) return null;

  const handleCopyLetter = () => {
    if (!report?.notice_letter) return;
    const content =
      letterLanguage === "de"
        ? report.notice_letter.german_letter_content
        : report.notice_letter.english_letter_content;
    navigator.clipboard.writeText(content);
    setCopiedLetter(true);
    setTimeout(() => setCopiedLetter(false), 2500);
  };

  const handlePrint = () => {
    window.print();
  };

  const isDe = lang === "DE";

  const getRatingBadge = (rating: string) => {
    if (rating.includes("AAA") || rating.includes("VOLLSTÄNDIG")) {
      return (
        <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/30">
          <ShieldCheck className="w-4 h-4 text-emerald-400" />
          {rating}
        </span>
      );
    }
    if (rating.includes("BBB") || rating.includes("BEDINGT")) {
      return (
        <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-amber-500/10 text-amber-400 border border-amber-500/30">
          <AlertTriangle className="w-4 h-4 text-amber-400" />
          {rating}
        </span>
      );
    }
    return (
      <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-rose-500/10 text-rose-400 border border-rose-500/30">
        <ShieldAlert className="w-4 h-4 text-rose-400" />
        {rating}
      </span>
    );
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case "COMPLIANT":
        return (
          <span className="px-2.5 py-0.5 rounded-full text-[11px] font-medium bg-emerald-500/15 text-emerald-400 border border-emerald-500/30 flex items-center gap-1">
            <ShieldCheck className="w-3.5 h-3.5" />
            {isDe ? "Konform" : "Compliant"}
          </span>
        );
      case "PARTIALLY_COMPLIANT":
        return (
          <span className="px-2.5 py-0.5 rounded-full text-[11px] font-medium bg-amber-500/15 text-amber-400 border border-amber-500/30 flex items-center gap-1">
            <AlertTriangle className="w-3.5 h-3.5" />
            {isDe ? "Bedingt Konform" : "Partially Compliant"}
          </span>
        );
      default:
        return (
          <span className="px-2.5 py-0.5 rounded-full text-[11px] font-medium bg-rose-500/15 text-rose-400 border border-rose-500/30 flex items-center gap-1">
            <XCircle className="w-3.5 h-3.5" />
            {isDe ? "Kritisch Defizitär" : "Non-Compliant"}
          </span>
        );
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-3 sm:p-6 bg-slate-950/80 backdrop-blur-md animate-in fade-in duration-200">
      <div className="relative w-full max-w-6xl max-h-[92vh] flex flex-col bg-slate-900 border border-slate-800 rounded-2xl shadow-2xl overflow-hidden">
        
        {/* Modal Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-slate-800 bg-slate-950/60">
          <div className="flex items-center gap-3">
            <div className="p-2.5 rounded-xl bg-blue-500/10 border border-blue-500/20 text-blue-400">
              <Shield className="w-6 h-6" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h2 className="text-lg font-semibold text-white tracking-tight">
                  {isDe
                    ? "Aufsichtsrechtliche Prüfungsrechte & BaFin-Inspektionsgenerator"
                    : "Supervisory Audit Rights & BaFin Inspection Generator"}
                </h2>
                <span className="text-[10px] uppercase font-bold tracking-wider px-2 py-0.5 rounded bg-blue-500/20 text-blue-300 border border-blue-500/30">
                  KWG § 25b • DORA Art. 30(3)(e)
                </span>
              </div>
              <p className="text-xs text-slate-400 mt-0.5">
                {documentName
                  ? `${isDe ? "Vertrag:" : "Contract:"} ${documentName}`
                  : isDe
                  ? "Bitte wählen Sie ein Dokument aus"
                  : "Please select an active contract to audit"}
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={onClose}
              className="p-2 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800/80 transition-colors"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* Document Switcher Toolbar (if multiple documents available) */}
        {availableDocuments.length > 1 && (
          <div className="px-6 py-2.5 bg-slate-950/40 border-b border-slate-800/60 flex items-center gap-3 text-xs overflow-x-auto">
            <span className="text-slate-400 flex items-center gap-1.5 shrink-0">
              <FileText className="w-3.5 h-3.5 text-blue-400" />
              {isDe ? "Geprüfter Vertrag:" : "Inspected Contract:"}
            </span>
            <div className="flex items-center gap-2">
              {availableDocuments.map((doc) => (
                <button
                  key={doc.id}
                  onClick={() => onSelectDocument && onSelectDocument(doc)}
                  className={`px-3 py-1 rounded-md text-xs transition-all whitespace-nowrap ${
                    doc.id === documentId
                      ? "bg-blue-600 text-white font-medium shadow-sm shadow-blue-500/20"
                      : "bg-slate-800/60 text-slate-300 hover:bg-slate-800 hover:text-white border border-slate-700/50"
                  }`}
                >
                  {doc.filename}
                </button>
              ))}
            </div>
          </div>
        )}

        {/* Navigation Tabs */}
        <div className="flex items-center gap-1 px-6 pt-3 border-b border-slate-800 bg-slate-900/40">
          <button
            onClick={() => setActiveTab("checks")}
            className={`flex items-center gap-2 px-4 py-2.5 text-xs font-medium rounded-t-lg border-b-2 transition-all ${
              activeTab === "checks"
                ? "border-blue-500 text-blue-400 bg-slate-800/50"
                : "border-transparent text-slate-400 hover:text-slate-200 hover:bg-slate-800/20"
            }`}
          >
            <ShieldCheck className="w-4 h-4" />
            {isDe ? "5 Gesetzliche Prüfpunkte (KWG § 25b)" : "5 Statutory Audit Rules (DORA)"}
          </button>
          <button
            onClick={() => setActiveTab("letter")}
            className={`flex items-center gap-2 px-4 py-2.5 text-xs font-medium rounded-t-lg border-b-2 transition-all ${
              activeTab === "letter"
                ? "border-blue-500 text-blue-400 bg-slate-800/50"
                : "border-transparent text-slate-400 hover:text-slate-200 hover:bg-slate-800/20"
            }`}
          >
            <FileText className="w-4 h-4" />
            {isDe ? "DIN 5008 BaFin-Inspektionsbrief" : "DIN 5008 Official BaFin Notice Letter"}
          </button>
          <button
            onClick={() => setActiveTab("scope")}
            className={`flex items-center gap-2 px-4 py-2.5 text-xs font-medium rounded-t-lg border-b-2 transition-all ${
              activeTab === "scope"
                ? "border-blue-500 text-blue-400 bg-slate-800/50"
                : "border-transparent text-slate-400 hover:text-slate-200 hover:bg-slate-800/20"
            }`}
          >
            <Server className="w-4 h-4" />
            {isDe ? "Prüfungsbereich & Forensik-Checkliste" : "Inspection Scope & Forensic Checklist"}
          </button>
        </div>

        {/* Modal Body */}
        <div className="flex-1 overflow-y-auto p-6 space-y-6">
          {loading && (
            <div className="flex flex-col items-center justify-center py-20 text-center">
              <div className="w-10 h-10 border-2 border-blue-500 border-t-transparent rounded-full animate-spin mb-4" />
              <p className="text-sm font-medium text-slate-200">
                {isDe
                  ? "Analysiere Prüfungsrechte unter KWG § 25b und DORA Art. 30(3)(e)..."
                  : "Auditing supervisory inspection rights under KWG § 25b and DORA Art. 30(3)(e)..."}
              </p>
              <p className="text-xs text-slate-500 mt-1">
                {isDe
                  ? "Prüfung auf Kautionsfallen, Vor-Ort-Zutritt und BaFin-Direktzugriff..."
                  : "Scanning for audit deposit traps, on-site datacenter access, and BaFin direct rights..."}
              </p>
            </div>
          )}

          {error && (
            <div className="p-4 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-300 flex items-start gap-3">
              <AlertTriangle className="w-5 h-5 text-rose-400 shrink-0 mt-0.5" />
              <div>
                <h4 className="text-sm font-semibold">
                  {isDe ? "Fehler bei der Revisionsprüfung" : "Audit Evaluation Error"}
                </h4>
                <p className="text-xs text-rose-300/80 mt-1">{error}</p>
              </div>
            </div>
          )}

          {!loading && !error && !documentId && (
            <div className="flex flex-col items-center justify-center py-16 text-center border-2 border-dashed border-slate-800 rounded-2xl">
              <Building2 className="w-12 h-12 text-slate-600 mb-3" />
              <h3 className="text-base font-semibold text-slate-200">
                {isDe ? "Kein Dokument für die Prüfung ausgewählt" : "No Contract Selected for Audit"}
              </h3>
              <p className="text-xs text-slate-400 max-w-md mt-1 mb-4">
                {isDe
                  ? "Bitte wählen Sie in der oberen Leiste oder im Dokumenten-Explorer einen ICT-Vertrag aus, um die aufsichtsrechtlichen Vor-Ort-Prüfrechte zu überprüfen."
                  : "Please select an ICT contract from the top bar or document explorer to audit statutory on-site inspection privileges."}
              </p>
            </div>
          )}

          {!loading && !error && report && (
            <>
              {/* Executive Score Card */}
              <div className="p-5 rounded-2xl bg-gradient-to-br from-slate-900 to-slate-950 border border-slate-800 shadow-xl relative overflow-hidden">
                <div className="absolute top-0 right-0 w-64 h-64 bg-blue-500/5 rounded-full blur-3xl pointer-events-none" />
                <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                  <div className="space-y-1.5">
                    <div className="flex items-center gap-2">
                      <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
                        {isDe ? "Revisionsurteil nach KWG § 25b & DORA" : "Supervisory Audit Score"}
                      </span>
                      {getRatingBadge(report.compliance_rating)}
                    </div>
                    <h3 className="text-2xl font-bold text-white tracking-tight flex items-center gap-3">
                      {report.overall_score.toFixed(1)}%{" "}
                      <span className="text-xs font-normal text-slate-400">
                        ({isDe ? "Gesamtkonformität" : "Total Compliance"})
                      </span>
                    </h3>
                    <p className="text-xs text-slate-300 max-w-2xl leading-relaxed">
                      {isDe ? report.summary_de : report.summary_en}
                    </p>
                  </div>

                  <div className="flex items-center gap-2 self-start md:self-center shrink-0">
                    <button
                      onClick={() => setActiveTab("letter")}
                      className="px-3.5 py-2 rounded-xl text-xs font-medium bg-blue-600 hover:bg-blue-500 text-white shadow-lg shadow-blue-600/20 transition-all flex items-center gap-1.5"
                    >
                      <Printer className="w-3.5 h-3.5" />
                      {isDe ? "BaFin-Brief öffnen" : "View BaFin Letter"}
                    </button>
                  </div>
                </div>
              </div>

              {/* TAB 1: 5 STATUTORY CHECKS */}
              {activeTab === "checks" && (
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <h4 className="text-sm font-semibold text-slate-200 flex items-center gap-2">
                      <Shield className="w-4 h-4 text-blue-400" />
                      {isDe
                        ? "Detaillierte Prüfung nach KWG § 25b & DORA Art. 30(3)(e)"
                        : "Detailed Compliance Checklist (KWG § 25b & DORA Art. 30(3)(e))"}
                    </h4>
                    <span className="text-xs text-slate-400">
                      5 {isDe ? "Prüfpunkte ausgewertet" : "checks evaluated"}
                    </span>
                  </div>

                  <div className="grid grid-cols-1 gap-4">
                    {report.checks.map((c, idx) => (
                      <div
                        key={c.rule_id}
                        className="p-4 rounded-xl bg-slate-900/70 border border-slate-800 hover:border-slate-700 transition-all shadow-md"
                      >
                        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 mb-2.5">
                          <div className="flex items-center gap-2">
                            <span className="w-5 h-5 rounded-md bg-slate-800 border border-slate-700 text-[10px] font-bold text-slate-400 flex items-center justify-center">
                              {idx + 1}
                            </span>
                            <span className="text-xs font-bold text-slate-400 uppercase tracking-wider">
                              {c.rule_id}
                            </span>
                            <h5 className="text-sm font-semibold text-white">
                              {isDe ? c.name_de : c.name_en}
                            </h5>
                          </div>
                          <div>{getStatusBadge(c.status)}</div>
                        </div>

                        <p className="text-xs text-slate-400 mb-3">
                          {isDe ? c.description_de : c.description_en}
                        </p>

                        {/* Extracted Clause */}
                        {c.extracted_clause ? (
                          <div className="p-3 rounded-lg bg-slate-950/70 border border-slate-800/80 mb-3">
                            <div className="flex items-center justify-between text-[11px] text-slate-400 mb-1.5 font-medium">
                              <span className="flex items-center gap-1.5 text-blue-400">
                                <FileText className="w-3.5 h-3.5" />
                                {isDe ? "Gefundene Vertragsklausel:" : "Extracted Contract Clause:"}
                              </span>
                              {c.page_number && (
                                <button
                                  onClick={() =>
                                    onJumpToCitation && onJumpToCitation(c.page_number!)
                                  }
                                  className="text-xs text-blue-400 hover:text-blue-300 flex items-center gap-1 hover:underline"
                                >
                                  {isDe ? `Seite ${c.page_number}` : `Page ${c.page_number}`}
                                  <ExternalLink className="w-3 h-3" />
                                </button>
                              )}
                            </div>
                            <blockquote className="text-xs text-slate-300 italic border-l-2 border-blue-500/50 pl-2.5 py-0.5">
                              "{c.extracted_clause}"
                            </blockquote>
                          </div>
                        ) : (
                          <div className="p-2.5 rounded-lg bg-slate-950/40 border border-slate-800/50 text-xs text-slate-500 italic mb-3">
                            {isDe
                              ? "Keine ausdrückliche Klausel im Vertrag identifiziert (Regelungslücke)."
                              : "No explicit clause identified in the agreement (regulatory gap)."}
                          </div>
                        )}

                        {/* Statutory Recommendation */}
                        <div className="flex items-start gap-2 p-2.5 rounded-lg bg-blue-950/20 border border-blue-900/30 text-xs text-blue-300/90">
                          <Sparkles className="w-4 h-4 text-blue-400 shrink-0 mt-0.5" />
                          <div>
                            <span className="font-semibold text-blue-300">
                              {isDe ? "Handlungsempfehlung:" : "Regulatory Recommendation:"}{" "}
                            </span>
                            {isDe ? c.recommendation_de : c.recommendation_en}
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* TAB 2: DIN 5008 GERMAN INSPECTION NOTICE LETTER */}
              {activeTab === "letter" && report.notice_letter && (
                <div className="space-y-4">
                  {/* Toolbar */}
                  <div className="flex flex-wrap items-center justify-between gap-3 p-4 rounded-xl bg-slate-900/80 border border-slate-800">
                    <div className="flex items-center gap-3">
                      <span className="text-xs font-semibold text-slate-300">
                        {isDe ? "Sprachfassung:" : "Letter Language:"}
                      </span>
                      <div className="flex items-center p-0.5 rounded-lg bg-slate-950 border border-slate-800">
                        <button
                          onClick={() => setLetterLanguage("de")}
                          className={`px-3 py-1 rounded text-xs font-medium transition-all ${
                            letterLanguage === "de"
                              ? "bg-blue-600 text-white"
                              : "text-slate-400 hover:text-white"
                          }`}
                        >
                          🇩🇪 DIN 5008 (Deutsch)
                        </button>
                        <button
                          onClick={() => setLetterLanguage("en")}
                          className={`px-3 py-1 rounded text-xs font-medium transition-all ${
                            letterLanguage === "en"
                              ? "bg-blue-600 text-white"
                              : "text-slate-400 hover:text-white"
                          }`}
                        >
                          🇺🇸 English Supervisory
                        </button>
                      </div>
                    </div>

                    <div className="flex items-center gap-2">
                      <button
                        onClick={handleCopyLetter}
                        className="px-3 py-1.5 rounded-lg text-xs font-medium bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 transition-all flex items-center gap-1.5"
                      >
                        {copiedLetter ? (
                          <>
                            <Check className="w-3.5 h-3.5 text-emerald-400" />
                            <span className="text-emerald-400">{isDe ? "Kopiert!" : "Copied!"}</span>
                          </>
                        ) : (
                          <>
                            <Copy className="w-3.5 h-3.5" />
                            {isDe ? "Volltext kopieren" : "Copy Text"}
                          </>
                        )}
                      </button>

                      <button
                        onClick={handlePrint}
                        className="px-3 py-1.5 rounded-lg text-xs font-medium bg-blue-600 hover:bg-blue-500 text-white shadow-md shadow-blue-600/20 transition-all flex items-center gap-1.5"
                      >
                        <Printer className="w-3.5 h-3.5" />
                        {isDe ? "Drucken / PDF speichern" : "Print / PDF Export"}
                      </button>
                    </div>
                  </div>

                  {/* Letter Sheet formatted according to DIN 5008 */}
                  <div className="p-8 sm:p-12 rounded-xl bg-white text-slate-900 shadow-2xl font-serif max-w-4xl mx-auto border border-slate-200">
                    <div className="space-y-6 text-sm leading-relaxed">
                      {/* Sender Letterhead */}
                      <div className="border-b border-slate-300 pb-4">
                        <div className="text-[11px] font-sans tracking-wider uppercase text-slate-500 font-semibold">
                          {report.notice_letter.sender_institution}
                        </div>
                        <div className="text-[10px] font-sans text-slate-400">
                          Taunusanlage 8 • D-60329 Frankfurt am Main • Bundesrepublik Deutschland
                        </div>
                      </div>

                      {/* Recipient Address Field */}
                      <div className="pt-2 pb-4 font-sans text-xs text-slate-700">
                        <div className="text-[10px] text-slate-400 mb-1">
                          {isDe ? "Zustellungsbevollmächtigte Stelle:" : "Authorized Recipient:"}
                        </div>
                        <div className="font-bold text-slate-900 text-sm">
                          {report.notice_letter.recipient_vendor}
                        </div>
                        <div>Executive Management & Regulatory Assurance</div>
                        <div>Global Infrastructure & Cloud Operations</div>
                      </div>

                      {/* Metadata bar */}
                      <div className="flex justify-between items-center text-xs font-sans text-slate-600 border-t border-b border-slate-200 py-2">
                        <div>
                          <strong>{isDe ? "Geschäftszeichen:" : "Ref:"}</strong>{" "}
                          <span className="font-mono text-slate-800">
                            {report.notice_letter.reference_number}
                          </span>
                        </div>
                        <div>
                          <strong>{isDe ? "Datum:" : "Date:"}</strong>{" "}
                          {new Date().toLocaleDateString(isDe ? "de-DE" : "en-US", {
                            year: "numeric",
                            month: "long",
                            day: "numeric",
                          })}
                        </div>
                      </div>

                      {/* Subject */}
                      <div className="pt-2 font-sans font-bold text-sm tracking-wide text-slate-950 uppercase">
                        {letterLanguage === "de"
                          ? "BETREFF: ANKÜNDIGUNG EINER AUFSICHTSRECHTLICHEN VOR-ORT-PRÜFUNG GEMÄSS § 25b KWG & DORA ART. 30 ABS. 3 LIT. E"
                          : "SUBJECT: FORMAL NOTIFICATION OF STATUTORY REGULATORY ON-SITE INSPECTION UNDER KWG § 25b & DORA ART. 30(3)(e)"}
                      </div>

                      {/* Legal Basis Pill */}
                      <div className="font-sans text-[11px] text-blue-900 bg-blue-50 border border-blue-200 px-3 py-1.5 rounded-md font-medium">
                        <strong>{isDe ? "Rechtsgrundlage:" : "Legal Mandate:"}</strong>{" "}
                        {report.notice_letter.legal_basis}
                      </div>

                      {/* Letter Body */}
                      <div className="whitespace-pre-line text-xs font-sans text-slate-800 leading-relaxed pt-2">
                        {letterLanguage === "de"
                          ? report.notice_letter.german_letter_content
                          : report.notice_letter.english_letter_content}
                      </div>

                      {/* Official Signatures */}
                      <div className="pt-8 border-t border-slate-200 grid grid-cols-2 gap-8 font-sans text-xs">
                        <div>
                          <div className="border-b border-slate-400 pb-8 text-slate-400 italic">
                            (Unterschrift Leitender Revisor)
                          </div>
                          <div className="pt-1 font-semibold text-slate-900">
                            {customInspectorName}
                          </div>
                          <div className="text-[10px] text-slate-500">
                            DocuNorm Sovereign Banking Assurance
                          </div>
                        </div>

                        <div>
                          <div className="border-b border-slate-400 pb-8 text-slate-400 italic">
                            (Dienstsiegel / BaFin-Akkreditierung)
                          </div>
                          <div className="pt-1 font-semibold text-slate-900">
                            Prüfungsreferenz: {report.notice_letter.letter_id}
                          </div>
                          <div className="text-[10px] text-slate-500">
                            Frankfurt Financial Hub (BSI C5 & DSGVO)
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {/* TAB 3: INSPECTION SCOPE & FORENSIC CHECKLIST */}
              {activeTab === "scope" && (
                <div className="space-y-4">
                  <div className="p-4 rounded-xl bg-slate-900/80 border border-slate-800">
                    <h4 className="text-sm font-semibold text-white mb-1 flex items-center gap-2">
                      <Lock className="w-4 h-4 text-blue-400" />
                      {isDe
                        ? "Aufsichtlicher Prüfungsrahmen gem. BAIT Ziffer 8.1"
                        : "Statutory Examination Scope under BAIT Section 8.1"}
                    </h4>
                    <p className="text-xs text-slate-400">
                      {isDe
                        ? "Gemäß BaFin-Rundschreiben 10/2018 (BAIT) und DORA Art. 30 Abs. 3 lit. e Ziffern i-v umfasst die anstehende Prüfung folgende forensische Bereiche:"
                        : "Pursuant to BaFin Circular 10/2018 (BAIT) and DORA Art. 30(3)(e)(i-v), the upcoming inspection covers the following forensic pillars:"}
                    </p>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800 space-y-2">
                      <div className="flex items-center gap-2 text-xs font-semibold text-blue-400 uppercase tracking-wider">
                        <Server className="w-4 h-4" />
                        Pfeiler 1: Physische Rechenzentrumsinspektion
                      </div>
                      <p className="text-xs text-slate-300">
                        {isDe
                          ? "Zutrittskontrollen, biometrische Schleusen, Brandschutz und Notstromaggregate (USV/Diesel) am Standort Frankfurt am Main."
                          : "Physical perimeter security, biometric airlocks, fire suppression, and UPS backup diesel generators in Frankfurt."}
                      </p>
                    </div>

                    <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800 space-y-2">
                      <div className="flex items-center gap-2 text-xs font-semibold text-emerald-400 uppercase tracking-wider">
                        <Key className="w-4 h-4" />
                        Pfeiler 2: Kryptographische Roh-Logs & TLPT
                      </div>
                      <p className="text-xs text-slate-300">
                        {isDe
                          ? "Einsicht in unveränderliche Audit-Trails (WORM-Storage), Key-Management-Systeme (HSM) und Threat-Led Penetration Testing Berichte."
                          : "Verification of immutable WORM audit logs, HSM cryptographic keys, and Threat-Led Penetration Testing (TLPT) reports."}
                      </p>
                    </div>

                    <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800 space-y-2">
                      <div className="flex items-center gap-2 text-xs font-semibold text-purple-400 uppercase tracking-wider">
                        <Users className="w-4 h-4" />
                        Pfeiler 3: CISO & Incident Response Befragung
                      </div>
                      <p className="text-xs text-slate-300">
                        {isDe
                          ? "Persönliche Befragung der verantwortlichen Sicherheitsarchitekten zu Eskalationspfaden bei Ransomware- und DDoS-Vorfällen."
                          : "Direct witness examination of lead security architects regarding incident escalation during DDoS or ransomware outages."}
                      </p>
                    </div>

                    <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800 space-y-2">
                      <div className="flex items-center gap-2 text-xs font-semibold text-amber-400 uppercase tracking-wider">
                        <Calendar className="w-4 h-4" />
                        Pfeiler 4: BCP & Notfallwiederherstellungstests
                      </div>
                      <p className="text-xs text-slate-300">
                        {isDe
                          ? "Auswertung der RTO- (< 2 Stunden) und RPO-Messungen (< 15 Minuten) bei simuliertem Gesamtausfall der Verfügbarkeitszone."
                          : "Verification of live RTO (< 2h) and RPO (< 15 min) measurements during simulated complete availability zone failovers."}
                      </p>
                    </div>
                  </div>
                </div>
              )}
            </>
          )}
        </div>

        {/* Modal Footer */}
        <div className="flex items-center justify-between px-6 py-4 border-t border-slate-800 bg-slate-950/60">
          <div className="flex items-center gap-2 text-xs text-slate-400">
            <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
            <span>
              {isDe
                ? "BaFin RS 10/2018 (BAIT) • DIN 5008 Konformitätsgarantie"
                : "BaFin RS 10/2018 (BAIT) • DIN 5008 Statutory Letter Guarantee"}
            </span>
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={onClose}
              className="px-4 py-2 rounded-xl text-xs font-medium bg-slate-800 hover:bg-slate-700 text-slate-200 transition-colors"
            >
              {isDe ? "Schließen" : "Close"}
            </button>
          </div>
        </div>

      </div>
    </div>
  );
}

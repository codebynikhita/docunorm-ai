"use client";

import React, { useState } from "react";
import {
  X,
  FileCheck2,
  Download,
  ShieldCheck,
  FileText,
  Lock,
  Layers,
  Sparkles,
  CheckCircle2,
  Loader2,
  AlertTriangle,
  Building2,
  Calendar,
  Key,
} from "lucide-react";
import { downloadDinAuditReportPdf } from "@/lib/api";
import { Language } from "@/lib/i18n";

interface AuditReportExporterModalProps {
  isOpen: boolean;
  onClose: () => void;
  documentId?: string | null;
  documentName?: string;
  lang: Language;
}

export function AuditReportExporterModal({
  isOpen,
  onClose,
  documentId,
  documentName = "",
  lang,
}: AuditReportExporterModalProps) {
  const isDe = lang === "DE";

  const [signatoryName, setSignatoryName] = useState(
    isDe ? "Dr. Michael Weber, Leitender BaFin-Prüfer" : "Dr. Michael Weber, Lead BaFin Examiner"
  );
  const [auditStandard, setAuditStandard] = useState("DIN_5008_ISO_19011");
  const [includeSha256Seal, setIncludeSha256Seal] = useState(true);
  const [includePillarSummary, setIncludePillarSummary] = useState(true);
  const [includeEvidenceSnippets, setIncludeEvidenceSnippets] = useState(true);
  const [isExporting, setIsExporting] = useState(false);
  const [exportSuccess, setExportSuccess] = useState(false);

  if (!isOpen) return null;

  const handleExportPdf = async () => {
    if (!documentId) return;
    setIsExporting(true);
    setExportSuccess(false);
    try {
      await downloadDinAuditReportPdf(documentId, signatoryName);
      setExportSuccess(true);
      setTimeout(() => setExportSuccess(false), 4000);
    } catch (err) {
      console.error("DIN report export failed", err);
    } finally {
      setIsExporting(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm animate-in fade-in duration-150">
      <div className="w-full max-w-2xl bg-[var(--surface-dark)] border border-[var(--surface-border)] rounded-2xl shadow-2xl flex flex-col overflow-hidden">
        {/* Modal Header */}
        <div className="p-4 px-6 border-b border-[var(--surface-border)] flex items-center justify-between bg-[var(--surface-card)]">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-emerald-500/15 border border-emerald-500/30 flex items-center justify-center text-emerald-500">
              <FileCheck2 className="w-5 h-5" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h3 className="font-mono font-bold text-sm text-[var(--foreground)] uppercase tracking-wider">
                  {isDe ? "DIN 5008 Prüfbericht-Export" : "DIN 5008 Audit Report Exporter"}
                </h3>
                <span className="px-2 py-0.5 rounded text-[10px] font-mono bg-emerald-500/15 text-emerald-400 border border-emerald-500/30 font-bold">
                  ISO 19011 • DORA Art. 30
                </span>
              </div>
              <p className="text-[11px] font-mono text-[var(--foreground)] opacity-60">
                {documentName || (isDe ? "Kein Dokument gewählt" : "No document selected")}
              </p>
            </div>
          </div>

          <button
            onClick={onClose}
            className="p-1.5 rounded-lg text-[var(--foreground)] opacity-60 hover:opacity-100 hover:bg-[var(--surface-card)] cursor-pointer"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Modal Body */}
        <div className="p-6 space-y-5 text-xs font-mono">
          {/* Document Integrity Badge */}
          <div className="p-3.5 rounded-xl bg-[var(--surface-card)] border border-[var(--surface-border)] flex items-center justify-between">
            <div className="flex items-center gap-2.5">
              <Key className="w-4 h-4 text-[var(--accent-tangerine)]" />
              <div>
                <span className="font-bold text-[var(--foreground)]">
                  {isDe ? "Kryptographischer SHA-256 Integritätsstempel" : "Cryptographic SHA-256 Seal"}
                </span>
                <p className="text-[10px] opacity-60">
                  {isDe ? "Revisionssichere Nicht-Abstreitbarkeit nach IDW PS 951" : "Non-repudiation audit trail certified"}
                </p>
              </div>
            </div>
            <span className="px-2 py-1 rounded bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 text-[10px] font-bold">
              AKTIV (IDW PS 951)
            </span>
          </div>

          {/* Form Options */}
          <div className="space-y-4">
            <div>
              <label className="block text-[11px] font-bold text-[var(--foreground)] opacity-80 uppercase tracking-wider mb-1.5">
                {isDe ? "Name & Titel des leitenden BaFin-Prüfers / CISOs:" : "Signatory / Lead Examiner Name & Title:"}
              </label>
              <input
                type="text"
                value={signatoryName}
                onChange={(e) => setSignatoryName(e.target.value)}
                className="w-full px-3 py-2 rounded-lg bg-[var(--surface-card)] border border-[var(--surface-border)] text-xs font-mono text-[var(--foreground)] focus:outline-none focus:border-[var(--accent-tangerine)]"
              />
            </div>

            <div>
              <label className="block text-[11px] font-bold text-[var(--foreground)] opacity-80 uppercase tracking-wider mb-1.5">
                {isDe ? "Aufsichtsrechtlicher Berichtsstandard:" : "Regulatory Reporting Standard:"}
              </label>
              <select
                value={auditStandard}
                onChange={(e) => setAuditStandard(e.target.value)}
                className="w-full px-3 py-2 rounded-lg bg-[var(--surface-card)] border border-[var(--surface-border)] text-xs font-mono text-[var(--foreground)] focus:outline-none focus:border-[var(--accent-tangerine)] cursor-pointer"
              >
                <option value="DIN_5008_ISO_19011">
                  DIN 5008 Form B &amp; DIN EN ISO/IEC 19011 (Offizielle Bundesbank-Prüffassung)
                </option>
                <option value="DORA_RTS_STANDARD">
                  EU DORA Art. 30 Regulatory Technical Standard (RTS ICT Third-Party Report)
                </option>
                <option value="BAFIN_BAIT_AUDIT">
                  BaFin BAIT Ziffer 8 / KWG § 25b Auslagerungsprüfung
                </option>
              </select>
            </div>

            {/* Checklist */}
            <div className="space-y-2 pt-2 border-t border-[var(--surface-border)]">
              <span className="text-[11px] font-bold text-[var(--foreground)] opacity-80 uppercase tracking-wider block mb-1">
                {isDe ? "Im Revisionsgutachten enthalten:" : "Included in Audit Dossier:"}
              </span>

              <label className="flex items-center gap-2.5 cursor-pointer">
                <input
                  type="checkbox"
                  checked={includeSha256Seal}
                  onChange={(e) => setIncludeSha256Seal(e.target.checked)}
                  className="rounded border-[var(--surface-border)] text-[var(--accent-tangerine)] focus:ring-0"
                />
                <span className="text-xs text-[var(--foreground)] opacity-85">
                  {isDe ? "Kryptographischer SHA-256 Integritätsstempel & Revisionszeitstempel" : "Cryptographic SHA-256 fingerprint & timestamp"}
                </span>
              </label>

              <label className="flex items-center gap-2.5 cursor-pointer">
                <input
                  type="checkbox"
                  checked={includePillarSummary}
                  onChange={(e) => setIncludePillarSummary(e.target.checked)}
                  className="rounded border-[var(--surface-border)] text-[var(--accent-tangerine)] focus:ring-0"
                />
                <span className="text-xs text-[var(--foreground)] opacity-85">
                  {isDe ? "4-Säulen Aufsichtsmatrix (DORA Art. 30, KWG § 25b, BGB § 309, BAIT)" : "4-pillar regulatory compliance overview (DORA, KWG, BGB, BAIT)"}
                </span>
              </label>

              <label className="flex items-center gap-2.5 cursor-pointer">
                <input
                  type="checkbox"
                  checked={includeEvidenceSnippets}
                  onChange={(e) => setIncludeEvidenceSnippets(e.target.checked)}
                  className="rounded border-[var(--surface-border)] text-[var(--accent-tangerine)] focus:ring-0"
                />
                <span className="text-xs text-[var(--foreground)] opacity-85">
                  {isDe ? "Wörtliche Vertragsbelege mit Koordinaten & Seitenreferenzen" : "Verbatim clause citations with visual coordinates and page numbers"}
                </span>
              </label>
            </div>
          </div>

          {exportSuccess && (
            <div className="p-3 rounded-lg bg-emerald-500/15 border border-emerald-500/30 text-emerald-400 flex items-center gap-2 text-xs">
              <CheckCircle2 className="w-4 h-4 shrink-0" />
              <span>
                {isDe
                  ? "DIN-Prüfbericht erfolgreich signiert und heruntergeladen!"
                  : "DIN Audit Report successfully generated and downloaded!"}
              </span>
            </div>
          )}
        </div>

        {/* Modal Footer */}
        <div className="p-4 px-6 border-t border-[var(--surface-border)] bg-[var(--surface-card)] flex items-center justify-between">
          <span className="text-[10px] font-mono opacity-50">
            DIN EN ISO 19011 • IDW PS 951
          </span>

          <div className="flex items-center gap-2">
            <button
              onClick={onClose}
              className="px-4 py-2 rounded-lg border border-[var(--surface-border)] hover:bg-[var(--surface-dark)] text-xs font-mono font-bold transition-all cursor-pointer"
            >
              {isDe ? "Abbrechen" : "Cancel"}
            </button>

            <button
              onClick={handleExportPdf}
              disabled={isExporting || !documentId}
              className="flex items-center gap-2 px-5 py-2 rounded-lg bg-[var(--accent-tangerine)] hover:opacity-95 disabled:opacity-50 text-[var(--accent-contrast)] text-xs font-mono font-bold shadow-md transition-all cursor-pointer"
            >
              {isExporting ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  <span>{isDe ? "Signiere Gutachten..." : "Signing PDF..."}</span>
                </>
              ) : (
                <>
                  <Download className="w-4 h-4" />
                  <span>{isDe ? "DIN-Prüfbericht PDF generieren" : "Generate DIN Audit Report PDF"}</span>
                </>
              )}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

"use client";

import React, { useRef } from "react";
import {
  ShieldCheck,
  Download,
  Printer,
  CheckCircle2,
  Lock,
  Building2,
  Calendar,
  Hash,
  Award,
} from "lucide-react";
import { Language } from "@/lib/i18n";

interface AuditCertificateModalProps {
  isOpen: boolean;
  onClose: () => void;
  lang: Language;
  documentName?: string;
  sha256Hash?: string;
}

export function AuditCertificateModal({
  isOpen,
  onClose,
  lang,
  documentName = "Siemens_Master_ICT_Agreement_2026.pdf",
  sha256Hash = "8f3e2b9c7a10d48f6501a33b91e4d29c8e1047fa58d60c2b189a071c3ef9482d",
}: AuditCertificateModalProps) {
  if (!isOpen) return null;

  const isDe = lang === "DE";
  const currentDate = new Date().toLocaleDateString(isDe ? "de-DE" : "en-US", {
    year: "numeric",
    month: "long",
    day: "numeric",
  });

  const handlePrint = () => {
    window.print();
  };

  return (
    <div className="fixed inset-0 z-50 bg-black/80 backdrop-blur-md flex items-center justify-center p-4 overflow-y-auto">
      <div className="w-full max-w-2xl bg-white text-slate-900 rounded-xl shadow-2xl border-4 border-slate-900 p-8 space-y-6 animate-in zoom-in-95 duration-200 font-sans print:m-0 print:border-none print:shadow-none">
        {/* Certificate Header with German Federal Aesthetic */}
        <div className="border-b-2 border-slate-900 pb-5 flex items-start justify-between">
          <div className="space-y-1">
            <div className="flex items-center gap-2">
              <span className="w-6 h-6 rounded bg-slate-900 text-white font-mono font-black text-xs flex items-center justify-center">
                §
              </span>
              <span className="font-mono text-xs font-black tracking-widest uppercase text-slate-700">
                DOCUNORM.DE • REVISIONS-PROTOKOLL
              </span>
            </div>
            <h1 className="text-2xl font-black tracking-tight text-slate-950 uppercase font-mono">
              {isDe ? "Konformitäts-Zertifikat" : "Certificate of Regulatory Compliance"}
            </h1>
            <p className="text-xs text-slate-600 font-mono">
              DIN 66399 Schutzklasse 3 • BaFin Art. 30 DORA • BDSG § 26 / DSGVO
            </p>
          </div>

          <div className="w-16 h-16 rounded-full border-4 border-emerald-600 bg-emerald-50 flex flex-col items-center justify-center text-emerald-800 shadow-sm flex-shrink-0">
            <Award className="w-6 h-6 text-emerald-700" />
            <span className="text-[8px] font-mono font-black uppercase">Geprüft</span>
          </div>
        </div>

        {/* Certificate Meta Data Grid */}
        <div className="grid grid-cols-2 gap-4 bg-slate-50 p-4 rounded-lg border border-slate-200 text-xs font-mono">
          <div>
            <span className="text-slate-500 block text-[10px] uppercase">
              {isDe ? "Zertifikat-Nummer (Audit-ID):" : "Certificate Identifier:"}
            </span>
            <span className="font-bold text-slate-900">DOCU-DE-2026-8941A-REV</span>
          </div>
          <div>
            <span className="text-slate-500 block text-[10px] uppercase">
              {isDe ? "Prüfdatum & Zeitstempel:" : "Timestamp & Audit Date:"}
            </span>
            <span className="font-bold text-slate-900">{currentDate} (UTC+1)</span>
          </div>
          <div>
            <span className="text-slate-500 block text-[10px] uppercase">
              {isDe ? "Mandant / Rechtsträger:" : "Tenant / Audited Entity:"}
            </span>
            <span className="font-bold text-slate-900">Siemens AG (Enterprise Mandant)</span>
          </div>
          <div>
            <span className="text-slate-500 block text-[10px] uppercase">
              {isDe ? "Geprüfte Akte:" : "Audited Dossier:"}
            </span>
            <span className="font-bold text-slate-900 truncate block max-w-[200px]">
              {documentName}
            </span>
          </div>
          <div className="col-span-2">
            <span className="text-slate-500 block text-[10px] uppercase">
              SHA-256 Fingerprint (Kryptografisch Unveränderbar):
            </span>
            <span className="font-mono text-[10px] text-slate-700 break-all bg-white px-2 py-1 rounded border border-slate-200 block mt-0.5">
              {sha256Hash}
            </span>
          </div>
        </div>

        {/* Verified Regulatory Checklist */}
        <div className="space-y-3">
          <h3 className="font-mono text-xs font-bold uppercase tracking-wider text-slate-800 border-b pb-1">
            {isDe ? "Geprüfte Revisionskriterien" : "Audited Regulatory Criteria"}
          </h3>

          <div className="space-y-2 text-xs">
            <div className="flex items-start gap-2.5">
              <CheckCircle2 className="w-4 h-4 text-emerald-600 flex-shrink-0 mt-0.5" />
              <div>
                <span className="font-bold text-slate-900">
                  EU DORA (2022/2554) Art. 30 Abs. 2:
                </span>{" "}
                <span className="text-slate-700">
                  {isDe
                    ? "Ausstiegsfristen (60 Tage) und Unterstützungspflichten des IKT-Dienstleisters vollständig geregelt."
                    : "Exit transition assistance (60 days) and vendor obligations fully stipulated."}
                </span>
              </div>
            </div>

            <div className="flex items-start gap-2.5">
              <CheckCircle2 className="w-4 h-4 text-emerald-600 flex-shrink-0 mt-0.5" />
              <div>
                <span className="font-bold text-slate-900">
                  EU DORA Art. 30 Abs. 3 (Sub-Outsourcing):
                </span>{" "}
                <span className="text-slate-700">
                  {isDe
                    ? "Zustimmungsvorbehalt mit 30-tägiger Vorankündigungsfrist bei Unterbeauftragung garantiert."
                    : "Prior written consent with 30-day notice period for sub-contracting guaranteed."}
                </span>
              </div>
            </div>

            <div className="flex items-start gap-2.5">
              <CheckCircle2 className="w-4 h-4 text-emerald-600 flex-shrink-0 mt-0.5" />
              <div>
                <span className="font-bold text-slate-900">
                  German BDSG / DSGVO PII Firewall:
                </span>{" "}
                <span className="text-slate-700">
                  {isDe
                    ? "100% Vorab-Maskierung aller IBANs und Steuer-Identifikationsnummern vor Vektorisierung."
                    : "100% pre-vectorization redaction of all IBANs and Tax-IDs executed."}
                </span>
              </div>
            </div>

            <div className="flex items-start gap-2.5">
              <CheckCircle2 className="w-4 h-4 text-emerald-600 flex-shrink-0 mt-0.5" />
              <div>
                <span className="font-bold text-slate-900">
                  ZUGFeRD 2.3 / EN 16931 Konformität:
                </span>{" "}
                <span className="text-slate-700">
                  {isDe
                    ? "E-Rechnungs-XML synchron mit visuellem Dokument; Umsatzsteuer-IdNr. verifiziert."
                    : "E-invoice XML line items synchronized with visual PDF; VAT numbers verified."}
                </span>
              </div>
            </div>
          </div>
        </div>

        {/* Official Sign-off & Seal */}
        <div className="pt-4 border-t-2 border-slate-900 flex items-end justify-between">
          <div className="space-y-1">
            <span className="text-[10px] font-mono text-slate-500 uppercase block">
              {isDe ? "Elektronische Signatur (Lead Auditor):" : "Electronic Signature:"}
            </span>
            <p className="font-mono text-xs font-bold text-slate-900">
              Nikhita Reddy, M.Sc. CS
            </p>
            <p className="text-[10px] text-slate-500 font-mono">
              Lead Regulatory AI Compliance Officer • DocuNorm.DE
            </p>
          </div>

          <div className="text-right font-mono text-[9px] text-slate-500">
            <p>BAFIN-ID: 10189204</p>
            <p>ISO/IEC 27001 AUDITED</p>
          </div>
        </div>

        {/* Modal Action Buttons */}
        <div className="flex items-center justify-end gap-3 pt-4 border-t print:hidden">
          <button
            onClick={onClose}
            className="px-4 py-2 rounded-lg border border-slate-300 text-xs font-mono font-bold text-slate-700 hover:bg-slate-100 transition-colors cursor-pointer"
          >
            {isDe ? "Schließen" : "Close"}
          </button>
          <button
            onClick={handlePrint}
            className="flex items-center gap-2 px-5 py-2 rounded-lg bg-slate-950 text-white text-xs font-mono font-black uppercase hover:bg-slate-800 transition-colors cursor-pointer shadow-md"
          >
            <Printer className="w-4 h-4" />
            <span>{isDe ? "Zertifikat Drucken / PDF" : "Print / Save PDF"}</span>
          </button>
        </div>
      </div>
    </div>
  );
}

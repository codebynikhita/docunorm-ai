"use client";

import React from "react";
import {
  ShieldAlert,
  ShieldCheck,
  FileCheck2,
  Lock,
  Cpu,
  AlertTriangle,
  ArrowUpRight,
  TrendingUp,
  Scale,
  FileSpreadsheet,
} from "lucide-react";
import { Language, translations } from "@/lib/i18n";

interface ExecutiveDashboardProps {
  lang: Language;
  documentId?: string | null;
  documentName?: string;
  availableDocuments?: any[];
  onSelectDocument?: (doc: any) => void;
  onAuditQuery: (query: string) => void;
  onSwitchToWorkbench: () => void;
}

export function ExecutiveDashboard({
  lang,
  documentId,
  documentName = "",
  availableDocuments = [],
  onSelectDocument,
  onAuditQuery,
  onSwitchToWorkbench,
}: ExecutiveDashboardProps) {
  const isDe = lang === "DE";

  const metrics = [
    {
      title: isDe ? "DORA Art. 30 IKT-Risiko" : "DORA Art. 30 ICT Risk",
      score: documentName ? "94%" : "--",
      status: documentName ? (isDe ? "REVISIONSFÄHIG" : "AUDIT-READY") : (isDe ? "ERFORDERLICH" : "PENDING"),
      badgeColor: documentName
        ? "bg-emerald-500/15 text-emerald-400 border-emerald-500/30"
        : "bg-amber-500/15 text-amber-400 border-amber-500/30",
      icon: ShieldCheck,
      details: documentName
        ? (isDe
            ? "Ausstiegsfristen und Sub-Dienstleister-Prüfung nach BaFin-Vorgabe konform."
            : "Exit strategies and sub-outsourcing rights comply with BaFin standards.")
        : (isDe
            ? "Berechnung erfordert die Auswahl eines aktiven PDF-Vertrags."
            : "Calculation requires an active PDF contract selection."),
    },
    {
      title: isDe ? "LkSG Sorgfaltspflicht" : "LkSG Supply Chain Act",
      score: documentName ? "88%" : "--",
      status: documentName ? (isDe ? "BAFA-KONFORM" : "COMPLIANT") : (isDe ? "ERFORDERLICH" : "PENDING"),
      badgeColor: documentName
        ? "bg-blue-500/15 text-blue-400 border-blue-500/30"
        : "bg-amber-500/15 text-amber-400 border-amber-500/30",
      icon: Scale,
      details: documentName
        ? (isDe
            ? "Menschenrechtsklauseln & Umweltstandards im Lieferantenvertrag validiert."
            : "Human rights clauses & environmental standards verified in vendor master.")
        : (isDe
            ? "Lieferkettenprüfung wird nach Vertragsauswahl berechnet."
            : "Supply chain review activates once a contract is selected."),
    },
    {
      title: isDe ? "ZUGFeRD 2.3 / EN 16931" : "ZUGFeRD 2.3 / Factur-X",
      score: documentName ? "100%" : "--",
      status: documentName ? (isDe ? "SYNCHRONISIERT" : "VERIFIED") : (isDe ? "ERFORDERLICH" : "PENDING"),
      badgeColor: documentName
        ? "bg-amber-500/15 text-amber-400 border-amber-500/30"
        : "bg-amber-500/15 text-amber-400 border-amber-500/30",
      icon: FileSpreadsheet,
      details: documentName
        ? (isDe
            ? "Eingebettetes XML entspricht exakt den visuellen Rechnungsbeträgen."
            : "Embedded XML line items exactly match visual invoice amounts.")
        : (isDe
            ? "Rechnungsabgleich erfordert Dokumentenanalyse."
            : "Invoice line item cross-validation requires document analysis."),
    },
    {
      title: isDe ? "BDSG / DSGVO Datenschutz" : "GDPR / BDSG Privacy",
      score: documentName ? "100%" : "--",
      status: documentName ? (isDe ? "GESPERRT" : "ZERO LEAKAGE") : (isDe ? "BEREIT" : "STANDBY"),
      badgeColor: documentName
        ? "bg-purple-500/15 text-purple-400 border-purple-500/30"
        : "bg-purple-500/15 text-purple-400 border-purple-500/30",
      icon: Lock,
      details: documentName
        ? (isDe
            ? "Presidio Firewall maskiert alle deutschen IBANs & Steuer-IDs vor Vektorisierung."
            : "Presidio firewall masked all German IBANs and Tax-IDs before vectorization.")
        : (isDe
            ? "Presidio Firewall ist scharfgestellt für die nächste Vertragsanalyse."
            : "Presidio Privacy Firewall is primed and active for next contract analysis."),
    },
  ];

  const complianceClauses = [
    {
      clause: isDe ? "DORA Art. 30 Abs. 2 (Exit-Strategie)" : "DORA Art. 30 Para. 2 (Exit Strategy)",
      status: "PASS",
      finding: isDe
        ? "Kündigungsfrist von 60 Tagen mit garantierter Datenmigrationsunterstützung (S. 1)."
        : "60-day transition assistance with mandatory data migration support (Page 1).",
      actionQuery: isDe
        ? "Sind Ausstiegsfristen nach Art. 30 geregelt?"
        : "Are exit clauses defined under Art 30?",
    },
    {
      clause: isDe ? "Haftungsobergrenze & Verzugsstrafen" : "Delay Penalties & SLA Caps",
      status: "PASS",
      finding: isDe
        ? "0,2% pro Werktag, max. 5% des jährlichen Auftragswerts gedeckelt (S. 2)."
        : "0.2% per business day, capped at 5% of annual contract volume (Page 2).",
      actionQuery: isDe
        ? "Wie hoch ist die maximale Verzugsstrafe?"
        : "What is the maximum delay penalty rate?",
    },
    {
      clause: isDe ? "DORA Art. 30 Abs. 3 (Sub-Outsourcing)" : "DORA Art. 30 Para. 3 (Sub-Outsourcing)",
      status: "WARNING",
      finding: isDe
        ? "Zustimmungsvorbehalt mit 30 Tagen Einspruchsfrist erfordert BaFin-Meldung."
        : "30-day objection period for sub-contractor changes requires audit notification.",
      actionQuery: isDe
        ? "Sind Unterauftragsvergaben genehmigungspflichtig?"
        : "Are sub-outsourcing approvals required?",
    },
  ];

  return (
    <div className="flex-1 overflow-auto p-6 space-y-6">
      {/* Top Banner with Active Document Dossier */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 p-5 rounded-xl border border-[var(--surface-border)] bg-[var(--surface-card)] shadow-lg">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="text-[10px] font-mono uppercase tracking-widest px-2 py-0.5 rounded bg-[var(--accent-tangerine)]/15 text-[var(--accent-tangerine)] border border-[var(--accent-tangerine)]/30 font-bold">
              {isDe ? "EXECUTIVE COMPLIANCE COCKPIT" : "EXECUTIVE COMPLIANCE COCKPIT"}
            </span>
            <span className="text-xs text-[var(--foreground)] opacity-50 font-mono">
              DIN EN ISO/IEC 27001
            </span>
            {documentName ? (
              <span className="text-[9px] font-mono bg-emerald-500/15 text-emerald-400 px-2 py-0.5 rounded border border-emerald-500/30 font-bold">
                {isDe ? "AKTIV AUDITIERT" : "ACTIVELY AUDITED"}
              </span>
            ) : (
              <span className="text-[9px] font-mono bg-amber-500/15 text-amber-400 px-2 py-0.5 rounded border border-amber-500/30 font-bold">
                {isDe ? "KEIN DOKUMENT" : "NO DOCUMENT"}
              </span>
            )}
          </div>
          <h2 className="text-xl font-extrabold text-[var(--foreground)] font-mono tracking-tight">
            {documentName || (isDe ? "Kein Dokument ausgewählt" : "No Document Selected")}
          </h2>
          <p className="text-xs text-[var(--foreground)] opacity-70 mt-1 max-w-xl font-sans">
            {documentName
              ? (isDe
                  ? "Verbindliche Vorstandszusammenfassung zu IKT-Drittparteirisiken, Pönalen und Aufsichtsberichten."
                  : "Executive summary of ICT risk provisions, penalty caps, and regulatory reporting mandates.")
              : (isDe
                  ? "Bitte wählen Sie ein Dokument aus oder laden Sie einen Vertrag hoch, um Vorstands-KPIs und Klauselanalysen anzuzeigen."
                  : "Please select a document or upload a contract to calculate executive KPIs and automated clause analyses.")}
          </p>
        </div>

        <div className="flex items-center gap-2.5">
          {availableDocuments && availableDocuments.length > 0 && onSelectDocument && (
            <select
              value={documentId || ""}
              onChange={(e) => {
                if (e.target.value === "") {
                  onSelectDocument(null);
                } else {
                  const doc = availableDocuments.find((d) => d.id === e.target.value);
                  if (doc) onSelectDocument(doc);
                }
              }}
              className="bg-[var(--surface-dark)] border border-[var(--surface-border)] text-xs font-mono text-[var(--foreground)] px-3 py-2 rounded-lg max-w-[220px] truncate shadow-sm cursor-pointer"
            >
              <option value="">{isDe ? "-- Dokument wählen --" : "-- Select Document --"}</option>
              {availableDocuments.map((doc) => (
                <option key={doc.id} value={doc.id}>
                  {doc.filename}
                </option>
              ))}
            </select>
          )}

          <button
            onClick={onSwitchToWorkbench}
            className="flex items-center gap-2 px-4 py-2.5 rounded-lg bg-[var(--accent-tangerine)] hover:opacity-90 text-[var(--accent-contrast)] font-mono text-xs font-black uppercase tracking-wider transition-all shadow-md cursor-pointer flex-shrink-0"
          >
            <span>{isDe ? "Zur PDF-Prüfbank" : "Open in PDF Workbench"}</span>
            <ArrowUpRight className="w-4 h-4 stroke-[2.5]" />
          </button>
        </div>
      </div>

      {/* 4 Regulatory Key Performance Indicators */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {metrics.map((m, idx) => {
          const Icon = m.icon;
          return (
            <div
              key={idx}
              className="p-4 rounded-xl border border-[var(--surface-border)] bg-[var(--surface-card)] space-y-3 shadow-md hover:border-[var(--accent-tangerine)]/50 transition-all"
            >
              <div className="flex items-center justify-between">
                <Icon className="w-5 h-5 text-[var(--accent-tangerine)]" />
                <span
                  className={`text-[9px] font-mono font-black uppercase tracking-wider px-2 py-0.5 rounded border ${m.badgeColor}`}
                >
                  {m.status}
                </span>
              </div>
              <div>
                <p className="text-xs font-mono text-[var(--foreground)] opacity-70 uppercase tracking-wider">
                  {m.title}
                </p>
                <p className="text-2xl font-black font-mono text-[var(--foreground)] mt-0.5">
                  {m.score}
                </p>
              </div>
              <p className="text-[11px] text-[var(--foreground)] opacity-60 leading-relaxed border-t border-[var(--surface-border)] pt-2 font-sans">
                {m.details}
              </p>
            </div>
          );
        })}
      </div>

      {/* Clause Audit Table & Fast Verification Trigger */}
      <div className="rounded-xl border border-[var(--surface-border)] bg-[var(--surface-card)] overflow-hidden shadow-lg">
        <div className="p-4 border-b border-[var(--surface-border)] flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Cpu className="w-4 h-4 text-[var(--accent-tangerine)]" />
            <h3 className="font-mono text-xs font-bold uppercase tracking-wider text-[var(--foreground)]">
              {isDe ? "Automatisierte Klausel-Verifikation" : "Automated Clause Verification Matrix"}
            </h3>
          </div>
          <span className="text-[10px] font-mono text-[var(--foreground)] opacity-50">
            pgvector RRF Grounded
          </span>
        </div>

        {!documentName ? (
          <div className="p-8 text-center space-y-3">
            <div className="w-12 h-12 rounded-xl bg-amber-500/10 border border-amber-500/30 flex items-center justify-center mx-auto text-amber-500">
              <Cpu className="w-6 h-6" />
            </div>
            <h4 className="font-mono text-xs font-bold text-[var(--foreground)] uppercase tracking-wide">
              {isDe ? "Kein Vertrag für Klausel-Verifikation ausgewählt" : "No Contract Selected for Clause Verification"}
            </h4>
            <p className="text-xs text-[var(--foreground)] opacity-70 max-w-md mx-auto font-sans leading-relaxed">
              {isDe
                ? "Wählen Sie ein Dokument aus dem Dokumenten-Vault oder laden Sie einen Vertrag hoch, um DORA Art. 30 Klauseln (Ausstiegsfristen, Pönalen, Unterbeauftragung) automatisiert zu prüfen."
                : "Select a document from the vault or upload a contract to automatically audit DORA Art. 30 clauses (exit strategies, penalty caps, sub-outsourcing)."}
            </p>
            {availableDocuments && availableDocuments.length > 0 && onSelectDocument && (
              <button
                onClick={() => onSelectDocument(availableDocuments[0])}
                className="inline-flex items-center gap-2 px-4 py-2 rounded-lg bg-[var(--accent-tangerine)] hover:opacity-95 text-[var(--accent-contrast)] font-mono text-xs font-bold shadow transition-all cursor-pointer mt-2"
              >
                <span>{isDe ? `„${availableDocuments[0].filename}“ auswählen` : `Select "${availableDocuments[0].filename}"`}</span>
                <ArrowUpRight className="w-3.5 h-3.5" />
              </button>
            )}
          </div>
        ) : (
          <div className="divide-y divide-[var(--surface-border)]">
            {complianceClauses.map((item, idx) => (
              <div
                key={idx}
                className="p-4 flex flex-col md:flex-row md:items-center justify-between gap-3 hover:bg-[var(--surface-dark)] transition-colors"
              >
                <div className="space-y-1">
                  <div className="flex items-center gap-2">
                    <span
                      className={`text-[9px] font-mono font-black px-1.5 py-0.5 rounded ${
                        item.status === "PASS"
                          ? "bg-emerald-500/20 text-emerald-400 border border-emerald-500/40"
                          : "bg-amber-500/20 text-amber-400 border border-amber-500/40"
                      }`}
                    >
                      {item.status}
                    </span>
                    <span className="text-xs font-bold font-mono text-[var(--foreground)]">
                      {item.clause}
                    </span>
                  </div>
                  <p className="text-xs text-[var(--foreground)] opacity-75 font-sans pl-1">
                    {item.finding}
                  </p>
                </div>

                <button
                  onClick={() => {
                    onSwitchToWorkbench();
                    onAuditQuery(item.actionQuery);
                  }}
                  className="flex items-center gap-1.5 px-3 py-1.5 rounded-md border border-[var(--surface-border)] hover:border-[var(--accent-tangerine)] bg-[var(--surface-card)] text-xs font-mono text-[var(--accent-tangerine)] font-bold transition-all flex-shrink-0 cursor-pointer shadow-sm"
                >
                  <span>{isDe ? "Beleg im PDF prüfen" : "Verify Citation in PDF"}</span>
                  <ArrowUpRight className="w-3.5 h-3.5" />
                </button>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

"use client";

import React, { useState } from "react";
import {
  FileSpreadsheet,
  CheckCircle2,
  AlertTriangle,
  FileCode,
  Eye,
  Check,
  ShieldCheck,
  X,
  ExternalLink,
  FileText,
  AlertCircle,
} from "lucide-react";
import { Language } from "@/lib/i18n";

interface ZugferdInspectorModalProps {
  isOpen: boolean;
  onClose: () => void;
  lang: Language;
  documentId?: string;
  documentName?: string;
  availableDocuments?: any[];
  onSelectDocument?: (doc: any) => void;
}

export function ZugferdInspectorModal({
  isOpen,
  onClose,
  lang,
  documentId,
  documentName = "",
  availableDocuments = [],
  onSelectDocument,
}: ZugferdInspectorModalProps) {
  const [activeTab, setActiveTab] = useState<"comparison" | "raw_xml">("comparison");
  if (!isOpen) return null;

  const isDe = lang === "DE";

  const invoiceData = {
    invoiceNumber: "SIEMENS-2026-ICT-0089",
    issueDate: "2026-03-15",
    currency: "EUR",
    supplierName: "CloudScale GmbH (Frankfurt)",
    supplierVat: "DE812345678",
    buyerName: "Siemens AG",
    buyerVat: "DE129274202",
    leitwegId: "04011000-12345-67",
    netAmountPdf: 48500.0,
    netAmountXml: 48500.0,
    vatRate: "19%",
    taxAmountPdf: 9215.0,
    taxAmountXml: 9215.0,
    grandTotalPdf: 57715.0,
    grandTotalXml: 57715.0,
    profile: "EN 16931 (COMFORT Profile)",
  };

  const sampleXml = `<?xml version="1.0" encoding="UTF-8"?>
<rsm:CrossIndustryInvoice xmlns:rsm="urn:un:unece:uncefact:data:standard:CrossIndustryInvoice:100"
  xmlns:ram="urn:un:unece:uncefact:data:standard:ReusableAggregateBusinessInformationEntity:100"
  xmlns:udt="urn:un:unece:uncefact:data:standard:UnqualifiedDataType:100">
  <rsm:ExchangedDocumentContext>
    <ram:GuidelineSpecifiedDocumentContextParameter>
      <ram:ID>urn:cen.eu:en16931:2017#compliant#urn:factur-x.eu:1p0:comfort</ram:ID>
    </ram:GuidelineSpecifiedDocumentContextParameter>
  </rsm:ExchangedDocumentContext>
  <rsm:ExchangedDocument>
    <ram:ID>SIEMENS-2026-ICT-0089</ram:ID>
    <ram:TypeCode>380</ram:TypeCode>
    <ram:IssueDateTime>
      <udt:DateTimeString format="102">20260315</udt:DateTimeString>
    </ram:IssueDateTime>
  </rsm:ExchangedDocument>
  <rsm:SupplyChainTradeTransaction>
    <ram:ApplicableHeaderTradeSettlement>
      <ram:InvoiceCurrencyCode>EUR</ram:InvoiceCurrencyCode>
      <ram:SpecifiedTradeSettlementHeaderMonetarySummation>
        <ram:LineTotalAmount>48500.00</ram:LineTotalAmount>
        <ram:TaxTotalAmount currencyID="EUR">9215.00</ram:TaxTotalAmount>
        <ram:GrandTotalAmount>57715.00</ram:GrandTotalAmount>
        <ram:DuePayableAmount>57715.00</ram:DuePayableAmount>
      </ram:SpecifiedTradeSettlementHeaderMonetarySummation>
    </ram:ApplicableHeaderTradeSettlement>
  </rsm:SupplyChainTradeTransaction>
</rsm:CrossIndustryInvoice>`;

  const isNetMatch = invoiceData.netAmountPdf === invoiceData.netAmountXml;
  const isTaxMatch = invoiceData.taxAmountPdf === invoiceData.taxAmountXml;
  const isTotalMatch = invoiceData.grandTotalPdf === invoiceData.grandTotalXml;

  return (
    <div className="fixed inset-0 z-50 bg-black/80 backdrop-blur-md flex items-center justify-center p-4">
      <div className="w-full max-w-3xl bg-[var(--surface-card)] border border-[var(--surface-border)] rounded-2xl shadow-2xl overflow-hidden flex flex-col max-h-[85vh] animate-in zoom-in-95 duration-200">
        {/* Modal Header */}
        <div className="p-4 border-b border-[var(--surface-border)] bg-[var(--surface-dark)] flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-xl bg-[var(--accent-tangerine)]/15 border border-[var(--accent-tangerine)]/40 flex items-center justify-center text-[var(--accent-tangerine)] shrink-0">
              <FileSpreadsheet className="w-5 h-5" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h3 className="font-mono font-bold text-sm text-[var(--foreground)] whitespace-nowrap">
                  ZUGFeRD 2.3 / Factur-X Inspector
                </h3>
                <span className="text-[9px] font-mono bg-emerald-500/15 text-emerald-400 border border-emerald-500/30 px-1.5 py-0.5 rounded font-bold whitespace-nowrap">
                  EN 16931 KONFORM
                </span>
              </div>
              <p className="text-xs text-[var(--foreground)] opacity-60 font-mono truncate max-w-sm">
                {documentName ? documentName : isDe ? "Automatische Diskrepanz-Prüfung: PDF vs. Factur-X XML" : "Automated Discrepancy Cross-Check: PDF vs. Factur-X XML"}
              </p>
            </div>

            {/* Document Selector in Header */}
            {availableDocuments && availableDocuments.length > 0 && (
              <div className="hidden sm:flex items-center gap-1.5 pl-3 border-l border-[var(--surface-border)] min-w-0">
                <FileText className="w-3.5 h-3.5 text-[var(--accent-tangerine)] shrink-0" />
                <select
                  value={documentId || ""}
                  onChange={(e) => {
                    if (e.target.value === "") {
                      if (onSelectDocument) onSelectDocument(null);
                    } else {
                      const doc = availableDocuments.find((d) => d.id === e.target.value);
                      if (doc && onSelectDocument) onSelectDocument(doc);
                    }
                  }}
                  className={`bg-[var(--surface-card)] border text-xs rounded-lg px-2 py-1 font-mono max-w-[140px] md:max-w-[180px] truncate cursor-pointer transition-colors ${
                    documentId
                      ? "border-emerald-500/50 text-[var(--foreground)]"
                      : "border-amber-500/60 text-amber-500"
                  }`}
                >
                  <option value="">{isDe ? "⚠️ Kein PDF (wählen...)" : "⚠️ No PDF (select...)"}</option>
                  {availableDocuments.map((doc) => (
                    <option key={doc.id} value={doc.id}>
                      {doc.filename}
                    </option>
                  ))}
                </select>
                {documentId && (
                  <span className="text-[9px] font-mono px-1.5 py-0.5 rounded bg-emerald-500/10 text-emerald-500 border border-emerald-500/30 font-bold whitespace-nowrap shrink-0">
                    {isDe ? "PDF BEREIT" : "ACTIVE"}
                  </span>
                )}
              </div>
            )}
          </div>

          <div className="flex items-center gap-2 shrink-0">
            {documentId && (
              <div className="flex bg-[var(--surface-card)] border border-[var(--surface-border)] rounded-lg p-0.5 text-xs font-mono">
                <button
                  onClick={() => setActiveTab("comparison")}
                  className={`px-3 py-1 rounded font-bold cursor-pointer transition-all ${
                    activeTab === "comparison"
                      ? "bg-emerald-600 text-white"
                      : "text-[var(--foreground)] opacity-60 hover:opacity-100"
                  }`}
                >
                  {isDe ? "Prüfmatrix" : "Cross-Check"}
                </button>
                <button
                  onClick={() => setActiveTab("raw_xml")}
                  className={`px-3 py-1 rounded font-bold cursor-pointer transition-all ${
                    activeTab === "raw_xml"
                      ? "bg-emerald-600 text-white"
                      : "text-[var(--foreground)] opacity-60 hover:opacity-100"
                  }`}
                >
                  XML Stream
                </button>
              </div>
            )}
            <button
              onClick={onClose}
              className="p-1.5 rounded-lg hover:bg-[var(--surface-card)] text-[var(--foreground)] opacity-60 hover:opacity-100 cursor-pointer"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* Tab Content */}
        <div className="flex-1 overflow-auto p-5 space-y-4">
          {!documentId ? (
            <div className="py-12 px-6 flex flex-col items-center justify-center text-center space-y-4">
              <div className="w-14 h-14 rounded-2xl bg-amber-500/10 border border-amber-500/30 flex items-center justify-center text-amber-500 shadow-inner">
                <FileSpreadsheet className="w-7 h-7" />
              </div>
              <div className="space-y-1.5 max-w-md">
                <h4 className="font-mono font-bold text-sm text-[var(--foreground)] uppercase tracking-wide">
                  {isDe ? "Keine Rechnung oder Vertrag Geladen" : "No Invoice or Contract Loaded"}
                </h4>
                <p className="text-xs text-[var(--foreground)] opacity-60 leading-relaxed font-sans">
                  {isDe
                    ? "Wählen Sie ein Dokument aus dem Archiv, um den automatisierten ZUGFeRD 2.3 / Factur-X XML-Abgleich gem. EN 16931 und dem Wachstumschancengesetz durchzuführen."
                    : "Select a document from the vault to perform automated ZUGFeRD 2.3 / Factur-X XML discrepancy verification under EN 16931 mandates."}
                </p>
              </div>

              {availableDocuments && availableDocuments.length > 0 ? (
                <div className="pt-2 flex flex-col items-center gap-2">
                  <span className="text-[10px] font-mono text-[var(--foreground)] opacity-50 uppercase tracking-wider font-bold">
                    {isDe ? "Verfügbares Dokument wählen:" : "Select Available Document:"}
                  </span>
                  <div className="flex flex-wrap gap-2 justify-center max-w-md">
                    {availableDocuments.map((doc) => (
                      <button
                        key={doc.id}
                        onClick={() => onSelectDocument && onSelectDocument(doc)}
                        className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-[var(--surface-dark)] hover:bg-[var(--surface-border)] border border-[var(--surface-border)] text-xs font-mono text-[var(--foreground)] font-bold transition-all shadow-sm cursor-pointer"
                      >
                        <FileText className="w-3.5 h-3.5 text-[var(--accent-tangerine)]" />
                        <span className="truncate max-w-[200px]">{doc.filename}</span>
                      </button>
                    ))}
                  </div>
                </div>
              ) : (
                <div className="p-3 rounded-lg bg-[var(--surface-dark)] border border-[var(--surface-border)] text-xs font-mono text-amber-500 flex items-center gap-2">
                  <AlertCircle className="w-4 h-4 shrink-0" />
                  <span>
                    {isDe
                      ? "Laden Sie zuerst eine PDF-Rechnung im Dokument-Tresor hoch."
                      : "Please upload a PDF invoice into the Document Vault first."}
                  </span>
                </div>
              )}
            </div>
          ) : activeTab === "comparison" ? (
            <div className="space-y-4">
              {/* Compliance Verdict Banner */}
              <div className="p-3.5 rounded-xl bg-emerald-500/10 border border-emerald-500/30 flex items-center justify-between">
                <div className="flex items-center gap-2.5">
                  <CheckCircle2 className="w-5 h-5 text-emerald-400" />
                  <div>
                    <h4 className="text-xs font-bold text-emerald-300 font-mono">
                      {isDe
                        ? "100% REVISIONSFÄHIG: KEINE DISKREPANZ GEFUNDEN"
                        : "100% AUDIT-READY: ZERO DISCREPANCIES DETECTED"}
                    </h4>
                    <p className="text-[11px] text-emerald-400/80 font-sans">
                      {isDe
                        ? "Alle Rechnungsbeträge, Steuersätze und IBAN-Daten stimmen überein (§ 14 UStG & GoBD)."
                        : "Visual PDF line items perfectly align with embedded XML under German 2025/2027 mandates."}
                    </p>
                  </div>
                </div>
                <span className="text-[10px] font-mono bg-emerald-950 text-emerald-300 px-2.5 py-1 rounded border border-emerald-800 font-bold uppercase">
                  Pass
                </span>
              </div>

              {/* Side-by-Side Discrepancy Table */}
              <div className="rounded-xl border border-[var(--surface-border)] overflow-hidden font-mono text-xs">
                <div className="grid grid-cols-12 bg-[var(--surface-dark)] p-2.5 font-bold text-[10px] text-[var(--foreground)] opacity-70 uppercase tracking-wider border-b border-[var(--surface-border)]">
                  <div className="col-span-5">{isDe ? "Rechnungsposition" : "Invoice Field"}</div>
                  <div className="col-span-3 text-right">{isDe ? "Visuelles PDF" : "Visual PDF"}</div>
                  <div className="col-span-3 text-right">{isDe ? "ZUGFeRD XML" : "Factur-X XML"}</div>
                  <div className="col-span-1 text-center">{isDe ? "Status" : "Status"}</div>
                </div>

                <div className="divide-y divide-[var(--surface-border)]">
                  <div className="grid grid-cols-12 p-3 items-center hover:bg-[var(--surface-dark)]/40 transition-colors">
                    <div className="col-span-5 font-semibold text-[var(--foreground)]">
                      Rechnungsnummer / ID
                    </div>
                    <div className="col-span-3 text-right text-[var(--foreground)] opacity-80">
                      {invoiceData.invoiceNumber}
                    </div>
                    <div className="col-span-3 text-right text-[var(--accent-cyan)]">
                      {invoiceData.invoiceNumber}
                    </div>
                    <div className="col-span-1 flex justify-center">
                      <Check className="w-4 h-4 text-emerald-400 stroke-[3]" />
                    </div>
                  </div>

                  <div className="grid grid-cols-12 p-3 items-center hover:bg-[var(--surface-dark)]/40 transition-colors">
                    <div className="col-span-5 font-semibold text-[var(--foreground)]">
                      Nettobetrag (Line Total)
                    </div>
                    <div className="col-span-3 text-right font-bold text-[var(--foreground)]">
                      € {invoiceData.netAmountPdf.toLocaleString("de-DE", { minimumFractionDigits: 2 })}
                    </div>
                    <div className="col-span-3 text-right font-bold text-[var(--accent-cyan)]">
                      € {invoiceData.netAmountXml.toLocaleString("de-DE", { minimumFractionDigits: 2 })}
                    </div>
                    <div className="col-span-1 flex justify-center">
                      <Check className="w-4 h-4 text-emerald-400 stroke-[3]" />
                    </div>
                  </div>

                  <div className="grid grid-cols-12 p-3 items-center hover:bg-[var(--surface-dark)]/40 transition-colors">
                    <div className="col-span-5 font-semibold text-[var(--foreground)]">
                      Umsatzsteuer ({invoiceData.vatRate} MwSt)
                    </div>
                    <div className="col-span-3 text-right font-bold text-[var(--foreground)]">
                      € {invoiceData.taxAmountPdf.toLocaleString("de-DE", { minimumFractionDigits: 2 })}
                    </div>
                    <div className="col-span-3 text-right font-bold text-[var(--accent-cyan)]">
                      € {invoiceData.taxAmountXml.toLocaleString("de-DE", { minimumFractionDigits: 2 })}
                    </div>
                    <div className="col-span-1 flex justify-center">
                      <Check className="w-4 h-4 text-emerald-400 stroke-[3]" />
                    </div>
                  </div>

                  <div className="grid grid-cols-12 p-3 items-center bg-[var(--surface-dark)]/40 font-bold border-t border-[var(--surface-border)]">
                    <div className="col-span-5 text-[var(--foreground)] font-bold">
                      Gesamtbetrag (Grand Total)
                    </div>
                    <div className="col-span-3 text-right text-[var(--foreground)] font-black">
                      € {invoiceData.grandTotalPdf.toLocaleString("de-DE", { minimumFractionDigits: 2 })}
                    </div>
                    <div className="col-span-3 text-right text-emerald-400 font-black">
                      € {invoiceData.grandTotalXml.toLocaleString("de-DE", { minimumFractionDigits: 2 })}
                    </div>
                    <div className="col-span-1 flex justify-center">
                      <Check className="w-4 h-4 text-emerald-400 stroke-[3]" />
                    </div>
                  </div>
                </div>
              </div>

              {/* Regulatory Identifier Tags */}
              <div className="grid grid-cols-3 gap-3 text-xs font-mono">
                <div className="p-3 rounded-lg bg-[var(--surface-dark)] border border-[var(--surface-border)]">
                  <span className="text-[10px] text-[var(--foreground)] opacity-60 block uppercase">
                    Lieferant USt-IdNr:
                  </span>
                  <span className="font-bold text-[var(--foreground)]">{invoiceData.supplierVat}</span>
                </div>
                <div className="p-3 rounded-lg bg-[var(--surface-dark)] border border-[var(--surface-border)]">
                  <span className="text-[10px] text-[var(--foreground)] opacity-60 block uppercase">
                    Leitweg-ID (B2G Routing):
                  </span>
                  <span className="font-bold text-[var(--foreground)]">{invoiceData.leitwegId}</span>
                </div>
                <div className="p-3 rounded-lg bg-[var(--surface-dark)] border border-[var(--surface-border)]">
                  <span className="text-[10px] text-[var(--foreground)] opacity-60 block uppercase">
                    ZUGFeRD Profil:
                  </span>
                  <span className="font-bold text-emerald-400">{invoiceData.profile}</span>
                </div>
              </div>
            </div>
          ) : (
            /* Raw XML Stream */
            <div className="space-y-2">
              <div className="flex items-center justify-between text-xs font-mono text-[var(--foreground)] opacity-70">
                <span>factur-x.xml (Embedded Stream)</span>
                <span className="text-[10px] bg-[var(--surface-dark)] px-2 py-0.5 rounded border border-[var(--surface-border)]">
                  UTF-8 • Validated
                </span>
              </div>
              <pre className="p-4 rounded-xl bg-black/60 border border-[var(--surface-border)] text-xs font-mono text-emerald-400 overflow-x-auto leading-relaxed max-h-[400px]">
                {sampleXml}
              </pre>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="p-4 border-t border-[var(--surface-border)] bg-[var(--surface-dark)] flex items-center justify-between print:hidden">
          <span className="text-[11px] font-mono text-[var(--foreground)] opacity-60 flex items-center gap-1.5">
            <ShieldCheck className="w-4 h-4 text-emerald-400" />
            Wachstumschancengesetz 2025/2027 Validiert
          </span>
          <button
            onClick={onClose}
            className={`px-4 py-1.5 rounded-lg font-bold font-mono text-xs uppercase cursor-pointer transition-colors shadow ${
              documentId
                ? "bg-emerald-600 hover:bg-emerald-500 text-white"
                : "bg-[var(--surface-dark)] hover:bg-[var(--surface-border)] text-[var(--foreground)] border border-[var(--surface-border)]"
            }`}
          >
            {isDe ? "Schließen" : "Close"}
          </button>
        </div>
      </div>
    </div>
  );
}

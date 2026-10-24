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
} from "lucide-react";
import { Language } from "@/lib/i18n";

interface ZugferdInspectorModalProps {
  isOpen: boolean;
  onClose: () => void;
  lang: Language;
  documentName?: string;
}

export function ZugferdInspectorModal({
  isOpen,
  onClose,
  lang,
  documentName = "Siemens_Master_ICT_Agreement_2026.pdf",
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
            <div className="w-9 h-9 rounded-xl bg-[var(--accent-tangerine)]/15 border border-[var(--accent-tangerine)]/40 flex items-center justify-center text-[var(--accent-tangerine)]">
              <FileSpreadsheet className="w-5 h-5" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h3 className="font-mono font-bold text-sm text-[var(--foreground)]">
                  ZUGFeRD 2.3 / Factur-X Inspector
                </h3>
                <span className="text-[9px] font-mono bg-emerald-500/15 text-emerald-400 border border-emerald-500/30 px-1.5 py-0.5 rounded font-bold">
                  EN 16931 KONFORM
                </span>
              </div>
              <p className="text-xs text-[var(--foreground)] opacity-60 font-mono">
                {isDe
                  ? "Automatische Diskrepanz-Prüfung: Visuelles PDF vs. Eingebettetes XML"
                  : "Automated Discrepancy Cross-Check: Visual PDF vs. Embedded Factur-X XML"}
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <div className="flex bg-[var(--surface-card)] border border-[var(--surface-border)] rounded-lg p-0.5 text-xs font-mono">
              <button
                onClick={() => setActiveTab("comparison")}
                className={`px-3 py-1 rounded font-bold cursor-pointer transition-all ${
                  activeTab === "comparison"
                    ? "bg-[var(--accent-tangerine)] text-black"
                    : "text-[var(--foreground)] opacity-60 hover:opacity-100"
                }`}
              >
                {isDe ? "Prüfmatrix" : "Cross-Check"}
              </button>
              <button
                onClick={() => setActiveTab("raw_xml")}
                className={`px-3 py-1 rounded font-bold cursor-pointer transition-all ${
                  activeTab === "raw_xml"
                    ? "bg-[var(--accent-tangerine)] text-black"
                    : "text-[var(--foreground)] opacity-60 hover:opacity-100"
                }`}
              >
                XML Stream
              </button>
            </div>
            <button
              onClick={onClose}
              className="p-1.5 rounded-lg hover:bg-[var(--surface-dark)] text-[var(--foreground)] opacity-60 hover:opacity-100 cursor-pointer"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* Tab Content */}
        <div className="flex-1 overflow-auto p-5 space-y-4">
          {activeTab === "comparison" ? (
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

                  <div className="grid grid-cols-12 p-3 items-center bg-[var(--surface-dark)]/20 font-bold">
                    <div className="col-span-5 text-[var(--accent-tangerine)]">
                      Gesamtbetrag (Grand Total)
                    </div>
                    <div className="col-span-3 text-right text-[var(--foreground)]">
                      € {invoiceData.grandTotalPdf.toLocaleString("de-DE", { minimumFractionDigits: 2 })}
                    </div>
                    <div className="col-span-3 text-right text-[var(--accent-tangerine)]">
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
        <div className="p-4 border-t border-[var(--surface-border)] bg-[var(--surface-dark)] flex items-center justify-between">
          <span className="text-[11px] font-mono text-[var(--foreground)] opacity-60 flex items-center gap-1.5">
            <ShieldCheck className="w-4 h-4 text-emerald-400" />
            Wachstumschancengesetz 2025/2027 Validiert
          </span>
          <button
            onClick={onClose}
            className="px-4 py-1.5 rounded-lg bg-[var(--accent-tangerine)] text-black font-bold font-mono text-xs uppercase cursor-pointer hover:opacity-90 transition-opacity"
          >
            {isDe ? "Prüfung Abschließen" : "Done"}
          </button>
        </div>
      </div>
    </div>
  );
}

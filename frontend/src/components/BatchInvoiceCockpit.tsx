"use client";

import React, { useEffect, useState } from "react";
import {
  AlertCircle,
  Archive,
  ArrowRight,
  Building2,
  CheckCircle2,
  ChevronDown,
  ChevronRight,
  Code2,
  Copy,
  Download,
  FileCheck,
  FileSpreadsheet,
  FileText,
  Layers,
  Play,
  RefreshCw,
  Scale,
  Settings2,
  Upload,
  XCircle,
} from "lucide-react";
import {
  batchIngestInvoices,
  BatchIngestionSummary,
  BatchInvoiceProcessingItem,
  ChartOfAccounts,
  downloadDatevCsv,
  downloadSapJson,
  getSampleBatchSummary,
} from "@/lib/api";

interface BatchInvoiceCockpitProps {
  onClose?: () => void;
  onSelectInvoice?: (invoice: BatchInvoiceProcessingItem) => void;
}

export function BatchInvoiceCockpit({
  onClose,
  onSelectInvoice,
}: BatchInvoiceCockpitProps) {
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [summary, setSummary] = useState<BatchIngestionSummary | null>(null);

  // Configuration State
  const [chartOfAccounts, setChartOfAccounts] = useState<ChartOfAccounts>("SKR03");
  const [beraternummer, setBeraternummer] = useState<number>(1001);
  const [mandantennummer, setMandantennummer] = useState<number>(70001);
  const [companyCode, setCompanyCode] = useState<string>("1000");

  // UI Tabs: "batch" | "datev" | "sap"
  const [activeTab, setActiveTab] = useState<"batch" | "datev" | "sap">("batch");
  const [expandedInvoiceIdx, setExpandedInvoiceIdx] = useState<number | null>(null);
  const [uploading, setUploading] = useState<boolean>(false);
  const [copiedDatev, setCopiedDatev] = useState<boolean>(false);
  const [copiedSap, setCopiedSap] = useState<boolean>(false);
  const [downloadingDatev, setDownloadingDatev] = useState<boolean>(false);
  const [downloadingSap, setDownloadingSap] = useState<boolean>(false);

  // Load sample batch initially
  const loadBatch = async (
    chart: ChartOfAccounts = chartOfAccounts,
    bNum: number = beraternummer,
    mNum: number = mandantennummer,
    cCode: string = companyCode,
  ) => {
    try {
      setLoading(true);
      setError(null);
      const res = await getSampleBatchSummary(chart, bNum, mNum, cCode);
      setSummary(res);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Fehler beim Laden des Buchungsstapels.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadBatch();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const handleChartChange = (newChart: ChartOfAccounts) => {
    setChartOfAccounts(newChart);
    loadBatch(newChart, beraternummer, mandantennummer, companyCode);
  };

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    try {
      setUploading(true);
      setError(null);
      const res = await batchIngestInvoices(
        file,
        chartOfAccounts,
        beraternummer,
        mandantennummer,
        companyCode,
      );
      setSummary(res);
      setActiveTab("batch");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Batch-Verarbeitung fehlgeschlagen.");
    } finally {
      setUploading(false);
    }
  };

  const handleCopyDatev = () => {
    if (summary?.datev_csv_content) {
      navigator.clipboard.writeText(summary.datev_csv_content);
      setCopiedDatev(true);
      setTimeout(() => setCopiedDatev(false), 2000);
    }
  };

  const handleCopySap = () => {
    if (summary?.sap_json_content) {
      navigator.clipboard.writeText(summary.sap_json_content);
      setCopiedSap(true);
      setTimeout(() => setCopiedSap(false), 2000);
    }
  };

  const handleDownloadDatev = async () => {
    try {
      setDownloadingDatev(true);
      await downloadDatevCsv(chartOfAccounts, beraternummer, mandantennummer);
    } catch (err) {
      setError(err instanceof Error ? err.message : "DATEV Download fehlgeschlagen.");
    } finally {
      setDownloadingDatev(false);
    }
  };

  const handleDownloadSap = async () => {
    try {
      setDownloadingSap(true);
      await downloadSapJson(companyCode, 2026);
    } catch (err) {
      setError(err instanceof Error ? err.message : "SAP Download fehlgeschlagen.");
    } finally {
      setDownloadingSap(false);
    }
  };

  return (
    <div className="flex flex-col h-full bg-slate-950 text-slate-100 overflow-hidden font-sans">
      {/* Top Header Bar */}
      <div className="flex items-center justify-between px-6 py-4 border-b border-slate-800 bg-slate-900/80 backdrop-blur-md shrink-0">
        <div className="flex items-center space-x-3">
          <div className="p-2 rounded-lg bg-emerald-500/10 border border-emerald-500/30 text-emerald-400">
            <Archive className="w-5 h-5" />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <h2 className="text-base font-semibold tracking-tight text-white">
                ZUGFeRD 2027 ERP &amp; Buchungsstapel-Bridge
              </h2>
              <span className="px-2 py-0.5 text-xs font-mono font-medium rounded-full bg-emerald-500/15 border border-emerald-500/30 text-emerald-300">
                DATEV 700 &amp; SAP S/4HANA
              </span>
            </div>
            <p className="text-xs text-slate-400">
              High-Throughput Batch-Ingestion, Kontenmapping &amp; GoBD-Export (§§ 146, 147 AO)
            </p>
          </div>
        </div>

        <div className="flex items-center space-x-3">
          {/* Quick Chart of Accounts Switcher */}
          <div className="flex items-center bg-slate-900 border border-slate-700/80 rounded-lg p-0.5 text-xs">
            <button
              onClick={() => handleChartChange("SKR03")}
              className={`px-2.5 py-1 rounded font-mono font-medium transition-colors ${
                chartOfAccounts === "SKR03"
                  ? "bg-emerald-600 text-white"
                  : "text-slate-400 hover:text-slate-200"
              }`}
            >
              SKR03
            </button>
            <button
              onClick={() => handleChartChange("SKR04")}
              className={`px-2.5 py-1 rounded font-mono font-medium transition-colors ${
                chartOfAccounts === "SKR04"
                  ? "bg-emerald-600 text-white"
                  : "text-slate-400 hover:text-slate-200"
              }`}
            >
              SKR04
            </button>
            <button
              onClick={() => handleChartChange("IKR")}
              className={`px-2.5 py-1 rounded font-mono font-medium transition-colors ${
                chartOfAccounts === "IKR"
                  ? "bg-emerald-600 text-white"
                  : "text-slate-400 hover:text-slate-200"
              }`}
            >
              IKR
            </button>
          </div>

          {/* Upload Button */}
          <label className="inline-flex items-center px-3 py-1.5 rounded-lg text-xs font-medium bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 cursor-pointer shadow-sm transition-colors">
            <Upload className="w-3.5 h-3.5 mr-1.5 text-cyan-400" />
            <span>{uploading ? "Verarbeite..." : "ZIP / Stapel Ingest"}</span>
            <input
              type="file"
              accept=".zip,.xml,.pdf"
              onChange={handleFileUpload}
              disabled={uploading}
              className="hidden"
            />
          </label>

          {/* Refresh Sample Batch */}
          <button
            onClick={() => loadBatch()}
            disabled={loading}
            className="p-1.5 rounded-lg text-slate-400 hover:text-white bg-slate-800 hover:bg-slate-700 transition-colors"
            title="Musterstapel neu laden"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? "animate-spin text-emerald-400" : ""}`} />
          </button>

          {onClose && (
            <button
              onClick={onClose}
              className="px-3 py-1.5 text-xs font-medium text-slate-400 hover:text-white bg-slate-800 hover:bg-slate-700 rounded-md transition-colors"
            >
              Schließen
            </button>
          )}
        </div>
      </div>

      {loading && !summary ? (
        <div className="flex flex-col items-center justify-center flex-1 space-y-4">
          <RefreshCw className="w-8 h-8 text-emerald-400 animate-spin" />
          <p className="text-sm text-slate-400 font-mono">
            Generiere DATEV Buchungsstapel &amp; berechne Kontenmapping...
          </p>
        </div>
      ) : error ? (
        <div className="p-6">
          <div className="p-4 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-300 flex items-start space-x-3">
            <XCircle className="w-5 h-5 flex-shrink-0 mt-0.5" />
            <div>
              <h4 className="font-semibold text-sm">Batch-Verarbeitungsfehler</h4>
              <p className="text-xs text-rose-200/80 mt-1">{error}</p>
            </div>
          </div>
        </div>
      ) : summary ? (
        <div className="flex flex-col flex-1 overflow-hidden">
          {/* Global KPI Summary Bar */}
          <div className="grid grid-cols-2 md:grid-cols-6 gap-3 p-4 bg-slate-900/40 border-b border-slate-800/80 shrink-0">
            <div className="p-3 rounded-xl bg-slate-900/80 border border-slate-800">
              <span className="text-[11px] text-slate-400">Verarbeitete Belege</span>
              <div className="text-base font-bold text-white font-mono mt-0.5">
                {summary.total_invoices_processed} Rechnungen
              </div>
              <div className="text-[10px] text-slate-500 mt-0.5 font-mono">{summary.batch_id}</div>
            </div>

            <div className="p-3 rounded-xl bg-slate-900/80 border border-slate-800">
              <span className="text-[11px] text-slate-400">EN 16931 &amp; UStG Konform</span>
              <div className="text-base font-bold text-emerald-400 font-mono mt-0.5">
                {summary.compliant_invoices_count} Belege
              </div>
              <div className="text-[10px] text-emerald-500/80 mt-0.5">
                {((summary.compliant_invoices_count / summary.total_invoices_processed) * 100).toFixed(0)}% Quote
              </div>
            </div>

            <div className="p-3 rounded-xl bg-slate-900/80 border border-slate-800">
              <span className="text-[11px] text-slate-400">Prüffälle / Abgelehnt</span>
              <div className="text-base font-bold text-rose-400 font-mono mt-0.5">
                {summary.rejected_invoices_count} Fehler
              </div>
              <div className="text-[10px] text-amber-400 mt-0.5">
                {summary.warning_invoices_count} mit Warnungen
              </div>
            </div>

            <div className="p-3 rounded-xl bg-slate-900/80 border border-slate-800">
              <span className="text-[11px] text-slate-400">Nettovolumen ({summary.chart_of_accounts})</span>
              <div className="text-base font-bold text-slate-200 font-mono mt-0.5">
                {summary.total_net_amount_eur.toLocaleString("de-DE", { style: "currency", currency: "EUR" })}
              </div>
              <div className="text-[10px] text-slate-500 mt-0.5">Aufwand gesamt</div>
            </div>

            <div className="p-3 rounded-xl bg-slate-900/80 border border-slate-800">
              <span className="text-[11px] text-slate-400">Vorsteuerbetrag</span>
              <div className="text-base font-bold text-blue-400 font-mono mt-0.5">
                {summary.total_tax_amount_eur.toLocaleString("de-DE", { style: "currency", currency: "EUR" })}
              </div>
              <div className="text-[10px] text-slate-500 mt-0.5">Abzugsfähig</div>
            </div>

            <div className="p-3 rounded-xl bg-slate-900/80 border border-slate-800">
              <span className="text-[11px] text-slate-400">Bruttovolumen (Verbindlichkeiten)</span>
              <div className="text-base font-bold text-emerald-400 font-mono mt-0.5">
                {summary.total_grand_amount_eur.toLocaleString("de-DE", { style: "currency", currency: "EUR" })}
              </div>
              <div className="text-[10px] text-slate-500 mt-0.5">Zahlbetrag Kreditor</div>
            </div>
          </div>

          {/* Navigation Tabs */}
          <div className="flex items-center justify-between px-6 pt-3 border-b border-slate-800 bg-slate-900/60 shrink-0">
            <div className="flex items-center space-x-1">
              <button
                onClick={() => setActiveTab("batch")}
                className={`flex items-center space-x-2 px-4 py-2 text-xs font-medium border-b-2 transition-colors ${
                  activeTab === "batch"
                    ? "border-emerald-400 text-emerald-400 bg-emerald-500/5"
                    : "border-transparent text-slate-400 hover:text-slate-200"
                }`}
              >
                <Layers className="w-3.5 h-3.5" />
                <span>Rechnungsstapel ({summary.items.length} Belege)</span>
              </button>

              <button
                onClick={() => setActiveTab("datev")}
                className={`flex items-center space-x-2 px-4 py-2 text-xs font-medium border-b-2 transition-colors ${
                  activeTab === "datev"
                    ? "border-emerald-400 text-emerald-400 bg-emerald-500/5"
                    : "border-transparent text-slate-400 hover:text-slate-200"
                }`}
              >
                <FileSpreadsheet className="w-3.5 h-3.5" />
                <span>DATEV Format 700 (Buchungsstapel)</span>
              </button>

              <button
                onClick={() => setActiveTab("sap")}
                className={`flex items-center space-x-2 px-4 py-2 text-xs font-medium border-b-2 transition-colors ${
                  activeTab === "sap"
                    ? "border-emerald-400 text-emerald-400 bg-emerald-500/5"
                    : "border-transparent text-slate-400 hover:text-slate-200"
                }`}
              >
                <Code2 className="w-3.5 h-3.5" />
                <span>SAP S/4HANA Finance Bridge</span>
              </button>
            </div>

            {/* Quick Export Buttons */}
            <div className="flex items-center space-x-2 pb-2">
              <button
                onClick={handleDownloadDatev}
                disabled={downloadingDatev}
                className="inline-flex items-center px-2.5 py-1 rounded-md text-xs font-medium bg-emerald-600 hover:bg-emerald-500 disabled:opacity-50 text-white shadow-sm transition-colors"
              >
                <Download className="w-3 h-3 mr-1" />
                {downloadingDatev ? "Lade..." : "DATEV .CSV"}
              </button>
              <button
                onClick={handleDownloadSap}
                disabled={downloadingSap}
                className="inline-flex items-center px-2.5 py-1 rounded-md text-xs font-medium bg-blue-600 hover:bg-blue-500 disabled:opacity-50 text-white shadow-sm transition-colors"
              >
                <Download className="w-3 h-3 mr-1" />
                {downloadingSap ? "Lade..." : "SAP .JSON"}
              </button>
            </div>
          </div>

          {/* Main Content Area */}
          <div className="flex-1 overflow-y-auto p-6 space-y-4">
            {/* ------------------------------------------------------------ */}
            {/* TAB: RECHNUNGSSTAPEL (MULTI-INVOICE GRID)                    */}
            {/* ------------------------------------------------------------ */}
            {activeTab === "batch" && (
              <div className="space-y-4">
                <div className="rounded-xl border border-slate-800 bg-slate-900/60 overflow-hidden">
                  <div className="overflow-x-auto">
                    <table className="w-full text-left text-xs">
                      <thead className="bg-slate-900 border-b border-slate-800 text-slate-400">
                        <tr>
                          <th className="py-3 px-4 font-medium">Status</th>
                          <th className="py-3 px-4 font-medium">Rechnungsnummer</th>
                          <th className="py-3 px-4 font-medium">Lieferant / Kreditor</th>
                          <th className="py-3 px-4 font-medium">Profil</th>
                          <th className="py-3 px-4 font-medium text-right">Netto</th>
                          <th className="py-3 px-4 font-medium text-right">USt</th>
                          <th className="py-3 px-4 font-medium text-right">Brutto (Umsatz)</th>
                          <th className="py-3 px-4 font-medium">Konto ({summary.chart_of_accounts})</th>
                          <th className="py-3 px-4 font-medium">Gegenkonto</th>
                          <th className="py-3 px-4 font-medium text-center">BU</th>
                          <th className="py-3 px-4 font-medium text-center">Aktion</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-slate-800 font-mono">
                        {summary.items.map((item, idx) => {
                          const isExpanded = expandedInvoiceIdx === idx;
                          return (
                            <React.Fragment key={idx}>
                              <tr className="hover:bg-slate-800/40 transition-colors">
                                <td className="py-3 px-4 font-sans">
                                  {item.status === "COMPLIANT" ? (
                                    <span className="inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-medium bg-emerald-500/15 text-emerald-300 border border-emerald-500/30">
                                      <CheckCircle2 className="w-3 h-3 mr-1" />
                                      Konform
                                    </span>
                                  ) : item.status === "WARNING" ? (
                                    <span className="inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-medium bg-amber-500/15 text-amber-300 border border-amber-500/30">
                                      <AlertCircle className="w-3 h-3 mr-1" />
                                      Warnung
                                    </span>
                                  ) : (
                                    <span className="inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-medium bg-rose-500/15 text-rose-300 border border-rose-500/30">
                                      <XCircle className="w-3 h-3 mr-1" />
                                      Gesperrt
                                    </span>
                                  )}
                                </td>
                                <td className="py-3 px-4 font-bold text-white">
                                  {item.invoice_number}
                                  <div className="text-[10px] text-slate-500 font-sans font-normal">
                                    {item.issue_date || "—"}
                                  </div>
                                </td>
                                <td className="py-3 px-4 font-sans text-slate-300 max-w-[180px] truncate">
                                  <div className="font-medium text-white truncate">{item.seller_name}</div>
                                  <div className="text-[10px] text-slate-500 font-mono">
                                    {item.seller_vat_id || "Keine USt-IdNr"}
                                  </div>
                                </td>
                                <td className="py-3 px-4 font-sans text-slate-400 text-[11px]">
                                  <span className="px-1.5 py-0.5 rounded bg-slate-800 border border-slate-700 font-mono">
                                    {item.profile}
                                  </span>
                                </td>
                                <td className="py-3 px-4 text-right text-slate-300">
                                  {item.net_amount_eur.toFixed(2)}
                                </td>
                                <td className="py-3 px-4 text-right text-blue-400">
                                  {item.tax_amount_eur.toFixed(2)}
                                </td>
                                <td className="py-3 px-4 text-right text-emerald-400 font-bold">
                                  {item.grand_total_eur.toFixed(2)} {item.currency}
                                </td>
                                <td className="py-3 px-4 text-cyan-300 font-bold">{item.aufwand_konto}</td>
                                <td className="py-3 px-4 text-slate-300">{item.kreditor_konto}</td>
                                <td className="py-3 px-4 text-center text-amber-300 font-bold">
                                  {item.bu_schluessel || "—"}
                                </td>
                                <td className="py-3 px-4 text-center font-sans">
                                  <button
                                    onClick={() => setExpandedInvoiceIdx(isExpanded ? null : idx)}
                                    className="p-1 rounded text-slate-400 hover:text-white hover:bg-slate-800 transition-colors"
                                    title="ERP Buchungszeile einsehen"
                                  >
                                    {isExpanded ? (
                                      <ChevronDown className="w-4 h-4 text-emerald-400" />
                                    ) : (
                                      <ChevronRight className="w-4 h-4" />
                                    )}
                                  </button>
                                </td>
                              </tr>

                              {/* Expanded Booking Row Detail */}
                              {isExpanded && (
                                <tr className="bg-slate-950/90 font-mono text-xs">
                                  <td colSpan={11} className="p-4 border-t border-slate-800/80">
                                    <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
                                      {/* DATEV Detail */}
                                      <div className="p-3 rounded-lg bg-slate-900 border border-slate-800 space-y-2">
                                        <div className="text-[11px] font-sans font-semibold text-emerald-400 flex items-center space-x-1.5">
                                          <FileSpreadsheet className="w-3.5 h-3.5" />
                                          <span>DATEV Buchungssatz (Format 700)</span>
                                        </div>
                                        <div className="grid grid-cols-2 gap-2 text-[11px] text-slate-300">
                                          <div>Umsatz: {item.datev_booking_row.umsatz_eur.toFixed(2)} € (S)</div>
                                          <div>Belegdatum: {item.datev_booking_row.belegdatum} (TTMM)</div>
                                          <div>
                                            Konto: {item.datev_booking_row.konto} → Kreditor:{" "}
                                            {item.datev_booking_row.gegenkonto}
                                          </div>
                                          <div>BU-Schlüssel: {item.datev_booking_row.bu_schluessel || "0"}</div>
                                          <div className="col-span-2 truncate">
                                            Text: {item.datev_booking_row.buchungstext}
                                          </div>
                                          <div className="col-span-2 text-slate-500 truncate">
                                            Beleglink: {item.datev_booking_row.beleglink}
                                          </div>
                                        </div>
                                      </div>

                                      {/* SAP Detail */}
                                      <div className="p-3 rounded-lg bg-slate-900 border border-slate-800 space-y-2">
                                        <div className="text-[11px] font-sans font-semibold text-blue-400 flex items-center space-x-1.5">
                                          <Code2 className="w-3.5 h-3.5" />
                                          <span>SAP S/4HANA Journal Entry ({item.sap_journal_entry.company_code})</span>
                                        </div>
                                        <div className="text-[11px] text-slate-300 space-y-1">
                                          <div>Belegart: {item.sap_journal_entry.accounting_document_type} (Lieferant)</div>
                                          <div>Ref-ID: {item.sap_journal_entry.document_reference_id}</div>
                                          <div className="pt-1 text-[10px] text-slate-400">
                                            {item.sap_journal_entry.items.map((it, i) => (
                                              <div key={i}>
                                                Pos {it.item_number} ({it.account_type}): {it.account} ·{" "}
                                                {it.amount_eur.toFixed(2)} EUR ({it.debit_credit_code})
                                              </div>
                                            ))}
                                          </div>
                                        </div>
                                      </div>
                                    </div>
                                  </td>
                                </tr>
                              )}
                            </React.Fragment>
                          );
                        })}
                      </tbody>
                    </table>
                  </div>
                </div>
              </div>
            )}

            {/* ------------------------------------------------------------ */}
            {/* TAB: DATEV FORMAT 700 CSV PREVIEW                            */}
            {/* ------------------------------------------------------------ */}
            {activeTab === "datev" && (
              <div className="space-y-4">
                <div className="p-4 rounded-xl border border-slate-800 bg-slate-900/60 flex items-center justify-between">
                  <div>
                    <h3 className="text-sm font-semibold text-white">
                      DATEV Buchungsstapel (Format Version 700 · EXTF)
                    </h3>
                    <p className="text-xs text-slate-400 mt-0.5">
                      Offizieller DATEV-ASCII Buchungsstapel für Kanzlei-Rechnungswesen / Unternehmen online.
                    </p>
                  </div>
                  <div className="flex items-center space-x-2">
                    <button
                      onClick={handleCopyDatev}
                      className="inline-flex items-center px-3 py-1.5 rounded-lg text-xs font-medium bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 transition-colors"
                    >
                      <Copy className="w-3.5 h-3.5 mr-1" />
                      <span>{copiedDatev ? "Kopiert!" : "Kopieren"}</span>
                    </button>
                    <button
                      onClick={handleDownloadDatev}
                      disabled={downloadingDatev}
                      className="inline-flex items-center px-3 py-1.5 rounded-lg text-xs font-medium bg-emerald-600 hover:bg-emerald-500 disabled:opacity-50 text-white shadow-sm transition-colors"
                    >
                      <Download className="w-3.5 h-3.5 mr-1" />
                      <span>{downloadingDatev ? "Lade..." : "EXTF_Buchungsstapel.csv"}</span>
                    </button>
                  </div>
                </div>

                <div className="p-4 rounded-xl bg-slate-950 border border-slate-800 font-mono text-[11px] text-slate-300 overflow-x-auto max-h-[500px]">
                  <pre>{summary.datev_csv_content}</pre>
                </div>
              </div>
            )}

            {/* ------------------------------------------------------------ */}
            {/* TAB: SAP S/4HANA FINANCE JSON PREVIEW                        */}
            {/* ------------------------------------------------------------ */}
            {activeTab === "sap" && (
              <div className="space-y-4">
                <div className="p-4 rounded-xl border border-slate-800 bg-slate-900/60 flex items-center justify-between">
                  <div>
                    <h3 className="text-sm font-semibold text-white">
                      SAP S/4HANA Cloud Finance JournalEntryCreateRequest
                    </h3>
                    <p className="text-xs text-slate-400 mt-0.5">
                      REST/OData Payload für SAP S/4HANA Financial Accounting (Buchungskreis {companyCode}).
                    </p>
                  </div>
                  <div className="flex items-center space-x-2">
                    <button
                      onClick={handleCopySap}
                      className="inline-flex items-center px-3 py-1.5 rounded-lg text-xs font-medium bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 transition-colors"
                    >
                      <Copy className="w-3.5 h-3.5 mr-1" />
                      <span>{copiedSap ? "Kopiert!" : "Kopieren"}</span>
                    </button>
                    <button
                      onClick={handleDownloadSap}
                      disabled={downloadingSap}
                      className="inline-flex items-center px-3 py-1.5 rounded-lg text-xs font-medium bg-blue-600 hover:bg-blue-500 disabled:opacity-50 text-white shadow-sm transition-colors"
                    >
                      <Download className="w-3.5 h-3.5 mr-1" />
                      <span>{downloadingSap ? "Lade..." : "SAP_JournalEntries.json"}</span>
                    </button>
                  </div>
                </div>

                <div className="p-4 rounded-xl bg-slate-950 border border-slate-800 font-mono text-[11px] text-slate-300 overflow-x-auto max-h-[500px]">
                  <pre>{summary.sap_json_content}</pre>
                </div>
              </div>
            )}
          </div>
        </div>
      ) : null}
    </div>
  );
}

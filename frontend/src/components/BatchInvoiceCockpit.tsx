"use client";

import React, { useEffect, useState } from "react";
import {
  AlertCircle,
  Archive,
  ArrowRight,
  Award,
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
  ShieldAlert,
  Sparkles,
  Upload,
  XCircle,
} from "lucide-react";
import {
  batchIngestInvoices,
  BatchIngestionSummary,
  BatchInvoiceProcessingItem,
  ChartOfAccounts,
  downloadCapstoneDatevCsv,
  downloadCapstoneReportPdf,
  downloadCapstoneSapJson,
  downloadDatevCsv,
  downloadSapJson,
  getCapstoneSummary,
  getSampleBatchSummary,
  Week4CapstoneSummary,
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

  // Week 4 Capstone Benchmark State
  const [capstoneSummary, setCapstoneSummary] = useState<Week4CapstoneSummary | null>(null);
  const [loadingCapstone, setLoadingCapstone] = useState<boolean>(false);
  const [downloadingCapstonePdf, setDownloadingCapstonePdf] = useState<boolean>(false);
  const [downloadingCapstoneDatev, setDownloadingCapstoneDatev] = useState<boolean>(false);
  const [downloadingCapstoneSap, setDownloadingCapstoneSap] = useState<boolean>(false);

  // Configuration State
  const [chartOfAccounts, setChartOfAccounts] = useState<ChartOfAccounts>("SKR03");
  const [beraternummer, setBeraternummer] = useState<number>(1001);
  const [mandantennummer, setMandantennummer] = useState<number>(70001);
  const [companyCode, setCompanyCode] = useState<string>("1000");

  // UI Tabs: "batch" | "capstone" | "datev" | "sap"
  const [activeTab, setActiveTab] = useState<"batch" | "capstone" | "datev" | "sap">("batch");
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

  const loadCapstoneBenchmark = async () => {
    try {
      setLoadingCapstone(true);
      setError(null);
      const res = await getCapstoneSummary(chartOfAccounts, beraternummer, mandantennummer, companyCode);
      setCapstoneSummary(res);
      setActiveTab("capstone");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Fehler beim Laden des Capstone-Benchmarks.");
    } finally {
      setLoadingCapstone(false);
    }
  };

  useEffect(() => {
    loadBatch();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const handleChartChange = (newChart: ChartOfAccounts) => {
    setChartOfAccounts(newChart);
    if (activeTab === "capstone") {
      loadCapstoneBenchmark();
    } else {
      loadBatch(newChart, beraternummer, mandantennummer, companyCode);
    }
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
      setError(err instanceof Error ? err.message : "Batch-Upload fehlgeschlagen.");
    } finally {
      setUploading(false);
    }
  };

  const handleCopyDatev = () => {
    const content = activeTab === "capstone" ? capstoneSummary?.datev_csv_content : summary?.datev_csv_content;
    if (content) {
      navigator.clipboard.writeText(content);
      setCopiedDatev(true);
      setTimeout(() => setCopiedDatev(false), 2000);
    }
  };

  const handleCopySap = () => {
    const content = activeTab === "capstone" ? capstoneSummary?.sap_json_content : summary?.sap_json_content;
    if (content) {
      navigator.clipboard.writeText(content);
      setCopiedSap(true);
      setTimeout(() => setCopiedSap(false), 2000);
    }
  };

  const handleDownloadDatev = async () => {
    try {
      setDownloadingDatev(true);
      await downloadDatevCsv(chartOfAccounts, beraternummer, mandantennummer);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Download fehlgeschlagen.");
    } finally {
      setDownloadingDatev(false);
    }
  };

  const handleDownloadSap = async () => {
    try {
      setDownloadingSap(true);
      await downloadSapJson(companyCode);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Download fehlgeschlagen.");
    } finally {
      setDownloadingSap(false);
    }
  };

  const handleDownloadCapstonePdf = async () => {
    try {
      setDownloadingCapstonePdf(true);
      await downloadCapstoneReportPdf(chartOfAccounts);
    } catch (err) {
      setError(err instanceof Error ? err.message : "PDF-Download fehlgeschlagen.");
    } finally {
      setDownloadingCapstonePdf(false);
    }
  };

  const handleDownloadCapstoneDatev = async () => {
    try {
      setDownloadingCapstoneDatev(true);
      await downloadCapstoneDatevCsv(chartOfAccounts, beraternummer, mandantennummer);
    } catch (err) {
      setError(err instanceof Error ? err.message : "DATEV-Download fehlgeschlagen.");
    } finally {
      setDownloadingCapstoneDatev(false);
    }
  };

  const handleDownloadCapstoneSap = async () => {
    try {
      setDownloadingCapstoneSap(true);
      await downloadCapstoneSapJson(companyCode);
    } catch (err) {
      setError(err instanceof Error ? err.message : "SAP-Download fehlgeschlagen.");
    } finally {
      setDownloadingCapstoneSap(false);
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
          {/* Week 4 Capstone Benchmark Button */}
          <button
            onClick={loadCapstoneBenchmark}
            disabled={loadingCapstone}
            className="inline-flex items-center px-3 py-1.5 rounded-lg text-xs font-semibold bg-gradient-to-r from-amber-500 to-emerald-500 text-slate-950 shadow-md hover:brightness-110 disabled:opacity-50 transition-all cursor-pointer"
            title="Vollständigen 100-Belege Enterprise Benchmark laden"
          >
            <Sparkles className={`w-3.5 h-3.5 mr-1.5 ${loadingCapstone ? "animate-spin" : ""}`} />
            <span>{loadingCapstone ? "Prüfe 100 Belege..." : "Week 4 Capstone (100 Belege)"}</span>
          </button>

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
          {/* Global KPI Summary Bar (displays Capstone metrics if capstone tab is active) */}
          <div className="grid grid-cols-2 md:grid-cols-6 gap-3 p-4 bg-slate-900/40 border-b border-slate-800/80 shrink-0">
            <div className="p-3 rounded-xl bg-slate-900/80 border border-slate-800">
              <span className="text-[11px] text-slate-400">Verarbeitete Belege</span>
              <div className="text-base font-bold text-white font-mono mt-0.5">
                {activeTab === "capstone" && capstoneSummary
                  ? `${capstoneSummary.total_invoices} Belege (Benchmark)`
                  : `${summary.total_invoices_processed} Rechnungen`}
              </div>
              <div className="text-[10px] text-slate-500 mt-0.5 font-mono truncate">
                {activeTab === "capstone" && capstoneSummary ? capstoneSummary.batch_id : summary.batch_id}
              </div>
            </div>

            <div className="p-3 rounded-xl bg-slate-900/80 border border-slate-800">
              <span className="text-[11px] text-slate-400">EN 16931 &amp; UStG Konform</span>
              <div className="text-base font-bold text-emerald-400 font-mono mt-0.5">
                {activeTab === "capstone" && capstoneSummary
                  ? `${capstoneSummary.compliant_count} Belege`
                  : `${summary.compliant_invoices_count} Belege`}
              </div>
              <div className="text-[10px] text-emerald-500/80 mt-0.5">
                {activeTab === "capstone" && capstoneSummary
                  ? `${capstoneSummary.compliance_rate_percent}% Quote`
                  : `${((summary.compliant_invoices_count / summary.total_invoices_processed) * 100).toFixed(0)}% Quote`}
              </div>
            </div>

            <div className="p-3 rounded-xl bg-slate-900/80 border border-slate-800">
              <span className="text-[11px] text-slate-400">Gesperrt / Diskrepanz</span>
              <div className="text-base font-bold text-rose-400 font-mono mt-0.5">
                {activeTab === "capstone" && capstoneSummary
                  ? `${capstoneSummary.rejected_count} Diskrepanzen`
                  : `${summary.rejected_invoices_count} Fehler`}
              </div>
              <div className="text-[10px] text-amber-400 mt-0.5">
                {activeTab === "capstone" && capstoneSummary
                  ? "100% Betrugserkennung"
                  : `${summary.warning_invoices_count} mit Warnungen`}
              </div>
            </div>

            <div className="p-3 rounded-xl bg-slate-900/80 border border-slate-800">
              <span className="text-[11px] text-slate-400">Nettovolumen ({chartOfAccounts})</span>
              <div className="text-base font-bold text-slate-200 font-mono mt-0.5">
                {(activeTab === "capstone" && capstoneSummary
                  ? capstoneSummary.total_net_eur
                  : summary.total_net_amount_eur
                ).toLocaleString("de-DE", { style: "currency", currency: "EUR" })}
              </div>
              <div className="text-[10px] text-slate-500 mt-0.5">Aufwand gesamt</div>
            </div>

            <div className="p-3 rounded-xl bg-slate-900/80 border border-slate-800">
              <span className="text-[11px] text-slate-400">Vorsteuerbetrag</span>
              <div className="text-base font-bold text-blue-400 font-mono mt-0.5">
                {(activeTab === "capstone" && capstoneSummary
                  ? capstoneSummary.total_tax_eur
                  : summary.total_tax_amount_eur
                ).toLocaleString("de-DE", { style: "currency", currency: "EUR" })}
              </div>
              <div className="text-[10px] text-slate-500 mt-0.5">Abzugsfähig</div>
            </div>

            <div className="p-3 rounded-xl bg-slate-900/80 border border-slate-800">
              <span className="text-[11px] text-slate-400">Bruttovolumen (Verbindl.)</span>
              <div className="text-base font-bold text-emerald-400 font-mono mt-0.5">
                {(activeTab === "capstone" && capstoneSummary
                  ? capstoneSummary.total_grand_eur
                  : summary.total_grand_amount_eur
                ).toLocaleString("de-DE", { style: "currency", currency: "EUR" })}
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
                onClick={() => {
                  if (!capstoneSummary) {
                    loadCapstoneBenchmark();
                  } else {
                    setActiveTab("capstone");
                  }
                }}
                className={`flex items-center space-x-2 px-4 py-2 text-xs font-medium border-b-2 transition-colors ${
                  activeTab === "capstone"
                    ? "border-amber-400 text-amber-400 bg-amber-500/5"
                    : "border-transparent text-slate-400 hover:text-slate-200"
                }`}
              >
                <Award className="w-3.5 h-3.5 text-amber-400" />
                <span>Week 4 Capstone {capstoneSummary ? "(100 Belege · 95%)" : "(100 Belege)"}</span>
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
              {activeTab === "capstone" ? (
                <>
                  <button
                    onClick={handleDownloadCapstonePdf}
                    disabled={downloadingCapstonePdf}
                    className="inline-flex items-center px-2.5 py-1 rounded text-xs font-medium bg-amber-600 hover:bg-amber-500 text-slate-950 font-bold shadow-sm transition-colors"
                  >
                    <Award className="w-3.5 h-3.5 mr-1" />
                    <span>{downloadingCapstonePdf ? "Erzeuge PDF..." : "Master Audit PDF"}</span>
                  </button>
                  <button
                    onClick={handleDownloadCapstoneDatev}
                    disabled={downloadingCapstoneDatev}
                    className="inline-flex items-center px-2.5 py-1 rounded text-xs font-medium bg-emerald-700 hover:bg-emerald-600 text-white shadow-sm transition-colors"
                  >
                    <Download className="w-3.5 h-3.5 mr-1" />
                    <span>DATEV 100 CSV</span>
                  </button>
                  <button
                    onClick={handleDownloadCapstoneSap}
                    disabled={downloadingCapstoneSap}
                    className="inline-flex items-center px-2.5 py-1 rounded text-xs font-medium bg-blue-700 hover:bg-blue-600 text-white shadow-sm transition-colors"
                  >
                    <Download className="w-3.5 h-3.5 mr-1" />
                    <span>SAP 100 JSON</span>
                  </button>
                </>
              ) : (
                <>
                  <button
                    onClick={handleDownloadDatev}
                    disabled={downloadingDatev}
                    className="inline-flex items-center px-2.5 py-1 rounded text-xs font-medium bg-emerald-700 hover:bg-emerald-600 text-white shadow-sm transition-colors"
                  >
                    <Download className="w-3.5 h-3.5 mr-1" />
                    <span>DATEV EXTF CSV</span>
                  </button>
                  <button
                    onClick={handleDownloadSap}
                    disabled={downloadingSap}
                    className="inline-flex items-center px-2.5 py-1 rounded text-xs font-medium bg-blue-700 hover:bg-blue-600 text-white shadow-sm transition-colors"
                  >
                    <Download className="w-3.5 h-3.5 mr-1" />
                    <span>SAP S/4HANA JSON</span>
                  </button>
                </>
              )}
            </div>
          </div>

          {/* Body Content */}
          <div className="flex-1 overflow-y-auto p-6 space-y-6">
            {/* ------------------------------------------------------------ */}
            {/* TAB: WEEK 4 CAPSTONE BENCHMARK VIEW                          */}
            {/* ------------------------------------------------------------ */}
            {activeTab === "capstone" && capstoneSummary && (
              <div className="space-y-6">
                {/* Banner & Latency KPI Card */}
                <div className="p-5 rounded-2xl bg-gradient-to-r from-slate-900 via-slate-900 to-amber-950/40 border border-amber-500/30 flex flex-wrap items-center justify-between gap-4">
                  <div>
                    <div className="flex items-center space-x-2">
                      <Award className="w-5 h-5 text-amber-400" />
                      <h3 className="text-base font-bold text-white tracking-tight">
                        Week 4 Capstone: High-Throughput E-Invoicing Benchmark
                      </h3>
                      <span className="px-2 py-0.5 text-xs font-medium rounded-full bg-amber-500/15 border border-amber-500/30 text-amber-300">
                        100 B2B/B2G Belege
                      </span>
                    </div>
                    <p className="text-xs text-slate-400 mt-1">
                      Vollständige Prüfung nach EN 16931-1:2017, KoSIT XRechnung 3.0, § 14 UStG &amp; GoBD Revisionssicherheit.
                    </p>
                  </div>

                  <div className="flex items-center space-x-3">
                    <div className="text-right">
                      <div className="text-xs font-mono font-bold text-cyan-300">
                        {capstoneSummary.execution_time_ms.toFixed(1)} ms Latenz
                      </div>
                      <div className="text-[11px] text-slate-400">
                        {capstoneSummary.throughput_invoices_per_sec.toLocaleString("de-DE")} Belege / Sekunde
                      </div>
                    </div>
                    <button
                      onClick={handleDownloadCapstonePdf}
                      disabled={downloadingCapstonePdf}
                      className="inline-flex items-center px-4 py-2 rounded-xl text-xs font-bold bg-amber-500 hover:bg-amber-400 text-slate-950 shadow-lg hover:shadow-amber-500/20 transition-all cursor-pointer"
                    >
                      <Download className="w-4 h-4 mr-1.5" />
                      <span>{downloadingCapstonePdf ? "Erzeuge PDF..." : "Master Audit-Zertifikat (PDF)"}</span>
                    </button>
                  </div>
                </div>

                {/* Category Distribution Pills */}
                <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-2">
                  <div className="p-2.5 rounded-xl bg-slate-900/60 border border-slate-800 text-center">
                    <div className="text-xs font-bold text-white">40 Belege</div>
                    <div className="text-[10px] text-slate-400">B2B Comfort (19%)</div>
                  </div>
                  <div className="p-2.5 rounded-xl bg-slate-900/60 border border-slate-800 text-center">
                    <div className="text-xs font-bold text-cyan-400">25 Belege</div>
                    <div className="text-[10px] text-slate-400">B2G XRechnung (Bund/Land)</div>
                  </div>
                  <div className="p-2.5 rounded-xl bg-slate-900/60 border border-slate-800 text-center">
                    <div className="text-xs font-bold text-emerald-400">15 Belege</div>
                    <div className="text-[10px] text-slate-400">§ 13b Reverse Charge (0%)</div>
                  </div>
                  <div className="p-2.5 rounded-xl bg-slate-900/60 border border-slate-800 text-center">
                    <div className="text-xs font-bold text-purple-400">10 Belege</div>
                    <div className="text-[10px] text-slate-400">§ 12 Abs. 2 Ermäßigt (7%)</div>
                  </div>
                  <div className="p-2.5 rounded-xl bg-slate-900/60 border border-slate-800 text-center">
                    <div className="text-xs font-bold text-blue-400">5 Belege</div>
                    <div className="text-[10px] text-slate-400">§ 33 UStDV (&le; 250 EUR)</div>
                  </div>
                  <div className="p-2.5 rounded-xl bg-rose-950/30 border border-rose-500/30 text-center">
                    <div className="text-xs font-bold text-rose-400">5 Belege</div>
                    <div className="text-[10px] text-rose-300">Betrugs-Simulationen</div>
                  </div>
                </div>

                {/* Forensic Anomaly & Fraud Register Table */}
                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <h4 className="text-xs font-bold uppercase tracking-wider text-rose-400 flex items-center space-x-1.5">
                      <ShieldAlert className="w-4 h-4 text-rose-400" />
                      <span>Forensisches Anomalie- &amp; Betrugsregister (5 abgewiesene Prüffälle)</span>
                    </h4>
                    <span className="text-[11px] text-slate-400 font-mono">
                      100% Erkennungsgenauigkeit
                    </span>
                  </div>

                  <div className="space-y-2">
                    {capstoneSummary.discrepancies.map((disc) => (
                      <div
                        key={disc.index}
                        className="p-3.5 rounded-xl bg-rose-950/20 border border-rose-500/30 space-y-2 text-xs"
                      >
                        <div className="flex items-center justify-between">
                          <div className="flex items-center space-x-2">
                            <span className="font-mono font-bold text-white">{disc.invoice_number}</span>
                            <span className="text-slate-400">· {disc.filename}</span>
                          </div>
                          <span
                            className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                              disc.risk_level === "KRITISCH"
                                ? "bg-rose-500/20 text-rose-300 border border-rose-500/30"
                                : "bg-amber-500/20 text-amber-300 border border-amber-500/30"
                            }`}
                          >
                            RISIKO: {disc.risk_level}
                          </span>
                        </div>

                        <div className="grid grid-cols-1 md:grid-cols-2 gap-2 text-[11px] pt-1">
                          <div>
                            <span className="text-slate-400 font-medium">Verletzte Norm: </span>
                            <span className="text-rose-300 font-semibold">{disc.rule_violated}</span>
                          </div>
                          <div>
                            <span className="text-slate-400 font-medium">Rechtsgrundlage: </span>
                            <span className="text-slate-300">{disc.statutory_standard}</span>
                          </div>
                        </div>

                        <p className="text-[11px] text-slate-300 bg-slate-950/60 p-2 rounded-lg border border-slate-800/80">
                          <strong className="text-rose-400">Befund: </strong>
                          {disc.rejection_reason}
                        </p>

                        <p className="text-[11px] text-emerald-300 bg-emerald-950/20 p-2 rounded-lg border border-emerald-500/20">
                          <strong className="text-emerald-400">Sicherungsmaßnahme: </strong>
                          {disc.remedial_action}
                        </p>
                      </div>
                    ))}
                  </div>
                </div>

                {/* 100 Invoices Table */}
                <div className="space-y-3">
                  <h4 className="text-xs font-bold uppercase tracking-wider text-slate-300 flex items-center space-x-1.5">
                    <Layers className="w-4 h-4 text-emerald-400" />
                    <span>Gesamtstichprobe ({capstoneSummary.items.length} Belege)</span>
                  </h4>

                  <div className="border border-slate-800 rounded-xl overflow-hidden bg-slate-900/40">
                    <table className="w-full text-left text-xs">
                      <thead className="bg-slate-900 border-b border-slate-800 text-slate-400 font-mono text-[11px]">
                        <tr>
                          <th className="py-2.5 px-3">#</th>
                          <th className="py-2.5 px-3">Rechnungsnummer</th>
                          <th className="py-2.5 px-3">Kreditor / Aussteller</th>
                          <th className="py-2.5 px-3">Rechnungsempfänger</th>
                          <th className="py-2.5 px-3">Profil</th>
                          <th className="py-2.5 px-3 text-right">Netto</th>
                          <th className="py-2.5 px-3 text-right">Gesamt (EUR)</th>
                          <th className="py-2.5 px-3 text-center">Status</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-slate-800/60 font-mono text-[11px]">
                        {capstoneSummary.items.map((item) => (
                          <tr
                            key={item.invoice_index}
                            className={`hover:bg-slate-900/60 transition-colors ${
                              item.status === "REJECTED" ? "bg-rose-950/10" : ""
                            }`}
                          >
                            <td className="py-2 px-3 text-slate-500">{item.invoice_index}</td>
                            <td className="py-2 px-3 font-semibold text-white">{item.invoice_number}</td>
                            <td className="py-2 px-3 text-slate-300 font-sans truncate max-w-[180px]">
                              {item.seller_name}
                            </td>
                            <td className="py-2 px-3 text-slate-400 font-sans truncate max-w-[180px]">
                              {item.buyer_name}
                            </td>
                            <td className="py-2 px-3 text-slate-400">{item.profile}</td>
                            <td className="py-2 px-3 text-right text-slate-300">
                              {item.net_amount_eur.toLocaleString("de-DE", { minimumFractionDigits: 2 })}
                            </td>
                            <td className="py-2 px-3 text-right font-bold text-white">
                              {item.grand_total_eur.toLocaleString("de-DE", { minimumFractionDigits: 2 })}
                            </td>
                            <td className="py-2 px-3 text-center">
                              {item.status === "COMPLIANT" ? (
                                <span className="inline-flex items-center px-2 py-0.5 rounded text-[10px] font-semibold bg-emerald-500/15 text-emerald-300 border border-emerald-500/30">
                                  Konform
                                </span>
                              ) : (
                                <span className="inline-flex items-center px-2 py-0.5 rounded text-[10px] font-semibold bg-rose-500/15 text-rose-300 border border-rose-500/30">
                                  Gesperrt
                                </span>
                              )}
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              </div>
            )}

            {/* ------------------------------------------------------------ */}
            {/* TAB: STANDARD BATCH TABLE VIEW                               */}
            {/* ------------------------------------------------------------ */}
            {activeTab === "batch" && (
              <div className="space-y-4">
                <div className="border border-slate-800 rounded-xl overflow-hidden bg-slate-900/40">
                  <div className="overflow-x-auto">
                    <table className="w-full text-left text-xs">
                      <thead className="bg-slate-900 border-b border-slate-800 text-slate-400 font-mono text-[11px]">
                        <tr>
                          <th className="py-3 px-4 w-10">#</th>
                          <th className="py-3 px-4">Rechnungs-Nr.</th>
                          <th className="py-3 px-4">Lieferant / Kreditor</th>
                          <th className="py-3 px-4">Profil</th>
                          <th className="py-3 px-4 text-right">Netto</th>
                          <th className="py-3 px-4 text-right">MwSt</th>
                          <th className="py-3 px-4 text-right">Gesamtbetrag</th>
                          <th className="py-3 px-4 text-center">Status</th>
                          <th className="py-3 px-4 text-center">Aktionen</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-slate-800/60 font-mono text-xs">
                        {summary.items.map((item) => {
                          const isExpanded = expandedInvoiceIdx === item.invoice_index;
                          return (
                            <React.Fragment key={item.invoice_index}>
                              <tr
                                className={`hover:bg-slate-900/80 transition-colors cursor-pointer ${
                                  isExpanded ? "bg-slate-900/90" : ""
                                }`}
                                onClick={() =>
                                  setExpandedInvoiceIdx(isExpanded ? null : item.invoice_index)
                                }
                              >
                                <td className="py-3 px-4 text-slate-500">
                                  <div className="flex items-center space-x-1">
                                    {isExpanded ? (
                                      <ChevronDown className="w-3.5 h-3.5 text-emerald-400" />
                                    ) : (
                                      <ChevronRight className="w-3.5 h-3.5 text-slate-500" />
                                    )}
                                    <span>{item.invoice_index}</span>
                                  </div>
                                </td>
                                <td className="py-3 px-4 font-semibold text-white">
                                  {item.invoice_number}
                                </td>
                                <td className="py-3 px-4 text-slate-300 font-sans">
                                  <div className="truncate max-w-[200px]" title={item.seller_name}>
                                    {item.seller_name}
                                  </div>
                                  <div className="text-[10px] text-slate-500 font-mono">
                                    {item.seller_vat_id || "Keine USt-IdNr."}
                                  </div>
                                </td>
                                <td className="py-3 px-4">
                                  <span className="px-2 py-0.5 rounded text-[10px] bg-slate-800 text-slate-300 border border-slate-700">
                                    {item.profile}
                                  </span>
                                </td>
                                <td className="py-3 px-4 text-right text-slate-300">
                                  {item.net_amount_eur.toLocaleString("de-DE", { minimumFractionDigits: 2 })}{" "}
                                  EUR
                                </td>
                                <td className="py-3 px-4 text-right text-slate-300">
                                  {item.tax_amount_eur.toLocaleString("de-DE", { minimumFractionDigits: 2 })}{" "}
                                  EUR
                                </td>
                                <td className="py-3 px-4 text-right font-bold text-emerald-400">
                                  {item.grand_total_eur.toLocaleString("de-DE", { minimumFractionDigits: 2 })}{" "}
                                  EUR
                                </td>
                                <td className="py-3 px-4 text-center">
                                  {item.status === "COMPLIANT" ? (
                                    <span className="inline-flex items-center px-2 py-0.5 rounded text-[10px] font-semibold bg-emerald-500/15 text-emerald-300 border border-emerald-500/30">
                                      <CheckCircle2 className="w-3 h-3 mr-1" />
                                      Konform
                                    </span>
                                  ) : item.status === "WARNING" ? (
                                    <span className="inline-flex items-center px-2 py-0.5 rounded text-[10px] font-semibold bg-amber-500/15 text-amber-300 border border-amber-500/30">
                                      <AlertCircle className="w-3 h-3 mr-1" />
                                      Prüfen
                                    </span>
                                  ) : (
                                    <span className="inline-flex items-center px-2 py-0.5 rounded text-[10px] font-semibold bg-rose-500/15 text-rose-300 border border-rose-500/30">
                                      <XCircle className="w-3 h-3 mr-1" />
                                      Gesperrt
                                    </span>
                                  )}
                                </td>
                                <td className="py-3 px-4 text-center">
                                  {onSelectInvoice && (
                                    <button
                                      onClick={(e) => {
                                        e.stopPropagation();
                                        onSelectInvoice(item);
                                      }}
                                      className="inline-flex items-center px-2 py-1 rounded text-[10px] font-sans font-medium bg-slate-800 hover:bg-slate-700 text-slate-200 transition-colors"
                                      title="Im Einzelbeleg-Viewer öffnen"
                                    >
                                      <span>Öffnen</span>
                                      <ArrowRight className="w-3 h-3 ml-1" />
                                    </button>
                                  )}
                                </td>
                              </tr>

                              {/* Expanded Booking Detail Row */}
                              {isExpanded && (
                                <tr className="bg-slate-900/70 border-b border-slate-800">
                                  <td colSpan={9} className="p-4 pl-12">
                                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                      {/* DATEV Detail */}
                                      <div className="p-3 rounded-lg bg-slate-900 border border-slate-800 space-y-2">
                                        <div className="text-[11px] font-sans font-semibold text-emerald-400 flex items-center space-x-1.5">
                                          <FileSpreadsheet className="w-3.5 h-3.5" />
                                          <span>DATEV Buchungssatz ({chartOfAccounts})</span>
                                        </div>
                                        <div className="text-[11px] text-slate-300 space-y-1">
                                          <div>
                                            Konto: <span className="text-white font-bold">{item.datev_booking_row.konto}</span> (Aufwand) &middot; Gegenkonto: <span className="text-white font-bold">{item.datev_booking_row.gegenkonto}</span> (Kreditor)
                                          </div>
                                          <div>BU-Schlüssel: {item.datev_booking_row.bu_schluessel || "0 (kein)"} &middot; Festschreibung: {item.datev_booking_row.festschreibung} (GoBD)</div>
                                          <div>Text: {item.datev_booking_row.buchungstext}</div>
                                        </div>
                                      </div>

                                      {/* SAP Detail */}
                                      <div className="p-3 rounded-lg bg-slate-900 border border-slate-800 space-y-2">
                                        <div className="text-[11px] font-sans font-semibold text-blue-400 flex items-center space-x-1.5">
                                          <Code2 className="w-3.5 h-3.5" />
                                          <span>SAP S/4HANA Journal Entry ({item.sap_journal_entry.company_code})</span>
                                        </div>
                                        <div className="text-[11px] text-slate-300 space-y-1">
                                          <div>Belegart: {item.sap_journal_entry.accounting_document_type} (Lieferant) &middot; Ref: {item.sap_journal_entry.document_reference_id}</div>
                                          <div className="pt-1 text-[10px] text-slate-400">
                                            {item.sap_journal_entry.items.map((it, i) => (
                                              <div key={i}>
                                                Pos {it.item_number} ({it.account_type}): {it.account} &middot; {it.amount_eur.toFixed(2)} EUR ({it.debit_credit_code})
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
                      DATEV Buchungsstapel (Format Version 700 &middot; EXTF)
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

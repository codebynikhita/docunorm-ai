"use client";

import React, { useEffect, useState } from "react";
import {
  AlertCircle,
  Building2,
  CheckCircle2,
  Code2,
  Columns2,
  Copy,
  CreditCard,
  Download,
  Eye,
  FileCheck,
  FileSpreadsheet,
  FileText,
  Landmark,
  Layers,
  PanelLeft,
  PanelRight,
  Play,
  Receipt,
  RefreshCw,
  RotateCcw,
  Route,
  Scale,
  ShieldCheck,
  Sparkles,
  XCircle,
} from "lucide-react";
import {
  downloadZugferdCertificatePdf,
  getZugferdInvoice,
  getZugferdSampleProfiles,
  LeitwegValidationResult,
  reconcileZugferdVisualXml,
  validateLeitwegId,
  validateZugferdXml,
  ZugferdInvoiceExtraction,
  ZugferdSampleProfile,
  ZugferdVisualReconciliation,
} from "@/lib/api";

interface ZugferdInvoiceViewerProps {
  documentId: string;
  filename: string;
  onClose?: () => void;
}

export function ZugferdInvoiceViewer({
  documentId,
  filename,
  onClose,
}: ZugferdInvoiceViewerProps) {
  const [data, setData] = useState<ZugferdInvoiceExtraction | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  // Layout mode: split (both panes), cockpit (only right), preview (only left)
  const [layoutMode, setLayoutMode] = useState<"split" | "cockpit" | "preview">("split");

  // Cockpit tabs
  const [activeTab, setActiveTab] = useState<
    "items" | "totals" | "reconciliation" | "vat" | "validation" | "xml"
  >("reconciliation");

  // Day 26 State
  const [visualReconciliation, setVisualReconciliation] = useState<ZugferdVisualReconciliation | null>(null);
  const [reconciling, setReconciling] = useState<boolean>(false);
  const [highlightedField, setHighlightedField] = useState<string | null>(null);
  const [sampleProfiles, setSampleProfiles] = useState<ZugferdSampleProfile[]>([]);
  const [selectedProfileId, setSelectedProfileId] = useState<string>("");

  // XML Studio State
  const [xmlContent, setXmlContent] = useState<string>("");
  const [validatingXml, setValidatingXml] = useState<boolean>(false);
  const [xmlStatusMessage, setXmlStatusMessage] = useState<string | null>(null);

  // Interactive Tools State
  const [copied, setCopied] = useState<boolean>(false);
  const [exportingPdf, setExportingPdf] = useState<boolean>(false);
  const [leitwegInput, setLeitwegInput] = useState<string>("");
  const [leitwegTestResult, setLeitwegTestResult] = useState<LeitwegValidationResult | null>(null);
  const [testingLeitweg, setTestingLeitweg] = useState<boolean>(false);

  // Load initial extraction & sample profiles
  useEffect(() => {
    let isMounted = true;
    async function loadData() {
      try {
        setLoading(true);
        setError(null);
        const [resInvoice, resProfiles] = await Promise.all([
          getZugferdInvoice(documentId),
          getZugferdSampleProfiles().catch(() => []),
        ]);

        if (isMounted) {
          setData(resInvoice);
          setSampleProfiles(resProfiles);
          if (resInvoice.raw_xml_content) {
            setXmlContent(resInvoice.raw_xml_content);
          }
          if (resProfiles.length > 0) {
            setSelectedProfileId(resProfiles[0].profile_id);
          }
        }

        // Run automatic visual-to-xml reconciliation
        try {
          setReconciling(true);
          const resRec = await reconcileZugferdVisualXml(documentId);
          if (isMounted) {
            setVisualReconciliation(resRec);
          }
        } catch {
          // Fallback handled gracefully
        } finally {
          if (isMounted) setReconciling(false);
        }
      } catch (err: unknown) {
        if (isMounted) {
          setError(err instanceof Error ? err.message : "Fehler beim Laden der ZUGFeRD-Daten.");
        }
      } finally {
        if (isMounted) {
          setLoading(false);
        }
      }
    }
    loadData();
    return () => {
      isMounted = false;
    };
  }, [documentId]);

  const handleCopyXml = () => {
    if (xmlContent || data?.raw_xml_content) {
      navigator.clipboard.writeText(xmlContent || data?.raw_xml_content || "");
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  const handleDownloadCertificate = async () => {
    if (!data) return;
    try {
      setExportingPdf(true);
      await downloadZugferdCertificatePdf(documentId, data.invoice_number);
    } catch (err) {
      setError(err instanceof Error ? err.message : "PDF Export fehlgeschlagen.");
    } finally {
      setExportingPdf(false);
    }
  };

  const handleCheckCustomLeitweg = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!leitwegInput.trim()) return;
    try {
      setTestingLeitweg(true);
      const res = await validateLeitwegId(leitwegInput.trim());
      setLeitwegTestResult(res);
    } catch (err) {
      setLeitwegTestResult(null);
      setError(err instanceof Error ? err.message : "Leitweg-ID Prüfung fehlgeschlagen.");
    } finally {
      setTestingLeitweg(false);
    }
  };

  const handleLoadSampleProfile = (profileId: string) => {
    setSelectedProfileId(profileId);
    const profile = sampleProfiles.find((p) => p.profile_id === profileId);
    if (!profile) return;
    setXmlContent(profile.raw_xml);
    setXmlStatusMessage(`Musterprofil '${profile.name}' geladen.`);
  };

  const handleValidateEditedXml = async () => {
    if (!xmlContent.trim()) return;
    try {
      setValidatingXml(true);
      setXmlStatusMessage(null);
      const updatedExtraction = await validateZugferdXml(xmlContent, data?.xml_filename || "invoice.xml");
      setData(updatedExtraction);

      // Re-run visual reconciliation against newly updated extraction
      const rec = await reconcileZugferdVisualXml(documentId);
      setVisualReconciliation(rec);

      setXmlStatusMessage("XML erfolgreich validiert & Cockpit-Daten aktualisiert.");
    } catch (err) {
      setXmlStatusMessage(err instanceof Error ? `Fehler: ${err.message}` : "Validierung fehlgeschlagen.");
    } finally {
      setValidatingXml(false);
    }
  };

  const handleFieldHotspotClick = (fieldKey: string) => {
    setHighlightedField(fieldKey);
    setActiveTab("reconciliation");
    setTimeout(() => {
      const el = document.getElementById(`rec-row-${fieldKey}`);
      if (el) {
        el.scrollIntoView({ behavior: "smooth", block: "center" });
      }
    }, 100);
  };

  return (
    <div className="flex flex-col h-full bg-slate-950 text-slate-100 overflow-hidden font-sans">
      {/* Top Header Bar */}
      <div className="flex items-center justify-between px-6 py-3.5 border-b border-slate-800 bg-slate-900/80 backdrop-blur-md shrink-0">
        <div className="flex items-center space-x-3">
          <div className="p-2 rounded-lg bg-emerald-500/10 border border-emerald-500/30 text-emerald-400">
            <FileSpreadsheet className="w-5 h-5" />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <h2 className="text-base font-semibold tracking-tight text-white">
                ZUGFeRD 2.3 &amp; XRechnung Cockpit
              </h2>
              {data && (
                <span className="px-2 py-0.5 text-xs font-mono font-medium rounded-full bg-blue-500/15 border border-blue-500/30 text-blue-300">
                  {data.profile}
                </span>
              )}
              {data?.is_hybrid_pdf_a3 && (
                <span className="px-2 py-0.5 text-xs font-medium rounded-full bg-emerald-500/15 border border-emerald-500/30 text-emerald-300">
                  Hybrid PDF/A-3
                </span>
              )}
            </div>
            <p className="text-xs text-slate-400">
              EN 16931-1:2017 &amp; § 14 UStG E-Rechnungs-Prüfstand · {filename}
            </p>
          </div>
        </div>

        {/* View Mode & Actions Group */}
        <div className="flex items-center space-x-3">
          {data && (
            <div className="flex items-center space-x-2">
              {/* Compliance Pills */}
              {data.validation_report.is_en16931_compliant ? (
                <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-emerald-500/15 text-emerald-300 border border-emerald-500/30">
                  <ShieldCheck className="w-3.5 h-3.5 mr-1" />
                  EN 16931
                </span>
              ) : (
                <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-rose-500/15 text-rose-300 border border-rose-500/30">
                  <AlertCircle className="w-3.5 h-3.5 mr-1" />
                  Beanstandet
                </span>
              )}

              {visualReconciliation && (
                <span
                  className={`inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium border ${
                    visualReconciliation.is_reconciled
                      ? "bg-cyan-500/15 text-cyan-300 border-cyan-500/30"
                      : "bg-amber-500/15 text-amber-300 border-amber-500/30"
                  }`}
                >
                  <Eye className="w-3.5 h-3.5 mr-1" />
                  Visual-Match {visualReconciliation.reconciliation_score_percent.toFixed(0)}%
                </span>
              )}

              {/* Layout Mode Toggles */}
              <div className="flex items-center bg-slate-900 border border-slate-700/80 rounded-lg p-0.5 text-xs">
                <button
                  onClick={() => setLayoutMode("preview")}
                  className={`px-2 py-1 rounded flex items-center space-x-1 transition-colors ${
                    layoutMode === "preview"
                      ? "bg-emerald-600 text-white font-medium"
                      : "text-slate-400 hover:text-slate-200"
                  }`}
                  title="Nur Belegsicht anzeigen"
                >
                  <PanelLeft className="w-3.5 h-3.5" />
                  <span className="hidden sm:inline">Beleg</span>
                </button>
                <button
                  onClick={() => setLayoutMode("split")}
                  className={`px-2 py-1 rounded flex items-center space-x-1 transition-colors ${
                    layoutMode === "split"
                      ? "bg-emerald-600 text-white font-medium"
                      : "text-slate-400 hover:text-slate-200"
                  }`}
                  title="Split-Screen (Beleg links, Cockpit rechts)"
                >
                  <Columns2 className="w-3.5 h-3.5" />
                  <span className="hidden sm:inline">Split-Screen</span>
                </button>
                <button
                  onClick={() => setLayoutMode("cockpit")}
                  className={`px-2 py-1 rounded flex items-center space-x-1 transition-colors ${
                    layoutMode === "cockpit"
                      ? "bg-emerald-600 text-white font-medium"
                      : "text-slate-400 hover:text-slate-200"
                  }`}
                  title="Nur Daten-Cockpit anzeigen"
                >
                  <PanelRight className="w-3.5 h-3.5" />
                  <span className="hidden sm:inline">Cockpit</span>
                </button>
              </div>

              {/* PDF Download Button */}
              <button
                onClick={handleDownloadCertificate}
                disabled={exportingPdf}
                className="inline-flex items-center px-3 py-1.5 rounded-lg text-xs font-medium bg-emerald-600 hover:bg-emerald-500 disabled:opacity-50 text-white shadow-sm transition-colors"
              >
                <Download className="w-3.5 h-3.5 mr-1.5" />
                {exportingPdf ? "Erzeuge PDF..." : "GoBD Prüfzertifikat PDF"}
              </button>
            </div>
          )}

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

      {loading ? (
        <div className="flex flex-col items-center justify-center flex-1 space-y-4">
          <RefreshCw className="w-8 h-8 text-emerald-400 animate-spin" />
          <p className="text-sm text-slate-400 font-mono">
            Initialisiere Split-Screen E-Invoice Inspector &amp; extrahiere XML-Metadaten...
          </p>
        </div>
      ) : error ? (
        <div className="p-6">
          <div className="p-4 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-300 flex items-start space-x-3">
            <XCircle className="w-5 h-5 flex-shrink-0 mt-0.5" />
            <div>
              <h4 className="font-semibold text-sm">ZUGFeRD Cockpit-Fehler</h4>
              <p className="text-xs text-rose-200/80 mt-1">{error}</p>
            </div>
          </div>
        </div>
      ) : data ? (
        <div className="flex flex-1 overflow-hidden">
          {/* ============================================================== */}
          {/* LEFT PANE: VISUAL INVOICE PREVIEW & OCR / VISUAL LAYER         */}
          {/* ============================================================== */}
          {(layoutMode === "split" || layoutMode === "preview") && (
            <div
              className={`flex flex-col border-r border-slate-800 bg-slate-950 overflow-hidden ${
                layoutMode === "preview" ? "w-full" : "w-1/2 lg:w-[48%]"
              }`}
            >
              {/* Left Pane Header */}
              <div className="px-4 py-2.5 border-b border-slate-800 bg-slate-900/60 flex items-center justify-between text-xs">
                <div className="flex items-center space-x-2 text-slate-300 font-medium">
                  <Eye className="w-4 h-4 text-cyan-400" />
                  <span>Sichtbeleg (Visuelle Ebene &amp; DIN 5008 Layout)</span>
                </div>
                <div className="flex items-center space-x-2 text-[11px] text-slate-400 font-mono">
                  <span>{data.is_hybrid_pdf_a3 ? "PDF/A-3 Hybrid" : "Visuelle Simulation"}</span>
                </div>
              </div>

              {/* Visual Invoice Canvas (DIN 5008 Inspired) */}
              <div className="flex-1 overflow-y-auto p-6 bg-slate-900/30">
                <div className="max-w-xl mx-auto bg-slate-900/90 border border-slate-800 rounded-xl p-6 shadow-xl space-y-6 text-xs text-slate-300">
                  {/* Sender Letterhead */}
                  <div className="flex items-start justify-between border-b border-slate-800/80 pb-4">
                    <div>
                      <div className="text-[11px] text-emerald-400 font-mono font-medium">
                        DIN 5008 · Rechnungssteller
                      </div>
                      <h3 className="text-sm font-bold text-white mt-0.5">{data.seller.name}</h3>
                      <p className="text-slate-400 text-[11px] mt-0.5">
                        {data.seller.postal_address?.line_one || "Taunusanlage 8"} ·{" "}
                        {data.seller.postal_address?.postcode} {data.seller.postal_address?.city_name} (
                        {data.seller.postal_address?.country_id})
                      </p>
                      <button
                        onClick={() => handleFieldHotspotClick("seller_vat_id")}
                        className="mt-1 text-[11px] font-mono text-cyan-300 hover:underline flex items-center space-x-1"
                      >
                        <span>USt-IdNr: {data.seller.vat_id || "Nicht angegeben"}</span>
                      </button>
                    </div>
                    <div className="text-right">
                      <span className="px-2.5 py-1 rounded bg-emerald-500/10 border border-emerald-500/30 text-emerald-300 font-mono font-bold text-xs">
                        {data.invoice_type_name_de}
                      </span>
                    </div>
                  </div>

                  {/* Recipient Window & Invoice Meta */}
                  <div className="grid grid-cols-2 gap-4">
                    <div className="p-3 rounded-lg bg-slate-950/60 border border-slate-800/80">
                      <div className="text-[10px] text-slate-500 font-mono">RECHNUNGSEMPFÄNGER</div>
                      <div className="font-semibold text-white mt-1">{data.buyer.name}</div>
                      <div className="text-[11px] text-slate-400 mt-0.5">
                        {data.buyer.postal_address?.line_one || "Marktplatz 1"}
                        <br />
                        {data.buyer.postal_address?.postcode} {data.buyer.postal_address?.city_name} (
                        {data.buyer.postal_address?.country_id || "DE"})
                      </div>
                    </div>

                    <div className="p-3 rounded-lg bg-slate-950/60 border border-slate-800/80 space-y-1.5">
                      <div>
                        <div className="text-[10px] text-slate-500 font-mono">RECHNUNGSNUMMER (BT-1)</div>
                        <button
                          onClick={() => handleFieldHotspotClick("invoice_number")}
                          className="font-mono font-bold text-white hover:text-cyan-300 transition-colors"
                        >
                          {data.invoice_number}
                        </button>
                      </div>
                      <div>
                        <div className="text-[10px] text-slate-500 font-mono">DATUM (BT-2)</div>
                        <button
                          onClick={() => handleFieldHotspotClick("issue_date")}
                          className="font-mono text-slate-300 hover:text-cyan-300 transition-colors"
                        >
                          {data.issue_date || "08.11.2026"}
                        </button>
                      </div>
                      {data.buyer_reference && (
                        <div>
                          <div className="text-[10px] text-slate-500 font-mono">LEITWEG-ID (BT-10)</div>
                          <button
                            onClick={() => handleFieldHotspotClick("buyer_reference")}
                            className="font-mono text-amber-300 hover:text-amber-200 transition-colors text-[11px]"
                          >
                            {data.buyer_reference}
                          </button>
                        </div>
                      )}
                    </div>
                  </div>

                  {/* Line Items Visual Strip */}
                  <div className="border border-slate-800 rounded-lg overflow-hidden">
                    <div className="bg-slate-950 px-3 py-2 border-b border-slate-800 text-[11px] font-medium text-slate-400 grid grid-cols-12">
                      <span className="col-span-1">Pos</span>
                      <span className="col-span-6">Beschreibung</span>
                      <span className="col-span-2 text-right">Menge</span>
                      <span className="col-span-3 text-right">Netto</span>
                    </div>
                    <div className="divide-y divide-slate-800/80 bg-slate-900/40">
                      {data.line_items.map((item, idx) => (
                        <div key={idx} className="px-3 py-2 text-[11px] grid grid-cols-12 items-center">
                          <span className="col-span-1 font-mono text-slate-400">{item.line_id}</span>
                          <span className="col-span-6 font-medium text-slate-200 truncate pr-2">
                            {item.item_name}
                          </span>
                          <span className="col-span-2 text-right font-mono text-slate-300">
                            {item.billed_quantity} {item.unit_code}
                          </span>
                          <span className="col-span-3 text-right font-mono text-slate-100 font-semibold">
                            {item.line_total_eur.toLocaleString("de-DE", {
                              style: "currency",
                              currency: data.currency_code,
                            })}
                          </span>
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* Monetary Totals Visual Box */}
                  <div className="p-3.5 rounded-lg bg-slate-950/80 border border-slate-800 space-y-1.5 font-mono text-xs">
                    <div className="flex justify-between text-slate-400">
                      <span>Nettobetrag (BT-109):</span>
                      <button
                        onClick={() => handleFieldHotspotClick("tax_basis_total")}
                        className="text-slate-200 hover:text-cyan-300"
                      >
                        {data.monetary_summation.tax_basis_total_amount_eur.toLocaleString("de-DE", {
                          style: "currency",
                          currency: data.currency_code,
                        })}
                      </button>
                    </div>
                    <div className="flex justify-between text-slate-400">
                      <span>Umsatzsteuer ({data.currency_code}):</span>
                      <button
                        onClick={() => handleFieldHotspotClick("tax_total")}
                        className="text-cyan-300 hover:underline"
                      >
                        {data.monetary_summation.tax_total_amount_eur.toLocaleString("de-DE", {
                          style: "currency",
                          currency: data.currency_code,
                        })}
                      </button>
                    </div>
                    <div className="flex justify-between text-sm font-bold pt-2 border-t border-slate-800 text-white">
                      <span>Gesamtbetrag Brutto (BT-112):</span>
                      <button
                        onClick={() => handleFieldHotspotClick("grand_total")}
                        className="text-emerald-400 hover:underline font-mono"
                      >
                        {data.monetary_summation.grand_total_amount_eur.toLocaleString("de-DE", {
                          style: "currency",
                          currency: data.currency_code,
                        })}
                      </button>
                    </div>
                  </div>

                  {/* Banking Footer */}
                  <div className="pt-3 border-t border-slate-800/80 flex items-center justify-between text-[11px] text-slate-400">
                    <div className="flex items-center space-x-2">
                      <Landmark className="w-3.5 h-3.5 text-slate-500" />
                      <span>IBAN:</span>
                      <button
                        onClick={() => handleFieldHotspotClick("iban")}
                        className="font-mono text-slate-300 hover:text-cyan-300"
                      >
                        {data.iban || "DE89370400440532013000"}
                      </button>
                    </div>
                    <span className="text-[10px] text-slate-500">GoBD Revisionsarchiv</span>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* ============================================================== */}
          {/* RIGHT PANE: INTERACTIVE E-INVOICE DATA COCKPIT & VALIDATOR     */}
          {/* ============================================================== */}
          {(layoutMode === "split" || layoutMode === "cockpit") && (
            <div
              className={`flex flex-col bg-slate-950 overflow-hidden ${
                layoutMode === "cockpit" ? "w-full" : "w-1/2 lg:w-[52%]"
              }`}
            >
              {/* Quick Metrics Bar */}
              <div className="grid grid-cols-2 md:grid-cols-4 gap-3 p-4 bg-slate-900/40 border-b border-slate-800/80 shrink-0">
                <div className="p-2.5 rounded-lg bg-slate-900/80 border border-slate-800">
                  <span className="text-[11px] font-medium text-slate-400">Rechnungsnummer</span>
                  <div className="text-sm font-semibold text-white font-mono mt-0.5 truncate">
                    {data.invoice_number}
                  </div>
                  <div className="text-[10px] text-slate-500 mt-0.5">Datum: {data.issue_date || "—"}</div>
                </div>

                <div className="p-2.5 rounded-lg bg-slate-900/80 border border-slate-800">
                  <span className="text-[11px] font-medium text-slate-400">Gesamtbetrag (Brutto)</span>
                  <div className="text-sm font-semibold text-emerald-400 font-mono mt-0.5">
                    {data.monetary_summation.grand_total_amount_eur.toLocaleString("de-DE", {
                      style: "currency",
                      currency: data.currency_code,
                    })}
                  </div>
                  <div className="text-[10px] text-slate-500 mt-0.5">
                    Netto: {data.monetary_summation.tax_basis_total_amount_eur.toFixed(2)} {data.currency_code}
                  </div>
                </div>

                <div className="p-2.5 rounded-lg bg-slate-900/80 border border-slate-800">
                  <span className="text-[11px] font-medium text-slate-400">USt-Betrag</span>
                  <div className="text-sm font-semibold text-blue-400 font-mono mt-0.5">
                    {data.monetary_summation.tax_total_amount_eur.toLocaleString("de-DE", {
                      style: "currency",
                      currency: data.currency_code,
                    })}
                  </div>
                  <div className="text-[10px] text-slate-500 mt-0.5">
                    {data.tax_subtotals.length} Teilbeträge deklariert
                  </div>
                </div>

                <div className="p-2.5 rounded-lg bg-slate-900/80 border border-slate-800">
                  <span className="text-[11px] font-medium text-slate-400">Leitweg-ID / B2G</span>
                  <div
                    className={`text-sm font-semibold font-mono mt-0.5 truncate ${
                      data.leitweg_validation?.is_valid ? "text-emerald-300" : "text-amber-300"
                    }`}
                  >
                    {data.buyer_reference || "— (B2B Standard)"}
                  </div>
                  <div className="text-[10px] text-slate-400 mt-0.5 truncate">
                    {data.leitweg_validation
                      ? data.leitweg_validation.is_valid
                        ? `MOD-97-10 OK · ${data.leitweg_validation.bundesland_or_authority}`
                        : "Prüfziffer ungültig"
                      : "Keine Leitweg-ID"}
                  </div>
                </div>
              </div>

              {/* Navigation Tabs Bar */}
              <div className="flex flex-wrap items-center gap-1 px-4 pt-2 border-b border-slate-800 bg-slate-900/60 shrink-0">
                <button
                  onClick={() => setActiveTab("reconciliation")}
                  className={`flex items-center space-x-1.5 px-3 py-2 text-xs font-medium border-b-2 transition-colors ${
                    activeTab === "reconciliation"
                      ? "border-cyan-400 text-cyan-300 bg-cyan-500/5"
                      : "border-transparent text-slate-400 hover:text-slate-200"
                  }`}
                >
                  <Eye className="w-3.5 h-3.5" />
                  <span>
                    Visueller Abgleich
                    {visualReconciliation ? ` (${visualReconciliation.reconciliation_score_percent.toFixed(0)}%)` : ""}
                  </span>
                </button>

                <button
                  onClick={() => setActiveTab("items")}
                  className={`flex items-center space-x-1.5 px-3 py-2 text-xs font-medium border-b-2 transition-colors ${
                    activeTab === "items"
                      ? "border-emerald-400 text-emerald-400 bg-emerald-500/5"
                      : "border-transparent text-slate-400 hover:text-slate-200"
                  }`}
                >
                  <Layers className="w-3.5 h-3.5" />
                  <span>Positionen ({data.line_items.length})</span>
                </button>

                <button
                  onClick={() => setActiveTab("totals")}
                  className={`flex items-center space-x-1.5 px-3 py-2 text-xs font-medium border-b-2 transition-colors ${
                    activeTab === "totals"
                      ? "border-emerald-400 text-emerald-400 bg-emerald-500/5"
                      : "border-transparent text-slate-400 hover:text-slate-200"
                  }`}
                >
                  <CreditCard className="w-3.5 h-3.5" />
                  <span>Summen &amp; Steuer</span>
                </button>

                <button
                  onClick={() => setActiveTab("vat")}
                  className={`flex items-center space-x-1.5 px-3 py-2 text-xs font-medium border-b-2 transition-colors ${
                    activeTab === "vat"
                      ? "border-emerald-400 text-emerald-400 bg-emerald-500/5"
                      : "border-transparent text-slate-400 hover:text-slate-200"
                  }`}
                >
                  <Receipt className="w-3.5 h-3.5" />
                  <span>
                    UStG § 14 &amp; § 13b
                    {data.vat_audit ? ` (${data.vat_audit.mandatory_fields_score_percent.toFixed(0)}%)` : ""}
                  </span>
                </button>

                <button
                  onClick={() => setActiveTab("validation")}
                  className={`flex items-center space-x-1.5 px-3 py-2 text-xs font-medium border-b-2 transition-colors ${
                    activeTab === "validation"
                      ? "border-emerald-400 text-emerald-400 bg-emerald-500/5"
                      : "border-transparent text-slate-400 hover:text-slate-200"
                  }`}
                >
                  <Scale className="w-3.5 h-3.5" />
                  <span>
                    EN 16931 ({data.validation_report.passed_rules_count}/{data.validation_report.total_rules_evaluated})
                  </span>
                </button>

                <button
                  onClick={() => setActiveTab("xml")}
                  className={`flex items-center space-x-1.5 px-3 py-2 text-xs font-medium border-b-2 transition-colors ${
                    activeTab === "xml"
                      ? "border-emerald-400 text-emerald-400 bg-emerald-500/5"
                      : "border-transparent text-slate-400 hover:text-slate-200"
                  }`}
                >
                  <Code2 className="w-3.5 h-3.5" />
                  <span>Live XML-Studio</span>
                </button>
              </div>

              {/* Tab Contents Area */}
              <div className="flex-1 overflow-y-auto p-4 space-y-4">
                {/* -------------------------------------------------------- */}
                {/* TAB: VISUELLER ABGLEICH (PDF VS. XML) - DAY 26 CORE      */}
                {/* -------------------------------------------------------- */}
                {activeTab === "reconciliation" && (
                  <div className="space-y-4">
                    {/* Reconciliation Header Card */}
                    {visualReconciliation ? (
                      <div className="p-4 rounded-xl border border-slate-800 bg-slate-900/60 space-y-3">
                        <div className="flex items-center justify-between">
                          <div className="flex items-center space-x-2">
                            <FileCheck className="w-5 h-5 text-cyan-400" />
                            <div>
                              <h3 className="text-sm font-semibold text-white">
                                Visueller vs. Strukturierter Belegabgleich
                              </h3>
                              <p className="text-xs text-slate-400 mt-0.5">
                                Abgleich zwischen menschlich sichtbarem PDF-Beleg und eingebetteter Factur-X /
                                ZUGFeRD XML-Nutzlast.
                              </p>
                            </div>
                          </div>
                          <div className="text-right">
                            <span
                              className={`text-lg font-bold font-mono ${
                                visualReconciliation.is_reconciled ? "text-emerald-400" : "text-amber-400"
                              }`}
                            >
                              {visualReconciliation.reconciliation_score_percent.toFixed(0)}%
                            </span>
                            <div className="text-[11px] text-slate-500">Übereinstimmung</div>
                          </div>
                        </div>

                        <div className="p-2.5 rounded-lg bg-slate-950/80 border border-slate-800/80 text-xs text-slate-300">
                          {visualReconciliation.summary_de}
                        </div>
                      </div>
                    ) : reconciling ? (
                      <div className="p-6 text-center text-xs text-slate-400 flex items-center justify-center space-x-2">
                        <RefreshCw className="w-4 h-4 text-cyan-400 animate-spin" />
                        <span>Führe optischen Abgleich zwischen PDF und XML durch...</span>
                      </div>
                    ) : null}

                    {/* Field-by-Field Reconciliation Table */}
                    {visualReconciliation && (
                      <div className="rounded-xl border border-slate-800 bg-slate-900/60 overflow-hidden">
                        <table className="w-full text-left text-xs">
                          <thead className="bg-slate-900 border-b border-slate-800 text-slate-400">
                            <tr>
                              <th className="py-2.5 px-3 font-medium">Rechnungsfeld</th>
                              <th className="py-2.5 px-3 font-medium">XML-Wert (Strukturiert)</th>
                              <th className="py-2.5 px-3 font-medium">Sichtbeleg-Wert (PDF)</th>
                              <th className="py-2.5 px-3 font-medium text-right">Status</th>
                            </tr>
                          </thead>
                          <tbody className="divide-y divide-slate-800/80">
                            {visualReconciliation.fields.map((field, idx) => (
                              <tr
                                key={idx}
                                id={`rec-row-${field.field_key}`}
                                className={`transition-colors ${
                                  highlightedField === field.field_key
                                    ? "bg-cyan-500/15"
                                    : "hover:bg-slate-800/40"
                                }`}
                              >
                                <td className="py-2.5 px-3 font-medium text-slate-200">
                                  <div>{field.field_name_de}</div>
                                  <div className="text-[10px] text-slate-500 font-mono">{field.field_key}</div>
                                </td>
                                <td className="py-2.5 px-3 font-mono text-cyan-300 font-semibold max-w-[160px] truncate">
                                  {field.xml_value}
                                </td>
                                <td className="py-2.5 px-3 font-mono text-slate-300 max-w-[160px] truncate">
                                  {field.pdf_visual_value || "—"}
                                </td>
                                <td className="py-2.5 px-3 text-right">
                                  {field.is_match ? (
                                    <span className="inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-medium bg-emerald-500/15 text-emerald-300 border border-emerald-500/30">
                                      <CheckCircle2 className="w-3 h-3 mr-1" />
                                      Match
                                    </span>
                                  ) : (
                                    <span className="inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-medium bg-rose-500/15 text-rose-300 border border-rose-500/30">
                                      <AlertCircle className="w-3 h-3 mr-1" />
                                      Abweichung
                                    </span>
                                  )}
                                </td>
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      </div>
                    )}
                  </div>
                )}

                {/* -------------------------------------------------------- */}
                {/* TAB: POSITIONSÜBERSICHT (LINE ITEMS)                     */}
                {/* -------------------------------------------------------- */}
                {activeTab === "items" && (
                  <div className="rounded-xl border border-slate-800 bg-slate-900/60 overflow-hidden">
                    <div className="overflow-x-auto">
                      <table className="w-full text-left text-xs">
                        <thead className="bg-slate-900 border-b border-slate-800 text-slate-400">
                          <tr>
                            <th className="py-2.5 px-3 font-medium">Pos.</th>
                            <th className="py-2.5 px-3 font-medium">Bezeichnung</th>
                            <th className="py-2.5 px-3 font-medium text-right">Menge</th>
                            <th className="py-2.5 px-3 font-medium text-right">Einzelpreis</th>
                            <th className="py-2.5 px-3 font-medium text-right">USt</th>
                            <th className="py-2.5 px-3 font-medium text-right">Netto Gesamt</th>
                          </tr>
                        </thead>
                        <tbody className="divide-y divide-slate-800 font-mono">
                          {data.line_items.map((item, idx) => (
                            <tr key={idx} className="hover:bg-slate-800/40 transition-colors">
                              <td className="py-2.5 px-3 text-slate-400 font-sans">{item.line_id}</td>
                              <td className="py-2.5 px-3 font-sans font-medium text-white">
                                <div>{item.item_name}</div>
                                {item.item_description && (
                                  <div className="text-[11px] text-slate-400 mt-0.5">{item.item_description}</div>
                                )}
                              </td>
                              <td className="py-2.5 px-3 text-right text-slate-200">
                                {item.billed_quantity} {item.unit_code}
                              </td>
                              <td className="py-2.5 px-3 text-right text-slate-200">
                                {item.net_price_eur.toFixed(2)}
                              </td>
                              <td className="py-2.5 px-3 text-right text-slate-400">
                                {item.vat_rate_percent.toFixed(0)}%
                              </td>
                              <td className="py-2.5 px-3 text-right text-emerald-400 font-bold">
                                {item.line_total_eur.toFixed(2)}
                              </td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  </div>
                )}

                {/* -------------------------------------------------------- */}
                {/* TAB: STEUER- & SUMMENAUFSTELLUNG                         */}
                {/* -------------------------------------------------------- */}
                {activeTab === "totals" && (
                  <div className="space-y-4">
                    <div className="p-4 rounded-xl border border-slate-800 bg-slate-900/60 space-y-3 font-mono text-xs">
                      <div className="text-xs font-sans font-semibold text-white">
                        Monetäre Gesamtabstimmung (BG-22)
                      </div>
                      <div className="space-y-2">
                        <div className="flex justify-between text-slate-400">
                          <span>Summe der Positionsbeträge (BT-106):</span>
                          <span className="text-white">
                            {data.monetary_summation.line_total_amount_eur.toFixed(2)} {data.currency_code}
                          </span>
                        </div>
                        <div className="flex justify-between text-slate-400">
                          <span>Gesamt-Zuschläge (BT-108):</span>
                          <span>+{data.monetary_summation.charge_total_amount_eur.toFixed(2)}</span>
                        </div>
                        <div className="flex justify-between text-slate-400">
                          <span>Gesamt-Nachlässe (BT-107):</span>
                          <span>-{data.monetary_summation.allowance_total_amount_eur.toFixed(2)}</span>
                        </div>
                        <div className="flex justify-between text-slate-300 font-semibold pt-1 border-t border-slate-800">
                          <span>Steuerbemessungsgrundlage Netto (BT-109):</span>
                          <span>
                            {data.monetary_summation.tax_basis_total_amount_eur.toFixed(2)} {data.currency_code}
                          </span>
                        </div>
                        <div className="flex justify-between text-blue-400 font-semibold">
                          <span>Umsatzsteuer Gesamtbetrag (BT-110):</span>
                          <span>
                            +{data.monetary_summation.tax_total_amount_eur.toFixed(2)} {data.currency_code}
                          </span>
                        </div>
                        <div className="flex justify-between text-emerald-400 font-bold text-sm pt-2 border-t border-slate-700">
                          <span>Rechnungsgesamtbetrag Brutto (BT-112):</span>
                          <span>
                            {data.monetary_summation.grand_total_amount_eur.toFixed(2)} {data.currency_code}
                          </span>
                        </div>
                        <div className="flex justify-between text-slate-400">
                          <span>Bereits geleistete Vorauszahlung (BT-113):</span>
                          <span>-{data.monetary_summation.prepaid_amount_eur.toFixed(2)}</span>
                        </div>
                        <div className="flex justify-between text-white font-bold text-sm pt-1 border-t border-slate-800">
                          <span>Fälliger Zahlbetrag (BT-115):</span>
                          <span className="text-cyan-300">
                            {data.monetary_summation.due_payable_amount_eur.toFixed(2)} {data.currency_code}
                          </span>
                        </div>
                      </div>
                    </div>

                    {/* Tax Subtotals Strip */}
                    <div className="p-4 rounded-xl border border-slate-800 bg-slate-900/60 space-y-2">
                      <div className="text-xs font-semibold text-white">
                        Umsatzsteuer-Teilbeträge nach Kategorie (BG-23)
                      </div>
                      <div className="space-y-2">
                        {data.tax_subtotals.map((sub, idx) => (
                          <div
                            key={idx}
                            className="p-3 rounded-lg bg-slate-950 border border-slate-800/80 flex items-center justify-between font-mono text-xs"
                          >
                            <div>
                              <span className="font-sans font-medium text-slate-200">
                                Kategorie {sub.tax_category_code} ({sub.tax_rate_percent.toFixed(1)}%)
                              </span>
                              {sub.exemption_reason && (
                                <div className="text-[11px] text-slate-500 font-sans mt-0.5">
                                  Grund: {sub.exemption_reason}
                                </div>
                              )}
                            </div>
                            <div className="text-right">
                              <div className="text-slate-400 text-[11px]">
                                Bemessung: {sub.taxable_amount_eur.toFixed(2)}
                              </div>
                              <div className="text-emerald-400 font-bold">
                                Steuer: {sub.tax_amount_eur.toFixed(2)} {data.currency_code}
                              </div>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>
                )}

                {/* -------------------------------------------------------- */}
                {/* TAB: USTG § 14 & REVERSE-CHARGE                         */}
                {/* -------------------------------------------------------- */}
                {activeTab === "vat" && (
                  <div className="space-y-4">
                    {data.vat_audit ? (
                      <>
                        <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
                          <div className="p-3 rounded-xl border border-slate-800 bg-slate-900/60">
                            <div className="text-[11px] text-slate-400">§ 14 UStG Status</div>
                            <div
                              className={`text-sm font-bold mt-0.5 ${
                                data.vat_audit.is_ustg_compliant ? "text-emerald-400" : "text-rose-400"
                              }`}
                            >
                              {data.vat_audit.is_ustg_compliant ? "Konform" : "Prüfung nötig"}
                            </div>
                          </div>
                          <div className="p-3 rounded-xl border border-slate-800 bg-slate-900/60">
                            <div className="text-[11px] text-slate-400">Pflichtangaben-Score</div>
                            <div className="text-sm font-bold font-mono text-white mt-0.5">
                              {data.vat_audit.mandatory_fields_score_percent.toFixed(0)}%
                            </div>
                          </div>
                          <div className="p-3 rounded-xl border border-slate-800 bg-slate-900/60">
                            <div className="text-[11px] text-slate-400">Nachgerechnete USt</div>
                            <div className="text-sm font-bold font-mono text-cyan-300 mt-0.5">
                              {data.vat_audit.recalculated_tax_total_eur.toFixed(2)} {data.currency_code}
                            </div>
                          </div>
                          <div className="p-3 rounded-xl border border-slate-800 bg-slate-900/60">
                            <div className="text-[11px] text-slate-400">Steuerdifferenz</div>
                            <div
                              className={`text-sm font-bold font-mono mt-0.5 ${
                                data.vat_audit.tax_discrepancy_eur > 0.02 ? "text-rose-400" : "text-emerald-400"
                              }`}
                            >
                              {data.vat_audit.tax_discrepancy_eur.toFixed(2)} {data.currency_code}
                            </div>
                          </div>
                        </div>

                        <div className="flex flex-wrap gap-2">
                          {data.vat_audit.is_small_value_invoice && (
                            <span className="px-2.5 py-1 rounded-full text-xs font-medium bg-indigo-500/15 border border-indigo-500/30 text-indigo-300">
                              Kleinbetragsrechnung ≤ 250 EUR (§ 33 UStDV)
                            </span>
                          )}
                          {data.vat_audit.reverse_charge_detected && (
                            <span className="px-2.5 py-1 rounded-full text-xs font-medium bg-amber-500/15 border border-amber-500/30 text-amber-300">
                              Reverse Charge (§ 13b UStG · AE)
                            </span>
                          )}
                          {data.vat_audit.intra_community_supply_detected && (
                            <span className="px-2.5 py-1 rounded-full text-xs font-medium bg-cyan-500/15 border border-cyan-500/30 text-cyan-300">
                              Innergemeinschaftliche Lieferung (§ 6a UStG · K)
                            </span>
                          )}
                        </div>

                        <div className="p-3 rounded-xl border border-slate-800 bg-slate-900/60 text-xs text-slate-300">
                          {data.vat_audit.audit_summary_de}
                        </div>

                        <div className="space-y-2">
                          {data.vat_audit.findings.length === 0 ? (
                            <div className="p-6 text-center rounded-xl bg-emerald-500/5 border border-emerald-500/20 text-emerald-300 text-xs">
                              Alle UStG-Pflichtangaben (§ 14 Abs. 4 UStG) sowie Steuersätze (§ 12 UStG) sind
                              vollständig und rechnerisch einwandfrei.
                            </div>
                          ) : (
                            data.vat_audit.findings.map((finding, idx) => (
                              <div
                                key={idx}
                                className={`p-3 rounded-xl border text-xs flex items-start space-x-3 ${
                                  finding.severity === "CRITICAL"
                                    ? "bg-rose-500/10 border-rose-500/30 text-rose-200"
                                    : finding.severity === "WARNING"
                                      ? "bg-amber-500/10 border-amber-500/30 text-amber-200"
                                      : "bg-slate-800/70 border-slate-700 text-slate-300"
                                }`}
                              >
                                <AlertCircle className="w-4 h-4 flex-shrink-0 mt-0.5" />
                                <div className="flex-1 space-y-1">
                                  <div className="flex items-center space-x-2 font-mono">
                                    <span className="font-bold">{finding.code}</span>
                                    <span className="text-slate-500">·</span>
                                    <span>{finding.statutory_reference}</span>
                                  </div>
                                  <div>{finding.description_de}</div>
                                </div>
                              </div>
                            ))
                          )}
                        </div>
                      </>
                    ) : (
                      <div className="p-6 text-center text-xs text-slate-400">
                        Keine UStG-Prüfdaten verfügbar.
                      </div>
                    )}
                  </div>
                )}

                {/* -------------------------------------------------------- */}
                {/* TAB: EN 16931 & LEITWEG-ID                              */}
                {/* -------------------------------------------------------- */}
                {activeTab === "validation" && (
                  <div className="space-y-4">
                    {/* Leitweg-ID Interactive Test Widget */}
                    <div className="p-4 rounded-xl border border-slate-800 bg-slate-900/60 space-y-3">
                      <div className="flex items-center space-x-2 text-xs font-semibold text-white">
                        <Route className="w-4 h-4 text-cyan-400" />
                        <span>Leitweg-ID &amp; Behörden-Routing (§ 4 E-Rech-VO · ISO 7064 MOD-97-10)</span>
                      </div>
                      <form onSubmit={handleCheckCustomLeitweg} className="flex items-center space-x-2">
                        <input
                          type="text"
                          value={leitwegInput}
                          onChange={(e) => setLeitwegInput(e.target.value)}
                          placeholder="Leitweg-ID prüfen (z.B. 04011000-12345-03 oder 991-12345-64)"
                          className="flex-1 bg-slate-950 border border-slate-700 rounded-lg px-3 py-1.5 text-xs font-mono text-slate-200 placeholder:text-slate-500 focus:outline-none focus:border-cyan-500"
                        />
                        <button
                          type="submit"
                          disabled={testingLeitweg || !leitwegInput.trim()}
                          className="px-3 py-1.5 rounded-lg text-xs font-medium bg-slate-800 hover:bg-slate-700 disabled:opacity-50 text-cyan-300 border border-slate-700 transition-colors"
                        >
                          {testingLeitweg ? "Prüfe..." : "MOD-97-10 Testen"}
                        </button>
                      </form>
                      {leitwegTestResult && (
                        <div
                          className={`p-3 rounded-lg border text-xs ${
                            leitwegTestResult.is_valid
                              ? "bg-emerald-500/10 border-emerald-500/30 text-emerald-300"
                              : "bg-rose-500/10 border-rose-500/30 text-rose-300"
                          }`}
                        >
                          <div className="font-mono font-bold">{leitwegTestResult.raw_id}</div>
                          <div className="mt-0.5">
                            {leitwegTestResult.is_valid
                              ? `${leitwegTestResult.federal_entity_type}: ${leitwegTestResult.bundesland_or_authority} · Portal: ${leitwegTestResult.submission_portal}`
                              : leitwegTestResult.errors.join("; ")}
                          </div>
                        </div>
                      )}
                    </div>

                    {/* EN 16931 Issues List */}
                    <div className="space-y-2">
                      {data.validation_report.issues.length === 0 ? (
                        <div className="p-6 text-center rounded-xl bg-emerald-500/5 border border-emerald-500/20 text-emerald-300 text-xs space-y-1">
                          <CheckCircle2 className="w-6 h-6 mx-auto text-emerald-400" />
                          <div className="font-semibold">Vollständig EN 16931-1 konform</div>
                          <p className="text-slate-400">
                            Alle {data.validation_report.total_rules_evaluated} Konformitätsregeln wurden ohne
                            Beanstandung bestanden.
                          </p>
                        </div>
                      ) : (
                        data.validation_report.issues.map((issue, idx) => (
                          <div
                            key={idx}
                            className={`p-3 rounded-xl border text-xs flex items-start space-x-3 ${
                              issue.severity === "ERROR"
                                ? "bg-rose-500/10 border-rose-500/30 text-rose-300"
                                : "bg-amber-500/10 border-amber-500/30 text-amber-300"
                            }`}
                          >
                            <AlertCircle className="w-4 h-4 flex-shrink-0 mt-0.5" />
                            <div>
                              <div className="font-mono font-bold">
                                [{issue.severity}] {issue.code} · {issue.rule_id}
                              </div>
                              <div className="mt-1 text-slate-200">{issue.description}</div>
                              <div className="text-[10px] text-slate-400 font-mono mt-0.5">
                                Rechtsnorm: {issue.statutory_reference}
                              </div>
                            </div>
                          </div>
                        ))
                      )}
                    </div>
                  </div>
                )}

                {/* -------------------------------------------------------- */}
                {/* TAB: LIVE XML-STUDIO & VALIDATOR - DAY 26 UPGRADE        */}
                {/* -------------------------------------------------------- */}
                {activeTab === "xml" && (
                  <div className="space-y-3">
                    {/* Sample Profile Switcher Bar */}
                    <div className="p-3 rounded-xl bg-slate-900 border border-slate-800 flex flex-wrap items-center justify-between gap-2 text-xs">
                      <div className="flex items-center space-x-2">
                        <Sparkles className="w-4 h-4 text-emerald-400" />
                        <span className="font-medium text-slate-300">Musterprofil wählen:</span>
                        <select
                          value={selectedProfileId}
                          onChange={(e) => handleLoadSampleProfile(e.target.value)}
                          className="bg-slate-950 border border-slate-700 text-slate-200 rounded-md px-2.5 py-1 font-mono text-xs focus:outline-none focus:border-emerald-500"
                        >
                          {sampleProfiles.map((p) => (
                            <option key={p.profile_id} value={p.profile_id}>
                              {p.name}
                            </option>
                          ))}
                        </select>
                      </div>

                      <div className="flex items-center space-x-2">
                        <button
                          onClick={handleValidateEditedXml}
                          disabled={validatingXml}
                          className="flex items-center space-x-1.5 px-3 py-1 rounded-md bg-emerald-600 hover:bg-emerald-500 disabled:opacity-50 text-white font-medium text-xs shadow transition-colors"
                        >
                          <Play className="w-3 h-3 fill-current" />
                          <span>{validatingXml ? "Validiere..." : "XML Live Prüfen"}</span>
                        </button>
                        <button
                          onClick={handleCopyXml}
                          className="flex items-center space-x-1 px-2.5 py-1 rounded-md bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs transition-colors"
                        >
                          <Copy className="w-3 h-3" />
                          <span>{copied ? "Kopiert!" : "Kopieren"}</span>
                        </button>
                      </div>
                    </div>

                    {xmlStatusMessage && (
                      <div className="p-2.5 rounded-lg bg-emerald-500/10 border border-emerald-500/30 text-emerald-300 text-xs font-mono">
                        {xmlStatusMessage}
                      </div>
                    )}

                    {/* Live Editable XML Code Area */}
                    <div className="rounded-xl border border-slate-800 bg-slate-950 overflow-hidden flex flex-col h-[420px]">
                      <div className="px-3 py-1.5 bg-slate-900/80 border-b border-slate-800 text-[11px] font-mono text-slate-400 flex items-center justify-between">
                        <span>{data.xml_filename || "factur-x.xml"} (Syntax: {data.validation_report.syntax_format})</span>
                        <span>{xmlContent.length} Zeichen</span>
                      </div>
                      <textarea
                        value={xmlContent}
                        onChange={(e) => setXmlContent(e.target.value)}
                        className="flex-1 w-full bg-slate-950 p-4 font-mono text-[11px] text-slate-200 resize-none focus:outline-none focus:ring-1 focus:ring-emerald-500 selection:bg-emerald-500/30 leading-relaxed overflow-y-auto"
                        placeholder="XML hier einfügen..."
                        spellCheck={false}
                      />
                    </div>
                  </div>
                )}
              </div>
            </div>
          )}
        </div>
      ) : null}
    </div>
  );
}

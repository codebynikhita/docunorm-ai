"use client";

import React, { useEffect, useState } from "react";
import {
  AlertCircle,
  Building2,
  CheckCircle2,
  Code2,
  Copy,
  CreditCard,
  Download,
  FileSpreadsheet,
  FileText,
  Landmark,
  Layers,
  Receipt,
  RefreshCw,
  Route,
  Scale,
  ShieldCheck,
  XCircle,
} from "lucide-react";
import {
  downloadZugferdCertificatePdf,
  getZugferdInvoice,
  LeitwegValidationResult,
  validateLeitwegId,
  ZugferdInvoiceExtraction,
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
  const [activeTab, setActiveTab] = useState<"items" | "totals" | "vat" | "validation" | "xml">("items");
  const [copied, setCopied] = useState<boolean>(false);
  const [exportingPdf, setExportingPdf] = useState<boolean>(false);
  const [leitwegInput, setLeitwegInput] = useState<string>("");
  const [leitwegTestResult, setLeitwegTestResult] = useState<LeitwegValidationResult | null>(null);
  const [testingLeitweg, setTestingLeitweg] = useState<boolean>(false);

  useEffect(() => {
    let isMounted = true;
    async function loadData() {
      try {
        setLoading(true);
        setError(null);
        const res = await getZugferdInvoice(documentId);
        if (isMounted) {
          setData(res);
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
    if (data?.raw_xml_content) {
      navigator.clipboard.writeText(data.raw_xml_content);
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

  return (
    <div className="flex flex-col h-full bg-slate-950 text-slate-100 overflow-hidden">
      {/* Top Header Bar */}
      <div className="flex items-center justify-between px-6 py-4 border-b border-slate-800 bg-slate-900/60 backdrop-blur-md">
        <div className="flex items-center space-x-3">
          <div className="p-2 rounded-lg bg-emerald-500/10 border border-emerald-500/30 text-emerald-400">
            <FileSpreadsheet className="w-5 h-5" />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <h2 className="text-lg font-semibold tracking-tight text-white">
                ZUGFeRD 2.3 / Factur-X Inspector
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
              EN 16931-1:2017 &amp; § 14 UStG E-Rechnungs-Konformität · {filename}
            </p>
          </div>
        </div>

        <div className="flex items-center space-x-3">
          {data && (
            <div className="flex items-center space-x-2">
              {data.validation_report.is_en16931_compliant ? (
                <span className="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-medium bg-emerald-500/15 text-emerald-300 border border-emerald-500/30">
                  <ShieldCheck className="w-3.5 h-3.5 mr-1" />
                  EN 16931 Konform
                </span>
              ) : (
                <span className="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-medium bg-rose-500/15 text-rose-300 border border-rose-500/30">
                  <AlertCircle className="w-3.5 h-3.5 mr-1" />
                  Prüfung erforderlich
                </span>
              )}

              {data.validation_report.has_math_discrepancy ? (
                <span className="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-medium bg-amber-500/15 text-amber-300 border border-amber-500/30">
                  <AlertCircle className="w-3.5 h-3.5 mr-1" />
                  Rechenabweichung
                </span>
              ) : (
                <span className="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-medium bg-cyan-500/15 text-cyan-300 border border-cyan-500/30">
                  <CheckCircle2 className="w-3.5 h-3.5 mr-1" />
                  Mathematisch exakt
                </span>
              )}

              {data.vat_audit && (
                <span
                  className={`inline-flex items-center px-2.5 py-1 rounded-full text-xs font-medium border ${
                    data.vat_audit.is_ustg_compliant
                      ? "bg-emerald-500/10 text-emerald-300 border-emerald-500/30"
                      : "bg-rose-500/15 text-rose-300 border-rose-500/30"
                  }`}
                >
                  <Receipt className="w-3.5 h-3.5 mr-1" />
                  {data.vat_audit.is_ustg_compliant ? "§ 14 UStG OK" : "§ 14 UStG Prüffall"}
                </span>
              )}

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
            Extrahiere Factur-X / ZUGFeRD XML &amp; berechne EN 16931 Validierung...
          </p>
        </div>
      ) : error ? (
        <div className="p-6">
          <div className="p-4 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-300 flex items-start space-x-3">
            <XCircle className="w-5 h-5 flex-shrink-0 mt-0.5" />
            <div>
              <h4 className="font-semibold text-sm">ZUGFeRD Parsing-Fehler</h4>
              <p className="text-xs text-rose-200/80 mt-1">{error}</p>
            </div>
          </div>
        </div>
      ) : data ? (
        <div className="flex flex-col flex-1 overflow-hidden">
          {/* Quick Metrics Bar */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 p-6 bg-slate-900/30 border-b border-slate-800/80">
            <div className="p-3.5 rounded-xl bg-slate-900/80 border border-slate-800">
              <span className="text-xs font-medium text-slate-400">Rechnungsnummer</span>
              <div className="text-base font-semibold text-white font-mono mt-0.5">
                {data.invoice_number}
              </div>
              <div className="text-[11px] text-slate-500 mt-1">
                Datum: {data.issue_date || "—"}
              </div>
            </div>

            <div className="p-3.5 rounded-xl bg-slate-900/80 border border-slate-800">
              <span className="text-xs font-medium text-slate-400">Rechnungsgesamtbetrag (Brutto)</span>
              <div className="text-base font-semibold text-emerald-400 font-mono mt-0.5">
                {data.monetary_summation.grand_total_amount_eur.toLocaleString("de-DE", {
                  style: "currency",
                  currency: data.currency_code,
                })}
              </div>
              <div className="text-[11px] text-slate-500 mt-1">
                Netto: {data.monetary_summation.tax_basis_total_amount_eur.toLocaleString("de-DE", {
                  style: "currency",
                  currency: data.currency_code,
                })}
              </div>
            </div>

            <div className="p-3.5 rounded-xl bg-slate-900/80 border border-slate-800">
              <span className="text-xs font-medium text-slate-400">Umsatzsteuer ({data.currency_code})</span>
              <div className="text-base font-semibold text-blue-400 font-mono mt-0.5">
                {data.monetary_summation.tax_total_amount_eur.toLocaleString("de-DE", {
                  style: "currency",
                  currency: data.currency_code,
                })}
              </div>
              <div className="text-[11px] text-slate-500 mt-1">
                {data.tax_subtotals.length} Steuersätze deklariert
              </div>
            </div>

            <div className="p-3.5 rounded-xl bg-slate-900/80 border border-slate-800">
              <span className="text-xs font-medium text-slate-400">Käuferreferenz / Leitweg-ID</span>
              <div
                className={`text-base font-semibold font-mono mt-0.5 truncate ${
                  data.leitweg_validation
                    ? data.leitweg_validation.is_valid
                      ? "text-emerald-300"
                      : "text-rose-300"
                    : "text-amber-300"
                }`}
                title={data.buyer_reference || "Nicht angegeben"}
              >
                {data.buyer_reference || "— (Keine Leitweg-ID)"}
              </div>
              <div className="text-[11px] text-slate-400 mt-1 truncate">
                {data.leitweg_validation
                  ? data.leitweg_validation.is_valid
                    ? `MOD-97-10 OK · ${data.leitweg_validation.bundesland_or_authority}`
                    : "Prüfziffer ungültig (MOD-97-10)"
                  : data.buyer_reference
                    ? "Käuferreferenz hinterlegt"
                    : "B2B Standard"}
              </div>
            </div>
          </div>

          {/* Parties Cards (Seller / Buyer) */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 px-6 py-4 bg-slate-950 border-b border-slate-800/80">
            {/* Seller */}
            <div className="p-4 rounded-xl bg-slate-900/50 border border-slate-800/90">
              <div className="flex items-center space-x-2 text-xs font-semibold text-slate-300 mb-2">
                <Building2 className="w-4 h-4 text-emerald-400" />
                <span>RECHNUNGSSTELLER (VERKÄUFER)</span>
              </div>
              <div className="text-sm font-semibold text-white">{data.seller.name}</div>
              <div className="text-xs text-slate-400 mt-1">
                {data.seller.postal_address?.line_one},{" "}
                {data.seller.postal_address?.postcode} {data.seller.postal_address?.city_name} (
                {data.seller.postal_address?.country_id})
              </div>
              <div className="flex items-center space-x-3 mt-2 text-xs font-mono text-slate-300">
                {data.seller.vat_id && (
                  <span className="bg-slate-800 px-2 py-0.5 rounded">
                    USt-IdNr: {data.seller.vat_id}
                  </span>
                )}
                {data.seller.contact_email && (
                  <span className="text-slate-400 font-sans">
                    ✉️ {data.seller.contact_email}
                  </span>
                )}
              </div>
            </div>

            {/* Buyer */}
            <div className="p-4 rounded-xl bg-slate-900/50 border border-slate-800/90">
              <div className="flex items-center space-x-2 text-xs font-semibold text-slate-300 mb-2">
                <Landmark className="w-4 h-4 text-blue-400" />
                <span>RECHNUNGSEMPFÄNGER (KÄUFER)</span>
              </div>
              <div className="text-sm font-semibold text-white">{data.buyer.name}</div>
              <div className="text-xs text-slate-400 mt-1">
                {data.buyer.postal_address?.line_one || "Anschrift vorhanden"},{" "}
                {data.buyer.postal_address?.postcode} {data.buyer.postal_address?.city_name} (
                {data.buyer.postal_address?.country_id || "DE"})
              </div>
              <div className="flex items-center space-x-3 mt-2 text-xs font-mono text-slate-300">
                {data.buyer.vat_id ? (
                  <span className="bg-slate-800 px-2 py-0.5 rounded">
                    USt-IdNr: {data.buyer.vat_id}
                  </span>
                ) : (
                  <span className="text-slate-500 font-sans">Keine USt-IdNr deklariert</span>
                )}
                {data.buyer_reference && (
                  <span
                    className={`px-2 py-0.5 rounded border ${
                      data.leitweg_validation?.is_valid
                        ? "bg-emerald-500/15 border-emerald-500/30 text-emerald-300"
                        : "bg-blue-500/15 border-blue-500/30 text-blue-300"
                    }`}
                  >
                    Leitweg-ID: {data.buyer_reference}
                    {data.leitweg_validation && (
                      <span className="ml-1.5 font-sans text-[10px] opacity-90">
                        {data.leitweg_validation.checksum_valid ? "· MOD-97-10 OK" : "· Prüfziffer ungültig"}
                      </span>
                    )}
                  </span>
                )}
              </div>
              {data.leitweg_validation && (
                <div className="mt-2.5 pt-2 border-t border-slate-800/80 flex items-start space-x-2 text-[11px] text-slate-400">
                  <Route className="w-3.5 h-3.5 text-cyan-400 mt-0.5 flex-shrink-0" />
                  <div className="min-w-0 flex-1">
                    <span className="text-slate-200 font-medium">
                      {data.leitweg_validation.federal_entity_type}: {data.leitweg_validation.bundesland_or_authority}
                    </span>
                    <div className="text-slate-400 truncate">
                      Portal: {data.leitweg_validation.submission_portal}
                    </div>
                  </div>
                </div>
              )}

              <form onSubmit={handleCheckCustomLeitweg} className="mt-3 pt-2.5 border-t border-slate-800/80 flex items-center space-x-2">
                <input
                  type="text"
                  value={leitwegInput}
                  onChange={(e) => setLeitwegInput(e.target.value)}
                  placeholder="Leitweg-ID testen (z.B. 991-12345-64)"
                  className="flex-1 bg-slate-950 border border-slate-700/80 rounded-md px-2.5 py-1 text-xs font-mono text-slate-200 placeholder:text-slate-500 focus:outline-none focus:border-cyan-500"
                />
                <button
                  type="submit"
                  disabled={testingLeitweg || !leitwegInput.trim()}
                  className="px-2.5 py-1 rounded-md text-xs font-medium bg-slate-800 hover:bg-slate-700 disabled:opacity-50 text-cyan-300 border border-slate-700 transition-colors"
                >
                  {testingLeitweg ? "Prüfe..." : "MOD-97-10 Check"}
                </button>
              </form>
              {leitwegTestResult && (
                <div
                  className={`mt-2 p-2 rounded-md border text-[11px] ${
                    leitwegTestResult.is_valid
                      ? "bg-emerald-500/10 border-emerald-500/30 text-emerald-300"
                      : "bg-rose-500/10 border-rose-500/30 text-rose-300"
                  }`}
                >
                  <span className="font-mono font-semibold">{leitwegTestResult.raw_id || "—"}</span>
                  {" · "}
                  {leitwegTestResult.is_valid
                    ? `${leitwegTestResult.bundesland_or_authority} (${leitwegTestResult.submission_portal})`
                    : leitwegTestResult.errors.join(" ")}
                </div>
              )}
            </div>
          </div>

          {/* Navigation Tabs */}
          <div className="flex flex-wrap items-center gap-1 px-6 pt-3 border-b border-slate-800 bg-slate-900/40">
            <button
              onClick={() => setActiveTab("items")}
              className={`flex items-center space-x-2 px-4 py-2 text-xs font-medium border-b-2 transition-colors ${
                activeTab === "items"
                  ? "border-emerald-400 text-emerald-400 bg-emerald-500/5"
                  : "border-transparent text-slate-400 hover:text-slate-200"
              }`}
            >
              <Layers className="w-3.5 h-3.5" />
              <span>Positionsübersicht ({data.line_items.length})</span>
            </button>

            <button
              onClick={() => setActiveTab("totals")}
              className={`flex items-center space-x-2 px-4 py-2 text-xs font-medium border-b-2 transition-colors ${
                activeTab === "totals"
                  ? "border-emerald-400 text-emerald-400 bg-emerald-500/5"
                  : "border-transparent text-slate-400 hover:text-slate-200"
              }`}
            >
              <CreditCard className="w-3.5 h-3.5" />
              <span>Steuer- &amp; Summenaufstellung</span>
            </button>

            <button
              onClick={() => setActiveTab("vat")}
              className={`flex items-center space-x-2 px-4 py-2 text-xs font-medium border-b-2 transition-colors ${
                activeTab === "vat"
                  ? "border-emerald-400 text-emerald-400 bg-emerald-500/5"
                  : "border-transparent text-slate-400 hover:text-slate-200"
              }`}
            >
              <Receipt className="w-3.5 h-3.5" />
              <span>
                UStG § 14 &amp; Reverse-Charge
                {data.vat_audit ? ` (${data.vat_audit.mandatory_fields_score_percent.toFixed(0)}%)` : ""}
              </span>
            </button>

            <button
              onClick={() => setActiveTab("validation")}
              className={`flex items-center space-x-2 px-4 py-2 text-xs font-medium border-b-2 transition-colors ${
                activeTab === "validation"
                  ? "border-emerald-400 text-emerald-400 bg-emerald-500/5"
                  : "border-transparent text-slate-400 hover:text-slate-200"
              }`}
            >
              <Scale className="w-3.5 h-3.5" />
              <span>
                EN 16931 Validierungsbericht (
                {data.validation_report.passed_rules_count}/{data.validation_report.total_rules_evaluated})
              </span>
            </button>

            <button
              onClick={() => setActiveTab("xml")}
              className={`flex items-center space-x-2 px-4 py-2 text-xs font-medium border-b-2 transition-colors ${
                activeTab === "xml"
                  ? "border-emerald-400 text-emerald-400 bg-emerald-500/5"
                  : "border-transparent text-slate-400 hover:text-slate-200"
              }`}
            >
              <Code2 className="w-3.5 h-3.5" />
              <span>Roh-XML Inspektor</span>
            </button>
          </div>

          {/* Tab Content Area */}
          <div className="flex-1 overflow-y-auto p-6 space-y-4">
            {activeTab === "items" && (
              <div className="rounded-xl border border-slate-800 bg-slate-900/60 overflow-hidden">
                <div className="overflow-x-auto">
                  <table className="w-full text-left text-xs">
                    <thead className="bg-slate-900 border-b border-slate-800 text-slate-400">
                      <tr>
                        <th className="py-3 px-4 font-medium">Pos.</th>
                        <th className="py-3 px-4 font-medium">Artikelbezeichnung / Leistungsbeschreibung</th>
                        <th className="py-3 px-4 font-medium text-right">Menge</th>
                        <th className="py-3 px-4 font-medium text-right">Einheit</th>
                        <th className="py-3 px-4 font-medium text-right">Einzelpreis Netto</th>
                        <th className="py-3 px-4 font-medium text-right">MwSt. %</th>
                        <th className="py-3 px-4 font-medium text-right">Gesamt Netto</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-800 font-mono">
                      {data.line_items.map((item, idx) => (
                        <tr key={idx} className="hover:bg-slate-800/40 transition-colors">
                          <td className="py-3 px-4 text-slate-400 font-sans">{item.line_id}</td>
                          <td className="py-3 px-4 font-sans font-medium text-white">
                            <div>{item.item_name}</div>
                            {item.item_description && (
                              <div className="text-[11px] text-slate-400 mt-0.5">{item.item_description}</div>
                            )}
                          </td>
                          <td className="py-3 px-4 text-right text-slate-200">{item.billed_quantity}</td>
                          <td className="py-3 px-4 text-right text-slate-400">{item.unit_code}</td>
                          <td className="py-3 px-4 text-right text-slate-200">
                            {item.net_price_eur.toLocaleString("de-DE", { minimumFractionDigits: 2 })} €
                          </td>
                          <td className="py-3 px-4 text-right">
                            <span className="px-1.5 py-0.5 rounded bg-slate-800 text-slate-300 text-[11px]">
                              {item.vat_rate_percent.toFixed(1)}% ({item.vat_category_code})
                            </span>
                          </td>
                          <td className="py-3 px-4 text-right font-semibold text-emerald-400">
                            {item.line_total_eur.toLocaleString("de-DE", { minimumFractionDigits: 2 })} €
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}

            {activeTab === "totals" && (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {/* Mathematical Summation Table */}
                <div className="p-5 rounded-xl bg-slate-900/60 border border-slate-800 space-y-3 font-mono text-xs">
                  <h3 className="text-sm font-semibold text-white font-sans flex items-center space-x-2">
                    <CreditCard className="w-4 h-4 text-emerald-400" />
                    <span>Monetäre Summenrechnung (BT-106 – BT-115)</span>
                  </h3>

                  <div className="flex justify-between py-1.5 border-b border-slate-800 text-slate-300">
                    <span className="text-slate-400 font-sans">Zeilensumme (BT-106):</span>
                    <span>{data.monetary_summation.line_total_amount_eur.toFixed(2)} €</span>
                  </div>
                  <div className="flex justify-between py-1.5 border-b border-slate-800 text-slate-300">
                    <span className="text-slate-400 font-sans">Zuschläge (BT-108):</span>
                    <span>{data.monetary_summation.charge_total_amount_eur.toFixed(2)} €</span>
                  </div>
                  <div className="flex justify-between py-1.5 border-b border-slate-800 text-slate-300">
                    <span className="text-slate-400 font-sans">Abschläge / Skonti (BT-107):</span>
                    <span>{data.monetary_summation.allowance_total_amount_eur.toFixed(2)} €</span>
                  </div>
                  <div className="flex justify-between py-1.5 border-b border-slate-800 font-semibold text-white">
                    <span className="text-slate-300 font-sans">Steuerbasisbetrag (Netto BT-109):</span>
                    <span>{data.monetary_summation.tax_basis_total_amount_eur.toFixed(2)} €</span>
                  </div>
                  <div className="flex justify-between py-1.5 border-b border-slate-800 font-semibold text-blue-400">
                    <span className="text-slate-300 font-sans">Gesamtbetrag Umsatzsteuer (BT-110):</span>
                    <span>{data.monetary_summation.tax_total_amount_eur.toFixed(2)} €</span>
                  </div>
                  <div className="flex justify-between py-2 border-b-2 border-emerald-500/40 text-sm font-bold text-emerald-400">
                    <span className="font-sans">Rechnungsgesamtbetrag (Brutto BT-112):</span>
                    <span>{data.monetary_summation.grand_total_amount_eur.toFixed(2)} €</span>
                  </div>
                  <div className="flex justify-between py-1.5 text-slate-300">
                    <span className="text-slate-400 font-sans">Bereits gezahlt (BT-113):</span>
                    <span>{data.monetary_summation.prepaid_amount_eur.toFixed(2)} €</span>
                  </div>
                  <div className="flex justify-between py-2 rounded-lg bg-emerald-500/10 px-3 text-sm font-bold text-emerald-300 border border-emerald-500/20">
                    <span className="font-sans">Fälliger Zahlbetrag (BT-115):</span>
                    <span>{data.monetary_summation.due_payable_amount_eur.toFixed(2)} €</span>
                  </div>
                </div>

                {/* Tax Subtotals & Payment Terms */}
                <div className="space-y-4">
                  <div className="p-5 rounded-xl bg-slate-900/60 border border-slate-800 space-y-3">
                    <h3 className="text-sm font-semibold text-white flex items-center space-x-2">
                      <Scale className="w-4 h-4 text-blue-400" />
                      <span>Umsatzsteuer-Aufschlüsselung gem. § 14 UStG</span>
                    </h3>
                    <div className="space-y-2 font-mono text-xs">
                      {data.tax_subtotals.map((tax, idx) => (
                        <div key={idx} className="p-3 rounded-lg bg-slate-950 border border-slate-800 flex justify-between items-center">
                          <div>
                            <span className="font-sans font-medium text-white">
                              Kategorie {tax.tax_category_code} ({tax.tax_rate_percent.toFixed(1)}%)
                            </span>
                            <div className="text-[11px] text-slate-400 font-sans mt-0.5">
                              Basis: {tax.taxable_amount_eur.toFixed(2)} €
                            </div>
                          </div>
                          <div className="text-right">
                            <span className="font-bold text-blue-400">
                              {tax.tax_amount_eur.toFixed(2)} €
                            </span>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>

                  <div className="p-5 rounded-xl bg-slate-900/60 border border-slate-800 space-y-2">
                    <h3 className="text-sm font-semibold text-white flex items-center space-x-2">
                      <Landmark className="w-4 h-4 text-amber-400" />
                      <span>Zahlungsmodalitäten &amp; Bankverbindung</span>
                    </h3>
                    <div className="text-xs text-slate-300 space-y-1">
                      {data.iban && (
                        <div>
                          <span className="text-slate-400">IBAN: </span>
                          <span className="font-mono text-white">{data.iban}</span>
                        </div>
                      )}
                      {data.bic && (
                        <div>
                          <span className="text-slate-400">BIC: </span>
                          <span className="font-mono text-white">{data.bic}</span>
                        </div>
                      )}
                      {data.payment_due_date && (
                        <div>
                          <span className="text-slate-400">Fälligkeitsdatum: </span>
                          <span className="font-mono text-amber-300">{data.payment_due_date}</span>
                        </div>
                      )}
                      {data.payment_terms_description && (
                        <div className="mt-2 p-2.5 rounded bg-slate-950 border border-slate-800 text-[11px] text-slate-300">
                          {data.payment_terms_description}
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              </div>
            )}

            {activeTab === "vat" && (
              <div className="space-y-4">
                {data.vat_audit ? (
                  <>
                    <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
                      <div className="p-3.5 rounded-xl border border-slate-800 bg-slate-900/60">
                        <div className="text-[11px] text-slate-400">§ 14 UStG Status</div>
                        <div
                          className={`text-sm font-bold mt-1 ${
                            data.vat_audit.is_ustg_compliant ? "text-emerald-400" : "text-rose-400"
                          }`}
                        >
                          {data.vat_audit.is_ustg_compliant ? "Konform" : "Diskrepanz erkannt"}
                        </div>
                      </div>
                      <div className="p-3.5 rounded-xl border border-slate-800 bg-slate-900/60">
                        <div className="text-[11px] text-slate-400">Pflichtangaben-Score</div>
                        <div className="text-sm font-bold font-mono text-white mt-1">
                          {data.vat_audit.mandatory_fields_score_percent.toFixed(0)}%
                        </div>
                      </div>
                      <div className="p-3.5 rounded-xl border border-slate-800 bg-slate-900/60">
                        <div className="text-[11px] text-slate-400">Nachgerechnete USt</div>
                        <div className="text-sm font-bold font-mono text-cyan-300 mt-1">
                          {data.vat_audit.recalculated_tax_total_eur.toFixed(2)} {data.currency_code}
                        </div>
                      </div>
                      <div className="p-3.5 rounded-xl border border-slate-800 bg-slate-900/60">
                        <div className="text-[11px] text-slate-400">Steuerdifferenz</div>
                        <div
                          className={`text-sm font-bold font-mono mt-1 ${
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

                    <div className="p-4 rounded-xl border border-slate-800 bg-slate-900/60 text-xs text-slate-300">
                      {data.vat_audit.audit_summary_de}
                    </div>

                    <div className="space-y-2">
                      {data.vat_audit.findings.length === 0 ? (
                        <div className="p-6 text-center rounded-xl bg-emerald-500/5 border border-emerald-500/20 text-emerald-300 text-xs">
                          Alle UStG-Pflichtangaben (§ 14 Abs. 4 UStG) sowie Steuersätze (§ 12 UStG) sind vollständig und rechnerisch einwandfrei.
                        </div>
                      ) : (
                        data.vat_audit.findings.map((finding, idx) => (
                          <div
                            key={idx}
                            className={`p-4 rounded-xl border text-xs flex items-start space-x-3 ${
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
                              {(finding.expected_value || finding.found_value) && (
                                <div className="text-[11px] font-mono text-slate-400">
                                  Erwartet: {finding.expected_value || "-"} · Gefunden: {finding.found_value || "-"}
                                </div>
                              )}
                            </div>
                          </div>
                        ))
                      )}
                    </div>
                  </>
                ) : (
                  <div className="p-6 text-center text-xs text-slate-400">
                    Keine UStG-Prüfdaten für dieses Dokument verfügbar.
                  </div>
                )}
              </div>
            )}

            {activeTab === "validation" && (
              <div className="space-y-4">
                <div className="p-5 rounded-xl bg-slate-900/60 border border-slate-800">
                  <div className="flex items-center justify-between">
                    <div>
                      <h3 className="text-sm font-semibold text-white">
                        EN 16931-1 Prüfprotokoll &amp; Konformitätsnachweis
                      </h3>
                      <p className="text-xs text-slate-400 mt-0.5">
                        {data.validation_report.validation_summary_de}
                      </p>
                    </div>
                    <div className="text-right">
                      <span className="text-lg font-bold text-emerald-400 font-mono">
                        {data.validation_report.passed_rules_count} / {data.validation_report.total_rules_evaluated}
                      </span>
                      <div className="text-[11px] text-slate-500">Regeln erfüllt</div>
                    </div>
                  </div>
                </div>

                <div className="space-y-2">
                  {data.validation_report.issues.length === 0 ? (
                    <div className="p-8 text-center rounded-xl bg-emerald-500/5 border border-emerald-500/20 text-emerald-300 space-y-2">
                      <CheckCircle2 className="w-8 h-8 mx-auto text-emerald-400" />
                      <div className="text-sm font-semibold">Keine Fehler oder Beanstandungen festgestellt</div>
                      <p className="text-xs text-slate-400">
                        Diese Rechnung erfüllt sämtliche Vorgaben der europäischen Norm EN 16931-1 sowie des § 14 UStG uneingeschränkt.
                      </p>
                    </div>
                  ) : (
                    data.validation_report.issues.map((issue, idx) => (
                      <div
                        key={idx}
                        className={`p-4 rounded-xl border flex items-start space-x-3 text-xs ${
                          issue.severity === "ERROR"
                            ? "bg-rose-500/10 border-rose-500/30 text-rose-300"
                            : "bg-amber-500/10 border-amber-500/30 text-amber-300"
                        }`}
                      >
                        {issue.severity === "ERROR" ? (
                          <XCircle className="w-4 h-4 flex-shrink-0 mt-0.5 text-rose-400" />
                        ) : (
                          <AlertCircle className="w-4 h-4 flex-shrink-0 mt-0.5 text-amber-400" />
                        )}
                        <div className="flex-1">
                          <div className="flex items-center space-x-2">
                            <span className="font-mono font-bold">{issue.code}</span>
                            <span className="text-slate-400">·</span>
                            <span className="font-mono text-[11px]">{issue.rule_id}</span>
                          </div>
                          <div className="mt-1 text-slate-200">{issue.description}</div>
                          <div className="text-[11px] text-slate-400 mt-1 font-mono">
                            Rechtsnorm: {issue.statutory_reference}
                          </div>
                        </div>
                      </div>
                    ))
                  )}
                </div>
              </div>
            )}

            {activeTab === "xml" && (
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-2 text-xs text-slate-400 font-mono">
                    <FileText className="w-4 h-4 text-emerald-400" />
                    <span>{data.xml_filename || "factur-x.xml"} ({data.validation_report.syntax_format})</span>
                  </div>
                  <button
                    onClick={handleCopyXml}
                    className="flex items-center space-x-1.5 px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-xs font-medium text-slate-200 transition-colors"
                  >
                    <Copy className="w-3.5 h-3.5" />
                    <span>{copied ? "Kopiert!" : "XML Kopieren"}</span>
                  </button>
                </div>

                <div className="p-4 rounded-xl bg-slate-950 border border-slate-800 font-mono text-[11px] text-slate-300 overflow-x-auto max-h-[500px]">
                  <pre>{data.raw_xml_content || "<!-- Kein Roh-XML verfügbar -->"}</pre>
                </div>
              </div>
            )}
          </div>
        </div>
      ) : null}
    </div>
  );
}

"use client";

import React, { useState, useEffect } from "react";
import {
  Table as TableIcon,
  FileSpreadsheet,
  Download,
  Copy,
  Check,
  ExternalLink,
  ShieldCheck,
  AlertTriangle,
  FileText,
  X,
  Layers,
  Sparkles,
  Search,
} from "lucide-react";
import { Language } from "@/lib/i18n";
import {
  TableStructure,
  TableCell,
  getDocumentTables,
  downloadTableCsv,
} from "@/lib/api";

interface TableInspectorModalProps {
  isOpen: boolean;
  onClose: () => void;
  lang: Language;
  documentId?: string | null;
  documentName?: string;
  availableDocuments?: any[];
  onSelectDocument?: (doc: any) => void;
  onJumpToCitation?: (page: number, bbox?: [number, number, number, number]) => void;
}

export function TableInspectorModal({
  isOpen,
  onClose,
  lang,
  documentId,
  documentName = "",
  availableDocuments = [],
  onSelectDocument,
  onJumpToCitation,
}: TableInspectorModalProps) {
  const isDe = lang === "DE";

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [tables, setTables] = useState<TableStructure[]>([]);
  const [selectedTableIdx, setSelectedTableIdx] = useState<number>(0);
  const [hoveredCell, setHoveredCell] = useState<TableCell | null>(null);
  const [copiedMd, setCopiedMd] = useState(false);
  const [activeTab, setActiveTab] = useState<"grid" | "raw_md" | "dora">("grid");

  // Fetch tables whenever documentId changes or modal opens
  useEffect(() => {
    if (!isOpen) return;

    if (!documentId) {
      setTables([]);
      return;
    }

    let isMounted = true;
    setLoading(true);
    setError(null);

    getDocumentTables(documentId)
      .then((res) => {
        if (!isMounted) return;
        setTables(res.tables || []);
        setSelectedTableIdx(0);
        setLoading(false);
      })
      .catch((err) => {
        if (!isMounted) return;
        setError(err.message || (isDe ? "Fehler beim Laden der Tabellen" : "Failed to load tables"));
        setLoading(false);
      });

    return () => {
      isMounted = false;
    };
  }, [isOpen, documentId, isDe]);

  if (!isOpen) return null;

  const currentTable: TableStructure | undefined = tables[selectedTableIdx];

  const handleCopyMarkdown = () => {
    if (!currentTable) return;
    navigator.clipboard.writeText(currentTable.markdown_table);
    setCopiedMd(true);
    setTimeout(() => setCopiedMd(false), 2000);
  };

  const handleDownloadCsv = () => {
    if (!currentTable || !documentId) return;
    downloadTableCsv(documentId, currentTable.table_id, currentTable.title);
  };

  const handleJumpToTable = () => {
    if (!currentTable || !onJumpToCitation) return;
    onJumpToCitation(currentTable.page_number, currentTable.bounding_box);
    onClose();
  };

  const handleJumpToCell = (cell: TableCell) => {
    if (!currentTable || !onJumpToCitation) return;
    onJumpToCitation(currentTable.page_number, cell.bounding_box);
    onClose();
  };

  return (
    <div className="fixed inset-0 z-50 bg-black/80 backdrop-blur-md flex items-center justify-center p-3 sm:p-5">
      <div className="w-full max-w-5xl bg-[var(--surface-card)] border border-[var(--surface-border)] rounded-2xl shadow-2xl overflow-hidden flex flex-col max-h-[90vh] animate-in zoom-in-95 duration-200">
        
        {/* Modal Top Header */}
        <div className="p-4 border-b border-[var(--surface-border)] bg-[var(--surface-dark)] flex items-center justify-between shrink-0">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-[var(--accent-tangerine)]/15 border border-[var(--accent-tangerine)]/40 flex items-center justify-center shadow-inner">
              <TableIcon className="w-5 h-5 text-[var(--accent-tangerine)]" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h2 className="text-sm sm:text-base font-bold text-[var(--foreground)] tracking-tight">
                  {isDe ? "SLA-Tabellen & Pönalen-Inspektor" : "SLA Table & Penalty Matrix Inspector"}
                </h2>
                <span className="text-[10px] font-mono px-2 py-0.5 rounded-full bg-[var(--accent-tangerine)]/15 text-[var(--accent-tangerine)] border border-[var(--accent-tangerine)]/30 font-bold uppercase tracking-wider">
                  DORA Art. 30
                </span>
              </div>
              <p className="text-xs text-[var(--foreground)] opacity-60">
                {isDe
                  ? "Strukturierte Tabellenerkennung mit Bounding-Box-Koordinaten & SLA-Prüfung"
                  : "Structured table extraction with bounding box coordinates & SLA compliance audit"}
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2">
            {/* Document Selector */}
            {availableDocuments.length > 1 && onSelectDocument && (
              <div className="relative">
                <select
                  value={documentId || ""}
                  onChange={(e) => {
                    const sel = availableDocuments.find((d) => d.id === e.target.value);
                    if (sel) onSelectDocument(sel);
                  }}
                  className="bg-[var(--surface-card)] border border-[var(--surface-border)] text-xs text-[var(--foreground)] rounded-lg px-2.5 py-1.5 font-mono max-w-[180px] sm:max-w-[220px] truncate focus:outline-none focus:border-[var(--accent-tangerine)]"
                >
                  {availableDocuments.map((doc) => (
                    <option key={doc.id} value={doc.id}>
                      {doc.filename}
                    </option>
                  ))}
                </select>
              </div>
            )}

            <button
              onClick={onClose}
              className="p-1.5 rounded-lg hover:bg-[var(--surface-border)] text-[var(--foreground)] opacity-60 hover:opacity-100 transition-colors cursor-pointer"
              title={isDe ? "Schließen" : "Close"}
            >
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* Multi-Table Tabs Header */}
        {tables.length > 0 && (
          <div className="bg-[var(--surface-dark)]/60 px-4 pt-2 border-b border-[var(--surface-border)] flex items-center justify-between gap-2 overflow-x-auto shrink-0">
            <div className="flex items-center gap-1.5">
              {tables.map((t, idx) => {
                const isSelected = idx === selectedTableIdx;
                return (
                  <button
                    key={t.table_id}
                    onClick={() => {
                      setSelectedTableIdx(idx);
                      setHoveredCell(null);
                    }}
                    className={`px-3 py-1.5 text-xs font-mono rounded-t-lg transition-all flex items-center gap-2 cursor-pointer border-t border-x ${
                      isSelected
                        ? "bg-[var(--surface-card)] border-[var(--surface-border)] text-[var(--accent-tangerine)] font-bold shadow-sm"
                        : "border-transparent text-[var(--foreground)] opacity-60 hover:opacity-100 hover:bg-[var(--surface-card)]/50"
                    }`}
                  >
                    <Layers className="w-3.5 h-3.5" />
                    <span className="truncate max-w-[150px] sm:max-w-[200px]">{t.title}</span>
                    <span className="text-[10px] px-1.5 py-0.2 rounded bg-black/30 font-normal">
                      {isDe ? `S. ${t.page_number}` : `P. ${t.page_number}`}
                    </span>
                  </button>
                );
              })}
            </div>

            {/* View Mode Tabs */}
            <div className="flex items-center gap-1 pb-1 shrink-0">
              <button
                onClick={() => setActiveTab("grid")}
                className={`px-2 py-1 text-xs rounded font-medium transition-colors ${
                  activeTab === "grid"
                    ? "bg-[var(--surface-border)] text-[var(--foreground)]"
                    : "text-[var(--foreground)] opacity-60 hover:opacity-100"
                }`}
              >
                {isDe ? "Rasteransicht" : "Grid View"}
              </button>
              <button
                onClick={() => setActiveTab("dora")}
                className={`px-2 py-1 text-xs rounded font-medium transition-colors ${
                  activeTab === "dora"
                    ? "bg-[var(--surface-border)] text-[var(--foreground)]"
                    : "text-[var(--foreground)] opacity-60 hover:opacity-100"
                }`}
              >
                {isDe ? "SLA-Prüfung" : "SLA Audit"}
              </button>
              <button
                onClick={() => setActiveTab("raw_md")}
                className={`px-2 py-1 text-xs rounded font-medium transition-colors ${
                  activeTab === "raw_md"
                    ? "bg-[var(--surface-border)] text-[var(--foreground)]"
                    : "text-[var(--foreground)] opacity-60 hover:opacity-100"
                }`}
              >
                Markdown
              </button>
            </div>
          </div>
        )}

        {/* Content Body */}
        <div className="flex-1 overflow-y-auto p-4 sm:p-5 space-y-4">
          {loading && (
            <div className="flex flex-col items-center justify-center py-20 text-[var(--foreground)] opacity-60 space-y-3">
              <div className="w-8 h-8 border-2 border-[var(--accent-tangerine)] border-t-transparent rounded-full animate-spin" />
              <p className="text-sm font-mono">
                {isDe
                  ? "Analysiere PDF-Vektorpfade & SLA-Tabellen..."
                  : "Analyzing PDF vector paths & SLA tables..."}
              </p>
            </div>
          )}

          {!loading && error && (
            <div className="p-4 rounded-xl bg-rose-950/40 border border-rose-500/40 text-rose-300 text-sm flex items-center gap-3">
              <AlertTriangle className="w-5 h-5 shrink-0" />
              <span>{error}</span>
            </div>
          )}

          {!loading && !error && tables.length === 0 && (
            <div className="text-center py-16 space-y-3">
              <FileSpreadsheet className="w-12 h-12 text-[var(--foreground)] opacity-30 mx-auto" />
              <h3 className="text-base font-bold text-[var(--foreground)]">
                {isDe ? "Keine Tabellenstrukturen im aktuellen Dokument identifiziert" : "No structured tables found in this document"}
              </h3>
              <p className="text-xs text-[var(--foreground)] opacity-60 max-w-md mx-auto">
                {isDe
                  ? "Laden Sie den Siemens Master-IKT-Vertrag 2026 oder ein offizielles IELTS-Zertifikat hoch, um automatisierte SLA-Pönalenmatrizen zu extrahieren."
                  : "Upload the Siemens Master ICT Contract 2026 or an official IELTS certificate to extract automated SLA penalty matrices."}
              </p>
            </div>
          )}

          {!loading && currentTable && (
            <>
              {/* Table Metadata Banner */}
              <div className="bg-[var(--surface-dark)]/80 border border-[var(--surface-border)] rounded-xl p-3 flex flex-wrap items-center justify-between gap-3 text-xs">
                <div className="flex items-center gap-3">
                  <div className="font-mono">
                    <span className="opacity-60">{isDe ? "Dimension:" : "Dimensions:"}</span>{" "}
                    <span className="font-bold text-[var(--foreground)]">
                      {currentTable.row_count} {isDe ? "Zeilen" : "Rows"} × {currentTable.col_count} {isDe ? "Spalten" : "Cols"}
                    </span>
                  </div>
                  <div className="font-mono">
                    <span className="opacity-60">{isDe ? "Seite:" : "Page:"}</span>{" "}
                    <span className="font-bold text-[var(--accent-tangerine)]">{currentTable.page_number}</span>
                  </div>
                  <div className="font-mono hidden sm:block">
                    <span className="opacity-60">BBox:</span>{" "}
                    <span className="text-[10px] text-[var(--foreground)] opacity-80">
                      [{currentTable.bounding_box.map((v) => Math.round(v)).join(", ")}]
                    </span>
                  </div>
                </div>

                {/* Jump to Table on Page */}
                {onJumpToCitation && (
                  <button
                    onClick={handleJumpToTable}
                    className="flex items-center gap-1.5 px-2.5 py-1 rounded-md bg-[var(--surface-card)] hover:bg-[var(--surface-border)] border border-[var(--surface-border)] font-mono text-[11px] text-[var(--accent-cyan)] transition-colors cursor-pointer"
                  >
                    <ExternalLink className="w-3 h-3" />
                    <span>{isDe ? "Im PDF visualisieren" : "Visualize on PDF"}</span>
                  </button>
                )}
              </div>

              {/* Regulatory Analysis Banner (SLA & DORA compliance) */}
              {currentTable.regulatory_analysis && (
                <div className="bg-gradient-to-r from-emerald-950/30 to-blue-950/20 border border-emerald-500/30 rounded-xl p-3.5 space-y-2">
                  <div className="flex flex-wrap items-center justify-between gap-2">
                    <div className="flex items-center gap-2">
                      <ShieldCheck className="w-4 h-4 text-emerald-400 shrink-0" />
                      <span className="font-bold text-xs text-emerald-200">
                        {currentTable.regulatory_analysis.sla_classification}
                      </span>
                    </div>
                    <span className="px-2 py-0.5 rounded-full text-[10px] font-mono font-bold uppercase tracking-wider bg-emerald-500/20 text-emerald-300 border border-emerald-500/40">
                      {currentTable.regulatory_analysis.compliance_status}
                    </span>
                  </div>

                  {currentTable.regulatory_analysis.availability_target && (
                    <div className="text-xs text-[var(--foreground)] opacity-90 flex items-center gap-2">
                      <span className="font-mono opacity-60">{isDe ? "Soll-Ziel:" : "Target:"}</span>
                      <span className="font-semibold text-emerald-300">
                        {currentTable.regulatory_analysis.availability_target}
                      </span>
                    </div>
                  )}

                  {/* Assessed Penalty Scales */}
                  {currentTable.regulatory_analysis.penalty_scale_assessed.length > 0 && (
                    <div className="pt-1">
                      <div className="text-[10px] font-mono opacity-60 uppercase tracking-wider mb-1">
                        {isDe ? "Aufsichtsrechtliche Einstufung & Pönalstaffel:" : "Regulatory Assessment & Penalty Tiers:"}
                      </div>
                      <div className="flex flex-wrap gap-1.5">
                        {currentTable.regulatory_analysis.penalty_scale_assessed.map((p, pIdx) => (
                          <span
                            key={pIdx}
                            className="text-[11px] font-mono px-2 py-0.5 rounded bg-[var(--surface-dark)] border border-[var(--surface-border)] text-[var(--foreground)]"
                          >
                            {p}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              )}

              {/* Main Tab: Grid View */}
              {activeTab === "grid" && (
                <div className="space-y-2">
                  <div className="border border-[var(--surface-border)] rounded-xl overflow-hidden overflow-x-auto bg-[var(--surface-dark)]/40 shadow-inner">
                    <table className="w-full text-left border-collapse text-xs">
                      <thead>
                        <tr className="bg-[var(--surface-dark)] border-b border-[var(--surface-border)]">
                          {currentTable.headers.map((h, colIdx) => (
                            <th
                              key={colIdx}
                              className="p-3 font-mono font-bold text-[var(--foreground)] opacity-90 tracking-wide border-r border-[var(--surface-border)] last:border-r-0 whitespace-nowrap"
                            >
                              {h || `Spalte ${colIdx + 1}`}
                            </th>
                          ))}
                        </tr>
                      </thead>
                      <tbody>
                        {currentTable.rows.map((row, rIdx) => (
                          <tr
                            key={rIdx}
                            className="border-b border-[var(--surface-border)]/60 hover:bg-[var(--accent-tangerine)]/5 transition-colors last:border-b-0"
                          >
                            {row.map((val, cIdx) => {
                              const matchingCell = currentTable.cells.find(
                                (c) => c.row_idx === rIdx + 1 && c.col_idx === cIdx
                              );
                              const isHovered =
                                hoveredCell &&
                                hoveredCell.row_idx === rIdx + 1 &&
                                hoveredCell.col_idx === cIdx;

                              return (
                                <td
                                  key={cIdx}
                                  onMouseEnter={() => matchingCell && setHoveredCell(matchingCell)}
                                  onClick={() => matchingCell && handleJumpToCell(matchingCell)}
                                  className={`p-3 border-r border-[var(--surface-border)]/60 last:border-r-0 font-mono text-[11px] sm:text-xs transition-colors cursor-pointer ${
                                    isHovered
                                      ? "bg-[var(--accent-tangerine)]/20 text-[var(--accent-tangerine)] font-bold"
                                      : "text-[var(--foreground)] opacity-90"
                                  }`}
                                  title={
                                    matchingCell
                                      ? `[x0: ${matchingCell.bounding_box[0]}, y0: ${matchingCell.bounding_box[1]}, x1: ${matchingCell.bounding_box[2]}, y1: ${matchingCell.bounding_box[3]}] - ${isDe ? "Klicken zum Hervorheben" : "Click to jump"}`
                                      : undefined
                                  }
                                >
                                  {val}
                                </td>
                              );
                            })}
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>

                  {/* Cell Coordinate HUD indicator */}
                  <div className="min-h-[26px] flex items-center justify-between text-[11px] font-mono text-[var(--foreground)] opacity-70 px-1">
                    {hoveredCell ? (
                      <div className="flex items-center gap-2">
                        <span className="text-[var(--accent-tangerine)] font-bold">
                          Zelle [Z:{hoveredCell.row_idx}, S:{hoveredCell.col_idx}]:
                        </span>
                        <span>
                          BBox: [{hoveredCell.bounding_box.map((v) => Math.round(v)).join(", ")}]
                        </span>
                        <span className="opacity-50">
                          ({isDe ? "Klick = PDF-Sprung" : "Click = Jump to PDF"})
                        </span>
                      </div>
                    ) : (
                      <span className="opacity-50">
                        {isDe
                          ? "Fahren Sie über eine Zelle, um visuelle Koordinaten einzusehen."
                          : "Hover over any cell to inspect visual coordinates."}
                      </span>
                    )}
                  </div>
                </div>
              )}

              {/* Main Tab: SLA Audit Deep-Dive */}
              {activeTab === "dora" && currentTable.regulatory_analysis && (
                <div className="space-y-4">
                  <div className="bg-[var(--surface-dark)] border border-[var(--surface-border)] rounded-xl p-4 space-y-3">
                    <h4 className="font-bold text-sm text-[var(--foreground)] flex items-center gap-2">
                      <Sparkles className="w-4 h-4 text-[var(--accent-tangerine)]" />
                      {isDe ? "Aufsichtsrechtliche Rechtsgrundlage & Empfehlungen" : "Regulatory Basis & Recommendations"}
                    </h4>
                    
                    <div className="text-xs space-y-2">
                      <div>
                        <span className="font-mono opacity-60">{isDe ? "Gesetzliche Norm:" : "Statutory Basis:"}</span>{" "}
                        <span className="font-semibold text-[var(--foreground)]">
                          {currentTable.regulatory_analysis.dora_statutory_basis}
                        </span>
                      </div>

                      {currentTable.regulatory_analysis.recommendations.length > 0 && (
                        <div className="pt-2 space-y-1.5">
                          <span className="font-mono text-[10px] opacity-60 uppercase tracking-wider block">
                            {isDe ? "Audit-Empfehlungen zur Revisionssicherheit:" : "Audit Recommendations:"}
                          </span>
                          <ul className="space-y-1 list-disc list-inside text-xs opacity-90 text-[var(--foreground)]">
                            {currentTable.regulatory_analysis.recommendations.map((rec, rIdx) => (
                              <li key={rIdx}>{rec}</li>
                            ))}
                          </ul>
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              )}

              {/* Main Tab: Raw Markdown Representation */}
              {activeTab === "raw_md" && (
                <div className="relative">
                  <pre className="p-4 rounded-xl bg-black/60 border border-[var(--surface-border)] font-mono text-xs text-emerald-400 overflow-x-auto whitespace-pre">
                    {currentTable.markdown_table}
                  </pre>
                </div>
              )}
            </>
          )}
        </div>

        {/* Modal Action Footer */}
        {currentTable && (
          <div className="p-3.5 border-t border-[var(--surface-border)] bg-[var(--surface-dark)] flex flex-wrap items-center justify-between gap-3 shrink-0">
            <div className="flex items-center gap-2 text-xs font-mono opacity-60">
              <TableIcon className="w-4 h-4 text-[var(--accent-tangerine)]" />
              <span>Table ID: {currentTable.table_id}</span>
            </div>

            <div className="flex items-center gap-2">
              <button
                onClick={handleCopyMarkdown}
                className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-[var(--surface-card)] hover:bg-[var(--surface-border)] border border-[var(--surface-border)] text-xs font-mono font-medium text-[var(--foreground)] transition-colors cursor-pointer"
              >
                {copiedMd ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
                <span>{copiedMd ? (isDe ? "Kopiert!" : "Copied!") : (isDe ? "Markdown kopieren" : "Copy Markdown")}</span>
              </button>

              <button
                onClick={handleDownloadCsv}
                className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-[var(--accent-tangerine)] hover:opacity-90 text-[var(--accent-contrast)] text-xs font-mono font-bold transition-all shadow-sm cursor-pointer"
              >
                <Download className="w-3.5 h-3.5" />
                <span>{isDe ? "CSV exportieren" : "Export CSV"}</span>
              </button>
            </div>
          </div>
        )}

      </div>
    </div>
  );
}

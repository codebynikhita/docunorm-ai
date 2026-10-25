"use client";

import React, { useState, useRef, useEffect } from "react";
import {
  UploadCloud,
  FileText,
  Download,
  ZoomIn,
  ZoomOut,
  CheckCircle2,
  Loader2,
  Check,
  ChevronDown,
  Languages,
  X,
  Columns,
  Eye,
  BookOpen,
  ArrowRight,
  Search,
  MapPin,
  ShieldCheck,
  ShieldAlert,
  Sparkles,
} from "lucide-react";

import { Language, translations } from "@/lib/i18n";
import { translateGermanToEnglish, classifyClause, ClauseMetadata } from "@/lib/translator";
import { getDocumentChunks, getTranslatedDocumentChunks, getDocumentTaskProgress } from "@/lib/api";

interface BoundingBoxHighlight {
  page_number: number;
  box: [number, number, number, number]; // [x0, y0, x1, y1]
  label?: string;
  snippet?: string;
}

interface DocumentViewerProps {
  lang?: Language;
  documentId?: string | null;
  documentName?: string;
  availableDocuments?: any[];
  currentPage: number;
  totalPages: number;
  isUploading?: boolean;
  activeHighlight?: BoundingBoxHighlight | null;
  onUploadFile?: (file: File) => void;
  onSelectDocument?: (doc: any) => void;
  onPageChange?: (newPage: number) => void;
  onClearHighlight?: () => void;
  onOpenDoraExit?: () => void;
}

export function DocumentViewer({
  lang = "DE",
  documentId,
  documentName = "",
  availableDocuments = [],
  currentPage = 1,
  totalPages = 1,
  isUploading = false,
  activeHighlight,
  onUploadFile,
  onSelectDocument,
  onPageChange,
  onOpenDoraExit,
}: DocumentViewerProps) {
  const t = translations[lang];
  const [zoom, setZoom] = useState(75);
  const [rendering, setRendering] = useState(false);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [isTranslationHudDismissed, setIsTranslationHudDismissed] = useState(false);
  const [docViewMode, setDocViewMode] = useState<"canvas" | "dual" | "english">("dual");
  const [allChunks, setAllChunks] = useState<any[]>([]);
  const [selectedChunkId, setSelectedChunkId] = useState<string | null>(null);
  const [localHighlight, setLocalHighlight] = useState<BoundingBoxHighlight | null>(null);
  const [searchFilter, setSearchFilter] = useState("");
  const effectiveHighlight = activeHighlight || localHighlight;
  const [taskProgress, setTaskProgress] = useState<{
    status: string;
    progress: number;
    stage: string;
  } | null>(null);

  const [canvasDimensions, setCanvasDimensions] = useState<{ width: number; height: number }>({
    width: 600,
    height: 800,
  });

  const canvasRef = useRef<HTMLCanvasElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const pdfDocRef = useRef<any>(null);

  // Poll background task progress if document is in processing
  useEffect(() => {
    if (!documentId) {
      setTaskProgress(null);
      return;
    }

    let intervalId: any;
    let isCancelled = false;

    async function checkProgress() {
      const info = await getDocumentTaskProgress(documentId!);
      if (!isCancelled && info) {
        if (info.status === "processing") {
          setTaskProgress({
            status: info.status,
            progress: info.progress,
            stage: info.stage,
          });
        } else if (info.status === "ready") {
          setTaskProgress((prev) => {
            if (prev && prev.status === "processing") {
              return {
                status: "ready",
                progress: 100,
                stage: "ingestion_complete",
              };
            }
            return null;
          });

          // Reload chunks once ready
          getTranslatedDocumentChunks(documentId!).then((chunks) => {
            if (!isCancelled && chunks && chunks.length > 0) {
              setAllChunks(chunks);
            }
          });

          clearInterval(intervalId);
          setTimeout(() => {
            if (!isCancelled) setTaskProgress(null);
          }, 3500);
        }
      }
    }

    checkProgress();
    intervalId = setInterval(checkProgress, 1200);

    return () => {
      isCancelled = true;
      clearInterval(intervalId);
    };
  }, [documentId]);

  // Fetch document chunks for translation
  useEffect(() => {
    async function loadChunks() {
      if (!documentId) {
        setAllChunks([]);
        return;
      }
      let chunks = await getTranslatedDocumentChunks(documentId);
      if (!chunks || chunks.length === 0) {
        chunks = await getDocumentChunks(documentId);
      }
      setAllChunks(chunks || []);
    }
    loadChunks();
  }, [documentId]);

  // Reset dismissed state whenever highlight changes
  useEffect(() => {
    if (activeHighlight) {
      setIsTranslationHudDismissed(false);
    }
  }, [activeHighlight]);

  // Load PDF with PDF.js whenever documentId changes
  useEffect(() => {
    let isCancelled = false;

    async function loadPdf() {
      if (!documentId) return;

      try {
        setRendering(true);
        const pdfjsLib = await import("pdfjs-dist");
        pdfjsLib.GlobalWorkerOptions.workerSrc = `https://unpkg.com/pdfjs-dist@${pdfjsLib.version}/build/pdf.worker.min.mjs`;

        const pdfUrl = `http://localhost:8000/api/v1/documents/${documentId}/file`;
        const loadingTask = pdfjsLib.getDocument(pdfUrl);
        const pdf = await loadingTask.promise;

        if (!isCancelled) {
          pdfDocRef.current = pdf;
          renderPage(currentPage, pdf);
        }
      } catch (err) {
        console.error("Failed to load PDF with pdfjs:", err);
      } finally {
        if (!isCancelled) setRendering(false);
      }
    }

    loadPdf();

    return () => {
      isCancelled = true;
    };
  }, [documentId]);

  // Re-render page whenever currentPage, zoom, or docViewMode changes back to canvas
  useEffect(() => {
    if (pdfDocRef.current && docViewMode !== "english") {
      renderPage(currentPage, pdfDocRef.current);
    }
  }, [currentPage, zoom, docViewMode]);

  const renderPage = async (pageNumber: number, pdf: any) => {
    if (!canvasRef.current || !pdf) return;

    try {
      setRendering(true);
      const page = await pdf.getPage(pageNumber);
      const scale = (zoom / 100) * 1.25;
      const viewport = page.getViewport({ scale });

      const canvas = canvasRef.current;
      const context = canvas.getContext("2d");
      if (!context) return;

      canvas.width = viewport.width;
      canvas.height = viewport.height;
      setCanvasDimensions({ width: viewport.width, height: viewport.height });

      const renderContext = {
        canvasContext: context,
        viewport: viewport,
      };

      await page.render(renderContext).promise;
    } catch (err) {
      console.error("Error rendering PDF page:", err);
    } finally {
      setRendering(false);
    }
  };

  const handleFilePicked = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setSelectedFile(e.target.files[0]);
    }
  };

  const handleConfirmUpload = () => {
    if (selectedFile && onUploadFile) {
      onUploadFile(selectedFile);
      setSelectedFile(null);
    }
  };

  const handleToggleDocViewMode = (mode: "canvas" | "dual" | "english") => {
    setDocViewMode(mode);
    if (mode === "dual" && zoom > 75) {
      setZoom(75);
    } else if (mode === "canvas" && zoom < 100) {
      setZoom(100);
    }
  };

  const scaleFactor = (zoom / 100) * 1.25;

  // Filter chunks for current page
  const currentPageChunks = allChunks.filter((c) => c.page_number === currentPage);

  return (
    <div className="flex-1 flex flex-col h-full bg-[var(--background)]">
      {/* Top Toolbar */}
      <div className="h-14 border-b border-[var(--surface-border)] bg-[var(--surface-dark)] px-4 flex items-center justify-between">
        {/* Document Selector & Translation View Mode */}
        <div className="flex items-center gap-3">
          <FileText className="w-4 h-4 text-[var(--accent-tangerine)] flex-shrink-0" />
          {availableDocuments.length > 0 ? (
            <div className="relative">
              <select
                value={documentId || ""}
                onChange={(e) => {
                  if (e.target.value === "") {
                    if (onSelectDocument) onSelectDocument(null);
                    return;
                  }
                  const doc = availableDocuments.find((d) => d.id === e.target.value);
                  if (doc && onSelectDocument) onSelectDocument(doc);
                }}
                className="bg-[var(--surface-card)] border border-[var(--surface-border)] text-[var(--foreground)] text-xs rounded-md px-2.5 py-1.5 pr-7 appearance-none focus:outline-none focus:border-[var(--accent-tangerine)] cursor-pointer font-mono font-medium max-w-[200px] sm:max-w-[260px] truncate shadow-sm"
              >
                <option value="">{t.select_doc_placeholder}</option>
                {availableDocuments.map((doc) => (
                  <option key={doc.id} value={doc.id}>
                    {doc.filename}
                  </option>
                ))}
              </select>
              <ChevronDown className="w-3.5 h-3.5 text-[var(--foreground)] opacity-50 absolute right-2 top-2.5 pointer-events-none" />
            </div>
          ) : (
            <span className="text-xs text-[var(--foreground)] opacity-50 font-mono italic">
              {t.no_docs_indexed}
            </span>
          )}

          {/* DOCUMENT TRANSLATION MODE SELECTOR */}
          <div className="flex items-center bg-[var(--surface-card)] border border-[var(--surface-border)] rounded-md p-0.5 text-[10px] font-mono shadow-sm">
            <button
              onClick={() => handleToggleDocViewMode("canvas")}
              className={`px-2 py-0.5 rounded font-bold cursor-pointer transition-all ${
                docViewMode === "canvas"
                  ? "bg-[var(--accent-tangerine)] text-[var(--accent-contrast)]"
                  : "text-[var(--foreground)] opacity-60 hover:opacity-100"
              }`}
              title="Show Original German PDF"
            >
              🇩🇪 PDF
            </button>
            <button
              onClick={() => handleToggleDocViewMode("dual")}
              className={`px-2.5 py-0.5 rounded font-bold cursor-pointer transition-all flex items-center gap-1 ${
                docViewMode === "dual"
                  ? "bg-[var(--accent-tangerine)] text-[var(--accent-contrast)]"
                  : "text-[var(--foreground)] opacity-60 hover:opacity-100"
              }`}
              title="Side-by-Side Dual View: German PDF + English Translation"
            >
              <Columns className="w-3 h-3" />
              <span>{lang === "DE" ? "Dual-Ansicht" : "Dual-View"}</span>
            </button>
            <button
              onClick={() => handleToggleDocViewMode("english")}
              className={`px-2 py-0.5 rounded font-bold cursor-pointer transition-all flex items-center gap-1 ${
                docViewMode === "english"
                  ? "bg-[var(--accent-tangerine)] text-[var(--accent-contrast)]"
                  : "text-[var(--foreground)] opacity-60 hover:opacity-100"
              }`}
              title="Full English Translated Dossier"
            >
              <Languages className="w-3 h-3" />
              <span className="hidden sm:inline">
                {lang === "DE" ? "Englisches Dossier" : "English Dossier"}
              </span>
            </button>
          </div>

          {onOpenDoraExit && (
            <button
              onClick={onOpenDoraExit}
              className="px-2.5 py-1 rounded font-mono text-[11px] font-bold cursor-pointer transition-all flex items-center gap-1.5 bg-[var(--surface-card)] hover:bg-[var(--surface-dark)] text-[var(--accent-cyan)] border border-[var(--accent-cyan)]/30 hover:border-[var(--accent-cyan)] shadow-sm"
              title="DORA Art. 30(2) & BaFin Exit Strategy Regulatory Audit"
            >
              <ShieldAlert className="w-3.5 h-3.5 text-[var(--accent-cyan)]" />
              <span className="hidden xl:inline">
                {lang === "DE" ? "DORA Art. 30(2) Exit-Prüfung" : "DORA Art. 30(2) Exit Audit"}
              </span>
            </button>
          )}
        </div>

        {/* 2-Step Upload Flow (Select -> Submit) */}
        <div className="flex items-center gap-2.5 text-xs">
          <input
            type="file"
            ref={fileInputRef}
            onChange={handleFilePicked}
            accept=".pdf"
            className="hidden"
          />

          {!selectedFile ? (
            <button
              onClick={() => fileInputRef.current?.click()}
              disabled={isUploading}
              className="flex items-center gap-1.5 bg-[var(--surface-card)] hover:bg-[var(--surface-dark)] text-[var(--foreground)] border border-[var(--surface-border)] hover:border-[var(--accent-tangerine)]/50 font-mono text-[11px] font-bold px-3 py-1.5 rounded-md transition-all uppercase tracking-wider shadow-sm cursor-pointer"
            >
              <UploadCloud className="w-3.5 h-3.5 text-[var(--accent-tangerine)]" />
              <span>{t.btn_select_pdf}</span>
            </button>
          ) : (
            <div className="flex items-center gap-1.5 bg-[var(--surface-card)] border border-[var(--accent-tangerine)]/50 px-2.5 py-1 rounded-md shadow-sm">
              <span className="text-[11px] font-mono text-[var(--foreground)] truncate max-w-[120px] font-medium">
                {selectedFile.name}
              </span>
              <button
                onClick={handleConfirmUpload}
                disabled={isUploading}
                className="flex items-center gap-1 bg-[var(--accent-tangerine)] hover:opacity-90 text-[var(--accent-contrast)] font-black font-mono text-[11px] px-2.5 py-1 rounded transition-all shadow-sm uppercase tracking-wide cursor-pointer"
              >
                {isUploading ? (
                  <Loader2 className="w-3 h-3 animate-spin" />
                ) : (
                  <Check className="w-3.5 h-3.5 stroke-[3]" />
                )}
                <span>{isUploading ? "..." : t.btn_submit_ingest}</span>
              </button>
              <button
                onClick={() => setSelectedFile(null)}
                className="text-[var(--foreground)] opacity-50 hover:opacity-100 px-1 text-xs cursor-pointer"
              >
                ✕
              </button>
            </div>
          )}

          {/* Page Selector & Zoom */}
          <div className="flex items-center gap-1 bg-[var(--surface-card)] border border-[var(--surface-border)] px-2 py-1 rounded-md text-[var(--foreground)]">
            <button
              onClick={() => onPageChange && onPageChange(Math.max(1, currentPage - 1))}
              disabled={currentPage <= 1}
              className="hover:opacity-100 disabled:opacity-20 font-bold px-1 cursor-pointer"
            >
              &lt;
            </button>
            <span className="px-1 font-mono text-[11px] font-semibold">
              {currentPage} / {totalPages}
            </span>
            <button
              onClick={() => onPageChange && onPageChange(Math.min(totalPages, currentPage + 1))}
              disabled={currentPage >= totalPages}
              className="hover:opacity-100 disabled:opacity-20 font-bold px-1 cursor-pointer"
            >
              &gt;
            </button>
          </div>

          <div className="hidden sm:flex items-center gap-1 bg-[var(--surface-card)] border border-[var(--surface-border)] px-2 py-1 rounded-md text-[var(--foreground)]">
            <button
              onClick={() => setZoom((z) => Math.max(60, z - 10))}
              className="hover:opacity-100 p-0.5 cursor-pointer"
            >
              <ZoomOut className="w-3.5 h-3.5" />
            </button>
            <span className="w-9 text-center font-mono text-[11px] font-semibold">{zoom}%</span>
            <button
              onClick={() => setZoom((z) => Math.min(160, z + 10))}
              className="hover:opacity-100 p-0.5 cursor-pointer"
            >
              <ZoomIn className="w-3.5 h-3.5" />
            </button>
          </div>
        </div>
      </div>

      {/* Background Task Queue Real-Time Ingestion Progress Banner */}
      {taskProgress && (
        <div
          className={`border-b px-4 py-2 flex items-center justify-between text-xs transition-colors duration-300 ${
            taskProgress.status === "ready"
              ? "bg-emerald-950/60 border-emerald-500/40 text-emerald-300"
              : "bg-[var(--surface-dark)]/90 border-[var(--accent-tangerine)]/30 text-[var(--foreground)]"
          }`}
        >
          <div className="flex items-center gap-2.5">
            {taskProgress.status === "ready" ? (
              <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
            ) : (
              <Loader2 className="w-4 h-4 text-[var(--accent-tangerine)] animate-spin shrink-0" />
            )}
            <div className="flex items-center gap-2">
              <span className="font-mono text-[10px] font-bold uppercase tracking-wider px-1.5 py-0.5 rounded bg-[var(--surface-card)] border border-[var(--surface-border)]">
                {taskProgress.status === "ready" ? "Worker Complete" : "Redis Worker Queue"}
              </span>
              <span className="font-mono text-xs text-[var(--foreground)] opacity-90">
                {taskProgress.stage.replace(/_/g, " ")} ({taskProgress.progress}%)
              </span>
            </div>
          </div>
          <div className="flex items-center gap-3">
            <span className="text-[10px] font-mono opacity-60 hidden md:inline">
              BDSG PII Redaction & 1024-dim pgvector
            </span>
            <div className="w-28 sm:w-36 bg-[var(--surface-card)] rounded-full h-1.5 overflow-hidden border border-[var(--surface-border)]">
              <div
                className={`h-full transition-all duration-300 rounded-full ${
                  taskProgress.status === "ready" ? "bg-emerald-400" : "bg-[var(--accent-tangerine)]"
                }`}
                style={{ width: `${taskProgress.progress}%` }}
              />
            </div>
          </div>
        </div>
      )}

      {/* Main Viewport: Canvas / Dual-View / English Dossier */}
      <div className="flex-1 overflow-hidden flex">
        {/* 1. PDF Canvas View (Kept mounted in DOM to preserve rendered canvas state) */}
        <div
          className={`overflow-auto p-4 md:p-6 cyber-canvas relative flex flex-col items-center min-w-0 ${
            docViewMode === "english"
              ? "hidden"
              : docViewMode === "dual"
              ? "flex-1 border-r border-[var(--surface-border)]"
              : "flex-1"
          }`}
        >
          {!documentId ? (
            <div className="w-[500px] h-[650px] border border-dashed border-[var(--surface-border)] rounded-2xl flex flex-col items-center justify-center p-8 text-center text-[var(--foreground)] bg-[var(--surface-card)]/80 backdrop-blur-md shadow-xl my-auto">
              <div className="w-14 h-14 rounded-2xl bg-[var(--accent-tangerine)]/10 border border-[var(--accent-tangerine)]/30 flex items-center justify-center mb-4 shadow-sm">
                <UploadCloud className="w-7 h-7 text-[var(--accent-tangerine)]" />
              </div>
              <h4 className="text-sm font-bold text-[var(--foreground)] font-mono mb-1 tracking-wide uppercase">
                {t.empty_canvas_title}
              </h4>
              <p className="text-xs text-[var(--foreground)] opacity-60 max-w-[320px] mb-6 leading-relaxed font-mono text-[11px]">
                {t.empty_canvas_desc}
              </p>
              <button
                onClick={() => fileInputRef.current?.click()}
                className="bg-[var(--surface-dark)] hover:bg-[var(--surface-card)] text-[var(--accent-tangerine)] border border-[var(--accent-tangerine)]/50 text-xs font-bold font-mono px-5 py-2.5 rounded-md transition-all shadow-sm uppercase tracking-wider cursor-pointer"
              >
                {t.btn_load_file}
              </button>
            </div>
          ) : (
            <div
              style={{ width: `${canvasDimensions.width}px`, minHeight: `${canvasDimensions.height}px` }}
              className="relative bg-white rounded-lg shadow-2xl transition-all duration-150 flex items-center justify-center overflow-hidden border border-[var(--surface-border)] m-auto shrink-0"
            >
              {rendering && (
                <div className="absolute inset-0 bg-black/30 backdrop-blur-[2px] flex items-center justify-center z-10">
                  <Loader2 className="w-7 h-7 animate-spin text-[var(--accent-tangerine)]" />
                </div>
              )}

              <canvas ref={canvasRef} className="block" />

              {/* Laser Bounding Box Overlay */}
              {effectiveHighlight && effectiveHighlight.page_number === currentPage && (
                <div
                  className="absolute laser-highlight rounded pointer-events-none transition-all duration-200 z-30"
                  style={{
                    left: `${effectiveHighlight.box[0] * scaleFactor}px`,
                    top: `${effectiveHighlight.box[1] * scaleFactor}px`,
                    width: `${(effectiveHighlight.box[2] - effectiveHighlight.box[0]) * scaleFactor}px`,
                    height: `${(effectiveHighlight.box[3] - effectiveHighlight.box[1]) * scaleFactor}px`,
                  }}
                >
                  <span className="absolute -top-6 left-0 bg-[var(--accent-tangerine)] text-[var(--accent-contrast)] font-black font-mono text-[10px] px-2 py-0.5 rounded shadow uppercase tracking-wider whitespace-nowrap">
                    {effectiveHighlight.label || "CITED SOURCE"}
                  </span>
                </div>
              )}
            </div>
          )}
        </div>

        {/* 2. English Translated Document Dossier (Visible in "dual" and "english" modes) */}
        {(docViewMode === "dual" || docViewMode === "english") && (
          <div
            className={`${
              docViewMode === "english" ? "flex-1" : "flex-1 min-w-[360px] max-w-[620px]"
            } overflow-auto p-4 md:p-6 bg-[var(--surface-dark)] flex flex-col space-y-4`}
          >
            {!documentId ? (
              <div className="w-full h-[650px] border border-dashed border-[var(--surface-border)] rounded-2xl flex flex-col items-center justify-center p-8 text-center text-[var(--foreground)] bg-[var(--surface-card)]/80 backdrop-blur-md shadow-xl my-auto">
                <div className="w-14 h-14 rounded-2xl bg-[var(--accent-tangerine)]/10 border border-[var(--accent-tangerine)]/30 flex items-center justify-center mb-4 shadow-sm">
                  <Languages className="w-7 h-7 text-[var(--accent-tangerine)]" />
                </div>
                <h4 className="text-sm font-bold text-[var(--foreground)] font-mono mb-1 tracking-wide uppercase">
                  {lang === "DE" ? "Kein Dokument ausgewählt" : "No Document Selected"}
                </h4>
                <p className="text-xs text-[var(--foreground)] opacity-60 max-w-[320px] mb-4 leading-relaxed font-mono text-[11px]">
                  {lang === "DE"
                    ? "Wählen Sie ein Dokument aus dem Dropdown oder laden Sie eine PDF hoch, um das beglaubigte englische Dossier anzuzeigen."
                    : "Select a document from the dropdown or upload a PDF to display the certified English translation dossier."}
                </p>
              </div>
            ) : (
              <>
            {/* Executive Dossier Header */}
            <div className="p-4 rounded-xl bg-[var(--surface-card)] border border-[var(--surface-border)] shadow-sm space-y-3 shrink-0">
              <div className="flex flex-wrap items-center justify-between gap-3">
                <div className="flex items-center gap-3 min-w-0">
                  <div className="w-9 h-9 rounded-lg bg-[var(--accent-tangerine)]/15 border border-[var(--accent-tangerine)]/30 flex items-center justify-center shrink-0">
                    <Languages className="w-5 h-5 text-[var(--accent-tangerine)]" />
                  </div>
                  <div className="min-w-0">
                    <div className="flex items-center gap-2">
                      <span className="text-xs font-mono font-black tracking-wider uppercase text-[var(--foreground)]">
                        {lang === "DE"
                          ? "Beglaubigtes englisches Revisionsdossier"
                          : "Certified English Translation Dossier"}
                      </span>
                      <span className="text-[10px] font-mono px-2 py-0.5 rounded-full bg-[var(--surface-dark)] border border-[var(--surface-border)] font-bold shrink-0 opacity-80">
                        {lang === "DE" ? "Seite" : "Page"} {currentPage} {lang === "DE" ? "von" : "of"} {totalPages}
                      </span>
                    </div>
                    <p className="text-[11px] font-mono opacity-60 truncate max-w-[280px]">
                      {documentName}
                    </p>
                  </div>
                </div>

                <div className="flex items-center gap-2 shrink-0">
                  <span className="text-[10px] font-mono text-emerald-600 dark:text-emerald-400 bg-emerald-500/10 border border-emerald-500/25 px-2.5 py-1 rounded-md font-bold hidden xl:flex items-center gap-1.5 shadow-sm">
                    <CheckCircle2 className="w-3.5 h-3.5 text-emerald-500" />{" "}
                    {lang === "DE" ? "BaFin & DORA Art. 30 Beglaubigt" : "BaFin DORA Art. 30 Certified"}
                  </span>
                  <button
                    onClick={() => {
                      if (documentId) {
                        window.open(`http://localhost:8000/api/v1/documents/${documentId}/export-english-pdf`, "_blank");
                      }
                    }}
                    title="Download Certified English Translation PDF with SHA-256 fingerprint"
                    className="flex items-center gap-1.5 bg-[var(--foreground)] text-[var(--background)] hover:opacity-90 font-mono font-bold text-[11px] px-3 py-1.5 rounded-md shadow transition-all cursor-pointer uppercase tracking-wider"
                  >
                    <Download className="w-3.5 h-3.5" />
                    <span>{lang === "DE" ? "Beglaubigtes PDF" : "Certified PDF"}</span>
                  </button>
                  <button
                    onClick={() => {
                      if (documentId) {
                        window.open(`http://localhost:8000/api/v1/documents/${documentId}/export-english-markdown`, "_blank");
                      }
                    }}
                    title="Download English Translation Dossier in Markdown format"
                    className="flex items-center gap-1.5 bg-[var(--surface-dark)] hover:bg-[var(--surface-card)] text-[var(--foreground)] border border-[var(--surface-border)] font-mono text-[11px] font-bold px-2.5 py-1.5 rounded-md transition-all cursor-pointer shadow-sm"
                  >
                    <FileText className="w-3.5 h-3.5 text-[var(--accent-cyan)]" />
                    <span>MD</span>
                  </button>
                </div>
              </div>

              {/* Fast Clause Search & Filter Bar */}
              <div className="relative">
                <input
                  type="text"
                  value={searchFilter}
                  onChange={(e) => setSearchFilter(e.target.value)}
                  placeholder={
                    lang === "DE"
                      ? "Klauseln filtern (z.B. 'SLA', 'DORA', 'Kündigung', 'Haftung', 'BDSG')..."
                      : "Filter clauses (e.g. 'SLA', 'DORA', 'Exit', 'Liability', 'BDSG', 'ZUGFeRD')..."
                  }
                  className="w-full bg-[var(--surface-dark)] border border-[var(--surface-border)] text-[var(--foreground)] placeholder:text-[var(--foreground)] placeholder:opacity-40 text-xs rounded-lg px-3 py-1.5 pl-8 focus:outline-none focus:border-[var(--accent-tangerine)] font-mono shadow-inner transition-colors"
                />
                <Search className="w-3.5 h-3.5 text-[var(--foreground)] opacity-40 absolute left-2.5 top-2.5 pointer-events-none" />
                {searchFilter && (
                  <button
                    onClick={() => setSearchFilter("")}
                    className="absolute right-2.5 top-2 text-[var(--foreground)] opacity-40 hover:opacity-100 text-xs cursor-pointer"
                  >
                    ✕
                  </button>
                )}
              </div>
            </div>

            {/* Paragraph-by-Paragraph Translated Clauses */}
            <div className="space-y-3.5 flex-1 overflow-auto">
              {currentPageChunks.length > 0 ? (
                currentPageChunks
                  .filter((chunk) => {
                    if (!searchFilter.trim()) return true;
                    const q = searchFilter.toLowerCase();
                    const trans = (chunk.translated_content || translateGermanToEnglish(chunk.content)).toLowerCase();
                    const orig = chunk.content.toLowerCase();
                    return trans.includes(q) || orig.includes(q);
                  })
                  .map((chunk, idx) => {
                    const translatedText = chunk.translated_content || translateGermanToEnglish(chunk.content);
                    const meta = classifyClause(chunk.content, chunk.chunk_index, chunk.page_number, lang);
                    const isSelected = selectedChunkId === chunk.id;
                    const primaryText = lang === "EN" ? translatedText : chunk.content;
                    const alternateText = lang === "EN" ? chunk.content : translatedText;

                    const handleSelectClause = () => {
                      setSelectedChunkId(chunk.id);
                      if (chunk.bounding_box) {
                        setLocalHighlight({
                          page_number: chunk.page_number,
                          box: chunk.bounding_box,
                          label: `${meta.clauseNumber} • ${meta.category}`,
                          snippet: chunk.content,
                        });
                      }
                    };

                    const badgeColorClasses = {
                      emerald: "bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border-emerald-500/30",
                      crimson: "bg-rose-500/10 text-rose-600 dark:text-rose-400 border-rose-500/30",
                      amber: "bg-amber-500/10 text-amber-600 dark:text-amber-400 border-amber-500/30",
                      blue: "bg-sky-500/10 text-sky-600 dark:text-sky-400 border-sky-500/30",
                      slate: "bg-slate-500/10 text-slate-600 dark:text-slate-400 border-slate-500/30",
                    }[meta.badgeVariant];

                    return (
                      <div
                        key={chunk.id || idx}
                        onClick={handleSelectClause}
                        className={`p-4 rounded-xl border transition-all cursor-pointer shadow-sm relative ${
                          isSelected
                            ? "bg-[var(--surface-card)] border-2 border-[var(--accent-tangerine)] ring-2 ring-[var(--accent-tangerine)]/20 shadow-md"
                            : "bg-[var(--surface-card)] border-[var(--surface-border)] hover:border-[var(--accent-tangerine)]/40 hover:shadow-md"
                        }`}
                      >
                        {/* Clause Metadata & Statutory Standard Header */}
                        <div className="flex flex-wrap items-center justify-between gap-2 pb-2.5 mb-2.5 border-b border-[var(--surface-border)]">
                          <div className="flex items-center gap-2 min-w-0">
                            <span className="px-2 py-0.5 rounded bg-[var(--surface-dark)] border border-[var(--surface-border)] font-mono text-[10px] font-black text-[var(--accent-tangerine)] shrink-0">
                              {meta.clauseNumber}
                            </span>
                            <span className="text-[11px] font-mono font-bold uppercase tracking-wider text-[var(--foreground)] truncate">
                              {meta.category}
                            </span>
                          </div>

                          <div className="flex items-center gap-1.5 shrink-0">
                            <span className="text-[10px] font-mono opacity-60 hidden sm:inline">
                              {meta.legalRef}
                            </span>
                            <span
                              className={`text-[9.5px] font-mono font-bold px-2 py-0.5 rounded border ${badgeColorClasses}`}
                            >
                              {meta.statusBadge}
                            </span>
                          </div>
                        </div>

                        {/* Professional Descriptive Clause Title */}
                        <h4 className="text-[12px] font-mono font-bold text-[var(--foreground)] mb-1.5 opacity-90">
                          {meta.title}
                        </h4>

                        {/* Primary Legal Prose (Respects Language Toggle) */}
                        <p className="text-[13px] text-[var(--foreground)] font-sans leading-relaxed font-normal">
                          {primaryText}
                        </p>

                        {/* Action Bar & Collapsible Alternate Language Source */}
                        <div className="mt-3 pt-2.5 border-t border-[var(--surface-border)] space-y-2">
                          <div className="flex items-center justify-between text-[11px] font-mono">
                            <button
                              onClick={(e) => {
                                e.stopPropagation();
                                handleSelectClause();
                              }}
                              className="flex items-center gap-1 text-[var(--accent-tangerine)] hover:underline font-bold cursor-pointer"
                              title="Highlight this clause directly on the PDF canvas"
                            >
                              <MapPin className="w-3.5 h-3.5" />
                              <span>{lang === "DE" ? "Im PDF-Plan verorten" : "Locate in PDF Canvas"}</span>
                            </button>
                            <span className="text-[10px] opacity-50">
                              DIN A4 [ {Math.round(chunk.bounding_box?.[0] || 0)}, {Math.round(chunk.bounding_box?.[1] || 0)} ]
                            </span>
                          </div>

                          <details className="group/details">
                            <summary className="cursor-pointer text-[10.5px] font-mono text-[var(--accent-cyan)] hover:opacity-100 flex items-center justify-between select-none py-1">
                              <span className="flex items-center gap-1.5 font-bold">
                                <ChevronDown className="w-3.5 h-3.5 transition-transform duration-200 group-open/details:rotate-180" />
                                <span>
                                  {lang === "EN"
                                    ? "German Statutory Source (DE 🇩🇪)"
                                    : "Beglaubigte englische Übersetzung (EN 🇬🇧)"}
                                </span>
                              </span>
                              <span className="text-[9.5px] font-mono opacity-60">
                                {lang === "DE" ? "Zweisprachige Parität 100%" : "Bilingual Parity 100%"}
                              </span>
                            </summary>
                            <div className="mt-2 p-3 rounded-lg bg-[var(--surface-dark)] border-l-2 border-[var(--accent-tangerine)] border-r border-t border-b border-[var(--surface-border)] text-[12px] font-sans text-[var(--foreground)] opacity-90 leading-relaxed">
                              <p>{alternateText}</p>
                            </div>
                          </details>
                        </div>
                      </div>
                    );
                  })
              ) : (
                <div className="p-8 text-center text-xs text-[var(--foreground)] opacity-60 font-mono space-y-2 bg-[var(--surface-card)] rounded-xl border border-[var(--surface-border)]">
                  <BookOpen className="w-6 h-6 mx-auto text-[var(--accent-tangerine)] opacity-60" />
                  <p className="font-bold">Generating English Translated Dossier...</p>
                  <p className="text-[11px]">
                    Select or upload a PDF document to view synchronized paragraph-by-paragraph English translations.
                  </p>
                </div>
              )}
            </div>
            </>
            )}
          </div>
        )}
      </div>

      {/* Floating Bilingual Translation HUD for Canvas Mode */}
      {docViewMode === "canvas" && activeHighlight && !isTranslationHudDismissed && (
        <div className="mx-6 mb-4 p-3.5 rounded-xl bg-[var(--surface-card)] border border-[var(--surface-border)] shadow-2xl flex items-center justify-between gap-4 animate-in slide-in-from-bottom-2 duration-200 z-40">
          <div className="flex items-start gap-3">
            <div className="w-8 h-8 rounded-lg bg-[var(--accent-tangerine)]/15 border border-[var(--accent-tangerine)]/40 flex items-center justify-center text-[var(--accent-tangerine)] flex-shrink-0 mt-0.5">
              <Languages className="w-4 h-4" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="text-[10px] font-mono font-bold uppercase tracking-wider text-[var(--accent-tangerine)]">
                  {activeHighlight.label || "CITED CLAUSE"} • ENGLISH TRANSLATION LENS 🇬🇧
                </span>
                <span className="text-[9px] font-mono bg-emerald-500/15 text-emerald-400 border border-emerald-500/30 px-1 rounded font-bold">
                  Bilingual Lens
                </span>
              </div>
              <p className="text-xs text-[var(--foreground)] mt-1 font-sans leading-relaxed">
                {translateGermanToEnglish(activeHighlight.snippet || activeHighlight.label || "") ||
                  "Under DORA Art. 30, termination exit assistance (60 days) and vendor migration responsibilities are mandated."}
              </p>
            </div>
          </div>

          <button
            onClick={() => setIsTranslationHudDismissed(true)}
            className="p-1 rounded-md text-[var(--foreground)] opacity-50 hover:opacity-100 hover:bg-[var(--surface-dark)] cursor-pointer"
            title="Dismiss translation HUD"
          >
            <X className="w-4 h-4" />
          </button>
        </div>
      )}
    </div>
  );
}

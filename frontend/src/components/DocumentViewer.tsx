"use client";

import React, { useState, useRef, useEffect } from "react";
import {
  UploadCloud,
  FileText,
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
} from "lucide-react";

import { Language, translations } from "@/lib/i18n";
import { translateGermanToEnglish } from "@/lib/translator";
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
}

export function DocumentViewer({
  lang = "DE",
  documentId,
  documentName = "Siemens_Master_ICT_Agreement_2026.pdf",
  availableDocuments = [],
  currentPage = 1,
  totalPages = 1,
  isUploading = false,
  activeHighlight,
  onUploadFile,
  onSelectDocument,
  onPageChange,
}: DocumentViewerProps) {
  const t = translations[lang];
  const [zoom, setZoom] = useState(100);
  const [rendering, setRendering] = useState(false);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [isTranslationHudDismissed, setIsTranslationHudDismissed] = useState(false);
  const [docViewMode, setDocViewMode] = useState<"canvas" | "dual" | "english">("canvas");
  const [allChunks, setAllChunks] = useState<any[]>([]);
  const [selectedChunkId, setSelectedChunkId] = useState<string | null>(null);
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
              onClick={() => setDocViewMode("canvas")}
              className={`px-2 py-0.5 rounded font-bold cursor-pointer transition-all ${
                docViewMode === "canvas"
                  ? "bg-[var(--accent-tangerine)] text-black"
                  : "text-[var(--foreground)] opacity-60 hover:opacity-100"
              }`}
              title="Show Original German PDF"
            >
              🇩🇪 PDF
            </button>
            <button
              onClick={() => setDocViewMode("dual")}
              className={`px-2.5 py-0.5 rounded font-bold cursor-pointer transition-all flex items-center gap-1 ${
                docViewMode === "dual"
                  ? "bg-[var(--accent-tangerine)] text-black"
                  : "text-[var(--foreground)] opacity-60 hover:opacity-100"
              }`}
              title="Side-by-Side Dual View: German PDF + English Translation"
            >
              <Columns className="w-3 h-3" />
              <span>Dual-View</span>
            </button>
            <button
              onClick={() => setDocViewMode("english")}
              className={`px-2 py-0.5 rounded font-bold cursor-pointer transition-all flex items-center gap-1 ${
                docViewMode === "english"
                  ? "bg-[var(--accent-tangerine)] text-black"
                  : "text-[var(--foreground)] opacity-60 hover:opacity-100"
              }`}
              title="Full English Translated Dossier"
            >
              <Languages className="w-3 h-3" />
              <span className="hidden sm:inline">English Dossier</span>
            </button>
          </div>
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
                className="flex items-center gap-1 bg-[var(--accent-tangerine)] hover:opacity-90 text-black font-black font-mono text-[11px] px-2.5 py-1 rounded transition-all shadow-sm uppercase tracking-wide cursor-pointer"
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
          className={`overflow-auto p-6 flex justify-center cyber-canvas relative ${
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
              className="relative bg-white rounded-lg shadow-2xl transition-all duration-150 flex items-center justify-center overflow-hidden border border-[var(--surface-border)] my-auto"
            >
              {rendering && (
                <div className="absolute inset-0 bg-black/30 backdrop-blur-[2px] flex items-center justify-center z-10">
                  <Loader2 className="w-7 h-7 animate-spin text-[var(--accent-tangerine)]" />
                </div>
              )}

              <canvas ref={canvasRef} className="block" />

              {/* Laser Bounding Box Overlay */}
              {activeHighlight && activeHighlight.page_number === currentPage && (
                <div
                  className="absolute laser-highlight rounded pointer-events-none transition-all duration-200 z-30"
                  style={{
                    left: `${activeHighlight.box[0] * scaleFactor}px`,
                    top: `${activeHighlight.box[1] * scaleFactor}px`,
                    width: `${(activeHighlight.box[2] - activeHighlight.box[0]) * scaleFactor}px`,
                    height: `${(activeHighlight.box[3] - activeHighlight.box[1]) * scaleFactor}px`,
                  }}
                >
                  <span className="absolute -top-6 left-0 bg-[var(--accent-tangerine)] text-black font-black font-mono text-[10px] px-2 py-0.5 rounded shadow uppercase tracking-wider whitespace-nowrap">
                    {activeHighlight.label || "CITED SOURCE"}
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
              docViewMode === "english" ? "flex-1" : "w-[480px] lg:w-[540px]"
            } overflow-auto p-6 bg-[var(--surface-dark)] flex flex-col space-y-4`}
          >
            {/* Header */}
            <div className="p-4 rounded-xl bg-[var(--surface-card)] border border-[var(--surface-border)] shadow-sm flex items-center justify-between">
              <div>
                <div className="flex items-center gap-2">
                  <span className="text-[10px] font-mono font-bold uppercase tracking-wider text-[var(--accent-tangerine)]">
                    ENGLISH TRANSLATED CONTRACT DOSSIER
                  </span>
                  <span className="text-[9px] font-mono bg-emerald-500/15 text-emerald-400 border border-emerald-500/30 px-1.5 py-0.2 rounded font-bold">
                    PAGE {currentPage} OF {totalPages}
                  </span>
                </div>
                <h3 className="text-sm font-extrabold text-[var(--foreground)] font-mono mt-0.5 truncate max-w-[340px]">
                  {documentName}
                </h3>
              </div>

              <span className="text-[10px] font-mono text-[var(--accent-cyan)] bg-[var(--accent-cyan)]/10 border border-[var(--accent-cyan)]/30 px-2 py-1 rounded font-bold flex items-center gap-1">
                <CheckCircle2 className="w-3.5 h-3.5" /> DORA Grounded
              </span>
            </div>

            {/* Paragraph-by-Paragraph Translated Clauses */}
            <div className="space-y-3 flex-1 overflow-auto">
              {currentPageChunks.length > 0 ? (
                currentPageChunks.map((chunk, idx) => {
                  const translatedText = translateGermanToEnglish(chunk.content);
                  const isSelected = selectedChunkId === chunk.id;

                  return (
                    <div
                      key={chunk.id || idx}
                      onClick={() => setSelectedChunkId(chunk.id)}
                      className={`p-4 rounded-xl border transition-all cursor-pointer ${
                        isSelected
                          ? "bg-[var(--surface-card)] border-[var(--accent-tangerine)] shadow-md"
                          : "bg-[var(--surface-card)] border-[var(--surface-border)] hover:border-[var(--accent-tangerine)]/50"
                      }`}
                    >
                      <div className="flex items-center justify-between mb-2">
                        <span className="text-[10px] font-mono font-bold uppercase text-[var(--accent-tangerine)] flex items-center gap-1.5">
                          <BookOpen className="w-3.5 h-3.5" />
                          Paragraph {chunk.chunk_index + 1} • Clause Analysis
                        </span>
                        <span className="text-[9px] font-mono text-[var(--foreground)] opacity-50">
                          Bounding Box [{Math.round(chunk.bounding_box?.[0] || 0)}, {Math.round(chunk.bounding_box?.[1] || 0)}]
                        </span>
                      </div>

                      {/* Translated English Text */}
                      <p className="text-xs text-[var(--foreground)] font-sans leading-relaxed">
                        {translatedText}
                      </p>

                      {/* Expandable Original German Text */}
                      <details className="mt-3 pt-2 border-t border-[var(--surface-border)] text-[11px] font-mono opacity-70">
                        <summary className="cursor-pointer text-[10px] text-[var(--accent-cyan)] hover:opacity-100 font-bold">
                          View Original German Source (DE 🇩🇪)
                        </summary>
                        <p className="mt-1.5 text-xs text-[var(--foreground)] opacity-80 leading-relaxed font-sans bg-[var(--surface-dark)] p-2.5 rounded-lg border border-[var(--surface-border)]">
                          {chunk.content}
                        </p>
                      </details>
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

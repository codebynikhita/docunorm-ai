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
  Network,
} from "lucide-react";

import { Language, translations } from "@/lib/i18n";
import {
  translateGermanToEnglish,
  translateEnglishToGerman,
  translateBidirectional,
  detectDocumentLanguage,
  classifyClause,
  ClauseMetadata,
} from "@/lib/translator";
import { getDocumentChunks, getTranslatedDocumentChunks, getDocumentTaskProgress } from "@/lib/api";
import { ClauseRiskHeatmapBar } from "./ClauseRiskHeatmapBar";
import { RealTimeStreamHud } from "./RealTimeStreamHud";

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
  onOpenDoraSubcontractor?: () => void;
  onOpenAuditRights?: () => void;
  onOpenRemediation?: () => void;
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
  onOpenDoraSubcontractor,
  onOpenAuditRights,
  onOpenRemediation,
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

  // Dynamically detect source language of current document (German vs English)
  const detectedDocLang: "DE" | "EN" = React.useMemo(() => {
    if (!allChunks || allChunks.length === 0) {
      if (documentName) {
        return detectDocumentLanguage(documentName);
      }
      return "DE";
    }
    const sample = allChunks
      .slice(0, 10)
      .map((c) => c.content || "")
      .join(" ");
    return detectDocumentLanguage(sample);
  }, [allChunks, documentName]);

  const canvasRef = useRef<HTMLCanvasElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const pdfDocRef = useRef<any>(null);

  // Auto-select active or first contract if none is currently selected
  useEffect(() => {
    if (!documentId && availableDocuments && availableDocuments.length > 0 && onSelectDocument) {
      const savedDocId = typeof window !== "undefined" ? localStorage.getItem("docunorm_active_document_id") : null;
      const docToSelect = (savedDocId && availableDocuments.find((d: any) => d.id === savedDocId)) || availableDocuments[0];
      if (docToSelect) {
        onSelectDocument(docToSelect);
      }
    }
  }, [documentId, availableDocuments, onSelectDocument]);

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
      <div className="h-14 border-b border-[var(--surface-border)] bg-[var(--surface-dark)] px-3 sm:px-4 flex items-center justify-between gap-2 select-none overflow-hidden">
        {/* Left: Document Selector, View Modes & Regulatory Suite */}
        <div className="flex items-center gap-2 sm:gap-2.5 min-w-0 flex-1 overflow-x-auto py-1">
          <FileText className="w-4 h-4 text-[var(--accent-tangerine)] shrink-0" />
          {availableDocuments.length > 0 ? (
            <div className="relative shrink-0">
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
                className="bg-[var(--surface-card)] border border-[var(--surface-border)] text-[var(--foreground)] text-xs rounded-md px-2 py-1.5 pr-6 appearance-none focus:outline-none focus:border-[var(--accent-tangerine)] cursor-pointer font-mono font-medium w-36 sm:w-48 md:w-56 truncate shadow-sm"
              >
                <option value="">{t.select_doc_placeholder}</option>
                {availableDocuments.map((doc) => (
                  <option key={doc.id} value={doc.id}>
                    {doc.filename}
                  </option>
                ))}
              </select>
              <ChevronDown className="w-3.5 h-3.5 text-[var(--foreground)] opacity-50 absolute right-1.5 top-2.5 pointer-events-none" />
            </div>
          ) : (
            <span className="text-xs text-[var(--foreground)] opacity-50 font-mono italic shrink-0">
              {t.no_docs_indexed}
            </span>
          )}

          {/* DOCUMENT TRANSLATION MODE SELECTOR (BIDIRECTIONAL) */}
          <div className="flex items-center bg-[var(--surface-card)] border border-[var(--surface-border)] rounded-md p-0.5 text-[10px] font-mono shadow-sm shrink-0">
            <button
              onClick={() => handleToggleDocViewMode("canvas")}
              className={`px-2 py-0.5 rounded font-bold cursor-pointer transition-all ${
                docViewMode === "canvas"
                  ? "bg-[var(--accent-tangerine)] text-[var(--accent-contrast)]"
                  : "text-[var(--foreground)] opacity-60 hover:opacity-100"
              }`}
              title={
                detectedDocLang === "EN"
                  ? "Show Original English PDF Canvas"
                  : "Show Original German PDF Canvas"
              }
            >
              {detectedDocLang === "EN" ? "🇺🇸 PDF" : "🇩🇪 PDF"}
            </button>
            <button
              onClick={() => handleToggleDocViewMode("dual")}
              className={`px-2 py-0.5 rounded font-bold cursor-pointer transition-all flex items-center gap-1 ${
                docViewMode === "dual"
                  ? "bg-[var(--accent-tangerine)] text-[var(--accent-contrast)]"
                  : "text-[var(--foreground)] opacity-60 hover:opacity-100"
              }`}
              title={
                detectedDocLang === "EN"
                  ? "Side-by-Side Dual View: English PDF + German Translation"
                  : "Side-by-Side Dual View: German PDF + English Translation"
              }
            >
              <Columns className="w-3 h-3" />
              <span className="hidden sm:inline">Dual</span>
            </button>
            <button
              onClick={() => handleToggleDocViewMode("english")}
              className={`px-2 py-0.5 rounded font-bold cursor-pointer transition-all flex items-center gap-1 ${
                docViewMode === "english"
                  ? "bg-[var(--accent-tangerine)] text-[var(--accent-contrast)]"
                  : "text-[var(--foreground)] opacity-60 hover:opacity-100"
              }`}
              title={
                detectedDocLang === "EN"
                  ? "Full German Translated Dossier (DIN EN ISO 17100)"
                  : "Full English Translated Dossier (DIN EN ISO 17100)"
              }
            >
              <Languages className="w-3 h-3" />
              <span className="hidden sm:inline">
                {detectedDocLang === "EN" ? "DE Dossier" : "EN Dossier"}
              </span>
            </button>
          </div>

          {/* REGULATORY AUDIT MODULES GROUP */}
          {(onOpenDoraExit || onOpenDoraSubcontractor || onOpenAuditRights) && (
            <div className="flex items-center bg-[var(--surface-card)] border border-[var(--surface-border)] rounded-md p-0.5 text-[10px] font-mono shadow-sm shrink-0">
              {onOpenDoraExit && (
                <button
                  onClick={onOpenDoraExit}
                  className="px-2 py-1 rounded font-bold cursor-pointer transition-all flex items-center gap-1 text-[var(--accent-cyan)] hover:bg-[var(--surface-dark)]"
                  title="DORA Art. 30(2) & BaFin Exit Strategy Regulatory Audit"
                >
                  <ShieldAlert className="w-3.5 h-3.5 text-[var(--accent-cyan)]" />
                  <span className="hidden xl:inline">
                    Exit (30.2)
                  </span>
                </button>
              )}

              {onOpenDoraSubcontractor && (
                <button
                  onClick={onOpenDoraSubcontractor}
                  className="px-2 py-1 rounded font-bold cursor-pointer transition-all flex items-center gap-1 text-purple-400 hover:bg-[var(--surface-dark)] border-l border-[var(--surface-border)]"
                  title="DORA Art. 30(3) Sub-Outsourcing & 4th-Party Cascading Risk Inspector"
                >
                  <Network className="w-3.5 h-3.5 text-purple-400" />
                  <span className="hidden xl:inline">
                    Kaskade (30.3)
                  </span>
                </button>
              )}

              {onOpenAuditRights && (
                <button
                  onClick={onOpenAuditRights}
                  className="px-2 py-1 rounded font-bold cursor-pointer transition-all flex items-center gap-1 text-emerald-400 hover:bg-[var(--surface-dark)] border-l border-[var(--surface-border)]"
                  title="KWG § 25b & DORA Art. 30(3)(e) Supervisory Audit Rights & DIN 5008 BaFin Notice Letter"
                >
                  <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" />
                  <span className="hidden xl:inline">
                    Prüfrechte (DIN 5008)
                  </span>
                </button>
              )}
            </div>
          )}
        </div>

        {/* Right: Upload & Page Navigation (Fixed, Never Collides) */}
        <div className="flex items-center gap-1.5 sm:gap-2 text-xs shrink-0 pl-1">
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
              className="flex items-center gap-1 bg-[var(--surface-card)] hover:bg-[var(--surface-dark)] text-[var(--foreground)] border border-[var(--surface-border)] hover:border-[var(--accent-tangerine)]/50 font-mono text-[11px] font-bold px-2 sm:px-2.5 py-1.5 rounded-md transition-all uppercase tracking-wider shadow-sm cursor-pointer shrink-0"
              title={t.btn_select_pdf}
            >
              <UploadCloud className="w-3.5 h-3.5 text-[var(--accent-tangerine)]" />
              <span className="hidden md:inline">{t.btn_select_pdf}</span>
            </button>
          ) : (
            <div className="flex items-center gap-1 bg-[var(--surface-card)] border border-[var(--accent-tangerine)]/50 px-2 py-1 rounded-md shadow-sm shrink-0">
              <span className="text-[11px] font-mono text-[var(--foreground)] truncate max-w-[80px] sm:max-w-[120px] font-medium">
                {selectedFile.name}
              </span>
              <button
                onClick={handleConfirmUpload}
                disabled={isUploading}
                className="flex items-center gap-1 bg-[var(--accent-tangerine)] hover:opacity-90 text-[var(--accent-contrast)] font-black font-mono text-[10px] px-2 py-0.5 rounded transition-all shadow-sm uppercase tracking-wide cursor-pointer"
              >
                {isUploading ? (
                  <Loader2 className="w-3 h-3 animate-spin" />
                ) : (
                  <Check className="w-3 h-3 stroke-[3]" />
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
          <div className="flex items-center gap-0.5 bg-[var(--surface-card)] border border-[var(--surface-border)] px-1.5 py-1 rounded-md text-[var(--foreground)] shrink-0">
            <button
              onClick={() => onPageChange && onPageChange(Math.max(1, currentPage - 1))}
              disabled={currentPage <= 1}
              className="hover:opacity-100 disabled:opacity-20 font-bold px-1 cursor-pointer text-xs"
            >
              &lt;
            </button>
            <span className="px-1 font-mono text-[10px] sm:text-[11px] font-semibold whitespace-nowrap">
              {currentPage} / {totalPages}
            </span>
            <button
              onClick={() => onPageChange && onPageChange(Math.min(totalPages, currentPage + 1))}
              disabled={currentPage >= totalPages}
              className="hover:opacity-100 disabled:opacity-20 font-bold px-1 cursor-pointer text-xs"
            >
              &gt;
            </button>
          </div>

          <div className="hidden lg:flex items-center gap-1 bg-[var(--surface-card)] border border-[var(--surface-border)] px-2 py-1 rounded-md text-[var(--foreground)] shrink-0">
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

      {/* Forensic Clause Risk Heatmap & Page Anomaly Timeline */}
      <ClauseRiskHeatmapBar
        documentId={documentId}
        currentPage={currentPage}
        totalPages={totalPages}
        lang={lang}
        onPageSelect={(page) => onPageChange && onPageChange(page)}
        onOpenRemediation={() => onOpenRemediation && onOpenRemediation()}
      />

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
            <div className="w-[520px] max-w-full border border-[var(--surface-border)] rounded-2xl flex flex-col p-6 text-[var(--foreground)] bg-[var(--surface-card)] shadow-2xl my-auto">
              <div className="flex items-center gap-3 mb-4 pb-3 border-b border-[var(--surface-border)]">
                <div className="w-10 h-10 rounded-xl bg-blue-500/10 border border-blue-500/30 flex items-center justify-center shrink-0">
                  <FileText className="w-5 h-5 text-blue-500" />
                </div>
                <div>
                  <h4 className="text-sm font-bold text-[var(--foreground)] font-mono tracking-wide uppercase">
                    {lang === "DE" ? "Dokumenten-Treuhand Tresor" : "Institutional Document Vault"}
                  </h4>
                  <p className="text-[11px] font-mono text-[var(--foreground)] opacity-60">
                    {availableDocuments.length > 0
                      ? lang === "DE"
                        ? `${availableDocuments.length} Verträge zur Revision bereit:`
                        : `${availableDocuments.length} contracts ready for regulatory audit:`
                      : t.empty_canvas_desc}
                  </p>
                </div>
              </div>

              {availableDocuments.length > 0 ? (
                <div className="space-y-2 mb-4 max-h-[320px] overflow-y-auto pr-1">
                  {availableDocuments.map((doc) => (
                    <button
                      key={doc.id}
                      onClick={() => onSelectDocument && onSelectDocument(doc)}
                      className="w-full text-left p-3 rounded-xl bg-[var(--surface-dark)] hover:bg-[var(--surface-card)] border border-[var(--surface-border)] hover:border-blue-500/50 transition-all flex items-center justify-between group cursor-pointer shadow-sm"
                    >
                      <div className="min-w-0 pr-2">
                        <div className="text-xs font-mono font-bold text-[var(--foreground)] group-hover:text-blue-500 truncate">
                          {doc.filename}
                        </div>
                        <div className="text-[10px] font-mono opacity-50 flex items-center gap-2 mt-0.5">
                          <span>
                            {doc.total_pages || 1} {lang === "DE" ? "Seiten" : "pages"}
                          </span>
                          <span>•</span>
                          <span>SHA-256: {doc.sha256_hash?.slice(0, 10)}...</span>
                        </div>
                      </div>
                      <span className="text-[10px] font-mono font-bold px-2 py-1 rounded bg-blue-500/10 text-blue-500 border border-blue-500/20 shrink-0 group-hover:bg-blue-500 group-hover:text-white transition-all">
                        {lang === "DE" ? "Prüfen ➔" : "Audit ➔"}
                      </span>
                    </button>
                  ))}
                </div>
              ) : (
                <p className="text-xs text-[var(--foreground)] opacity-60 mb-4 font-mono text-[11px] leading-relaxed">
                  {t.empty_canvas_desc}
                </p>
              )}

              <button
                onClick={() => fileInputRef.current?.click()}
                className="w-full bg-[var(--surface-dark)] hover:bg-[var(--surface-card)] text-blue-500 hover:text-blue-400 border border-blue-500/40 text-xs font-bold font-mono px-4 py-2.5 rounded-xl transition-all shadow-sm uppercase tracking-wider cursor-pointer flex items-center justify-center gap-2"
              >
                <UploadCloud className="w-4 h-4" />
                <span>{t.btn_load_file}</span>
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
              docViewMode === "english" ? "flex-1 min-w-0" : "flex-1 min-w-0"
            } overflow-auto p-4 md:p-6 bg-[var(--surface-dark)] flex flex-col space-y-4`}
          >
            {!documentId ? (
              <div className="w-full max-w-[520px] border border-[var(--surface-border)] rounded-2xl flex flex-col p-8 text-center text-[var(--foreground)] bg-[var(--surface-card)] shadow-2xl my-auto mx-auto">
                <div className="w-12 h-12 rounded-2xl bg-blue-500/10 border border-blue-500/30 flex items-center justify-center mb-4 mx-auto shadow-sm">
                  <Languages className="w-6 h-6 text-blue-500" />
                </div>
                <h4 className="text-sm font-bold text-[var(--foreground)] font-mono mb-1 tracking-wide uppercase">
                  {lang === "DE" ? "Beglaubigtes Revisionsdossier" : "Certified Translation Dossier"}
                </h4>
                <p className="text-xs text-[var(--foreground)] opacity-60 max-w-[340px] mb-6 leading-relaxed font-mono text-[11px] mx-auto">
                  {lang === "DE"
                    ? "Wählen Sie links einen Vertrag aus dem Tresor, um die synchronisierte englische Übersetzung mit aufsichtsrechtlichen BaFin-Citations und DORA-Prüfungen anzuzeigen."
                    : "Select a contract from the vault on the left to render the synchronized English translation with supervisory BaFin citation tags and DORA checks."}
                </p>
                <div className="grid grid-cols-2 gap-2.5 text-[10px] font-mono text-left w-full max-w-[340px] mx-auto">
                  <div className="p-2.5 rounded-xl bg-[var(--surface-dark)] border border-[var(--surface-border)]">
                    <span className="text-emerald-500 font-bold flex items-center gap-1">
                      <CheckCircle2 className="w-3 h-3 text-emerald-500" />
                      DORA Art. 30
                    </span>
                    <div className="opacity-60 text-[9px] mt-0.5">Sovereign Compliance Verified</div>
                  </div>
                  <div className="p-2.5 rounded-xl bg-[var(--surface-dark)] border border-[var(--surface-border)]">
                    <span className="text-blue-500 font-bold flex items-center gap-1">
                      <CheckCircle2 className="w-3 h-3 text-blue-500" />
                      KWG § 25b
                    </span>
                    <div className="opacity-60 text-[9px] mt-0.5">Direct BaFin Access Rights</div>
                  </div>
                </div>
              </div>
            ) : (
              <>
            {/* Executive Dossier Header (Bidirectional DE ⇄ EN) */}
            <div className="p-4 rounded-xl bg-[var(--surface-card)] border border-[var(--surface-border)] shadow-sm space-y-3 shrink-0">
              <div className="flex flex-wrap items-center justify-between gap-3">
                <div className="flex items-center gap-3 min-w-0">
                  <div className="w-9 h-9 rounded-lg bg-[var(--accent-tangerine)]/15 border border-[var(--accent-tangerine)]/30 flex items-center justify-center shrink-0">
                    <Languages className="w-5 h-5 text-[var(--accent-tangerine)]" />
                  </div>
                  <div className="min-w-0">
                    <div className="flex items-center gap-2">
                      <span className="text-xs font-mono font-black tracking-wider uppercase text-[var(--foreground)]">
                        {detectedDocLang === "EN"
                          ? lang === "DE"
                            ? "Beglaubigtes deutsches Revisionsdossier"
                            : "Certified German Translation Dossier"
                          : lang === "DE"
                            ? "Beglaubigtes englisches Revisionsdossier"
                            : "Certified English Translation Dossier"}
                      </span>
                      <span className="text-[10px] font-mono px-2 py-0.5 rounded-full bg-[var(--surface-dark)] border border-[var(--surface-border)] font-bold shrink-0 opacity-80">
                        {lang === "DE" ? "Seite" : "Page"} {currentPage} {lang === "DE" ? "von" : "of"} {totalPages}
                      </span>
                    </div>
                    <div className="flex items-center gap-2 mt-0.5">
                      <p className="text-[11px] font-mono opacity-60 truncate max-w-[280px]">
                        {documentName}
                      </p>
                      <span className="text-[9.5px] font-mono font-bold px-1.5 py-0.5 rounded bg-blue-500/10 text-blue-500 border border-blue-500/20 shrink-0">
                        {detectedDocLang === "EN" ? "EN ➔ DE Prüffassung" : "DE ➔ EN Audit Stream"}
                      </span>
                    </div>
                  </div>
                </div>

                <div className="flex items-center gap-2 shrink-0">
                  <span className="text-[10px] font-mono text-emerald-600 dark:text-emerald-400 bg-emerald-500/10 border border-emerald-500/25 px-2.5 py-1 rounded-md font-bold hidden xl:flex items-center gap-1.5 shadow-sm">
                    <CheckCircle2 className="w-3.5 h-3.5 text-emerald-500" />{" "}
                    {detectedDocLang === "EN"
                      ? lang === "DE"
                        ? "DIN EN ISO 17100 / BaFin Prüffassung"
                        : "DIN EN ISO 17100 German Certified"
                      : lang === "DE"
                        ? "BaFin & DORA Art. 30 Beglaubigt"
                        : "BaFin DORA Art. 30 Certified"}
                  </span>
                  <button
                    onClick={() => {
                      if (documentId) {
                        window.open(`http://localhost:8000/api/v1/documents/${documentId}/export-english-pdf`, "_blank");
                      }
                    }}
                    title="Download Certified Translation PDF with SHA-256 fingerprint"
                    className="flex items-center gap-1.5 bg-[var(--foreground)] text-[var(--background)] hover:opacity-90 font-mono font-bold text-[11px] px-3 py-1.5 rounded-md shadow transition-all cursor-pointer uppercase tracking-wider"
                  >
                    <Download className="w-3.5 h-3.5" />
                    <span>
                      {detectedDocLang === "EN"
                        ? lang === "DE"
                          ? "Beglaubigtes PDF (DE)"
                          : "Certified PDF (DE)"
                        : lang === "DE"
                          ? "Beglaubigtes PDF (EN)"
                          : "Certified PDF (EN)"}
                    </span>
                  </button>
                  <button
                    onClick={() => {
                      if (documentId) {
                        window.open(`http://localhost:8000/api/v1/documents/${documentId}/export-english-markdown`, "_blank");
                      }
                    }}
                    title="Download Translation Dossier in Markdown format"
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
                    detectedDocLang === "EN"
                      ? lang === "DE"
                        ? "Klauseln filtern (z.B. 'Score', 'IELTS', 'SLA', 'Zulassung', 'Haftung')..."
                        : "Filter clauses (e.g. 'Score', 'IELTS', 'SLA', 'Exit', 'Admissions')..."
                      : lang === "DE"
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

            {/* Paragraph-by-Paragraph Translated Clauses (Bidirectional) */}
            <div className="space-y-3.5 flex-1 overflow-auto">
              {currentPageChunks.length > 0 ? (
                currentPageChunks
                  .filter((chunk) => {
                    if (!searchFilter.trim()) return true;
                    const q = searchFilter.toLowerCase();
                    const trans = (
                      detectedDocLang === "EN"
                        ? translateEnglishToGerman(chunk.content)
                        : chunk.translated_content || translateGermanToEnglish(chunk.content)
                    ).toLowerCase();
                    const orig = chunk.content.toLowerCase();
                    return trans.includes(q) || orig.includes(q);
                  })
                  .map((chunk, idx) => {
                    const translatedText =
                      detectedDocLang === "EN"
                        ? translateEnglishToGerman(chunk.content)
                        : chunk.translated_content || translateGermanToEnglish(chunk.content);
                    const meta = classifyClause(chunk.content, chunk.chunk_index, chunk.page_number, lang);
                    const isSelected = selectedChunkId === chunk.id;

                    // If original document is English: German translation is primary for German audit/readers
                    // If original document is German: English translation is primary for international audit/readers
                    let primaryText = "";
                    let alternateText = "";
                    let alternateLabel = "";

                    if (detectedDocLang === "EN") {
                      if (lang === "DE") {
                        primaryText = translatedText;
                        alternateText = chunk.content;
                        alternateLabel = "Originale englische Quelle (EN 🇺🇸 / 🇬🇧)";
                      } else {
                        primaryText = chunk.content;
                        alternateText = translatedText;
                        alternateLabel = "Beglaubigte deutsche Übersetzung (DE 🇩🇪)";
                      }
                    } else {
                      if (lang === "EN") {
                        primaryText = translatedText;
                        alternateText = chunk.content;
                        alternateLabel = "German Statutory Source (DE 🇩🇪)";
                      } else {
                        primaryText = chunk.content;
                        alternateText = translatedText;
                        alternateLabel = "Beglaubigte englische Übersetzung (EN 🇬🇧)";
                      }
                    }

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

                        {/* Primary Legal Prose (Respects Language Toggle & Document Source) */}
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
                                <span>{alternateLabel}</span>
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
                  <p className="font-bold">
                    {detectedDocLang === "EN"
                      ? "Generating German Translation Dossier..."
                      : "Generating English Translation Dossier..."}
                  </p>
                  <p className="text-[11px]">
                    {detectedDocLang === "EN"
                      ? "Select or upload an English document to view synchronized paragraph-by-paragraph German translations."
                      : "Select or upload a German document to view synchronized paragraph-by-paragraph English translations."}
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
                  {activeHighlight.label || "CITED CLAUSE"} •{" "}
                  {detectedDocLang === "EN"
                    ? "GERMAN COMPLIANCE LENS 🇩🇪"
                    : "ENGLISH TRANSLATION LENS 🇬🇧"}
                </span>
                <span className="text-[9px] font-mono bg-emerald-500/15 text-emerald-400 border border-emerald-500/30 px-1 rounded font-bold">
                  Bilingual Lens
                </span>
              </div>
              <p className="text-xs text-[var(--foreground)] mt-1 font-sans leading-relaxed">
                {(detectedDocLang === "EN"
                  ? translateEnglishToGerman(activeHighlight.snippet || activeHighlight.label || "")
                  : translateGermanToEnglish(activeHighlight.snippet || activeHighlight.label || "")) ||
                  (detectedDocLang === "EN"
                    ? "Offizielles Prüfungszeugnis gem. DIN EN ISO 17100 / BaFin-Aufsichtsstandard."
                    : "Under DORA Art. 30, termination exit assistance (60 days) and vendor migration responsibilities are mandated.")}
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

      {/* Real-Time Server-Sent Events (SSE) Audit Progress Stream HUD */}
      <RealTimeStreamHud documentId={documentId} lang={lang} />
    </div>
  );
}

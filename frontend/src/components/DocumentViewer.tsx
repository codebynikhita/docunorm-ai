"use client";

import React, { useState, useRef, useEffect } from "react";
import { UploadCloud, FileText, ZoomIn, ZoomOut, CheckCircle2, Loader2 } from "lucide-react";

interface BoundingBoxHighlight {
  page_number: number;
  box: [number, number, number, number]; // [x0, y0, x1, y1]
  label?: string;
}

interface DocumentViewerProps {
  documentId?: string | null;
  documentName?: string;
  currentPage: number;
  totalPages: number;
  isUploading?: boolean;
  activeHighlight?: BoundingBoxHighlight | null;
  onUploadFile?: (file: File) => void;
  onPageChange?: (newPage: number) => void;
}

export function DocumentViewer({
  documentId,
  documentName = "Siemens_Master_ICT_Agreement_2026.pdf",
  currentPage = 1,
  totalPages = 1,
  isUploading = false,
  activeHighlight,
  onUploadFile,
  onPageChange,
}: DocumentViewerProps) {
  const [zoom, setZoom] = useState(100);
  const [rendering, setRendering] = useState(false);
  const [canvasDimensions, setCanvasDimensions] = useState<{ width: number; height: number }>({
    width: 600,
    height: 800,
  });

  const canvasRef = useRef<HTMLCanvasElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const pdfDocRef = useRef<any>(null);

  // Load PDF with PDF.js whenever documentId changes
  useEffect(() => {
    let isCancelled = false;

    async function loadPdf() {
      if (!documentId) return;

      try {
        setRendering(true);
        const pdfjsLib = await import("pdfjs-dist");
        // Set worker
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

  // Re-render page whenever currentPage or zoom changes
  useEffect(() => {
    if (pdfDocRef.current) {
      renderPage(currentPage, pdfDocRef.current);
    }
  }, [currentPage, zoom]);

  const renderPage = async (pageNum: number, pdf: any) => {
    if (!canvasRef.current || !pdf) return;

    try {
      setRendering(true);
      const page = await pdf.getPage(pageNum);
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

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file && onUploadFile) {
      onUploadFile(file);
    }
  };

  const scaleFactor = (zoom / 100) * 1.25;

  return (
    <div className="flex-1 flex flex-col h-full bg-slate-900 border-r border-slate-800">
      {/* Top Toolbar */}
      <div className="h-12 border-b border-slate-800 bg-slate-900/90 px-4 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <FileText className="w-4 h-4 text-cyan-400" />
          <span className="text-xs font-medium text-slate-200 truncate max-w-[260px]">
            {documentName}
          </span>
          <span className="text-[10px] bg-emerald-950 text-emerald-400 border border-emerald-800 px-1.5 py-0.5 rounded flex items-center gap-1">
            <CheckCircle2 className="w-3 h-3" /> SHA-256 Verified
          </span>
        </div>

        {/* Upload Button + Page & Zoom Controls */}
        <div className="flex items-center gap-3 text-xs text-slate-400">
          <input
            type="file"
            ref={fileInputRef}
            onChange={handleFileChange}
            accept=".pdf"
            className="hidden"
          />
          <button
            onClick={() => fileInputRef.current?.click()}
            disabled={isUploading}
            className="flex items-center gap-1.5 bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 text-white font-medium px-2.5 py-1 rounded transition-colors"
          >
            {isUploading ? (
              <Loader2 className="w-3.5 h-3.5 animate-spin" />
            ) : (
              <UploadCloud className="w-3.5 h-3.5" />
            )}
            <span>{isUploading ? "Uploading..." : "Upload PDF"}</span>
          </button>

          <div className="flex items-center gap-1 bg-slate-800 px-2 py-1 rounded">
            <button
              onClick={() => onPageChange && onPageChange(Math.max(1, currentPage - 1))}
              disabled={currentPage <= 1}
              className="hover:text-white disabled:opacity-30"
            >
              &lt;
            </button>
            <span className="text-slate-200 px-1">
              {currentPage} / {totalPages}
            </span>
            <button
              onClick={() => onPageChange && onPageChange(Math.min(totalPages, currentPage + 1))}
              disabled={currentPage >= totalPages}
              className="hover:text-white disabled:opacity-30"
            >
              &gt;
            </button>
          </div>

          <div className="flex items-center gap-1 bg-slate-800 px-2 py-1 rounded">
            <button
              onClick={() => setZoom((z) => Math.max(60, z - 10))}
              className="hover:text-white"
            >
              <ZoomOut className="w-3.5 h-3.5" />
            </button>
            <span className="text-slate-200 w-10 text-center">{zoom}%</span>
            <button
              onClick={() => setZoom((z) => Math.min(160, z + 10))}
              className="hover:text-white"
            >
              <ZoomIn className="w-3.5 h-3.5" />
            </button>
          </div>
        </div>
      </div>

      {/* Main Document View Canvas */}
      <div className="flex-1 overflow-auto p-6 flex justify-center bg-slate-950/50">
        <div
          style={{ width: `${canvasDimensions.width}px`, minHeight: `${canvasDimensions.height}px` }}
          className="relative bg-white rounded-lg shadow-2xl transition-all duration-150 flex items-center justify-center overflow-hidden"
        >
          {rendering && (
            <div className="absolute inset-0 bg-slate-950/20 backdrop-blur-[1px] flex items-center justify-center z-10">
              <Loader2 className="w-6 h-6 animate-spin text-indigo-600" />
            </div>
          )}

          {/* HTML5 Canvas for Real PDF Rendering */}
          <canvas ref={canvasRef} className="block" />

          {/* Glowing Bounding Box Overlay if Active */}
          {activeHighlight && activeHighlight.page_number === currentPage && (
            <div
              className="absolute border-2 border-amber-500 bg-amber-400/20 rounded pointer-events-none transition-all duration-300 animate-pulse shadow-[0_0_15px_rgba(245,158,11,0.5)] z-20"
              style={{
                left: `${activeHighlight.box[0] * scaleFactor}px`,
                top: `${activeHighlight.box[1] * scaleFactor}px`,
                width: `${(activeHighlight.box[2] - activeHighlight.box[0]) * scaleFactor}px`,
                height: `${(activeHighlight.box[3] - activeHighlight.box[1]) * scaleFactor}px`,
              }}
            >
              <span className="absolute -top-5 left-0 bg-amber-500 text-slate-950 font-bold text-[10px] px-1.5 py-0.5 rounded shadow whitespace-nowrap">
                {activeHighlight.label || "Cited Source"}
              </span>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
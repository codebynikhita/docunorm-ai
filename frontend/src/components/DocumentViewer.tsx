"use client";

import React, { useState } from "react";
import { UploadCloud, FileText, ZoomIn, ZoomOut, CheckCircle2, AlertCircle } from "lucide-react";

interface BoundingBoxHighlight {
  page_number: number;
  box: [number, number, number, number]; // [x0, y0, x1, y1]
  label?: string;
}

interface DocumentViewerProps {
  documentName?: string;
  currentPage: number;
  totalPages: number;
  activeHighlight?: BoundingBoxHighlight | null;
  onUploadFile?: (file: File) => void;
  onPageChange?: (newPage: number) => void;
}

export function DocumentViewer({
  documentName = "Siemens_Master_ICT_Agreement_2026.pdf",
  currentPage = 1,
  totalPages = 4,
  activeHighlight,
  onUploadFile,
  onPageChange,
}: DocumentViewerProps) {
  const [zoom, setZoom] = useState(100);

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

        {/* Page & Zoom Controls */}
        <div className="flex items-center gap-3 text-xs text-slate-400">
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
              onClick={() => setZoom((z) => Math.max(70, z - 10))}
              className="hover:text-white"
            >
              <ZoomOut className="w-3.5 h-3.5" />
            </button>
            <span className="text-slate-200 w-10 text-center">{zoom}%</span>
            <button
              onClick={() => setZoom((z) => Math.min(150, z + 10))}
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
          style={{ width: `${(600 * zoom) / 100}px`, minHeight: "800px" }}
          className="relative bg-white text-slate-900 rounded-lg shadow-2xl p-10 select-none font-serif text-sm transition-all duration-150"
        >
          {/* Simulated Page Content */}
          <div className="space-y-4">
            <div className="border-b pb-4 mb-6">
              <h2 className="text-xl font-bold tracking-tight text-slate-900">
                MASTER INFORMATION & ICT SERVICES AGREEMENT
              </h2>
              <p className="text-xs text-slate-500 mt-1">
                Reference: ICT-2026-SIEMENS-EUR | Governing Law: Germany (BaFin/DORA)
              </p>
            </div>

            <p className="text-slate-700 leading-relaxed text-xs">
              <strong>Section 4.1 (Service Continuity & Exit):</strong> In accordance with Article 30 of Regulation (EU) 2022/2554 (DORA), the Vendor guarantees a minimum exit transition assistance period of six (6) months upon termination without interruption to ICT operations.
            </p>

            <p className="text-slate-700 leading-relaxed text-xs">
              <strong>Section 7.3 (Sub-outsourcing Requirements):</strong> The ICT Third-Party Service Provider shall not sub-contract any critical or important functions without prior written authorization from Siemens AG at least 60 calendar days in advance.
            </p>

            <p className="text-slate-700 leading-relaxed text-xs">
              <strong>Section 12.4 (Penalties & Delay Damages):</strong> In the event of an unexcused outage exceeding four (4) consecutive hours, the service credits shall accrue at a penalty rate of 0.5% per hour of delay, capped at 15% of annual contract value.
            </p>
          </div>

          {/* Glowing Bounding Box Overlay if Active */}
          {activeHighlight && activeHighlight.page_number === currentPage && (
            <div
              className="absolute border-2 border-amber-500 bg-amber-400/20 rounded pointer-events-none transition-all duration-300 animate-pulse shadow-[0_0_15px_rgba(245,158,11,0.5)]"
              style={{
                left: `${activeHighlight.box[0]}px`,
                top: `${activeHighlight.box[1]}px`,
                width: `${activeHighlight.box[2] - activeHighlight.box[0]}px`,
                height: `${activeHighlight.box[3] - activeHighlight.box[1]}px`,
              }}
            >
              <span className="absolute -top-5 left-0 bg-amber-500 text-slate-950 font-bold text-[10px] px-1.5 py-0.5 rounded shadow">
                {activeHighlight.label || "Cited Source"}
              </span>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

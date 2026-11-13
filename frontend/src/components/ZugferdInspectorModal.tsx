"use client";

import React, { useEffect, useState } from "react";
import {
  FileSpreadsheet,
  FileText,
  Layers,
  X,
} from "lucide-react";
import { Language } from "@/lib/i18n";
import { ZugferdInvoiceViewer } from "@/components/ZugferdInvoiceViewer";
import { BatchInvoiceCockpit } from "@/components/BatchInvoiceCockpit";
import { BatchInvoiceProcessingItem } from "@/lib/api";

export interface ZugferdDocumentItem {
  id: string;
  filename: string;
  [key: string]: unknown;
}

interface ZugferdInspectorModalProps {
  isOpen: boolean;
  onClose: () => void;
  lang: Language;
  documentId?: string;
  documentName?: string;
  availableDocuments?: ZugferdDocumentItem[];
  onSelectDocument?: (doc: ZugferdDocumentItem | null) => void;
  initialMode?: "single" | "batch";
}

export function ZugferdInspectorModal({
  isOpen,
  onClose,
  lang,
  documentId,
  documentName = "",
  availableDocuments = [],
  onSelectDocument,
  initialMode = "single",
}: ZugferdInspectorModalProps) {
  const [viewMode, setViewMode] = useState<"single" | "batch">(initialMode);

  useEffect(() => {
    if (isOpen && initialMode) {
      setViewMode(initialMode);
    }
  }, [isOpen, initialMode]);

  if (!isOpen) return null;

  const isDe = lang === "DE";

  const handleSelectBatchItem = (invoice: BatchInvoiceProcessingItem) => {
    if (invoice.document_id && onSelectDocument) {
      const match = availableDocuments.find((d) => d.id === invoice.document_id);
      if (match) {
        onSelectDocument(match);
      }
    }
    setViewMode("single");
  };

  return (
    <div className="fixed inset-0 z-50 bg-black/80 backdrop-blur-md flex items-center justify-center p-3">
      <div className="w-full max-w-[96vw] bg-slate-950 border border-slate-800 rounded-2xl shadow-2xl overflow-hidden flex flex-col h-[94vh] animate-in zoom-in-95 duration-200">
        {/* Navigation & Mode Switcher Header Bar */}
        <div className="px-5 py-2.5 border-b border-slate-800 bg-slate-900/90 flex flex-wrap items-center justify-between gap-3 text-xs">
          {/* Left: Mode Switching Tabs */}
          <div className="flex items-center space-x-2">
            <div className="flex items-center bg-slate-950 border border-slate-800 rounded-lg p-0.5">
              <button
                onClick={() => setViewMode("single")}
                className={`px-3 py-1.5 rounded-md flex items-center space-x-1.5 font-medium transition-colors ${
                  viewMode === "single"
                    ? "bg-emerald-600 text-white shadow-sm"
                    : "text-slate-400 hover:text-slate-200"
                }`}
              >
                <FileSpreadsheet className="w-3.5 h-3.5" />
                <span>{isDe ? "Einzelbeleg-Prüfung (EN 16931)" : "Single Invoice Audit"}</span>
              </button>

              <button
                onClick={() => setViewMode("batch")}
                className={`px-3 py-1.5 rounded-md flex items-center space-x-1.5 font-medium transition-colors ${
                  viewMode === "batch"
                    ? "bg-cyan-600 text-white shadow-sm"
                    : "text-slate-400 hover:text-slate-200"
                }`}
              >
                <Layers className="w-3.5 h-3.5" />
                <span>{isDe ? "Stapelverarbeitung & DATEV / SAP" : "Batch & DATEV/SAP"}</span>
              </button>
            </div>
          </div>

          {/* Center: Document Selector (shown in Single mode) */}
          {viewMode === "single" && availableDocuments && availableDocuments.length > 0 && (
            <div className="flex items-center space-x-2">
              <FileText className="w-4 h-4 text-emerald-400" />
              <span className="text-slate-400 font-medium">
                {isDe ? "Dokument wählen:" : "Select Document:"}
              </span>
              <select
                value={documentId || ""}
                onChange={(e) => {
                  if (e.target.value === "") {
                    if (onSelectDocument) onSelectDocument(null);
                  } else {
                    const doc = availableDocuments.find((d) => d.id === e.target.value);
                    if (doc && onSelectDocument) onSelectDocument(doc);
                  }
                }}
                className="bg-slate-950 border border-slate-700 text-slate-200 text-xs rounded-lg px-2.5 py-1 font-mono max-w-[260px] truncate cursor-pointer focus:outline-none focus:border-emerald-500"
              >
                <option value="">{isDe ? "— Authentisches Standard-Muster (ZUGFeRD 2.3) —" : "— Authentic Sample (ZUGFeRD 2.3) —"}</option>
                {availableDocuments.map((doc) => (
                  <option key={doc.id} value={doc.id}>
                    {doc.filename}
                  </option>
                ))}
              </select>
            </div>
          )}

          {/* Right: Close Action */}
          <button
            onClick={onClose}
            className="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition-colors ml-auto"
            title="Schließen"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Dynamic Body Content */}
        <div className="flex-1 overflow-hidden">
          {viewMode === "single" ? (
            <ZugferdInvoiceViewer
              documentId={documentId || "default-sample"}
              filename={documentName || "SAMPLE_ZUGFERD_FACTURX_EN16931.pdf"}
              onClose={onClose}
              onOpenBatch={() => setViewMode("batch")}
            />
          ) : (
            <BatchInvoiceCockpit
              onClose={onClose}
              onSelectInvoice={handleSelectBatchItem}
            />
          )}
        </div>
      </div>
    </div>
  );
}

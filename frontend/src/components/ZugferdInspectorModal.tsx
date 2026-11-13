"use client";

import React from "react";
import {
  FileSpreadsheet,
  FileText,
  X,
} from "lucide-react";
import { Language } from "@/lib/i18n";
import { ZugferdInvoiceViewer } from "@/components/ZugferdInvoiceViewer";

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
}

export function ZugferdInspectorModal({
  isOpen,
  onClose,
  lang,
  documentId,
  documentName = "",
  availableDocuments = [],
  onSelectDocument,
}: ZugferdInspectorModalProps) {
  if (!isOpen) return null;

  const isDe = lang === "DE";

  return (
    <div className="fixed inset-0 z-50 bg-black/80 backdrop-blur-md flex items-center justify-center p-3">
      <div className="w-full max-w-[96vw] bg-slate-950 border border-slate-800 rounded-2xl shadow-2xl overflow-hidden flex flex-col h-[94vh] animate-in zoom-in-95 duration-200">
        {/* Document Selector Header Bar */}
        {availableDocuments && availableDocuments.length > 0 && (
          <div className="px-6 py-2.5 border-b border-slate-800 bg-slate-900/90 flex items-center justify-between text-xs">
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

            <button
              onClick={onClose}
              className="p-1 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition-colors"
            >
              <X className="w-4 h-4" />
            </button>
          </div>
        )}

        {/* Live ZUGFeRD 2.3 & Factur-X / EN 16931 Viewer */}
        <div className="flex-1 overflow-hidden">
          <ZugferdInvoiceViewer
            documentId={documentId || "default-sample"}
            filename={documentName || "SAMPLE_ZUGFERD_FACTURX_EN16931.pdf"}
            onClose={onClose}
          />
        </div>
      </div>
    </div>
  );
}

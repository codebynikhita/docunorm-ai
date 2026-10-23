"use client";

import React, { useState, useEffect } from "react";
import { Header } from "@/components/Header";
import { DocumentViewer } from "@/components/DocumentViewer";
import { AuditPanel, CitationItem } from "@/components/AuditorPanel";
import { uploadDocument, listDocuments } from "@/lib/api";

export default function Home() {
  const [documentId, setDocumentId] = useState<string | null>(null);
  const [documentName, setDocumentName] = useState("Siemens_Master_ICT_Agreement_2026.pdf");
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(4);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadError, setUploadError] = useState<string | null>(null);
  const [activeHighlight, setActiveHighlight] = useState<{
    page_number: number;
    box: [number, number, number, number];
    label?: string;
  } | null>(null);

  // Auto-load most recently uploaded document from database
  useEffect(() => {
    async function initLatestDocument() {
      const docs = await listDocuments();
      if (docs && docs.length > 0) {
        const latest = docs[0];
        setDocumentId(latest.id);
        setDocumentName(latest.filename);
        setTotalPages(latest.total_pages || 1);
      }
    }
    initLatestDocument();
  }, []);

  const handleSelectCitation = (citation: CitationItem) => {
    setCurrentPage(citation.page_number);
    setActiveHighlight({
      page_number: citation.page_number,
      box: citation.box,
      label: `${citation.source_tag} Cited`,
    });
  };

  const handleUploadFile = async (file: File) => {
    setIsUploading(true);
    setUploadError(null);
    try {
      const res = await uploadDocument(file);
      console.log("Uploaded successfully, document ID:", res.document.id);
      setDocumentId(res.document.id);
      setDocumentName(res.document.filename);
      setTotalPages(res.document.total_pages || 1);
      setCurrentPage(1);
      setActiveHighlight(null);
    } catch (err: any) {
      setUploadError(err.message || "Failed to upload document");
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <div className="flex flex-col h-screen overflow-hidden bg-slate-950">
      {/* 1. Top Enterprise Header */}
      <Header />

      {/* Upload Error Banner if present */}
      {uploadError && (
        <div className="bg-rose-900/80 border-b border-rose-700 px-6 py-2 text-xs text-rose-200 flex items-center justify-between">
          <span>Error: {uploadError}</span>
          <button
            onClick={() => setUploadError(null)}
            className="text-rose-400 hover:text-white font-bold"
          >
            ✕
          </button>
        </div>
      )}

      {/* 2. Dual-Pane Workbench Layout */}
      <main className="flex-1 flex overflow-hidden">
        {/* Left Pane: Document Viewer with Bounding Box Highlights */}
        <DocumentViewer
          documentId={documentId}
          documentName={documentName}
          currentPage={currentPage}
          totalPages={totalPages}
          isUploading={isUploading}
          activeHighlight={activeHighlight}
          onUploadFile={handleUploadFile}
          onPageChange={(page) => setCurrentPage(page)}
        />

        {/* Right Pane: Regulatory Auditor Assistant */}
        <AuditPanel documentId={documentId} onSelectCitation={handleSelectCitation} />
      </main>
    </div>
  );
}
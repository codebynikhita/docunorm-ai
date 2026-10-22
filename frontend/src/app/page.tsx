"use client";

import React, { useState } from "react";
import { Header } from "@/components/Header";
import { DocumentViewer } from "@/components/DocumentViewer";
import { AuditPanel, CitationItem } from "@/components/AuditorPanel";

export default function Home() {
  const [currentPage, setCurrentPage] = useState(1);
  const [activeHighlight, setActiveHighlight] = useState<{
    page_number: number;
    box: [number, number, number, number];
    label?: string;
  } | null>(null);

  const handleSelectCitation = (citation: CitationItem) => {
    setCurrentPage(citation.page_number);
    setActiveHighlight({
      page_number: citation.page_number,
      box: citation.box,
      label: `${citation.source_tag} Cited`,
    });
  };

  return (
    <div className="flex flex-col h-screen overflow-hidden bg-slate-950">
      {/* 1. Top Enterprise Header */}
      <Header />

      {/* 2. Dual-Pane Workbench Layout */}
      <main className="flex-1 flex overflow-hidden">
        {/* Left Pane: Document Viewer with Bounding Box Highlights */}
        <DocumentViewer
          documentName="Siemens_Master_ICT_Agreement_2026.pdf"
          currentPage={currentPage}
          totalPages={4}
          activeHighlight={activeHighlight}
          onPageChange={(page) => setCurrentPage(page)}
        />

        {/* Right Pane: Regulatory Auditor Assistant */}
        <AuditPanel onSelectCitation={handleSelectCitation} />
      </main>
    </div>
  );
}
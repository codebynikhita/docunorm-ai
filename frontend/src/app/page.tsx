"use client";

import React, { useState, useEffect } from "react";
import { Header, Theme, LayoutMode } from "@/components/Header";
import { Sidebar } from "@/components/Sidebar";
import { DocumentViewer } from "@/components/DocumentViewer";
import { AuditPanel, CitationItem } from "@/components/AuditorPanel";
import { ExecutiveDashboard } from "@/components/ExecutiveDashboard";
import { IngestionModal } from "@/components/IngestionModal";
import { AuditCertificateModal } from "@/components/AuditCertificateModal";
import { ZugferdInspectorModal } from "@/components/ZugferdInspectorModal";
import { Language } from "@/lib/i18n";
import { uploadDocument, listDocuments } from "@/lib/api";
import { Bot, Award } from "lucide-react";

export default function Home() {
  const [lang, setLang] = useState<Language>("DE");
  const [theme, setTheme] = useState<Theme>("bauhaus");
  const [layoutMode, setLayoutMode] = useState<LayoutMode>("workbench");

  const [activeTab, setActiveTab] = useState<
    "documents" | "dora" | "lksg" | "zugferd" | "audit_log"
  >("documents");
  const [documentId, setDocumentId] = useState<string | null>(null);
  const [documentName, setDocumentName] = useState<string>("");
  const [availableDocuments, setAvailableDocuments] = useState<any[]>([]);
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadError, setUploadError] = useState<string | null>(null);
  const [isIngestModalOpen, setIsIngestModalOpen] = useState(false);
  const [isCertificateOpen, setIsCertificateOpen] = useState(false);
  const [isZugferdModalOpen, setIsZugferdModalOpen] = useState(false);
  const [pendingFile, setPendingFile] = useState<File | null>(null);
  const [isFloatingAuditorOpen, setIsFloatingAuditorOpen] = useState(true);
  const [isAuditorOpen, setIsAuditorOpen] = useState(true);
  const [activeHighlight, setActiveHighlight] = useState<{
    page_number: number;
    box: [number, number, number, number];
    label?: string;
    snippet?: string;
  } | null>(null);

  // Load available documents list for dropdown and select German demo contract
  useEffect(() => {
    async function initDocumentList() {
      const docs = await listDocuments();
      if (docs && docs.length > 0) {
        setAvailableDocuments(docs);
        const demoDoc =
          docs.find((d) => d.filename.includes("Siemens_Master_IKT_Vertrag_2026")) || docs[0];
        if (demoDoc) {
          setDocumentId(demoDoc.id);
          setDocumentName(demoDoc.filename);
          setTotalPages(demoDoc.total_pages || 3);
        }
      }
    }
    initDocumentList();
  }, []);

  const handleSelectDocument = (doc: any) => {
    setDocumentId(doc.id);
    setDocumentName(doc.filename);
    setTotalPages(doc.total_pages || 1);
    setCurrentPage(1);
    setActiveHighlight(null);
  };

  const handleSelectCitation = (citation: CitationItem) => {
    setCurrentPage(citation.page_number);
    setActiveHighlight({
      page_number: citation.page_number,
      box: citation.box,
      label: `${citation.source_tag} Cited`,
      snippet: citation.snippet,
    });
  };

  const handleUploadFile = async (file: File) => {
    setPendingFile(file);
    setIsIngestModalOpen(true);
    setIsUploading(true);
    setUploadError(null);
    try {
      const res = await uploadDocument(file);
      setDocumentId(res.document.id);
      setDocumentName(res.document.filename);
      setTotalPages(res.document.total_pages || 1);
      setCurrentPage(1);
      setActiveHighlight(null);

      // Refresh list
      const updatedDocs = await listDocuments();
      setAvailableDocuments(updatedDocs);
    } catch (err: any) {
      setUploadError(err.message || "Failed to upload document");
      setIsIngestModalOpen(false);
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <div
      data-theme={theme}
      className="flex flex-col h-screen overflow-hidden bg-[var(--background)] text-[var(--foreground)] font-sans transition-colors duration-200"
    >
      {/* Top Enterprise Header with Theme & Layout Switchers */}
      <Header
        lang={lang}
        onToggleLang={(l) => setLang(l)}
        theme={theme}
        onThemeChange={(th) => setTheme(th)}
        layoutMode={layoutMode}
        onLayoutChange={(lm) => setLayoutMode(lm)}
        onOpenCertificate={() => setIsCertificateOpen(true)}
        onOpenZugferd={() => setIsZugferdModalOpen(true)}
      />

      {/* Upload Error Banner if present */}
      {uploadError && (
        <div className="bg-rose-500/15 border-b border-rose-500/30 px-6 py-2 text-xs text-rose-500 flex items-center justify-between z-50 font-mono">
          <span>Error: {uploadError}</span>
          <button
            onClick={() => setUploadError(null)}
            className="hover:opacity-100 font-bold cursor-pointer"
          >
            ✕
          </button>
        </div>
      )}

      {/* Body Area with Sidebar + Dynamic Layout Template */}
      <div className="flex-1 flex overflow-hidden">
        {/* Zone 1: Mini Compliance Navigation Sidebar */}
        <Sidebar
          lang={lang}
          activeTab={activeTab}
          onTabChange={(tab) => {
            setActiveTab(tab);
            if (tab === "dora" || tab === "lksg") {
              setLayoutMode("executive");
            } else if (tab === "zugferd") {
              setIsZugferdModalOpen(true);
            } else if (tab === "audit_log") {
              setIsCertificateOpen(true);
            }
          }}
          documentCount={availableDocuments.length}
        />

        {/* Dynamic Layout Template Switcher */}
        {layoutMode === "executive" ? (
          /* Template 2: Executive Compliance Cockpit */
          <main className="flex-1 flex overflow-hidden bg-[var(--background)]">
            <ExecutiveDashboard
              lang={lang}
              documentName={documentName}
              onAuditQuery={() => {}}
              onSwitchToWorkbench={() => setLayoutMode("workbench")}
            />
          </main>
        ) : layoutMode === "focus" ? (
          /* Template 3: Full-Screen Document Focus Canvas with Floating Auditor */
          <main className="flex-1 flex relative overflow-hidden bg-[var(--background)]">
            <DocumentViewer
              lang={lang}
              documentId={documentId}
              documentName={documentName}
              availableDocuments={availableDocuments}
              onSelectDocument={handleSelectDocument}
              currentPage={currentPage}
              totalPages={totalPages}
              isUploading={isUploading}
              activeHighlight={activeHighlight}
              onUploadFile={handleUploadFile}
              onPageChange={(page) => setCurrentPage(page)}
            />

            {/* Floating Glass Auditor HUD */}
            <div className="absolute top-4 right-4 z-40">
              {isFloatingAuditorOpen ? (
                <div className="relative">
                  <button
                    onClick={() => setIsFloatingAuditorOpen(false)}
                    className="absolute -top-3 -right-3 z-50 w-7 h-7 rounded-full bg-[var(--accent-tangerine)] text-[var(--accent-contrast)] font-black flex items-center justify-center text-xs shadow-lg cursor-pointer"
                  >
                    ✕
                  </button>
                  <AuditPanel
                    lang={lang}
                    documentId={documentId}
                    onSelectCitation={handleSelectCitation}
                    floating={true}
                  />
                </div>
              ) : (
                <button
                  onClick={() => setIsFloatingAuditorOpen(true)}
                  className="flex items-center gap-2 px-4 py-2.5 rounded-full bg-[var(--accent-tangerine)] text-[var(--accent-contrast)] font-mono font-bold text-xs shadow-2xl hover:opacity-90 transition-all cursor-pointer"
                >
                  <Bot className="w-4 h-4 stroke-[2.5]" />
                  <span>Auditor HUD</span>
                </button>
              )}
            </div>
          </main>
        ) : (
          /* Template 1: Classic Split Dual-Workbench */
          <main className="flex-1 flex overflow-hidden bg-[var(--background)]">
            <DocumentViewer
              lang={lang}
              documentId={documentId}
              documentName={documentName}
              availableDocuments={availableDocuments}
              onSelectDocument={handleSelectDocument}
              currentPage={currentPage}
              totalPages={totalPages}
              isUploading={isUploading}
              activeHighlight={activeHighlight}
              onUploadFile={handleUploadFile}
              onPageChange={(page) => setCurrentPage(page)}
            />

            {isAuditorOpen ? (
              <AuditPanel
                lang={lang}
                documentId={documentId}
                onSelectCitation={handleSelectCitation}
                onClose={() => setIsAuditorOpen(false)}
              />
            ) : (
              <div className="w-10 shrink-0 bg-[var(--surface-dark)] border-l border-[var(--surface-border)] flex flex-col items-center py-4 select-none">
                <button
                  onClick={() => setIsAuditorOpen(true)}
                  title="Open Auditor Panel"
                  className="flex flex-col items-center gap-3 text-[var(--foreground)] opacity-60 hover:opacity-100 hover:text-[var(--accent-tangerine)] transition-all cursor-pointer p-1"
                >
                  <Bot className="w-4 h-4 text-[var(--accent-tangerine)]" />
                  <span className="font-mono text-[9px] font-bold uppercase tracking-widest [writing-mode:vertical-rl] rotate-180">
                    Revisionsprüfer
                  </span>
                </button>
              </div>
            )}
          </main>
        )}
      </div>

      {/* Advanced Regulatory Ingestion Telemetry Modal */}
      <IngestionModal
        isOpen={isIngestModalOpen}
        filename={pendingFile?.name || "document.pdf"}
        fileSizeBytes={pendingFile?.size || 0}
        onComplete={() => setIsIngestModalOpen(false)}
      />

      {/* Official BaFin / DIN 66399 Regulatory Certificate Modal */}
      <AuditCertificateModal
        isOpen={isCertificateOpen}
        onClose={() => setIsCertificateOpen(false)}
        lang={lang}
        documentName={documentName || "Siemens_Master_ICT_Agreement_2026.pdf"}
      />

      {/* ZUGFeRD 2.3 XML vs Visual PDF Discrepancy Inspector Modal */}
      <ZugferdInspectorModal
        isOpen={isZugferdModalOpen}
        onClose={() => setIsZugferdModalOpen(false)}
        lang={lang}
        documentName={documentName || "Siemens_Master_ICT_Agreement_2026.pdf"}
      />
    </div>
  );
}

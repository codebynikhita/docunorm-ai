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
import { DoraExitInspectorModal } from "@/components/DoraExitInspectorModal";
import { DoraSubcontractorModal } from "@/components/DoraSubcontractorModal";
import { AuditRightsModal } from "@/components/AuditRightsModal";
import { CommandPalette } from "@/components/CommandPalette";
import { AuthModal } from "@/components/AuthModal";
import { LandingPage } from "@/components/LandingPage";
import { LoginPage } from "@/components/LoginPage";
import { StandaloneAuditorStudio } from "@/components/StandaloneAuditorStudio";
import { RemediationModal } from "@/components/RemediationModal";
import { Language } from "@/lib/i18n";
import { uploadDocument, listDocuments, UserProfile } from "@/lib/api";
import { Bot, Award } from "lucide-react";

export default function Home() {
  const [lang, setLang] = useState<Language>("DE");
  const [theme, setTheme] = useState<Theme>("bauhaus");
  const [layoutMode, setLayoutMode] = useState<LayoutMode>("portal");

  // User Authentication State
  const [user, setUser] = useState<UserProfile | null>(null);
  const [isAuthModalOpen, setIsAuthModalOpen] = useState(false);

  const [activeTab, setActiveTab] = useState<
    "documents" | "dora" | "lksg" | "zugferd" | "audit_log" | "auditor" | "audit_rights"
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
  const [isDoraExitModalOpen, setIsDoraExitModalOpen] = useState(false);
  const [isDoraSubcontractorModalOpen, setIsDoraSubcontractorModalOpen] = useState(false);
  const [isAuditRightsModalOpen, setIsAuditRightsModalOpen] = useState(false);
  const [isRemediationModalOpen, setIsRemediationModalOpen] = useState(false);
  const [isCommandPaletteOpen, setIsCommandPaletteOpen] = useState(false);
  const [pendingFile, setPendingFile] = useState<File | null>(null);
  const [isFloatingAuditorOpen, setIsFloatingAuditorOpen] = useState(true);
  const [isAuditorOpen, setIsAuditorOpen] = useState(true);
  const [isSidebarCollapsed, setIsSidebarCollapsed] = useState(false);
  const [activeHighlight, setActiveHighlight] = useState<{
    page_number: number;
    box: [number, number, number, number];
    label?: string;
    snippet?: string;
  } | null>(null);

  // Restore User Session & Language Preference from localStorage on mount
  useEffect(() => {
    const savedLang = localStorage.getItem("docunorm_lang") as Language;
    if (savedLang === "DE" || savedLang === "EN") {
      setLang(savedLang);
    }

    const savedSidebar = localStorage.getItem("docunorm_sidebar_collapsed");
    if (savedSidebar === "true") {
      setIsSidebarCollapsed(true);
    }

    const savedUser = localStorage.getItem("docunorm_user");
    const savedToken = localStorage.getItem("docunorm_token");
    if (savedUser && savedToken) {
      try {
        const parsed = JSON.parse(savedUser);
        setUser(parsed);
        setLayoutMode("workbench");
      } catch {
        localStorage.removeItem("docunorm_user");
        localStorage.removeItem("docunorm_token");
        setUser(null);
        setLayoutMode("portal");
      }
    } else {
      setUser(null);
      setLayoutMode("portal");
    }
  }, []);

  const handleToggleLang = (newLang: Language) => {
    setLang(newLang);
    try {
      localStorage.setItem("docunorm_lang", newLang);
    } catch (e) {
      console.warn("Could not save language to localStorage", e);
    }
  };

  // Load available documents list and auto-select active or first document
  useEffect(() => {
    async function initDocumentList() {
      const docs = await listDocuments();
      if (docs && docs.length > 0) {
        setAvailableDocuments(docs);
        const savedDocId = localStorage.getItem("docunorm_active_document_id");
        const validSavedId = savedDocId && savedDocId !== "null" && savedDocId !== "undefined" ? savedDocId : null;
        const docToSelect = (validSavedId && docs.find((d: any) => d.id === validSavedId)) || docs[0];
        if (docToSelect) {
          setDocumentId(docToSelect.id);
          setDocumentName(docToSelect.filename);
          setTotalPages(docToSelect.total_pages || 1);
          setCurrentPage(1);
          localStorage.setItem("docunorm_active_document_id", docToSelect.id);
        }
      }
    }
    initDocumentList();
  }, []);

  // Silicon Valley Command Palette (⌘K / Ctrl+K) Global Listener
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === "k") {
        e.preventDefault();
        setIsCommandPaletteOpen((prev) => !prev);
      }
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, []);

  // Route Guard: Ensure unauthenticated users cannot access Workbench/Auditor without signing in
  useEffect(() => {
    if (!user && layoutMode !== "portal" && layoutMode !== "login") {
      setLayoutMode("portal");
    }
  }, [user, layoutMode]);

  const handleSelectDocument = (doc: any) => {
    if (!doc) {
      setDocumentId(null);
      setDocumentName("");
      setTotalPages(1);
      setCurrentPage(1);
      setActiveHighlight(null);
      localStorage.removeItem("docunorm_active_document_id");
      return;
    }
    setDocumentId(doc.id);
    setDocumentName(doc.filename);
    setTotalPages(doc.total_pages || 1);
    setCurrentPage(1);
    setActiveHighlight(null);
    localStorage.setItem("docunorm_active_document_id", doc.id);
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

  const handleAuthSuccess = (authUser: UserProfile, token: string) => {
    setUser(authUser);
    setIsAuthModalOpen(false);
    setLayoutMode("workbench");
  };

  const handleLogout = () => {
    localStorage.removeItem("docunorm_user");
    localStorage.removeItem("docunorm_token");
    setUser(null);
    setLayoutMode("portal");
  };

  const handleEnterAsDemo = (role: "siemens" | "bafin") => {
    const demoUser: UserProfile =
      role === "siemens"
        ? {
            id: "demo-weber",
            email: "dr.weber@siemens.de",
            full_name: "Dr. M. Weber",
            role: "auditor",
            tenant_id: "siemens-ag",
            organization: "Siemens AG",
          }
        : {
            id: "demo-bafin",
            email: "auditor@bafin.de",
            full_name: "BaFin Lead Auditor",
            role: "admin",
            tenant_id: "bafin-supervisory",
            organization: "Bundesanstalt für Finanzdienstleistungsaufsicht",
          };
    localStorage.setItem("docunorm_user", JSON.stringify(demoUser));
    localStorage.setItem("docunorm_token", "demo-token-" + Date.now());
    setUser(demoUser);
    setLayoutMode("workbench");
  };

  const handleToggleSidebar = () => {
    setIsSidebarCollapsed((prev) => {
      const next = !prev;
      localStorage.setItem("docunorm_sidebar_collapsed", String(next));
      return next;
    });
  };

  return (
    <div
      data-theme={theme}
      className="flex flex-col h-screen overflow-hidden bg-[var(--background)] text-[var(--foreground)] font-sans transition-colors duration-200"
    >
      {/* Top Enterprise Header with Theme & Layout Switchers */}
      <Header
        lang={lang}
        onToggleLang={handleToggleLang}
        theme={theme}
        onThemeChange={(th) => setTheme(th)}
        layoutMode={layoutMode}
        onLayoutChange={(lm) => setLayoutMode(lm)}
        onOpenCertificate={() => setIsCertificateOpen(true)}
        onOpenZugferd={() => setIsZugferdModalOpen(true)}
        user={user}
        onOpenAuth={() => setIsAuthModalOpen(true)}
        onLogout={handleLogout}
        isSidebarCollapsed={isSidebarCollapsed}
        onToggleSidebar={handleToggleSidebar}
        onOpenCommandPalette={() => setIsCommandPaletteOpen(true)}
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

      {/* 1. Public Landing Portal (Overview) */}
      {layoutMode === "portal" ? (
        <LandingPage
          lang={lang}
          user={user}
          onOpenAuth={() => setLayoutMode("login")}
          onEnterAsDemo={handleEnterAsDemo}
          onExploreWorkbench={() => {
            if (!user) {
              setLayoutMode("login");
            } else {
              setLayoutMode("workbench");
            }
          }}
        />
      ) : layoutMode === "login" ? (
        /* 2. Dedicated Institutional Sign In & Registration Page */
        <LoginPage
          lang={lang}
          onAuthSuccess={handleAuthSuccess}
          onBackToOverview={() => setLayoutMode("portal")}
        />
      ) : (
        /* Authenticated Application Shell with Sidebar + Main Viewport */
        <div className="flex-1 flex overflow-hidden">
          {/* Zone 1: Mini Compliance Navigation Sidebar */}
          <Sidebar
            lang={lang}
            activeTab={activeTab}
            isCollapsed={isSidebarCollapsed}
            onToggleCollapse={handleToggleSidebar}
            onTabChange={(tab) => {
              setActiveTab(tab);
              if (tab === "auditor") {
                setLayoutMode("auditor");
              } else if (tab === "dora") {
                setIsDoraExitModalOpen(true);
              } else if (tab === "audit_rights") {
                setIsAuditRightsModalOpen(true);
              } else if (tab === "lksg") {
                setIsDoraSubcontractorModalOpen(true);
              } else if (tab === "zugferd") {
                setIsZugferdModalOpen(true);
              } else if (tab === "audit_log") {
                setIsCertificateOpen(true);
              } else if (tab === "documents") {
                setLayoutMode("workbench");
              }
            }}
            documentCount={availableDocuments.length}
          />

          {/* Dynamic Viewport Switcher */}
          {layoutMode === "auditor" ? (
            /* DEDICATED STANDALONE AI COMPLIANCE AUDITOR STUDIO */
            <StandaloneAuditorStudio
              lang={lang}
              documentId={documentId}
              documentName={documentName}
              availableDocuments={availableDocuments}
              onSelectDocument={handleSelectDocument}
              onSwitchToWorkbench={() => setLayoutMode("workbench")}
              onOpenWorkbenchWithCitation={(page, bbox) => {
                setCurrentPage(page);
                setActiveHighlight({
                  page_number: page,
                  box: bbox,
                  label: "Cited Source",
                });
                setLayoutMode("workbench");
              }}
            />
          ) : layoutMode === "executive" ? (
            /* Template 2: Executive Compliance Cockpit */
            <main className="flex-1 flex overflow-hidden bg-[var(--background)]">
              <ExecutiveDashboard
                lang={lang}
                documentId={documentId}
                documentName={documentName}
                availableDocuments={availableDocuments}
                onSelectDocument={handleSelectDocument}
                onAuditQuery={() => setLayoutMode("auditor")}
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
                onOpenDoraExit={() => setIsDoraExitModalOpen(true)}
                onOpenDoraSubcontractor={() => setIsDoraSubcontractorModalOpen(true)}
                onOpenAuditRights={() => setIsAuditRightsModalOpen(true)}
                onOpenRemediation={() => setIsRemediationModalOpen(true)}
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
                onOpenDoraExit={() => setIsDoraExitModalOpen(true)}
                onOpenDoraSubcontractor={() => setIsDoraSubcontractorModalOpen(true)}
                onOpenAuditRights={() => setIsAuditRightsModalOpen(true)}
                onOpenRemediation={() => setIsRemediationModalOpen(true)}
              />
            </main>
          )}
        </div>
      )}

      {/* Authentication Modal (Sign In & Sign Up) */}
      <AuthModal
        isOpen={isAuthModalOpen}
        onClose={() => setIsAuthModalOpen(false)}
        lang={lang}
        onAuthSuccess={handleAuthSuccess}
      />

      {/* Advanced Regulatory Ingestion Telemetry Modal */}
      <IngestionModal
        isOpen={isIngestModalOpen}
        lang={lang}
        filename={pendingFile?.name || "document.pdf"}
        fileSizeBytes={pendingFile?.size || 0}
        onComplete={() => setIsIngestModalOpen(false)}
      />

      {/* Official BaFin / DIN 66399 Regulatory Certificate Modal */}
      <AuditCertificateModal
        isOpen={isCertificateOpen}
        onClose={() => setIsCertificateOpen(false)}
        lang={lang}
        documentId={documentId || undefined}
        documentName={documentName}
        availableDocuments={availableDocuments}
        onSelectDocument={handleSelectDocument}
      />

      {/* ZUGFeRD 2.3 XML vs Visual PDF Discrepancy Inspector Modal */}
      <ZugferdInspectorModal
        isOpen={isZugferdModalOpen}
        onClose={() => setIsZugferdModalOpen(false)}
        lang={lang}
        documentId={documentId || undefined}
        documentName={documentName}
        availableDocuments={availableDocuments}
        onSelectDocument={handleSelectDocument}
      />

      {/* EU DORA Art. 30(2) & BaFin Exit Strategy Regulatory Inspector Modal */}
      <DoraExitInspectorModal
        isOpen={isDoraExitModalOpen}
        onClose={() => setIsDoraExitModalOpen(false)}
        lang={lang}
        documentId={documentId || undefined}
        documentName={documentName}
        availableDocuments={availableDocuments}
        onSelectDocument={handleSelectDocument}
        onJumpToCitation={(page, bbox) => {
          setCurrentPage(page);
          if (bbox) {
            setActiveHighlight({
              page_number: page,
              box: bbox,
              label: "DORA Art. 30(2) Clause Evidence",
            });
          }
          setLayoutMode("workbench");
        }}
      />

      {/* EU DORA Art. 30(3) & BaFin Sub-Outsourcing & Cascading Risk Inspector Modal */}
      <DoraSubcontractorModal
        isOpen={isDoraSubcontractorModalOpen}
        onClose={() => setIsDoraSubcontractorModalOpen(false)}
        lang={lang}
        documentId={documentId || undefined}
        documentName={documentName}
        availableDocuments={availableDocuments}
        onSelectDocument={handleSelectDocument}
        onJumpToCitation={(page, bbox) => {
          setCurrentPage(page);
          if (bbox) {
            setActiveHighlight({
              page_number: page,
              box: bbox,
              label: "DORA Art. 30(3) Subcontractor Evidence",
            });
          }
          setLayoutMode("workbench");
        }}
      />

      {/* KWG § 25b & EU DORA Art. 30(3)(e) Supervisory Audit Rights & DIN 5008 Letter Modal */}
      <AuditRightsModal
        isOpen={isAuditRightsModalOpen}
        onClose={() => setIsAuditRightsModalOpen(false)}
        lang={lang}
        documentId={documentId || undefined}
        documentName={documentName}
        availableDocuments={availableDocuments}
        onSelectDocument={handleSelectDocument}
        onJumpToCitation={(page, bbox) => {
          setCurrentPage(page);
          if (bbox) {
            setActiveHighlight({
              page_number: page,
              box: bbox,
              label: "KWG § 25b / DORA Art. 30(3)(e) Audit Evidence",
            });
          }
          setLayoutMode("workbench");
        }}
      />

      {/* BGB § 311 Contract Amendment & Redline Diff Synthesizer Modal */}
      <RemediationModal
        isOpen={isRemediationModalOpen}
        onClose={() => setIsRemediationModalOpen(false)}
        documentId={documentId}
        documentName={documentName}
        lang={lang}
      />

      {/* Silicon Valley Command Palette & Spotlight (⌘K / Ctrl+K) */}
      <CommandPalette
        isOpen={isCommandPaletteOpen}
        onClose={() => setIsCommandPaletteOpen(false)}
        lang={lang}
        onToggleLang={() => handleToggleLang(lang === "DE" ? "EN" : "DE")}
        onOpenWorkbench={() => {
          if (!user) setLayoutMode("login");
          else setLayoutMode("workbench");
        }}
        onOpenAuditor={() => {
          if (!user) setLayoutMode("login");
          else setLayoutMode("auditor");
        }}
        onOpenDoraExit={() => setIsDoraExitModalOpen(true)}
        onOpenDoraSubcontractor={() => setIsDoraSubcontractorModalOpen(true)}
        onOpenAuditRights={() => setIsAuditRightsModalOpen(true)}
        onOpenRemediation={() => setIsRemediationModalOpen(true)}
        onOpenZugferd={() => setIsZugferdModalOpen(true)}
        onOpenCertificate={() => setIsCertificateOpen(true)}
        availableDocuments={availableDocuments}
        onSelectDocument={handleSelectDocument}
      />
    </div>
  );
}

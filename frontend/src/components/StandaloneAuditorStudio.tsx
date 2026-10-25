"use client";

import React, { useState, useRef, useEffect } from "react";
import {
  Scale,
  Send,
  CheckCircle,
  AlertCircle,
  ExternalLink,
  Bot,
  User,
  Sparkles,
  Languages,
  Download,
  FileText,
  Clock,
  Plus,
  BookOpen,
  ShieldCheck,
  ChevronRight,
  ArrowUpRight,
  HelpCircle,
  Copy,
  Check,
  Trash2,
} from "lucide-react";
import { auditDocument, AuditApiResponse, AuditCitationResponse } from "@/lib/api";
import { Language, translations } from "@/lib/i18n";
import { translateGermanToEnglish } from "@/lib/translator";

export interface StandaloneAuditorProps {
  lang?: Language;
  documentId?: string | null;
  documentName?: string;
  availableDocuments?: any[];
  onSelectDocument?: (doc: any) => void;
  onOpenWorkbenchWithCitation?: (page: number, bbox: [number, number, number, number]) => void;
  onSwitchToWorkbench?: () => void;
}

interface ThreadInquiry {
  id: string;
  title: string;
  framework: "DORA" | "LkSG" | "ZUGFeRD";
  timestamp: string;
  messages: Array<{
    id: string;
    sender: "user" | "auditor";
    text: string;
    citations?: AuditCitationResponse[];
    timestamp: string;
  }>;
}

const PRESET_PROMPTS = {
  DE: [
    {
      framework: "DORA" as const,
      label: "DORA Art. 30 Ausstiegsfrist",
      prompt: "Welche Kündigungs- und Übergangsfristen für den Ausstieg sind gem. DORA Art. 30 Abs. 2 geregelt?",
    },
    {
      framework: "DORA" as const,
      label: "Haftung & 0,2% Verzugsstrafe",
      prompt: "Wie hoch ist die maximale Verzugsstrafe und welche Haftungsbeschränkungen greifen nicht?",
    },
    {
      framework: "DORA" as const,
      label: "30 Tage Unterauftrag Veto",
      prompt: "Welche Frist und Genehmigungspflicht gilt für Unterauftragsvergaben nach DORA Art. 30 Abs. 3?",
    },
    {
      framework: "ZUGFeRD" as const,
      label: "ZUGFeRD 2.3 XML & Leitweg-ID",
      prompt: "Welches Rechnungsformat und welche Leitweg-ID sind nach ZUGFeRD 2.3 / Factur-X vereinbart?",
    },
    {
      framework: "LkSG" as const,
      label: "Sorgfaltspflichten & Audit",
      prompt: "Welche Kontroll- und Prüfungsrechte stehen dem Auftraggeber bezüglich Sub-Dienstleistern zu?",
    },
  ],
  EN: [
    {
      framework: "DORA" as const,
      label: "DORA Art. 30 Exit Window",
      prompt: "What termination and transition exit periods are stipulated under DORA Art. 30 (2)?",
    },
    {
      framework: "DORA" as const,
      label: "Liability & 0.2% Delay Penalty",
      prompt: "What is the maximum delay penalty rate and which liability caps are explicitly waived?",
    },
    {
      framework: "DORA" as const,
      label: "30-Day Subcontractor Veto",
      prompt: "What notice period and approval requirements apply to sub-outsourcing under DORA Art. 30 (3)?",
    },
    {
      framework: "ZUGFeRD" as const,
      label: "ZUGFeRD 2.3 XML & Leitweg-ID",
      prompt: "Which invoice format and Leitweg-ID are agreed under ZUGFeRD 2.3 / Factur-X standards?",
    },
    {
      framework: "LkSG" as const,
      label: "Due Diligence & Audit Rights",
      prompt: "What audit and inspection rights does the client retain regarding sub-contractor facilities?",
    },
  ],
};

export function StandaloneAuditorStudio({
  lang = "DE",
  documentId,
  documentName = "",
  availableDocuments = [],
  onSelectDocument,
  onOpenWorkbenchWithCitation,
  onSwitchToWorkbench,
}: StandaloneAuditorProps) {
  const t = translations[lang];
  const [framework, setFramework] = useState<"DORA" | "LkSG" | "ZUGFeRD">("DORA");
  const [query, setQuery] = useState("");
  const [loading, setLoading] = useState(false);
  const [auditWarning, setAuditWarning] = useState<string | null>(null);
  const [translatedMap, setTranslatedMap] = useState<Record<string, boolean>>({});
  const [selectedCitation, setSelectedCitation] = useState<AuditCitationResponse | null>(null);
  const [copiedId, setCopiedId] = useState<string | null>(null);

  // Initial Threads - Clean state without fake pre-populated answers
  const [threads, setThreads] = useState<ThreadInquiry[]>([
    {
      id: "thread-1",
      title: lang === "DE" ? "Neuer Prüfvorgang" : "New Audit Inquiry",
      framework: "DORA",
      timestamp: lang === "DE" ? "Jetzt" : "Just now",
      messages: [],
    },
  ]);

  const [activeThreadId, setActiveThreadId] = useState<string>("thread-1");
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const activeThread = threads.find((t) => t.id === activeThreadId) || threads[0];

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [activeThread?.messages, loading]);

  const handleCreateNewThread = () => {
    const newId = `thread-${Date.now()}`;
    const newThread: ThreadInquiry = {
      id: newId,
      title: lang === "DE" ? "Neuer Prüfvorgang" : "New Audit Inquiry",
      framework: framework,
      timestamp: lang === "DE" ? "Gerade eben" : "Just now",
      messages: [],
    };
    setThreads([newThread, ...threads]);
    setActiveThreadId(newId);
    setSelectedCitation(null);
    setAuditWarning(null);
  };

  const handleDeleteThread = (threadIdToDelete: string) => {
    setThreads((prev) => {
      const filtered = prev.filter((t) => t.id !== threadIdToDelete);
      if (threadIdToDelete === activeThreadId) {
        if (filtered.length > 0) {
          setActiveThreadId(filtered[0].id);
          setSelectedCitation(
            filtered[0].messages.find((m) => m.citations?.length)?.citations?.[0] || null
          );
        } else {
          const freshId = `thread-${Date.now()}`;
          const freshThread: ThreadInquiry = {
            id: freshId,
            title: lang === "DE" ? "Neuer Prüfvorgang" : "New Audit Inquiry",
            framework: framework,
            timestamp: lang === "DE" ? "Jetzt" : "Just now",
            messages: [],
          };
          setActiveThreadId(freshId);
          setSelectedCitation(null);
          return [freshThread];
        }
      }
      return filtered;
    });
  };

  const handleClearAllHistory = () => {
    const freshId = `thread-${Date.now()}`;
    const freshThread: ThreadInquiry = {
      id: freshId,
      title: lang === "DE" ? "Neuer Prüfvorgang" : "New Audit Inquiry",
      framework: framework,
      timestamp: lang === "DE" ? "Jetzt" : "Just now",
      messages: [],
    };
    setThreads([freshThread]);
    setActiveThreadId(freshId);
    setSelectedCitation(null);
    setAuditWarning(null);
  };

  const handleDeleteMessage = (messageIdToDelete: string) => {
    setThreads((prev) =>
      prev.map((t) =>
        t.id === activeThreadId
          ? {
              ...t,
              messages: t.messages.filter((m) => m.id !== messageIdToDelete),
            }
          : t
      )
    );
  };

  const handleSendQuery = async (customPrompt?: string) => {
    const promptToSend = (customPrompt || query).trim();
    if (!promptToSend) return;

    // Strict Zero-Hallucination Guard: Require a selected PDF before executing compliance audit
    if (!documentId) {
      setAuditWarning(
        lang === "DE"
          ? "Kein PDF-Dokument ausgewählt! Bitte wählen Sie oben ein Dokument aus oder laden Sie einen Vertrag hoch, um eine KI-Konformitätsprüfung durchzuführen."
          : "No PDF document selected! Please select a document from the top bar or upload a contract before conducting an AI audit."
      );
      return;
    }

    setAuditWarning(null);
    const userMessageId = `msg-user-${Date.now()}`;
    const userMsg = {
      id: userMessageId,
      sender: "user" as const,
      text: promptToSend,
      timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
    };

    // Append to active thread
    setThreads((prev) =>
      prev.map((t) =>
        t.id === activeThreadId
          ? {
              ...t,
              title: t.messages.length === 0 ? promptToSend.slice(0, 38) + "..." : t.title,
              messages: [...t.messages, userMsg],
            }
          : t
      )
    );

    setQuery("");
    setLoading(true);

    try {
      const historyPayload = (activeThread?.messages || []).map((m) => ({
        role: m.sender as "user" | "auditor",
        text: m.text,
      }));

      const res = await auditDocument(documentId, promptToSend, framework, historyPayload);
      const resultText = res.finding_summary;
      const citationsList = res.citations || [];

      const auditorMsg = {
        id: `msg-auditor-${Date.now()}`,
        sender: "auditor" as const,
        text: resultText,
        citations: citationsList,
        timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
      };

      setThreads((prev) =>
        prev.map((t) =>
          t.id === activeThreadId
            ? { ...t, messages: [...t.messages, auditorMsg] }
            : t
        )
      );

      if (citationsList.length > 0) {
        setSelectedCitation(citationsList[0]);
      }
    } catch (err: any) {
      console.error("Auditor error:", err);
      setAuditWarning(err.message || "Failed to execute audit inquiry.");
    } finally {
      setLoading(false);
    }
  };

  const handleCopyText = (text: string, id: string) => {
    navigator.clipboard.writeText(text);
    setCopiedId(id);
    setTimeout(() => setCopiedId(null), 2000);
  };

  return (
    <div className="flex-1 flex h-full overflow-hidden bg-[var(--background)] font-sans">
      {/* 1. Left Sidebar: Audit History & Framework Selector */}
      <aside className="w-72 shrink-0 bg-[var(--surface-dark)] border-r border-[var(--surface-border)] flex flex-col justify-between select-none">
        <div className="p-4 space-y-4 flex-1 overflow-auto">
          {/* New Thread Action */}
          <button
            onClick={handleCreateNewThread}
            className="w-full flex items-center justify-center gap-2 bg-[var(--surface-card)] hover:bg-[var(--surface-dark)] text-[var(--foreground)] border border-[var(--surface-border)] hover:border-[var(--accent-tangerine)] font-mono text-xs font-bold py-2.5 px-3 rounded-xl transition-all shadow-sm cursor-pointer"
          >
            <Plus className="w-4 h-4 text-[var(--accent-tangerine)]" />
            <span>{t.studio_new_thread}</span>
          </button>

          {/* Framework Switcher */}
          <div className="space-y-1.5">
            <span className="text-[10px] font-mono font-bold uppercase tracking-wider text-[var(--foreground)] opacity-50 px-1">
              {t.studio_framework_label}
            </span>
            <div className="grid grid-cols-3 gap-1 bg-[var(--surface-card)] p-1 rounded-lg border border-[var(--surface-border)] font-mono text-[10px]">
              {(["DORA", "LkSG", "ZUGFeRD"] as const).map((fw) => (
                <button
                  key={fw}
                  onClick={() => setFramework(fw)}
                  className={`py-1 rounded font-bold transition-all cursor-pointer ${
                    framework === fw
                      ? "bg-[var(--accent-tangerine)] text-[var(--accent-contrast)] shadow-sm"
                      : "text-[var(--foreground)] opacity-60 hover:opacity-100"
                  }`}
                >
                  {fw}
                </button>
              ))}
            </div>
          </div>

          {/* Audit History List */}
          <div className="space-y-1 pt-2">
            <div className="flex items-center justify-between px-1">
              <span className="text-[10px] font-mono font-bold uppercase tracking-wider text-[var(--foreground)] opacity-50 flex items-center gap-1.5">
                <Clock className="w-3 h-3 text-[var(--accent-tangerine)]" />
                <span>{t.studio_history_label} ({threads.length})</span>
              </span>
              {(threads.length > 1 || threads[0]?.messages.length > 0) && (
                <button
                  onClick={handleClearAllHistory}
                  title={lang === "DE" ? "Gesamte Historie leeren" : "Clear all history"}
                  className="text-[9px] font-mono text-rose-400 opacity-60 hover:opacity-100 transition-opacity cursor-pointer flex items-center gap-1 hover:underline"
                >
                  <Trash2 className="w-2.5 h-2.5" />
                  <span>{lang === "DE" ? "Leeren" : "Clear"}</span>
                </button>
              )}
            </div>
            <div className="space-y-1 pt-1">
              {threads.map((item) => {
                const isActive = item.id === activeThreadId;
                const displayTitle =
                  lang === "EN"
                    ? item.title
                        .replace("Ausstiegsfrist & Migration", "Exit Period & Migration")
                        .replace("Haftung & 0,2% Verzugsstrafen", "Liability & 0.2% Delay Penalties")
                        .replace("Neuer Prüfvorgang", "New Audit Inquiry")
                    : item.title;

                return (
                  <div
                    key={item.id}
                    onClick={() => {
                      setActiveThreadId(item.id);
                      setSelectedCitation(item.messages.find((m) => m.citations?.length)?.citations?.[0] || null);
                    }}
                    className={`group relative w-full text-left p-2.5 rounded-xl text-xs font-mono transition-all cursor-pointer border ${
                      isActive
                        ? "bg-[var(--surface-card)] border-[var(--accent-tangerine)] text-[var(--foreground)] font-bold shadow-sm"
                        : "border-transparent text-[var(--foreground)] opacity-65 hover:opacity-100 hover:bg-[var(--surface-card)]/50"
                    }`}
                  >
                    <div className="flex items-center justify-between mb-1">
                      <span className="text-[9px] px-1.5 py-0.2 rounded bg-[var(--surface-dark)] border border-[var(--surface-border)] text-[var(--accent-tangerine)] font-bold">
                        {item.framework}
                      </span>
                      <div className="flex items-center gap-1.5">
                        <span className="text-[9px] opacity-40">{item.timestamp}</span>
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            handleDeleteThread(item.id);
                          }}
                          title={lang === "DE" ? "Diesen Vorgang aus Historie löschen" : "Delete this inquiry from history"}
                          className="opacity-0 group-hover:opacity-100 hover:text-rose-400 p-0.5 rounded transition-opacity cursor-pointer text-[var(--foreground)]/60 hover:bg-rose-500/10"
                        >
                          <Trash2 className="w-3 h-3 text-rose-400" />
                        </button>
                      </div>
                    </div>
                    <p className="truncate text-[11px] pr-2">{displayTitle}</p>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Prompt Library Presets */}
          <div className="space-y-1.5 pt-3 border-t border-[var(--surface-border)]">
            <span className="text-[10px] font-mono font-bold uppercase tracking-wider text-[var(--foreground)] opacity-50 px-1 flex items-center gap-1.5">
              <Sparkles className="w-3 h-3 text-[var(--accent-cyan)]" />
              <span>{t.studio_presets_label}</span>
            </span>
            <div className="space-y-1">
              {PRESET_PROMPTS[lang].map((p, idx) => (
                <button
                  key={idx}
                  onClick={() => handleSendQuery(p.prompt)}
                  className={`w-full text-left p-2 rounded-lg bg-[var(--surface-card)] hover:bg-[var(--surface-dark)] border border-[var(--surface-border)] hover:border-[var(--accent-cyan)] text-[10.5px] font-mono text-[var(--foreground)] opacity-75 hover:opacity-100 transition-all cursor-pointer truncate ${!documentId ? "opacity-50 hover:border-amber-500/50" : ""}`}
                  title={documentId ? p.prompt : (lang === "DE" ? "⚠️ Kein PDF ausgewählt (Bitte zuerst Dokument wählen)" : "⚠️ No PDF selected (Select document first)")}
                >
                  <div className="flex items-center justify-between">
                    <span className="truncate">{p.label}</span>
                    {!documentId && (
                      <span className="text-[9px] text-amber-500 font-bold ml-1">PDF!</span>
                    )}
                  </div>
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Sidebar Footer */}
        <div className="p-3 border-t border-[var(--surface-border)] text-[10px] font-mono text-[var(--foreground)] opacity-60 flex items-center justify-between">
          <span className="flex items-center gap-1.5">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-400"></span>
            {lang === "DE" ? "KI-Audit Engine v0.2" : "AI Audit Engine v0.2"}
          </span>
          <span className="text-[9px] bg-emerald-500/10 text-emerald-500 border border-emerald-500/25 px-1.5 py-0.5 rounded font-bold">
            BAFIN READY
          </span>
        </div>
      </aside>

      {/* 2. Center Stage: Harvey / ChatGPT Legal Conversational Workspace */}
      <main className="flex-1 flex flex-col h-full overflow-hidden bg-[var(--background)]">
        {/* Studio Top Bar */}
        <div className="h-14 border-b border-[var(--surface-border)] bg-[var(--surface-card)] px-6 flex items-center justify-between shrink-0">
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 rounded-lg bg-[var(--accent-tangerine)]/15 border border-[var(--accent-tangerine)]/30 flex items-center justify-center text-[var(--accent-tangerine)] shrink-0">
                <Scale className="w-4 h-4 stroke-[2.5]" />
              </div>
              <div>
                <div className="flex items-center gap-2">
                  <h2 className="font-extrabold text-xs tracking-wider uppercase font-mono text-[var(--foreground)]">
                    {t.studio_title}
                  </h2>
                  <span className="text-[10px] font-mono px-2 py-0.5 rounded-full bg-[var(--surface-dark)] border border-[var(--surface-border)] font-bold text-[var(--accent-tangerine)]">
                    {framework} Grounded
                  </span>
                </div>
              </div>
            </div>

            {/* Document Selector in Studio Header */}
            {availableDocuments && availableDocuments.length > 0 && (
              <div className="hidden md:flex items-center gap-2 pl-3 border-l border-[var(--surface-border)]">
                <FileText className="w-3.5 h-3.5 text-[var(--accent-tangerine)] shrink-0" />
                <select
                  value={documentId || ""}
                  onChange={(e) => {
                    setAuditWarning(null);
                    if (e.target.value === "") {
                      if (onSelectDocument) onSelectDocument(null);
                    } else {
                      const doc = availableDocuments.find((d) => d.id === e.target.value);
                      if (doc && onSelectDocument) onSelectDocument(doc);
                    }
                  }}
                  className={`bg-[var(--surface-dark)] border text-xs rounded-lg px-2.5 py-1.5 font-mono max-w-[220px] lg:max-w-[300px] truncate shadow-sm cursor-pointer transition-colors ${
                    documentId
                      ? "border-emerald-500/50 text-[var(--foreground)]"
                      : "border-amber-500/60 text-amber-500 animate-pulse"
                  }`}
                >
                  <option value="">{lang === "DE" ? "⚠️ Kein PDF gewählt (Dokument wählen...)" : "⚠️ No PDF (Select document...)"}</option>
                  {availableDocuments.map((doc) => (
                    <option key={doc.id} value={doc.id}>
                      {doc.filename}
                    </option>
                  ))}
                </select>
                {documentId ? (
                  <span className="text-[9px] font-mono px-1.5 py-0.5 rounded bg-emerald-500/10 text-emerald-500 border border-emerald-500/30 font-bold hidden lg:inline">
                    PDF BEREIT
                  </span>
                ) : (
                  <span className="text-[9px] font-mono px-1.5 py-0.5 rounded bg-amber-500/10 text-amber-500 border border-amber-500/30 font-bold hidden lg:inline">
                    KEIN DOKUMENT
                  </span>
                )}
              </div>
            )}
          </div>

          <div className="flex items-center gap-2">
            {onSwitchToWorkbench && (
              <button
                onClick={onSwitchToWorkbench}
                className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-[var(--surface-dark)] hover:bg-[var(--surface-card)] border border-[var(--surface-border)] text-[var(--foreground)] font-mono text-xs font-bold transition-all shadow-sm cursor-pointer"
              >
                <span>{t.studio_btn_workbench}</span>
                <ArrowUpRight className="w-3.5 h-3.5 stroke-[2.5]" />
              </button>
            )}
            <button
              onClick={() => {
                if (documentId) {
                  window.open(`http://localhost:8000/api/v1/documents/${documentId}/export-english-pdf`, "_blank");
                }
              }}
              title="Download Certified Audit Dossier in PDF"
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-[var(--foreground)] text-[var(--background)] hover:opacity-90 font-mono text-xs font-bold transition-all shadow cursor-pointer uppercase tracking-wider"
            >
              <Download className="w-3.5 h-3.5" />
              <span>{t.studio_btn_pdf}</span>
            </button>
          </div>
        </div>

        {/* Warning Banner if Audit Attempted without Document */}
        {auditWarning && (
          <div className="mx-6 mt-3 p-3.5 rounded-xl bg-amber-500/15 border border-amber-500/40 text-amber-500 text-xs font-mono flex items-center justify-between shadow-sm animate-in fade-in duration-150">
            <div className="flex items-center gap-2.5">
              <AlertCircle className="w-4 h-4 flex-shrink-0" />
              <span>{auditWarning}</span>
            </div>
            <button
              onClick={() => setAuditWarning(null)}
              className="p-1 hover:opacity-100 opacity-60 font-bold cursor-pointer"
            >
              ✕
            </button>
          </div>
        )}

        {/* Message Thread */}
        <div className="flex-1 overflow-auto p-6 space-y-6">
          {activeThread.messages.length === 0 ? (
            <div className="h-full flex flex-col items-center justify-center text-center p-8 max-w-lg mx-auto">
              <div className="w-16 h-16 rounded-2xl bg-[var(--accent-tangerine)]/10 border border-[var(--accent-tangerine)]/30 flex items-center justify-center text-[var(--accent-tangerine)] mb-4 shadow-md">
                <Bot className="w-8 h-8" />
              </div>
              <h3 className="font-extrabold text-sm font-mono uppercase tracking-wide text-[var(--foreground)] mb-2">
                {t.studio_empty_title}
              </h3>
              <p className="text-xs text-[var(--foreground)] opacity-60 leading-relaxed font-sans mb-6">
                {t.studio_empty_desc}
              </p>

              {!documentId ? (
                /* Clear callout when NO PDF is selected */
                <div className="w-full p-5 rounded-2xl bg-[var(--surface-card)] border border-amber-500/30 shadow-md text-left space-y-3.5">
                  <div className="flex items-center gap-2 text-amber-500 font-mono text-xs font-bold">
                    <AlertCircle className="w-4 h-4 flex-shrink-0" />
                    <span>{lang === "DE" ? "Kein PDF-Dokument ausgewählt" : "No PDF Document Selected"}</span>
                  </div>
                  <p className="text-xs text-[var(--foreground)] opacity-80 font-sans leading-relaxed">
                    {lang === "DE"
                      ? "Für eine revisionssichere Prüfung gem. DORA Art. 30 und BaFin-Kriterien muss zuerst ein Vertrag ausgewählt werden. Ohne Dokument werden keine Vermutungen oder Schein-Ergebnisse generiert."
                      : "For an audit-proof compliance review under DORA Art. 30 and BaFin criteria, a contract must be selected first. No hypothetical or ungrounded answers will be generated without a document."}
                  </p>
                  {availableDocuments && availableDocuments.length > 0 && onSelectDocument && (
                    <button
                      onClick={() => onSelectDocument(availableDocuments[0])}
                      className="w-full py-2.5 px-4 rounded-xl bg-[var(--accent-tangerine)] hover:opacity-95 text-[var(--accent-contrast)] font-mono text-xs font-bold shadow-md transition-all cursor-pointer flex items-center justify-center gap-2 active:scale-95"
                    >
                      <FileText className="w-4 h-4" />
                      <span>{lang === "DE" ? `„${availableDocuments[0].filename}“ auswählen` : `Select "${availableDocuments[0].filename}"`}</span>
                    </button>
                  )}
                  {onSwitchToWorkbench && (
                    <button
                      onClick={onSwitchToWorkbench}
                      className="w-full py-2.5 px-4 rounded-xl bg-[var(--surface-dark)] hover:bg-[var(--surface-card)] border border-[var(--surface-border)] text-[var(--foreground)] font-mono text-xs font-bold transition-all cursor-pointer flex items-center justify-center gap-2"
                    >
                      <ArrowUpRight className="w-4 h-4" />
                      <span>{lang === "DE" ? "Zur PDF-Prüfbank & Dokument hochladen" : "Go to PDF Workbench & Upload"}</span>
                    </button>
                  )}
                </div>
              ) : (
                <div className="grid grid-cols-2 gap-2 w-full text-left">
                  {PRESET_PROMPTS[lang].slice(0, 4).map((p, idx) => (
                    <button
                      key={idx}
                      onClick={() => handleSendQuery(p.prompt)}
                      className="p-3 rounded-xl bg-[var(--surface-card)] border border-[var(--surface-border)] hover:border-[var(--accent-tangerine)] text-xs font-mono text-[var(--foreground)] opacity-80 hover:opacity-100 transition-all cursor-pointer shadow-sm"
                    >
                      <div className="text-[10px] text-[var(--accent-tangerine)] font-bold mb-1">
                        {p.framework}
                      </div>
                      <div className="truncate text-[11px]">{p.label}</div>
                    </button>
                  ))}
                </div>
              )}
            </div>
          ) : (
            activeThread.messages.map((msg) => {
              const isUser = msg.sender === "user";
              // If lang is EN, default to English translation unless toggled off
              const isTranslated =
                translatedMap[msg.id] !== undefined
                  ? translatedMap[msg.id]
                  : lang === "EN";
              const displayedText = isTranslated
                ? translateGermanToEnglish(msg.text)
                : msg.text;

              return (
                <div
                  key={msg.id}
                  className={`flex gap-3 max-w-3xl ${isUser ? "ml-auto justify-end" : "mr-auto"}`}
                >
                  {!isUser && (
                    <div className="w-8 h-8 rounded-xl bg-[var(--surface-card)] border border-[var(--surface-border)] flex items-center justify-center text-[var(--accent-tangerine)] shrink-0 mt-1 shadow-sm">
                      <Bot className="w-4 h-4" />
                    </div>
                  )}

                  <div
                    className={`rounded-2xl p-4 space-y-3 shadow-sm ${
                      isUser
                        ? "bg-[var(--surface-card)] border border-[var(--accent-tangerine)]/40 text-[var(--foreground)] max-w-xl"
                        : "bg-[var(--surface-card)] border border-[var(--surface-border)] border-l-4 border-l-[var(--accent-tangerine)] flex-1"
                    }`}
                  >
                    {!isUser && (
                      <div className="flex items-center justify-between pb-2 border-b border-[var(--surface-border)] text-xs">
                        <span className="font-mono font-bold text-emerald-500 flex items-center gap-1.5">
                          <CheckCircle className="w-3.5 h-3.5" />
                          <span>{framework} {lang === "DE" ? "Geprüft (Audit-Beleg)" : "Verified (Audit Evidence)"}</span>
                        </span>

                        <div className="flex items-center gap-2">
                          <button
                            onClick={() =>
                              setTranslatedMap((prev) => ({
                                ...prev,
                                [msg.id]: !prev[msg.id],
                              }))
                            }
                            className="flex items-center gap-1 text-[10px] font-mono px-2 py-0.5 rounded bg-[var(--surface-dark)] border border-[var(--surface-border)] text-[var(--accent-cyan)] font-bold hover:border-[var(--accent-cyan)] transition-all cursor-pointer"
                          >
                            <Languages className="w-3 h-3" />
                            <span>{isTranslated ? (lang === "DE" ? "Original Deutsch 🇩🇪" : "German Original 🇩🇪") : (lang === "DE" ? "Auf Englisch übersetzen 🇬🇧" : "Translate to English 🇬🇧")}</span>
                          </button>

                          <button
                            onClick={() => handleCopyText(displayedText, msg.id)}
                            className="text-[var(--foreground)] opacity-50 hover:opacity-100 p-1 rounded hover:bg-[var(--surface-dark)] cursor-pointer"
                            title={lang === "DE" ? "Befund kopieren" : "Copy Finding"}
                          >
                            {copiedId === msg.id ? (
                              <Check className="w-3.5 h-3.5 text-emerald-400" />
                            ) : (
                              <Copy className="w-3.5 h-3.5" />
                            )}
                          </button>

                          <button
                            onClick={() => handleDeleteMessage(msg.id)}
                            className="text-[var(--foreground)] opacity-40 hover:opacity-100 hover:text-rose-400 p-1 rounded hover:bg-rose-500/10 cursor-pointer transition-colors"
                            title={lang === "DE" ? "Befund aus Historie löschen" : "Delete finding from history"}
                          >
                            <Trash2 className="w-3.5 h-3.5" />
                          </button>
                        </div>
                      </div>
                    )}

                    <p className="text-[13px] text-[var(--foreground)] leading-relaxed font-sans whitespace-pre-line">
                      {displayedText}
                    </p>

                    {/* Interactive Citation Pills */}
                    {msg.citations && msg.citations.length > 0 && (
                      <div className="pt-2.5 border-t border-[var(--surface-border)] space-y-1.5">
                        <span className="text-[10px] font-mono uppercase tracking-wider text-[var(--foreground)] opacity-50 font-bold block">
                          {lang === "DE" ? "Geprüfte Belegstellen im Vertrag:" : "Verified Contract Citations:"}
                        </span>
                        <div className="flex flex-wrap gap-2">
                          {msg.citations.map((c, idx) => (
                            <button
                              key={idx}
                              onClick={() => setSelectedCitation(c)}
                              className={`flex items-center gap-1.5 px-2.5 py-1 rounded-lg border font-mono text-[10.5px] transition-all cursor-pointer shadow-sm ${
                                selectedCitation?.source_tag === c.source_tag
                                  ? "bg-[var(--accent-tangerine)] text-[var(--accent-contrast)] border-[var(--accent-tangerine)] font-bold"
                                  : "bg-[var(--surface-dark)] border-[var(--surface-border)] text-[var(--foreground)] hover:border-[var(--accent-tangerine)]"
                              }`}
                            >
                              <span>{c.source_tag}</span>
                              <span className="opacity-70 text-[9.5px]">
                                {lang === "DE" ? "S." : "P."} {c.page_number}
                              </span>
                            </button>
                          ))}
                        </div>
                      </div>
                    )}

                    <div className="flex items-center justify-between text-[9.5px] font-mono opacity-40 pt-1">
                      {isUser ? (
                        <button
                          onClick={() => handleDeleteMessage(msg.id)}
                          className="opacity-60 hover:opacity-100 hover:text-rose-400 flex items-center gap-1 transition-opacity cursor-pointer text-rose-400/80"
                          title={lang === "DE" ? "Frage löschen" : "Delete question"}
                        >
                          <Trash2 className="w-3 h-3" />
                          <span>{lang === "DE" ? "Löschen" : "Delete"}</span>
                        </button>
                      ) : (
                        <span />
                      )}
                      <span>{msg.timestamp}</span>
                    </div>
                  </div>

                  {isUser && (
                    <div className="w-8 h-8 rounded-xl bg-[var(--accent-tangerine)]/15 border border-[var(--accent-tangerine)]/40 flex items-center justify-center text-[var(--accent-tangerine)] shrink-0 mt-1 shadow-sm">
                      <User className="w-4 h-4" />
                    </div>
                  )}
                </div>
              );
            })
          )}
          <div ref={messagesEndRef} />
        </div>

        {/* Legal Inquiry Composer */}
        <div className="p-4 bg-[var(--surface-card)] border-t border-[var(--surface-border)] shrink-0">
          <div className="max-w-3xl mx-auto space-y-2">
            <div className="relative">
              <textarea
                value={query}
                onChange={(e) => {
                  setQuery(e.target.value);
                  if (auditWarning) setAuditWarning(null);
                }}
                onKeyDown={(e) => {
                  if (e.key === "Enter" && !e.shiftKey) {
                    e.preventDefault();
                    handleSendQuery();
                  }
                }}
                placeholder={
                  documentId
                    ? t.studio_input_placeholder
                    : lang === "DE"
                    ? "⚠️ Bitte wählen Sie zuerst oben ein PDF-Dokument aus, um Fragen zu stellen..."
                    : "⚠️ Please select a PDF document from the top bar first to submit audit inquiries..."
                }
                rows={2}
                className={`w-full bg-[var(--surface-dark)] border rounded-xl px-4 py-3 pr-12 text-xs text-[var(--foreground)] font-mono leading-relaxed focus:outline-none resize-none shadow-inner transition-colors ${
                  !documentId
                    ? "border-amber-500/40 placeholder:text-amber-500/60"
                    : "border-[var(--surface-border)] focus:border-[var(--accent-tangerine)]"
                }`}
              />
              <button
                onClick={() => handleSendQuery()}
                disabled={!query.trim() || loading}
                className="absolute right-3 bottom-3 p-2 rounded-lg bg-[var(--accent-tangerine)] hover:opacity-90 disabled:opacity-30 text-[var(--accent-contrast)] transition-all shadow-sm cursor-pointer"
                title={documentId ? (lang === "DE" ? "Prüfung ausführen" : "Run Audit Inquiry") : (lang === "DE" ? "Bitte zuerst PDF auswählen" : "Please select PDF first")}
              >
                <Send className="w-4 h-4 stroke-[2.5]" />
              </button>
            </div>
            <p className="text-[10px] font-mono text-[var(--foreground)] opacity-50 text-center">
              {lang === "DE"
                ? "Revisionssicher gem. BaFin Rundschreiben & DORA Art. 30 · Zero-Hallucination-Standard (Erfordert aktiven PDF-Vertrag)."
                : "Audit-proof under BaFin circulars & DORA Art. 30 · Zero-Hallucination Standard (Requires active PDF contract)."}
            </p>
          </div>
        </div>
      </main>

      {/* 3. Right Drawer: Verifiable Evidence & Document Context */}
      <aside className="w-80 shrink-0 bg-[var(--surface-dark)] border-l border-[var(--surface-border)] flex flex-col justify-between select-none">
        <div className="p-4 space-y-4 flex-1 overflow-auto">
          <div className="flex items-center justify-between border-b border-[var(--surface-border)] pb-2.5">
            <div className="flex items-center gap-2">
              <BookOpen className="w-4 h-4 text-[var(--accent-tangerine)]" />
              <span className="font-mono font-bold text-xs uppercase tracking-wide text-[var(--foreground)]">
                {t.studio_evidence_title}
              </span>
            </div>
            <span className="text-[9.5px] font-mono text-emerald-500 bg-emerald-500/10 px-2 py-0.5 rounded border border-emerald-500/25 font-bold">
              {t.studio_evidence_verified}
            </span>
          </div>

          {selectedCitation ? (
            <div className="p-4 rounded-xl bg-[var(--surface-card)] border border-[var(--surface-border)] space-y-3 shadow-md animate-in fade-in duration-150">
              <div className="flex items-center justify-between text-xs font-mono">
                <span className="px-2 py-0.5 rounded bg-[var(--accent-tangerine)]/15 text-[var(--accent-tangerine)] border border-[var(--accent-tangerine)]/30 font-bold">
                  {selectedCitation.source_tag}
                </span>
                <span className="opacity-60 text-[11px]">
                  {lang === "DE" ? "Seite" : "Page"} {selectedCitation.page_number}
                </span>
              </div>

              <div>
                <span className="text-[10px] font-mono uppercase tracking-wider text-[var(--foreground)] opacity-50 font-bold block mb-1">
                  {lang === "DE" ? "Visuelle DIN A4 Koordinaten:" : "Visual DIN A4 Coordinates:"}
                </span>
                <span className="font-mono text-xs text-[var(--accent-cyan)] bg-[var(--surface-dark)] px-2 py-1 rounded border border-[var(--surface-border)] block">
                  📍 [{Math.round(selectedCitation.bounding_box?.[0] || 0)}, {Math.round(selectedCitation.bounding_box?.[1] || 0)}, {Math.round(selectedCitation.bounding_box?.[2] || 0)}, {Math.round(selectedCitation.bounding_box?.[3] || 0)}]
                </span>
              </div>

              <div>
                <span className="text-[10px] font-mono uppercase tracking-wider text-[var(--foreground)] opacity-50 font-bold block mb-1">
                  {lang === "DE" ? "Originaltext (Authentischer Wortlaut):" : "Verified Statutory Content (English):"}
                </span>
                <div className="p-3 rounded-lg bg-[var(--surface-dark)] border-l-2 border-[var(--accent-tangerine)] border-r border-t border-b border-[var(--surface-border)] text-xs font-sans text-[var(--foreground)] leading-relaxed">
                  "{lang === "EN" ? translateGermanToEnglish(selectedCitation.content || "") : selectedCitation.content}"
                </div>
                {lang === "EN" && (
                  <details className="mt-2 group/citation">
                    <summary className="text-[10px] font-mono text-[var(--accent-cyan)] cursor-pointer select-none">
                      Show German Statutory Source (DE 🇩🇪)
                    </summary>
                    <div className="mt-1 p-2.5 rounded bg-[var(--surface-dark)] border border-[var(--surface-border)] text-[11px] font-sans opacity-80 leading-relaxed">
                      "{selectedCitation.content}"
                    </div>
                  </details>
                )}
              </div>

              {onOpenWorkbenchWithCitation && (
                <button
                  onClick={() =>
                    onOpenWorkbenchWithCitation(
                      selectedCitation.page_number,
                      selectedCitation.bounding_box || [0, 0, 0, 0]
                    )
                  }
                  className="w-full flex items-center justify-center gap-1.5 py-2 px-3 rounded-lg bg-[var(--surface-dark)] hover:bg-[var(--surface-card)] text-[var(--accent-tangerine)] border border-[var(--accent-tangerine)]/40 font-mono text-[11px] font-bold transition-all shadow-sm cursor-pointer"
                >
                  <span>{t.studio_locate_workbench}</span>
                  <ArrowUpRight className="w-3.5 h-3.5" />
                </button>
              )}
            </div>
          ) : (
            <div className="p-6 rounded-xl bg-[var(--surface-card)] border border-[var(--surface-border)] text-center text-xs font-mono opacity-60 space-y-2">
              <ShieldCheck className="w-8 h-8 mx-auto text-[var(--accent-tangerine)] opacity-60" />
              <p className="font-bold">{lang === "DE" ? "Kein Beleg ausgewählt" : "No Citation Selected"}</p>
              <p className="text-[11px]">
                {lang === "DE"
                  ? "Klicken Sie auf ein [SOURCE_X] Tag im Chat, um die exakte Textstelle und Koordinaten einzusehen."
                  : "Click a [SOURCE_X] tag in the chat stream to view exact contract text and coordinates."}
              </p>
            </div>
          )}

          {/* Active Contract Info */}
          <div className="p-3.5 rounded-xl bg-[var(--surface-card)] border border-[var(--surface-border)] space-y-2 font-mono text-[11px] shadow-sm">
            <span className="text-[10px] uppercase tracking-wider opacity-50 font-bold block">
              {lang === "DE" ? "Geprüfter Master-Vertrag:" : "Audited Master Contract:"}
            </span>
            <div className="truncate font-bold text-[var(--foreground)]">
              {documentName}
            </div>
            <div className="text-[10px] opacity-60">
              {lang === "DE"
                ? "DIN 66399 Schutzklasse 3 · BaFin Audit-Prüfstrom aktiv"
                : "DIN 66399 Class 3 · BaFin Audit Stream Active"}
            </div>
          </div>
        </div>
      </aside>
    </div>
  );
}

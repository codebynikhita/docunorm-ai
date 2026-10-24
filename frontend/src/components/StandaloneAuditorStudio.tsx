"use client";

import React, { useState, useRef, useEffect } from "react";
import {
  Scale,
  Send,
  CheckCircle,
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
} from "lucide-react";
import { auditDocument, AuditApiResponse, AuditCitationResponse } from "@/lib/api";
import { Language, translations } from "@/lib/i18n";
import { translateGermanToEnglish } from "@/lib/translator";

export interface StandaloneAuditorProps {
  lang?: Language;
  documentId?: string | null;
  documentName?: string;
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

const PRESET_PROMPTS = [
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
];

export function StandaloneAuditorStudio({
  lang = "DE",
  documentId,
  documentName = "Siemens_Master_IKT_Vertrag_2026.pdf",
  onOpenWorkbenchWithCitation,
  onSwitchToWorkbench,
}: StandaloneAuditorProps) {
  const t = translations[lang];
  const [framework, setFramework] = useState<"DORA" | "LkSG" | "ZUGFeRD">("DORA");
  const [query, setQuery] = useState("");
  const [loading, setLoading] = useState(false);
  const [translatedMap, setTranslatedMap] = useState<Record<string, boolean>>({});
  const [selectedCitation, setSelectedCitation] = useState<AuditCitationResponse | null>(null);
  const [copiedId, setCopiedId] = useState<string | null>(null);

  // Initial Threads
  const [threads, setThreads] = useState<ThreadInquiry[]>([
    {
      id: "thread-1",
      title: "DORA Art. 30 Ausstiegsfrist & Migration",
      framework: "DORA",
      timestamp: "Heute, 16:30",
      messages: [
        {
          id: "m-1",
          sender: "user",
          text: "Welche Kündigungs- und Übergangsfristen für den Ausstieg sind gem. DORA Art. 30 Abs. 2 geregelt?",
          timestamp: "16:30",
        },
        {
          id: "m-2",
          sender: "auditor",
          text: "• [SOURCE_1]: Gemäß DORA Art. 30 Abs. 2 ist eine ordentliche Kündigungsfrist von 60 Tagen zum Quartalsende vereinbart.\n• [SOURCE_2]: Im Beendigungsfall garantiert der Auftragnehmer eine vollumfängliche Migrationsunterstützung für mindestens 90 Tage ohne Unterbrechung des Geschäftsbetriebs.",
          citations: [
            {
              source_tag: "[SOURCE_1]",
              page_number: 2,
              bounding_box: [50, 115, 528, 203],
              content:
                "Jede Vertragspartei kann diesen Vertrag mit einer ordentlichen Kündigungsfrist von sechzig (60) Tagen zum Quartalsende kündigen.",
            },
            {
              source_tag: "[SOURCE_2]",
              page_number: 2,
              bounding_box: [50, 115, 528, 203],
              content:
                "Der Auftragnehmer garantiert im Falle der Beendigung eine umfassende Unterstützungspflicht bei der Migration von Datenbeständen und Anwendungen auf den Auftraggeber oder einen benannten Dritte-Dienstleister für mindestens neunzig (90) Tage ohne Unterbrechung des Geschäftsbetriebs.",
            },
          ],
          timestamp: "16:31",
        },
      ],
    },
    {
      id: "thread-2",
      title: "Haftung & 0,2% Verzugsstrafen",
      framework: "DORA",
      timestamp: "Gestern",
      messages: [
        {
          id: "m-3",
          sender: "user",
          text: "Wie hoch ist die maximale Verzugsstrafe und welche Haftungsbeschränkungen greifen nicht?",
          timestamp: "Gestern",
        },
        {
          id: "m-4",
          sender: "auditor",
          text: "• [SOURCE_1]: Bei schuldhafter Nichteinhaltung vereinbarter Fristen zahlt der Auftragnehmer 0,2 % der jährlichen Vergütung pro Werktag, gedeckelt auf maximal 5 % des Gesamtauftragswerts.\n• [SOURCE_2]: Haftungsausschlüsse greifen ausdrücklich nicht bei grober Fahrlässigkeit, Vorsatz oder Verletzung von Datenschutzgesetzen.",
          citations: [
            {
              source_tag: "[SOURCE_1]",
              page_number: 2,
              bounding_box: [50, 225, 528, 283],
              content:
                "Vertragsstrafe in Höhe von 0,2 % der jährlichen Vergütung pro Werktag des Verzugs, höchstens jedoch 5 % des jährlichen Gesamtauftragswerts.",
            },
          ],
          timestamp: "Gestern",
        },
      ],
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
      title: "Neuer Prüfvorgang",
      framework: framework,
      timestamp: "Gerade eben",
      messages: [],
    };
    setThreads([newThread, ...threads]);
    setActiveThreadId(newId);
    setSelectedCitation(null);
  };

  const handleSendQuery = async (customPrompt?: string) => {
    const promptToSend = (customPrompt || query).trim();
    if (!promptToSend) return;

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
      let resultText = "";
      let citationsList: AuditCitationResponse[] = [];

      if (documentId) {
        const res = await auditDocument(documentId, promptToSend, framework);
        resultText = res.finding_summary;
        citationsList = res.citations || [];
      } else {
        // Fallback demo response
        resultText =
          "• [SOURCE_1]: Gemäß DORA Art. 30 Abs. 2 ist eine Ausstiegsfrist von 60 Tagen mit garantierter Migrationsunterstützung geregelt.\n• [SOURCE_2]: Der IKT-Dienstleister ist verpflichtet, Datenbestände geordnet und ohne Unterbrechung des Geschäftsbetriebs zu übergeben.";
        citationsList = [
          {
            source_tag: "[SOURCE_1]",
            page_number: 2,
            bounding_box: [50, 115, 528, 203],
            content: "Kündigungsfrist von 60 Tagen mit 90 Tagen Migrationsunterstützung.",
          },
        ];
      }

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
            <span>Neuer Prüfvorgang</span>
          </button>

          {/* Framework Switcher */}
          <div className="space-y-1.5">
            <span className="text-[10px] font-mono font-bold uppercase tracking-wider text-[var(--foreground)] opacity-50 px-1">
              Aufsichtsrahmen (Framework)
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
            <span className="text-[10px] font-mono font-bold uppercase tracking-wider text-[var(--foreground)] opacity-50 px-1 flex items-center gap-1.5">
              <Clock className="w-3 h-3 text-[var(--accent-tangerine)]" />
              <span>Prüfhistorie ({threads.length})</span>
            </span>
            <div className="space-y-1 pt-1">
              {threads.map((item) => {
                const isActive = item.id === activeThreadId;
                return (
                  <button
                    key={item.id}
                    onClick={() => {
                      setActiveThreadId(item.id);
                      setSelectedCitation(item.messages.find((m) => m.citations?.length)?.citations?.[0] || null);
                    }}
                    className={`w-full text-left p-2.5 rounded-xl text-xs font-mono transition-all cursor-pointer border ${
                      isActive
                        ? "bg-[var(--surface-card)] border-[var(--accent-tangerine)] text-[var(--foreground)] font-bold shadow-sm"
                        : "border-transparent text-[var(--foreground)] opacity-65 hover:opacity-100 hover:bg-[var(--surface-card)]/50"
                    }`}
                  >
                    <div className="flex items-center justify-between mb-1">
                      <span className="text-[9px] px-1.5 py-0.2 rounded bg-[var(--surface-dark)] border border-[var(--surface-border)] text-[var(--accent-tangerine)] font-bold">
                        {item.framework}
                      </span>
                      <span className="text-[9px] opacity-40">{item.timestamp}</span>
                    </div>
                    <p className="truncate text-[11px]">{item.title}</p>
                  </button>
                );
              })}
            </div>
          </div>

          {/* Prompt Library Presets */}
          <div className="space-y-1.5 pt-3 border-t border-[var(--surface-border)]">
            <span className="text-[10px] font-mono font-bold uppercase tracking-wider text-[var(--foreground)] opacity-50 px-1 flex items-center gap-1.5">
              <Sparkles className="w-3 h-3 text-[var(--accent-cyan)]" />
              <span>Standard-Prüffragen</span>
            </span>
            <div className="space-y-1">
              {PRESET_PROMPTS.map((p, idx) => (
                <button
                  key={idx}
                  onClick={() => handleSendQuery(p.prompt)}
                  className="w-full text-left p-2 rounded-lg bg-[var(--surface-card)] hover:bg-[var(--surface-dark)] border border-[var(--surface-border)] hover:border-[var(--accent-cyan)] text-[10.5px] font-mono text-[var(--foreground)] opacity-75 hover:opacity-100 transition-all cursor-pointer truncate"
                  title={p.prompt}
                >
                  {p.label}
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Sidebar Footer */}
        <div className="p-3 border-t border-[var(--surface-border)] text-[10px] font-mono text-[var(--foreground)] opacity-60 flex items-center justify-between">
          <span className="flex items-center gap-1.5">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-400"></span>
            KI-Audit Engine v0.2
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
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-lg bg-[var(--accent-tangerine)]/15 border border-[var(--accent-tangerine)]/30 flex items-center justify-center text-[var(--accent-tangerine)] shrink-0">
              <Scale className="w-4 h-4 stroke-[2.5]" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h2 className="font-extrabold text-xs tracking-wider uppercase font-mono text-[var(--foreground)]">
                  KI-Revisionsprüfer Studio
                </h2>
                <span className="text-[10px] font-mono px-2 py-0.5 rounded-full bg-[var(--surface-dark)] border border-[var(--surface-border)] font-bold text-[var(--accent-tangerine)]">
                  {framework} Grounded
                </span>
              </div>
              <p className="text-[11px] font-mono opacity-50 truncate max-w-[320px]">
                {documentName}
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2">
            {onSwitchToWorkbench && (
              <button
                onClick={onSwitchToWorkbench}
                className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-[var(--surface-dark)] hover:bg-[var(--surface-card)] border border-[var(--surface-border)] text-[var(--foreground)] font-mono text-xs font-bold transition-all shadow-sm cursor-pointer"
              >
                <span>Zur PDF-Prüfbank</span>
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
              <span>Prüfbericht PDF</span>
            </button>
          </div>
        </div>

        {/* Message Thread */}
        <div className="flex-1 overflow-auto p-6 space-y-6">
          {activeThread.messages.length === 0 ? (
            <div className="h-full flex flex-col items-center justify-center text-center p-8 max-w-lg mx-auto">
              <div className="w-16 h-16 rounded-2xl bg-[var(--accent-tangerine)]/10 border border-[var(--accent-tangerine)]/30 flex items-center justify-center text-[var(--accent-tangerine)] mb-4 shadow-md">
                <Bot className="w-8 h-8" />
              </div>
              <h3 className="font-extrabold text-sm font-mono uppercase tracking-wide text-[var(--foreground)] mb-2">
                Rechtskonforme BaFin & DORA Prüfinstanz
              </h3>
              <p className="text-xs text-[var(--foreground)] opacity-60 leading-relaxed font-sans mb-6">
                Stellen Sie konkrete Prüffragen zu Ausstiegsfristen, Haftungsobergrenzen,
                ZUGFeRD 2.3 E-Rechnungen oder BDSG § 26 Datenschutzstandards.
              </p>
              <div className="grid grid-cols-2 gap-2 w-full text-left">
                {PRESET_PROMPTS.slice(0, 4).map((p, idx) => (
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
            </div>
          ) : (
            activeThread.messages.map((msg) => {
              const isUser = msg.sender === "user";
              const isTranslated = translatedMap[msg.id] || false;
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
                          <span>{framework} Geprüft (Audit Evidence)</span>
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
                            <span>{isTranslated ? "Auf Deutsch 🇩🇪" : "Translate to English 🇬🇧"}</span>
                          </button>

                          <button
                            onClick={() => handleCopyText(displayedText, msg.id)}
                            className="text-[var(--foreground)] opacity-50 hover:opacity-100 p-1 rounded hover:bg-[var(--surface-dark)] cursor-pointer"
                            title="Befund kopieren"
                          >
                            {copiedId === msg.id ? (
                              <Check className="w-3.5 h-3.5 text-emerald-400" />
                            ) : (
                              <Copy className="w-3.5 h-3.5" />
                            )}
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
                          Geprüfte Belegstellen im Vertrag:
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
                              <span className="opacity-70 text-[9.5px]">S. {c.page_number}</span>
                            </button>
                          ))}
                        </div>
                      </div>
                    )}

                    <div className="text-[9.5px] font-mono opacity-40 text-right">
                      {msg.timestamp}
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
                onChange={(e) => setQuery(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === "Enter" && !e.shiftKey) {
                    e.preventDefault();
                    handleSendQuery();
                  }
                }}
                placeholder={`Frage zu ${framework} oder Vertragsklauseln eingeben (z. B. 'Wie hoch ist die maximale Verzugsstrafe?')...`}
                rows={2}
                className="w-full bg-[var(--surface-dark)] border border-[var(--surface-border)] focus:border-[var(--accent-tangerine)] rounded-xl px-4 py-3 pr-12 text-xs text-[var(--foreground)] font-mono leading-relaxed focus:outline-none resize-none shadow-inner transition-colors"
              />
              <button
                onClick={() => handleSendQuery()}
                disabled={!query.trim() || loading}
                className="absolute right-3 bottom-3 p-2 rounded-lg bg-[var(--accent-tangerine)] hover:opacity-90 disabled:opacity-30 text-[var(--accent-contrast)] transition-all shadow-sm cursor-pointer"
              >
                <Send className="w-4 h-4 stroke-[2.5]" />
              </button>
            </div>
            <p className="text-[10px] font-mono text-[var(--foreground)] opacity-50 text-center">
              Revisionssicher gem. BaFin Rundschreiben & DORA Art. 30 · Zero Hallucination Standard.
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
                Prüfbeleg & Kontext
              </span>
            </div>
            <span className="text-[9.5px] font-mono text-emerald-500 bg-emerald-500/10 px-2 py-0.5 rounded border border-emerald-500/25 font-bold">
              VERIFIZIERT
            </span>
          </div>

          {selectedCitation ? (
            <div className="p-4 rounded-xl bg-[var(--surface-card)] border border-[var(--surface-border)] space-y-3 shadow-md animate-in fade-in duration-150">
              <div className="flex items-center justify-between text-xs font-mono">
                <span className="px-2 py-0.5 rounded bg-[var(--accent-tangerine)]/15 text-[var(--accent-tangerine)] border border-[var(--accent-tangerine)]/30 font-bold">
                  {selectedCitation.source_tag}
                </span>
                <span className="opacity-60 text-[11px]">
                  Seite {selectedCitation.page_number}
                </span>
              </div>

              <div>
                <span className="text-[10px] font-mono uppercase tracking-wider text-[var(--foreground)] opacity-50 font-bold block mb-1">
                  Visuelle DIN A4 Koordinaten:
                </span>
                <span className="font-mono text-xs text-[var(--accent-cyan)] bg-[var(--surface-dark)] px-2 py-1 rounded border border-[var(--surface-border)] block">
                  📍 [{Math.round(selectedCitation.bounding_box?.[0] || 0)}, {Math.round(selectedCitation.bounding_box?.[1] || 0)}, {Math.round(selectedCitation.bounding_box?.[2] || 0)}, {Math.round(selectedCitation.bounding_box?.[3] || 0)}]
                </span>
              </div>

              <div>
                <span className="text-[10px] font-mono uppercase tracking-wider text-[var(--foreground)] opacity-50 font-bold block mb-1">
                  Originaltext (Authentischer Wortlaut):
                </span>
                <div className="p-3 rounded-lg bg-[var(--surface-dark)] border-l-2 border-[var(--accent-tangerine)] border-r border-t border-b border-[var(--surface-border)] text-xs font-sans text-[var(--foreground)] leading-relaxed">
                  "{selectedCitation.content}"
                </div>
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
                  <span>In PDF-Prüfbank Anspringen</span>
                  <ArrowUpRight className="w-3.5 h-3.5" />
                </button>
              )}
            </div>
          ) : (
            <div className="p-6 rounded-xl bg-[var(--surface-card)] border border-[var(--surface-border)] text-center text-xs font-mono opacity-60 space-y-2">
              <ShieldCheck className="w-8 h-8 mx-auto text-[var(--accent-tangerine)] opacity-60" />
              <p className="font-bold">Kein Beleg ausgewählt</p>
              <p className="text-[11px]">
                Klicken Sie auf ein [SOURCE_X] Tag im Chat, um die exakte Textstelle und
                Koordinaten einzusehen.
              </p>
            </div>
          )}

          {/* Active Contract Info */}
          <div className="p-3.5 rounded-xl bg-[var(--surface-card)] border border-[var(--surface-border)] space-y-2 font-mono text-[11px] shadow-sm">
            <span className="text-[10px] uppercase tracking-wider opacity-50 font-bold block">
              Geprüfter Master-Vertrag:
            </span>
            <div className="truncate font-bold text-[var(--foreground)]">
              {documentName}
            </div>
            <div className="text-[10px] opacity-60">
              DIN 66399 Schutzklasse 3 · BaFin Audit-Prüfstrom aktiv
            </div>
          </div>
        </div>
      </aside>
    </div>
  );
}

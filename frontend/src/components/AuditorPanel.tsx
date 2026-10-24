"use client";

import React, { useState, useRef, useEffect } from "react";
import {
  Send,
  CheckCircle,
  ExternalLink,
  Scale,
  Loader2,
  AlertCircle,
  User,
  Bot,
  Sparkles,
  Languages,
} from "lucide-react";
import { auditDocument, AuditApiResponse, AuditCitationResponse } from "@/lib/api";
import { Language, translations } from "@/lib/i18n";
import { translateGermanToEnglish } from "@/lib/translator";

export interface CitationItem {
  id: string;
  source_tag: string;
  page_number: number;
  box: [number, number, number, number];
  snippet: string;
}

interface AuditMessage {
  id: string;
  question: string;
  framework: string;
  finding_summary: string;
  citations: AuditCitationResponse[];
  timestamp: string;
}

interface AuditPanelProps {
  lang?: Language;
  documentId?: string | null;
  onSelectCitation: (citation: CitationItem) => void;
  floating?: boolean;
  onClose?: () => void;
}

export function AuditPanel({
  lang = "DE",
  documentId,
  onSelectCitation,
  floating = false,
  onClose,
}: AuditPanelProps) {
  const t = translations[lang];
  const [mode, setMode] = useState<"DORA" | "LkSG" | "ZUGFeRD">("DORA");
  const [query, setQuery] = useState("");
  const [loading, setLoading] = useState(false);
  const [messages, setMessages] = useState<AuditMessage[]>([]);
  const [auditError, setAuditError] = useState<string | null>(null);
  const [translatedMap, setTranslatedMap] = useState<Record<string, boolean>>({});
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages, loading]);

  const toggleTranslate = (msgId: string) => {
    setTranslatedMap((prev) => ({
      ...prev,
      [msgId]: !prev[msgId],
    }));
  };

  const executeAudit = async (searchQuery: string) => {
    if (!searchQuery.trim()) return;
    if (!documentId) {
      setAuditError(
        lang === "DE"
          ? "Bitte zuerst ein Dokument hochladen oder aus der Liste wählen."
          : "Please upload or select a PDF document first."
      );
      return;
    }

    setLoading(true);
    setAuditError(null);
    const userQuestion = searchQuery.trim();
    setQuery("");

    try {
      const result = await auditDocument(documentId, userQuestion, mode);
      const newMessage: AuditMessage = {
        id: `msg-${Date.now()}`,
        question: userQuestion,
        framework: result.framework,
        finding_summary: result.finding_summary,
        citations: result.citations,
        timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
      };
      setMessages((prev) => [...prev, newMessage]);
    } catch (err: any) {
      console.error("Audit error:", err);
      setAuditError(err.message || "Failed to execute audit inquiry.");
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      executeAudit(query);
    }
  };

  const panelClasses = floating
    ? "w-[400px] max-h-[600px] flex flex-col rounded-2xl bg-[var(--surface-card)] border border-[var(--surface-border)] shadow-2xl overflow-hidden backdrop-blur-xl"
    : "w-[340px] xl:w-[380px] shrink-0 flex flex-col h-full bg-[var(--surface-dark)] border-l border-[var(--surface-border)] overflow-hidden transition-all duration-200";

  return (
    <div className={panelClasses}>
      {/* Panel Header & Mode Selector */}
      <div className="p-3.5 border-b border-[var(--surface-border)] bg-[var(--surface-dark)]">
        <div className="flex items-center justify-between mb-2.5">
          <div className="flex items-center gap-2">
            <Scale className="w-3.5 h-3.5 text-[var(--accent-tangerine)]" />
            <h3 className="font-extrabold text-xs tracking-wider uppercase text-[var(--foreground)] font-mono">
              {t.audit_engine_title}
            </h3>
          </div>
          <div className="flex items-center gap-1.5">
            <span className="text-[9px] font-mono bg-emerald-500/15 text-emerald-400 px-2 py-0.5 rounded border border-emerald-500/30 font-bold flex items-center gap-1">
              <Languages className="w-3 h-3" /> DE/EN
            </span>
            {onClose && (
              <button
                onClick={onClose}
                title="Collapse Auditor Panel"
                className="w-5 h-5 rounded hover:bg-[var(--surface-card)] flex items-center justify-center text-[var(--foreground)] opacity-60 hover:opacity-100 font-mono text-xs cursor-pointer ml-1"
              >
                ✕
              </button>
            )}
          </div>
        </div>

        {/* Framework Tabs */}
        <div className="grid grid-cols-3 gap-1 bg-[var(--surface-card)] p-1 rounded-md border border-[var(--surface-border)]">
          {(["DORA", "LkSG", "ZUGFeRD"] as const).map((tab) => (
            <button
              key={tab}
              onClick={() => setMode(tab)}
              className={`py-1 text-xs font-mono font-bold rounded transition-all cursor-pointer ${
                mode === tab
                  ? "bg-[var(--accent-tangerine)] text-[var(--accent-contrast)] shadow-sm"
                  : "text-[var(--foreground)] opacity-60 hover:opacity-100"
              }`}
            >
              {tab === "DORA" ? "DORA (ICT)" : tab === "LkSG" ? "LkSG (Supply)" : "ZUGFeRD"}
            </button>
          ))}
        </div>
      </div>

      {/* Audit Findings Thread */}
      <div ref={scrollRef} className="flex-1 overflow-auto p-4 space-y-4">
        {auditError && (
          <div className="p-3 rounded-lg bg-rose-500/10 border border-rose-500/30 text-xs text-rose-500 flex items-center gap-2 font-mono">
            <AlertCircle className="w-4 h-4 flex-shrink-0" />
            <span>{auditError}</span>
          </div>
        )}

        {/* Empty State Welcome */}
        {messages.length === 0 && !loading && (
          <div className="p-6 rounded-xl bg-[var(--surface-card)] border border-[var(--surface-border)] text-xs text-[var(--foreground)] opacity-75 text-center space-y-2.5 shadow-sm">
            <div className="w-10 h-10 rounded-xl bg-[var(--accent-tangerine)]/10 border border-[var(--accent-tangerine)]/30 flex items-center justify-center mx-auto text-[var(--accent-tangerine)] shadow-sm">
              <Bot className="w-5 h-5 text-[var(--accent-tangerine)]" />
            </div>
            <p className="font-bold text-[var(--foreground)] font-mono text-xs uppercase tracking-wide">
              {t.audit_ready_title}
            </p>
            <p className="text-[11px] opacity-70 leading-relaxed max-w-[300px] mx-auto font-sans">
              {t.audit_ready_desc}
            </p>
          </div>
        )}

        {/* Conversation History */}
        {messages.map((msg) => {
          // If lang is EN, default to English unless toggled. If lang is DE, default to German.
          const isTranslated =
            translatedMap[msg.id] !== undefined
              ? translatedMap[msg.id]
              : lang === "EN";

          const displayedSummary = isTranslated
            ? translateGermanToEnglish(msg.finding_summary)
            : msg.finding_summary;

          return (
            <div key={msg.id} className="space-y-2.5 animate-in fade-in duration-200">
              {/* User Question */}
              <div className="flex items-start gap-2 justify-end">
                <div className="bg-[var(--surface-card)] border border-[var(--accent-tangerine)]/40 text-[var(--foreground)] font-medium rounded-2xl rounded-tr-sm px-3.5 py-2.5 text-xs max-w-[85%] shadow-sm leading-relaxed">
                  <p>{msg.question}</p>
                  <span className="text-[9px] font-mono opacity-50 block text-right mt-1">
                    {msg.timestamp}
                  </span>
                </div>
                <div className="w-6 h-6 rounded-full bg-[var(--accent-tangerine)]/15 border border-[var(--accent-tangerine)]/40 flex items-center justify-center flex-shrink-0">
                  <User className="w-3.5 h-3.5 text-[var(--accent-tangerine)]" />
                </div>
              </div>

              {/* AI Audit Finding Card */}
              <div className="flex items-start gap-2">
                <div className="w-6 h-6 rounded-full bg-[var(--surface-card)] border border-[var(--surface-border)] flex items-center justify-center flex-shrink-0 mt-1">
                  <Bot className="w-3.5 h-3.5 text-[var(--accent-tangerine)]" />
                </div>
                <div className="flex-1 p-3.5 rounded-xl bg-[var(--surface-card)] border border-[var(--surface-border)] border-l-2 border-l-[var(--accent-tangerine)] space-y-2.5 shadow-md">
                  <div className="flex items-center justify-between border-b border-[var(--surface-border)] pb-2">
                    <span className="text-xs font-bold text-[var(--accent-lime)] flex items-center gap-1.5 font-mono">
                      <CheckCircle className="w-3.5 h-3.5 text-[var(--accent-lime)]" /> {msg.framework} Verified
                    </span>

                    {/* Instant German <-> English Translation Toggle */}
                    <button
                      onClick={() => toggleTranslate(msg.id)}
                      className="flex items-center gap-1 text-[10px] font-mono px-2 py-0.5 rounded bg-[var(--surface-dark)] border border-[var(--surface-border)] hover:border-[var(--accent-tangerine)] text-[var(--accent-tangerine)] font-bold transition-all cursor-pointer shadow-sm"
                      title="Convert German legal text to English for international compliance"
                    >
                      <Languages className="w-3 h-3" />
                      <span>{isTranslated ? "Auf Deutsch 🇩🇪" : "Translate to English 🇬🇧"}</span>
                    </button>
                  </div>

                  <p className="text-xs text-[var(--foreground)] leading-relaxed whitespace-pre-line font-sans">
                    {displayedSummary}
                  </p>

                  {/* Interactive Citations */}
                  {msg.citations && msg.citations.length > 0 && (
                    <div className="pt-2 space-y-1.5 border-t border-[var(--surface-border)]">
                      <div className="flex items-center justify-between text-[10px] font-mono font-bold text-[var(--foreground)] opacity-60 uppercase tracking-wider">
                        <span>
                          {lang === "DE" ? "GEPRÜFTE BELEGE (AUDIT EVIDENCE)" : "VERIFIED AUDIT EVIDENCE"}
                        </span>
                        <span className="text-[9px] text-[var(--accent-cyan)] font-mono">
                          {isTranslated ? "EN Translated" : "DE Original"}
                        </span>
                      </div>

                      {msg.citations.map((citation, idx) => (
                        <button
                          key={idx}
                          onClick={() =>
                            onSelectCitation({
                              id: citation.chunk_id || `cit-${idx}`,
                              source_tag: citation.source_tag,
                              page_number: citation.page_number,
                              box:
                                (citation.bounding_box as [number, number, number, number]) || [
                                  40, 160, 560, 220,
                                ],
                              snippet: citation.content || "",
                            })
                          }
                          className="group flex items-center gap-2 px-3 py-2 rounded-md bg-[var(--accent-tangerine)]/10 border border-[var(--accent-tangerine)]/30 hover:border-[var(--accent-tangerine)] hover:bg-[var(--accent-tangerine)]/20 text-[var(--accent-tangerine)] text-xs transition-all w-full text-left shadow-sm cursor-pointer"
                        >
                          <span className="font-black font-mono text-[9px] bg-[var(--accent-tangerine)] text-[var(--accent-contrast)] px-1.5 py-0.5 rounded shadow">
                            {citation.source_tag}
                          </span>
                          <span className="truncate flex-1 text-[11px] text-[var(--foreground)] opacity-80 group-hover:opacity-100 font-mono">
                            Page {citation.page_number} • Reveal Laser Bounding Box
                          </span>
                          <ExternalLink className="w-3.5 h-3.5 text-[var(--accent-tangerine)] opacity-70 group-hover:opacity-100" />
                        </button>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            </div>
          );
        })}

        {/* Loading Spinner */}
        {loading && (
          <div className="p-3.5 rounded-xl bg-[var(--surface-card)] border border-[var(--surface-border)] flex items-center gap-3 text-[var(--foreground)]">
            <Loader2 className="w-4 h-4 animate-spin text-[var(--accent-tangerine)]" />
            <p className="text-xs font-mono opacity-80">
              {lang === "DE"
                ? "Führe pgvector-Kosinus-Prüfung durch..."
                : "pgvector Cosine Search in progress..."}
            </p>
          </div>
        )}

        {/* Quick Audit Prompt Suggestions */}
        <div className="pt-2 space-y-2">
          <p className="text-[10px] font-mono font-bold text-[var(--foreground)] opacity-60 uppercase tracking-wider flex items-center gap-1.5">
            <Sparkles className="w-3 h-3 text-[var(--accent-tangerine)]" />
            {t.suggested_checks_title}
          </p>
          <div className="space-y-1.5">
            {[t.suggested_1, t.suggested_2, t.suggested_3].map((suggested, idx) => (
              <button
                key={idx}
                onClick={() => executeAudit(suggested)}
                className="w-full text-[11px] text-[var(--foreground)] opacity-80 hover:opacity-100 bg-[var(--surface-card)] hover:bg-[var(--surface-dark)] border border-[var(--surface-border)] hover:border-[var(--accent-tangerine)]/60 rounded-md px-3 py-2 text-left transition-all font-mono shadow-sm flex items-center justify-between cursor-pointer group"
              >
                <span className="truncate">{suggested}</span>
                <span className="text-[var(--accent-tangerine)] opacity-0 group-hover:opacity-100 font-bold ml-2">→</span>
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Query Input Box */}
      <div className="p-3.5 border-t border-[var(--surface-border)] bg-[var(--surface-dark)]">
        <div className="relative">
          <textarea
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder={t.input_placeholder}
            rows={3}
            className="w-full bg-[var(--surface-card)] border border-[var(--surface-border)] focus:border-[var(--accent-tangerine)] rounded-lg px-3 py-2.5 text-xs text-[var(--foreground)] placeholder:opacity-40 focus:outline-none resize-none transition-colors font-mono leading-relaxed"
          />
          <button
            onClick={() => executeAudit(query)}
            disabled={!query.trim() || loading}
            className="absolute right-2.5 bottom-3.5 p-2 rounded-md bg-[var(--accent-tangerine)] hover:opacity-90 disabled:opacity-40 text-[var(--accent-contrast)] font-black transition-all shadow-sm cursor-pointer"
          >
            {loading ? (
              <Loader2 className="w-3.5 h-3.5 animate-spin" />
            ) : (
              <Send className="w-3.5 h-3.5 stroke-[2.5]" />
            )}
          </button>
        </div>
      </div>
    </div>
  );
}

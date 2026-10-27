"use client";

import React, { useState, useEffect, useRef } from "react";
import {
  Search,
  Command,
  FileText,
  Shield,
  ShieldCheck,
  Network,
  FileSpreadsheet,
  Bot,
  Award,
  Languages,
  ArrowRight,
  Sparkles,
  ExternalLink,
  X,
} from "lucide-react";
import { Language } from "@/lib/i18n";

interface CommandItem {
  id: string;
  title_de: string;
  title_en: string;
  category: "navigation" | "regulatory" | "document";
  icon: React.ComponentType<{ className?: string }>;
  shortcut?: string;
  action: () => void;
}

interface CommandPaletteProps {
  isOpen: boolean;
  onClose: () => void;
  lang: Language;
  onToggleLang: () => void;
  onOpenWorkbench: () => void;
  onOpenAuditor: () => void;
  onOpenDoraExit: () => void;
  onOpenDoraSubcontractor: () => void;
  onOpenAuditRights: () => void;
  onOpenRemediation?: () => void;
  onOpenZugferd: () => void;
  onOpenCertificate: () => void;
  availableDocuments?: any[];
  onSelectDocument?: (doc: any) => void;
}

export function CommandPalette({
  isOpen,
  onClose,
  lang,
  onToggleLang,
  onOpenWorkbench,
  onOpenAuditor,
  onOpenDoraExit,
  onOpenDoraSubcontractor,
  onOpenAuditRights,
  onOpenRemediation,
  onOpenZugferd,
  onOpenCertificate,
  availableDocuments = [],
  onSelectDocument,
}: CommandPaletteProps) {
  const [query, setQuery] = useState("");
  const [selectedIndex, setSelectedIndex] = useState(0);
  const inputRef = useRef<HTMLInputElement>(null);
  const isDe = lang === "DE";

  // Focus input whenever opened
  useEffect(() => {
    if (isOpen) {
      setQuery("");
      setSelectedIndex(0);
      setTimeout(() => inputRef.current?.focus(), 50);
    }
  }, [isOpen]);

  // Base Commands
  const baseCommands: CommandItem[] = [
    {
      id: "nav-auditor",
      title_de: "KI-Auditor Studio öffnen (Gemini 2.0 Flash)",
      title_en: "Open AI Compliance Auditor Studio (Gemini 2.0)",
      category: "navigation",
      icon: Bot,
      shortcut: "G A",
      action: () => {
        onOpenAuditor();
        onClose();
      },
    },
    {
      id: "nav-workbench",
      title_de: "PDF-Prüfbank (Split Dual-Workbench)",
      title_en: "PDF Workbench (Dual-Screen Dossier)",
      category: "navigation",
      icon: FileText,
      shortcut: "G W",
      action: () => {
        onOpenWorkbench();
        onClose();
      },
    },
    {
      id: "reg-dora-exit",
      title_de: "DORA Art. 30(2) Exit-Strategie & Fristen Inspektor",
      title_en: "DORA Art. 30(2) Exit Strategy & Notice Inspector",
      category: "regulatory",
      icon: Shield,
      shortcut: "D E",
      action: () => {
        onOpenDoraExit();
        onClose();
      },
    },
    {
      id: "reg-dora-subcontractor",
      title_de: "DORA Art. 30(3) Sub-Outsourcing & Kaskaden-Risiko",
      title_en: "DORA Art. 30(3) 4th-Party Cascading Risk Graph",
      category: "regulatory",
      icon: Network,
      shortcut: "D S",
      action: () => {
        onOpenDoraSubcontractor();
        onClose();
      },
    },
    {
      id: "reg-dora-audit-rights",
      title_de: "KWG § 25b & DORA Art. 30(3)(e) Aufsichtliche Prüfrechte & DIN 5008 Brief",
      title_en: "KWG § 25b & DORA Art. 30(3)(e) Supervisory Audit Rights & DIN 5008 Letter",
      category: "regulatory",
      icon: ShieldCheck,
      shortcut: "D A",
      action: () => {
        onOpenAuditRights();
        onClose();
      },
    },
    {
      id: "reg-remediation",
      title_de: "BGB § 311 Vertragsnachbesserung & Redline-Diff (Musterklauseln)",
      title_en: "BGB § 311 Contract Amendment & Redline Diff (Standard Clauses)",
      category: "regulatory",
      icon: Sparkles,
      shortcut: "B R",
      action: () => {
        if (onOpenRemediation) onOpenRemediation();
        onClose();
      },
    },
    {
      id: "reg-zugferd",
      title_de: "ZUGFeRD 2.3 XML / Factur-X Rechnungsprüfer 2025",
      title_en: "ZUGFeRD 2.3 XML / Factur-X E-Invoice Inspector",
      category: "regulatory",
      icon: FileSpreadsheet,
      shortcut: "Z U",
      action: () => {
        onOpenZugferd();
        onClose();
      },
    },
    {
      id: "reg-certificate",
      title_de: "Revisionssicheres DIN A4 Audit-Zertifikat drucken",
      title_en: "Print Certified DIN A4 Compliance Certificate",
      category: "regulatory",
      icon: Award,
      shortcut: "⌘ P",
      action: () => {
        onOpenCertificate();
        onClose();
      },
    },
    {
      id: "nav-lang",
      title_de: "Sprache umschalten (Deutsch ↔ English)",
      title_en: "Switch Language (English ↔ Deutsch)",
      category: "navigation",
      icon: Languages,
      shortcut: "⌘ L",
      action: () => {
        onToggleLang();
        onClose();
      },
    },
  ];

  // Document commands
  const documentCommands: CommandItem[] = availableDocuments.map((doc) => ({
    id: `doc-${doc.id}`,
    title_de: `Vertrag: ${doc.title || doc.filename || "Dokument"}`,
    title_en: `Contract: ${doc.title || doc.filename || "Document"}`,
    category: "document",
    icon: FileText,
    action: () => {
      if (onSelectDocument) onSelectDocument(doc);
      onOpenWorkbench();
      onClose();
    },
  }));

  const allItems = [...baseCommands, ...documentCommands];

  // Filter items
  const filteredItems = allItems.filter((item) => {
    const title = isDe ? item.title_de : item.title_en;
    return title.toLowerCase().includes(query.toLowerCase());
  });

  // Keyboard navigation
  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "ArrowDown") {
      e.preventDefault();
      setSelectedIndex((prev) => (prev + 1) % (filteredItems.length || 1));
    } else if (e.key === "ArrowUp") {
      e.preventDefault();
      setSelectedIndex((prev) => (prev - 1 + filteredItems.length) % (filteredItems.length || 1));
    } else if (e.key === "Enter" && filteredItems[selectedIndex]) {
      e.preventDefault();
      filteredItems[selectedIndex].action();
    } else if (e.key === "Escape") {
      onClose();
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-start justify-center pt-24 px-4 bg-slate-950/70 backdrop-blur-md animate-in fade-in duration-150">
      <div
        className="w-full max-w-xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl shadow-2xl overflow-hidden ring-1 ring-black/10"
        onKeyDown={handleKeyDown}
      >
        {/* Input Bar (Silicon Valley Raycast/Linear Style) */}
        <div className="flex items-center gap-3 px-4 py-3.5 border-b border-slate-200 dark:border-slate-800 bg-slate-50/50 dark:bg-slate-900/50">
          <Search className="w-5 h-5 text-slate-400 shrink-0" />
          <input
            ref={inputRef}
            type="text"
            value={query}
            onChange={(e) => {
              setQuery(e.target.value);
              setSelectedIndex(0);
            }}
            placeholder={
              isDe
                ? "Befehl, Modul oder Vertrag suchen... (z. B. 'DORA', 'ZUGFeRD', 'Auditor')"
                : "Type a command, module, or contract... (e.g. 'DORA', 'ZUGFeRD', 'Auditor')"
            }
            className="flex-1 bg-transparent text-sm text-slate-900 dark:text-white placeholder:text-slate-400 focus:outline-none font-sans"
          />
          <div className="flex items-center gap-1.5 text-[10px] font-mono text-slate-400 bg-slate-200 dark:bg-slate-800 px-2 py-0.5 rounded">
            <span>ESC</span>
          </div>
        </div>

        {/* Results List */}
        <div className="max-h-80 overflow-y-auto p-2 space-y-1">
          {filteredItems.length === 0 ? (
            <div className="p-8 text-center text-xs text-slate-400">
              {isDe ? "Keine passenden Befehle gefunden." : "No matching commands found."}
            </div>
          ) : (
            filteredItems.map((item, index) => {
              const Icon = item.icon;
              const isSelected = index === selectedIndex;
              return (
                <button
                  key={item.id}
                  onClick={item.action}
                  onMouseEnter={() => setSelectedIndex(index)}
                  className={`w-full flex items-center justify-between px-3 py-2.5 rounded-xl text-left text-xs transition-all ${
                    isSelected
                      ? "bg-purple-600 text-white shadow-sm"
                      : "text-slate-700 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800/60"
                  }`}
                >
                  <div className="flex items-center gap-2.5 truncate">
                    <Icon
                      className={`w-4 h-4 shrink-0 ${
                        isSelected ? "text-white" : "text-purple-500"
                      }`}
                    />
                    <span className="font-medium truncate">
                      {isDe ? item.title_de : item.title_en}
                    </span>
                  </div>

                  <div className="flex items-center gap-2 text-[10px] font-mono shrink-0">
                    {item.shortcut && (
                      <span
                        className={`px-1.5 py-0.5 rounded ${
                          isSelected
                            ? "bg-purple-700 text-purple-100"
                            : "bg-slate-100 dark:bg-slate-800 text-slate-400"
                        }`}
                      >
                        {item.shortcut}
                      </span>
                    )}
                    <ArrowRight
                      className={`w-3.5 h-3.5 transition-transform ${
                        isSelected ? "translate-x-0.5 text-white" : "opacity-0"
                      }`}
                    />
                  </div>
                </button>
              );
            })
          )}
        </div>

        {/* Footer Shortcut Bar */}
        <div className="flex items-center justify-between px-4 py-2 border-t border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-900/60 text-[10px] font-mono text-slate-400">
          <div className="flex items-center gap-3">
            <span>↑↓ {isDe ? "Navigieren" : "Navigate"}</span>
            <span>↵ {isDe ? "Auswählen" : "Select"}</span>
          </div>
          <span className="flex items-center gap-1 text-purple-600 dark:text-purple-400 font-bold">
            <Sparkles className="w-3 h-3" />
            DocuNorm Silicon Valley Spotlight
          </span>
        </div>
      </div>
    </div>
  );
}

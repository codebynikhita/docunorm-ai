"use client";

import React from "react";
import {
  Shield,
  FileText,
  FileSpreadsheet,
  History,
  Layers,
  Cpu,
  Bot,
} from "lucide-react";

import { Language, translations } from "@/lib/i18n";

interface SidebarProps {
  lang: Language;
  activeTab: "documents" | "dora" | "lksg" | "zugferd" | "audit_log" | "auditor";
  onTabChange: (tab: "documents" | "dora" | "lksg" | "zugferd" | "audit_log" | "auditor") => void;
  documentCount: number;
}

export function Sidebar({ lang, activeTab, onTabChange, documentCount }: SidebarProps) {
  const t = translations[lang];

  const navItems = [
    {
      id: "documents" as const,
      label: t.vault_title,
      icon: FileText,
      badge: `${documentCount} PDFs`,
    },
    {
      id: "auditor" as const,
      label: lang === "DE" ? "KI-Prüfassistent" : "AI Auditor Studio",
      icon: Bot,
      badge: "Studio",
    },
    {
      id: "dora" as const,
      label: t.dora_title,
      icon: Shield,
      badge: "IKT-Risk",
    },
    {
      id: "zugferd" as const,
      label: t.zugferd_title,
      icon: FileSpreadsheet,
      badge: "EN 16931",
    },
    {
      id: "lksg" as const,
      label: t.lksg_title,
      icon: Layers,
      badge: "Sorgfalt",
    },
    {
      id: "audit_log" as const,
      label: t.ledger_title,
      icon: History,
      badge: lang === "DE" ? "Unveränderbar" : "Immutable",
    },
  ];

  return (
    <aside className="w-56 shrink-0 bg-[var(--surface-dark)] border-r border-[var(--surface-border)] flex flex-col justify-between select-none transition-all duration-200">
      <div className="p-3.5 space-y-5">
        {/* Navigation Category */}
        <div className="space-y-1">
          <p className="text-[10px] font-mono font-bold uppercase tracking-wider text-[var(--foreground)] opacity-50 px-3 pb-1 flex items-center justify-between">
            <span>{lang === "DE" ? "Prüfmodule" : "Audit Modules"}</span>
            <span className="w-1.5 h-1.5 rounded-full bg-[var(--accent-tangerine)]"></span>
          </p>
          <nav className="space-y-1">
            {navItems.map((item) => {
              const Icon = item.icon;
              const isActive = activeTab === item.id;
              return (
                <button
                  key={item.id}
                  onClick={() => onTabChange(item.id)}
                  className={`w-full flex items-center justify-between px-3 py-2 rounded-md text-xs font-mono transition-all cursor-pointer ${
                    isActive
                      ? "bg-[var(--surface-card)] border-l-2 border-[var(--accent-tangerine)] text-[var(--foreground)] font-bold shadow-sm"
                      : "text-[var(--foreground)] opacity-65 hover:opacity-100 hover:bg-[var(--surface-card)]/50 border-l-2 border-transparent"
                  }`}
                >
                  <div className="flex items-center gap-2.5">
                    <Icon
                      className={`w-3.5 h-3.5 transition-colors ${
                        isActive ? "text-[var(--accent-tangerine)]" : "opacity-60"
                      }`}
                    />
                    <span className="text-[11px] truncate">{item.label}</span>
                  </div>
                  <span
                    className={`text-[9px] font-mono px-1.5 py-0.5 rounded ${
                      isActive
                        ? "bg-[var(--accent-tangerine)]/15 text-[var(--accent-tangerine)] border border-[var(--accent-tangerine)]/30 font-bold"
                        : "bg-[var(--surface-card)] text-[var(--foreground)] opacity-60 border border-[var(--surface-border)]"
                    }`}
                  >
                    {item.badge}
                  </span>
                </button>
              );
            })}
          </nav>
        </div>

        {/* Live German Telemetry Card */}
        <div className="bg-[var(--surface-card)] border border-[var(--surface-border)] rounded-lg p-3 space-y-2 text-[11px] font-mono shadow-sm">
          <div className="flex items-center justify-between border-b border-[var(--surface-border)] pb-1.5">
            <span className="text-[10px] font-bold text-[var(--foreground)] opacity-70 uppercase tracking-wider flex items-center gap-1.5">
              <Cpu className="w-3 h-3 text-[var(--accent-tangerine)]" />
              {t.telemetry_title}
            </span>
            <span className="flex items-center gap-1 text-[9px] text-[var(--accent-lime)] font-black tracking-wide">
              <span className="w-1.5 h-1.5 rounded-full bg-[var(--accent-lime)] animate-pulse"></span>
              LIVE
            </span>
          </div>

          <div className="space-y-1.5 pt-0.5 text-[10px]">
            <div className="flex justify-between items-center">
              <span className="text-[var(--foreground)] opacity-60">pgvector DB:</span>
              <span className="text-[var(--accent-cyan)] font-semibold">Postgres 16</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-[var(--foreground)] opacity-60">
                {lang === "DE" ? "Embedding-Modell:" : "Embedding Model:"}
              </span>
              <span className="text-[var(--accent-cyan)] font-semibold">
                {lang === "DE" ? "1024-dim Kosinus" : "1024-dim Cosine"}
              </span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-[var(--foreground)] opacity-60">BDSG / DSGVO:</span>
              <span className="text-[var(--accent-lime)] font-bold bg-[var(--accent-lime)]/10 px-1 py-0.2 rounded border border-[var(--accent-lime)]/30">
                {t.dsgvo_verified}
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Footer Info with German Legal Impressum link style */}
      <div className="p-3 border-t border-[var(--surface-border)] text-[10px] font-mono text-[var(--foreground)] opacity-60 flex items-center justify-between bg-[var(--surface-dark)]">
        <span className="flex items-center gap-1.5">
          <span className="w-1.5 h-1.5 rounded-full bg-[var(--accent-lime)]"></span>
          DocuNorm DE v0.2
        </span>
        <span className="text-[9px] bg-[var(--accent-tangerine)]/10 px-1.5 py-0.5 rounded border border-[var(--accent-tangerine)]/30 text-[var(--accent-tangerine)] font-bold tracking-wider">
          BAFIN-READY
        </span>
      </div>
    </aside>
  );
}

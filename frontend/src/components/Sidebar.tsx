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
  ChevronLeft,
  ChevronRight,
  PanelLeftClose,
  PanelLeft,
} from "lucide-react";

import { Language, translations } from "@/lib/i18n";

interface SidebarProps {
  lang: Language;
  activeTab: "documents" | "dora" | "lksg" | "zugferd" | "audit_log" | "auditor";
  onTabChange: (tab: "documents" | "dora" | "lksg" | "zugferd" | "audit_log" | "auditor") => void;
  documentCount: number;
  isCollapsed?: boolean;
  onToggleCollapse?: () => void;
}

export function Sidebar({
  lang,
  activeTab,
  onTabChange,
  documentCount,
  isCollapsed = false,
  onToggleCollapse,
}: SidebarProps) {
  const t = translations[lang];

  const navItems = [
    {
      id: "documents" as const,
      label: lang === "DE" ? "Dokumenten-Vault" : "Document Vault",
      icon: FileText,
      badge: `${documentCount} PDFs`,
    },
    {
      id: "auditor" as const,
      label: lang === "DE" ? "KI-Auditor" : "AI Auditor",
      icon: Bot,
      badge: "Studio",
    },
    {
      id: "dora" as const,
      label: "DORA Art. 30",
      icon: Shield,
      badge: "BaFin",
    },
    {
      id: "zugferd" as const,
      label: "ZUGFeRD 2.3",
      icon: FileSpreadsheet,
      badge: "Factur-X",
    },
    {
      id: "lksg" as const,
      label: lang === "DE" ? "LkSG Lieferkette" : "LkSG Supply Chain",
      icon: Layers,
      badge: "BAFA",
    },
    {
      id: "audit_log" as const,
      label: lang === "DE" ? "Audit-Log" : "Audit Ledger",
      icon: History,
      badge: lang === "DE" ? "Zertifiziert" : "Certified",
    },
  ];

  return (
    <aside
      className={`shrink-0 bg-[var(--surface-dark)] border-r border-[var(--surface-border)] flex flex-col justify-between select-none transition-all duration-200 ${
        isCollapsed ? "w-16" : "w-64"
      }`}
    >
      <div className={`${isCollapsed ? "p-2" : "p-3.5"} space-y-4`}>
        {/* Navigation Category Header & Collapse Toggle */}
        <div className="space-y-1">
          {isCollapsed ? (
            <div className="flex justify-center pb-1">
              <button
                onClick={onToggleCollapse}
                title={lang === "DE" ? "Sidebar erweitern" : "Expand Sidebar"}
                className="w-8 h-8 rounded-lg bg-[var(--surface-card)] hover:bg-[var(--surface-border)] border border-[var(--surface-border)] flex items-center justify-center text-[var(--foreground)] opacity-70 hover:opacity-100 transition-all cursor-pointer shadow-sm"
              >
                <ChevronRight className="w-4 h-4 text-[var(--accent-tangerine)]" />
              </button>
            </div>
          ) : (
            <div className="flex items-center justify-between px-3 pb-1">
              <p className="text-[10px] font-mono font-bold uppercase tracking-wider text-[var(--foreground)] opacity-50 flex items-center gap-1.5">
                <span>{lang === "DE" ? "Prüfmodule" : "Audit Modules"}</span>
                <span className="w-1.5 h-1.5 rounded-full bg-[var(--accent-tangerine)]"></span>
              </p>
              {onToggleCollapse && (
                <button
                  onClick={onToggleCollapse}
                  title={lang === "DE" ? "Sidebar einklappen" : "Collapse Sidebar"}
                  className="p-1 rounded-md hover:bg-[var(--surface-card)] text-[var(--foreground)] opacity-50 hover:opacity-100 transition-all cursor-pointer"
                >
                  <ChevronLeft className="w-3.5 h-3.5" />
                </button>
              )}
            </div>
          )}

          {/* Navigation Items */}
          <nav className="space-y-1">
            {navItems.map((item) => {
              const Icon = item.icon;
              const isActive = activeTab === item.id;
              return (
                <button
                  key={item.id}
                  onClick={() => onTabChange(item.id)}
                  title={isCollapsed ? `${item.label} (${item.badge})` : undefined}
                  className={`w-full flex items-center transition-all cursor-pointer overflow-hidden ${
                    isCollapsed
                      ? `justify-center p-2.5 rounded-lg ${
                          isActive
                            ? "bg-[var(--surface-card)] text-[var(--accent-tangerine)] border border-[var(--accent-tangerine)]/40 shadow-sm"
                            : "text-[var(--foreground)] opacity-65 hover:opacity-100 hover:bg-[var(--surface-card)]/50"
                        }`
                      : `justify-between px-3 py-2 rounded-md text-xs font-mono ${
                          isActive
                            ? "bg-[var(--surface-card)] border-l-2 border-[var(--accent-tangerine)] text-[var(--foreground)] font-bold shadow-sm"
                            : "text-[var(--foreground)] opacity-65 hover:opacity-100 hover:bg-[var(--surface-card)]/50 border-l-2 border-transparent"
                        }`
                  }`}
                >
                  <div className={`flex items-center ${isCollapsed ? "justify-center" : "gap-2 min-w-0 mr-2"}`}>
                    <Icon
                      className={`shrink-0 transition-colors ${
                        isCollapsed ? "w-4 h-4" : "w-3.5 h-3.5"
                      } ${isActive ? "text-[var(--accent-tangerine)]" : "opacity-60"}`}
                    />
                    {!isCollapsed && <span className="text-[11px] truncate">{item.label}</span>}
                  </div>
                  {!isCollapsed && (
                    <span
                      className={`text-[9px] font-mono px-1.5 py-0.5 rounded shrink-0 ${
                        isActive
                          ? "bg-[var(--accent-tangerine)]/15 text-[var(--accent-tangerine)] border border-[var(--accent-tangerine)]/30 font-bold"
                          : "bg-[var(--surface-card)] text-[var(--foreground)] opacity-60 border border-[var(--surface-border)]"
                      }`}
                    >
                      {item.badge}
                    </span>
                  )}
                </button>
              );
            })}
          </nav>
        </div>

        {/* Live German Telemetry Card */}
        {isCollapsed ? (
          <div
            className="flex flex-col items-center justify-center p-2 rounded-lg bg-[var(--surface-card)] border border-[var(--surface-border)] cursor-pointer"
            title={`${t.telemetry_title} (Postgres 16, pgvector, BDSG/DSGVO Live)`}
          >
            <Cpu className="w-4 h-4 text-[var(--accent-tangerine)] mb-1" />
            <span className="w-2 h-2 rounded-full bg-[var(--accent-lime)] animate-pulse"></span>
          </div>
        ) : (
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
        )}
      </div>

      {/* Footer Info with German Legal Impressum link style */}
      {isCollapsed ? (
        <div className="p-2 border-t border-[var(--surface-border)] flex justify-center bg-[var(--surface-dark)]">
          <span
            className="w-2 h-2 rounded-full bg-[var(--accent-lime)]"
            title="DocuNorm DE v0.2 • BAFIN-READY"
          ></span>
        </div>
      ) : (
        <div className="p-3 pl-12 border-t border-[var(--surface-border)] text-[10px] font-mono text-[var(--foreground)] opacity-60 flex items-center justify-between bg-[var(--surface-dark)] overflow-hidden">
          <span className="flex items-center gap-1.5 truncate mr-2 min-w-0">
            <span className="w-1.5 h-1.5 rounded-full bg-[var(--accent-lime)] shrink-0"></span>
            <span className="truncate">DocuNorm DE v0.2</span>
          </span>
          <span className="text-[9px] bg-[var(--accent-tangerine)]/10 px-1.5 py-0.5 rounded border border-[var(--accent-tangerine)]/30 text-[var(--accent-tangerine)] font-bold tracking-wider shrink-0">
            BAFIN-READY
          </span>
        </div>
      )}
    </aside>
  );
}

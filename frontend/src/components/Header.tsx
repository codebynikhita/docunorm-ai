import React from "react";
import {
  FileSpreadsheet,
  Lock,
  Building2,
  LayoutGrid,
  Columns3,
  Maximize2,
  Award,
  Bot,
  User,
  LogOut,
  Globe,
  PanelLeftClose,
  PanelLeft,
  Search,
} from "lucide-react";
import { Language, translations } from "@/lib/i18n";
import { UserProfile } from "@/lib/api";
import { DocuNormLogo } from "@/components/DocuNormLogo";

export type Theme = "cyber" | "bauhaus" | "terminal";
export type LayoutMode = "workbench" | "auditor" | "executive" | "focus" | "portal" | "login";

interface HeaderProps {
  lang: Language;
  onToggleLang: (newLang: Language) => void;
  theme: Theme;
  onThemeChange: (theme: Theme) => void;
  layoutMode: LayoutMode;
  onLayoutChange: (mode: LayoutMode) => void;
  onOpenCertificate?: () => void;
  onOpenZugferd?: () => void;
  user?: UserProfile | null;
  onOpenAuth?: () => void;
  onLogout?: () => void;
  isSidebarCollapsed?: boolean;
  onToggleSidebar?: () => void;
  onOpenCommandPalette?: () => void;
}

export function Header({
  lang,
  onToggleLang,
  theme,
  onThemeChange,
  layoutMode,
  onLayoutChange,
  onOpenCertificate,
  onOpenZugferd,
  user,
  onOpenAuth,
  onLogout,
  isSidebarCollapsed = false,
  onToggleSidebar,
  onOpenCommandPalette,
}: HeaderProps) {
  const t = translations[lang];

  return (
    <header className="h-14 border-b border-[var(--surface-border)] bg-[var(--surface-dark)]/95 backdrop-blur-md px-4 flex items-center justify-between sticky top-0 z-50 select-none">
      {/* 1. Left: Brand Identity & Sidebar Collapse Toggle */}
      <div className="flex items-center gap-2">
        {onToggleSidebar && layoutMode !== "portal" && layoutMode !== "login" && (
          <button
            onClick={onToggleSidebar}
            title={
              isSidebarCollapsed
                ? lang === "DE"
                  ? "Sidebar einblenden"
                  : "Expand Sidebar"
                : lang === "DE"
                ? "Sidebar einklappen"
                : "Collapse Sidebar"
            }
            className="w-8 h-8 rounded-lg bg-[var(--surface-card)] hover:bg-[var(--surface-border)] border border-[var(--surface-border)] flex items-center justify-center text-[var(--foreground)] opacity-70 hover:opacity-100 transition-all cursor-pointer mr-1"
          >
            {isSidebarCollapsed ? (
              <PanelLeft className="w-4 h-4 text-[var(--accent-tangerine)]" />
            ) : (
              <PanelLeftClose className="w-4 h-4" />
            )}
          </button>
        )}

        <button
          onClick={() => onLayoutChange("portal")}
          className="flex items-center text-left cursor-pointer group"
          title="Return to Public Portal"
        >
          <DocuNormLogo size="sm" showSubtitle={true} />
        </button>
      </div>

      {/* 2. Middle: Navigation & Layout Switcher */}
      <div className="flex items-center gap-1 bg-[var(--surface-card)] border border-[var(--surface-border)] rounded-lg p-1 font-mono text-[11px] shadow-sm shrink-0">
        <button
          onClick={() => onLayoutChange("portal")}
          className={`flex items-center gap-1.5 px-2.5 py-1 rounded transition-all font-bold cursor-pointer ${
            layoutMode === "portal"
              ? "bg-[var(--accent-tangerine)] text-[var(--accent-contrast)] shadow-sm"
              : "text-[var(--foreground)] opacity-70 hover:opacity-100"
          }`}
          title="Public Portal & Institutional Overview"
        >
          <Building2 className="w-3.5 h-3.5 stroke-[2.5]" />
          <span className="hidden xl:inline">{lang === "DE" ? "Übersicht" : "Overview"}</span>
        </button>

        <button
          onClick={() => {
            if (!user) {
              onLayoutChange("login");
            } else {
              onLayoutChange("workbench");
            }
          }}
          className={`flex items-center gap-1.5 px-2.5 py-1 rounded transition-all font-bold cursor-pointer ${
            layoutMode === "workbench"
              ? "bg-[var(--accent-tangerine)] text-[var(--accent-contrast)] shadow-sm"
              : "text-[var(--foreground)] opacity-70 hover:opacity-100"
          }`}
          title={user ? "Split Dual-View: Original PDF + English Translation Dossier" : "Sign In required to open Dual-Workbench"}
        >
          <Columns3 className="w-3.5 h-3.5 stroke-[2.5]" />
          <span className="hidden xl:inline">{t.nav_workbench}</span>
          {!user && <Lock className="w-2.5 h-2.5 opacity-50 ml-0.5" />}
        </button>

        {/* Dedicated Standalone KI-Auditor Studio */}
        <button
          onClick={() => {
            if (!user) {
              onLayoutChange("login");
            } else {
              onLayoutChange("auditor");
            }
          }}
          className={`flex items-center gap-1.5 px-2.5 py-1 rounded transition-all font-bold cursor-pointer ${
            layoutMode === "auditor"
              ? "bg-[var(--accent-tangerine)] text-[var(--accent-contrast)] shadow-sm"
              : "text-[var(--foreground)] opacity-70 hover:opacity-100"
          }`}
          title={user ? "Standalone AI Compliance Auditor (Harvey / ChatGPT Studio)" : "Sign In required to open AI Auditor Studio"}
        >
          <Bot className="w-3.5 h-3.5 stroke-[2.5] text-[var(--accent-tangerine)]" />
          <span className="hidden xl:inline">{t.nav_auditor}</span>
          {!user && <Lock className="w-2.5 h-2.5 opacity-50 ml-0.5" />}
        </button>

        <button
          onClick={() => {
            if (!user) {
              onLayoutChange("login");
            } else {
              onLayoutChange("executive");
            }
          }}
          className={`flex items-center gap-1.5 px-2.5 py-1 rounded transition-all font-bold cursor-pointer ${
            layoutMode === "executive"
              ? "bg-[var(--accent-tangerine)] text-[var(--accent-contrast)] shadow-sm"
              : "text-[var(--foreground)] opacity-70 hover:opacity-100"
          }`}
          title={user ? "Executive Compliance Cockpit & Metrics" : "Sign In required to open Executive Cockpit"}
        >
          <LayoutGrid className="w-3.5 h-3.5 stroke-[2.5]" />
          <span className="hidden xl:inline">{t.nav_cockpit}</span>
          {!user && <Lock className="w-2.5 h-2.5 opacity-50 ml-0.5" />}
        </button>

        {/* Silicon Valley Command Palette (⌘K) Trigger */}
        {onOpenCommandPalette && (
          <button
            onClick={onOpenCommandPalette}
            className="flex items-center gap-1.5 px-2 py-1 rounded bg-[var(--surface-dark)] hover:bg-[var(--surface-border)] text-slate-400 hover:text-white transition-all font-mono text-[11px] border border-[var(--surface-border)] cursor-pointer shadow-sm ml-1"
            title="Spotlight Search & Quick Actions (⌘K / Ctrl+K)"
          >
            <Search className="w-3 h-3 text-purple-400" />
            <span className="hidden xl:inline">{lang === "DE" ? "Suche" : "Search"}</span>
            <kbd className="text-[10px] bg-slate-800 text-slate-300 px-1 py-0.2 rounded border border-slate-700">⌘K</kbd>
          </button>
        )}
      </div>

      {/* 3. Right: Sovereign Telemetry Status, User Profile, Certificate Export, Theme & Language */}
      <div className="flex items-center gap-2 shrink-0">
        {/* High-Craft Sovereign Infrastructure Indicator (Option A) */}
        <div className="relative group hidden sm:block">
          <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-[var(--surface-card)] border border-[var(--surface-border)] hover:border-emerald-500/40 text-[10px] font-mono cursor-pointer transition-all shadow-sm">
            <span className="relative flex h-2 w-2">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
            </span>
            <span className="text-[var(--foreground)] font-bold">Frankfurt</span>
            <span className="opacity-40">•</span>
            <span className="text-emerald-600 dark:text-emerald-400 font-semibold">12ms</span>
          </div>

          {/* Interactive Hover Popover with German Banking Compliance Specs */}
          <div className="absolute top-full right-0 mt-2 w-64 p-3 rounded-xl bg-slate-900 border border-slate-800 text-slate-200 text-xs shadow-2xl opacity-0 group-hover:opacity-100 pointer-events-none group-hover:pointer-events-auto transition-all duration-200 z-50 font-mono">
            <div className="flex items-center justify-between pb-2 mb-2 border-b border-slate-800">
              <span className="font-bold text-white text-[11px] flex items-center gap-1.5">
                <span className="w-2 h-2 rounded-full bg-emerald-400"></span>
                SOVEREIGN NODE
              </span>
              <span className="text-[10px] text-emerald-400 bg-emerald-500/10 px-1.5 py-0.5 rounded border border-emerald-500/20">
                ACTIVE
              </span>
            </div>
            <div className="space-y-1.5 text-[10px]">
              <div className="flex justify-between">
                <span className="text-slate-400">Datacenter:</span>
                <span className="text-white font-medium">Frankfurt (eu-central-1)</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-400">Standard:</span>
                <span className="text-emerald-400 font-medium">BSI C5 • Type II</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-400">Privacy:</span>
                <span className="text-blue-400 font-medium">DSGVO / BDSG § 26</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-400">Latency:</span>
                <span className="text-slate-300">12ms Round-Trip</span>
              </div>
            </div>
          </div>
        </div>

        {/* User Authentication Status */}
        {user ? (
          <div className="flex items-center gap-2 bg-[var(--surface-card)] border border-[var(--surface-border)] px-2.5 py-1 rounded-lg text-xs font-mono shadow-sm">
            <div className="flex items-center gap-1.5">
              <div className="w-5 h-5 rounded-full bg-[var(--accent-tangerine)]/15 border border-[var(--accent-tangerine)]/30 flex items-center justify-center text-[var(--accent-tangerine)] font-bold text-[10px]">
                {user.full_name.charAt(0)}
              </div>
              <span className="font-bold text-[var(--foreground)] truncate max-w-[110px] hidden sm:inline">
                {user.full_name}
              </span>
            </div>
            <span className="text-[9px] px-1.5 py-0.2 rounded bg-[var(--surface-dark)] border border-[var(--surface-border)] uppercase text-[var(--accent-tangerine)] font-bold hidden md:inline">
              {user.role}
            </span>
            <button
              onClick={onLogout}
              title={t.btn_logout}
              className="text-[var(--foreground)] opacity-50 hover:opacity-100 hover:text-rose-500 p-0.5 cursor-pointer ml-1"
            >
              <LogOut className="w-3.5 h-3.5" />
            </button>
          </div>
        ) : (
          <button
            onClick={() => onLayoutChange("login")}
            className={`flex items-center gap-1.5 px-3 py-1 rounded-md transition-all font-mono font-bold text-[11px] shadow-sm cursor-pointer ${
              layoutMode === "login"
                ? "bg-[var(--accent-tangerine)] text-[var(--accent-contrast)]"
                : "bg-[var(--surface-card)] hover:bg-[var(--surface-dark)] border border-[var(--accent-tangerine)]/50 text-[var(--foreground)]"
            }`}
          >
            <Lock className="w-3 h-3 text-[var(--accent-tangerine)]" />
            <span>{t.btn_sign_in}</span>
          </button>
        )}

        {/* Official Certificate Export Button (Active in Workspace) */}
        {layoutMode !== "portal" && layoutMode !== "login" && (
          <button
            onClick={onOpenCertificate}
            className="flex items-center gap-1.5 px-2.5 py-1 rounded-md bg-[var(--accent-tangerine)] hover:opacity-90 text-[var(--accent-contrast)] font-mono font-black text-[11px] transition-all shadow-sm cursor-pointer uppercase tracking-wider"
            title="Official BaFin / DIN 66399 Compliance Certificate"
          >
            <Award className="w-3.5 h-3.5 stroke-[2.5]" />
            <span className="hidden lg:inline">{t.btn_certificate}</span>
          </button>
        )}

        {/* Color Palette Switcher */}
        <div className="flex items-center bg-[var(--surface-card)] border border-[var(--surface-border)] rounded-md p-0.5 font-mono text-[10px]">
          <button
            onClick={() => onThemeChange("cyber")}
            className={`px-2 py-0.5 rounded transition-all font-bold cursor-pointer ${
              theme === "cyber"
                ? "bg-[var(--accent-tangerine)] text-black"
                : "text-[var(--foreground)] opacity-60 hover:opacity-100"
            }`}
            title="Cyber-Onyx Dark"
          >
            ⚡
          </button>
          <button
            onClick={() => onThemeChange("bauhaus")}
            className={`px-2 py-0.5 rounded transition-all font-bold cursor-pointer ${
              theme === "bauhaus"
                ? "bg-[var(--accent-tangerine)] text-white"
                : "text-[var(--foreground)] opacity-60 hover:opacity-100"
            }`}
            title="Bauhaus German Architectural Light"
          >
            🏛️
          </button>
          <button
            onClick={() => onThemeChange("terminal")}
            className={`px-2 py-0.5 rounded transition-all font-bold cursor-pointer ${
              theme === "terminal"
                ? "bg-[var(--accent-tangerine)] text-black shadow-sm"
                : "text-[var(--foreground)] opacity-60 hover:opacity-100"
            }`}
            title="Prussian Navy Blueprint"
          >
            🌊
          </button>
        </div>

        {/* Language Switcher DE | EN */}
        <div className="flex items-center bg-[var(--surface-card)] border border-[var(--surface-border)] rounded-md p-0.5 font-mono text-[10px]">
          <button
            onClick={() => onToggleLang("DE")}
            className={`px-1.5 py-0.5 rounded transition-all font-bold cursor-pointer ${
              lang === "DE"
                ? "bg-[var(--accent-tangerine)] text-[var(--accent-contrast)]"
                : "text-[var(--foreground)] opacity-60 hover:opacity-100"
            }`}
          >
            DE
          </button>
          <button
            onClick={() => onToggleLang("EN")}
            className={`px-1.5 py-0.5 rounded transition-all font-bold cursor-pointer ${
              lang === "EN"
                ? "bg-[var(--accent-tangerine)] text-[var(--accent-contrast)]"
                : "text-[var(--foreground)] opacity-60 hover:opacity-100"
            }`}
          >
            EN
          </button>
        </div>
      </div>
    </header>
  );
}

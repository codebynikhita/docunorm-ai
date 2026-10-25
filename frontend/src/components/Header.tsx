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
} from "lucide-react";
import { Language, translations } from "@/lib/i18n";
import { UserProfile } from "@/lib/api";

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
}: HeaderProps) {
  const t = translations[lang];

  return (
    <header className="h-14 border-b border-[var(--surface-border)] bg-[var(--surface-dark)]/95 backdrop-blur-md px-4 flex items-center justify-between sticky top-0 z-50 select-none">
      {/* 1. Left: Brand Identity */}
      <div className="flex items-center gap-3">
        <button
          onClick={() => onLayoutChange("portal")}
          className="flex items-center gap-2.5 text-left cursor-pointer group"
          title="Return to Public Portal"
        >
          <div className="w-8 h-8 rounded-md bg-[var(--accent-tangerine)]/15 border border-[var(--accent-tangerine)]/40 flex items-center justify-center text-[var(--accent-tangerine)] font-mono font-black text-sm shadow-sm group-hover:bg-[var(--accent-tangerine)] group-hover:text-[var(--accent-contrast)] transition-all">
            §
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="font-extrabold text-sm tracking-tight text-[var(--foreground)] font-mono">
                DOCUNORM<span className="text-[var(--accent-tangerine)] font-black">.DE</span>
              </span>
              <span className="hidden sm:inline-block text-[9px] font-mono tracking-widest bg-[var(--accent-tangerine)]/10 text-[var(--accent-tangerine)] border border-[var(--accent-tangerine)]/30 px-1.5 py-0.5 rounded uppercase font-semibold">
                DIN 66399 / BDSG
              </span>
            </div>
            <p className="text-[10px] text-[var(--foreground)] opacity-60 font-mono tracking-tight hidden md:block">
              {t.brand_sub}
            </p>
          </div>
        </button>
      </div>

      {/* 2. Middle: Navigation & Layout Switcher */}
      <div className="flex items-center gap-1 bg-[var(--surface-card)] border border-[var(--surface-border)] rounded-lg p-1 font-mono text-[11px] shadow-sm">
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
          <span className="hidden md:inline">{lang === "DE" ? "Übersicht" : "Overview"}</span>
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
          <span className="hidden md:inline">{t.nav_workbench}</span>
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
          <span className="hidden md:inline">{t.nav_auditor}</span>
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
          <span className="hidden md:inline">{t.nav_cockpit}</span>
          {!user && <Lock className="w-2.5 h-2.5 opacity-50 ml-0.5" />}
        </button>
      </div>

      {/* 3. Right: User Profile, Certificate Export, Theme & Language */}
      <div className="flex items-center gap-2">
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

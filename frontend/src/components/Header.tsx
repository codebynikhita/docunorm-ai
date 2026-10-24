import React from "react";
import {
  FileSpreadsheet,
  Lock,
  Building2,
  LayoutGrid,
  Columns3,
  Maximize2,
  Award,
} from "lucide-react";
import { Language, translations } from "@/lib/i18n";

export type Theme = "cyber" | "bauhaus" | "terminal";
export type LayoutMode = "workbench" | "executive" | "focus";

interface HeaderProps {
  lang: Language;
  onToggleLang: (newLang: Language) => void;
  theme: Theme;
  onThemeChange: (theme: Theme) => void;
  layoutMode: LayoutMode;
  onLayoutChange: (mode: LayoutMode) => void;
  onOpenCertificate?: () => void;
  onOpenZugferd?: () => void;
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
}: HeaderProps) {
  const t = translations[lang];

  return (
    <header className="h-14 border-b border-[var(--surface-border)] bg-[var(--surface-dark)]/95 backdrop-blur-md px-4 flex items-center justify-between sticky top-0 z-50 select-none">
      {/* 1. Left: Brand Identity */}
      <div className="flex items-center gap-3">
        <div className="w-8 h-8 rounded-md bg-[var(--accent-tangerine)]/15 border border-[var(--accent-tangerine)]/40 flex items-center justify-center text-[var(--accent-tangerine)] font-mono font-black text-sm shadow-sm">
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
      </div>

      {/* 2. Middle: Layout Template Switcher */}
      <div className="flex items-center gap-1 bg-[var(--surface-card)] border border-[var(--surface-border)] rounded-lg p-1 font-mono text-[11px] shadow-sm">
        <button
          onClick={() => onLayoutChange("workbench")}
          className={`flex items-center gap-1.5 px-2.5 py-1 rounded transition-all font-bold cursor-pointer ${
            layoutMode === "workbench"
              ? "bg-[var(--accent-tangerine)] text-[var(--accent-contrast)] shadow-sm"
              : "text-[var(--foreground)] opacity-70 hover:opacity-100"
          }`}
          title="Split View: PDF Viewer + Auditor"
        >
          <Columns3 className="w-3.5 h-3.5 stroke-[2.5]" />
          <span className="hidden md:inline">Workbench</span>
        </button>

        <button
          onClick={() => onLayoutChange("executive")}
          className={`flex items-center gap-1.5 px-2.5 py-1 rounded transition-all font-bold cursor-pointer ${
            layoutMode === "executive"
              ? "bg-[var(--accent-tangerine)] text-[var(--accent-contrast)] shadow-sm"
              : "text-[var(--foreground)] opacity-70 hover:opacity-100"
          }`}
          title="Executive Compliance Cockpit & Metrics"
        >
          <LayoutGrid className="w-3.5 h-3.5 stroke-[2.5]" />
          <span className="hidden md:inline">Executive Cockpit</span>
        </button>

        <button
          onClick={() => onLayoutChange("focus")}
          className={`flex items-center gap-1.5 px-2.5 py-1 rounded transition-all font-bold cursor-pointer ${
            layoutMode === "focus"
              ? "bg-[var(--accent-tangerine)] text-[var(--accent-contrast)] shadow-sm"
              : "text-[var(--foreground)] opacity-70 hover:opacity-100"
          }`}
          title="Full-Screen Document Focus Canvas"
        >
          <Maximize2 className="w-3.5 h-3.5 stroke-[2.5]" />
          <span className="hidden md:inline">Focus Canvas</span>
        </button>
      </div>

      {/* 3. Right: Certificate Export, Theme Selector, Language & Tenant */}
      <div className="flex items-center gap-2.5">
        {/* Official Certificate Export Button */}
        <button
          onClick={onOpenCertificate}
          className="flex items-center gap-1.5 px-3 py-1 rounded-md bg-[var(--accent-tangerine)] hover:opacity-90 text-[var(--accent-contrast)] font-mono font-black text-[11px] transition-all shadow-sm cursor-pointer uppercase tracking-wider"
          title="Official BaFin / DIN 66399 Compliance Certificate"
        >
          <Award className="w-3.5 h-3.5 stroke-[2.5]" />
          <span className="hidden sm:inline">
            {lang === "DE" ? "Prüfbericht" : "Audit Certificate"}
          </span>
        </button>

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
            ⚡ Cyber
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
            🏛️ Bauhaus
          </button>
          <button
            onClick={() => onThemeChange("terminal")}
            className={`px-2 py-0.5 rounded transition-all font-bold cursor-pointer ${
              theme === "terminal"
                ? "bg-[var(--accent-tangerine)] text-black shadow-sm"
                : "text-[var(--foreground)] opacity-60 hover:opacity-100"
            }`}
            title="Prussian Navy & Cyan Blueprint"
          >
            🌊 Blueprint
          </button>
        </div>

        {/* Language Switcher DE | EN */}
        <div className="flex items-center bg-[var(--surface-card)] border border-[var(--surface-border)] rounded-md p-0.5 font-mono text-[10px]">
          <button
            onClick={() => onToggleLang("DE")}
            className={`px-2 py-0.5 rounded transition-all font-bold cursor-pointer ${
              lang === "DE"
                ? "bg-[var(--accent-tangerine)] text-[var(--accent-contrast)]"
                : "text-[var(--foreground)] opacity-60 hover:opacity-100"
            }`}
          >
            DE 🇩🇪
          </button>
          <button
            onClick={() => onToggleLang("EN")}
            className={`px-2 py-0.5 rounded transition-all font-bold cursor-pointer ${
              lang === "EN"
                ? "bg-[var(--accent-tangerine)] text-[var(--accent-contrast)]"
                : "text-[var(--foreground)] opacity-60 hover:opacity-100"
            }`}
          >
            EN 🇬🇧
          </button>
        </div>

        {/* Tenant Crest */}
        <div className="hidden xl:flex items-center gap-2 px-2.5 py-1 rounded-md bg-[var(--surface-card)] border border-[var(--surface-border)] text-[11px] font-mono">
          <Building2 className="w-3.5 h-3.5 text-[var(--accent-tangerine)]" />
          <span className="text-[var(--foreground)] font-semibold">Siemens AG</span>
        </div>
      </div>
    </header>
  );
}

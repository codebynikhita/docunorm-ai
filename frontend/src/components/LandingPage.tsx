"use client";

import React, { useState } from "react";
import {
  Shield,
  FileCheck,
  Scale,
  Lock,
  ArrowRight,
  Languages,
  CheckCircle2,
  FileSpreadsheet,
  Building2,
  Cpu,
  Layers,
  Award,
  Sparkles,
  Columns,
  Bot,
  Check,
  ExternalLink,
  ChevronRight,
  Database,
  Search,
  Network,
  GitBranch,
  Server,
  Globe2,
  AlertTriangle,
  Terminal,
  Zap,
} from "lucide-react";
import { Language, translations } from "@/lib/i18n";
import { UserProfile } from "@/lib/api";
import { DocuNormLogo } from "@/components/DocuNormLogo";

interface LandingPageProps {
  lang?: Language;
  user?: UserProfile | null;
  onOpenAuth: () => void;
  onEnterAsDemo: (role: "siemens" | "bafin") => void;
  onExploreWorkbench: () => void;
}

export function LandingPage({
  lang = "DE",
  user,
  onOpenAuth,
  onEnterAsDemo,
  onExploreWorkbench,
}: LandingPageProps) {
  const t = translations[lang];
  const isDe = lang === "DE";

  // Interactive Live Product Preview Tabs (Silicon Valley Craft)
  const [activePreviewTab, setActivePreviewTab] = useState<"exit" | "kaskade" | "zugferd" | "auditor">("exit");

  return (
    <div className="flex-1 overflow-auto bg-[var(--background)] text-[var(--foreground)] font-sans selection:bg-[var(--accent-tangerine)]/20">
      {/* 1. Hero Section */}
      <section className="relative pt-16 pb-12 px-4 sm:px-6 max-w-6xl mx-auto text-center space-y-7">
        {/* Subtle Ambient Glow */}
        <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[700px] h-[350px] bg-gradient-to-r from-cyan-500/10 via-[var(--accent-tangerine)]/10 to-purple-500/10 blur-[130px] pointer-events-none rounded-full" />

        {/* Regulatory Seal Pill with Frankfurt Sovereign Telemetry */}
        <div className="inline-flex items-center gap-2.5 px-3.5 py-1.5 rounded-full bg-[var(--surface-card)] border border-[var(--surface-border)] text-xs font-mono shadow-sm">
          <DocuNormLogo size="xs" showText={false} isHoverable={false} />
          <span className="font-extrabold tracking-wider text-[var(--foreground)] uppercase text-[11px]">
            DocuNorm.de • Sovereign Regulatory AI
          </span>
          <span className="opacity-30">|</span>
          <span className="text-emerald-500 font-bold text-[11px] tracking-wide flex items-center gap-1.5">
            <span className="relative flex h-1.5 w-1.5">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-1.5 w-1.5 bg-emerald-500"></span>
            </span>
            {isDe ? "Frankfurt Sovereign Cloud (eu-central-1)" : "Frankfurt Sovereign Cloud (eu-central-1)"}
          </span>
        </div>

        {/* Hero Headline */}
        <h1 className="text-4xl sm:text-6xl lg:text-7xl font-black font-sans tracking-tight max-w-5xl mx-auto leading-[1.08] text-[var(--foreground)]">
          {t.landing_hero_h1_pre}{" "}
          <span className="text-transparent bg-clip-text bg-gradient-to-r from-[var(--accent-tangerine)] via-amber-500 to-orange-400 relative inline-block">
            {t.landing_hero_h1_accent}
            <span className="absolute bottom-1 left-0 w-full h-[3px] bg-[var(--accent-tangerine)]/30 rounded-full" />
          </span>
        </h1>

        {/* Executive Subtitle */}
        <p
          spellCheck={false}
          className="text-base sm:text-lg text-[var(--foreground)] opacity-75 max-w-2xl mx-auto leading-relaxed font-sans"
        >
          {isDe
            ? "Silicon Valley Technologie für das deutsche Aufsichtsrecht. Vollautomatische forensische Prüfungen für BaFin RS 10/2018 (BAIT), EU DORA Art. 30 und ZUGFeRD 2.3 E-Rechnungen."
            : "Silicon Valley grade AI engineering for German & EU financial compliance. Fully automated forensic audits for BaFin BAIT, EU DORA Art. 30, and ZUGFeRD 2.3 e-invoices."}
        </p>

        {/* Primary Call-to-Actions */}
        <div className="flex flex-wrap items-center justify-center gap-3.5 pt-2 font-mono text-xs">
          {user ? (
            <>
              <button
                onClick={onExploreWorkbench}
                className="flex items-center gap-2.5 px-7 py-3.5 rounded-xl bg-[var(--accent-tangerine)] hover:opacity-95 text-[var(--accent-contrast)] font-extrabold shadow-xl shadow-[var(--accent-tangerine)]/20 transition-all cursor-pointer uppercase tracking-wider text-xs border border-white/20 active:scale-95"
              >
                <Columns className="w-4 h-4 stroke-[2.5]" />
                <span>{isDe ? "Zur PDF-Prüfbank öffnen" : "Open PDF Workbench"}</span>
                <ArrowRight className="w-4 h-4 stroke-[2.5]" />
              </button>
              <div className="flex items-center gap-2 px-5 py-3 rounded-xl bg-[var(--surface-card)] border border-[var(--surface-border)] text-xs font-mono shadow-sm">
                <span className="w-2 h-2 rounded-full bg-emerald-500" />
                <span className="text-[var(--foreground)] opacity-70">
                  {isDe ? "Eingeloggt als:" : "Signed in as:"}
                </span>
                <strong className="text-[var(--foreground)] font-bold">{user.full_name}</strong>
              </div>
            </>
          ) : (
            <>
              <button
                onClick={() => onEnterAsDemo("siemens")}
                className="flex items-center gap-2.5 px-7 py-3.5 rounded-xl bg-[var(--accent-tangerine)] hover:opacity-95 text-[var(--accent-contrast)] font-extrabold shadow-xl shadow-[var(--accent-tangerine)]/20 transition-all cursor-pointer uppercase tracking-wider text-xs border border-white/20 active:scale-95"
              >
                <span>{t.landing_cta_demo}</span>
                <ArrowRight className="w-4 h-4 stroke-[2.5]" />
              </button>

              <button
                onClick={onOpenAuth}
                className="flex items-center gap-2 px-6 py-3.5 rounded-xl bg-[var(--surface-card)] hover:bg-[var(--surface-dark)] text-[var(--foreground)] border border-[var(--surface-border)] hover:border-[var(--accent-tangerine)]/60 font-bold transition-all shadow-sm cursor-pointer"
              >
                <Lock className="w-4 h-4 text-[var(--accent-tangerine)]" />
                <span>{t.landing_cta_auth}</span>
              </button>
            </>
          )}
        </div>

        {/* German Institutional Trust Badges Strip (Silicon Valley Style) */}
        <div className="pt-2 flex flex-wrap items-center justify-center gap-4 text-[11px] font-mono text-slate-500 dark:text-slate-400">
          <span className="flex items-center gap-1.5 px-2.5 py-1 rounded-md bg-slate-100 dark:bg-slate-800/80 border border-slate-200 dark:border-slate-700">
            <Shield className="w-3.5 h-3.5 text-cyan-500" />
            BaFin DORA Art. 30
          </span>
          <span className="flex items-center gap-1.5 px-2.5 py-1 rounded-md bg-slate-100 dark:bg-slate-800/80 border border-slate-200 dark:border-slate-700">
            <Building2 className="w-3.5 h-3.5 text-purple-500" />
            Deutsche Bundesbank KWG § 25b
          </span>
          <span className="flex items-center gap-1.5 px-2.5 py-1 rounded-md bg-slate-100 dark:bg-slate-800/80 border border-slate-200 dark:border-slate-700">
            <FileSpreadsheet className="w-3.5 h-3.5 text-emerald-500" />
            ZUGFeRD 2.3 / Factur-X
          </span>
          <span className="flex items-center gap-1.5 px-2.5 py-1 rounded-md bg-slate-100 dark:bg-slate-800/80 border border-slate-200 dark:border-slate-700">
            <Lock className="w-3.5 h-3.5 text-amber-500" />
            BSI C5 & DSGVO
          </span>
        </div>

        {/* 2. Interactive Silicon Valley-Grade Live Product Preview */}
        <div className="pt-4 max-w-5xl mx-auto text-left">
          <div className="rounded-2xl border border-[var(--surface-border)] bg-[var(--surface-dark)] shadow-2xl overflow-hidden ring-1 ring-black/5">
            {/* macOS Chrome Header with Feature Switcher Tabs */}
            <div className="px-4 py-2 bg-[var(--surface-card)] border-b border-[var(--surface-border)] flex flex-wrap items-center justify-between gap-3 select-none font-mono text-xs">
              <div className="flex items-center gap-3">
                <div className="flex gap-1.5">
                  <div className="w-3 h-3 rounded-full bg-rose-500/80" />
                  <div className="w-3 h-3 rounded-full bg-amber-500/80" />
                  <div className="w-3 h-3 rounded-full bg-emerald-500/80" />
                </div>
                {/* 4 Interactive Feature Tabs */}
                <div className="flex items-center gap-1 bg-[var(--surface-dark)] p-0.5 rounded-lg border border-[var(--surface-border)]">
                  <button
                    onClick={() => setActivePreviewTab("exit")}
                    className={`px-2.5 py-1 rounded text-[11px] font-bold transition-all ${
                      activePreviewTab === "exit"
                        ? "bg-cyan-500/20 text-cyan-400 border border-cyan-500/40 shadow-sm"
                        : "text-slate-400 hover:text-white"
                    }`}
                  >
                    DORA Art. 30(2) Exit
                  </button>
                  <button
                    onClick={() => setActivePreviewTab("kaskade")}
                    className={`px-2.5 py-1 rounded text-[11px] font-bold transition-all ${
                      activePreviewTab === "kaskade"
                        ? "bg-purple-500/20 text-purple-400 border border-purple-500/40 shadow-sm"
                        : "text-slate-400 hover:text-white"
                    }`}
                  >
                    Art. 30(3) Kaskade
                  </button>
                  <button
                    onClick={() => setActivePreviewTab("zugferd")}
                    className={`px-2.5 py-1 rounded text-[11px] font-bold transition-all ${
                      activePreviewTab === "zugferd"
                        ? "bg-emerald-500/20 text-emerald-400 border border-emerald-500/40 shadow-sm"
                        : "text-slate-400 hover:text-white"
                    }`}
                  >
                    ZUGFeRD 2.3 XML
                  </button>
                  <button
                    onClick={() => setActivePreviewTab("auditor")}
                    className={`px-2.5 py-1 rounded text-[11px] font-bold transition-all ${
                      activePreviewTab === "auditor"
                        ? "bg-[var(--accent-tangerine)]/20 text-[var(--accent-tangerine)] border border-[var(--accent-tangerine)]/40 shadow-sm"
                        : "text-slate-400 hover:text-white"
                    }`}
                  >
                    Gemini 2.0 Studio
                  </button>
                </div>
              </div>

              <div className="flex items-center gap-2">
                <span className="text-[10px] text-emerald-500 font-bold bg-emerald-500/10 border border-emerald-500/30 px-2 py-0.5 rounded flex items-center gap-1">
                  <CheckCircle2 className="w-3 h-3 text-emerald-500" />
                  100% BaFin Grounded
                </span>
              </div>
            </div>

            {/* Dynamic Viewport Content based on active tab */}
            {activePreviewTab === "exit" && (
              <div className="grid grid-cols-1 md:grid-cols-2 divide-y md:divide-y-0 md:divide-x divide-[var(--surface-border)] bg-[var(--canvas-bg)] p-4 sm:p-6 gap-4">
                {/* Left: German Authentic Contract Clause */}
                <div className="space-y-3 p-4 rounded-xl bg-white text-slate-900 border border-slate-200 shadow-md font-sans">
                  <div className="flex items-center justify-between pb-2 border-b border-slate-200 text-[11px] font-mono">
                    <span className="font-bold text-slate-800">
                      Siemens_Master_IKT_Vertrag_2026.pdf
                    </span>
                    <span className="text-[10px] bg-slate-100 px-1.5 py-0.5 rounded border border-slate-300 font-bold">
                      Seite 2 von 3
                    </span>
                  </div>
                  <div className="space-y-2 text-[12px] text-slate-700 leading-relaxed">
                    <p className="font-bold text-slate-900 text-xs font-mono uppercase">
                      § 3 Kündigung, Übergangsfristen und Ausstiegsstrategie (Art. 30 Abs. 2 DORA)
                    </p>
                    <div className="p-3 rounded-lg border-2 border-cyan-500 bg-cyan-50 text-slate-950 font-medium relative shadow-sm">
                      <span className="absolute -top-3 right-3 text-[9px] font-mono font-black uppercase tracking-wider bg-cyan-600 text-white px-1.5 py-0.2 rounded shadow">
                        [SOURCE_1] Bounding Box [50, 115, 528, 203]
                      </span>
                      <p>
                        „Jede Vertragspartei kann diesen Vertrag mit einer ordentlichen
                        Kündigungsfrist von sechzig (60) Tagen zum Quartalsende kündigen. Der
                        Auftragnehmer garantiert im Falle der Beendigung eine umfassende
                        Unterstützungspflicht bei der Migration von Datenbeständen für mindestens neunzig (90) Tage
                        ohne Unterbrechung des Geschäftsbetriebs.“
                      </p>
                    </div>
                  </div>
                </div>

                {/* Right: Certified English Translation Dossier */}
                <div className="space-y-3 p-4 rounded-xl bg-[var(--surface-card)] border border-[var(--surface-border)] shadow-md font-sans flex flex-col justify-between">
                  <div className="space-y-3">
                    <div className="flex items-center justify-between pb-2 border-b border-[var(--surface-border)] text-[11px] font-mono">
                      <span className="font-bold text-[var(--foreground)]">
                        Certified_English_Regulatory_Dossier.pdf
                      </span>
                      <span className="text-[10px] bg-emerald-500/10 text-emerald-500 px-1.5 py-0.5 rounded border border-emerald-500/30 font-bold">
                        DIN EN 15038 Parität
                      </span>
                    </div>
                    <div className="space-y-2">
                      <div className="flex items-center justify-between text-[11px] font-mono">
                        <span className="font-bold text-[var(--foreground)]">
                          Section 3: Termination & Disengagement Terms
                        </span>
                        <span className="text-[10px] text-emerald-500 bg-emerald-500/10 px-1.5 py-0.5 rounded border border-emerald-500/25 font-bold">
                          60d / 90d Guarantee
                        </span>
                      </div>
                      <p className="text-[12.5px] text-[var(--foreground)] opacity-90 leading-relaxed font-sans">
                        &ldquo;Either contractual party may terminate this agreement with an ordinary notice
                        period of sixty (60) days to the end of a calendar quarter. In the event of
                        termination, the contractor contractually guarantees a transition assistance period
                        for at least ninety (90) days without interruption of business operations.&rdquo;
                      </p>
                    </div>
                  </div>
                  <div className="p-2.5 rounded-lg bg-[var(--surface-dark)] border border-emerald-500/30 flex items-center justify-between text-[11px] font-mono">
                    <div className="flex items-center gap-2">
                      <Bot className="w-4 h-4 text-emerald-500 shrink-0" />
                      <span className="text-[var(--foreground)] opacity-85">
                        {isDe
                          ? "DORA Art. 30(2) Exit-Fristen (60d/90d) vollständig erfüllt."
                          : "DORA Art. 30(2) exit periods (60d/90d) fully compliant."}
                      </span>
                    </div>
                    <span className="text-[9px] font-bold text-emerald-500 uppercase">PASS (AAA)</span>
                  </div>
                </div>
              </div>
            )}

            {activePreviewTab === "kaskade" && (
              <div className="p-6 bg-[var(--canvas-bg)] space-y-4 font-mono text-xs">
                <div className="flex items-center justify-between">
                  <span className="font-bold text-purple-400 flex items-center gap-1.5">
                    <GitBranch className="w-4 h-4 text-purple-500" />
                    DORA Art. 30(3) Kaskadierender Lieferketten-Graph (4th-Party Concentration Risk)
                  </span>
                  <span className="px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-500 text-[10px] font-bold border border-emerald-500/30">
                    Konzentrationsrisiko: NIEDRIG
                  </span>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                  <div className="p-3.5 rounded-xl bg-[var(--surface-card)] border border-purple-500/30">
                    <span className="text-[10px] font-bold text-purple-400">TIER 1 PRIMARY</span>
                    <h5 className="font-bold text-white text-sm mt-1">SAP Deutschland SE</h5>
                    <p className="text-[11px] text-slate-400 mt-0.5">Core Banking Cloud Host</p>
                    <div className="mt-2 pt-2 border-t border-slate-700/60 flex justify-between text-[10px]">
                      <span>Frankfurt am Main</span>
                      <span className="text-emerald-400 font-bold">GENEHMIGT</span>
                    </div>
                  </div>
                  <div className="p-3.5 rounded-xl bg-[var(--surface-card)] border border-slate-700">
                    <span className="text-[10px] font-bold text-indigo-400">TIER 2 PLATFORM</span>
                    <h5 className="font-bold text-white text-sm mt-1">AWS EMEA SARL</h5>
                    <p className="text-[11px] text-slate-400 mt-0.5">IaaS Compute & Storage</p>
                    <div className="mt-2 pt-2 border-t border-slate-700/60 flex justify-between text-[10px]">
                      <span>Dublin / Frankfurt</span>
                      <span className="text-emerald-400 font-bold">60d VETORECHT</span>
                    </div>
                  </div>
                  <div className="p-3.5 rounded-xl bg-[var(--surface-card)] border border-slate-700">
                    <span className="text-[10px] font-bold text-slate-400">TIER 3 FACILITY</span>
                    <h5 className="font-bold text-white text-sm mt-1">Equinix FR2 Datacenter</h5>
                    <p className="text-[11px] text-slate-400 mt-0.5">Physisches Rechenzentrum</p>
                    <div className="mt-2 pt-2 border-t border-slate-700/60 flex justify-between text-[10px]">
                      <span>Frankfurt am Main</span>
                      <span className="text-emerald-400 font-bold">BSI C5 AUDIT</span>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {activePreviewTab === "zugferd" && (
              <div className="p-6 bg-[var(--canvas-bg)] space-y-4 font-mono text-xs">
                <div className="flex items-center justify-between">
                  <span className="font-bold text-emerald-400 flex items-center gap-1.5">
                    <FileSpreadsheet className="w-4 h-4 text-emerald-500" />
                    ZUGFeRD 2.3 / Factur-X XML vs. Visueller PDF Abgleich (Wachstumschancengesetz 2025)
                  </span>
                  <span className="px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-500 text-[10px] font-bold border border-emerald-500/30">
                    EN 16931 COMFORT
                  </span>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="p-3.5 rounded-xl bg-[var(--surface-card)] border border-slate-700 space-y-2">
                    <span className="text-[10px] font-bold text-slate-400 uppercase">Eingebettetes XML (Factur-X)</span>
                    <div className="space-y-1 text-[11px]">
                      <div className="flex justify-between">
                        <span className="text-slate-400">Leitweg-ID (B2G/B2B):</span>
                        <span className="font-bold text-white">991-12345-67</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-slate-400">Nettobetrag:</span>
                        <span className="font-bold text-white">4.500,00 EUR</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-slate-400">Umsatzsteuer (19%):</span>
                        <span className="font-bold text-white">855,00 EUR</span>
                      </div>
                      <div className="flex justify-between pt-1 border-t border-slate-700">
                        <span className="font-bold text-slate-300">Gesamtbetrag (XML):</span>
                        <span className="font-bold text-emerald-400">5.355,00 EUR</span>
                      </div>
                    </div>
                  </div>
                  <div className="p-3.5 rounded-xl bg-[var(--surface-card)] border border-slate-700 space-y-2">
                    <span className="text-[10px] font-bold text-slate-400 uppercase">Visuelles PDF Abgleich-Ergebnis</span>
                    <div className="space-y-1 text-[11px]">
                      <div className="flex justify-between">
                        <span className="text-slate-400">Gedruckter Betrag:</span>
                        <span className="font-bold text-white">5.355,00 EUR</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-slate-400">Diskrepanz:</span>
                        <span className="font-bold text-emerald-400">0,00 EUR (0.00%)</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-slate-400">GoBD-Archivierungsstatus:</span>
                        <span className="font-bold text-emerald-400">REVISIONSSICHER</span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {activePreviewTab === "auditor" && (
              <div className="p-6 bg-[var(--canvas-bg)] space-y-4 font-mono text-xs">
                <div className="flex items-center justify-between">
                  <span className="font-bold text-[var(--accent-tangerine)] flex items-center gap-1.5">
                    <Bot className="w-4 h-4 text-[var(--accent-tangerine)]" />
                    DocuNorm Sovereign AI • Gemini 2.0 Flash Forensic Reasoning
                  </span>
                  <span className="px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-500 text-[10px] font-bold border border-emerald-500/30">
                    Zero-Hallucination Tagging
                  </span>
                </div>
                <div className="p-4 rounded-xl bg-[var(--surface-card)] border border-slate-700 space-y-2 text-[12px]">
                  <div className="text-slate-400 font-bold">
                    Prüffrage: „Sind die Kündigungsfristen nach DORA Art. 30 zulässig?“
                  </div>
                  <div className="p-3 rounded-lg bg-[var(--surface-dark)] border border-slate-700/80 text-slate-200 space-y-1.5">
                    <div className="text-emerald-400 font-bold">
                      ⚖️ AUFSICHTSRECHTLICHE PRÜFFESTSTELLUNG: ✅ VOLLSTÄNDIG KONFORM
                    </div>
                    <p className="text-slate-300">
                      • [SOURCE_1]: § 8 Abs. 2 garantiert eine Kündigungsfrist von 60 Tagen und 90 Tage lückenlose Migrationsunterstützung.
                    </p>
                    <p className="text-slate-300">
                      • BaFin-Würdigung: Erfüllt DORA Art. 30 Abs. 2 lit. h und schließt operative Betriebsunterbrechungen vollständig aus.
                    </p>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* 3. Silicon Valley Telemetry Grid */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3.5 max-w-5xl mx-auto pt-6 text-left font-mono">
          <div className="p-4 rounded-xl bg-[var(--surface-card)] border border-[var(--surface-border)] shadow-sm hover:border-[var(--accent-tangerine)]/40 transition-colors">
            <div className="text-[10px] opacity-60 uppercase font-bold tracking-wider">
              {t.landing_metric_authority}
            </div>
            <div className="text-sm font-extrabold text-[var(--foreground)] mt-1">BaFin / EZB</div>
            <div className="text-[10.5px] text-emerald-500 font-bold mt-1">
              DORA Art. 30 Konform
            </div>
          </div>

          <div className="p-4 rounded-xl bg-[var(--surface-card)] border border-[var(--surface-border)] shadow-sm hover:border-[var(--accent-tangerine)]/40 transition-colors">
            <div className="text-[10px] opacity-60 uppercase font-bold tracking-wider">
              {t.landing_metric_privacy}
            </div>
            <div className="text-sm font-extrabold text-[var(--foreground)] mt-1">
              BDSG § 26 / DSGVO
            </div>
            <div className="text-[10.5px] text-emerald-500 font-bold mt-1">
              Zero US CLOUD Act
            </div>
          </div>

          <div className="p-4 rounded-xl bg-[var(--surface-card)] border border-[var(--surface-border)] shadow-sm hover:border-[var(--accent-tangerine)]/40 transition-colors">
            <div className="text-[10px] opacity-60 uppercase font-bold tracking-wider">
              {t.landing_metric_invoice}
            </div>
            <div className="text-sm font-extrabold text-[var(--foreground)] mt-1">
              ZUGFeRD 2.3
            </div>
            <div className="text-[10.5px] text-emerald-500 font-bold mt-1">
              CEN 16931 Validiert
            </div>
          </div>

          <div className="p-4 rounded-xl bg-[var(--surface-card)] border border-[var(--surface-border)] shadow-sm hover:border-[var(--accent-tangerine)]/40 transition-colors">
            <div className="text-[10px] opacity-60 uppercase font-bold tracking-wider">
              Audit-Inferenz
            </div>
            <div className="text-sm font-extrabold text-[var(--foreground)] mt-1">Gemini 2.0 Flash</div>
            <div className="text-[10.5px] text-emerald-500 font-bold mt-1">
              &lt; 70ms Latenz
            </div>
          </div>
        </div>
      </section>

      {/* 4. Core Enterprise Modules */}
      <section className="py-20 px-4 sm:px-6 max-w-6xl mx-auto border-t border-[var(--surface-border)] space-y-12">
        <div className="text-center space-y-3">
          <span className="text-xs font-mono font-bold uppercase tracking-widest text-[var(--accent-tangerine)]">
            {t.landing_modules_tag}
          </span>
          <h2 className="text-3xl sm:text-4xl font-black font-sans tracking-tight text-[var(--foreground)]">
            {t.landing_modules_title}
          </h2>
          <p className="text-sm text-[var(--foreground)] opacity-70 max-w-xl mx-auto font-sans leading-relaxed">
            {isDe
              ? "Revisionssichere Automatisierung für Vorstände, General Counsels und BaFin-Prüfteams nach Bundesaufsichts-Mindeststandards."
              : "Audit-ready intelligence for general counsels, risk officers, and supervisory audit teams according to German federal standards."}
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {/* Card 1: DORA Art. 30 */}
          <div className="p-7 rounded-2xl bg-[var(--surface-card)] border border-[var(--surface-border)] shadow-sm space-y-4 hover:border-[var(--accent-tangerine)]/50 transition-all group flex flex-col justify-between">
            <div className="space-y-4">
              <div className="w-12 h-12 rounded-xl bg-[var(--accent-tangerine)]/15 border border-[var(--accent-tangerine)]/30 flex items-center justify-center text-[var(--accent-tangerine)] group-hover:scale-105 transition-transform">
                <Shield className="w-6 h-6 stroke-[2.5]" />
              </div>
              <h3 className="font-mono font-bold text-base text-[var(--foreground)]">
                {t.landing_mod1_title}
              </h3>
              <p className="text-xs text-[var(--foreground)] opacity-70 leading-relaxed font-sans">
                {t.landing_mod1_desc}
              </p>
            </div>
            <div className="pt-4 border-t border-[var(--surface-border)] text-[11px] font-mono font-bold text-[var(--accent-tangerine)] flex items-center justify-between">
              <span>VO (EU) 2022/2554 Pillar IV</span>
              <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
            </div>
          </div>

          {/* Card 2: ZUGFeRD 2.3 */}
          <div className="p-7 rounded-2xl bg-[var(--surface-card)] border border-[var(--surface-border)] shadow-sm space-y-4 hover:border-sky-500/50 transition-all group flex flex-col justify-between">
            <div className="space-y-4">
              <div className="w-12 h-12 rounded-xl bg-sky-500/15 border border-sky-500/30 flex items-center justify-center text-sky-500 group-hover:scale-105 transition-transform">
                <FileSpreadsheet className="w-6 h-6 stroke-[2.5]" />
              </div>
              <h3 className="font-mono font-bold text-base text-[var(--foreground)]">
                {t.landing_mod2_title}
              </h3>
              <p className="text-xs text-[var(--foreground)] opacity-70 leading-relaxed font-sans">
                {t.landing_mod2_desc}
              </p>
            </div>
            <div className="pt-4 border-t border-[var(--surface-border)] text-[11px] font-mono font-bold text-sky-500 flex items-center justify-between">
              <span>Wachstumschancengesetz 2025</span>
              <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
            </div>
          </div>

          {/* Card 3: 4th-Party Cascading Subcontractor Engine */}
          <div className="p-7 rounded-2xl bg-[var(--surface-card)] border border-[var(--surface-border)] shadow-sm space-y-4 hover:border-purple-500/50 transition-all group flex flex-col justify-between">
            <div className="space-y-4">
              <div className="w-12 h-12 rounded-xl bg-purple-500/15 border border-purple-500/30 flex items-center justify-center text-purple-500 group-hover:scale-105 transition-transform">
                <Network className="w-6 h-6 stroke-[2.5]" />
              </div>
              <h3 className="font-mono font-bold text-base text-[var(--foreground)]">
                {isDe ? "Sub-Outsourcing & Kaskade" : "Sub-Outsourcing Cascading Risk"}
              </h3>
              <p className="text-xs text-[var(--foreground)] opacity-70 leading-relaxed font-sans">
                {isDe
                  ? "Kartierung der 4th-Party-Lieferkette bis Tier 4, Durchgriffshaftung gem. BGB § 278 und BaFin Widerspruchsfristenkalkulator."
                  : "Mapping multi-tier supply chains to Tier 4, strict vicarious liability under BGB § 278, and statutory BaFin objection calculators."}
              </p>
            </div>
            <div className="pt-4 border-t border-[var(--surface-border)] text-[11px] font-mono font-bold text-purple-500 flex items-center justify-between">
              <span>DORA Art. 30 Abs. 3 & KWG § 25b</span>
              <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
            </div>
          </div>
        </div>
      </section>

      {/* 5. Institutional Institutional Compliance Callout */}
      <section className="py-14 px-4 sm:px-6 bg-[var(--surface-dark)] border-t border-[var(--surface-border)] text-center space-y-4">
        <div className="max-w-3xl mx-auto space-y-3 font-mono">
          <div className="inline-flex items-center gap-2 text-xs font-bold uppercase tracking-wider text-[var(--accent-tangerine)]">
            <Award className="w-4 h-4" />
            <span>{isDe ? "Aufsichtsrechtlicher Mindeststandard" : "Supervisory Compliance Standard"}</span>
          </div>
          <p className="text-xs sm:text-sm text-[var(--foreground)] opacity-80 leading-relaxed font-sans">
            {isDe
              ? "DocuNorm AI wurde für hochgradig regulierte Kreditinstitute, DAX-40 IKT-Dienstleister und Wirtschaftsprüfer nach Maßgabe der BaFin-Rundschreiben (BAIT/VAIT) und des DORA Pillar IV entwickelt."
              : "DocuNorm AI is engineered for regulated credit institutions, DAX-40 ICT infrastructure vendors, and supervisory audit teams under BaFin BAIT/VAIT and EU DORA Pillar IV governance."}
          </p>
        </div>
      </section>

      {/* 6. Institutional Footer */}
      <footer className="border-t border-[var(--surface-border)] bg-[var(--surface-card)] py-10 px-6 text-center text-xs font-mono opacity-70 space-y-2">
        <div className="flex items-center justify-center gap-3 text-xs font-bold text-[var(--foreground)]">
          <span>DocuNorm.de AI</span>
          <span>•</span>
          <span>Frankfurt am Main Node (eu-central-1)</span>
          <span>•</span>
          <span>BDSG § 26 & EU-DSGVO</span>
        </div>
        <p className="text-[11px] opacity-60">
          DIN 66399 Schutzklasse 3 • BSI TR-02102 PBKDF2 Kryptografie • BaFin Revisions-Prüfpfad aktiv
        </p>
      </footer>
    </div>
  );
}

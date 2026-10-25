"use client";

import React from "react";
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
} from "lucide-react";
import { Language, translations } from "@/lib/i18n";
import { UserProfile } from "@/lib/api";

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

  return (
    <div className="flex-1 overflow-auto bg-[var(--background)] text-[var(--foreground)] font-sans selection:bg-[var(--accent-tangerine)]/20">
      {/* 1. Hero Section */}
      <section className="relative pt-16 pb-12 px-4 sm:px-6 max-w-6xl mx-auto text-center space-y-7">
        {/* Subtle Ambient Glow */}
        <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[600px] h-[300px] bg-[var(--accent-tangerine)]/8 blur-[120px] pointer-events-none rounded-full" />

        {/* Regulatory Seal Pill */}
        <div className="inline-flex items-center gap-2.5 px-4 py-1.5 rounded-full bg-[var(--surface-card)] border border-[var(--surface-border)] text-xs font-mono shadow-sm">
          <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
          <span className="font-extrabold tracking-wider text-[var(--foreground)] uppercase text-[11px]">
            DocuNorm.de • Regulatory Intelligence
          </span>
          <span className="opacity-30">|</span>
          <span className="text-[var(--accent-tangerine)] font-bold text-[11px] tracking-wide">
            {t.landing_badge}
          </span>
        </div>

        {/* Hero Headline */}
        <h1 className="text-4xl sm:text-6xl lg:text-7xl font-black font-sans tracking-tight max-w-5xl mx-auto leading-[1.08] text-[var(--foreground)]">
          {t.landing_hero_h1_pre}{" "}
          <span className="text-[var(--accent-tangerine)] relative inline-block">
            {t.landing_hero_h1_accent}
            <span className="absolute bottom-1 left-0 w-full h-[3px] bg-[var(--accent-tangerine)]/30 rounded-full" />
          </span>
        </h1>

        {/* Executive Subtitle */}
        <p
          spellCheck={false}
          className="text-base sm:text-lg text-[var(--foreground)] opacity-75 max-w-2xl mx-auto leading-relaxed font-sans"
        >
          {t.landing_hero_sub}
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

        {/* 2. Interactive High-Fidelity Dual-View Product Mockup Frame */}
        <div className="pt-6 max-w-5xl mx-auto text-left">
          <div className="rounded-2xl border border-[var(--surface-border)] bg-[var(--surface-dark)] shadow-2xl overflow-hidden ring-1 ring-black/5">
            {/* macOS Browser Chrome */}
            <div className="h-10 px-4 bg-[var(--surface-card)] border-b border-[var(--surface-border)] flex items-center justify-between select-none font-mono text-xs">
              <div className="flex items-center gap-2">
                <div className="flex gap-1.5">
                  <div className="w-3 h-3 rounded-full bg-rose-500/80" />
                  <div className="w-3 h-3 rounded-full bg-amber-500/80" />
                  <div className="w-3 h-3 rounded-full bg-emerald-500/80" />
                </div>
                <span className="ml-3 text-[11px] text-[var(--foreground)] opacity-50 hidden sm:inline">
                  docunorm.de/workbench/siemens-master-ikt-2026.pdf
                </span>
              </div>
              <div className="flex items-center gap-2">
                <span className="text-[10px] text-emerald-500 font-bold bg-emerald-500/10 border border-emerald-500/30 px-2 py-0.5 rounded flex items-center gap-1">
                  <CheckCircle2 className="w-3 h-3 text-emerald-500" />
                  BaFin DORA Art. 30 Verified
                </span>
                <span className="text-[10px] opacity-40 font-mono hidden md:inline">
                  SHA-256: 637c7b9c...
                </span>
              </div>
            </div>

            {/* Split Screen Mockup Interior */}
            <div className="grid grid-cols-1 md:grid-cols-2 divide-y md:divide-y-0 md:divide-x divide-[var(--surface-border)] bg-[var(--canvas-bg)] p-4 sm:p-6 gap-4">
              {/* Left Column: German Authentic PDF Document with Laser Coordinate */}
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

                  {/* Active Laser Bounding Box Simulation */}
                  <div className="p-3 rounded-lg border-2 border-[var(--accent-tangerine)] bg-[var(--accent-tangerine)]/10 text-slate-950 font-medium relative shadow-sm">
                    <span className="absolute -top-3 right-3 text-[9px] font-mono font-black uppercase tracking-wider bg-[var(--accent-tangerine)] text-white px-1.5 py-0.2 rounded shadow">
                      [SOURCE_1] Bounding Box [50, 115, 528, 203]
                    </span>
                    <p>
                      „Jede Vertragspartei kann diesen Vertrag mit einer ordentlichen
                      Kündigungsfrist von sechzig (60) Tagen zum Quartalsende kündigen. Der
                      Auftragnehmer garantiert im Falle der Beendigung eine umfassende
                      Unterstützungspflicht bei der Migration von Datenbeständen und Anwendungen auf
                      den Auftraggeber für mindestens neunzig (90) Tage ohne Unterbrechung des
                      Geschäftsbetriebs.“
                    </p>
                  </div>

                  <p className="opacity-70 text-[11px]">
                    § 4 Haftungsobergrenzen & Vertragsstrafen: 0,2 % der jährlichen Vergütung pro
                    Werktag, maximal 5 % des Gesamtauftragswerts.
                  </p>
                </div>
              </div>

              {/* Right Column: Synchronized English Regulatory Dossier */}
              <div className="space-y-3 p-4 rounded-xl bg-[var(--surface-card)] border border-[var(--surface-border)] shadow-md flex flex-col justify-between">
                <div>
                  <div className="flex items-center justify-between pb-2 border-b border-[var(--surface-border)] text-xs font-mono">
                    <span className="font-bold text-[var(--accent-tangerine)] uppercase tracking-wider flex items-center gap-1.5 text-[11px]">
                      <Languages className="w-3.5 h-3.5" />
                      {isDe ? "Beglaubigtes Revisionsdossier" : "Certified Translation Dossier"}
                    </span>
                    <span className="text-[10px] text-emerald-500 font-bold bg-emerald-500/10 px-2 py-0.5 rounded border border-emerald-500/25">
                      DIN EN 15038 Parität
                    </span>
                  </div>

                  <div className="mt-3 space-y-2">
                    <div className="flex items-center justify-between text-[11px] font-mono">
                      <span className="font-bold text-[var(--foreground)]">
                        § 3.1 Termination, Transition Notice Periods & Disentanglement
                      </span>
                      <span className="text-[10px] text-amber-500 bg-amber-500/10 px-1.5 py-0.5 rounded border border-amber-500/25 font-bold">
                        60d / 90d Guarantee
                      </span>
                    </div>

                    <p className="text-[12.5px] text-[var(--foreground)] opacity-90 leading-relaxed font-sans">
                      "Either contractual party may terminate this agreement with an ordinary notice
                      period of sixty (60) days to the end of a calendar quarter. In the event of
                      termination, the contractor guarantees a comprehensive support obligation for
                      the migration of datasets and applications to the client or a designated
                      third-party provider for at least ninety (90) days without interruption of
                      business operations."
                    </p>
                  </div>
                </div>

                {/* Simulated Floating KI-Auditor Finding Pill */}
                <div className="p-2.5 rounded-lg bg-[var(--surface-dark)] border border-emerald-500/30 flex items-center justify-between text-[11px] font-mono">
                  <div className="flex items-center gap-2">
                    <Bot className="w-4 h-4 text-emerald-500 shrink-0" />
                    <span className="text-[var(--foreground)] opacity-85">
                      {isDe
                        ? "KI-Auditor: DORA Art. 30 Abs. 2 Fristen (60d/90d) vollständig erfüllt."
                        : "AI Auditor: DORA Art. 30(2) exit periods (60d/90d) fully compliant."}
                    </span>
                  </div>
                  <span className="text-[9px] font-bold text-emerald-500 uppercase">PASS</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* 3. Trust & Compliance Metric Seals */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3.5 max-w-5xl mx-auto pt-6 text-left font-mono">
          <div className="p-4 rounded-xl bg-[var(--surface-card)] border border-[var(--surface-border)] shadow-sm hover:border-[var(--accent-tangerine)]/40 transition-colors">
            <div className="text-[10px] opacity-60 uppercase font-bold tracking-wider">
              {t.landing_metric_authority}
            </div>
            <div className="text-sm font-extrabold text-[var(--foreground)] mt-1">BaFin / EZB</div>
            <div className="text-[10.5px] text-emerald-500 font-bold mt-1">
              {t.landing_metric_authority_sub}
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
              {t.landing_metric_privacy_sub}
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
              {t.landing_metric_invoice_sub}
            </div>
          </div>

          <div className="p-4 rounded-xl bg-[var(--surface-card)] border border-[var(--surface-border)] shadow-sm hover:border-[var(--accent-tangerine)]/40 transition-colors">
            <div className="text-[10px] opacity-60 uppercase font-bold tracking-wider">
              {t.landing_metric_security}
            </div>
            <div className="text-sm font-extrabold text-[var(--foreground)] mt-1">DIN 66399</div>
            <div className="text-[10.5px] text-emerald-500 font-bold mt-1">
              {t.landing_metric_security_sub}
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
              <span>VO (EU) 2022/2554</span>
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

          {/* Card 3: Dual Language Dossier */}
          <div className="p-7 rounded-2xl bg-[var(--surface-card)] border border-[var(--surface-border)] shadow-sm space-y-4 hover:border-emerald-500/50 transition-all group flex flex-col justify-between">
            <div className="space-y-4">
              <div className="w-12 h-12 rounded-xl bg-emerald-500/15 border border-emerald-500/30 flex items-center justify-center text-emerald-500 group-hover:scale-105 transition-transform">
                <Languages className="w-6 h-6 stroke-[2.5]" />
              </div>
              <h3 className="font-mono font-bold text-base text-[var(--foreground)]">
                {t.landing_mod3_title}
              </h3>
              <p className="text-xs text-[var(--foreground)] opacity-70 leading-relaxed font-sans">
                {t.landing_mod3_desc}
              </p>
            </div>
            <div className="pt-4 border-t border-[var(--surface-border)] text-[11px] font-mono font-bold text-emerald-500 flex items-center justify-between">
              <span>DIN EN 15038 Parität</span>
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
          <span>Frankfurt am Main Node</span>
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

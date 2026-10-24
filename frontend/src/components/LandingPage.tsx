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
} from "lucide-react";
import { Language } from "@/lib/i18n";

interface LandingPageProps {
  lang?: Language;
  onOpenAuth: () => void;
  onEnterAsDemo: (role: "siemens" | "bafin") => void;
  onExploreWorkbench: () => void;
}

export function LandingPage({
  lang = "DE",
  onOpenAuth,
  onEnterAsDemo,
  onExploreWorkbench,
}: LandingPageProps) {
  return (
    <div className="flex-1 overflow-auto bg-[var(--background)] text-[var(--foreground)] font-sans">
      {/* 1. Hero Section */}
      <section className="relative pt-16 pb-20 px-6 max-w-6xl mx-auto text-center space-y-6">
        {/* Regulatory Seal Pill */}
        <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-[var(--surface-card)] border border-[var(--surface-border)] text-xs font-mono shadow-sm">
          <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
          <span className="font-bold text-[var(--foreground)]">DocuNorm DE v0.2</span>
          <span className="opacity-40">|</span>
          <span className="text-[var(--accent-tangerine)] font-bold">
            BaFin & DORA Art. 30 Validiert
          </span>
        </div>

        {/* Headline */}
        <h1 className="text-3xl sm:text-5xl lg:text-6xl font-black font-mono tracking-tight max-w-4xl mx-auto leading-[1.15]">
          Deutsche Regulatorik & IKT-Verträge.{" "}
          <span className="text-[var(--accent-tangerine)]">Revisionssicher geprüft.</span>
        </h1>

        {/* Subtitle */}
        <p className="text-sm sm:text-base text-[var(--foreground)] opacity-70 max-w-2xl mx-auto leading-relaxed font-sans">
          Automatisierte Vertragsanalyse nach <strong>EU DORA (VO 2022/2554)</strong>,{" "}
          <strong>BDSG § 26</strong> und <strong>ZUGFeRD 2.3 / Factur-X</strong>. Mit
          visuellem DIN A4 Belegnachweis und beglaubigtem englischen Revisionsdossier.
        </p>

        {/* Action CTAs */}
        <div className="flex flex-wrap items-center justify-center gap-3 pt-4 font-mono text-xs">
          <button
            onClick={() => onEnterAsDemo("siemens")}
            className="flex items-center gap-2 px-6 py-3 rounded-xl bg-[var(--accent-tangerine)] hover:opacity-90 text-[var(--accent-contrast)] font-bold shadow-lg shadow-[var(--accent-tangerine)]/20 transition-all cursor-pointer uppercase tracking-wider text-xs"
          >
            <span>Live-Demo Starten (Siemens IKT)</span>
            <ArrowRight className="w-4 h-4 stroke-[2.5]" />
          </button>

          <button
            onClick={onOpenAuth}
            className="flex items-center gap-2 px-6 py-3 rounded-xl bg-[var(--surface-card)] hover:bg-[var(--surface-dark)] text-[var(--foreground)] border border-[var(--surface-border)] hover:border-[var(--accent-tangerine)] font-bold transition-all shadow-sm cursor-pointer"
          >
            <Lock className="w-4 h-4 text-[var(--accent-tangerine)]" />
            <span>Anmelden / Registrieren</span>
          </button>

          <button
            onClick={onExploreWorkbench}
            className="flex items-center gap-2 px-5 py-3 rounded-xl bg-[var(--surface-dark)] hover:bg-[var(--surface-card)] text-[var(--foreground)] opacity-80 hover:opacity-100 border border-[var(--surface-border)] font-bold transition-all cursor-pointer"
          >
            <span>Direkt zur Prüfbank</span>
          </button>
        </div>

        {/* Trust & Compliance Metric Badges */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3 max-w-4xl mx-auto pt-10 text-left font-mono">
          <div className="p-3.5 rounded-xl bg-[var(--surface-card)] border border-[var(--surface-border)] shadow-sm">
            <div className="text-[10px] opacity-60 uppercase font-bold">Aufsichtsbehörde</div>
            <div className="text-sm font-bold text-[var(--foreground)] mt-0.5">BaFin / EZB</div>
            <div className="text-[10px] text-emerald-500 font-bold mt-1">DORA Pillar IV Konform</div>
          </div>
          <div className="p-3.5 rounded-xl bg-[var(--surface-card)] border border-[var(--surface-border)] shadow-sm">
            <div className="text-[10px] opacity-60 uppercase font-bold">Datensouveränität</div>
            <div className="text-sm font-bold text-[var(--foreground)] mt-0.5">BDSG § 26 / DSGVO</div>
            <div className="text-[10px] text-emerald-500 font-bold mt-1">Node Frankfurt a. M.</div>
          </div>
          <div className="p-3.5 rounded-xl bg-[var(--surface-card)] border border-[var(--surface-border)] shadow-sm">
            <div className="text-[10px] opacity-60 uppercase font-bold">E-Rechnungspflicht</div>
            <div className="text-sm font-bold text-[var(--foreground)] mt-0.5">ZUGFeRD 2.3</div>
            <div className="text-[10px] text-emerald-500 font-bold mt-1">EN 16931 / Factur-X</div>
          </div>
          <div className="p-3.5 rounded-xl bg-[var(--surface-card)] border border-[var(--surface-border)] shadow-sm">
            <div className="text-[10px] opacity-60 uppercase font-bold">Sicherheitsstufe</div>
            <div className="text-sm font-bold text-[var(--foreground)] mt-0.5">DIN 66399</div>
            <div className="text-[10px] text-emerald-500 font-bold mt-1">Schutzklasse 3 Validiert</div>
          </div>
        </div>
      </section>

      {/* 2. Core Modules Architecture */}
      <section className="py-16 px-6 max-w-6xl mx-auto border-t border-[var(--surface-border)] space-y-10">
        <div className="text-center space-y-2">
          <span className="text-xs font-mono font-bold uppercase tracking-widest text-[var(--accent-tangerine)]">
            Enterprise Module
          </span>
          <h2 className="text-2xl sm:text-3xl font-black font-mono">
            Vollständige Prüfung von IKT-Drittparteirisiken
          </h2>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {/* Card 1 */}
          <div className="p-6 rounded-2xl bg-[var(--surface-card)] border border-[var(--surface-border)] shadow-sm space-y-4 hover:border-[var(--accent-tangerine)]/40 transition-colors">
            <div className="w-12 h-12 rounded-xl bg-[var(--accent-tangerine)]/15 border border-[var(--accent-tangerine)]/30 flex items-center justify-center text-[var(--accent-tangerine)]">
              <Shield className="w-6 h-6 stroke-[2.5]" />
            </div>
            <h3 className="font-mono font-bold text-sm text-[var(--foreground)]">
              DORA Art. 30 Prüfung
            </h3>
            <p className="text-xs text-[var(--foreground)] opacity-70 leading-relaxed font-sans">
              Prüfung wesentlicher Vertragsklauseln: 60 Tage Kündigungsfrist, 90 Tage
              Migrationszusicherung und 30 Tage Widerspruchsrecht bei Unterauftragnehmern.
            </p>
            <div className="pt-2 text-[11px] font-mono font-bold text-[var(--accent-tangerine)] flex items-center gap-1">
              <span>VO (EU) 2022/2554</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </div>
          </div>

          {/* Card 2 */}
          <div className="p-6 rounded-2xl bg-[var(--surface-card)] border border-[var(--surface-border)] shadow-sm space-y-4 hover:border-[var(--accent-tangerine)]/40 transition-colors">
            <div className="w-12 h-12 rounded-xl bg-sky-500/15 border border-sky-500/30 flex items-center justify-center text-sky-500">
              <FileSpreadsheet className="w-6 h-6 stroke-[2.5]" />
            </div>
            <h3 className="font-mono font-bold text-sm text-[var(--foreground)]">
              ZUGFeRD 2.3 & Factur-X
            </h3>
            <p className="text-xs text-[var(--foreground)] opacity-70 leading-relaxed font-sans">
              Validierung hybrider PDF/XML Rechnungsdaten gem. EN 16931 und dem
              Wachstumschancengesetz. Automatische Leitweg-ID und Umsatzsteuer-Prüfung.
            </p>
            <div className="pt-2 text-[11px] font-mono font-bold text-sky-500 flex items-center gap-1">
              <span>Wachstumschancengesetz 2025</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </div>
          </div>

          {/* Card 3 */}
          <div className="p-6 rounded-2xl bg-[var(--surface-card)] border border-[var(--surface-border)] shadow-sm space-y-4 hover:border-[var(--accent-tangerine)]/40 transition-colors">
            <div className="w-12 h-12 rounded-xl bg-emerald-500/15 border border-emerald-500/30 flex items-center justify-center text-emerald-500">
              <Languages className="w-6 h-6 stroke-[2.5]" />
            </div>
            <h3 className="font-mono font-bold text-sm text-[var(--foreground)]">
              Beglaubigtes englisches Dossier
            </h3>
            <p className="text-xs text-[var(--foreground)] opacity-70 leading-relaxed font-sans">
              Automatische klauselweise Übersetzung für internationale Vorstände und
              Aufsichtsgremien mit SHA-256 Prüffingerabdruck und PDF-Download.
            </p>
            <div className="pt-2 text-[11px] font-mono font-bold text-emerald-500 flex items-center gap-1">
              <span>DIN EN 15038 Parität</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </div>
          </div>
        </div>
      </section>

      {/* 3. Footer */}
      <footer className="border-t border-[var(--surface-border)] bg-[var(--surface-dark)] py-8 px-6 text-center text-xs font-mono opacity-60">
        <p>DocuNorm AI © 2026 · Entwickelt für BaFin & europäische IKT-Compliance</p>
        <p className="text-[10px] mt-1">Frankfurt am Main · DIN 66399 Schutzklasse 3 · BDSG § 26 Konform</p>
      </footer>
    </div>
  );
}

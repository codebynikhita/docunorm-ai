"use client";

import React, { useState, useEffect } from "react";
import {
  ShieldCheck,
  CheckCircle2,
  Lock,
  Cpu,
  FileSpreadsheet,
  Database,
  Loader2,
  Sparkles,
} from "lucide-react";

import { Language } from "@/lib/i18n";

interface IngestionModalProps {
  isOpen: boolean;
  filename: string;
  fileSizeBytes: number;
  onComplete: () => void;
  lang?: Language;
}

export function IngestionModal({
  isOpen,
  filename,
  fileSizeBytes,
  onComplete,
  lang = "DE",
}: IngestionModalProps) {
  const [currentStep, setCurrentStep] = useState(0);

  const steps = [
    {
      title:
        lang === "DE"
          ? "Kryptografischer SHA-256 Fingerabdruck"
          : "Cryptographic SHA-256 Fingerprinting",
      desc:
        lang === "DE"
          ? "Berechnung des manipulationssicheren Hashs zur Duplikatvermeidung"
          : "Computing tamper-proof hash for duplicate prevention",
      icon: ShieldCheck,
      color: "text-[#00e5ff]",
    },
    {
      title:
        lang === "DE"
          ? "Strukturelle Koordinaten-Extraktion"
          : "Structural Coordinate Extraction",
      desc:
        lang === "DE"
          ? "PyMuPDF-Zuordnung von Absätzen zu exakten [x0, y0, x1, y1] Koordinaten"
          : "PyMuPDF mapping paragraphs to exact [x0, y0, x1, y1] coordinates",
      icon: Cpu,
      color: "text-[#ff5500]",
    },
    {
      title:
        lang === "DE"
          ? "Deutsche DSGVO / PII Redaktions-Firewall"
          : "German PII Redaction Firewall",
      desc:
        lang === "DE"
          ? "Automatische Schwärzung von IBANs, Steuer-IDs, E-Mails und Telefonnummern"
          : "Masking German IBANs, Steuer-ID, emails, and phone numbers",
      icon: Lock,
      color: "text-[#ffaa00]",
    },
    {
      title:
        lang === "DE"
          ? "1024-Dimensionale Semantische Vektorisierung"
          : "1024-Dimensional Semantic Vectorization",
      desc:
        lang === "DE"
          ? "Generierung normalisierter Einbettungen kompatibel mit pgvector"
          : "Generating normalized embeddings compatible with pgvector",
      icon: Sparkles,
      color: "text-[#00e5ff]",
    },
    {
      title:
        lang === "DE"
          ? "ZUGFeRD EN 16931 Datenstrom-Analyse"
          : "ZUGFeRD EN 16931 Stream Analysis",
      desc:
        lang === "DE"
          ? "Prüfung auf eingebettete hybride XML-Rechnungsanhänge"
          : "Probing for embedded XML invoice attachments",
      icon: FileSpreadsheet,
      color: "text-[#c6f000]",
    },
    {
      title:
        lang === "DE"
          ? "PostgreSQL & Revisions-Protokoll Speicherung"
          : "PostgreSQL & GDPR Audit Trail Commit",
      desc:
        lang === "DE"
          ? "Persistierung atomarer Abschnitte und unveränderbares Audit-Ledger"
          : "Persisting atomic chunks and recording immutable access ledger",
      icon: Database,
      color: "text-[#c6f000]",
    },
  ];

  useEffect(() => {
    if (!isOpen) {
      setCurrentStep(0);
      return;
    }

    // Advance step sequentially to show live telemetry
    const timer = setInterval(() => {
      setCurrentStep((prev) => {
        if (prev < steps.length - 1) {
          return prev + 1;
        }
        clearInterval(timer);
        return prev;
      });
    }, 450);

    return () => clearInterval(timer);
  }, [isOpen]);

  if (!isOpen) return null;

  const isDone = currentStep === steps.length - 1;

  return (
    <div className="fixed inset-0 z-50 bg-[#06080e]/85 backdrop-blur-md flex items-center justify-center p-4">
      <div className="w-full max-w-lg bg-[#0c101c] border border-[#1d263b] rounded-2xl shadow-2xl p-6 space-y-5 animate-in zoom-in-95 duration-200">
        {/* Header */}
        <div className="flex items-center justify-between border-b border-[#1b2336] pb-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-[#ff5500]/15 border border-[#ff5500]/40 flex items-center justify-center text-[#ff5500] shadow-[0_0_15px_rgba(255,85,0,0.2)]">
              <ShieldCheck className="w-5 h-5" />
            </div>
            <div>
              <h3 className="text-sm font-extrabold text-white tracking-wide font-mono">
                {lang === "DE" ? "Regulatorische Ingestions-Pipeline" : "Regulatory Ingestion Pipeline"}
              </h3>
              <p className="text-xs text-zinc-400 font-mono truncate max-w-[280px]">
                {filename} ({Math.round(fileSizeBytes / 1024)} KB)
              </p>
            </div>
          </div>
          <span className="text-[10px] uppercase font-mono px-2 py-0.5 rounded bg-[#c6f000]/15 text-[#c6f000] border border-[#c6f000]/30 font-bold">
            EU DORA & BDSG
          </span>
        </div>

        {/* Pipeline Stepper */}
        <div className="space-y-2.5">
          {steps.map((step, idx) => {
            const Icon = step.icon;
            const isCompleted = idx < currentStep || (idx === currentStep && isDone);
            const isRunning = idx === currentStep && !isDone;

            return (
              <div
                key={idx}
                className={`flex items-start gap-3 p-2.5 rounded-lg border transition-all ${
                  isRunning
                    ? "bg-[#131929] border-[#ff5500]/60 shadow-[0_0_12px_rgba(255,85,0,0.15)]"
                    : isCompleted
                    ? "bg-[#0f1422] border-[#1a2336]"
                    : "opacity-35 border-transparent"
                }`}
              >
                <div className="mt-0.5">
                  {isCompleted ? (
                    <CheckCircle2 className="w-4 h-4 text-[#c6f000]" />
                  ) : isRunning ? (
                    <Loader2 className="w-4 h-4 animate-spin text-[#ff5500]" />
                  ) : (
                    <Icon className="w-4 h-4 text-zinc-600" />
                  )}
                </div>
                <div className="flex-1">
                  <div className="flex items-center justify-between">
                    <p className="text-xs font-bold text-zinc-100 font-mono">{step.title}</p>
                    {isCompleted && (
                      <span className="text-[10px] font-mono text-[#c6f000] font-black uppercase tracking-wider">
                        OK
                      </span>
                    )}
                  </div>
                  <p className="text-[11px] text-zinc-400 leading-tight mt-0.5 font-sans">
                    {step.desc}
                  </p>
                </div>
              </div>
            );
          })}
        </div>

        {/* Footer Action */}
        <div className="pt-2 flex justify-end">
          <button
            onClick={onComplete}
            disabled={!isDone}
            className="w-full py-2.5 px-4 rounded-lg bg-[#ff5500] hover:bg-[#ff6a00] disabled:opacity-40 text-black font-black font-mono text-xs transition-all shadow-[0_0_20px_rgba(255,85,0,0.4)] cursor-pointer uppercase tracking-wider"
          >
            {isDone
              ? (lang === "DE" ? "Bereit • In Prüfbank öffnen" : "Ready • Open in Workbench")
              : (lang === "DE" ? "Pipeline wird ausgeführt..." : "Executing Ingestion Pipeline...")}
          </button>
        </div>
      </div>
    </div>
  );
}

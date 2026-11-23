"use client";

import React, { useState, useEffect, useCallback } from "react";
import {
  ShieldAlert,
  ShieldCheck,
  Zap,
  Activity,
  Download,
  Flame,
  CheckCircle2,
  Clock,
  Layers,
  Server,
  RefreshCw,
  X,
  FileCheck,
  Lock,
} from "lucide-react";
import {
  getLatestHardeningBenchmark,
  runHardeningBenchmark,
  downloadBenchmarkCertificatePdf,
  HardeningBenchmarkReport,
} from "@/lib/api";
import { Language } from "@/lib/i18n";

interface EnterpriseHardeningModalProps {
  isOpen: boolean;
  onClose: () => void;
  lang: Language;
}

export function EnterpriseHardeningModal({
  isOpen,
  onClose,
  lang,
}: EnterpriseHardeningModalProps) {
  const [report, setReport] = useState<HardeningBenchmarkReport | null>(null);
  const [isRunning, setIsRunning] = useState(false);
  const [isDownloading, setIsDownloading] = useState(false);

  const fetchBenchmark = useCallback(async () => {
    try {
      const data = await getLatestHardeningBenchmark();
      setReport(data);
    } catch (e) {
      console.error("Failed to fetch hardening benchmark:", e);
    }
  }, []);

  useEffect(() => {
    if (isOpen) {
      fetchBenchmark();
    }
  }, [isOpen, fetchBenchmark]);

  if (!isOpen) return null;

  const handleRunStressTest = async () => {
    setIsRunning(true);
    try {
      const newReport = await runHardeningBenchmark(60, 15);
      setReport(newReport);
    } catch (e) {
      console.error("Failed to run stress test:", e);
    } finally {
      setIsRunning(false);
    }
  };

  const handleDownloadPdf = async () => {
    setIsDownloading(true);
    try {
      await downloadBenchmarkCertificatePdf();
    } catch (e) {
      console.error("Failed to download PDF:", e);
    } finally {
      setIsDownloading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-3 sm:p-5 bg-black/80 backdrop-blur-md animate-in fade-in duration-200">
      <div className="relative w-full max-w-4xl bg-[var(--surface-dark)] border border-purple-500/40 rounded-2xl shadow-2xl flex flex-col max-h-[92vh] overflow-hidden text-[var(--foreground)]">
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-slate-800 bg-slate-900/70 shrink-0">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-purple-500/15 border border-purple-500/30 flex items-center justify-center text-purple-400">
              <ShieldCheck className="w-5 h-5 text-purple-400" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h2 className="text-base font-bold text-white tracking-tight">
                  {lang === "DE"
                    ? "Week 5 Capstone: Enterprise-Härtungsbenchmark & 100k-Token Stresstest"
                    : "Week 5 Capstone: Enterprise Hardening Benchmark & 100k-Token Stress Test"}
                </h2>
                <span className="px-2 py-0.5 rounded-full text-[10px] font-mono font-bold bg-emerald-500/15 border border-emerald-500/40 text-emerald-400">
                  {report ? `${report.overall_score_pct}% READY` : "READY"}
                </span>
              </div>
              <p className="text-xs text-slate-400 font-mono mt-0.5">
                <span>DORA Art. 30 · BaFin KWG § 25b · EU AI Act Art. 12 Revisionssiegel</span>
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={handleRunStressTest}
              disabled={isRunning}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-purple-600 hover:bg-purple-500 text-white font-mono text-xs font-bold transition-all cursor-pointer disabled:opacity-50 shadow-sm"
            >
              <RefreshCw className={`w-3.5 h-3.5 ${isRunning ? "animate-spin" : ""}`} />
              <span>{isRunning ? (lang === "DE" ? "Prüfung läuft..." : "Testing...") : (lang === "DE" ? "Stresstest starten" : "Run Stress Test")}</span>
            </button>

            <button
              onClick={handleDownloadPdf}
              disabled={isDownloading}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 border border-slate-700 text-slate-200 font-mono text-xs font-bold transition-all cursor-pointer disabled:opacity-50"
              title="Download DIN 5008 Master Certificate PDF"
            >
              <Download className={`w-3.5 h-3.5 ${isDownloading ? "animate-bounce" : ""}`} />
              <span className="hidden sm:inline">PDF</span>
            </button>

            <button
              onClick={onClose}
              className="p-1.5 rounded-lg bg-slate-800 border border-slate-700 hover:bg-rose-500/20 text-slate-400 hover:text-rose-400 transition-all cursor-pointer"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* Body */}
        <div className="flex-1 overflow-y-auto p-6 space-y-6">
          {report ? (
            <>
              {/* Scorecard Hero Banner */}
              <div className="p-4 rounded-xl bg-gradient-to-r from-purple-950/40 via-slate-900 to-slate-900 border border-purple-500/30 flex flex-col md:flex-row items-center justify-between gap-4">
                <div className="space-y-1">
                  <div className="flex items-center gap-2 text-xs font-mono text-purple-400 font-bold uppercase tracking-wider">
                    <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                    <span>{report.status}</span>
                  </div>
                  <div className="text-xl font-bold text-white font-mono">
                    {lang === "DE" ? "Enterprise-SLA & Ausfallsicherheit zertifiziert" : "Enterprise SLA & Resilience Certified"}
                  </div>
                  <p className="text-xs text-slate-400 font-mono">
                    ID: {report.benchmark_id} · {report.run_at.substring(0, 19)} · {report.certifying_authority}
                  </p>
                </div>

                <div className="text-right shrink-0">
                  <div className="text-3xl font-extrabold font-mono text-emerald-400">
                    {report.overall_score_pct}%
                  </div>
                  <div className="text-[10px] font-mono text-slate-400">
                    SLA Benchmark Score
                  </div>
                </div>
              </div>

              {/* 4 Primary Performance Metric Cards */}
              <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                <div className="p-3.5 rounded-xl bg-slate-900/60 border border-slate-800 space-y-1">
                  <div className="text-slate-400 text-xs font-mono flex items-center justify-between">
                    <span>{lang === "DE" ? "Korpus-Volumen" : "Corpus Volume"}</span>
                    <Layers className="w-4 h-4 text-blue-400" />
                  </div>
                  <div className="text-2xl font-bold font-mono text-white">
                    {report.corpus.total_tokens.toLocaleString()}
                  </div>
                  <div className="text-[11px] font-mono text-slate-400">
                    {report.corpus.total_pages} {lang === "DE" ? "Seiten (4 Mandanten)" : "Pages (4 Tenants)"}
                  </div>
                </div>

                <div className="p-3.5 rounded-xl bg-slate-900/60 border border-slate-800 space-y-1">
                  <div className="text-slate-400 text-xs font-mono flex items-center justify-between">
                    <span>{lang === "DE" ? "Durchsatz" : "Throughput"}</span>
                    <Zap className="w-4 h-4 text-amber-400" />
                  </div>
                  <div className="text-2xl font-bold font-mono text-amber-400">
                    {report.throughput.requests_per_second} req/s
                  </div>
                  <div className="text-[11px] font-mono text-slate-400">
                    {report.throughput.concurrent_streams} {lang === "DE" ? "parallele Streams" : "concurrent streams"}
                  </div>
                </div>

                <div className="p-3.5 rounded-xl bg-slate-900/60 border border-slate-800 space-y-1">
                  <div className="text-slate-400 text-xs font-mono flex items-center justify-between">
                    <span>{lang === "DE" ? "Latenz P95" : "Latency P95"}</span>
                    <Clock className="w-4 h-4 text-emerald-400" />
                  </div>
                  <div className="text-2xl font-bold font-mono text-emerald-400">
                    {report.latencies.p95_ms} ms
                  </div>
                  <div className="text-[11px] font-mono text-slate-400">
                    P50: {report.latencies.p50_ms}ms · P99: {report.latencies.p99_ms}ms
                  </div>
                </div>

                <div className="p-3.5 rounded-xl bg-slate-900/60 border border-slate-800 space-y-1">
                  <div className="text-slate-400 text-xs font-mono flex items-center justify-between">
                    <span>{lang === "DE" ? "Cache Deduplizierung" : "Deduplication"}</span>
                    <Flame className="w-4 h-4 text-purple-400" />
                  </div>
                  <div className="text-2xl font-bold font-mono text-purple-400">
                    {report.cache.deduplication_ratio_pct}%
                  </div>
                  <div className="text-[11px] font-mono text-slate-400">
                    {report.cache.tokens_saved.toLocaleString()} Tokens {lang === "DE" ? "gespart" : "saved"}
                  </div>
                </div>
              </div>

              {/* Resilience & Isolation Grid */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800 space-y-3 font-mono text-xs">
                  <h3 className="text-xs font-bold text-slate-200 uppercase tracking-wider flex items-center gap-1.5">
                    <Lock className="w-4 h-4 text-emerald-400" />
                    <span>{lang === "DE" ? "Mandanten-Isolation & Sicherheit" : "Tenant Isolation & Security"}</span>
                  </h3>

                  <div className="space-y-2">
                    <div className="flex justify-between p-2 rounded bg-slate-800/40 border border-slate-800">
                      <span className="text-slate-400">RLS Boundary Leakage:</span>
                      <span className="text-emerald-400 font-bold">
                        {report.resilience.tenant_isolation_leakage_detected ? "LEAK DETECTED" : "0% (PASSED)"}
                      </span>
                    </div>
                    <div className="flex justify-between p-2 rounded bg-slate-800/40 border border-slate-800">
                      <span className="text-slate-400">Redis In-Memory Fallback:</span>
                      <span className="text-emerald-400 font-bold">
                        {report.resilience.redis_fallback_successful ? "SOVEREIGN AIR-GAPPED" : "FAILED"}
                      </span>
                    </div>
                    <div className="flex justify-between p-2 rounded bg-slate-800/40 border border-slate-800">
                      <span className="text-slate-400">SSE Abort Memory Cleanup:</span>
                      <span className="text-emerald-400 font-bold">
                        {report.resilience.sse_abort_cleanup_successful ? "CLEAN" : "DIRTY"}
                      </span>
                    </div>
                  </div>
                </div>

                <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800 space-y-3 font-mono text-xs">
                  <h3 className="text-xs font-bold text-slate-200 uppercase tracking-wider flex items-center gap-1.5">
                    <Server className="w-4 h-4 text-purple-400" />
                    <span>{lang === "DE" ? "Latenz-Verteilung (Cache vs. KI)" : "Latency Breakdown (Cache vs. LLM)"}</span>
                  </h3>

                  <div className="space-y-2">
                    <div className="flex justify-between p-2 rounded bg-slate-800/40 border border-slate-800">
                      <span className="text-slate-400">Cache O(1) Hash Latency P50:</span>
                      <span className="text-purple-400 font-bold">{report.latencies.cached_p50_ms} ms</span>
                    </div>
                    <div className="flex justify-between p-2 rounded bg-slate-800/40 border border-slate-800">
                      <span className="text-slate-400">Synthese-Latenz (Cold LLM) P50:</span>
                      <span className="text-slate-200 font-bold">{report.latencies.llm_p50_ms} ms</span>
                    </div>
                    <div className="flex justify-between p-2 rounded bg-slate-800/40 border border-slate-800">
                      <span className="text-slate-400">Wartezeit-Einsparung (Total):</span>
                      <span className="text-emerald-400 font-bold">{report.cache.latency_saved_seconds}s</span>
                    </div>
                  </div>
                </div>
              </div>

              {/* SHA-256 Ledger Seal */}
              <div className="p-3.5 rounded-xl bg-slate-950 border border-purple-500/30 text-xs font-mono space-y-1">
                <div className="flex items-center justify-between text-slate-400">
                  <span className="font-bold text-purple-400">SHA-256 REVISIONSSIEGEL:</span>
                  <span className="text-[10px] text-slate-500">BSI TR-03103 / EU AI Act Art. 12</span>
                </div>
                <div className="text-[11px] text-slate-300 break-all select-all">
                  {report.sha256_attestation}
                </div>
              </div>
            </>
          ) : (
            <div className="p-12 text-center text-slate-500 font-mono text-xs">
              <RefreshCw className="w-6 h-6 animate-spin mx-auto mb-2 text-purple-400" />
              <span>{lang === "DE" ? "Lade Härtungsbenchmark..." : "Loading Hardening Benchmark..."}</span>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

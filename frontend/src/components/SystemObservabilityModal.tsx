"use client";

import React, { useState, useEffect, useCallback } from "react";
import {
  Activity,
  AlertTriangle,
  CheckCircle2,
  Clock,
  Copy,
  ExternalLink,
  Flame,
  Layers,
  Network,
  RefreshCw,
  Server,
  ShieldCheck,
  Terminal,
  X,
  Zap,
} from "lucide-react";
import {
  getMetricsSummary,
  getRecentTraces,
  getPrometheusRawMetrics,
  MetricsSummaryResponse,
  RecentTracesResponse,
} from "@/lib/api";
import { Language } from "@/lib/i18n";

interface SystemObservabilityModalProps {
  isOpen: boolean;
  onClose: () => void;
  lang: Language;
}

export function SystemObservabilityModal({
  isOpen,
  onClose,
  lang,
}: SystemObservabilityModalProps) {
  const [activeTab, setActiveTab] = useState<"kpis" | "traces" | "raw">("kpis");
  const [summary, setSummary] = useState<MetricsSummaryResponse | null>(null);
  const [traces, setTraces] = useState<RecentTracesResponse | null>(null);
  const [rawMetrics, setRawMetrics] = useState<string>("");
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [isAutoRefresh, setIsAutoRefresh] = useState<boolean>(true);
  const [copiedKey, setCopiedKey] = useState<string | null>(null);
  const [selectedSpanId, setSelectedSpanId] = useState<string | null>(null);

  const fetchData = useCallback(async () => {
    setIsLoading(true);
    try {
      const [sumData, traceData] = await Promise.all([
        getMetricsSummary().catch(() => null),
        getRecentTraces(25).catch(() => null),
      ]);
      if (sumData) setSummary(sumData);
      if (traceData) setTraces(traceData);

      if (activeTab === "raw") {
        const raw = await getPrometheusRawMetrics().catch(() => "");
        setRawMetrics(raw);
      }
    } catch (e) {
      console.error("Failed to load telemetry:", e);
    } finally {
      setIsLoading(false);
    }
  }, [activeTab]);

  useEffect(() => {
    if (!isOpen) return;
    fetchData();

    if (!isAutoRefresh) return;
    const interval = setInterval(() => {
      fetchData();
    }, 4000);
    return () => clearInterval(interval);
  }, [isOpen, isAutoRefresh, fetchData]);

  if (!isOpen) return null;

  const handleCopy = (text: string, key: string) => {
    navigator.clipboard.writeText(text);
    setCopiedKey(key);
    setTimeout(() => setCopiedKey(null), 2000);
  };

  const formatUptime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    if (mins < 60) return `${mins}m ${secs}s`;
    const hours = Math.floor(mins / 60);
    return `${hours}h ${mins % 60}m`;
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-3 sm:p-5 bg-black/80 backdrop-blur-md animate-in fade-in duration-200">
      <div className="relative w-full max-w-5xl bg-[var(--surface-dark)] border border-slate-700/80 rounded-2xl shadow-2xl flex flex-col max-h-[92vh] overflow-hidden text-[var(--foreground)]">
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-slate-800 bg-slate-900/60 shrink-0">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-purple-500/15 border border-purple-500/30 flex items-center justify-center text-purple-400">
              <Activity className="w-5 h-5 animate-pulse" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h2 className="text-base font-bold text-white tracking-tight">
                  {lang === "DE"
                    ? "Prometheus & OpenTelemetry Aufsichts-Telemetrie"
                    : "Prometheus & OpenTelemetry Regulatory Observability"}
                </h2>
                <span className="px-2 py-0.5 rounded-full text-[10px] font-mono font-bold bg-emerald-500/15 border border-emerald-500/40 text-emerald-400">
                  {summary?.status || "HEALTHY"}
                </span>
              </div>
              <p className="text-xs text-slate-400 font-mono flex items-center gap-2 mt-0.5">
                <span>Frankfurt eu-central-1</span>
                <span>•</span>
                <span>{summary ? `Uptime: ${formatUptime(summary.uptime_seconds)}` : "Connecting..."}</span>
                <span>•</span>
                <span className="text-purple-400">W3C TraceContext RFC</span>
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={() => setIsAutoRefresh((prev) => !prev)}
              className={`px-2.5 py-1.5 rounded-lg text-xs font-mono font-medium border transition-all cursor-pointer flex items-center gap-1.5 ${
                isAutoRefresh
                  ? "bg-emerald-500/15 border-emerald-500/40 text-emerald-400"
                  : "bg-slate-800 border-slate-700 text-slate-400 hover:text-white"
              }`}
              title={lang === "DE" ? "Live-Aktualisierung (4s)" : "Live Polling (4s)"}
            >
              <RefreshCw className={`w-3.5 h-3.5 ${isAutoRefresh && isLoading ? "animate-spin" : ""}`} />
              <span className="hidden sm:inline">{isAutoRefresh ? "Auto (4s)" : "Paused"}</span>
            </button>

            <button
              onClick={fetchData}
              className="p-1.5 rounded-lg bg-slate-800 border border-slate-700 hover:bg-slate-700 text-slate-300 hover:text-white transition-all cursor-pointer"
              title="Manual Refresh"
            >
              <RefreshCw className={`w-4 h-4 ${isLoading ? "animate-spin text-purple-400" : ""}`} />
            </button>

            <button
              onClick={onClose}
              className="p-1.5 rounded-lg bg-slate-800 border border-slate-700 hover:bg-rose-500/20 hover:border-rose-500/40 text-slate-400 hover:text-rose-400 transition-all cursor-pointer"
              title="Close"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* Tab Navigation */}
        <div className="flex items-center gap-1 px-6 pt-3 pb-2 border-b border-slate-800 bg-slate-900/30 text-xs font-mono shrink-0">
          <button
            onClick={() => setActiveTab("kpis")}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg transition-all font-bold cursor-pointer ${
              activeTab === "kpis"
                ? "bg-[var(--accent-tangerine)] text-black shadow-sm"
                : "text-slate-400 hover:text-white hover:bg-slate-800/60"
            }`}
          >
            <Layers className="w-3.5 h-3.5" />
            <span>{lang === "DE" ? "Prometheus Metriken & KPIs" : "Prometheus Metrics & KPIs"}</span>
          </button>

          <button
            onClick={() => setActiveTab("traces")}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg transition-all font-bold cursor-pointer ${
              activeTab === "traces"
                ? "bg-[var(--accent-tangerine)] text-black shadow-sm"
                : "text-slate-400 hover:text-white hover:bg-slate-800/60"
            }`}
          >
            <Network className="w-3.5 h-3.5" />
            <span>{lang === "DE" ? "OpenTelemetry Spans & Traces" : "OpenTelemetry Spans & Traces"}</span>
            {traces && (
              <span className="px-1.5 py-0.2 rounded-full text-[10px] bg-purple-500/20 text-purple-300 border border-purple-500/40">
                {traces.total_spans}
              </span>
            )}
          </button>

          <button
            onClick={() => {
              setActiveTab("raw");
              getPrometheusRawMetrics().then(setRawMetrics);
            }}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg transition-all font-bold cursor-pointer ${
              activeTab === "raw"
                ? "bg-[var(--accent-tangerine)] text-black shadow-sm"
                : "text-slate-400 hover:text-white hover:bg-slate-800/60"
            }`}
          >
            <Terminal className="w-3.5 h-3.5" />
            <span>{lang === "DE" ? "Prometheus /metrics Rohdaten" : "Prometheus /metrics Scrape"}</span>
          </button>
        </div>

        {/* Content Body */}
        <div className="flex-1 overflow-y-auto p-6 space-y-6">
          {activeTab === "kpis" && summary && (
            <div className="space-y-6">
              {/* Top KPI Cards Grid */}
              <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                <div className="p-3.5 rounded-xl bg-slate-900/60 border border-slate-800 shadow-sm space-y-1">
                  <div className="flex items-center justify-between text-slate-400 text-xs font-mono">
                    <span>{lang === "DE" ? "HTTP Anfragen" : "HTTP Requests"}</span>
                    <Server className="w-4 h-4 text-blue-400" />
                  </div>
                  <div className="text-2xl font-bold font-mono text-white">
                    {summary.traffic.total_requests.toLocaleString()}
                  </div>
                  <div className="text-[11px] font-mono text-emerald-400 flex items-center gap-1">
                    <CheckCircle2 className="w-3 h-3" />
                    <span>Fehlerrate: {summary.traffic.error_rate_pct}%</span>
                  </div>
                </div>

                <div className="p-3.5 rounded-xl bg-slate-900/60 border border-slate-800 shadow-sm space-y-1">
                  <div className="flex items-center justify-between text-slate-400 text-xs font-mono">
                    <span>{lang === "DE" ? "Aktive SSE Streams" : "Active SSE Streams"}</span>
                    <Zap className="w-4 h-4 text-emerald-400" />
                  </div>
                  <div className="text-2xl font-bold font-mono text-emerald-400 flex items-center gap-2">
                    {summary.active_sse_streams}
                    {summary.active_sse_streams > 0 && (
                      <span className="relative flex h-2 w-2">
                        <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                        <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
                      </span>
                    )}
                  </div>
                  <div className="text-[11px] font-mono text-slate-400">
                    Live Concurrency Gauge
                  </div>
                </div>

                <div className="p-3.5 rounded-xl bg-slate-900/60 border border-slate-800 shadow-sm space-y-1">
                  <div className="flex items-center justify-between text-slate-400 text-xs font-mono">
                    <span>{lang === "DE" ? "Cache Trefferquote" : "Cache Hit Ratio"}</span>
                    <Zap className="w-4 h-4 text-purple-400" />
                  </div>
                  <div className="text-2xl font-bold font-mono text-purple-400">
                    {summary.semantic_cache.hit_ratio_pct}%
                  </div>
                  <div className="text-[11px] font-mono text-slate-400">
                    {summary.semantic_cache.exact_hits} exakt • {summary.semantic_cache.semantic_hits} semantisch
                  </div>
                </div>

                <div className="p-3.5 rounded-xl bg-slate-900/60 border border-slate-800 shadow-sm space-y-1">
                  <div className="flex items-center justify-between text-slate-400 text-xs font-mono">
                    <span>{lang === "DE" ? "KI Token Verbrauch" : "LLM Tokens"}</span>
                    <Flame className="w-4 h-4 text-amber-400" />
                  </div>
                  <div className="text-2xl font-bold font-mono text-white">
                    {summary.llm_telemetry.total_tokens.toLocaleString()}
                  </div>
                  <div className="text-[11px] font-mono text-slate-400">
                    {summary.llm_telemetry.total_prompt_tokens} in • {summary.llm_telemetry.total_completion_tokens} out
                  </div>
                </div>
              </div>

              {/* Middle Section: Cache Deduplication & Regulatory Findings */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {/* Semantic Cache Deep Dive */}
                <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800 space-y-3">
                  <div className="flex items-center justify-between">
                    <h3 className="text-xs font-bold font-mono text-slate-200 uppercase tracking-wider flex items-center gap-1.5">
                      <Zap className="w-4 h-4 text-purple-400" />
                      <span>{lang === "DE" ? "Dynamischer Semantischer Cache" : "Dynamic Semantic Cache"}</span>
                    </h3>
                    <span className="text-[11px] font-mono text-slate-400">
                      {summary.semantic_cache.total_queries} {lang === "DE" ? "Abfragen" : "Total Queries"}
                    </span>
                  </div>

                  <div className="space-y-2">
                    <div className="flex justify-between text-xs font-mono">
                      <span className="text-slate-400">{lang === "DE" ? "Exakte SHA-256 Treffer" : "Exact Hash Hits"}:</span>
                      <span className="text-emerald-400 font-bold">{summary.semantic_cache.exact_hits}</span>
                    </div>
                    <div className="w-full bg-slate-800 h-1.5 rounded-full overflow-hidden">
                      <div
                        className="bg-emerald-500 h-full rounded-full transition-all duration-500"
                        style={{
                          width: `${summary.semantic_cache.total_queries ? (summary.semantic_cache.exact_hits / summary.semantic_cache.total_queries) * 100 : 0}%`,
                        }}
                      />
                    </div>

                    <div className="flex justify-between text-xs font-mono pt-1">
                      <span className="text-slate-400">{lang === "DE" ? "Vektor-Semantische Treffer" : "Vector Semantic Hits"}:</span>
                      <span className="text-purple-400 font-bold">{summary.semantic_cache.semantic_hits}</span>
                    </div>
                    <div className="w-full bg-slate-800 h-1.5 rounded-full overflow-hidden">
                      <div
                        className="bg-purple-500 h-full rounded-full transition-all duration-500"
                        style={{
                          width: `${summary.semantic_cache.total_queries ? (summary.semantic_cache.semantic_hits / summary.semantic_cache.total_queries) * 100 : 0}%`,
                        }}
                      />
                    </div>

                    <div className="flex justify-between text-xs font-mono pt-1">
                      <span className="text-slate-400">{lang === "DE" ? "Cache Misses (LLM Aufrufe)" : "Cache Misses (LLM Calls)"}:</span>
                      <span className="text-amber-400 font-bold">{summary.semantic_cache.misses}</span>
                    </div>
                    <div className="w-full bg-slate-800 h-1.5 rounded-full overflow-hidden">
                      <div
                        className="bg-amber-500 h-full rounded-full transition-all duration-500"
                        style={{
                          width: `${summary.semantic_cache.total_queries ? (summary.semantic_cache.misses / summary.semantic_cache.total_queries) * 100 : 0}%`,
                        }}
                      />
                    </div>
                  </div>
                </div>

                {/* Regulatory Findings Breakdown */}
                <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800 space-y-3">
                  <div className="flex items-center justify-between">
                    <h3 className="text-xs font-bold font-mono text-slate-200 uppercase tracking-wider flex items-center gap-1.5">
                      <ShieldCheck className="w-4 h-4 text-emerald-400" />
                      <span>{lang === "DE" ? "Aufsichtsrechtliche Befunde" : "Regulatory Findings Radar"}</span>
                    </h3>
                    <span className="text-[11px] font-mono text-slate-400">
                      {summary.regulatory_findings.total_violations} {lang === "DE" ? "Befunde" : "Violations"}
                    </span>
                  </div>

                  <div className="grid grid-cols-2 gap-2 text-xs font-mono">
                    <div className="p-2.5 rounded-lg bg-rose-500/10 border border-rose-500/30 flex items-center justify-between">
                      <span className="text-rose-400 font-bold">CRITICAL</span>
                      <span className="text-white font-bold">{summary.regulatory_findings.by_severity.CRITICAL || 0}</span>
                    </div>
                    <div className="p-2.5 rounded-lg bg-amber-500/10 border border-amber-500/30 flex items-center justify-between">
                      <span className="text-amber-400 font-bold">HIGH</span>
                      <span className="text-white font-bold">{summary.regulatory_findings.by_severity.HIGH || 0}</span>
                    </div>
                    <div className="p-2.5 rounded-lg bg-yellow-500/10 border border-yellow-500/30 flex items-center justify-between">
                      <span className="text-yellow-400 font-bold">MEDIUM</span>
                      <span className="text-white font-bold">{summary.regulatory_findings.by_severity.MEDIUM || 0}</span>
                    </div>
                    <div className="p-2.5 rounded-lg bg-blue-500/10 border border-blue-500/30 flex items-center justify-between">
                      <span className="text-blue-400 font-bold">LOW</span>
                      <span className="text-white font-bold">{summary.regulatory_findings.by_severity.LOW || 0}</span>
                    </div>
                  </div>

                  <div className="text-[11px] font-mono text-slate-400 pt-1 flex items-center gap-2">
                    <span className="font-bold text-slate-300">Frameworks:</span>
                    {Object.entries(summary.regulatory_findings.by_framework).length > 0 ? (
                      Object.entries(summary.regulatory_findings.by_framework).map(([fw, count]) => (
                        <span key={fw} className="px-1.5 py-0.5 rounded bg-slate-800 text-slate-300">
                          {fw}: {count}
                        </span>
                      ))
                    ) : (
                      <span className="text-slate-500">None detected yet</span>
                    )}
                  </div>
                </div>
              </div>

              {/* Endpoint Traffic Breakdown */}
              <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800 space-y-3">
                <h3 className="text-xs font-bold font-mono text-slate-200 uppercase tracking-wider flex items-center gap-1.5">
                  <Server className="w-4 h-4 text-blue-400" />
                  <span>{lang === "DE" ? "API Endpunkt Aufrufe & Verteilung" : "API Endpoints Traffic Distribution"}</span>
                </h3>

                <div className="space-y-1.5 font-mono text-xs">
                  {Object.entries(summary.traffic.requests_by_endpoint).map(([ep, count]) => (
                    <div key={ep} className="flex items-center justify-between p-2 rounded-lg bg-slate-800/40 border border-slate-800">
                      <span className="text-slate-300 truncate max-w-lg">{ep}</span>
                      <span className="px-2 py-0.5 rounded bg-blue-500/15 text-blue-400 border border-blue-500/30 font-bold">
                        {count} req
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}

          {activeTab === "traces" && traces && (
            <div className="space-y-4">
              {/* Active Trace ID header */}
              {traces.active_trace_id && (
                <div className="p-3.5 rounded-xl bg-purple-500/10 border border-purple-500/30 flex items-center justify-between text-xs font-mono">
                  <div className="flex items-center gap-2">
                    <Network className="w-4 h-4 text-purple-400" />
                    <span className="text-slate-300 font-bold">W3C Active Trace ID:</span>
                    <span className="text-purple-300 font-mono select-all">{traces.active_trace_id}</span>
                  </div>
                  <button
                    onClick={() => handleCopy(traces.active_trace_id || "", "active_tid")}
                    className="p-1 rounded hover:bg-purple-500/20 text-purple-400 transition-all cursor-pointer"
                    title="Copy Trace ID"
                  >
                    {copiedKey === "active_tid" ? <CheckCircle2 className="w-4 h-4 text-emerald-400" /> : <Copy className="w-4 h-4" />}
                  </button>
                </div>
              )}

              {/* Spans Waterfall List */}
              <div className="space-y-2">
                {traces.spans.length === 0 ? (
                  <div className="p-8 text-center text-slate-500 font-mono text-xs">
                    {lang === "DE" ? "Keine Spans im Ringpuffer aufgezeichnet." : "No spans recorded in ring buffer yet."}
                  </div>
                ) : (
                  traces.spans.map((span, idx) => {
                    const isSelected = selectedSpanId === `${span.span_id}-${idx}`;
                    return (
                      <div
                        key={`${span.span_id}-${idx}`}
                        onClick={() => setSelectedSpanId(isSelected ? null : `${span.span_id}-${idx}`)}
                        className={`p-3 rounded-xl border transition-all cursor-pointer font-mono text-xs ${
                          isSelected
                            ? "bg-slate-800/90 border-purple-500/60 shadow-md"
                            : "bg-slate-900/50 border-slate-800 hover:border-slate-700"
                        }`}
                      >
                        <div className="flex items-center justify-between">
                          <div className="flex items-center gap-2 min-w-0">
                            <span
                              className={`w-2 h-2 rounded-full ${
                                span.status === "OK" ? "bg-emerald-400" : "bg-rose-400"
                              }`}
                            />
                            <span className="font-bold text-white truncate">{span.name}</span>
                            <span className="text-[10px] text-slate-500 truncate hidden md:inline">
                              {span.span_id.substring(0, 8)}...
                            </span>
                          </div>

                          <div className="flex items-center gap-2 shrink-0">
                            <span className="text-slate-400 font-bold">{span.duration_ms}ms</span>
                            <span
                              className={`px-1.5 py-0.5 rounded text-[10px] font-bold ${
                                span.status === "OK"
                                  ? "bg-emerald-500/15 text-emerald-400 border border-emerald-500/30"
                                  : "bg-rose-500/15 text-rose-400 border border-rose-500/30"
                              }`}
                            >
                              {span.status}
                            </span>
                          </div>
                        </div>

                        {/* Latency Waterfall Bar */}
                        <div className="mt-2 w-full bg-slate-800 h-1 rounded-full overflow-hidden">
                          <div
                            className="bg-purple-500 h-full rounded-full"
                            style={{
                              width: `${Math.min(100, Math.max(5, (span.duration_ms / 200) * 100))}%`,
                            }}
                          />
                        </div>

                        {/* Expanded Span Details */}
                        {isSelected && (
                          <div className="mt-3 pt-3 border-t border-slate-700/60 space-y-2 text-[11px] animate-in fade-in duration-150">
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-2 text-slate-400">
                              <div>
                                <span className="font-bold text-slate-300">Trace ID:</span>{" "}
                                <span className="text-purple-300 select-all">{span.trace_id}</span>
                              </div>
                              <div>
                                <span className="font-bold text-slate-300">Span ID:</span>{" "}
                                <span className="text-purple-300 select-all">{span.span_id}</span>
                              </div>
                              <div>
                                <span className="font-bold text-slate-300">Timestamp:</span>{" "}
                                <span>{span.timestamp}</span>
                              </div>
                              <div>
                                <span className="font-bold text-slate-300">Duration:</span>{" "}
                                <span>{span.duration_ms} ms</span>
                              </div>
                            </div>

                            {Object.keys(span.attributes).length > 0 && (
                              <div className="mt-2 p-2 rounded bg-slate-950/70 border border-slate-800 space-y-1">
                                <span className="font-bold text-slate-400 text-[10px] uppercase">Attributes:</span>
                                <div className="space-y-0.5 text-[10px] font-mono">
                                  {Object.entries(span.attributes).map(([k, v]) => (
                                    <div key={k} className="flex justify-between">
                                      <span className="text-slate-400">{k}:</span>
                                      <span className="text-slate-200 truncate max-w-sm">{String(v)}</span>
                                    </div>
                                  ))}
                                </div>
                              </div>
                            )}
                          </div>
                        )}
                      </div>
                    );
                  })
                )}
              </div>
            </div>
          )}

          {activeTab === "raw" && (
            <div className="space-y-4">
              <div className="flex items-center justify-between text-xs font-mono">
                <span className="text-slate-400">
                  {lang === "DE"
                    ? "Standard Prometheus v0.0.4 Text Exposition Format (Direkt für Prometheus Scraper)"
                    : "Standard Prometheus v0.0.4 Text Exposition (Ready for Prometheus Scraper)"}
                </span>

                <div className="flex items-center gap-2">
                  <button
                    onClick={() => handleCopy(rawMetrics, "raw_metrics")}
                    className="flex items-center gap-1.5 px-2.5 py-1 rounded bg-slate-800 hover:bg-slate-700 text-slate-300 hover:text-white transition-all cursor-pointer font-bold border border-slate-700"
                  >
                    {copiedKey === "raw_metrics" ? <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
                    <span>{copiedKey === "raw_metrics" ? "Copied" : "Copy Exposition"}</span>
                  </button>

                  <a
                    href="http://localhost:8000/metrics"
                    target="_blank"
                    rel="noreferrer"
                    className="flex items-center gap-1.5 px-2.5 py-1 rounded bg-purple-500/20 hover:bg-purple-500/30 text-purple-300 border border-purple-500/40 transition-all font-bold cursor-pointer"
                  >
                    <ExternalLink className="w-3.5 h-3.5" />
                    <span>Open /metrics</span>
                  </a>
                </div>
              </div>

              {/* Scrape Config Snippet */}
              <div className="p-3 rounded-xl bg-slate-950 border border-slate-800 text-[11px] font-mono space-y-1">
                <div className="text-slate-400 font-bold">prometheus.yml (Example Scrape Job):</div>
                <pre className="text-emerald-400 overflow-x-auto p-2 bg-slate-900/80 rounded border border-slate-800">
{`scrape_configs:
  - job_name: 'docunorm-regulatory-ai'
    scrape_interval: 5s
    static_configs:
      - targets: ['localhost:8000']
    metrics_path: '/metrics'`}
                </pre>
              </div>

              {/* Raw Text Window */}
              <div className="p-4 rounded-xl bg-slate-950 border border-slate-800 max-h-[360px] overflow-y-auto">
                <pre className="text-[11px] font-mono text-slate-300 leading-relaxed whitespace-pre-wrap">
                  {rawMetrics || "# Fetching /metrics from backend..."}
                </pre>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

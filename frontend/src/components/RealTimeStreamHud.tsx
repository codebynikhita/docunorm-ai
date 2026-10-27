"use client";

import React, { useState, useEffect } from "react";
import {
  Activity,
  CheckCircle2,
  Cpu,
  Lock,
  Layers,
  Sparkles,
  X,
  Radio,
  FileCheck,
} from "lucide-react";
import { Language } from "@/lib/i18n";

interface StreamEvent {
  stage: string;
  progress: number;
  message: string;
}

interface RealTimeStreamHudProps {
  documentId?: string | null;
  lang: Language;
  onComplete?: () => void;
}

export function RealTimeStreamHud({
  documentId,
  lang,
  onComplete,
}: RealTimeStreamHudProps) {
  const [events, setEvents] = useState<StreamEvent[]>([]);
  const [currentProgress, setCurrentProgress] = useState(0);
  const [currentMessage, setCurrentMessage] = useState("");
  const [isVisible, setIsVisible] = useState(false);
  const isDe = lang === "DE";

  useEffect(() => {
    if (!documentId) {
      setIsVisible(false);
      return;
    }

    const eventSource = new EventSource(
      `http://localhost:8000/api/v1/documents/${documentId}/progress-stream`
    );

    setIsVisible(true);

    eventSource.onmessage = (e) => {
      try {
        const data: StreamEvent = JSON.parse(e.data);
        setCurrentProgress(data.progress || 0);
        setCurrentMessage(data.message || "");
        setEvents((prev) => [...prev.slice(-4), data]);

        if (data.progress >= 100 || data.stage === "complete") {
          eventSource.close();
          if (onComplete) onComplete();
          setTimeout(() => {
            setIsVisible(false);
          }, 3500);
        }
      } catch (err) {
        console.error("Failed to parse SSE event:", err);
      }
    };

    eventSource.onerror = () => {
      eventSource.close();
      setIsVisible(false);
    };

    return () => {
      eventSource.close();
    };
  }, [documentId]);

  if (!isVisible || !documentId) return null;

  return (
    <div className="mx-6 mb-3 p-3 rounded-xl bg-[var(--surface-card)] border border-[var(--surface-border)] shadow-xl flex items-center justify-between gap-4 animate-in slide-in-from-bottom-2 duration-200 z-30 font-mono text-xs">
      <div className="flex items-center gap-3 min-w-0">
        <div className="w-8 h-8 rounded-lg bg-[var(--accent-tangerine)]/15 border border-[var(--accent-tangerine)]/40 flex items-center justify-center text-[var(--accent-tangerine)] shrink-0">
          <Radio className="w-4 h-4 animate-pulse" />
        </div>

        <div className="min-w-0">
          <div className="flex items-center gap-2">
            <span className="text-[10px] font-bold uppercase tracking-wider text-[var(--accent-tangerine)]">
              {isDe ? "Echtzeit-Audit-Stream (SSE)" : "Real-Time Audit Stream (SSE)"}
            </span>
            <span className="text-[9px] bg-emerald-500/15 text-emerald-400 border border-emerald-500/30 px-1.5 py-0.2 rounded font-bold">
              {currentProgress}%
            </span>
          </div>
          <p className="text-[11px] text-[var(--foreground)] opacity-80 truncate mt-0.5 max-w-[500px]">
            {currentMessage || (isDe ? "Verbinde mit Frankfurt Audit-Stream..." : "Connecting to Frankfurt audit stream...")}
          </p>
        </div>
      </div>

      <div className="flex items-center gap-3 shrink-0">
        <div className="w-24 bg-[var(--surface-dark)] h-1.5 rounded-full overflow-hidden border border-[var(--surface-border)] hidden sm:block">
          <div
            className="bg-gradient-to-r from-[var(--accent-tangerine)] to-emerald-400 h-full transition-all duration-300"
            style={{ width: `${currentProgress}%` }}
          />
        </div>
        <button
          onClick={() => setIsVisible(false)}
          className="p-1 rounded-md text-[var(--foreground)] opacity-50 hover:opacity-100 hover:bg-[var(--surface-dark)] cursor-pointer"
        >
          <X className="w-4 h-4" />
        </button>
      </div>
    </div>
  );
}

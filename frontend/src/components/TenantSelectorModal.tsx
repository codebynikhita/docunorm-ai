"use client";

import React, { useState, useEffect } from "react";
import {
  Building2,
  ShieldCheck,
  CheckCircle2,
  X,
  RefreshCw,
  Lock,
  Layers,
  FileText,
} from "lucide-react";
import {
  TenantItem,
  TenantIsolationAuditReport,
  listEnterpriseTenants,
  getCurrentTenantContext,
  runTenantIsolationAudit,
  setActiveTenantSlug,
} from "@/lib/api";

interface TenantSelectorModalProps {
  isOpen: boolean;
  onClose: () => void;
  onTenantSwitched?: (tenant: TenantItem) => void;
}

export function TenantSelectorModal({
  isOpen,
  onClose,
  onTenantSwitched,
}: TenantSelectorModalProps) {
  const [tenants, setTenants] = useState<TenantItem[]>([]);
  const [activeTenant, setActiveTenant] = useState<TenantItem | null>(null);
  const [auditReport, setAuditReport] = useState<TenantIsolationAuditReport | null>(null);
  const [isAuditing, setIsAuditing] = useState(false);

  const loadTenants = React.useCallback(async () => {
    try {
      const all = await listEnterpriseTenants();
      setTenants(all);
      const current = await getCurrentTenantContext();
      setActiveTenant(current);
    } catch (err) {
      console.error("Failed to load enterprise tenants:", err);
    }
  }, []);

  useEffect(() => {
    if (isOpen) {
      loadTenants();
    }
  }, [isOpen, loadTenants]);

  async function handleSwitchTenant(tenant: TenantItem) {
    setActiveTenantSlug(tenant.slug);
    setActiveTenant(tenant);
    setAuditReport(null);
    if (onTenantSwitched) {
      onTenantSwitched(tenant);
    }
  }

  async function handleRunAudit() {
    if (!activeTenant) return;
    setIsAuditing(true);
    try {
      const report = await runTenantIsolationAudit(activeTenant.slug);
      setAuditReport(report);
    } catch (err) {
      console.error("Audit failed:", err);
    } finally {
      setIsAuditing(false);
    }
  }

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4 animate-in fade-in duration-200">
      <div className="bg-[var(--surface-card)] border border-[var(--surface-border)] rounded-xl w-full max-w-2xl max-h-[90vh] flex flex-col shadow-2xl overflow-hidden">
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-[var(--surface-border)] bg-[var(--surface-dark)]/40">
          <div className="flex items-center gap-2.5">
            <div className="p-2 rounded-lg bg-[var(--accent-tangerine)]/10 text-[var(--accent-tangerine)]">
              <Building2 className="w-5 h-5" />
            </div>
            <div>
              <h2 className="text-sm font-bold font-mono tracking-wide text-[var(--foreground)] uppercase flex items-center gap-2">
                Mandanten-Isolation & RLS Partitioning
                <span className="text-[10px] px-2 py-0.5 rounded bg-emerald-500/10 border border-emerald-500/20 text-emerald-500 font-mono">
                  GDPR Art. 32
                </span>
              </h2>
              <p className="text-xs text-[var(--foreground)] opacity-60">
                PostgreSQL Row-Level Security & BaFin KWG § 25b Multi-Client Segregation
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1 rounded-md text-[var(--foreground)] opacity-60 hover:opacity-100 hover:bg-[var(--surface-dark)] transition-all cursor-pointer"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Content */}
        <div className="p-6 overflow-y-auto space-y-5 flex-1 text-xs">
          {/* Active Tenant Hero */}
          {activeTenant && (
            <div className="p-4 rounded-lg bg-gradient-to-r from-amber-500/5 via-[var(--surface-dark)] to-emerald-500/5 border border-amber-500/20">
              <div className="flex items-center justify-between">
                <div>
                  <span className="text-[10px] font-mono uppercase tracking-wider text-amber-500 font-bold flex items-center gap-1.5">
                    <span className="w-2 h-2 rounded-full bg-amber-500 animate-pulse" />
                    Aktiver Enterprise Mandant
                  </span>
                  <h3 className="text-base font-bold text-[var(--foreground)] mt-1">
                    {activeTenant.name}
                  </h3>
                  <div className="flex items-center gap-3 mt-2 text-[11px] font-mono text-[var(--foreground)] opacity-70">
                    <span>Slug: <code className="text-amber-500">{activeTenant.slug}</code></span>
                    <span>•</span>
                    <span>UUID: <code>{activeTenant.id.slice(0, 13)}...</code></span>
                  </div>
                </div>
                <button
                  onClick={handleRunAudit}
                  disabled={isAuditing}
                  className="px-3 py-2 rounded-md bg-emerald-600 hover:bg-emerald-500 text-white font-mono font-bold text-xs flex items-center gap-1.5 shadow-sm transition-all cursor-pointer disabled:opacity-50"
                  title="Live RLS Penetration & Cross-Tenant Non-Leakage Audit"
                >
                  {isAuditing ? (
                    <RefreshCw className="w-3.5 h-3.5 animate-spin" />
                  ) : (
                    <ShieldCheck className="w-3.5 h-3.5" />
                  )}
                  <span>RLS Audit Starten</span>
                </button>
              </div>
            </div>
          )}

          {/* Audit Verification Result Banner */}
          {auditReport && (
            <div className="p-4 rounded-lg bg-emerald-500/10 border border-emerald-500/30 text-emerald-500 space-y-2 animate-in zoom-in-95 duration-150">
              <div className="flex items-center justify-between">
                <span className="font-bold font-mono text-[11px] flex items-center gap-1.5">
                  <CheckCircle2 className="w-4 h-4 text-emerald-500" />
                  {auditReport.compliance_certification}
                </span>
                <span className="text-[10px] font-mono opacity-80">
                  {new Date(auditReport.audit_timestamp).toLocaleTimeString()}
                </span>
              </div>
              <div className="grid grid-cols-3 gap-2 pt-1 font-mono text-[11px]">
                <div className="p-2 rounded bg-black/20">
                  <div className="text-[10px] opacity-70">RLS Modus</div>
                  <div className="font-bold text-[var(--foreground)]">{auditReport.rls_mode}</div>
                </div>
                <div className="p-2 rounded bg-black/20">
                  <div className="text-[10px] opacity-70">Sichtbare Belege</div>
                  <div className="font-bold text-emerald-400">{auditReport.total_documents_visible} Dokumente</div>
                </div>
                <div className="p-2 rounded bg-black/20">
                  <div className="text-[10px] opacity-70">Datenleckage</div>
                  <div className="font-bold text-emerald-400">
                    {auditReport.cross_tenant_leakage_detected ? "LECKAGE DETEKTIERT" : "0% (Vollständig Isoliert)"}
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Available Enterprise Tenants Grid */}
          <div>
            <div className="flex items-center justify-between mb-2.5">
              <h4 className="font-mono font-bold uppercase tracking-wider text-[11px] text-[var(--foreground)] opacity-80 flex items-center gap-1.5">
                <Layers className="w-3.5 h-3.5 text-[var(--accent-tangerine)]" />
                Verfügbare Mandanten-Partitionen
              </h4>
              <span className="text-[10px] font-mono text-[var(--foreground)] opacity-60">
                {tenants.length} Partitionen registriert
              </span>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5">
              {tenants.map((t) => {
                const isActive = activeTenant?.id === t.id;
                return (
                  <div
                    key={t.id}
                    onClick={() => handleSwitchTenant(t)}
                    className={`p-3 rounded-lg border transition-all cursor-pointer flex flex-col justify-between gap-2 ${
                      isActive
                        ? "bg-amber-500/10 border-amber-500/50 shadow-sm"
                        : "bg-[var(--surface-card)] border-[var(--surface-border)] hover:border-[var(--accent-tangerine)]/40 hover:bg-[var(--surface-dark)]/40"
                    }`}
                  >
                    <div className="flex items-start justify-between">
                      <div className="font-bold text-[12px] text-[var(--foreground)]">
                        {t.name}
                      </div>
                      {isActive && (
                        <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-amber-500 text-black font-bold shrink-0">
                          Aktiv
                        </span>
                      )}
                    </div>
                    <div className="flex items-center justify-between text-[10px] font-mono text-[var(--foreground)] opacity-70 pt-1 border-t border-[var(--surface-border)]/50">
                      <span>Slug: <code>{t.slug}</code></span>
                      <span className="flex items-center gap-1">
                        <FileText className="w-3 h-3 text-[var(--accent-tangerine)]" />
                        {t.document_count} Belege
                      </span>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="px-6 py-3 border-t border-[var(--surface-border)] bg-[var(--surface-dark)]/40 flex items-center justify-between text-xs font-mono text-[var(--foreground)] opacity-70">
          <span className="flex items-center gap-1">
            <Lock className="w-3 h-3 text-emerald-500" />
            Mandanten-Segregation nach ISO 27001 & BSI C5
          </span>
          <button
            onClick={onClose}
            className="px-3 py-1.5 rounded bg-[var(--surface-card)] hover:bg-[var(--surface-border)] border border-[var(--surface-border)] text-[var(--foreground)] font-bold transition-all cursor-pointer"
          >
            Schließen
          </button>
        </div>
      </div>
    </div>
  );
}

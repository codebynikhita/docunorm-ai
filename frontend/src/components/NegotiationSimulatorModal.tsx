"use client";

import React, { useState } from "react";
import {
  ClauseDomain,
  NegotiationRound,
  NegotiationSession,
  NegotiationStance,
  VendorArchetype,
  downloadNegotiationProtocolPdf,
  simulateContractNegotiation,
} from "@/lib/api";

interface NegotiationSimulatorModalProps {
  isOpen: boolean;
  onClose: () => void;
  documentId?: string;
  documentFilename?: string;
}

export const NegotiationSimulatorModal: React.FC<NegotiationSimulatorModalProps> = ({
  isOpen,
  onClose,
  documentId,
  documentFilename,
}) => {
  const [clauseDomain, setClauseDomain] = useState<ClauseDomain>("supervisory_audit_rights");
  const [vendorArchetype, setVendorArchetype] = useState<VendorArchetype>("US_HYPERSCALER");
  const [enterpriseStance, setEnterpriseStance] = useState<NegotiationStance>("STRICT_REGULATORY_LINE");
  const [currentClauseText, setCurrentClauseText] = useState<string>(
    "Der Anbieter behält sich vor, Vor-Ort-Audits abzulehnen und Prüfungen auf jährliche SOC-2 Type II Testate zu beschränken."
  );
  const [customCounterArgument, setCustomCounterArgument] = useState<string>("");
  const [session, setSession] = useState<NegotiationSession | null>(null);
  const [isSimulating, setIsSimulating] = useState<boolean>(false);
  const [isExporting, setIsExporting] = useState<boolean>(false);
  const [copiedClause, setCopiedClause] = useState<boolean>(false);

  if (!isOpen) return null;

  const handleRunSimulation = async () => {
    try {
      setIsSimulating(true);
      const res = await simulateContractNegotiation({
        document_id: documentId || "00000000-0000-0000-0000-000000000001",
        document_filename: documentFilename || "Enterprise_ICT_Outsourcing.pdf",
        clause_domain: clauseDomain,
        vendor_archetype: vendorArchetype,
        enterprise_stance: enterpriseStance,
        current_clause_text: currentClauseText,
        user_counter_argument: customCounterArgument || undefined,
        round_count: 3,
      });
      setSession(res);
    } catch (err) {
      alert(err instanceof Error ? err.message : "Simulation fehlgeschlagen.");
    } finally {
      setIsSimulating(false);
    }
  };

  const handleDownloadPdf = async () => {
    if (!session) return;
    try {
      setIsExporting(true);
      await downloadNegotiationProtocolPdf(session.session_id);
    } catch (err) {
      alert(err instanceof Error ? err.message : "PDF-Download fehlgeschlagen.");
    } finally {
      setIsExporting(false);
    }
  };

  const handleCopyCompromise = () => {
    if (!session?.final_reconciled_clause) return;
    navigator.clipboard.writeText(session.final_reconciled_clause);
    setCopiedClause(true);
    setTimeout(() => setCopiedClause(false), 2000);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-3 sm:p-5 bg-black/80 backdrop-blur-md animate-in fade-in duration-200">
      <div className="relative w-full max-w-6xl max-h-[92vh] flex flex-col bg-slate-900 border border-teal-800/60 rounded-xl shadow-2xl overflow-hidden text-slate-100">
        
        {/* Header Banner */}
        <div className="flex items-center justify-between px-6 py-4 bg-gradient-to-r from-slate-950 via-slate-900 to-teal-950/80 border-b border-teal-800/40">
          <div className="flex items-center gap-3">
            <span className="p-2.5 rounded-lg bg-teal-950/80 border border-teal-500/40 text-xl shadow-inner text-teal-300">
              🤝
            </span>
            <div>
              <div className="flex items-center gap-2">
                <h2 className="text-lg font-bold tracking-tight text-white">
                  KI-Verhandlungs-Simulator &amp; Multi-Turn Stresstest
                </h2>
                <span className="text-[10px] uppercase font-mono px-2 py-0.5 rounded bg-teal-900/50 text-teal-300 border border-teal-700/50">
                  DAY 41 • DORA &amp; BAFIN
                </span>
              </div>
              <p className="text-xs text-slate-400 mt-0.5">
                Autonome Dual-Agent Argumentationsrunden, Gegenpartei-Stresstest &amp; Reconciled Compromise Synthesis
                {documentFilename && (
                  <span className="ml-2 font-mono text-teal-300 text-xs">• {documentFilename}</span>
                )}
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2.5">
            {session && (
              <button
                onClick={handleDownloadPdf}
                disabled={isExporting}
                className="flex items-center gap-1.5 px-3.5 py-1.5 rounded-lg text-xs font-semibold bg-teal-700 hover:bg-teal-600 text-white transition-all shadow-md disabled:opacity-50"
              >
                {isExporting ? "Erzeuge PDF..." : "⬇️ Verhandlungsprotokoll PDF"}
              </button>
            )}

            <button
              onClick={onClose}
              className="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition-colors ml-1"
              aria-label="Schließen"
            >
              ✕
            </button>
          </div>
        </div>

        {/* Content Body */}
        <div className="flex-1 overflow-y-auto p-6 space-y-6">
          
          {/* Controls Bar */}
          <div className="p-4 rounded-xl bg-slate-950/80 border border-slate-800 space-y-3">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
              <div>
                <label className="text-[11px] font-mono text-slate-400 uppercase font-semibold block mb-1">
                  Regulatorische Domäne
                </label>
                <select
                  value={clauseDomain}
                  onChange={(e) => setClauseDomain(e.target.value as ClauseDomain)}
                  className="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-1.5 text-xs text-white focus:outline-none focus:border-teal-500"
                >
                  <option value="supervisory_audit_rights">DORA Art. 30(3)(e) Aufsichtliche Prüfrechte</option>
                  <option value="emergency_exit_unwinding">BaFin RS 10/2026 Notfall-Entflechtung</option>
                  <option value="subcontractor_veto">DORA RTS (JC 2024 28) 30-Tage Vetorecht</option>
                  <option value="cloud_act_byok">DSGVO Art. 48 &amp; CLOUD Act / BYOK</option>
                  <option value="sla_penalties">DORA Art. 30(2)(d) SLA &amp; Pönalen</option>
                </select>
              </div>

              <div>
                <label className="text-[11px] font-mono text-slate-400 uppercase font-semibold block mb-1">
                  Gegenpartei-Archetyp
                </label>
                <select
                  value={vendorArchetype}
                  onChange={(e) => setVendorArchetype(e.target.value as VendorArchetype)}
                  className="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-1.5 text-xs text-white focus:outline-none focus:border-teal-500"
                >
                  <option value="US_HYPERSCALER">US-Hyperscaler (AWS, Azure, GCP)</option>
                  <option value="EU_SOVEREIGN_CLOUD">Europäische Sovereign Cloud</option>
                  <option value="LEGACY_MAINFRAME_VENDOR">Legacy Mainframe / Core Banking</option>
                  <option value="TIER4_SUBCONTRACTOR">Tier-4 Kaskaden-Subunternehmer</option>
                </select>
              </div>

              <div>
                <label className="text-[11px] font-mono text-slate-400 uppercase font-semibold block mb-1">
                  Verhandlungshaltung
                </label>
                <select
                  value={enterpriseStance}
                  onChange={(e) => setEnterpriseStance(e.target.value as NegotiationStance)}
                  className="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-1.5 text-xs text-white focus:outline-none focus:border-teal-500"
                >
                  <option value="STRICT_REGULATORY_LINE">Strikte BaFin/DORA Linie (Keine Konzession)</option>
                  <option value="BALANCED_PRAGMATIC">Ausgewogen / Pragmatisch (Kompromiss)</option>
                  <option value="AGGRESSIVE_DEFENSE">Aggressive Verteidigung (Nulltoleranz)</option>
                </select>
              </div>
            </div>

            <div className="flex gap-2 items-center pt-1">
              <input
                type="text"
                placeholder="Optionales individuelles Gegenargument (z.B. Verweis auf BGB § 307 oder Prüfbericht)..."
                value={customCounterArgument}
                onChange={(e) => setCustomCounterArgument(e.target.value)}
                className="flex-1 bg-slate-900 border border-slate-700 rounded-lg px-3 py-1.5 text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-teal-500"
              />
              <button
                onClick={handleRunSimulation}
                disabled={isSimulating}
                className="px-4 py-1.5 rounded-lg text-xs font-bold bg-teal-600 hover:bg-teal-500 text-white transition-all shadow-md shrink-0 disabled:opacity-50"
              >
                {isSimulating ? "Simuliere Verhandlung..." : "⚡ Verhandlung starten"}
              </button>
            </div>
          </div>

          {/* Transcript Timeline */}
          {session && (
            <div className="space-y-4">
              
              {/* Scorecard Hero */}
              <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                <div className="p-3.5 rounded-xl bg-slate-950/80 border border-slate-800">
                  <span className="text-[10px] text-slate-400 uppercase font-mono">Verhandlungsstatus</span>
                  <div className="text-base font-bold font-mono text-emerald-400 mt-1">
                    {session.current_status === "CONSENSUS_REACHED" ? "✓ KONSENS ERREICHT" : session.current_status}
                  </div>
                </div>

                <div className="p-3.5 rounded-xl bg-slate-950/80 border border-slate-800">
                  <span className="text-[10px] text-slate-400 uppercase font-mono">Risikoreduktion</span>
                  <div className="text-base font-bold font-mono text-teal-300 mt-1">
                    -{session.risk_reduction_percentage}% ({session.initial_risk_score}% → {session.final_risk_score}%)
                  </div>
                </div>

                <div className="p-3.5 rounded-xl bg-slate-950/80 border border-slate-800">
                  <span className="text-[10px] text-slate-400 uppercase font-mono">BaFin / DORA Audit-Sicherheit</span>
                  <div className="text-base font-bold font-mono text-emerald-400 mt-1">
                    {session.bafin_audit_safe ? "✓ AUDIT-SAFE (KONFORM)" : "WARNUNG"}
                  </div>
                </div>

                <div className="p-3.5 rounded-xl bg-slate-950/80 border border-slate-800">
                  <span className="text-[10px] text-slate-400 uppercase font-mono">Revisions-Hash (SHA-256)</span>
                  <div className="text-xs font-mono text-cyan-300 mt-1 truncate">
                    {session.sha256_audit_trail.slice(0, 16)}...
                  </div>
                </div>
              </div>

              {/* Rounds Speech Bubbles */}
              <div className="space-y-3">
                <h3 className="text-xs font-bold text-slate-300 uppercase tracking-wide">
                  Transkript der Verhandlungsrunden ({session.rounds.length} Runden)
                </h3>

                {session.rounds.map((round: NegotiationRound) => {
                  const isBuyer = round.speaker === "ENTERPRISE_BUYER";
                  return (
                    <div
                      key={round.round_number}
                      className={`p-4 rounded-xl border space-y-2 transition-all ${
                        isBuyer
                          ? "bg-slate-950/90 border-teal-800/60 ml-0 mr-8"
                          : "bg-slate-950/90 border-rose-800/60 ml-8 mr-0"
                      }`}
                    >
                      <div className="flex items-center justify-between border-b border-slate-800/80 pb-2">
                        <div className="flex items-center gap-2">
                          <span
                            className={`px-2 py-0.5 rounded text-[10px] font-bold font-mono ${
                              isBuyer
                                ? "bg-teal-950 text-teal-300 border border-teal-700/60"
                                : "bg-rose-950 text-rose-300 border border-rose-700/60"
                            }`}
                          >
                            Runde {round.round_number} • {round.speaker_title}
                          </span>
                        </div>
                        <div className="flex items-center gap-2">
                          {round.cited_statutes.map((s) => (
                            <span
                              key={s}
                              className="px-1.5 py-0.5 rounded text-[10px] font-mono bg-slate-900 text-slate-300 border border-slate-800"
                            >
                              {s}
                            </span>
                          ))}
                        </div>
                      </div>

                      <p className="text-xs text-slate-200 leading-relaxed">{round.argument_de}</p>

                      <div className="p-2.5 rounded-lg bg-slate-900/90 border border-slate-800 text-[11px] font-mono text-slate-300">
                        <span className="text-slate-500 mr-2">Vorgeschlagener Klausel-Text:</span>
                        &bdquo;{round.proposed_redline_snippet}&ldquo;
                      </div>

                      <div className="flex items-center justify-between text-[10px] font-mono text-slate-400 pt-1">
                        <span>Restrisiko: {round.regulatory_risk_score}%</span>
                        <span>Zugeständnis-Index: {round.concession_score}</span>
                      </div>
                    </div>
                  );
                })}
              </div>

              {/* Reconciled Compromise Box */}
              {session.final_reconciled_clause && (
                <div className="p-5 rounded-xl bg-teal-950/40 border border-teal-600/70 shadow-lg space-y-3">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <span className="text-lg">⚖️</span>
                      <h4 className="text-xs font-bold text-teal-200 uppercase tracking-wide">
                        Rechtssichere Kompromiss-Klausel (Nachtragsvereinbarung gem. § 311 BGB)
                      </h4>
                    </div>
                    <button
                      onClick={handleCopyCompromise}
                      className="px-3 py-1 rounded text-xs font-semibold bg-teal-800 hover:bg-teal-700 text-white transition-colors"
                    >
                      {copiedClause ? "✓ Kopiert!" : "📋 Klausel kopieren"}
                    </button>
                  </div>

                  <p className="p-3.5 rounded-lg bg-slate-950/90 border border-teal-800/60 text-xs font-mono text-teal-100 leading-relaxed">
                    {session.final_reconciled_clause}
                  </p>
                </div>
              )}
            </div>
          )}
        </div>

        {/* Modal Footer */}
        <div className="px-6 py-3 bg-slate-950 border-t border-slate-800 flex items-center justify-between text-xs text-slate-500">
          <div className="flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-teal-500" />
            <span>Autonomous Multi-Turn Legal Agent aktiv • DORA Art. 30 &amp; KWG § 25b</span>
          </div>
          <span className="font-mono text-[11px]">DocuNorm AI • Negotiation Simulator v41.0</span>
        </div>
      </div>
    </div>
  );
};

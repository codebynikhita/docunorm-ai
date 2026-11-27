"""
DocuNorm AI — Day 41: AI Contract Negotiation Simulator & Multi-Turn Stresstest Schemas.
Models autonomous dual-agent negotiation rounds between Enterprise Buyer Legal Counsel
and Vendor Legal Counsel under DORA Art. 30, BaFin RS 10/2026, and BGB § 305 ff. AGB-Recht.
"""

from datetime import datetime
from typing import Literal
from uuid import UUID, uuid4

from pydantic import BaseModel, Field

NegotiationStance = Literal[
    "AGGRESSIVE_DEFENSE",
    "BALANCED_PRAGMATIC",
    "STRICT_REGULATORY_LINE",
]

VendorArchetype = Literal[
    "US_HYPERSCALER",
    "EU_SOVEREIGN_CLOUD",
    "LEGACY_MAINFRAME_VENDOR",
    "TIER4_SUBCONTRACTOR",
]

ClauseDomain = Literal[
    "supervisory_audit_rights",
    "emergency_exit_unwinding",
    "subcontractor_veto",
    "cloud_act_byok",
    "sla_penalties",
]

NegotiationSpeaker = Literal[
    "ENTERPRISE_BUYER",
    "VENDOR_LEGAL_COUNSEL",
    "SUPERVISORY_OBSERVER",
]


class NegotiationRound(BaseModel):
    round_number: int = Field(..., ge=1, le=10)
    speaker: NegotiationSpeaker
    speaker_title: str
    argument_de: str
    argument_en: str
    cited_statutes: list[str]
    proposed_redline_snippet: str
    concession_score: float = Field(..., ge=0.0, le=1.0, description="0.0 is zero concession, 1.0 is full capitulation")
    regulatory_risk_score: float = Field(..., ge=0.0, le=100.0, description="Residual statutory risk score (0 is clean)")


class NegotiationSession(BaseModel):
    session_id: UUID = Field(default_factory=uuid4)
    document_id: UUID
    document_filename: str
    clause_domain: ClauseDomain
    vendor_archetype: VendorArchetype
    enterprise_stance: NegotiationStance
    rounds: list[NegotiationRound]
    current_status: Literal["IN_PROGRESS", "CONSENSUS_REACHED", "DEADLOCK_ESCALATED"]
    final_reconciled_clause: str | None = None
    bafin_audit_safe: bool = True
    consensus_round_index: int | None = None
    initial_risk_score: float = Field(..., ge=0.0, le=100.0)
    final_risk_score: float = Field(..., ge=0.0, le=100.0)
    risk_reduction_percentage: float = Field(..., ge=0.0, le=100.0)
    executed_at: datetime
    sha256_audit_trail: str


class NegotiationStepRequest(BaseModel):
    document_id: UUID
    document_filename: str = "Enterprise_Cloud_Agreement.pdf"
    clause_domain: ClauseDomain = "supervisory_audit_rights"
    vendor_archetype: VendorArchetype = "US_HYPERSCALER"
    enterprise_stance: NegotiationStance = "STRICT_REGULATORY_LINE"
    current_clause_text: str = Field(..., min_length=10, description="Original deficient contract clause to negotiate")
    user_counter_argument: str | None = None
    round_count: int = Field(default=3, ge=1, le=5)

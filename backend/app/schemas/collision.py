"""
DocuNorm AI — Day 38: Cross-Regulatory Conflict & Jurisdictional Incompatibility Schemas.
Conforms to EU AI Act Art. 12, DORA Art. 30, GDPR Art. 48, BaFin KWG § 25b, and BGB AGB-Inhaltskontrolle.
"""

from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field

RegulatoryStandard = Literal[
    "DORA",
    "GDPR",
    "KWG",
    "CLOUD_ACT",
    "BGB",
    "LKSG",
    "NIS2",
    "BAIT_VAIT",
]

ConflictSeverity = Literal[
    "CRITICAL_BLOCKER",
    "HIGH_RISK",
    "MEDIUM_COLLISION",
    "HARMONIZED",
]


class NormativeConflict(BaseModel):
    conflict_id: str = Field(..., description="Unique conflict identifier (e.g. CONF-CLOUD-GDPR-01)")
    title_de: str
    title_en: str
    source_clause_text: str
    page_number: int = Field(default=1)
    bounding_box: list[float] = Field(default_factory=lambda: [0.0, 0.0, 0.0, 0.0])
    standard_a: RegulatoryStandard
    standard_b: RegulatoryStandard
    severity: ConflictSeverity
    statutory_clash_summary_de: str
    statutory_clash_summary_en: str
    jurisdiction_clash: str
    legal_risk_score: float = Field(..., ge=0.0, le=100.0)
    resolution_covenant_de: str
    resolution_covenant_en: str
    statutory_precedence_rule: str = Field(
        default="Lex Superior Derogat Legi Inferiori",
        description="Statutory canon of interpretation (e.g. Lex Superior, Lex Specialis, EU Primacy)",
    )


class DocumentConflictMatrix(BaseModel):
    document_id: UUID
    document_filename: str
    analyzed_at: datetime
    overall_collision_index: float = Field(..., ge=0.0, le=100.0, description="0 is clean, 100 is severe deadlock")
    conflicts_detected: int
    critical_blockers: int
    high_risks: int
    medium_risks: int
    jurisdictional_exposure_map: dict[str, int] = Field(
        default_factory=dict,
        description="Counts of clauses governed by EU_DE, US_EXTRATERRITORIAL, THIRD_COUNTRY",
    )
    conflicts: list[NormativeConflict]
    compliance_verdict: Literal["COMPATIBLE", "CONDITIONALLY_RECONCILABLE", "INCOMPATIBLE_BLOCKER"]
    sha256_hash: str


class ClauseReconcileRequest(BaseModel):
    clause_text: str = Field(..., min_length=10, description="Clause text to analyze for regulatory collisions")
    target_standards: list[RegulatoryStandard] = Field(
        default=["DORA", "GDPR", "KWG", "CLOUD_ACT", "BGB"],
        description="Regulatory regimes to cross-audit",
    )


class ClauseReconcileResponse(BaseModel):
    has_conflicts: bool
    detected_conflicts: list[NormativeConflict]
    reconciliation_covenant_de: str | None = None
    reconciliation_covenant_en: str | None = None
    jurisdiction_exposure: str

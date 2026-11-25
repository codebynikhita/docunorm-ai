"""
DocuNorm AI — Day 39: RegTech Horizon Scanner & Contract Drift Schemas.
Models European & German regulatory updates (DORA RTS, BaFin Circulars, EU AI Act, BAFA)
and calculates contract drift metrics against statutory enforcement deadlines.
"""

from datetime import date, datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field

IssuingAuthority = Literal[
    "BAFIN",
    "EBA",
    "EIOPA",
    "EU_COMMISSION",
    "BAFA",
    "BSI",
    "EDPB",
]

UpdateUrgency = Literal[
    "IMMEDIATE",
    "HIGH",
    "SCHEDULED",
    "INFORMATIONAL",
]

DriftSeverity = Literal[
    "CRITICAL_DRIFT",
    "HIGH_RISK",
    "MODERATE_GAP",
    "COMPLIANT",
]


class RegulatoryUpdate(BaseModel):
    update_id: str = Field(..., description="Unique statutory update identifier (e.g. REG-DORA-RTS-2026-01)")
    title_de: str
    title_en: str
    issuing_authority: IssuingAuthority
    publication_date: date
    enforcement_deadline: date
    urgency: UpdateUrgency
    impacted_frameworks: list[str]
    summary_de: str
    summary_en: str
    affected_clause_domains: list[str]
    statutory_source_url: str
    days_until_enforcement: int = Field(default=0)


class ContractDriftItem(BaseModel):
    clause_id: str
    page_number: int
    current_clause_text: str
    associated_update_id: str
    drift_severity: DriftSeverity
    compliance_gap_de: str
    compliance_gap_en: str
    days_until_deadline: int
    retrofitting_action_required: str


class ContractDriftReport(BaseModel):
    document_id: UUID
    document_filename: str
    audited_at: datetime
    overall_drift_score: float = Field(..., ge=0.0, le=100.0, description="0 is clean, 100 is severe obsolescence")
    total_clauses_analyzed: int
    drifting_clauses_count: int
    critical_enforcement_items: int
    earliest_enforcement_deadline: date | None = None
    applicable_regulatory_updates: list[RegulatoryUpdate]
    drift_items: list[ContractDriftItem]
    retrofitting_status: Literal["UP_TO_DATE", "ACTION_REQUIRED", "NON_COMPLIANT_EXPIRED"]
    sha256_seal: str

from datetime import UTC, datetime
from enum import StrEnum
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field


class ConflictPillar(StrEnum):
    CLOUD_ACT_CONFLICT = "CLOUD_ACT_CONFLICT"
    SCHREMS_II_TRANSFER = "SCHREMS_II_TRANSFER"
    EXIT_LOCKIN = "EXIT_LOCKIN"
    SUBCONTRACTOR_CHAIN = "SUBCONTRACTOR_CHAIN"
    AUDIT_OBSTRUCTION = "AUDIT_OBSTRUCTION"
    SLA_DEFICIT = "SLA_DEFICIT"
    BGB_LIABILITY_DISCLAIMER = "BGB_LIABILITY_DISCLAIMER"


class BattlecardSeverity(StrEnum):
    CRITICAL = "CRITICAL"  # Mandatory BaFin / DORA breach; contract cannot be signed
    HIGH = "HIGH"          # High risk; requires board exception or executive escalation
    MEDIUM = "MEDIUM"      # Negotiable tactical point


class BattlecardItem(BaseModel):
    id: str
    pillar: ConflictPillar
    severity: BattlecardSeverity
    title_de: str
    title_en: str
    statutory_reference: str = Field(..., description="e.g. 'DORA Art. 30 Abs. 2 · KWG § 25b'")
    vendor_clause_quote: str = Field(..., description="Verbatim quote from vendor agreement")
    page_number: int
    vendor_common_defense: str = Field(..., description="What the vendor's sales rep / legal counsel will argue")
    bank_counter_argument: str = Field(..., description="The unassailable statutory counter-argument for procurement")
    non_negotiable_clause_de: str = Field(..., description="Recommended German standard clause (Musterklausel)")
    bafin_escalation_script: str = Field(..., description="Formal supervisory statement to cite if vendor refuses")


class TiaAssessment(BaseModel):
    """
    Schrems II Transfer Impact Assessment & US CLOUD Act Conflict Metrics
    """
    overall_transfer_risk: Literal["CRITICAL", "ELEVATED", "RESILIENT", "COMPLIANT"]
    transfer_risk_score: float = Field(..., description="0 to 100% risk index")
    cloud_act_exposure: bool = Field(..., description="Whether US parentage triggers CLOUD Act extraterritoriality")
    encryption_hyok_verified: bool = Field(..., description="Hold-Your-Own-Key HSM key control verification")
    eu_data_residency_guaranteed: bool = Field(..., description="Frankfurt / Dublin / Amsterdam ring-fencing")
    bafin_audit_clearance: str = Field(..., description="Formal clearance verdict under KWG § 25b")
    mitigation_recommendation: str


class SlaSimulationRequest(BaseModel):
    downtime_hours: float = Field(default=8.0, ge=0.0, le=720.0, description="Hypothetical outage duration in hours")
    contract_value_eur: float = Field(default=500000.0, ge=0.0, description="Annual contract value in EUR")
    availability_target_pct: float = Field(default=99.95, ge=90.0, le=100.0, description="Agreed SLA uptime %")


class SlaSimulationResponse(BaseModel):
    downtime_hours: float
    contract_value_eur: float
    availability_target_pct: float
    tolerated_annual_downtime_hours: float
    excess_downtime_hours: float
    penalty_eur: float
    penalty_pct_of_annual_contract: float
    dora_incident_classification: Literal["NEGLIGIBLE", "MAJOR_INCIDENT", "CRITICAL_SYSTEMIC_INCIDENT"]
    bafin_initial_notification_deadline: str
    bafin_intermediate_report_deadline: str
    statutory_extraordinary_termination_triggered: bool
    rationale: str


class NegotiationBattlecardResponse(BaseModel):
    document_id: UUID
    filename: str
    overall_negotiation_posture: Literal["UNACCEPTABLE_HIGH_RISK", "CONDITIONAL_APPROVAL_REQUIRED", "MARKET_STANDARD_COMPLIANT"]
    total_battlecards: int
    critical_count: int
    high_count: int
    tia_assessment: TiaAssessment
    battlecards: list[BattlecardItem]
    generated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

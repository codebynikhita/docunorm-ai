from datetime import UTC, datetime
from enum import StrEnum
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field


class CapaSeverity(StrEnum):
    CRITICAL = "CRITICAL"  # Immediate statutory violation (e.g., child labor, mercury dump)
    HIGH = "HIGH"          # High compliance deficit (e.g., lack of whistleblower, wage deficit)
    MEDIUM = "MEDIUM"      # Formal or procedural deficit


class CapaStatus(StrEnum):
    OPEN = "OPEN"
    IN_REMEDIATION = "IN_REMEDIATION"
    VERIFIED_RESOLVED = "VERIFIED_RESOLVED"
    ESCALATED_TO_BAFA = "ESCALATED_TO_BAFA"


class CapaMilestone(BaseModel):
    id: str
    title_de: str
    title_en: str
    category: str
    severity: CapaSeverity
    deadline_days: int = Field(..., description="Remediation deadline in days (e.g. 30, 60, 90)")
    statutory_basis: str = Field(..., description="e.g. '§ 7 Abs. 1 LkSG · ILO 138'")
    deficiency_description: str
    required_action_de: str
    required_action_en: str
    verification_method: str = Field(..., description="e.g. 'Unabhängiges Vor-Ort-Audit durch TÜV/SGS'")
    penalty_upon_default_eur: float = Field(default=0.0, description="Vertragsstrafe bei Nichteinhaltung")
    status: CapaStatus = CapaStatus.OPEN


class SupplierCapaPlan(BaseModel):
    plan_id: str
    document_id: UUID
    filename: str
    supplier_name: str
    overall_compliance_posture: Literal["CRITICAL_ACTION_REQUIRED", "REMEDIATION_REQUIRED", "ACCEPTABLE"]
    total_milestones: int
    critical_milestones_count: int
    max_remediation_timeline_days: int
    estimated_remediation_cost_eur: float
    bafa_notification_required: bool
    milestones: list[CapaMilestone]
    executive_summary_de: str
    executive_summary_en: str
    generated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

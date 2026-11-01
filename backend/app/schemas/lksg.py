from datetime import datetime, timezone
from enum import Enum
from typing import Literal
from uuid import UUID
from pydantic import BaseModel, Field


class LkSGRiskCategory(str, Enum):
    """
    Statutory risk categories defined under § 2 Abs. 2 (Human Rights)
    and § 2 Abs. 3 (Environment) of the German Supply Chain Due Diligence Act (LkSG).
    """
    CHILD_LABOR = "CHILD_LABOR"  # § 2 Abs. 2 Nr. 1 LkSG (ILO 138/182)
    FORCED_LABOR = "FORCED_LABOR"  # § 2 Abs. 2 Nr. 2 LkSG
    OCCUPATIONAL_SAFETY = "OCCUPATIONAL_SAFETY"  # § 2 Abs. 2 Nr. 5 LkSG
    FREEDOM_OF_ASSOCIATION = "FREEDOM_OF_ASSOCIATION"  # § 2 Abs. 2 Nr. 6 LkSG
    DISCRIMINATION = "DISCRIMINATION"  # § 2 Abs. 2 Nr. 7 LkSG
    FAIR_WAGE = "FAIR_WAGE"  # § 2 Abs. 2 Nr. 8 LkSG
    ENVIRONMENT_MINAMATA = "ENVIRONMENT_MINAMATA"  # § 2 Abs. 3 Nr. 1 LkSG (Quecksilber-Übereinkommen)
    ENVIRONMENT_POPS = "ENVIRONMENT_POPS"  # § 2 Abs. 3 Nr. 2 LkSG (Stockholm-Übereinkommen)
    ENVIRONMENT_HAZARDOUS_WASTE = "ENVIRONMENT_HAZARDOUS_WASTE"  # § 2 Abs. 3 Nr. 3 LkSG (Basler Übereinkommen)
    COMPLAINTS_PROCEDURE = "COMPLAINTS_PROCEDURE"  # § 8 LkSG (Beschwerdeverfahren)
    ANNUAL_REPORTING_BAFA = "ANNUAL_REPORTING_BAFA"  # § 10 LkSG (Jährlicher BAFA-Bericht)
    INDIRECT_SUPPLIER_CONTROL = "INDIRECT_SUPPLIER_CONTROL"  # § 9 LkSG (Mittelbare Zulieferer)


class LkSGSeverity(str, Enum):
    CRITICAL = "CRITICAL"  # Immediate BAFA fine risk (up to 2% of annual turnover)
    HIGH = "HIGH"          # Substantial compliance deficit requiring remediation within 30 days
    MEDIUM = "MEDIUM"      # Moderate risk requiring procedural adjustment
    LOW = "LOW"            # Minor formal deficiency
    COMPLIANT = "COMPLIANT"  # Fully aligned with BAFA guidelines & statutory standards


class LkSGRiskItem(BaseModel):
    """
    Individual audit finding mapped to a specific clause, statutory article, and BAFA guideline.
    """
    category: LkSGRiskCategory
    severity: LkSGSeverity
    title_de: str
    title_en: str
    statutory_reference: str = Field(
        ..., description="e.g. '§ 2 Abs. 2 Nr. 1 LkSG · ILO-Übereinkommen 138'"
    )
    bafa_guideline_ref: str = Field(
        ..., description="e.g. 'BAFA Handreichung zur Risikoanalyse (Abschnitt 3.2)'"
    )
    finding_de: str
    finding_en: str
    evidence_snippet: str
    page_number: int = 1
    remediation_action_de: str
    remediation_action_en: str


class LkSGSupplierAssessment(BaseModel):
    """
    Consolidated supply chain due diligence evaluation for an enterprise supplier contract.
    """
    supplier_name: str
    supplier_tier: Literal["TIER_1_DIRECT", "TIER_N_INDIRECT"] = "TIER_1_DIRECT"
    overall_compliance_score: float = Field(
        ..., ge=0.0, le=100.0, description="100 = full compliance, 0 = severe non-compliance"
    )
    compliance_rating: Literal["AAA", "AA", "A", "BBB", "BB", "B", "CCC"]
    human_rights_score: float = Field(..., ge=0.0, le=100.0)
    environmental_score: float = Field(..., ge=0.0, le=100.0)
    governance_score: float = Field(..., ge=0.0, le=100.0)
    
    complaints_procedure_present: bool = False
    bafa_report_compliant: bool = False
    code_of_conduct_mandated: bool = False
    audit_rights_granted: bool = False
    
    identified_risks: list[LkSGRiskItem] = Field(default_factory=list)
    critical_risk_count: int = 0
    high_risk_count: int = 0
    
    executive_summary_de: str
    executive_summary_en: str


class LkSGAuditResponse(BaseModel):
    """
    API payload for German Supply Chain Due Diligence (LkSG) Document Audits.
    """
    document_id: UUID
    filename: str
    assessment: LkSGSupplierAssessment
    audit_timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

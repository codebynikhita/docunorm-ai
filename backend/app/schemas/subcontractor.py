from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, ConfigDict


class SubcontractorCheckResult(BaseModel):
    """
    Individual regulatory requirement check under DORA Art. 30 Abs. 3 and BaFin BAIT/KWG § 25b.
    """
    rule_id: str
    name_de: str
    name_en: str
    description_de: str
    description_en: str
    status: str  # "COMPLIANT" | "PARTIALLY_COMPLIANT" | "NON_COMPLIANT"
    score: float  # 0.0 to 1.0
    extracted_clause: str | None = None
    citation_tag: str | None = None
    page_number: int | None = None
    recommendation_de: str
    recommendation_en: str


class CascadingChainNode(BaseModel):
    """
    Represents an entity node in the multi-tier subcontracting supply chain.
    """
    node_id: str
    name: str
    tier: int  # 1 = Primary Vendor, 2 = Subcontractor, 3 = Sub-subcontractor, etc.
    service_type: str
    location: str  # e.g., "Frankfurt, Deutschland (EWR)"
    critical_function: bool
    approval_status: str  # "GENEHMIGT" | "UNTERRICHTET" | "NICHT_KONFORM"
    risk_level: str  # "NIEDRIG" | "MITTEL" | "HOCH" | "KRITISCH"


class DoraSubcontractorAuditReport(BaseModel):
    """
    Comprehensive Sub-Outsourcing & 4th-Party Cascading Risk Audit Report according to
    EU DORA Art. 30(3), Art. 28(3) and BaFin RS 10/2018 (BAIT Ziffer 8).
    """
    model_config = ConfigDict(from_attributes=True)

    document_id: UUID
    overall_score: float  # 0.0 to 100.0%
    compliance_rating: str  # "VOLLSTÄNDIG KONFORM (AAA)" | "BEDINGT KONFORM (BBB)" | "KRITISCH DEFIZITÄR (CCC)"
    evaluated_at: datetime
    dora_article: str = "Art. 30 Abs. 3 VO (EU) 2022/2554 & KWG § 25b"
    checks: list[SubcontractorCheckResult]
    cascading_nodes: list[CascadingChainNode]
    concentration_risk_level: str  # "NIEDRIG" | "MODERAT" | "ERHÖHT" | "KRITISCH"
    summary_de: str
    summary_en: str

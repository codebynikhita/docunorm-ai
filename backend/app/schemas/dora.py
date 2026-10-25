from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, ConfigDict


class DoraExitCheckResult(BaseModel):
    """
    Individual regulatory requirement check under DORA Art. 30 Abs. 2 and BaFin guidelines.
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
    bounding_box: list[float] | None = None
    recommendation_de: str
    recommendation_en: str


class DoraExitAuditReport(BaseModel):
    """
    Comprehensive Exit Strategy Audit Report according to EU DORA Art. 30(2)
    and BaFin Supervisory Circulars (BAIT/KAIT).
    """
    model_config = ConfigDict(from_attributes=True)

    document_id: UUID
    overall_score: float  # 0.0 to 100.0%
    compliance_rating: str  # "VOLLSTÄNDIG KONFORM (AAA)" | "BEDINGT KONFORM (BBB)" | "KRITISCH DEFIZITÄR (CCC)"
    evaluated_at: datetime
    dora_article: str = "Art. 30 Abs. 2 VO (EU) 2022/2554 & BaFin RS 10/2018"
    checks: list[DoraExitCheckResult]
    summary_de: str
    summary_en: str

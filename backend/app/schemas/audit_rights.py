from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, ConfigDict


class AuditRightCheckResult(BaseModel):
    """
    Individual regulatory check for supervisory audit rights under KWG § 25b,
    BaFin RS 10/2018 (BAIT Ziffer 8.1), and DORA Art. 30 Abs. 3 lit. e.
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


class InspectionNoticeLetter(BaseModel):
    """
    Automated formal BaFin/DORA supervisory on-site inspection letter according to DIN 5008.
    """
    letter_id: str
    sender_institution: str
    recipient_vendor: str
    reference_number: str
    inspection_date: str
    legal_basis: str
    scope_of_inspection: list[str]
    german_letter_content: str
    english_letter_content: str


class DoraAuditRightsReport(BaseModel):
    """
    Comprehensive Audit Rights & Supervisory Inspection Report under KWG § 25b and DORA Art. 30(3)(e).
    """
    model_config = ConfigDict(from_attributes=True)

    document_id: UUID
    overall_score: float  # 0.0 to 100.0%
    compliance_rating: str  # "VOLLSTÄNDIG KONFORM (AAA)" | "BEDINGT KONFORM (BBB)" | "KRITISCH DEFIZITÄR (CCC)"
    evaluated_at: datetime
    dora_article: str = "Art. 30 Abs. 3 lit. e VO (EU) 2022/2554 & KWG § 25b Abs. 1"
    checks: list[AuditRightCheckResult]
    notice_letter: InspectionNoticeLetter
    summary_de: str
    summary_en: str

from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field


class ClauseRiskItem(BaseModel):
    chunk_id: str
    page_number: int
    bounding_box: list[float] = Field(default_factory=lambda: [0.0, 0.0, 0.0, 0.0])
    severity: Literal["CRITICAL", "HIGH", "MEDIUM", "LOW", "CLEAN"]
    risk_score: float = Field(..., ge=0, le=100)
    title: str
    category: str
    deficiency_summary_de: str
    deficiency_summary_en: str
    statutory_ref: str
    snippet: str


class DocumentRiskHeatmap(BaseModel):
    document_id: UUID
    filename: str
    overall_risk_score: float = Field(..., ge=0, le=100)
    risk_rating: Literal["AAA", "AA", "A", "BBB", "BB", "B", "CCC"]
    critical_count: int
    high_count: int
    medium_count: int
    page_scores: dict[int, float]
    risk_items: list[ClauseRiskItem]


class DiffToken(BaseModel):
    type: Literal["equal", "delete", "insert"]
    text: str


class AmendmentProposal(BaseModel):
    rule_id: str
    title_de: str
    title_en: str
    original_text: str
    compliant_replacement_de: str
    compliant_replacement_en: str
    legal_justification_de: str
    legal_justification_en: str
    bgb_statutory_basis: str
    dora_statutory_basis: str
    diff_tokens: list[DiffToken]


class RemediationSynthesisRequest(BaseModel):
    rule_id: str = Field(default="BAFIN-AUDIT-01", description="Statutory rule identifier")
    original_clause: str = Field(..., min_length=5, description="Deficient contractual clause to be remediated")
    target_framework: str = Field(default="DORA", description="Regulatory framework: DORA, KWG, GDPR, LkSG, BGB")
    custom_parameters: dict[str, str | int | float | bool] | None = Field(
        default=None,
        description="Bespoke legal parameters such as exit_days (60/90), penalty_pct (0.2), audit_notice ('reasonable'/'48h')",
    )


class ApplyAmendmentRequest(BaseModel):
    chunk_id: str = Field(..., description="UUID of chunk to replace with compliant replacement clause")
    new_clause_text: str = Field(..., min_length=10, description="Compliant replacement clause text")
    rule_id: str = Field(default="REMEDIATION-APPLIED", description="Statutory rule ID")
    justification: str | None = Field(default=None, description="Legal justification for audit trail")


class ApplyAmendmentResponse(BaseModel):
    document_id: UUID
    chunk_id: str
    page_number: int
    new_content_preview: str
    reembedded: bool
    audit_event_id: str
    sha256_hash: str
    message: str


class LegalAmendmentAgreementResponse(BaseModel):
    document_id: UUID
    document_filename: str
    statutory_framework: str
    total_amendments: int
    amendments: list[AmendmentProposal]
    signatory_authority: str
    sha256_seal: str
    status: str = "SYNTHESIZED"

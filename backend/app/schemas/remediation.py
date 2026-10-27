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

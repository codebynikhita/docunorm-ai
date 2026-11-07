"""
Pydantic Schemas for Enterprise Multi-Contract Supply Chain Portfolio Aggregation
and BAFA Annual Statutory Reporting (§ 10 Abs. 2 LkSG).
"""

from datetime import datetime
from enum import StrEnum
from uuid import UUID

from pydantic import BaseModel, Field


class ConcentrationRiskLevel(StrEnum):
    DIVERSIFIED = "DIVERSIFIZIERT"
    MODERATE = "MODERAT_KONZENTRIERT"
    HIGH = "HOCH_KONZENTRIERT"
    CRITICAL_MONOPOLY = "KRITISCH_MONOPOLISTISCH"


class SupplierPortfolioItem(BaseModel):
    """
    Individual supplier audit summary within the enterprise portfolio.
    """
    document_id: UUID
    supplier_name: str
    contract_filename: str
    lksg_rating: str  # e.g., "AAA", "BBB", "CCC"
    overall_score: float = Field(..., ge=0.0, le=100.0)
    human_rights_score: float = Field(..., ge=0.0, le=100.0)
    environmental_score: float = Field(..., ge=0.0, le=100.0)
    governance_score: float = Field(..., ge=0.0, le=100.0)
    tier1_pass_through_status: str
    active_incidents_count: int = 0
    annual_spend_eur: float = 0.0
    spend_share_percentage: float = 0.0


class JurisdictionExposure(BaseModel):
    """
    Cross-border exposure to specific country jurisdictions across the supplier portfolio.
    """
    country_code: str
    country_name_de: str
    country_name_en: str
    supplier_count: int
    exposure_spend_eur: float
    exposure_percentage: float
    ituc_rating: int = Field(..., ge=1, le=5)
    cpi_score: int = Field(..., ge=0, le=100)
    basel_annex_vii: bool
    hazard_level: str  # "NIEDRIG" | "MODERAT" | "ERHÖHT" | "EXTREM_HOCH"


class PortfolioConcentrationMetrics(BaseModel):
    """
    Quantitative concentration metrics across the supply chain portfolio.
    Based on the Herfindahl-Hirschman Index (HHI).
    """
    herfindahl_hirschman_index: float = Field(
        ...,
        ge=0.0,
        le=10000.0,
        description="HHI concentration metric (0-1500=Diversified, 1500-2500=Moderate, >2500=High)",
    )
    concentration_level: ConcentrationRiskLevel
    top_3_vendor_share_percentage: float
    single_points_of_failure_count: int
    recommendation_de: str
    recommendation_en: str


class BafaAnnualReportSynthesis(BaseModel):
    """
    Official Annual Corporate Due Diligence Report Synthesis
    according to § 10 Abs. 2 LkSG and BAFA reporting directives.
    """
    tenant_id: UUID
    reporting_year: int = 2026
    submission_deadline: str = "31. März 2027"
    generated_at: datetime
    total_suppliers_audited: int
    direct_tier1_count: int
    indirect_tier_n_count: int
    portfolio_compliance_score: float = Field(..., ge=0.0, le=100.0)
    portfolio_rating: str  # "AAA" | "BBB" | "CCC"
    human_rights_portfolio_average: float
    environmental_portfolio_average: float
    governance_portfolio_average: float
    concentration_metrics: PortfolioConcentrationMetrics
    active_substantiated_knowledge_alerts: int
    resolved_capa_milestones_count: int
    total_capa_penalties_secured_eur: float
    grievance_cases_logged: int
    high_hazard_jurisdictions_count: int
    supplier_items: list[SupplierPortfolioItem]
    jurisdiction_breakdown: list[JurisdictionExposure]
    bafa_submission_readiness: str  # "EINREICHUNGSBEREIT (READY)" | "NACHBESSERUNG_ERFORDERLICH"
    executive_summary_de: str
    executive_summary_en: str

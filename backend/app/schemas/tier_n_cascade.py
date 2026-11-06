"""
Pydantic Schemas for Multi-Tier Supply Chain Cascade Audits and Cross-Border
Vendor Remediation Tracking under § 9 LkSG (Besondere Sorgfaltspflichten bei
mittelbaren Zulieferern) and official BAFA administrative guidelines.
"""

from datetime import datetime
from enum import StrEnum
from uuid import UUID

from pydantic import BaseModel, Field


class SupplyChainTier(StrEnum):
    TIER_1_DIRECT = "TIER_1_DIREKT"
    TIER_2_INDIRECT_COMPONENTS = "TIER_2_KOMPONENTEN"
    TIER_3_RAW_MATERIALS = "TIER_3_ROHSTOFFE"
    TIER_N_LOGISTICS_SERVICE = "TIER_N_LOGISTIK_SERVICES"


class PassThroughClauseStatus(StrEnum):
    PRESENT_ENFORCEABLE = "VOLLSTÄNDIG_DURCHSETZBAR"
    PARTIAL_INFORMATIONAL = "TEILWEISE_UNVOLLSTÄNDIG"
    MISSING_DEFICIENT = "FEHLEND_RECHTSWIDRIG"


class AuditRightsCascade(StrEnum):
    FULL_UNRESTRICTED = "UNEINGESCHRÄNKT_VOR_ORT"
    CONDITIONAL_48H = "BEDINGT_48H_VORANKÜNDIGUNG"
    NO_RIGHTS = "KEINE_KONTROLLRECHTE"


class JurisdictionHazardLevel(StrEnum):
    LOW = "NIEDRIG"
    MODERATE = "MODERAT"
    HIGH = "ERHÖHT"
    EXTREME = "EXTREM_HOCH"


class EscalationStage(StrEnum):
    STAGE_1_AD_HOC_ANALYSIS = "STUFE_1_ANLASSBEZOGENE_ANALYSE"  # 14 days
    STAGE_2_PREVENTIVE_CONCEPT = "STUFE_2_PRAEVENTIONSKONZEPT"  # 30 days
    STAGE_3_ON_SITE_AUDIT = "STUFE_3_VOR_ORT_AUDIT"  # 60 days
    STAGE_4_SUSPENSION_TERMINATION = "STUFE_4_VERTRAGSSUSPENSION"  # 90 days


class CountryRiskProfile(BaseModel):
    """
    Standardized cross-border jurisdiction risk index.
    Based on ITUC Global Rights Index, Corruption Perceptions Index (CPI),
    and Basel Convention Annex VII ratification status.
    """
    country_code: str = Field(..., description="ISO 3166-1 alpha-2 country code")
    country_name_de: str
    country_name_en: str
    ituc_rating: int = Field(..., ge=1, le=5, description="ITUC Global Rights Index rating (1=Best, 5=Worst)")
    cpi_score: int = Field(..., ge=0, le=100, description="Corruption Perceptions Index (0=High corruption, 100=Clean)")
    basel_annex_vii: bool = Field(..., description="True if OECD/EU/Liechtenstein territory under Basel Ban Amendment")
    hazard_level: JurisdictionHazardLevel
    risk_summary_de: str


class CascadeSupplierNode(BaseModel):
    """
    Represents an entity node in the multi-tier supply chain cascade.
    """
    node_id: str
    name: str
    tier: SupplyChainTier
    country: CountryRiskProfile
    sector: str
    component_or_service: str
    pass_through_status: PassThroughClauseStatus
    audit_rights: AuditRightsCascade
    has_substantiated_knowledge: bool = Field(
        default=False,
        description="True if substantiated knowledge (substantiierte Kenntnis nach § 9 Abs. 2 LkSG) exists"
    )
    active_incidents_count: int = 0
    statutory_citation: str = "§ 9 Abs. 1, 2 LkSG"


class SubstantiatedKnowledgeIncident(BaseModel):
    """
    Ad-hoc incident triggered under § 9 Abs. 2 LkSG upon substantiated knowledge
    of human rights or environmental violations at an indirect supplier.
    """
    incident_id: str
    supplier_node_id: str
    supplier_name: str
    tier: SupplyChainTier
    violation_title_de: str
    violation_title_en: str
    statutory_basis: str
    source_of_knowledge: str  # e.g., "Whistleblower-Meldung", "NGO-Untersuchungsbericht", "BAFA-Auskunftsersuchen"
    severity: str  # "KRITISCH" | "HOCH" | "MITTEL"
    escalation_stage: EscalationStage
    statutory_deadline_days: int
    days_remaining: int
    required_remediation_de: str
    required_remediation_en: str
    bafa_notification_required: bool = True


class TierNCascadeAuditReport(BaseModel):
    """
    Comprehensive Multi-Tier Supply Chain Cascade Audit Report under § 9 LkSG.
    """
    document_id: UUID
    evaluation_timestamp: datetime
    overall_cascade_score: float = Field(..., ge=0.0, le=100.0, description="Overall cascade compliance score (0-100%)")
    compliance_rating: str = Field(..., description="Institutional Rating: AAA, BBB, or CCC")
    statutory_framework: str = "§ 9 LkSG (Mittelbare Zulieferer) & BAFA Handreichung"
    primary_vendor_name: str
    pass_through_enforceable_rate: float = Field(..., ge=0.0, le=100.0)
    total_tiers_tracked: int
    direct_suppliers_count: int
    indirect_suppliers_count: int
    substantiated_knowledge_active: bool
    supplier_nodes: list[CascadeSupplierNode]
    active_incidents: list[SubstantiatedKnowledgeIncident]
    jurisdiction_breakdown: list[CountryRiskProfile]
    bafa_adhoc_filing_recommended: bool
    summary_de: str
    summary_en: str

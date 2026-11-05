from datetime import UTC, datetime
from enum import StrEnum
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field


class EnvironmentalConvention(StrEnum):
    MINAMATA_MERCURY = "MINAMATA_MERCURY"          # § 2 Abs. 3 Nr. 1 LkSG (Quecksilber-Übereinkommen)
    STOCKHOLM_POPS = "STOCKHOLM_POPS"              # § 2 Abs. 3 Nr. 2 LkSG (Persistente organische Schadstoffe)
    BASEL_HAZARDOUS_WASTE = "BASEL_HAZARDOUS_WASTE" # § 2 Abs. 3 Nr. 3 LkSG (Grenzüberschreitende Sonderabfälle)


class SubstanceComplianceStatus(StrEnum):
    PROHIBITED = "PROHIBITED"                    # Total international ban (e.g., aldrin, mercury in chlor-alkali)
    RESTRICTED_PHASEOUT = "RESTRICTED_PHASEOUT"  # Mandatory phase-out schedule active
    CONTROLLED = "CONTROLLED"                    # Permitted under strict threshold monitoring & emission limits
    COMPLIANT = "COMPLIANT"                      # Verified zero hazardous discharge or substitute deployed


class PicProcedureStatus(StrEnum):
    VERIFIED_APPROVED = "VERIFIED_APPROVED"      # Prior Informed Consent formally approved by receiving state
    MISSING_CONSENT = "MISSING_CONSENT"          # Missing official import permit (High BAFA fine risk)
    PROHIBITED_EXPORT = "PROHIBITED_EXPORT"      # Export banned under Basel Ban Amendment (Annex VII to non-Annex VII)


class SubstanceTrackingItem(BaseModel):
    id: str
    substance_name: str
    cas_number: str = Field(..., description="Chemical Abstracts Service registry number")
    convention: EnvironmentalConvention
    status: SubstanceComplianceStatus
    threshold_limit: str = Field(..., description="e.g. '0.1 mg/kg' or '0% (Total Ban)'")
    detected_in_contract: bool
    evidence_snippet: str | None = None
    page_number: int | None = None
    statutory_article: str = Field(..., description="e.g. '§ 2 Abs. 3 Nr. 1 LkSG · Art. 4 Minamata'")
    remediation_guidance: str


class WasteShipmentManifest(BaseModel):
    manifest_id: str
    waste_code: str = Field(..., description="Basel Y-code or European Waste Catalogue (EWC) 6-digit code")
    waste_description: str
    origin_country: str
    destination_country: str
    pic_status: PicProcedureStatus
    export_authorized: bool
    disposal_or_recycling_facility: str
    certifying_authority: str = Field(..., description="e.g. 'Umweltbundesamt (UBA)' or national authority")
    statutory_reference: str = Field(default="§ 2 Abs. 3 Nr. 3 LkSG · Basler Übereinkommen Art. 6")


class EnvironmentalAuditReport(BaseModel):
    document_id: UUID
    filename: str
    supplier_name: str
    overall_environmental_score: float = Field(..., ge=0.0, le=100.0, description="Overall compliance index")
    environmental_rating: Literal["AAA", "AA", "A", "BBB", "BB", "B", "CCC"]
    minamata_mercury_status: SubstanceComplianceStatus
    stockholm_pops_status: SubstanceComplianceStatus
    basel_waste_status: PicProcedureStatus
    total_substances_audited: int
    prohibited_substances_count: int
    waste_shipments_audited: int
    unauthorized_shipments_count: int
    substances: list[SubstanceTrackingItem]
    waste_manifests: list[WasteShipmentManifest]
    bafa_environmental_verdict_de: str
    bafa_environmental_verdict_en: str
    generated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

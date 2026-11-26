"""
DocuNorm AI — Day 40: DORA Art. 28(3) Register of Information & Portfolio Batch Remediation Schemas.
Conforms to ESA Final Draft ITS (JC 2024 05 / EBA/ITS/2024/01) and BaFin Circular 10/2026 mandates
for ICT Third-Party Service Provider Registers and portfolio-wide contract harmonization.
"""

from datetime import date, datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field

ICTServiceCategory = Literal[
    "CLOUD_SAAS",
    "CLOUD_PAAS",
    "CLOUD_IAAS",
    "DATACENTER_COLOCATION",
    "SOFTWARE_LICENSE",
    "SECURITY_OPERATIONS",
    "CORE_BANKING",
]

FunctionCriticality = Literal[
    "CRITICAL_IMPORTANT",
    "NON_CRITICAL",
    "SUPPORTING",
]

RemediationStatus = Literal[
    "CLEAN",
    "REMEDIATION_REQUIRED",
    "REMEDIATED_AUTOMATED",
]


class DoraRegisterEntry(BaseModel):
    contract_id: UUID
    contract_filename: str
    vendor_legal_name: str
    vendor_lei: str = Field(..., description="Legal Entity Identifier (20 alphanumeric chars) or statutory tax code")
    vendor_country: str = Field(default="DE", description="ISO 3166-1 alpha-2 country code")
    service_category: ICTServiceCategory
    criticality: FunctionCriticality
    governing_law: str = Field(default="German Law (BGB / HGB)")
    has_subcontracting: bool = True
    subcontractor_depth: int = Field(default=2, ge=1, le=5, description="Cascading subcontracting tier level (e.g. Tier-4)")
    audit_rights_compliant: bool = False
    exit_notice_period_days: int = Field(default=90, description="Statutory exit termination notice period")
    substitution_time_months: int = Field(default=6, description="Estimated time required to substitute service provider")
    remediation_status: RemediationStatus = "REMEDIATION_REQUIRED"
    last_audited_at: datetime


class DoraInformationRegister(BaseModel):
    tenant_id: UUID
    reporting_entity_name: str
    reporting_date: date
    reporting_lei: str
    total_ict_contracts: int
    critical_ict_contracts: int
    overall_compliance_rate: float = Field(..., ge=0.0, le=100.0, description="Percentage of fully compliant contracts")
    entries: list[DoraRegisterEntry]
    esa_template_version: str = "ESA JC 2024 05 / DORA Art. 28(3)"
    sha256_register_seal: str


class BatchRemediationItem(BaseModel):
    document_id: UUID
    document_filename: str
    vendor_name: str
    clauses_remediated_count: int
    pre_remediation_risk_score: float = Field(..., ge=0.0, le=100.0)
    post_remediation_risk_score: float = Field(..., ge=0.0, le=100.0)
    remediated_clause_types: list[str]
    synthesized_amendment_title: str


class BatchRemediationResult(BaseModel):
    tenant_id: UUID
    executed_at: datetime
    total_contracts_processed: int
    total_clauses_synthesized: int
    pre_risk_portfolio_average: float = Field(..., ge=0.0, le=100.0)
    post_risk_portfolio_average: float = Field(..., ge=0.0, le=100.0)
    risk_reduction_percentage: float = Field(..., ge=0.0, le=100.0)
    remediation_items: list[BatchRemediationItem]
    sha256_batch_seal: str

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

from app.schemas.erp_export import BatchInvoiceProcessingItem, ChartOfAccounts


class CapstoneDiscrepancyDetail(BaseModel):
    index: int
    invoice_number: str
    filename: str
    rule_violated: str
    statutory_standard: str
    risk_level: Literal["HOCH", "KRITISCH"]
    rejection_reason: str
    remedial_action: str


class Week4CapstoneSummary(BaseModel):
    batch_id: str
    processed_at: datetime
    total_invoices: int = 100
    compliant_count: int = 95
    warning_count: int = 0
    rejected_count: int = 5
    compliance_rate_percent: float = 95.0
    total_net_eur: float
    total_tax_eur: float
    total_grand_eur: float
    execution_time_ms: float
    throughput_invoices_per_sec: float
    chart_of_accounts: ChartOfAccounts = ChartOfAccounts.SKR03
    category_distribution: dict[str, int] = Field(
        default_factory=lambda: {
            "B2B_COMFORT": 40,
            "B2G_XRECHNUNG": 25,
            "REVERSE_CHARGE_13B": 15,
            "REDUCED_VAT_7": 10,
            "SMALL_VALUE_33": 5,
            "DISCREPANT_FRAUD_SIM": 5,
        }
    )
    gobd_sha256_batch_hash: str
    discrepancies: list[CapstoneDiscrepancyDetail] = Field(default_factory=list)
    items: list[BatchInvoiceProcessingItem] = Field(default_factory=list)
    datev_csv_content: str
    sap_json_content: str

from datetime import date, datetime
from enum import StrEnum
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field


class ZugferdProfile(StrEnum):
    MINIMUM = "MINIMUM"
    BASIC_WL = "BASIC_WL"
    BASIC = "BASIC"
    EN16931 = "EN16931"  # Comfort Profile (Standard B2B / EN 16931 compliance)
    EXTENDED = "EXTENDED"
    XRECHNUNG = "XRECHNUNG"  # German Federal B2G Standard (KoSIT)


class ZugferdInvoiceType(StrEnum):
    COMMERCIAL_INVOICE = "380"      # Handelsrechnung
    CREDIT_NOTE = "381"             # Gutschrift
    DEBIT_NOTE = "383"              # Belastungsanzeige
    CORRECTED_INVOICE = "384"       # Rechnungskorrektur
    ADVANCE_PAYMENT = "386"         # Vorauszahlungsrechnung
    SELF_BILLED_INVOICE = "389"     # Gutschriftsverfahren


class VatCategoryCode(StrEnum):
    STANDARD = "S"          # Standard rate (e.g. 19% in DE)
    REDUCED = "Z"           # Zero rated goods
    EXEMPT = "E"            # Exempt from tax
    REVERSE_CHARGE = "AE"   # Reverse charge (§ 13b UStG)
    INTRA_COMMUNITY = "K"   # Intra-community supply
    EXPORT = "G"            # Export outside EU
    NOT_SUBJECT_TO_VAT = "O"  # Services outside scope of tax


class ZugferdPostalAddress(BaseModel):
    postcode: str | None = None
    line_one: str | None = None
    line_two: str | None = None
    city_name: str | None = None
    country_id: str = "DE"
    country_sub_division_name: str | None = None


class ZugferdParty(BaseModel):
    name: str
    commercial_registration_id: str | None = None  # e.g. HRB 12345
    vat_id: str | None = None                      # e.g. DE123456789
    tax_number: str | None = None                  # e.g. 11/123/45678
    contact_name: str | None = None
    contact_email: str | None = None
    contact_phone: str | None = None
    postal_address: ZugferdPostalAddress | None = None


class ZugferdLineItem(BaseModel):
    line_id: str
    item_name: str
    item_description: str | None = None
    seller_item_id: str | None = None
    buyer_item_id: str | None = None
    billed_quantity: float = Field(..., description="Billed quantity")
    unit_code: str = Field(default="C62", description="UN/ECE Rec 20 unit code (e.g. C62, H87, HUR, KGM)")
    net_price_eur: float = Field(..., description="Net unit price in invoice currency")
    line_total_eur: float = Field(..., description="Net line amount (quantity * unit price)")
    vat_category_code: VatCategoryCode = VatCategoryCode.STANDARD
    vat_rate_percent: float = Field(default=19.0, description="Applicable tax rate (e.g. 19.0 or 7.0)")


class ZugferdTaxSubtotal(BaseModel):
    tax_category_code: VatCategoryCode
    tax_rate_percent: float
    taxable_amount_eur: float
    tax_amount_eur: float
    exemption_reason: str | None = None


class ZugferdMonetarySummation(BaseModel):
    line_total_amount_eur: float = Field(..., description="Sum of all line amounts (BT-106)")
    charge_total_amount_eur: float = Field(default=0.0, description="Sum of allowances/surcharges on document level (BT-108)")
    allowance_total_amount_eur: float = Field(default=0.0, description="Sum of discounts on document level (BT-107)")
    tax_basis_total_amount_eur: float = Field(..., description="Invoice net total (BT-109)")
    tax_total_amount_eur: float = Field(..., description="Total VAT amount (BT-110)")
    grand_total_amount_eur: float = Field(..., description="Invoice total with VAT (BT-112)")
    prepaid_amount_eur: float = Field(default=0.0, description="Prepaid amount (BT-113)")
    due_payable_amount_eur: float = Field(..., description="Amount due for payment (BT-115)")


class ZugferdValidationIssue(BaseModel):
    code: str
    severity: Literal["ERROR", "WARNING"]
    rule_id: str
    description: str
    statutory_reference: str  # e.g. "EN 16931 BR-CO-10", "§ 14 UStG Abs. 4"


class ZugferdValidationReport(BaseModel):
    is_en16931_compliant: bool
    detected_profile: ZugferdProfile
    profile_urn: str
    syntax_format: Literal["UN/CEFACT CII", "UBL 2.1 INVOICE", "UNKNOWN"]
    has_math_discrepancy: bool
    issues: list[ZugferdValidationIssue]
    passed_rules_count: int
    total_rules_evaluated: int
    validation_summary_de: str


class ZugferdInvoiceExtraction(BaseModel):
    document_id: UUID | None = None
    filename: str
    is_hybrid_pdf_a3: bool
    xml_filename: str | None = None
    raw_xml_content: str | None = None
    extracted_at: datetime

    # Header information
    profile: ZugferdProfile
    profile_urn: str
    invoice_number: str
    invoice_type_code: ZugferdInvoiceType
    invoice_type_name_de: str
    issue_date: date | None = None
    currency_code: str = "EUR"

    # Parties
    seller: ZugferdParty
    buyer: ZugferdParty

    # Administrative references
    buyer_reference: str | None = Field(default=None, description="Leitweg-ID or Buyer Reference (BT-10)")
    order_reference: str | None = None
    contract_reference: str | None = None

    # Payment & Bank Details
    payment_terms_description: str | None = None
    payment_due_date: date | None = None
    iban: str | None = None
    bic: str | None = None
    payment_means_code: str | None = None  # e.g. 58 (SEPA credit transfer)

    # Line Items & Sums
    line_items: list[ZugferdLineItem]
    tax_subtotals: list[ZugferdTaxSubtotal]
    monetary_summation: ZugferdMonetarySummation

    # EN 16931 Validation
    validation_report: ZugferdValidationReport

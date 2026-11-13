from datetime import date, datetime
from enum import StrEnum
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field


class ChartOfAccounts(StrEnum):
    SKR03 = "SKR03"  # Standard-Kontenrahmen 03 (Prozessgliederungsprinzip)
    SKR04 = "SKR04"  # Standard-Kontenrahmen 04 (Abschlussgliederungsprinzip)
    IKR = "IKR"      # Industrie-Kontenrahmen


class DatevExportConfig(BaseModel):
    chart_of_accounts: ChartOfAccounts = ChartOfAccounts.SKR03
    beraternummer: int = Field(default=1001, description="DATEV Beraternummer (Mandantenverwalter)")
    mandantennummer: int = Field(default=70001, description="DATEV Mandantennummer")
    wirtschaftsjahr_beginn: date = Field(default_factory=lambda: date(2026, 1, 1))
    sachkonto_wareneingang_19: str = Field(default="3400", description="SKR03: 3400 / SKR04: 5400 (Wareneingang 19%)")
    sachkonto_wareneingang_7: str = Field(default="3300", description="SKR03: 3300 / SKR04: 5300 (Wareneingang 7%)")
    sachkonto_reverse_charge: str = Field(default="3120", description="SKR03: 3120 / SKR04: 5920 (Bauleistungen / § 13b UStG)")
    sachkonto_steuerfrei: str = Field(default="3200", description="SKR03: 3200 / SKR04: 5200 (Steuerfreie Bezüge)")
    kreditor_start_konto: int = Field(default=70000, description="Nummernkreis Kreditoren (70000 - 79999)")
    festschreibung: bool = Field(default=True, description="GoBD Festschreibungskennzeichen (1 = festgeschrieben)")


class DatevBookingRow(BaseModel):
    umsatz_eur: float = Field(..., description="Umsatzbetrag in EUR (positiv)")
    soll_haben_kz: Literal["S", "H"] = Field(default="S", description="S = Soll (Aufwand), H = Haben")
    waehrung: str = Field(default="EUR", description="Währungskennzeichen ISO 4217")
    konto: str = Field(..., description="Aufwandskonto (SKR03/SKR04)")
    gegenkonto: str = Field(..., description="Kreditorenkonto (Personenkonto)")
    bu_schluessel: str = Field(default="", description="DATEV Steuerschlüssel / Berichtigungsschlüssel")
    belegdatum: str = Field(..., description="Belegdatum TTMM (4-stellig)")
    belegfeld_1: str = Field(..., description="Rechnungsnummer (max. 36 Zeichen)")
    belegfeld_2: str = Field(default="", description="Fälligkeit oder Auftragsnummer")
    buchungstext: str = Field(..., description="Buchungstext (max. 60 Zeichen)")
    beleglink: str = Field(default="", description="Verknüpfung zu Belegbild / PDF SHA-256")
    festschreibung: int = Field(default=1, description="1 = Festgeschrieben gem. GoBD, 0 = Offen")


class SapS4HanaExportConfig(BaseModel):
    company_code: str = Field(default="1000", description="SAP Buchungskreis (Company Code)")
    fiscal_year: int = Field(default=2026, description="Geschäftsjahr")
    document_type: str = Field(default="KR", description="SAP Belegart (KR = Lieferantenrechnung, KG = Gutschrift)")
    cost_center: str = Field(default="CC_IT_01", description="SAP Kostenstelle")
    gl_account_expense_19: str = Field(default="0000400000", description="SAP Sachkonto 19% Vorsteuer")
    gl_account_expense_7: str = Field(default="0000410000", description="SAP Sachkonto 7% Vorsteuer")
    gl_account_reverse_charge: str = Field(default="0000420000", description="SAP Sachkonto § 13b UStG")


class SapS4HanaJournalEntryItem(BaseModel):
    item_number: int = Field(..., description="Positionsnummer 1..n")
    account_type: Literal["K", "S", "T"] = Field(..., description="K = Kreditor, S = Sachkonto, T = Steuer")
    account: str = Field(..., description="Kreditorennummer oder Sachkontonummer")
    amount_eur: float = Field(..., description="Betrag in Belegwährung")
    debit_credit_code: Literal["S", "H"] = Field(..., description="S = Soll (Debit), H = Haben (Credit)")
    tax_code: str = Field(default="", description="SAP Steuerkennzeichen (V1=19%, V2=7%, V0=0%, RC=Reverse Charge)")
    tax_base_amount_eur: float | None = None
    cost_center: str | None = None
    text: str = Field(..., description="Positionstext (max 50 Zeichen)")


class SapS4HanaJournalEntry(BaseModel):
    company_code: str
    fiscal_year: int
    accounting_document_type: str
    document_date: str  # YYYY-MM-DD
    posting_date: str   # YYYY-MM-DD
    document_reference_id: str
    document_header_text: str
    transaction_currency: str = "EUR"
    items: list[SapS4HanaJournalEntryItem] = Field(default_factory=list)


class BatchInvoiceProcessingItem(BaseModel):
    invoice_index: int
    document_id: UUID | None = None
    filename: str
    invoice_number: str
    issue_date: date | None = None
    due_date: date | None = None
    seller_name: str
    seller_vat_id: str | None = None
    buyer_name: str
    profile: str
    currency: str = "EUR"
    net_amount_eur: float
    tax_amount_eur: float
    grand_total_eur: float
    is_en16931_compliant: bool
    is_ustg_compliant: bool
    leitweg_id: str | None = None
    leitweg_valid: bool | None = None
    status: Literal["COMPLIANT", "WARNING", "REJECTED"]
    kreditor_konto: str
    aufwand_konto: str
    bu_schluessel: str
    datev_booking_row: DatevBookingRow
    sap_journal_entry: SapS4HanaJournalEntry
    validation_issues_count: int = 0
    vat_findings_count: int = 0


class BatchIngestionSummary(BaseModel):
    batch_id: str
    processed_at: datetime
    total_invoices_processed: int
    compliant_invoices_count: int
    warning_invoices_count: int
    rejected_invoices_count: int
    total_net_amount_eur: float
    total_tax_amount_eur: float
    total_grand_amount_eur: float
    chart_of_accounts: ChartOfAccounts
    items: list[BatchInvoiceProcessingItem] = Field(default_factory=list)
    datev_csv_content: str
    sap_json_content: str

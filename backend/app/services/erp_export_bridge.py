import io
import json
import zipfile
from datetime import UTC, datetime
from uuid import UUID, uuid4

from app.schemas.erp_export import (
    BatchIngestionSummary,
    BatchInvoiceProcessingItem,
    ChartOfAccounts,
    DatevBookingRow,
    DatevExportConfig,
    SapS4HanaExportConfig,
    SapS4HanaJournalEntry,
    SapS4HanaJournalEntryItem,
)
from app.schemas.zugferd_invoice import VatCategoryCode, ZugferdInvoiceExtraction
from app.services.zugferd_extractor import zugferd_extractor_service


class ErpExportBridgeService:
    """
    Enterprise Sovereign ERP & Accounting Export Bridge for ZUGFeRD 2.3 & XRechnung.
    Conforms to DATEV Format 700 (Buchungsstapel EXTF) and SAP S/4HANA Finance (JournalEntry API).
    Complies with GoBD §§ 146, 147 AO (immutable audit trail, Festschreibung, SHA-256 seal).
    """

    # SKR03 / SKR04 Account Mapping Matrix for German Standard Invoicing
    ACCOUNT_MAPPING: dict[ChartOfAccounts, dict[str, tuple[str, str, str]]] = {
        ChartOfAccounts.SKR03: {
            "S_19": ("3400", "9", "V1"),     # Wareneingang 19% Vorsteuer, BU 9
            "S_7": ("3300", "8", "V2"),      # Wareneingang 7% Vorsteuer, BU 8
            "AE_0": ("3120", "19", "RC"),    # § 13b UStG Reverse Charge, BU 19
            "K_0": ("3125", "10", "IC"),     # Innergemeinschaftlicher Erwerb, BU 10
            "E_0": ("3200", "0", "V0"),      # Steuerfreie Umsätze, BU 0
            "DEFAULT": ("3400", "9", "V1"),  # Fallback Standard
        },
        ChartOfAccounts.SKR04: {
            "S_19": ("5400", "9", "V1"),     # Wareneingang 19% Vorsteuer, BU 9
            "S_7": ("5300", "8", "V2"),      # Wareneingang 7% Vorsteuer, BU 8
            "AE_0": ("5920", "19", "RC"),    # § 13b UStG Bauleistungen / Reverse Charge
            "K_0": ("5425", "10", "IC"),     # Innergemeinschaftlicher Erwerb
            "E_0": ("5200", "0", "V0"),      # Steuerfreie Umsätze
            "DEFAULT": ("5400", "9", "V1"),  # Fallback Standard
        },
        ChartOfAccounts.IKR: {
            "S_19": ("5100", "9", "V1"),
            "S_7": ("5100", "8", "V2"),
            "AE_0": ("5190", "19", "RC"),
            "K_0": ("5195", "10", "IC"),
            "E_0": ("5180", "0", "V0"),
            "DEFAULT": ("5100", "9", "V1"),
        },
    }

    @classmethod
    def _resolve_account_and_tax(
        cls,
        extraction: ZugferdInvoiceExtraction,
        chart: ChartOfAccounts,
    ) -> tuple[str, str, str]:
        """Resolves (Aufwandskonto, DATEV BU-Schlüssel, SAP Tax Code)."""
        mapping = cls.ACCOUNT_MAPPING.get(chart, cls.ACCOUNT_MAPPING[ChartOfAccounts.SKR03])

        # Priority 1: Reverse Charge (§ 13b UStG)
        if extraction.vat_audit and extraction.vat_audit.reverse_charge_detected:
            return mapping.get("AE_0", mapping["DEFAULT"])

        # Priority 2: Intra-Community Supply (§ 6a UStG)
        if extraction.vat_audit and extraction.vat_audit.intra_community_supply_detected:
            return mapping.get("K_0", mapping["DEFAULT"])

        # Priority 3: Subtotals Analysis
        if extraction.tax_subtotals:
            first_sub = extraction.tax_subtotals[0]
            cat = first_sub.tax_category_code
            rate = first_sub.tax_rate_percent

            if cat == VatCategoryCode.REVERSE_CHARGE:
                return mapping.get("AE_0", mapping["DEFAULT"])
            if cat == VatCategoryCode.INTRA_COMMUNITY:
                return mapping.get("K_0", mapping["DEFAULT"])
            if cat == VatCategoryCode.EXEMPT or cat == VatCategoryCode.REDUCED and rate == 0:
                return mapping.get("E_0", mapping["DEFAULT"])
            if abs(rate - 7.0) < 0.5:
                return mapping.get("S_7", mapping["DEFAULT"])
            if abs(rate - 19.0) < 0.5:
                return mapping.get("S_19", mapping["DEFAULT"])

        return mapping["DEFAULT"]

    @classmethod
    def _assign_creditor_account(cls, extraction: ZugferdInvoiceExtraction, base_number: int, index: int) -> str:
        """Assigns a deterministic creditor subledger account (e.g. 70001, 70002)."""
        seller_key = (extraction.seller.vat_id or extraction.seller.name or "").strip()
        hashed = sum(ord(c) for c in seller_key) % 900
        return str(base_number + hashed + 1)

    @classmethod
    def create_datev_row(
        cls,
        extraction: ZugferdInvoiceExtraction,
        config: DatevExportConfig,
        kreditor_konto: str,
    ) -> DatevBookingRow:
        """Converts an extracted e-invoice into an official DATEV Format 700 booking row."""
        aufwand_konto, bu_key, _ = cls._resolve_account_and_tax(extraction, config.chart_of_accounts)

        issue_date = extraction.issue_date or datetime.now(UTC).date()
        belegdatum = issue_date.strftime("%d%m")  # DDMM per DATEV specification

        due_date_str = extraction.payment_due_date.strftime("%d.%m.%Y") if extraction.payment_due_date else ""

        # Buchungstext max 60 chars per DATEV
        raw_text = f"{extraction.seller.name} {extraction.invoice_number}"
        buchungstext = raw_text[:60]

        beleglink = extraction.filename[:36]

        return DatevBookingRow(
            umsatz_eur=extraction.monetary_summation.grand_total_amount_eur,
            soll_haben_kz="S",  # S = Soll (Aufwand gegen Kreditor)
            waehrung=extraction.currency_code or "EUR",
            konto=aufwand_konto,
            gegenkonto=kreditor_konto,
            bu_schluessel=bu_key,
            belegdatum=belegdatum,
            belegfeld_1=extraction.invoice_number[:36],
            belegfeld_2=due_date_str[:36],
            buchungstext=buchungstext,
            beleglink=beleglink,
            festschreibung=1 if config.festschreibung else 0,
        )

    @classmethod
    def create_sap_journal_entry(
        cls,
        extraction: ZugferdInvoiceExtraction,
        config: SapS4HanaExportConfig,
        kreditor_konto: str,
    ) -> SapS4HanaJournalEntry:
        """Converts an extracted e-invoice into a SAP S/4HANA Cloud Finance Journal Entry (CE_JOURNALENTRY)."""
        _, _, tax_code = cls._resolve_account_and_tax(extraction, ChartOfAccounts.SKR03)

        issue_date = extraction.issue_date or datetime.now(UTC).date()
        doc_date_str = issue_date.strftime("%Y-%m-%d")
        posting_date_str = datetime.now(UTC).strftime("%Y-%m-%d")

        ms = extraction.monetary_summation
        grand_total = ms.grand_total_amount_eur
        net_total = ms.tax_basis_total_amount_eur
        tax_total = ms.tax_total_amount_eur

        items: list[SapS4HanaJournalEntryItem] = []

        # Item 1: Vendor Payable Line (Account Type K, Credit H)
        items.append(
            SapS4HanaJournalEntryItem(
                item_number=1,
                account_type="K",
                account=kreditor_konto,
                amount_eur=grand_total,
                debit_credit_code="H",
                tax_code=tax_code,
                text=f"Verbindlichkeit {extraction.seller.name[:30]}",
            )
        )

        # Item 2: Expense G/L Line (Account Type S, Debit S)
        items.append(
            SapS4HanaJournalEntryItem(
                item_number=2,
                account_type="S",
                account=config.gl_account_expense_19,
                amount_eur=net_total,
                debit_credit_code="S",
                tax_code=tax_code,
                tax_base_amount_eur=net_total,
                cost_center=config.cost_center,
                text=f"Aufwand {extraction.invoice_number[:25]}",
            )
        )

        # Item 3: VAT Line (Account Type T, Debit S) if tax applies
        if tax_total > 0.01:
            items.append(
                SapS4HanaJournalEntryItem(
                    item_number=3,
                    account_type="T",
                    account="0000157600",  # SAP Standard Vorsteuer 19%
                    amount_eur=tax_total,
                    debit_credit_code="S",
                    tax_code=tax_code,
                    tax_base_amount_eur=net_total,
                    text=f"Vorsteuer 19% {extraction.invoice_number[:20]}",
                )
            )

        return SapS4HanaJournalEntry(
            company_code=config.company_code,
            fiscal_year=config.fiscal_year,
            accounting_document_type=config.document_type,
            document_date=doc_date_str,
            posting_date=posting_date_str,
            document_reference_id=extraction.invoice_number[:16],
            document_header_text=f"DocuNorm e-Rechnung {extraction.invoice_number}"[:25],
            transaction_currency=extraction.currency_code or "EUR",
            items=items,
        )

    @classmethod
    def generate_datev_csv(
        cls,
        rows: list[DatevBookingRow],
        config: DatevExportConfig,
    ) -> str:
        """
        Generates official DATEV Format 700 CSV content conforming to DATEV Buchungsstapel.
        Uses exact header rows and semicolon delimiters with German comma decimal representation.
        """
        now = datetime.now(UTC)
        datum_str = now.strftime("%Y%m%d")
        uhrzeit_str = now.strftime("%H%M%S")
        wj_str = config.wirtschaftsjahr_beginn.strftime("%Y%m%d")

        # DATEV Header Row 1 (Metadaten)
        header_1 = (
            f'"EXTF";700;21;"Buchungsstapel";12;{datum_str};{uhrzeit_str};"DocuNorm Sovereign AI";'
            f'"";"";{config.beraternummer};{config.mandantennummer};{wj_str};4;{datum_str};{datum_str};'
            f'"DocuNorm ZUGFeRD 2027 Stapel";"";1;;;;"EUR";;'
        )

        # DATEV Header Row 2 (Feldbezeichnungen)
        header_2 = (
            '"Umsatz (ohne Soll/Haben-Kz)";"Soll/Haben-Kennzeichen";"WKZ Umsatz";"Konto";'
            '"Gegenkonto (ohne BU-Schlüssel)";"BU-Schlüssel";"Belegdatum";"Belegfeld 1";'
            '"Belegfeld 2";"Buchungstext";"Beleglink";"Festschreibung"'
        )

        lines = [header_1, header_2]

        for r in rows:
            umsatz_formatted = f"{r.umsatz_eur:.2f}".replace(".", ",")
            line = (
                f'{umsatz_formatted};"{r.soll_haben_kz}";"{r.waehrung}";"{r.konto}";'
                f'"{r.gegenkonto}";"{r.bu_schluessel}";"{r.belegdatum}";"{r.belegfeld_1}";'
                f'"{r.belegfeld_2}";"{r.buchungstext}";"{r.beleglink}";{r.festschreibung}'
            )
            lines.append(line)

        return "\r\n".join(lines) + "\r\n"

    @classmethod
    def generate_sap_json(
        cls,
        entries: list[SapS4HanaJournalEntry],
    ) -> str:
        """Generates structured JSON payload compliant with SAP S/4HANA Cloud Finance JournalEntry API."""
        payload = {
            "MessageHeader": {
                "CreationDateTime": datetime.now(UTC).isoformat(),
                "SenderBusinessSystemID": "DOCUNORM_SOVEREIGN_AI",
                "RecipientBusinessSystemID": "SAP_S4HANA_FINANCE",
            },
            "JournalEntryCreateRequest": [entry.model_dump() for entry in entries],
        }
        return json.dumps(payload, indent=2, ensure_ascii=False)

    @classmethod
    def process_batch(
        cls,
        invoices: list[tuple[str, bytes | str]],
        datev_config: DatevExportConfig | None = None,
        sap_config: SapS4HanaExportConfig | None = None,
    ) -> BatchIngestionSummary:
        """
        Processes a batch of e-invoices, performs automated EN 16931 and UStG auditing,
        maps accounts, and produces both DATEV Format 700 CSV and SAP S/4HANA JSON bridges.
        """
        datev_cfg = datev_config or DatevExportConfig()
        sap_cfg = sap_config or SapS4HanaExportConfig()

        batch_id = f"BATCH-{datetime.now(UTC).strftime('%Y%m%d%H%M%S')}-{uuid4().hex[:6]}"
        items: list[BatchInvoiceProcessingItem] = []
        datev_rows: list[DatevBookingRow] = []
        sap_entries: list[SapS4HanaJournalEntry] = []

        total_net = 0.0
        total_tax = 0.0
        total_grand = 0.0

        compliant_count = 0
        warning_count = 0
        rejected_count = 0

        for idx, (filename, raw_content) in enumerate(invoices, start=1):
            try:
                if isinstance(raw_content, bytes):
                    extraction = zugferd_extractor_service.extract_from_pdf_or_xml(
                        file_bytes=raw_content,
                        filename=filename,
                    )
                else:
                    extraction = zugferd_extractor_service.parse_xml_invoice(
                        raw_xml=raw_content,
                        filename=filename,
                    )

                ms = extraction.monetary_summation
                vr = extraction.validation_report
                vat = extraction.vat_audit
                lw = extraction.leitweg_validation

                # Determine compliance status
                is_en_ok = vr.is_en16931_compliant
                is_vat_ok = vat.is_ustg_compliant if vat else True
                is_lw_ok = True if (lw is None or lw.is_valid) else False

                if is_en_ok and is_vat_ok and is_lw_ok:
                    status = "COMPLIANT"
                    compliant_count += 1
                elif not is_en_ok or (vat and not vat.is_ustg_compliant and vat.tax_discrepancy_eur > 0.05):
                    status = "REJECTED"
                    rejected_count += 1
                else:
                    status = "WARNING"
                    warning_count += 1

                # ERP mapping
                kreditor = cls._assign_creditor_account(extraction, datev_cfg.kreditor_start_konto, idx)
                aufwand, bu_key, _ = cls._resolve_account_and_tax(extraction, datev_cfg.chart_of_accounts)

                datev_row = cls.create_datev_row(extraction, datev_cfg, kreditor)
                sap_entry = cls.create_sap_journal_entry(extraction, sap_cfg, kreditor)

                datev_rows.append(datev_row)
                sap_entries.append(sap_entry)

                total_net += ms.tax_basis_total_amount_eur
                total_tax += ms.tax_total_amount_eur
                total_grand += ms.grand_total_amount_eur

                items.append(
                    BatchInvoiceProcessingItem(
                        invoice_index=idx,
                        document_id=extraction.document_id,
                        filename=filename,
                        invoice_number=extraction.invoice_number,
                        issue_date=extraction.issue_date,
                        due_date=extraction.payment_due_date,
                        seller_name=extraction.seller.name,
                        seller_vat_id=extraction.seller.vat_id,
                        buyer_name=extraction.buyer.name,
                        profile=extraction.profile.value,
                        currency=extraction.currency_code,
                        net_amount_eur=ms.tax_basis_total_amount_eur,
                        tax_amount_eur=ms.tax_total_amount_eur,
                        grand_total_eur=ms.grand_total_amount_eur,
                        is_en16931_compliant=is_en_ok,
                        is_ustg_compliant=is_vat_ok,
                        leitweg_id=extraction.buyer_reference,
                        leitweg_valid=lw.is_valid if lw else None,
                        status=status,
                        kreditor_konto=kreditor,
                        aufwand_konto=aufwand,
                        bu_schluessel=bu_key,
                        datev_booking_row=datev_row,
                        sap_journal_entry=sap_entry,
                        validation_issues_count=len(vr.issues),
                        vat_findings_count=len(vat.findings) if vat else 0,
                    )
                )

            except Exception as e:
                # Corrupted invoice file handling in batch
                rejected_count += 1
                fallback_row = DatevBookingRow(
                    umsatz_eur=0.0,
                    soll_haben_kz="S",
                    waehrung="EUR",
                    konto="3400",
                    gegenkonto="70999",
                    bu_schluessel="",
                    belegdatum=datetime.now(UTC).strftime("%d%m"),
                    belegfeld_1="FEHLER",
                    belegfeld_2="",
                    buchungstext=f"PARSING_ERROR: {str(e)[:45]}",
                    beleglink=filename[:36],
                    festschreibung=0,
                )
                items.append(
                    BatchInvoiceProcessingItem(
                        invoice_index=idx,
                        document_id=UUID("00000000-0000-0000-0000-000000000000"),
                        filename=filename,
                        invoice_number=f"ERR-{idx}",
                        issue_date=None,
                        due_date=None,
                        seller_name="Unbekannter Lieferant (Parsingfehler)",
                        seller_vat_id=None,
                        buyer_name="Fehlerhaft",
                        profile="UNKNOWN",
                        currency="EUR",
                        net_amount_eur=0.0,
                        tax_amount_eur=0.0,
                        grand_total_eur=0.0,
                        is_en16931_compliant=False,
                        is_ustg_compliant=False,
                        leitweg_id=None,
                        leitweg_valid=False,
                        status="REJECTED",
                        kreditor_konto="70999",
                        aufwand_konto="3400",
                        bu_schluessel="",
                        datev_booking_row=fallback_row,
                        sap_journal_entry=SapS4HanaJournalEntry(
                            company_code=sap_cfg.company_code,
                            fiscal_year=sap_cfg.fiscal_year,
                            accounting_document_type="KR",
                            document_date=datetime.now(UTC).strftime("%Y-%m-%d"),
                            posting_date=datetime.now(UTC).strftime("%Y-%m-%d"),
                            document_reference_id="ERR",
                            document_header_text="PARSING_ERROR",
                            items=[],
                        ),
                        validation_issues_count=1,
                        vat_findings_count=1,
                    )
                )

        datev_csv = cls.generate_datev_csv(datev_rows, datev_cfg)
        sap_json = cls.generate_sap_json(sap_entries)

        return BatchIngestionSummary(
            batch_id=batch_id,
            processed_at=datetime.now(UTC),
            total_invoices_processed=len(invoices),
            compliant_invoices_count=compliant_count,
            warning_invoices_count=warning_count,
            rejected_invoices_count=rejected_count,
            total_net_amount_eur=round(total_net, 2),
            total_tax_amount_eur=round(total_tax, 2),
            total_grand_amount_eur=round(total_grand, 2),
            chart_of_accounts=datev_cfg.chart_of_accounts,
            items=items,
            datev_csv_content=datev_csv,
            sap_json_content=sap_json,
        )

    @classmethod
    def process_zip_archive(
        cls,
        zip_bytes: bytes,
        datev_config: DatevExportConfig | None = None,
        sap_config: SapS4HanaExportConfig | None = None,
    ) -> BatchIngestionSummary:
        """Unpacks a ZIP archive of hybrid PDFs or XML invoices and processes them in high-throughput batch mode."""
        invoices: list[tuple[str, bytes | str]] = []
        with zipfile.ZipFile(io.BytesIO(zip_bytes), "r") as z:
            for filename in z.namelist():
                lower = filename.lower()
                if lower.endswith(".xml") or lower.endswith(".pdf"):
                    content = z.read(filename)
                    invoices.append((filename, content))

        return cls.process_batch(invoices, datev_config=datev_config, sap_config=sap_config)


erp_export_bridge = ErpExportBridgeService()

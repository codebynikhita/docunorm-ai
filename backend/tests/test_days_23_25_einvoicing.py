from datetime import UTC, date, datetime
from uuid import uuid4

import pymupdf as fitz
from fastapi.testclient import TestClient

from app.main import app
from app.schemas.zugferd_invoice import (
    VatCategoryCode,
    ZugferdInvoiceExtraction,
    ZugferdInvoiceType,
    ZugferdLineItem,
    ZugferdMonetarySummation,
    ZugferdParty,
    ZugferdPostalAddress,
    ZugferdProfile,
    ZugferdTaxSubtotal,
    ZugferdValidationReport,
)
from app.services.leitweg_validator import leitweg_validator
from app.services.vat_auditor import vat_auditor
from app.services.zugferd_extractor import zugferd_extractor_service
from app.services.zugferd_pdf_exporter import generate_zugferd_reconciliation_pdf


def _build_extraction(
    *,
    buyer_ref: str = "991-12345-64",
    vat_cat: VatCategoryCode = VatCategoryCode.STANDARD,
    tax_rate: float = 19.0,
    net_amount: float = 1000.0,
    declared_tax: float = 190.0,
    seller_vat: str | None = "DE123456789",
    buyer_vat: str | None = "DE987654321",
    buyer_country: str = "DE",
    raw_xml: str = "<Invoice>sample</Invoice>",
) -> ZugferdInvoiceExtraction:
    line_item = ZugferdLineItem(
        line_id="1",
        item_name="Enterprise Compliance Audit",
        billed_quantity=1.0,
        unit_code="C62",
        net_price_eur=net_amount,
        line_total_eur=net_amount,
        vat_category_code=vat_cat,
        vat_rate_percent=tax_rate,
    )
    subtotal = ZugferdTaxSubtotal(
        tax_category_code=vat_cat,
        tax_rate_percent=tax_rate,
        taxable_amount_eur=net_amount,
        tax_amount_eur=declared_tax,
    )
    monetary = ZugferdMonetarySummation(
        line_total_amount_eur=net_amount,
        tax_basis_total_amount_eur=net_amount,
        tax_total_amount_eur=declared_tax,
        grand_total_amount_eur=round(net_amount + declared_tax, 2),
        due_payable_amount_eur=round(net_amount + declared_tax, 2),
    )
    val_report = ZugferdValidationReport(
        is_en16931_compliant=True,
        detected_profile=ZugferdProfile.XRECHNUNG,
        profile_urn="urn:cen.eu:en16931:2017#compliant#urn:xeinkauf.de:kosit:xrechnung_3.0",
        syntax_format="UN/CEFACT CII",
        has_math_discrepancy=False,
        issues=[],
        passed_rules_count=12,
        total_rules_evaluated=12,
        validation_summary_de="Konform.",
    )
    return ZugferdInvoiceExtraction(
        document_id=uuid4(),
        filename="rechnungspruefung.pdf",
        is_hybrid_pdf_a3=True,
        xml_filename="factur-x.xml",
        raw_xml_content=raw_xml,
        extracted_at=datetime.now(UTC),
        profile=ZugferdProfile.XRECHNUNG,
        profile_urn="urn:cen.eu:en16931:2017#compliant#urn:xeinkauf.de:kosit:xrechnung_3.0",
        invoice_number="RE-2026-2501",
        invoice_type_code=ZugferdInvoiceType.COMMERCIAL_INVOICE,
        invoice_type_name_de="Handelsrechnung",
        issue_date=date(2026, 11, 10),
        currency_code="EUR",
        seller=ZugferdParty(
            name="DocuNorm Sovereign GmbH",
            vat_id=seller_vat,
            postal_address=ZugferdPostalAddress(
                postcode="10117",
                city_name="Berlin",
                country_id="DE",
            ),
        ),
        buyer=ZugferdParty(
            name="Bundesamt für Bauwesen",
            vat_id=buyer_vat,
            postal_address=ZugferdPostalAddress(
                postcode="53179",
                city_name="Bonn",
                country_id=buyer_country,
            ),
        ),
        buyer_reference=buyer_ref,
        iban="DE89370400440532013000",
        line_items=[line_item],
        tax_subtotals=[subtotal],
        monetary_summation=monetary,
        validation_report=val_report,
        leitweg_validation=leitweg_validator.validate(buyer_ref),
    )


# ---------------------------------------------------------------------------
# DAY 23: Federal Leitweg-ID ISO 7064 MOD-97-10 Validator & Registry Tests
# ---------------------------------------------------------------------------


def test_leitweg_mod97_compute_and_validate_valid_federal_and_state():
    """Verifies ISO 7064 MOD-97-10 calculation and Bund/Länder jurisdiction lookup."""
    cd_bund = leitweg_validator.compute_check_digit("991", "123456")
    res_bund = leitweg_validator.validate(f"991-123456-{cd_bund}")
    assert res_bund.is_valid is True
    assert res_bund.format_valid is True
    assert res_bund.checksum_valid is True
    assert res_bund.federal_entity_type == "Bundesbehörde (ZRE)"
    assert "ZRE" in res_bund.submission_portal

    cd_alphanum = leitweg_validator.compute_check_digit("05111000", "AB12")
    res_nrw = leitweg_validator.validate(f"05111000-AB12-{cd_alphanum}")
    assert res_nrw.is_valid is True
    assert res_nrw.bundesland_or_authority == "Nordrhein-Westfalen"
    assert "NRW" in res_nrw.submission_portal


def test_leitweg_rejects_corrupted_checksum_and_bad_format():
    """Verifies MOD-97-10 catches single-digit typos and reports expected check digit."""
    expected_cd = leitweg_validator.compute_check_digit("04011000", "12345")
    assert expected_cd == "03"
    bad_cd = "99" if expected_cd != "99" else "00"

    res_bad = leitweg_validator.validate(f"04011000-12345-{bad_cd}")
    assert res_bad.is_valid is False
    assert res_bad.format_valid is True
    assert res_bad.checksum_valid is False
    assert res_bad.expected_check_digit == "03"
    assert len(res_bad.errors) >= 1

    res_malformed = leitweg_validator.validate("INVALID-ID")
    assert res_malformed.is_valid is False
    assert res_malformed.format_valid is False


def test_zugferd_extractor_enforces_br_de_15_on_invalid_leitweg_in_xml():
    """Ensures XRechnung XML parsing flags invalid Leitweg-ID checksums via BR-DE-15."""
    bad_xml = """<?xml version="1.0" encoding="UTF-8"?>
    <Invoice xmlns="urn:oasis:names:specification:ubl:schema:xsd:Invoice-2"
             xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"
             xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2">
        <cbc:CustomizationID>urn:cen.eu:en16931:2017#compliant#urn:xeinkauf.de:kosit:xrechnung_3.0</cbc:CustomizationID>
        <cbc:ID>XR-BAD-LW-01</cbc:ID>
        <cbc:IssueDate>2026-11-10</cbc:IssueDate>
        <cbc:InvoiceTypeCode>380</cbc:InvoiceTypeCode>
        <cbc:DocumentCurrencyCode>EUR</cbc:DocumentCurrencyCode>
        <cbc:BuyerReference>04011000-12345-99</cbc:BuyerReference>
        <cac:AccountingSupplierParty><cac:Party>
            <cac:PartyName><cbc:Name>Lieferant GmbH</cbc:Name></cac:PartyName>
            <cac:PostalAddress><cbc:CityName>Berlin</cbc:CityName><cbc:PostalZone>10115</cbc:PostalZone><cac:Country><cbc:IdentificationCode>DE</cbc:IdentificationCode></cac:Country></cac:PostalAddress>
            <cac:PartyTaxScheme><cbc:CompanyID>DE123456789</cbc:CompanyID></cac:PartyTaxScheme>
        </cac:Party></cac:AccountingSupplierParty>
        <cac:AccountingCustomerParty><cac:Party>
            <cac:PartyName><cbc:Name>Senat Bremen</cbc:Name></cac:PartyName>
            <cac:PostalAddress><cbc:CityName>Bremen</cbc:CityName><cbc:PostalZone>28195</cbc:PostalZone><cac:Country><cbc:IdentificationCode>DE</cbc:IdentificationCode></cac:Country></cac:PostalAddress>
        </cac:Party></cac:AccountingCustomerParty>
        <cac:TaxTotal><cbc:TaxAmount currencyID="EUR">190.00</cbc:TaxAmount></cac:TaxTotal>
        <cac:LegalMonetaryTotal><cbc:LineExtensionAmount currencyID="EUR">1000.00</cbc:LineExtensionAmount><cbc:TaxExclusiveAmount currencyID="EUR">1000.00</cbc:TaxExclusiveAmount><cbc:TaxInclusiveAmount currencyID="EUR">1190.00</cbc:TaxInclusiveAmount><cbc:PayableAmount currencyID="EUR">1190.00</cbc:PayableAmount></cac:LegalMonetaryTotal>
    </Invoice>
    """
    extraction = zugferd_extractor_service.parse_xml_invoice(bad_xml, filename="bad_lw.xml")
    assert extraction.leitweg_validation is not None
    assert extraction.leitweg_validation.is_valid is False
    assert extraction.validation_report.is_en16931_compliant is False
    assert any(issue.code == "BR-DE-15" for issue in extraction.validation_report.issues)


# ---------------------------------------------------------------------------
# DAY 24: § 14 UStG, Reverse Charge (§ 13b) & VAT Rate Discrepancy Tests
# ---------------------------------------------------------------------------


def test_vat_auditor_compliant_standard_and_small_value():
    """Standard 19% DE invoice passes 100%; <= 250 EUR invoice triggers § 33 UStDV relief."""
    cd = leitweg_validator.compute_check_digit("991", "12345")
    ext_std = _build_extraction(buyer_ref=f"991-12345-{cd}")
    report_std = vat_auditor.audit_invoice(ext_std)
    assert report_std.is_ustg_compliant is True
    assert report_std.tax_discrepancy_eur == 0.0
    assert report_std.mandatory_fields_score_percent == 100.0

    ext_small = _build_extraction(
        buyer_ref=f"991-12345-{cd}",
        net_amount=100.0,
        declared_tax=19.0,
        seller_vat=None,
    )
    report_small = vat_auditor.audit_invoice(ext_small)
    assert report_small.is_small_value_invoice is True
    assert report_small.is_ustg_compliant is True


def test_vat_auditor_catches_illegal_rate_and_arithmetic_mismatch():
    """Detects unlawful 15% domestic German VAT rate (§ 12 UStG) and sum mismatch."""
    cd = leitweg_validator.compute_check_digit("991", "12345")
    ext_bad = _build_extraction(
        buyer_ref=f"991-12345-{cd}",
        tax_rate=15.0,
        net_amount=1000.0,
        declared_tax=190.0,
    )
    report = vat_auditor.audit_invoice(ext_bad)
    assert report.is_ustg_compliant is False
    codes = {f.code for f in report.findings}
    assert "USTG-12-RATE" in codes
    assert "USTG-CALC-SUB" in codes
    assert "USTG-CALC-TOTAL" in codes


def test_vat_auditor_reverse_charge_13b_detection():
    """Catches Reverse-Charge AE with illegal positive VAT and missing § 14a Abs. 5 notice."""
    cd = leitweg_validator.compute_check_digit("991", "12345")
    ext_rc_bad = _build_extraction(
        buyer_ref=f"991-12345-{cd}",
        vat_cat=VatCategoryCode.REVERSE_CHARGE,
        tax_rate=19.0,
        net_amount=2000.0,
        declared_tax=380.0,
        raw_xml="<Invoice>No legal notice here</Invoice>",
    )
    report_bad = vat_auditor.audit_invoice(ext_rc_bad)
    assert report_bad.reverse_charge_detected is True
    assert report_bad.is_ustg_compliant is False
    codes = {f.code for f in report_bad.findings}
    assert "USTG-13B-TAX" in codes
    assert "USTG-14A-RC" in codes

    ext_rc_ok = _build_extraction(
        buyer_ref=f"991-12345-{cd}",
        vat_cat=VatCategoryCode.REVERSE_CHARGE,
        tax_rate=0.0,
        net_amount=2000.0,
        declared_tax=0.0,
        raw_xml="<Note>Steuerschuldnerschaft des Leistungsempfängers gem. § 13b UStG</Note>",
    )
    report_ok = vat_auditor.audit_invoice(ext_rc_ok)
    assert report_ok.reverse_charge_detected is True
    assert report_ok.is_ustg_compliant is True


def test_vat_auditor_intra_community_6a_requires_eu_buyer_vat():
    """Innergemeinschaftliche Lieferung (K) across EU requires valid foreign buyer VAT ID."""
    cd = leitweg_validator.compute_check_digit("991", "12345")
    ext_k_missing = _build_extraction(
        buyer_ref=f"991-12345-{cd}",
        vat_cat=VatCategoryCode.INTRA_COMMUNITY,
        tax_rate=0.0,
        net_amount=5000.0,
        declared_tax=0.0,
        buyer_vat=None,
        buyer_country="FR",
        raw_xml="<Note>Steuerfreie innergemeinschaftliche Lieferung § 6a UStG</Note>",
    )
    report = vat_auditor.audit_invoice(ext_k_missing)
    assert report.intra_community_supply_detected is True
    assert report.is_ustg_compliant is False


# ---------------------------------------------------------------------------
# DAY 25: 2-Page DIN 5008 / GoBD Reconciliation PDF & Endpoint Integration Tests
# ---------------------------------------------------------------------------


def test_zugferd_gobd_2page_pdf_export_and_sha256_seal(tmp_path):
    """Generates a 2-page DIN 5008 PDF certificate and verifies structure and SHA-256 seal."""
    cd = leitweg_validator.compute_check_digit("991", "12345")
    ext = _build_extraction(buyer_ref=f"991-12345-{cd}")
    ext.vat_audit = vat_auditor.audit_invoice(ext)

    pdf_path = generate_zugferd_reconciliation_pdf(ext, output_dir=tmp_path)
    assert pdf_path.exists()
    assert pdf_path.stat().st_size > 2000

    pdf_doc = fitz.open(str(pdf_path))
    assert len(pdf_doc) == 2
    p1_text = pdf_doc[0].get_text()
    p2_text = pdf_doc[1].get_text()
    pdf_doc.close()

    assert "PRÜFZERTIFIKAT E-RECHNUNG & GoBD" in p1_text
    assert f"991-12345-{cd}" in p1_text
    assert "SHA-256 Prüfsiegel" in p1_text
    assert "ABSCHNITT II" in p2_text
    assert "UMSATZSTEUERRECHTLICHE TIEFENPRÜFUNG" in p2_text
    assert "GoBD 10-JAHRES-ARCHIVIERUNGSFREIGABE" in p2_text


def test_days_23_to_25_rest_api_endpoints():
    """Tests Leitweg validation, § 14 UStG audit, and GoBD PDF streaming via FastAPI."""
    client = TestClient(app)

    # 1. Leitweg endpoint
    cd = leitweg_validator.compute_check_digit("08", "998877")
    r_lw = client.get(f"/api/v1/zugferd/validate-leitweg/08-998877-{cd}")
    assert r_lw.status_code == 200
    body_lw = r_lw.json()
    assert body_lw["is_valid"] is True
    assert body_lw["bundesland_or_authority"] == "Baden-Württemberg"

    # 2. Document extract includes leitweg_validation & vat_audit
    doc_id = uuid4()
    r_ext = client.get(f"/api/v1/documents/{doc_id}/zugferd-extract")
    assert r_ext.status_code == 200
    body_ext = r_ext.json()
    assert body_ext["leitweg_validation"]["is_valid"] is True
    assert body_ext["vat_audit"]["is_ustg_compliant"] is True

    # 3. Document VAT audit endpoint
    r_vat = client.post(f"/api/v1/documents/{doc_id}/vat-audit")
    assert r_vat.status_code == 200
    assert r_vat.json()["is_ustg_compliant"] is True

    # 4. Document 2-page GoBD PDF export endpoint
    r_pdf = client.get(f"/api/v1/documents/{doc_id}/export-zugferd-certificate-pdf")
    assert r_pdf.status_code == 200
    assert r_pdf.headers["content-type"] == "application/pdf"
    assert r_pdf.content.startswith(b"%PDF-")
    doc = fitz.open(stream=r_pdf.content, filetype="pdf")
    assert len(doc) == 2
    doc.close()

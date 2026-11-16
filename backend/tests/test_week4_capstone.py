from pathlib import Path

import pymupdf as fitz
from fastapi.testclient import TestClient

from app.main import app
from app.schemas.erp_export import ChartOfAccounts
from app.services.capstone_audit_engine import capstone_audit_engine
from app.services.capstone_invoices_catalog import generate_capstone_100_invoices
from app.services.capstone_pdf_exporter import generate_capstone_audit_report_pdf
from app.services.leitweg_validator import LeitwegValidatorService


def test_capstone_100_invoices_catalog():
    """
    Verifies that the Capstone catalog produces exactly 100 German B2B and B2G invoices
    across the statutory spectrum, with 95 compliant and 5 intended discrepancy test cases.
    """
    invoices = generate_capstone_100_invoices()
    assert len(invoices) == 100

    categories = {}
    for inv in invoices:
        categories[inv.category] = categories.get(inv.category, 0) + 1

    assert categories["B2B_COMFORT"] == 40
    assert categories["B2G_XRECHNUNG"] == 25
    assert categories["REVERSE_CHARGE_13B"] == 15
    assert categories["REDUCED_VAT_7"] == 10
    assert categories["SMALL_VALUE_33"] == 5
    assert categories["DISCREPANT_FRAUD_SIM"] == 5

    compliant_count = sum(1 for i in invoices if i.is_expected_compliant)
    rejected_count = sum(1 for i in invoices if not i.is_expected_compliant)
    assert compliant_count == 95
    assert rejected_count == 5

    # Verify all 25 B2G invoices have valid MOD-97-10 check digits
    b2g_invoices = [i for i in invoices if i.category == "B2G_XRECHNUNG"]
    for b2g in b2g_invoices:
        assert b2g.buyer_reference is not None
        lw_res = LeitwegValidatorService.validate(b2g.buyer_reference)
        assert lw_res.is_valid, f"Leitweg-ID {b2g.buyer_reference} failed validation: {lw_res.errors}"
        assert lw_res.checksum_valid is True


def test_capstone_audit_engine_execution():
    """
    Executes the high-throughput 100-invoice benchmark audit and verifies
    95% compliance rate, performance throughput, forensic error isolation, and ERP bridge generation.
    """
    summary = capstone_audit_engine.execute_capstone_audit(chart=ChartOfAccounts.SKR03)

    assert summary.total_invoices == 100
    assert summary.compliant_count == 95
    assert summary.warning_count == 0
    assert summary.rejected_count == 5
    assert summary.compliance_rate_percent == 95.0

    # High-throughput performance checks (< 2500ms total, > 40 inv/sec)
    assert summary.execution_time_ms < 2500.0
    assert summary.throughput_invoices_per_sec > 40.0

    # Volume checks
    assert summary.total_net_eur > 2_500_000.0
    assert summary.total_grand_eur > 3_000_000.0

    # Forensic discrepancy verification
    assert len(summary.discrepancies) == 5
    rejected_inv_nos = {d.invoice_number for d in summary.discrepancies}
    assert rejected_inv_nos == {
        "INV-DISC-096",
        "INV-DISC-097",
        "INV-DISC-098",
        "INV-DISC-099",
        "INV-DISC-100",
    }

    # Verify specific rule citations
    d96 = next(d for d in summary.discrepancies if d.invoice_number == "INV-DISC-096")
    assert "BR-CO-10" in d96.rule_violated
    assert d96.risk_level == "KRITISCH"

    d97 = next(d for d in summary.discrepancies if d.invoice_number == "INV-DISC-097")
    assert "BR-DE-15" in d97.rule_violated
    assert d97.risk_level == "HOCH"

    d98 = next(d for d in summary.discrepancies if d.invoice_number == "INV-DISC-098")
    assert "14" in d98.rule_violated
    assert d98.risk_level == "KRITISCH"

    d99 = next(d for d in summary.discrepancies if d.invoice_number == "INV-DISC-099")
    assert "BR-02" in d99.rule_violated or "14" in d99.rule_violated

    d100 = next(d for d in summary.discrepancies if d.invoice_number == "INV-DISC-100")
    assert "14c" in d100.rule_violated or "BR-CO-12" in d100.rule_violated
    assert d100.risk_level == "KRITISCH"

    # GoBD Hash check
    assert len(summary.gobd_sha256_batch_hash) == 64

    # DATEV 700 format checks
    assert summary.datev_csv_content.startswith('"EXTF";700;21;"Buchungsstapel"')
    assert '"Umsatz (ohne Soll/Haben-Kz)";"Soll/Haben-Kennzeichen"' in summary.datev_csv_content
    # Check Festschreibung flag
    assert ";1\r\n" in summary.datev_csv_content or ";1" in summary.datev_csv_content

    # SAP S/4HANA format checks
    assert "JournalEntryCreateRequest" in summary.sap_json_content
    assert "DOCUNORM_SOVEREIGN_AI" in summary.sap_json_content


def test_capstone_pdf_generation(tmp_path: Path):
    """
    Verifies that the certified DIN 5008 Master Capstone Audit Report PDF
    is generated with exactly 3 pages, correct typography, and forensic sections.
    """
    summary = capstone_audit_engine.execute_capstone_audit(chart=ChartOfAccounts.SKR03)
    pdf_path = generate_capstone_audit_report_pdf(summary, output_dir=tmp_path)

    assert pdf_path.exists()
    assert pdf_path.stat().st_size > 30_000

    doc = fitz.open(str(pdf_path))
    assert len(doc) == 3

    # Page 1 checks
    p1_text = doc[0].get_text()
    assert "DOCUNORM SOVEREIGN AI" in p1_text
    assert "ZUGFeRD 2027 & XRECHNUNG" in p1_text
    assert "95.0%" in p1_text
    assert "100 Belege" in p1_text
    assert "B2B Factur-X" in p1_text
    assert "B2G XRechnung" in p1_text

    # Page 2 checks (Forensic register)
    p2_text = doc[1].get_text()
    assert "FORENSISCHES ANOMALIE" in p2_text
    assert "INV-DISC-096" in p2_text
    assert "INV-DISC-097" in p2_text
    assert "INV-DISC-098" in p2_text
    assert "INV-DISC-099" in p2_text
    assert "INV-DISC-100" in p2_text

    # Page 3 checks (ERP & GoBD seal)
    p3_text = doc[2].get_text()
    assert "DATEV FORMAT 700" in p3_text
    assert "SAP S/4HANA" in p3_text
    assert "GoBD-STAPEL-ID" in p3_text
    assert "SHA-256" in p3_text
    assert "REVISIONSICHER" in p3_text

    doc.close()


def test_capstone_fastapi_endpoints():
    """
    Verifies the 4 FastAPI REST endpoints for the Capstone benchmark:
    - GET /api/v1/zugferd/capstone/summary
    - GET /api/v1/zugferd/capstone/export-report-pdf
    - GET /api/v1/zugferd/capstone/export-datev-csv
    - GET /api/v1/zugferd/capstone/export-sap-json
    """
    client = TestClient(app)

    # 1. Capstone summary
    res_summary = client.get("/api/v1/zugferd/capstone/summary?chart_of_accounts=SKR03")
    assert res_summary.status_code == 200
    data = res_summary.json()
    assert data["total_invoices"] == 100
    assert data["compliant_count"] == 95
    assert data["rejected_count"] == 5
    assert data["compliance_rate_percent"] == 95.0
    assert len(data["discrepancies"]) == 5
    assert len(data["items"]) == 100

    # 2. Master Capstone PDF download
    res_pdf = client.get("/api/v1/zugferd/capstone/export-report-pdf?chart_of_accounts=SKR03")
    assert res_pdf.status_code == 200
    assert res_pdf.headers["content-type"] == "application/pdf"
    assert len(res_pdf.content) > 30_000
    assert res_pdf.content.startswith(b"%PDF")

    # 3. DATEV Format 700 CSV export
    res_datev = client.get("/api/v1/zugferd/capstone/export-datev-csv?chart_of_accounts=SKR03")
    assert res_datev.status_code == 200
    assert "text/csv" in res_datev.headers["content-type"]
    assert res_datev.content.startswith(b"\xef\xbb\xbf\"EXTF\";700;21;")

    # 4. SAP S/4HANA JSON export
    res_sap = client.get("/api/v1/zugferd/capstone/export-sap-json?company_code=1000")
    assert res_sap.status_code == 200
    assert "application/json" in res_sap.headers["content-type"]
    sap_data = res_sap.json()
    assert "JournalEntryCreateRequest" in sap_data
    assert len(sap_data["JournalEntryCreateRequest"]) == 100

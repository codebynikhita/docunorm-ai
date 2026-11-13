import io
import json
import zipfile

from fastapi.testclient import TestClient

from app.main import app
from app.schemas.erp_export import (
    ChartOfAccounts,
    DatevExportConfig,
    SapS4HanaExportConfig,
)
from app.services.erp_export_bridge import erp_export_bridge
from app.services.zugferd_samples import (
    SAMPLE_DISCREPANT_TAMPERED,
    SAMPLE_FACTURX_COMFORT,
    SAMPLE_REVERSE_CHARGE,
    SAMPLE_XRECHNUNG_UBL,
)


def test_datev_format_700_export():
    """Verifies official DATEV Buchungsstapel Format 700 CSV generation."""
    invoices = [
        ("comfort.xml", SAMPLE_FACTURX_COMFORT),
        ("reverse_charge.xml", SAMPLE_REVERSE_CHARGE),
    ]

    # Test SKR03
    cfg_skr03 = DatevExportConfig(chart_of_accounts=ChartOfAccounts.SKR03, beraternummer=1234, mandantennummer=99999)
    summary_skr03 = erp_export_bridge.process_batch(invoices, datev_config=cfg_skr03)

    csv_skr03 = summary_skr03.datev_csv_content
    lines_skr03 = csv_skr03.strip().split("\r\n")

    # Header Row 1 checks
    assert lines_skr03[0].startswith('"EXTF";700;21;"Buchungsstapel";12;')
    assert ";1234;99999;" in lines_skr03[0]
    assert ';"EUR";' in lines_skr03[0]

    # Header Row 2 checks
    assert '"Umsatz (ohne Soll/Haben-Kz)";"Soll/Haben-Kennzeichen"' in lines_skr03[1]

    # Data Rows
    assert len(lines_skr03) >= 4  # 2 headers + 2 invoices
    row1 = lines_skr03[2]
    assert "38675,00" in row1  # German comma decimal
    assert '"3400"' in row1     # SKR03 Wareneingang 19%
    assert '"9"' in row1        # BU-Schlüssel 9 (19% Vorsteuer)
    assert ";1" in row1         # GoBD Festschreibung 1

    row2 = lines_skr03[3]
    assert "12500,00" in row2
    assert '"3120"' in row2     # SKR03 Reverse Charge § 13b
    assert '"19"' in row2       # BU-Schlüssel 19 (Reverse Charge)

    # Test SKR04
    cfg_skr04 = DatevExportConfig(chart_of_accounts=ChartOfAccounts.SKR04)
    summary_skr04 = erp_export_bridge.process_batch(invoices, datev_config=cfg_skr04)
    csv_skr04 = summary_skr04.datev_csv_content
    assert '"5400"' in csv_skr04  # SKR04 Wareneingang 19%
    assert '"5920"' in csv_skr04  # SKR04 § 13b


def test_sap_s4hana_journal_entry_json():
    """Verifies SAP S/4HANA Cloud Finance JournalEntry payload formatting."""
    invoices = [
        ("comfort.xml", SAMPLE_FACTURX_COMFORT),
        ("xrechnung.xml", SAMPLE_XRECHNUNG_UBL),
    ]

    cfg_sap = SapS4HanaExportConfig(company_code="DE01", fiscal_year=2026, cost_center="CC_PROD_99")
    summary = erp_export_bridge.process_batch(invoices, sap_config=cfg_sap)

    sap_json = summary.sap_json_content
    data = json.loads(sap_json)

    assert "MessageHeader" in data
    assert data["MessageHeader"]["SenderBusinessSystemID"] == "DOCUNORM_SOVEREIGN_AI"

    entries = data["JournalEntryCreateRequest"]
    assert len(entries) == 2

    e1 = entries[0]
    assert e1["company_code"] == "DE01"
    assert e1["accounting_document_type"] == "KR"
    assert e1["document_reference_id"] == "RE-2026-DE-84920"

    items = e1["items"]
    assert len(items) >= 2
    # Vendor line item (Credit H)
    assert items[0]["account_type"] == "K"
    assert items[0]["debit_credit_code"] == "H"
    assert items[0]["amount_eur"] == 38675.00

    # Expense line item (Debit S)
    assert items[1]["account_type"] == "S"
    assert items[1]["debit_credit_code"] == "S"
    assert items[1]["amount_eur"] == 32500.00
    assert items[1]["cost_center"] == "CC_PROD_99"


def test_batch_zip_ingestion_and_metrics():
    """Tests high-throughput batch ingestion from a ZIP archive of hybrid invoices."""
    zip_buf = io.BytesIO()
    with zipfile.ZipFile(zip_buf, "w") as z:
        z.writestr("inv1_comfort.xml", SAMPLE_FACTURX_COMFORT)
        z.writestr("inv2_xrechnung.xml", SAMPLE_XRECHNUNG_UBL)
        z.writestr("inv3_tampered.xml", SAMPLE_DISCREPANT_TAMPERED)

    zip_bytes = zip_buf.getvalue()

    summary = erp_export_bridge.process_zip_archive(zip_bytes)
    assert summary.total_invoices_processed == 3
    assert summary.compliant_invoices_count == 2
    assert summary.rejected_invoices_count == 1  # Tampered invoice rejected

    assert summary.total_net_amount_eur > 40000.0
    assert summary.total_tax_amount_eur > 6000.0
    assert summary.total_grand_amount_eur > 45000.0

    assert len(summary.items) == 3
    statuses = [item.status for item in summary.items]
    assert "COMPLIANT" in statuses
    assert "REJECTED" in statuses


def test_day_27_api_endpoints():
    """Verifies FastAPI REST endpoints for sample batch, ZIP upload, and DATEV/SAP downloads."""
    client = TestClient(app)

    # 1. Sample batch GET
    r_batch = client.get("/api/v1/zugferd/sample-batch?chart_of_accounts=SKR03")
    assert r_batch.status_code == 200
    b_data = r_batch.json()
    assert b_data["total_invoices_processed"] == 5
    assert len(b_data["items"]) == 5
    assert "EXTF" in b_data["datev_csv_content"]
    assert "JournalEntryCreateRequest" in b_data["sap_json_content"]

    # 2. DATEV CSV direct download stream
    r_datev = client.get("/api/v1/zugferd/export-datev-csv?chart_of_accounts=SKR03&mandantennummer=77777")
    assert r_datev.status_code == 200
    assert "text/csv" in r_datev.headers["content-type"]
    assert "attachment" in r_datev.headers["content-disposition"]
    assert r_datev.content.startswith(b"\xef\xbb\xbf")  # UTF-8 BOM
    assert b"77777" in r_datev.content

    # 3. SAP S/4HANA JSON direct download stream
    r_sap = client.get("/api/v1/zugferd/export-sap-json?company_code=DE99")
    assert r_sap.status_code == 200
    assert "application/json" in r_sap.headers["content-type"]
    assert b"DE99" in r_sap.content

    # 4. ZIP batch ingest POST endpoint
    zip_buf = io.BytesIO()
    with zipfile.ZipFile(zip_buf, "w") as z:
        z.writestr("test1.xml", SAMPLE_FACTURX_COMFORT)
    zip_buf.seek(0)

    r_upload = client.post(
        "/api/v1/zugferd/batch-ingest?chart_of_accounts=SKR04",
        files={"file": ("batch.zip", zip_buf.getvalue(), "application/zip")},
    )
    assert r_upload.status_code == 200
    up_data = r_upload.json()
    assert up_data["total_invoices_processed"] == 1
    assert up_data["chart_of_accounts"] == "SKR04"
    assert '"5400"' in up_data["datev_csv_content"]

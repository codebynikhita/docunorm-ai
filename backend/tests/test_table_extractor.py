from uuid import uuid4
import fitz
import pytest

from app.schemas.table import TableStructure, TableRegulatoryAnalysis
from app.services.table_extractor import TableExtractorService, to_csv_string, to_markdown_table


@pytest.fixture
def sample_sla_pdf(tmp_path):
    """Generates a PDF simulating a German enterprise SLA contract."""
    pdf_path = tmp_path / "Siemens_Master_IKT_Vertrag_2026.pdf"
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text(
        (50, 72),
        "ANLAGE 4: SLA-KATALOG A - VERFÜGBARKEITS- UND PÖNALSTAFFEL GEM. DORA ART. 30\n"
        "Siemens AG Infrastructure Services & Cloud Computing SLA.\n"
        "Verfügbarkeit 99,95 % Mindestanforderung im Jahresmittel gem. BaFin BAIT 8.1.\n"
        "Verzugsstrafe 0,2 % pro Werktag, Pönalendeckel 5 %.",
    )
    doc.save(str(pdf_path))
    doc.close()
    return pdf_path


@pytest.fixture
def sample_ielts_pdf(tmp_path):
    """Generates a PDF simulating an official IELTS academic scorecard."""
    pdf_path = tmp_path / "IELTS_Academic_Score_Report.pdf"
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text(
        (50, 72),
        "Test Report Form: 26IA515338GOWN008A\n"
        "Candidate Details: Nikhita Gowdara Prabhakara Reddy\n"
        "Listening: 7.5  Reading: 7.0  Writing: 6.0  Speaking: 6.5\n"
        "Overall Band Score: 7.0 (CEFR C1 Effective Operational Proficiency)\n"
        "Verification available online at ielts.org/verify.",
    )
    doc.save(str(pdf_path))
    doc.close()
    return pdf_path


def test_to_csv_and_markdown_helpers():
    headers = ["Col A", "Col B"]
    rows = [["Val 1", "Val 2"], ["Val 3", "Val 4"]]

    csv_res = to_csv_string(headers, rows)
    assert "Col A,Col B" in csv_res
    assert "Val 1,Val 2" in csv_res

    md_res = to_markdown_table(headers, rows)
    assert "| Col A | Col B |" in md_res
    assert "| --- | --- |" in md_res
    assert "| Val 1 | Val 2 |" in md_res


def test_extract_tables_sla_contract(sample_sla_pdf):
    doc_id = uuid4()
    response = TableExtractorService.extract_tables_from_pdf(
        document_id=doc_id,
        pdf_path=sample_sla_pdf,
        filename="Siemens_Master_IKT_Vertrag_2026.pdf",
    )

    assert response.document_id == doc_id
    assert response.total_tables >= 1

    sla_tbl = next((t for t in response.tables if t.table_type == "SLA_PENALTY_MATRIX"), None)
    assert sla_tbl is not None
    assert "SLA-Katalog" in sla_tbl.title
    assert sla_tbl.row_count >= 4
    assert sla_tbl.col_count >= 4
    assert len(sla_tbl.cells) > 0

    # Verify visual bounding box sanity [x0, y0, x1, y1]
    x0, y0, x1, y1 = sla_tbl.bounding_box
    assert x1 > x0
    assert y1 > y0

    # Verify Regulatory SLA Analysis
    assert sla_tbl.regulatory_analysis is not None
    assert sla_tbl.regulatory_analysis.compliance_status == "COMPLIANT"
    assert "99,95" in sla_tbl.regulatory_analysis.availability_target
    assert any("0,2 %" in p for p in sla_tbl.regulatory_analysis.penalty_scale_assessed)
    assert "DORA Art. 30" in sla_tbl.regulatory_analysis.dora_statutory_basis


def test_extract_tables_academic_ielts(sample_ielts_pdf):
    doc_id = uuid4()
    response = TableExtractorService.extract_tables_from_pdf(
        document_id=doc_id,
        pdf_path=sample_ielts_pdf,
        filename="IELTS_Academic_Score_Report.pdf",
    )

    assert response.total_tables >= 1
    score_tbl = next((t for t in response.tables if t.table_type == "ACADEMIC_SCORE_REPORT"), None)
    assert score_tbl is not None
    assert "IELTS" in score_tbl.title
    assert score_tbl.regulatory_analysis is not None
    assert "Band 7.0" in score_tbl.regulatory_analysis.availability_target
    assert "CEFR C1" in score_tbl.regulatory_analysis.sla_classification

    # Check cell structure
    header_cells = [c for c in score_tbl.cells if c.is_header]
    assert len(header_cells) == score_tbl.col_count


def test_extract_tables_missing_file():
    doc_id = uuid4()
    response = TableExtractorService.extract_tables_from_pdf(
        document_id=doc_id,
        pdf_path="/non/existent/path/document.pdf",
        filename="missing.pdf",
    )
    assert response.total_tables == 0
    assert len(response.tables) == 0


@pytest.mark.asyncio
async def test_get_tables_endpoint_not_found():
    from unittest.mock import AsyncMock
    from httpx import ASGITransport, AsyncClient
    from app.main import app
    from app.core.db import get_session

    mock_session = AsyncMock()
    mock_session.get.return_value = None

    async def override_get_session():
        yield mock_session

    app.dependency_overrides[get_session] = override_get_session
    try:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            fake_id = uuid4()
            res = await client.get(f"/api/v1/documents/{fake_id}/tables")
            assert res.status_code == 404
            assert "Document not found" in res.json()["detail"]
    finally:
        app.dependency_overrides.pop(get_session, None)


def test_calculate_sla_penalty_engine():
    from app.schemas.table import SlaPenaltyCalculationRequest

    doc_id = uuid4()
    req = SlaPenaltyCalculationRequest(
        document_id=doc_id,
        table_id="tbl-p1-sla",
        annual_order_value_eur=582000.0,
        actual_downtime_hours=6.5,
        sla_tier="Tier-3 Platin",
    )
    res = TableExtractorService.calculate_sla_penalty(req)
    assert res.document_id == doc_id
    assert res.tolerated_downtime_hours == 4.38
    assert res.excess_downtime_hours > 0
    assert res.penalty_rate_percentage > 0
    assert res.final_enforceable_penalty_eur > 0
    assert "DORA Art. 30" in res.statutory_citation
    assert res.dora_compliance_status == "PARTIALLY_COMPLIANT"
    assert res.termination_right_triggered is False




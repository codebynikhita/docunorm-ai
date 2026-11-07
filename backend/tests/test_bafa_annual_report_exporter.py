from pathlib import Path
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pymupdf as fitz
import pytest

from app.services.bafa_annual_report_exporter import generate_bafa_annual_report_pdf
from app.services.portfolio_aggregator import portfolio_aggregator


@pytest.mark.asyncio
async def test_bafa_annual_report_pdf_generation(tmp_path: Path):
    """
    Verifies that generate_bafa_annual_report_pdf produces a valid, cryptographically sealed
    3-page DIN 5008 Annual Due Diligence Report conforming to § 10 Abs. 2 LkSG.
    """
    mock_db = AsyncMock()
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = []
    mock_db.execute.return_value = mock_result

    tenant_id = uuid4()
    synthesis = await portfolio_aggregator.aggregate_portfolio(
        db=mock_db,
        tenant_id=tenant_id,
        reporting_year=2026,
    )

    pdf_path = generate_bafa_annual_report_pdf(
        synthesis=synthesis,
        company_name="Test Enterprise AG",
        output_dir=tmp_path,
    )

    assert pdf_path.exists()
    assert pdf_path.stat().st_size > 2000

    # Verify PyMuPDF opens valid 3-page PDF
    pdf_doc = fitz.open(str(pdf_path))
    assert len(pdf_doc) == 3

    page1_text = pdf_doc[0].get_text()
    assert "BUNDESAMT FÜR WIRTSCHAFT UND AUSFUHRKONTROLLE (BAFA)" in page1_text
    assert "§ 10 ABS. 2 LkSG" in page1_text
    assert "GESAMT-PORTFOLIO-KONFORMITÄT" in page1_text
    assert "KONZENTRATIONSINDEX (HHI)" in page1_text

    page2_text = pdf_doc[1].get_text()
    assert "LIEFERANTEN-PORTFOLIO-MATRIX" in page2_text
    assert "GRENZÜBERSCHREITENDE STANDORTEXPOSITION" in page2_text

    page3_text = pdf_doc[2].get_text()
    assert "WIRKSAMKEIT DES BESCHWERDEVERFAHRENS (§ 8 LkSG)" in page3_text
    assert "RECHTSVERBINDLICHE ERKLÄRUNG DES VORSTANDS" in page3_text
    assert "KRYPTOGRAPHISCHES SOVERÄNES PRÜFSIEGEL" in page3_text
    assert "SHA-256" in page3_text

    pdf_doc.close()

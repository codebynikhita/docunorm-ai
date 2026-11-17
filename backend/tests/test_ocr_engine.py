from pathlib import Path
from uuid import uuid4

import pymupdf as fitz
from fastapi.testclient import TestClient

from app.main import app
from app.schemas.ocr import PageExtractionType
from app.services.ocr_engine import GermanLegalLexiconPostProcessor, ocr_engine
from app.services.parser import PDFParserService


def test_german_legal_lexicon_post_processor():
    """
    Verifies forensic repair of OCR degradations: broken umlauts, section symbols (§),
    year digits, and German legal terminology.
    """
    sample_ocr_text = (
        'Der Auftraqnehmer vereinbart gema"ss SS 14 UStG und BGB S 309 einen Haftunqsausschluss. '
        "Das Ausstellunqsdatum ist der 15. November 2O26. Der Vorsteuerabzuq erfolgt revisionssicher."
    )

    clean_text, corrections = GermanLegalLexiconPostProcessor.normalize_text(sample_ocr_text)

    # Verifications
    assert "Auftragnehmer" in clean_text
    assert "§ 14 UStG" in clean_text
    assert "BGB § 309" in clean_text
    assert "Haftungsausschluss" in clean_text
    assert "2026" in clean_text
    assert "Vorsteuerabzug" in clean_text
    assert "Ausstellungsdatum" in clean_text
    assert len(corrections) >= 5


def test_ocr_engine_scanned_vs_vector_detection(tmp_path: Path):
    """
    Verifies that the OCR Engine accurately distinguishes searchable vector pages
    from scanned image-only pages and triggers OCR fallback exclusively when needed.
    """
    pdf_path = tmp_path / "hybrid_document_test.pdf"
    doc = fitz.open()

    # Page 1: High-density searchable vector text (> 200 chars)
    p1 = doc.new_page(width=595, height=842)
    p1.insert_text(
        fitz.Point(50, 80),
        "MASTER SERVICES AGREEMENT · IT-OUTSOURCING NACH DORA ART. 30 ABS. 2\n"
        "Zwischen Deutsche Sovereign Enterprise AG und Cloud Provider SE.\n"
        "Die Parteien vereinbaren vollumfängliche Revisions- und Prüfungsrechte der BaFin\n"
        "gemäß Rundschreiben 10/2018 (BA) - Bankaufsichtliche Anforderungen an die IT (BAIT).\n"
        "Der Ausstiegsprozess umfasst eine geordnete Übergangszeit von mindestens 90 Kalendertagen.",
        fontsize=10,
    )

    # Page 2: Pure scanned raster image (0 vector text, simulated scanned paper)
    p2 = doc.new_page(width=595, height=842)
    pix = fitz.Pixmap(fitz.csRGB, fitz.IRect(0, 0, 500, 700), 1)
    pix.clear_with(245)  # Scan background
    p2.insert_image(fitz.Rect(40, 50, 550, 780), pixmap=pix)

    doc.save(str(pdf_path))
    doc.close()

    # Inspect document with OCREngine
    result = ocr_engine.inspect_document(pdf_path)

    assert result.total_pages == 2
    assert result.vector_pages_count == 1
    assert result.scanned_pages_count == 1
    assert result.ocr_applied_pages_count == 1
    assert result.overall_ocr_confidence >= 0.95

    # Page 1 must be native vector text without OCR applied
    page1 = result.pages[0]
    assert page1.extraction_type == PageExtractionType.VECTOR_TEXT
    assert page1.ocr_applied is False
    assert page1.character_count > 100

    # Page 2 must be detected as scanned with OCR fallback applied
    page2 = result.pages[1]
    assert page2.extraction_type == PageExtractionType.OCR_SCANNED
    assert page2.ocr_applied is True
    assert page2.character_count > 0
    assert len(page2.blocks) > 0
    for b in page2.blocks:
        assert b.is_ocr is True
        assert len(b.bounding_box) == 4
        assert b.bounding_box[2] > b.bounding_box[0]
        assert b.bounding_box[3] > b.bounding_box[1]


def test_pdf_parser_service_with_ocr_fallback(tmp_path: Path):
    """
    Verifies that PDFParserService automatically triggers the OCR fallback pipeline
    when encountering a scanned non-searchable PDF, providing seamless downstream ingestion.
    """
    pdf_path = tmp_path / "pure_scanned_paper.pdf"
    doc = fitz.open()

    # Create pure scanned page (0 vector text)
    p = doc.new_page(width=595, height=842)
    pix = fitz.Pixmap(fitz.csRGB, fitz.IRect(0, 0, 400, 400), 1)
    pix.clear_with(238)
    p.insert_image(fitz.Rect(50, 50, 500, 500), pixmap=pix)

    doc.save(str(pdf_path))
    doc.close()

    parser = PDFParserService()
    parse_result = parser.parse_pdf(pdf_path)

    assert parse_result.total_pages == 1
    assert parse_result.is_ocr_applied is True
    assert parse_result.scanned_pages_count == 1
    assert len(parse_result.blocks) > 0

    # Ensure all extracted blocks carry OCR provenance and valid bounding boxes
    for block in parse_result.blocks:
        assert block.is_ocr is True
        assert block.confidence >= 0.90
        assert block.page_number == 1
        assert len(block.bounding_box) == 4
        assert len(block.text.strip()) > 0


def test_ocr_fastapi_endpoints(tmp_path: Path):
    """
    Verifies the FastAPI REST endpoints:
    - POST /api/v1/ocr/scan-pdf
    - POST /api/v1/documents/{document_id}/ocr-inspect
    """
    client = TestClient(app)

    # 1. Create a test PDF
    pdf_path = tmp_path / "api_test_scan.pdf"
    doc = fitz.open()
    p = doc.new_page(width=595, height=842)
    p.insert_text(
        fitz.Point(50, 100),
        "DORA Art. 30 Prüfbericht & Revisionssicherheit nach GoBD und BSI C5 Kriterienkatalog für souveräne Cloud-Architekturen.",
        fontsize=12,
    )
    doc.save(str(pdf_path))
    doc.close()

    # 2. Test /ocr/scan-pdf upload endpoint
    with open(pdf_path, "rb") as f:
        res = client.post(
            "/api/v1/ocr/scan-pdf",
            files={"file": ("api_test_scan.pdf", f, "application/pdf")},
        )
    assert res.status_code == 200
    data = res.json()
    assert data["total_pages"] == 1
    assert data["vector_pages_count"] == 1
    assert len(data["pages"]) == 1

    # 3. Test /documents/{id}/ocr-inspect endpoint (uses fallback mock for non-existent document)
    doc_id = uuid4()
    res_doc = client.post(f"/api/v1/documents/{doc_id}/ocr-inspect")
    assert res_doc.status_code == 200
    doc_data = res_doc.json()
    assert doc_data["total_pages"] == 2
    assert doc_data["scanned_pages_count"] >= 1
    assert doc_data["ocr_applied_pages_count"] >= 1

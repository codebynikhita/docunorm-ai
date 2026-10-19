from pathlib import Path

import fitz  # PyMuPDF
import pytest

from app.services.parser import PDFParserService


@pytest.fixture
def sample_pdf_file(tmp_path: Path) -> Path:
    """
    Creates a temporary 2-page test PDF with structured headings and paragraphs.
    """
    pdf_path = tmp_path / "sample_contract.pdf"
    doc = fitz.open()

    # Page 1
    page1 = doc.new_page(width=595, height=842)  # Standard A4 dimensions
    page1.insert_text(
        (50, 72), "1. MASTER SUPPLY AGREEMENT", fontsize=16, fontname="helv"
    )
    page1.insert_text(
        (50, 120),
        "This agreement is made between Siemens AG and Supplier GmbH.",
        fontsize=11,
        fontname="helv",
    )

    # Page 2
    page2 = doc.new_page(width=595, height=842)
    page2.insert_text(
        (50, 72), "2. PENALTY AND DEFAULT CLAUSES", fontsize=16, fontname="helv"
    )
    page2.insert_text(
        (50, 120),
        "Late deliveries incur a penalty fee of 0.5% per calendar week.",
        fontsize=11,
        fontname="helv",
    )

    doc.save(str(pdf_path))
    doc.close()
    return pdf_path


def test_pdf_parser_extracts_pages_and_blocks(sample_pdf_file: Path) -> None:
    """
    Verifies that the PDFParserService correctly parses pages, extracts text,
    and captures exact bounding-box coordinates for each text block.
    """
    parser = PDFParserService()
    result = parser.parse_pdf(sample_pdf_file)

    # Check total pages
    assert result.total_pages == 2
    assert len(result.blocks) >= 4

    # Verify Page 1 content
    page1_blocks = [b for b in result.blocks if b.page_number == 1]
    assert any("MASTER SUPPLY AGREEMENT" in b.text for b in page1_blocks)

    # Verify Page 2 content
    page2_blocks = [b for b in result.blocks if b.page_number == 2]
    penalty_block = next(b for b in page2_blocks if "0.5% per calendar week" in b.text)
    assert penalty_block is not None

    # Verify Bounding Box coordinates [x0, y0, x1, y1]
    bbox = penalty_block.bounding_box
    assert len(bbox) == 4
    # All coordinates must be valid numbers (within A4 page width 595 and height 842)
    assert 0 <= bbox[0] < bbox[2] <= 595
    assert 0 <= bbox[1] < bbox[3] <= 842


def test_pdf_parser_handles_non_existent_file(tmp_path: Path) -> None:
    """
    Verifies that passing a missing file path raises a FileNotFoundError.
    """
    parser = PDFParserService()
    missing_file = tmp_path / "does_not_exist.pdf"
    with pytest.raises(FileNotFoundError):
        parser.parse_pdf(missing_file)

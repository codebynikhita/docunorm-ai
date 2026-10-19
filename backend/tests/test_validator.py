import pytest

from app.services.validator import validate_pdf_metadata


def test_valid_pdf_passes():
    """Valid PDF under 50MB should return True."""
    assert validate_pdf_metadata("contract.pdf", 1024) is True
    assert validate_pdf_metadata("INVOICE.PDF", 5000) is True


def test_rejects_non_pdf():
    """Non-PDF files must raise ValueError with expected message."""
    with pytest.raises(ValueError, match="Only PDF files are supported."):
        validate_pdf_metadata("malware.exe", 1024)
    with pytest.raises(ValueError, match="Only PDF files are supported."):
        validate_pdf_metadata("report.docx", 2048)


def test_rejects_empty_file():
    """Zero or negative byte files must raise ValueError."""
    with pytest.raises(ValueError, match="File cannot be empty."):
        validate_pdf_metadata("empty.pdf", 0)
    with pytest.raises(ValueError, match="File cannot be empty."):
        validate_pdf_metadata("corrupt.pdf", -5)


def test_rejects_oversized_file():
    """Files over 50MB must raise ValueError."""
    over_limit = 50 * 1024 * 1024 + 1
    with pytest.raises(ValueError, match="File exceeds maximum allowed size of 50 MB."):
        validate_pdf_metadata("giant_document.pdf", over_limit)

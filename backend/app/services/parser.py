from dataclasses import dataclass
from pathlib import Path

import pymupdf as fitz

from app.services.ocr_engine import ocr_engine


@dataclass
class ParsedBlock:
    """
    Represents an atomic text paragraph with its page and visual coordinates.
    """

    text: str
    page_number: int
    bounding_box: list[float]
    block_index: int
    is_ocr: bool = False
    confidence: float = 1.0


@dataclass
class ParseResult:
    """
    Aggregated document extraction output containing all blocks, page count, and OCR metadata.
    """

    total_pages: int
    blocks: list[ParsedBlock]
    is_ocr_applied: bool = False
    scanned_pages_count: int = 0
    ocr_confidence: float = 1.0


class PDFParserService:
    """
    Structural PDF extraction service capturing text and bounding boxes.
    Features automated Heavy OCR Fallback for scanned non-searchable pages.
    """

    MIN_PAGE_CHARS_FOR_VECTOR = 50

    def parse_pdf(self, file_path: Path, force_ocr: bool = False) -> ParseResult:
        if not file_path.exists():
            raise FileNotFoundError(f"PDF file not found at: {file_path}")

        doc = fitz.open(str(file_path))
        try:
            if doc.is_encrypted and not doc.authenticate(""):
                raise ValueError("Password-protected or encrypted PDF documents are not supported.")

            total_pages = len(doc)
            parsed_blocks: list[ParsedBlock] = []
            scanned_pages = 0
            ocr_applied = False
            page_confidences: list[float] = []

            # Iterate over each page in the PDF (0-indexed)
            for page_idx in range(total_pages):
                page = doc[page_idx]
                page_number = page_idx + 1

                # Extract visual vector blocks: (x0, y0, x1, y1, text, block_no, block_type)
                raw_blocks = page.get_text("blocks")
                page_text = " ".join(b[4].strip() for b in raw_blocks if b[4].strip())
                char_count = len(page_text)

                # Check if page is non-searchable or low density requiring OCR Fallback
                if force_ocr or char_count < self.MIN_PAGE_CHARS_FOR_VECTOR:
                    ocr_applied = True
                    scanned_pages += 1
                    ocr_res = ocr_engine.inspect_and_extract_page(
                        page=page,
                        page_number=page_number,
                        force_ocr=True,
                    )
                    page_confidences.append(ocr_res.confidence)

                    for b in ocr_res.blocks:
                        parsed_blocks.append(
                            ParsedBlock(
                                text=b.text,
                                page_number=page_number,
                                bounding_box=b.bounding_box,
                                block_index=b.block_index,
                                is_ocr=True,
                                confidence=b.confidence,
                            )
                        )
                else:
                    page_confidences.append(1.0)
                    for b_idx, block in enumerate(raw_blocks):
                        content = block[4].strip()
                        if not content:
                            continue

                        bbox = [round(float(coord), 2) for coord in block[0:4]]
                        parsed_blocks.append(
                            ParsedBlock(
                                text=content,
                                page_number=page_number,
                                bounding_box=bbox,
                                block_index=b_idx,
                                is_ocr=False,
                                confidence=1.0,
                            )
                        )

            avg_conf = (
                round(sum(page_confidences) / len(page_confidences), 3)
                if page_confidences
                else 1.0
            )

            return ParseResult(
                total_pages=total_pages,
                blocks=parsed_blocks,
                is_ocr_applied=ocr_applied,
                scanned_pages_count=scanned_pages,
                ocr_confidence=avg_conf,
            )
        finally:
            doc.close()

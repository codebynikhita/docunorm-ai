from dataclasses import dataclass
from pathlib import Path

import fitz  # PyMuPDF


@dataclass
class ParsedBlock:
    """
    Represents an atomic text paragraph with its page and visual coordinates.
    """

    text: str
    page_number: int
    bounding_box: list[float]
    block_index: int


@dataclass
class ParseResult:
    """
    Aggregated document extraction output containing all blocks and page count.
    """

    total_pages: int
    blocks: list[ParsedBlock]


class PDFParserService:
    """
    Structural PDF extraction service capturing text and bounding boxes.
    """

    def parse_pdf(self, file_path: Path) -> ParseResult:
        if not file_path.exists():
            raise FileNotFoundError(f"PDF file not found at: {file_path}")

        doc = fitz.open(str(file_path))
        total_pages = len(doc)
        parsed_blocks: list[ParsedBlock] = []

        # Iterate over each page in the PDF (0-indexed)
        for page_idx in range(total_pages):
            page = doc[page_idx]
            page_number = page_idx + 1  # Humans count pages starting at 1

            # Extract visual blocks: (x0, y0, x1, y1, text, block_no, block_type)
            raw_blocks = page.get_text("blocks")

            for b_idx, block in enumerate(raw_blocks):
                # block[4] contains the extracted text
                content = block[4].strip()
                if not content:
                    continue  # Skip empty whitespace blocks

                # block[0:4] are the visual bounding box coordinates (x0, y0, x1, y1)
                bbox = [round(float(coord), 2) for coord in block[0:4]]

                parsed_blocks.append(
                    ParsedBlock(
                        text=content,
                        page_number=page_number,
                        bounding_box=bbox,
                        block_index=b_idx,
                    )
                )

        doc.close()
        return ParseResult(total_pages=total_pages, blocks=parsed_blocks)

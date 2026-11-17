from enum import StrEnum
from uuid import UUID

from pydantic import BaseModel, Field


class PageExtractionType(StrEnum):
    VECTOR_TEXT = "VECTOR_TEXT"        # Native searchable text layer embedded in PDF
    OCR_SCANNED = "OCR_SCANNED"        # Pure raster image page requiring full OCR fallback
    HYBRID = "HYBRID"                  # Partial text with low density requiring OCR augmentation


class OCRBlockDetail(BaseModel):
    block_index: int
    text: str
    bounding_box: list[float] = Field(..., description="[x0, y0, x1, y1] coordinates in PDF points (72 DPI)")
    confidence: float = Field(default=0.95, ge=0.0, le=1.0)
    line_count: int = 1
    is_ocr: bool = False
    lexicon_corrections: list[str] = Field(default_factory=list)


class PageOCROutput(BaseModel):
    page_number: int
    page_width: float
    page_height: float
    extraction_type: PageExtractionType
    character_count: int
    raster_images_count: int
    ocr_applied: bool
    ocr_engine: str = "PyMuPDF_Sovereign_OCR"
    confidence: float = 1.0
    blocks: list[OCRBlockDetail] = Field(default_factory=list)


class DocumentOCRInspectionResult(BaseModel):
    document_id: UUID | None = None
    filename: str
    total_pages: int
    vector_pages_count: int
    scanned_pages_count: int
    ocr_applied_pages_count: int
    overall_ocr_confidence: float
    german_lexicon_corrections_count: int
    execution_time_ms: float
    pages: list[PageOCROutput] = Field(default_factory=list)

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.models.document import DocumentStatus


class DocumentRead(BaseModel):
    """
    Public representation of a Document entity returned to clients.
    """

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    tenant_id: UUID
    uploaded_by: UUID
    filename: str
    file_size_bytes: int
    mime_type: str
    sha256_hash: str
    status: DocumentStatus
    total_pages: int | None = None
    created_at: datetime


class DocumentUploadResponse(BaseModel):
    """
    Response schema for document upload operations with deduplication indicators.
    """

    message: str
    is_duplicate: bool
    document: DocumentRead


class SearchQuery(BaseModel):
    """
    Inbound search query payload for hybrid and semantic vector retrieval.
    """

    query: str
    limit: int = 5


class SearchResultChunk(BaseModel):
    """
    Individual retrieved document chunk with relevance score and bounding-box coordinates.
    """

    chunk_id: UUID
    document_id: UUID
    page_number: int
    bounding_box: list[float] | None = None
    content: str
    similarity_score: float


class SearchResponse(BaseModel):
    """
    Complete response containing ranked search results and query metadata.
    """

    query: str
    document_id: UUID
    total_results: int
    results: list[SearchResultChunk]

class AuditHistoryItem(BaseModel):
    """
    Individual message turn in a multi-turn compliance conversation.
    """
    role: str = "user"  # "user" or "auditor" / "assistant"
    text: str = ""


class AuditRequest(BaseModel):
    """
    Inbound request for auditing a document against European regulations.
    Supports multi-turn conversational follow-up inquiries.
    """
    query: str
    framework: str = "DORA"  # DORA, LkSG, ZUGFeRD
    lang: str = "DE"  # DE or EN
    history: list[AuditHistoryItem] | None = None


class AuditCitation(BaseModel):
    """
    Individual cited source with page number and visual bounding box.
    """
    source_tag: str
    chunk_id: str | None = None
    page_number: int
    bounding_box: list[float] | None = None
    content: str | None = None


class AuditResponse(BaseModel):
    """
    Grounded regulatory audit finding returned to the enterprise workbench.
    """
    document_id: UUID
    query: str
    framework: str
    status: str  # "COMPLIANT", "FLAGGED", "INCONCLUSIVE"
    finding_summary: str
    citations: list[AuditCitation]

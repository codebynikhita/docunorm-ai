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

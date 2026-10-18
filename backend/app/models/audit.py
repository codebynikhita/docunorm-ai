from datetime import UTC, datetime
from typing import Any
from uuid import UUID, uuid4

from sqlalchemy import JSON, Column
from sqlmodel import Field, SQLModel


class AuditLog(SQLModel, table=True):
    """
    Immutable compliance audit trail required by GDPR (Art. 30) and EU AI Act (Art. 12).
    Records every document inspection, PII neutralization event, and LLM inference request.
    """

    __tablename__ = "audit_logs"

    id: UUID = Field(
        default_factory=uuid4,
        primary_key=True,
        index=True,
        nullable=False,
    )
    tenant_id: UUID = Field(
        foreign_key="tenants.id",
        index=True,
        nullable=False,
    )
    user_id: UUID | None = Field(
        default=None,
        foreign_key="users.id",
        index=True,
        nullable=True,
    )
    action: str = Field(
        index=True,
        max_length=100,
        nullable=False,
        description="Action type: e.g. DOCUMENT_INGEST, PII_REDACT, VECTOR_SEARCH, AUDIT_QUERY",
    )
    resource_type: str = Field(
        max_length=50,
        nullable=False,
        description="Target resource: DOCUMENT, CHUNK, CONVERSATION, TENANT",
    )
    resource_id: str | None = Field(
        default=None,
        max_length=100,
        nullable=True,
    )
    details: dict[str, Any] | None = Field(
        default=None,
        sa_column=Column(JSON, nullable=True),
        description="Structured forensic metadata (e.g. types of PII masked, search scores)",
    )
    ip_address: str | None = Field(
        default=None,
        max_length=45,
        nullable=True,
    )
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        index=True,
        nullable=False,
    )

from datetime import UTC, datetime
from uuid import UUID, uuid4

from sqlmodel import Field, SQLModel


class Tenant(SQLModel, table=True):
    """
    Enterprise Tenant entity representing a client company (e.g. Siemens, SAP, BMW).
    Enforces strict multi-tenant data isolation required by GDPR.
    """

    __tablename__ = "tenants"

    id: UUID = Field(
        default_factory=uuid4,
        primary_key=True,
        index=True,
        nullable=False,
    )
    name: str = Field(index=True, max_length=255, nullable=False)
    slug: str = Field(unique=True, index=True, max_length=100, nullable=False)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        nullable=False,
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        nullable=False,
    )

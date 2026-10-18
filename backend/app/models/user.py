from datetime import UTC, datetime
from enum import StrEnum
from uuid import UUID, uuid4

from sqlmodel import Field, SQLModel


class UserRole(StrEnum):
    """
    Role-Based Access Control (RBAC) tiers for enterprise compliance auditing.
    """

    ADMIN = "admin"
    AUDITOR = "auditor"
    VIEWER = "viewer"


class User(SQLModel, table=True):
    """
    User entity bound to a specific enterprise Tenant with RBAC enforcement.
    """

    __tablename__ = "users"

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
    email: str = Field(unique=True, index=True, max_length=255, nullable=False)
    full_name: str = Field(max_length=255, nullable=False)
    hashed_password: str = Field(nullable=False)
    role: UserRole = Field(default=UserRole.AUDITOR, nullable=False)
    is_active: bool = Field(default=True, nullable=False)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        nullable=False,
    )

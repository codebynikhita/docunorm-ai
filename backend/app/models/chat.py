from datetime import UTC, datetime
from uuid import UUID, uuid4

from sqlalchemy import Column, Text
from sqlmodel import Field, SQLModel


class Conversation(SQLModel, table=True):
    """
    An audit investigation session conducted by an enterprise user over documents.
    """

    __tablename__ = "conversations"

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
    user_id: UUID = Field(
        foreign_key="users.id",
        index=True,
        nullable=False,
    )
    title: str = Field(default="New Audit Session", max_length=255, nullable=False)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        nullable=False,
    )


class Message(SQLModel, table=True):
    """
    A single conversational turn (user inquiry or AI audit conclusion).
    """

    __tablename__ = "messages"

    id: UUID = Field(
        default_factory=uuid4,
        primary_key=True,
        index=True,
        nullable=False,
    )
    conversation_id: UUID = Field(
        foreign_key="conversations.id",
        index=True,
        nullable=False,
    )
    role: str = Field(max_length=20, nullable=False)  # "user" or "assistant"
    content: str = Field(sa_column=Column(Text, nullable=False))
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        nullable=False,
    )


class Citation(SQLModel, table=True):
    """
    Exact mathematical and visual attribution link connecting an AI statement
    to a specific document chunk and its bounding box on a specific page.
    """

    __tablename__ = "citations"

    id: UUID = Field(
        default_factory=uuid4,
        primary_key=True,
        index=True,
        nullable=False,
    )
    message_id: UUID = Field(
        foreign_key="messages.id",
        index=True,
        nullable=False,
    )
    chunk_id: UUID = Field(
        foreign_key="document_chunks.id",
        index=True,
        nullable=False,
    )
    confidence_score: float = Field(
        nullable=False,
        description="Cross-encoder relevance confidence score (0.0 to 1.0)",
    )
    snippet: str = Field(
        sa_column=Column(Text, nullable=False),
        description="Exact verbatim passage extracted from source document",
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        nullable=False,
    )

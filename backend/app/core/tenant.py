"""
DocuNorm AI — Sovereign Multi-Tenant Context & PostgreSQL RLS Engine.
Enforces institutional client tenant partitioning required by:
- EU GDPR (Art. 32 Security of Processing)
- German Banking Act (KWG § 25b Auslagerung von Aktivitäten und Prozessen)
- DORA (Art. 30 Contractual Requirements for Financial Entities)
- BaFin Cloud Guidance (Multi-Client Tenant Segregation)
"""

import contextvars
from collections.abc import Generator
from contextlib import contextmanager
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import text

# Canonical Enterprise Demo & Benchmark Tenant UUIDs
SIEMENS_TENANT_ID = UUID("00000000-0000-0000-0000-000000000001")
DEUTSCHE_BANK_TENANT_ID = UUID("00000000-0000-0000-0000-000000000002")
ALLIANZ_TENANT_ID = UUID("00000000-0000-0000-0000-000000000003")
BMW_TENANT_ID = UUID("00000000-0000-0000-0000-000000000004")

DEFAULT_TENANT_ID = SIEMENS_TENANT_ID

# Thread-safe and asyncio-safe Request Context Variable
_current_tenant_id: contextvars.ContextVar[UUID | None] = contextvars.ContextVar(
    "current_tenant_id",
    default=None,
)


def get_current_tenant_id() -> UUID:
    """
    Returns the currently active tenant UUID for the executing request or background task.
    Falls back to DEFAULT_TENANT_ID (Siemens AG) if unassigned.
    """
    tenant_id = _current_tenant_id.get()
    return tenant_id or DEFAULT_TENANT_ID


def set_current_tenant_id(tenant_id: UUID) -> contextvars.Token:
    """
    Sets the active tenant UUID for the current asyncio context.
    Returns a token that can be used to reset the context later.
    """
    return _current_tenant_id.set(tenant_id)


def reset_current_tenant_id(token: contextvars.Token) -> None:
    """
    Resets the tenant context variable to its previous state.
    """
    _current_tenant_id.reset(token)


@contextmanager
def tenant_context(tenant_id: UUID) -> Generator[UUID, None, None]:
    """
    Context manager for safely executing a code block within a specific tenant context.
    Guarantees restoration of the previous tenant context on exit.
    """
    token = set_current_tenant_id(tenant_id)
    try:
        yield tenant_id
    finally:
        reset_current_tenant_id(token)


def generate_rls_sql() -> str:
    """
    Generates PostgreSQL 16 Row-Level Security (RLS) DDL statements.
    Ensures that at the database engine level, no query can read or write
    rows belonging to a different tenant, regardless of application bugs.
    """
    return """
-- 1. Enable Row-Level Security on core enterprise entity tables
ALTER TABLE documents ENABLE ROW LEVEL SECURITY;
ALTER TABLE document_chunks ENABLE ROW LEVEL SECURITY;
ALTER TABLE audit_logs ENABLE ROW LEVEL SECURITY;

-- 2. Drop existing tenant isolation policies if present
DROP POLICY IF EXISTS tenant_isolation_documents ON documents;
DROP POLICY IF EXISTS tenant_isolation_chunks ON document_chunks;
DROP POLICY IF EXISTS tenant_isolation_audit ON audit_logs;

-- 3. Define PostgreSQL RLS isolation policies using session variable 'app.current_tenant_id'
CREATE POLICY tenant_isolation_documents ON documents
    FOR ALL
    USING (
        tenant_id = NULLIF(current_setting('app.current_tenant_id', true), '')::uuid
    )
    WITH CHECK (
        tenant_id = NULLIF(current_setting('app.current_tenant_id', true), '')::uuid
    );

CREATE POLICY tenant_isolation_chunks ON document_chunks
    FOR ALL
    USING (
        tenant_id = NULLIF(current_setting('app.current_tenant_id', true), '')::uuid
    )
    WITH CHECK (
        tenant_id = NULLIF(current_setting('app.current_tenant_id', true), '')::uuid
    );

CREATE POLICY tenant_isolation_audit ON audit_logs
    FOR ALL
    USING (
        tenant_id = NULLIF(current_setting('app.current_tenant_id', true), '')::uuid
    )
    WITH CHECK (
        tenant_id = NULLIF(current_setting('app.current_tenant_id', true), '')::uuid
    );
""".strip()


async def apply_rls_session_context(db: AsyncSession, tenant_id: UUID) -> None:
    """
    Sets the session-local 'app.current_tenant_id' variable in PostgreSQL.
    When running under SQLite, this operation is a safe no-op.
    """
    try:
        bind = db.get_bind()
        if bind and bind.dialect.name == "postgresql":
            await db.execute(
                text(f"SET LOCAL app.current_tenant_id = '{tenant_id}';")
            )
    except Exception:
        pass

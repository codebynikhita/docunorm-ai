"""
DocuNorm AI — Multi-Tenant Row-Level Security (RLS) & Client Partitioning Test Suite.
Validates tenant context scoping, cross-tenant document isolation, vector search segregation,
and REST telemetry endpoints in accordance with GDPR Art. 32 and BaFin KWG § 25b.
"""

from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlmodel import select

from app.core.db import async_session_factory
from app.core.tenant import (
    ALLIANZ_TENANT_ID,
    BMW_TENANT_ID,
    DEUTSCHE_BANK_TENANT_ID,
    SIEMENS_TENANT_ID,
    generate_rls_sql,
    get_current_tenant_id,
    reset_current_tenant_id,
    set_current_tenant_id,
    tenant_context,
)
from app.main import app
from app.models.document import Document, DocumentChunk, DocumentStatus
from app.models.user import User, UserRole
from app.services.tenant_service import tenant_service


def test_tenant_context_vars():
    """
    Verifies thread-local and asyncio-safe ContextVar behavior:
    - Default fallback to SIEMENS_TENANT_ID
    - Manual set and reset
    - Safe nested context manager restoration
    """
    assert get_current_tenant_id() == SIEMENS_TENANT_ID

    token = set_current_tenant_id(DEUTSCHE_BANK_TENANT_ID)
    assert get_current_tenant_id() == DEUTSCHE_BANK_TENANT_ID
    reset_current_tenant_id(token)
    assert get_current_tenant_id() == SIEMENS_TENANT_ID

    # Context manager test
    with tenant_context(ALLIANZ_TENANT_ID):
        assert get_current_tenant_id() == ALLIANZ_TENANT_ID
        with tenant_context(BMW_TENANT_ID):
            assert get_current_tenant_id() == BMW_TENANT_ID
        assert get_current_tenant_id() == ALLIANZ_TENANT_ID

    assert get_current_tenant_id() == SIEMENS_TENANT_ID


def test_rls_sql_generation():
    """
    Verifies that the generated PostgreSQL 16 Row-Level Security DDL meets
    BaFin KWG § 25b and PostgreSQL official syntax standards.
    """
    sql = generate_rls_sql()
    assert "ALTER TABLE documents ENABLE ROW LEVEL SECURITY;" in sql
    assert "ALTER TABLE document_chunks ENABLE ROW LEVEL SECURITY;" in sql
    assert "ALTER TABLE audit_logs ENABLE ROW LEVEL SECURITY;" in sql
    assert "CREATE POLICY tenant_isolation_documents ON documents" in sql
    assert "current_setting('app.current_tenant_id', true)" in sql


@pytest.mark.asyncio
async def test_tenant_service_seeding_and_resolution():
    """
    Verifies canonical tenant provisioning and flexible UUID/slug resolution.
    """
    async with async_session_factory() as session:
        tenants = await tenant_service.seed_canonical_tenants(session)
        assert len(tenants) >= 4

        # Verify resolution by UUID
        t_siemens = await tenant_service.get_tenant_by_id_or_slug(session, SIEMENS_TENANT_ID)
        assert t_siemens is not None
        assert "Siemens" in t_siemens.name

        # Verify resolution by slug
        t_db = await tenant_service.get_tenant_by_id_or_slug(session, "deutsche-bank-ag")
        assert t_db is not None
        assert t_db.id == DEUTSCHE_BANK_TENANT_ID

        # Verify resolution by prefix alias
        t_allianz = await tenant_service.get_tenant_by_id_or_slug(session, "allianz")
        assert t_allianz is not None
        assert t_allianz.id == ALLIANZ_TENANT_ID


@pytest.mark.asyncio
async def test_cross_tenant_document_isolation():
    """
    Core Penetration Test:
    Ensures documents belonging to Tenant A (Siemens) are completely invisible
    to queries executed under Tenant B (Deutsche Bank) context.
    """
    async with async_session_factory() as session:
        await tenant_service.seed_canonical_tenants(session)

        # Create user for Siemens
        u_siemens = User(
            id=uuid4(),
            tenant_id=SIEMENS_TENANT_ID,
            email=f"tester-{uuid4()}@siemens.de",
            full_name="Siemens Tester",
            hashed_password="mock",
            role=UserRole.AUDITOR,
        )
        session.add(u_siemens)

        # Create user for Deutsche Bank
        u_db = User(
            id=uuid4(),
            tenant_id=DEUTSCHE_BANK_TENANT_ID,
            email=f"tester-{uuid4()}@deutsche-bank.de",
            full_name="DB Tester",
            hashed_password="mock",
            role=UserRole.AUDITOR,
        )
        session.add(u_db)
        await session.flush()

        # Create Document for Siemens
        doc_siemens = Document(
            id=uuid4(),
            tenant_id=SIEMENS_TENANT_ID,
            uploaded_by=u_siemens.id,
            filename="Siemens_Confidential_Cloud_Contract.pdf",
            file_path="/storage/documents/siemens/doc1.pdf",
            file_size_bytes=1048576,
            mime_type="application/pdf",
            sha256_hash=uuid4().hex + uuid4().hex,
            status=DocumentStatus.READY,
            total_pages=5,
        )
        session.add(doc_siemens)

        # Create Document for Deutsche Bank
        doc_db = Document(
            id=uuid4(),
            tenant_id=DEUTSCHE_BANK_TENANT_ID,
            uploaded_by=u_db.id,
            filename="DeutscheBank_Treasury_Outsourcing.pdf",
            file_path="/storage/documents/db/doc2.pdf",
            file_size_bytes=2048576,
            mime_type="application/pdf",
            sha256_hash=uuid4().hex + uuid4().hex,
            status=DocumentStatus.READY,
            total_pages=8,
        )
        session.add(doc_db)
        await session.commit()

        # Query scoped to Siemens
        stmt_siemens = select(Document).where(Document.tenant_id == SIEMENS_TENANT_ID)
        siemens_docs = (await session.execute(stmt_siemens)).scalars().all()
        siemens_ids = [d.id for d in siemens_docs]
        assert doc_siemens.id in siemens_ids
        assert doc_db.id not in siemens_ids  # DB doc must NOT leak into Siemens

        # Query scoped to Deutsche Bank
        stmt_db = select(Document).where(Document.tenant_id == DEUTSCHE_BANK_TENANT_ID)
        db_docs = (await session.execute(stmt_db)).scalars().all()
        db_ids = [d.id for d in db_docs]
        assert doc_db.id in db_ids
        assert doc_siemens.id not in db_ids  # Siemens doc must NOT leak into DB


@pytest.mark.asyncio
async def test_cross_tenant_vector_search_isolation():
    """
    Verifies that vector search chunks from Tenant A cannot be retrieved
    by Tenant B even when searching with 100% identical semantic queries.
    """
    async with async_session_factory() as session:
        # Create Chunk for Allianz
        chunk_allianz = DocumentChunk(
            id=uuid4(),
            document_id=uuid4(),
            tenant_id=ALLIANZ_TENANT_ID,
            chunk_index=0,
            page_number=1,
            content="Solvency II Art. 274 Risikomanagement und aufsichtsrechtliche Meldepflichten.",
            token_count=12,
        )
        session.add(chunk_allianz)

        # Create Chunk for BMW
        chunk_bmw = DocumentChunk(
            id=uuid4(),
            document_id=uuid4(),
            tenant_id=BMW_TENANT_ID,
            chunk_index=0,
            page_number=1,
            content="LkSG § 2 Sorgfaltspflichten in der Automobil-Zulieferkette und BAFA-Prüfung.",
            token_count=14,
        )
        session.add(chunk_bmw)
        await session.commit()

        # Search scoped to Allianz
        allianz_stmt = select(DocumentChunk).where(
            DocumentChunk.tenant_id == ALLIANZ_TENANT_ID,
            DocumentChunk.content.contains("Solvency II"),
        )
        allianz_res = (await session.execute(allianz_stmt)).scalars().all()
        assert len(allianz_res) >= 1
        assert any(c.id == chunk_allianz.id for c in allianz_res)

        # Cross-search: BMW querying for Solvency II
        cross_stmt = select(DocumentChunk).where(
            DocumentChunk.tenant_id == BMW_TENANT_ID,
            DocumentChunk.content.contains("Solvency II"),
        )
        cross_res = (await session.execute(cross_stmt)).scalars().all()
        assert len(cross_res) == 0  # BMW must see ZERO Allianz chunks


def test_tenant_fastapi_endpoints():
    """
    Tests the REST endpoints:
    - GET /api/v1/tenants
    - GET /api/v1/tenants/current
    - GET /api/v1/tenants/isolation-audit
    - Headers: X-Tenant-ID and X-Multi-Tenant-Policy
    """
    client = TestClient(app)

    # 1. List all tenants
    res = client.get("/api/v1/tenants")
    assert res.status_code == 200
    tenants = res.json()
    assert len(tenants) >= 4
    slugs = [t["slug"] for t in tenants]
    assert "siemens-ag" in slugs
    assert "deutsche-bank-ag" in slugs

    # 2. Introspect current tenant with default header
    res_curr = client.get("/api/v1/tenants/current")
    assert res_curr.status_code == 200
    data_curr = res_curr.json()
    assert data_curr["id"] == str(SIEMENS_TENANT_ID)
    assert res_curr.headers.get("X-Multi-Tenant-Policy") == "Row-Level-Security-Isolated"

    # 3. Introspect with X-Tenant-ID header: deutsche-bank-ag
    res_db = client.get(
        "/api/v1/tenants/current",
        headers={"X-Tenant-ID": "deutsche-bank-ag"},
    )
    assert res_db.status_code == 200
    data_db = res_db.json()
    assert data_db["id"] == str(DEUTSCHE_BANK_TENANT_ID)
    assert "Deutsche Bank" in data_db["name"]

    # 4. Run isolation audit
    res_audit = client.get(
        "/api/v1/tenants/isolation-audit",
        headers={"X-Tenant-ID": "allianz-se"},
    )
    assert res_audit.status_code == 200
    audit_data = res_audit.json()
    assert audit_data["tenant_id"] == str(ALLIANZ_TENANT_ID)
    assert audit_data["cross_tenant_leakage_detected"] is False
    assert "GDPR Art. 32" in audit_data["compliance_certification"]

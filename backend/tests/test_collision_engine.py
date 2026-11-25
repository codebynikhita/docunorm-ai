"""
DocuNorm AI — Day 38: Cross-Regulatory Conflict & Jurisdictional Incompatibility Test Suite.
Validates multi-standard collision detection (DORA vs. CLOUD Act vs. GDPR vs. KWG vs. BGB),
statutory precedence rules (Lex Superior), DIN 5008 legal opinion PDF export, and REST endpoints.
"""

from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from app.core.db import async_session_factory
from app.core.tenant import SIEMENS_TENANT_ID
from app.main import app
from app.models.document import Document, DocumentChunk, DocumentStatus
from app.models.user import User, UserRole
from app.schemas.collision import ClauseReconcileRequest
from app.services.collision_engine import collision_engine


def test_cloud_act_vs_gdpr_collision():
    """
    Verifies detection of US CLOUD Act subpoena subjugation without international MLAT treaty,
    flagging CRITICAL_BLOCKER and Lex Superior EU privacy precedence.
    """
    chunks = [
        {
            "content": (
                "The contractor operates under United States law and shall promptly comply with all lawful "
                "subpoenas, court orders, or requests issued under the US CLOUD Act (18 U.S.C. § 2713) "
                "by US law enforcement agencies without requiring prior approval or court orders in Germany."
            ),
            "page_number": 2,
            "bounding_box": [50.0, 100.0, 500.0, 160.0],
        }
    ]

    matrix = collision_engine.analyze_conflicts(
        document_id=uuid4(),
        document_filename="AWS_Enterprise_Outsourcing.pdf",
        chunks=chunks,
    )

    assert matrix.conflicts_detected >= 1
    assert matrix.critical_blockers >= 1
    assert matrix.compliance_verdict == "INCOMPATIBLE_BLOCKER"
    assert matrix.jurisdictional_exposure_map["US_EXTRATERRITORIAL"] >= 1

    conf = matrix.conflicts[0]
    assert conf.conflict_id == "CONF-CLOUD-GDPR-01"
    assert conf.standard_a == "CLOUD_ACT"
    assert conf.standard_b == "GDPR"
    assert conf.severity == "CRITICAL_BLOCKER"
    assert "DSGVO Art. 48" in conf.statutory_clash_summary_de
    assert "BYOK" in conf.resolution_covenant_de or "HSM" in conf.resolution_covenant_de


def test_dora_audit_vs_datacenter_multi_tenant_secrecy():
    """
    Verifies collision between DORA Art. 30 on-site physical datacenter audit mandate
    and GDPR Art. 32 multi-tenant customer confidentiality, resolved via Pooled Audits.
    """
    chunks = [
        {
            "content": (
                "Vor-Ort-Prüfungen oder physischer Zutritt zu den Rechenzentren sind nicht gestattet, "
                "da der Dienstleister in einer Multi-Tenant Umgebung operiert und der Schutz der Daten "
                "anderer Kunden Vorrang hat."
            ),
            "page_number": 4,
            "bounding_box": [50.0, 200.0, 500.0, 260.0],
        }
    ]

    matrix = collision_engine.analyze_conflicts(
        document_id=uuid4(),
        document_filename="Azure_Banking_Cloud.pdf",
        chunks=chunks,
    )

    assert matrix.conflicts_detected >= 1
    assert matrix.high_risks >= 1
    conf = matrix.conflicts[0]
    assert conf.conflict_id == "CONF-DORA-GDPR-02"
    assert "DORA Art. 30" in conf.title_de
    assert "Pooled Audits" in conf.resolution_covenant_de or "Gemeinschaftsprüfungen" in conf.resolution_covenant_de


def test_bafin_termination_vs_bgb_lockin():
    """
    Verifies conflict between KWG § 25b supervisory termination rights and BGB fixed-term lock-in.
    """
    chunks = [
        {
            "content": (
                "Die Parteien vereinbaren eine feste Mindestlaufzeit von 36 Monaten. "
                "Eine vorzeitige ordentliche Kündigung ist ausgeschlossen. Bei vorzeitiger Beendigung fällt "
                "eine pauschale Vorfälligkeitsentschädigung von 80% der Restlaufzeit an."
            ),
            "page_number": 8,
            "bounding_box": [50.0, 300.0, 500.0, 360.0],
        }
    ]

    matrix = collision_engine.analyze_conflicts(
        document_id=uuid4(),
        document_filename="Core_Banking_SLA.pdf",
        chunks=chunks,
    )

    assert matrix.conflicts_detected >= 1
    assert matrix.critical_blockers >= 1
    conf = matrix.conflicts[0]
    assert conf.conflict_id == "CONF-BAFIN-BGB-03"
    assert "KWG § 25b" in conf.title_de
    assert "Vorfälligkeitsentschädigung" in conf.resolution_covenant_de


def test_lksg_vs_trade_secrets_act():
    """
    Verifies conflict between LkSG § 9 Tier-N transparency and GeschGehG trade secrets.
    """
    chunks = [
        {
            "content": (
                "Der Lieferant verweigert jegliche Offenlegung der Lieferanten und mittelbare Zulieferer (Tier-N), "
                "da dies ein streng vertrauliches Geschäftsgeheimnis darstellt."
            ),
            "page_number": 5,
        }
    ]

    matrix = collision_engine.analyze_conflicts(
        document_id=uuid4(),
        document_filename="Supply_Chain_Master.pdf",
        chunks=chunks,
    )

    assert matrix.conflicts_detected >= 1
    assert matrix.medium_risks >= 1
    conf = matrix.conflicts[0]
    assert conf.conflict_id == "CONF-LKSG-SECRECY-04"
    assert "Clean-Team" in conf.resolution_covenant_de or "Escrow" in conf.resolution_covenant_de


def test_nis2_vs_nda_secrecy():
    """
    Verifies conflict between NIS-2 24h cyber incident reporting and strict non-disclosure.
    """
    chunks = [
        {
            "content": (
                "Bei einem schwerwiegenden Cyber-Angriff oder Sicherheitsvorfall gilt strikte Geheimhaltung. "
                "Es darf keine Information an Behörden oder Dritte ohne schriftliche Genehmigung weitergeleitet werden."
            ),
            "page_number": 3,
        }
    ]

    matrix = collision_engine.analyze_conflicts(
        document_id=uuid4(),
        document_filename="Cybersecurity_NDA.pdf",
        chunks=chunks,
    )

    assert matrix.conflicts_detected >= 1
    assert matrix.high_risks >= 1
    conf = matrix.conflicts[0]
    assert conf.conflict_id == "CONF-NIS2-CONF-05"
    assert "NIS-2" in conf.title_de


def test_collision_matrix_pdf_generation(tmp_path):
    """
    Verifies 2-page certified DIN 5008 PDF generation with legal attestation and SHA-256 seal.
    """
    chunks = [
        {
            "content": "Compliance with US CLOUD Act subpoenas without prior German court approval.",
            "page_number": 1,
        },
        {
            "content": "Physische Audits im Rechenzentrum sind zum Schutz Dritter in Multi-Tenant Umgebungen verwehrt.",
            "page_number": 2,
        },
    ]

    matrix = collision_engine.analyze_conflicts(
        document_id=uuid4(),
        document_filename="Siemens_Cloud_2026.pdf",
        chunks=chunks,
    )

    pdf_file = collision_engine.generate_collision_matrix_pdf(
        document_filename="Siemens_Cloud_2026.pdf",
        matrix=matrix,
        output_dir=tmp_path,
    )

    assert pdf_file.exists()
    assert pdf_file.stat().st_size > 1500


def test_reconcile_clause_stateless_endpoint():
    """
    Verifies POST /api/v1/collision/reconcile-clause endpoint.
    """
    client = TestClient(app)
    payload = ClauseReconcileRequest(
        clause_text="Vendor complies with all US CLOUD Act law enforcement subpoenas immediately.",
    )

    res = client.post("/api/v1/collision/reconcile-clause", json=payload.model_dump())
    assert res.status_code == 200
    data = res.json()
    assert data["has_conflicts"] is True
    assert len(data["detected_conflicts"]) >= 1
    assert data["jurisdiction_exposure"] == "US_EXTRATERRITORIAL"
    assert data["reconciliation_covenant_de"] is not None


@pytest.mark.asyncio
async def test_document_collision_matrix_endpoints():
    """
    Verifies:
    1. GET /api/v1/collision/documents/{id}/matrix
    2. GET /api/v1/collision/documents/{id}/export-matrix-pdf
    """
    client = TestClient(app)

    async with async_session_factory() as session:
        user = User(
            id=uuid4(),
            email=f"jurist-{uuid4().hex[:6]}@siemens.de",
            full_name="Leitender Jurist",
            hashed_password="mock_pbkdf2_hash_for_testing",
            role=UserRole.ADMIN,
            is_active=True,
            tenant_id=SIEMENS_TENANT_ID,
        )
        session.add(user)

        doc = Document(
            id=uuid4(),
            tenant_id=SIEMENS_TENANT_ID,
            uploaded_by=user.id,
            filename="Siemens_MultiStandard_Test.pdf",
            file_path="/storage/documents/siemens/test_collision.pdf",
            file_size_bytes=20000,
            mime_type="application/pdf",
            sha256_hash=uuid4().hex + uuid4().hex,
            status=DocumentStatus.READY,
            total_pages=3,
        )
        session.add(doc)

        chunk1 = DocumentChunk(
            id=uuid4(),
            document_id=doc.id,
            tenant_id=SIEMENS_TENANT_ID,
            chunk_index=0,
            page_number=1,
            content="Präambel: Cloud-Dienstleistungen für Finanzinstitute unter US-Recht und CLOUD Act.",
            token_count=10,
        )
        chunk2 = DocumentChunk(
            id=uuid4(),
            document_id=doc.id,
            tenant_id=SIEMENS_TENANT_ID,
            chunk_index=1,
            page_number=2,
            content="Zutritt zum Rechenzentrum ist verwehrt da multi-tenant Umgebung.",
            token_count=12,
        )
        session.add_all([chunk1, chunk2])
        await session.commit()

        doc_id = doc.id
        chunk_ids = [chunk1.id, chunk2.id]

    # 1. Test GET /api/v1/collision/documents/{doc_id}/matrix
    matrix_res = client.get(
        f"/api/v1/collision/documents/{doc_id}/matrix",
        headers={"X-Tenant-ID": "siemens-ag"},
    )
    assert matrix_res.status_code == 200
    matrix_data = matrix_res.json()
    assert matrix_data["conflicts_detected"] >= 2
    assert matrix_data["compliance_verdict"] in ["INCOMPATIBLE_BLOCKER", "CONDITIONALLY_RECONCILABLE"]
    assert len(matrix_data["sha256_hash"]) == 64

    # 2. Test GET /api/v1/collision/documents/{doc_id}/export-matrix-pdf
    pdf_res = client.get(
        f"/api/v1/collision/documents/{doc_id}/export-matrix-pdf",
        headers={"X-Tenant-ID": "siemens-ag"},
    )
    assert pdf_res.status_code == 200
    assert pdf_res.headers["content-type"] == "application/pdf"
    assert len(pdf_res.content) > 1000

    # Teardown
    async with async_session_factory() as session:
        for cid in chunk_ids:
            c = await session.get(DocumentChunk, cid)
            if c:
                await session.delete(c)
        d = await session.get(Document, doc_id)
        u = await session.get(User, user.id)
        if d:
            await session.delete(d)
        if u:
            await session.delete(u)
        await session.commit()

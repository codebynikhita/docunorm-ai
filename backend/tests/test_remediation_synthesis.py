"""
DocuNorm AI — Day 37: Automated Regulatory Remediation & Contract Clause Synthesis Test Suite.
Validates bespoke AI clause synthesis, BaFin/DORA/GDPR parameterization, word-level redline diffs,
in-place document chunk remediation, and official § 311 BGB Nachtragsvereinbarung PDF export.
"""

from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from app.core.db import async_session_factory
from app.core.tenant import SIEMENS_TENANT_ID
from app.main import app
from app.models.document import Document, DocumentChunk, DocumentStatus
from app.models.user import User, UserRole
from app.schemas.remediation import RemediationSynthesisRequest
from app.services.remediation_engine import RemediationEngine


def test_bespoke_synthesis_dora_custom_parameters():
    """
    Verifies bespoke clause synthesis with customized exit and migration parameters.
    """
    req = RemediationSynthesisRequest(
        rule_id="DORA-EXIT-CUSTOM",
        original_clause="Kündigung ist mit 14 Tagen Frist möglich, ohne Unterstützung beim Übergang.",
        target_framework="DORA",
        custom_parameters={
            "exit_notice_days": 60,
            "migration_days": 90,
            "penalty_daily_pct": 0.25,
        },
    )

    proposal = RemediationEngine.synthesize_bespoke_amendment(
        rule_id=req.rule_id,
        original_clause=req.original_clause,
        target_framework=req.target_framework,
        custom_parameters=req.custom_parameters,
    )

    assert "60 Tagen" in proposal.compliant_replacement_de
    assert "90 Tage" in proposal.compliant_replacement_de
    assert "0.25 %" in proposal.compliant_replacement_de
    assert "DORA Art. 30" in proposal.dora_statutory_basis
    assert len(proposal.diff_tokens) > 0


def test_bespoke_synthesis_bafin_audit_rights():
    """
    Verifies BaFin KWG § 25b unrestricted audit rights with customizable notice window.
    """
    req = RemediationSynthesisRequest(
        rule_id="BAFIN-AUDIT-01",
        original_clause="Vor-Ort-Prüfungen durch den Auftraggeber sind ausgeschlossen.",
        target_framework="KWG",
        custom_parameters={
            "audit_notice": "48 Stunden Vorankündigung",
        },
    )

    proposal = RemediationEngine.synthesize_bespoke_amendment(
        rule_id=req.rule_id,
        original_clause=req.original_clause,
        target_framework=req.target_framework,
        custom_parameters=req.custom_parameters,
    )

    assert "BaFin" in proposal.compliant_replacement_de
    assert "48 Stunden Vorankündigung" in proposal.compliant_replacement_de
    assert "uneingeschränkten" in proposal.compliant_replacement_de
    assert "BGB § 307" in proposal.bgb_statutory_basis


def test_bespoke_synthesis_subcontracting_veto():
    """
    Verifies DORA Art. 30(3) and BGB § 278 subcontractor veto rights and vicarious liability.
    """
    proposal = RemediationEngine.synthesize_bespoke_amendment(
        rule_id="DORA-SUBCONTRACT-01",
        original_clause="Der Auftragnehmer darf Nachunternehmer ohne Zustimmung einsetzen. Haftung ist ausgeschlossen.",
        target_framework="DORA",
        custom_parameters={"subcontractor_veto_days": 45},
    )

    assert "45 Kalendertagen" in proposal.compliant_replacement_de
    assert "§ 278 BGB" in proposal.compliant_replacement_de
    assert "Widerspruchsrecht" in proposal.compliant_replacement_de


def test_bespoke_synthesis_gdpr_data_erasure():
    """
    Verifies GDPR Art. 28 / BDSG data erasure and DIN 66399 destruction protocol.
    """
    proposal = RemediationEngine.synthesize_bespoke_amendment(
        rule_id="GDPR-ERASURE-01",
        original_clause="Datensicherung verbleibt beim Dienstleister auf unbestimmte Zeit nach Kündigung.",
        target_framework="GDPR",
        custom_parameters={"erasure_days": 10},
    )

    assert "10 Kalendertagen" in proposal.compliant_replacement_de
    assert "DIN 66399 Schutzklasse 3" in proposal.compliant_replacement_de
    assert "Vernichtungsprotokoll" in proposal.compliant_replacement_de


def test_synthesize_agreement_package():
    """
    Verifies end-to-end agreement package synthesis with cryptographic SHA-256 seal.
    """
    doc_id = uuid4()
    chunks = [
        {
            "id": "c1",
            "page_number": 1,
            "content": "Zutritt zu den Rechenzentren und Vor-Ort-Prüfungen sind ausgeschlossen.",
        },
        {
            "id": "c2",
            "page_number": 2,
            "content": "Kündigung kann jederzeit mit 14 Tagen Frist ohne Übergangsunterstützung erfolgen.",
        },
    ]

    agreement = RemediationEngine.synthesize_agreement(
        document_id=doc_id,
        document_filename="Siemens_Cloud_Contract.pdf",
        chunks=chunks,
        target_framework="DORA",
    )

    assert agreement.total_amendments >= 2
    assert len(agreement.amendments) >= 2
    assert agreement.sha256_seal is not None
    assert len(agreement.sha256_seal) == 64
    assert agreement.status == "SYNTHESIZED"


@pytest.mark.asyncio
async def test_apply_amendment_endpoint_and_pdf():
    """
    Verifies:
    1. POST /api/v1/documents/{id}/synthesize-amendment
    2. POST /api/v1/documents/{id}/apply-amendment (updates chunk & generates audit log)
    3. GET /api/v1/documents/{id}/export-amendment-pdf (generates official PDF)
    """
    client = TestClient(app)

    async with async_session_factory() as session:
        user = User(
            id=uuid4(),
            email=f"compliance-tester-{uuid4().hex[:6]}@siemens.de",
            full_name="Compliance Officer",
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
            filename="Siemens_Remediation_Test.pdf",
            file_path="/storage/documents/siemens/test_remediation.pdf",
            file_size_bytes=15000,
            mime_type="application/pdf",
            sha256_hash=uuid4().hex + uuid4().hex,
            status=DocumentStatus.READY,
            total_pages=2,
        )
        session.add(doc)

        chunk = DocumentChunk(
            id=uuid4(),
            document_id=doc.id,
            tenant_id=SIEMENS_TENANT_ID,
            chunk_index=0,
            page_number=1,
            content="Vor-Ort-Prüfungen und Rechenzentrumsaudits sind dem Kunden untersagt.",
            token_count=10,
        )
        session.add(chunk)
        await session.commit()

        doc_id = doc.id
        chunk_id = chunk.id

    # 1. Synthesize bespoke amendment
    synth_res = client.post(
        f"/api/v1/documents/{doc_id}/synthesize-amendment",
        json={
            "rule_id": "BAFIN-AUDIT-01",
            "original_clause": "Vor-Ort-Prüfungen und Rechenzentrumsaudits sind dem Kunden untersagt.",
            "target_framework": "KWG",
            "custom_parameters": {"audit_notice": "unverzüglich bei begründetem Verdacht"},
        },
        headers={"X-Tenant-ID": "siemens-ag"},
    )
    assert synth_res.status_code == 200
    synth_data = synth_res.json()
    assert "BaFin" in synth_data["compliant_replacement_de"]
    assert "unverzüglich bei begründetem Verdacht" in synth_data["compliant_replacement_de"]

    # 2. Apply amendment in-place to the document chunk
    apply_res = client.post(
        f"/api/v1/documents/{doc_id}/apply-amendment",
        json={
            "chunk_id": str(chunk_id),
            "new_clause_text": synth_data["compliant_replacement_de"],
            "rule_id": "BAFIN-AUDIT-01",
            "justification": "Heilung des unzulässigen Zutrittsverbots gem. KWG § 25b",
        },
        headers={"X-Tenant-ID": "siemens-ag"},
    )
    assert apply_res.status_code == 200
    apply_data = apply_res.json()
    assert apply_data["reembedded"] is True
    assert apply_data["audit_event_id"] is not None
    assert len(apply_data["sha256_hash"]) == 64

    # 3. Verify chunk content was updated in the DB
    async with async_session_factory() as session:
        updated_chunk = await session.get(DocumentChunk, chunk_id)
        assert updated_chunk is not None
        assert "BaFin" in updated_chunk.content

    # 4. Export Addendum Contract PDF (GET and POST)
    pdf_res_get = client.get(
        f"/api/v1/documents/{doc_id}/export-amendment-pdf",
        headers={"X-Tenant-ID": "siemens-ag"},
    )
    assert pdf_res_get.status_code == 200
    assert pdf_res_get.headers["content-type"] == "application/pdf"
    assert len(pdf_res_get.content) > 1000

    pdf_res_post = client.post(
        f"/api/v1/documents/{doc_id}/export-amendment-pdf",
        json={"proposals": [synth_data]},
        headers={"X-Tenant-ID": "siemens-ag"},
    )
    assert pdf_res_post.status_code == 200
    assert pdf_res_post.headers["content-type"] == "application/pdf"

    # Teardown test artifacts
    async with async_session_factory() as session:
        c = await session.get(DocumentChunk, chunk_id)
        d = await session.get(Document, doc_id)
        u = await session.get(User, user.id)
        for obj in [c, d, u]:
            if obj:
                await session.delete(obj)
        await session.commit()

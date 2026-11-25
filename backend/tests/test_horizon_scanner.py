"""
DocuNorm AI — Day 39: RegTech Horizon Scanner & Contract Drift Test Suite.
Validates dynamic statutory updates (DORA RTS 2026, BaFin RS 10/2026, EU AI Act Aug 2026, EDPB 04/2026),
contract drift scoring, DIN 5008 legal opinion PDF export, and multi-tenant REST endpoints.
"""

from datetime import date
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from app.core.db import async_session_factory
from app.core.tenant import SIEMENS_TENANT_ID
from app.main import app
from app.models.document import Document, DocumentChunk, DocumentStatus
from app.models.user import User, UserRole
from app.services.horizon_scanner import horizon_scanner


def test_active_statutory_catalog():
    """
    Verifies statutory updates catalog retrieval, days-until-deadline calculation,
    and authority filtering.
    """
    ref_date = date(2026, 3, 1)
    updates = horizon_scanner.get_active_updates(reference_date=ref_date)

    assert len(updates) >= 5
    ids = [u.update_id for u in updates]
    assert "REG-DORA-RTS-2026-01" in ids
    assert "REG-BAFIN-RS-2026-10" in ids
    assert "REG-EU-AIACT-2026-08" in ids
    assert "REG-EDPB-KEY-2026-04" in ids
    assert "REG-BAFA-LKSG-2026-05" in ids

    # Test filtering by authority
    bafin_updates = [u for u in updates if u.issuing_authority == "BAFIN"]
    assert len(bafin_updates) >= 1
    assert bafin_updates[0].update_id == "REG-BAFIN-RS-2026-10"

    # Days until deadline should be positive for 2026-03-01 vs 2026-09-30
    assert bafin_updates[0].days_until_enforcement == (date(2026, 9, 30) - ref_date).days


def test_dora_rts_subcontracting_drift():
    """
    Verifies detection of subcontracting clause missing 4th-party flow-through under DORA RTS 2026.
    """
    chunks = [
        {
            "content": (
                "Der Auftragnehmer ist berechtigt, zur Erbringung der geschuldeten Leistungen Unterauftragnehmer "
                "einzusetzen. Die Haftung des Auftragnehmers für das Verschulden von Erfüllungsgehilfen richtet sich "
                "nach den gesetzlichen Vorschriften des BGB."
            ),
            "page_number": 4,
        }
    ]

    report = horizon_scanner.audit_contract_drift(
        document_id=uuid4(),
        document_filename="Cloud_Outsourcing_Legacy.pdf",
        chunks=chunks,
        reference_date=date(2026, 3, 1),
    )

    assert report.drifting_clauses_count >= 1
    assert report.critical_enforcement_items >= 1
    assert report.retrofitting_status in ["ACTION_REQUIRED", "NON_COMPLIANT_EXPIRED"]

    drift = report.drift_items[0]
    assert drift.associated_update_id == "REG-DORA-RTS-2026-01"
    assert drift.drift_severity == "CRITICAL_DRIFT"
    assert "DORA RTS" in drift.compliance_gap_de
    assert "30-Tage-Vetorechts" in drift.retrofitting_action_required


def test_bafin_unwinding_drift():
    """
    Verifies detection of termination/exit clause missing BaFin RS 10/2026 emergency unwinding provisions.
    """
    chunks = [
        {
            "content": (
                "Der Vertrag hat eine feste Laufzeit von fünf Jahren. Eine vorzeitige Kündigung ist ausgeschlossen. "
                "Bei Kündigung aus wichtigem Grund wird eine pauschale Vorfälligkeitsentschädigung in Höhe von "
                "50 % der Restvergütung fällig. Eine Datenmigration erfolgt nur gegen gesonderte Aufwandspauschale."
            ),
            "page_number": 8,
        }
    ]

    report = horizon_scanner.audit_contract_drift(
        document_id=uuid4(),
        document_filename="Hyperscaler_Agreement_2024.pdf",
        chunks=chunks,
        reference_date=date(2026, 3, 1),
    )

    assert report.drifting_clauses_count >= 1
    drift = next(d for d in report.drift_items if d.associated_update_id == "REG-BAFIN-RS-2026-10")
    assert drift.drift_severity == "CRITICAL_DRIFT"
    assert "BaFin RS 10/2026" in drift.compliance_gap_de
    assert "Vorfälligkeitsentschädigung" in drift.compliance_gap_de


def test_eu_ai_act_drift():
    """
    Verifies detection of AI components lacking Article 12 post-market logging covenants.
    """
    chunks = [
        {
            "content": (
                "Zur Optimierung von Kreditprüfungsentscheidungen setzt der Anbieter ein proprietäres KI-Modell "
                "(Machine Learning) ein. Die Parameter und Trainingsdaten des Algorithmus unterliegen dem Betriebsgeheimnis."
            ),
            "page_number": 6,
        }
    ]

    report = horizon_scanner.audit_contract_drift(
        document_id=uuid4(),
        document_filename="AI_Credit_Scoring_SaaS.pdf",
        chunks=chunks,
        reference_date=date(2026, 3, 1),
    )

    assert report.drifting_clauses_count >= 1
    drift = next(d for d in report.drift_items if d.associated_update_id == "REG-EU-AIACT-2026-08")
    assert drift.drift_severity == "HIGH_RISK"
    assert "EU AI Act" in drift.compliance_gap_de or "Art. 12" in drift.compliance_gap_de


def test_edpb_key_sovereignty_drift():
    """
    Verifies detection of cloud encryption with US-managed keys lacking EU HSM Key Sovereignty under EDPB 04/2026.
    """
    chunks = [
        {
            "content": (
                "Alle Daten werden im Ruhezustand (at rest) mittels AES-256 verschlüsselt. Das Key Management "
                "wird zentral durch AWS KMS in den Vereinigten Staaten gesteuert."
            ),
            "page_number": 11,
        }
    ]

    report = horizon_scanner.audit_contract_drift(
        document_id=uuid4(),
        document_filename="AWS_Storage_Service.pdf",
        chunks=chunks,
        reference_date=date(2026, 3, 1),
    )

    assert report.drifting_clauses_count >= 1
    drift = next(d for d in report.drift_items if d.associated_update_id == "REG-EDPB-KEY-2026-04")
    assert drift.drift_severity == "CRITICAL_DRIFT"
    assert "EDPB" in drift.compliance_gap_de or "Schrems" in drift.compliance_gap_de


def test_fully_compliant_contract_no_drift():
    """
    Verifies that a contract containing all modern 2026 compliance covenants achieves UP_TO_DATE status.
    """
    chunks = [
        {
            "content": (
                "Unterauftragsverhältnisse unterliegen den Vorgaben der DORA RTS (JC 2024 28). Tier-4 Verpflichtungen "
                "und quantitative Risikokennzahlen sowie das 30-Tage-Veto werden garantiert."
            ),
            "page_number": 3,
        },
        {
            "content": (
                "Bei aufsichtsrechtlicher Beanstandung greift die Notfall-Entflechtung gem. BaFin RS 10/2026 ohne "
                "Vorfälligkeitsentschädigung inklusive 90 Tage Migrationsbegleitung."
            ),
            "page_number": 5,
        },
    ]

    report = horizon_scanner.audit_contract_drift(
        document_id=uuid4(),
        document_filename="Modern_DORA_Compliant_Contract.pdf",
        chunks=chunks,
        reference_date=date(2026, 3, 1),
    )

    assert report.overall_drift_score == 0.0
    assert report.drifting_clauses_count == 0
    assert report.retrofitting_status == "UP_TO_DATE"
    assert len(report.drift_items) == 0


def test_certified_din5008_drift_pdf_generation():
    """
    Verifies generation of an official 2-page DIN 5008 Contract Drift Legal Opinion PDF.
    """
    chunks = [
        {
            "content": "Der Auftragnehmer kann Unterauftragnehmer ohne vorherige Ankündigung hinzuziehen.",
            "page_number": 1,
        },
        {
            "content": "Kündigung ist ausgeschlossen; Vorfälligkeitsentschädigung von 80% vereinbart.",
            "page_number": 2,
        },
    ]

    report = horizon_scanner.audit_contract_drift(
        document_id=uuid4(),
        document_filename="Legacy_Outsourcing_Draft.pdf",
        chunks=chunks,
        reference_date=date(2026, 3, 1),
    )

    pdf_path = horizon_scanner.generate_drift_report_pdf(
        document_filename="Legacy_Outsourcing_Draft.pdf",
        report=report,
        signatory_name="Dr. Hannelore Graf, Head of Enterprise Compliance",
    )

    assert pdf_path.exists()
    assert pdf_path.suffix == ".pdf"
    assert pdf_path.stat().st_size > 1000


@pytest.mark.asyncio
async def test_rest_horizon_updates_endpoint():
    """
    Verifies GET /api/v1/horizon/updates endpoint and authority filtering.
    """
    client = TestClient(app)
    response = client.get("/api/v1/horizon/updates")
    assert response.status_code == 200
    updates = response.json()
    assert len(updates) >= 5
    assert any(u["update_id"] == "REG-DORA-RTS-2026-01" for u in updates)

    # Filter by authority
    resp_filtered = client.get("/api/v1/horizon/updates?authority=EBA")
    assert resp_filtered.status_code == 200
    filtered = resp_filtered.json()
    assert len(filtered) >= 1
    assert all(u["issuing_authority"] == "EBA" for u in filtered)


@pytest.mark.asyncio
async def test_rest_document_drift_analysis_and_pdf():
    """
    Verifies document contract drift audit endpoint and DIN 5008 PDF download with tenant isolation.
    """
    async with async_session_factory() as db:
        # Create test user for tenant
        user = User(
            id=uuid4(),
            email=f"compliance_{uuid4().hex[:6]}@siemens.de",
            full_name="Compliance Auditor",
            role=UserRole.ADMIN,
            tenant_id=SIEMENS_TENANT_ID,
            hashed_password="mock_pbkdf2_hash_for_testing",
        )
        db.add(user)

        doc = Document(
            id=uuid4(),
            tenant_id=SIEMENS_TENANT_ID,
            uploaded_by=user.id,
            filename="Siemens_Cloud_Contract_2023.pdf",
            file_path="/tmp/Siemens_Cloud_Contract_2023.pdf",
            file_size_bytes=20480,
            mime_type="application/pdf",
            sha256_hash=uuid4().hex + uuid4().hex,
            status=DocumentStatus.READY,
            total_pages=2,
        )
        db.add(doc)
        await db.flush()

        chunk1 = DocumentChunk(
            id=uuid4(),
            tenant_id=SIEMENS_TENANT_ID,
            document_id=doc.id,
            content="Subunternehmer können jederzeit ohne Zustimmung beauftragt werden.",
            page_number=1,
            chunk_index=0,
            token_count=12,
        )
        chunk2 = DocumentChunk(
            id=uuid4(),
            tenant_id=SIEMENS_TENANT_ID,
            document_id=doc.id,
            content="Eine vorzeitige Kündigung ist unter Ausschluss jeglicher Rückabwicklung unzulässig.",
            page_number=2,
            chunk_index=1,
            token_count=14,
        )
        db.add_all([chunk1, chunk2])
        await db.commit()

        doc_id = doc.id

    client = TestClient(app)

    # 1. GET /api/v1/horizon/documents/{doc_id}/drift-analysis
    headers = {"X-Tenant-ID": str(SIEMENS_TENANT_ID)}
    res = client.get(f"/api/v1/horizon/documents/{doc_id}/drift-analysis", headers=headers)
    assert res.status_code == 200, res.text
    data = res.json()
    assert data["document_filename"] == "Siemens_Cloud_Contract_2023.pdf"
    assert data["drifting_clauses_count"] >= 2
    assert data["retrofitting_status"] in ["ACTION_REQUIRED", "NON_COMPLIANT_EXPIRED"]
    assert len(data["drift_items"]) >= 2
    assert "sha256_seal" in data

    # 2. GET /api/v1/horizon/documents/{doc_id}/export-drift-pdf
    pdf_res = client.get(f"/api/v1/horizon/documents/{doc_id}/export-drift-pdf", headers=headers)
    assert pdf_res.status_code == 200
    assert pdf_res.headers["content-type"] == "application/pdf"
    assert "GUTACHTEN_VERTRAGSDRIFT_Siemens_Cloud_Contract_2023.pdf" in pdf_res.headers["content-disposition"]
    assert len(pdf_res.content) > 1000

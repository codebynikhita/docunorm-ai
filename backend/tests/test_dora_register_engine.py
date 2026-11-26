"""
DocuNorm AI — Day 40: DORA Art. 28(3) Register of Information & Batch Remediation Test Suite.
Validates ESA JC 2024 05 / EBA/ITS/2024/01 register generation, BaFin Information Register PDF export,
portfolio batch remediation risk containment, and multi-tenant REST endpoints.
"""

from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from app.core.db import async_session_factory
from app.core.tenant import SIEMENS_TENANT_ID
from app.main import app
from app.models.document import Document, DocumentChunk, DocumentStatus
from app.models.user import User, UserRole
from app.services.dora_register_engine import dora_register_engine


@pytest.mark.asyncio
async def test_canonical_dora_register_generation():
    """
    Verifies generation of DORA Art. 28(3) Register of Information for a tenant
    with canonical fallback when no documents are uploaded yet.
    """
    empty_tenant_id = uuid4()
    async with async_session_factory() as db:
        register = await dora_register_engine.generate_register_for_tenant(empty_tenant_id, db)

        assert register.tenant_id == empty_tenant_id
        assert register.total_ict_contracts >= 4
        assert register.critical_ict_contracts >= 1
        assert 0.0 <= register.overall_compliance_rate <= 100.0
        assert "JC 2024 05" in register.esa_template_version
        assert len(register.sha256_register_seal) == 64

        # Validate entries
        leis = [e.vendor_lei for e in register.entries]
        assert "5493006MHB84DD0ZWV18" in leis  # AWS
        assert "5299000F053L529H6211" in leis  # SAP


@pytest.mark.asyncio
async def test_tenant_document_mapping_to_register():
    """
    Verifies mapping of ingested tenant contracts into structured DORA Art. 28(3) tables.
    """
    tenant_id = uuid4()
    async with async_session_factory() as db:
        user = User(
            id=uuid4(),
            email=f"auditor_{uuid4().hex[:6]}@enterprise.de",
            full_name="DORA Compliance Lead",
            role=UserRole.ADMIN,
            tenant_id=tenant_id,
            hashed_password="mock_pbkdf2_hash_for_testing",
        )
        db.add(user)

        doc = Document(
            id=uuid4(),
            tenant_id=tenant_id,
            uploaded_by=user.id,
            filename="AWS_Cloud_Hosting_CoreBanking.pdf",
            file_path="/tmp/AWS_Cloud_Hosting_CoreBanking.pdf",
            file_size_bytes=40960,
            mime_type="application/pdf",
            sha256_hash=uuid4().hex + uuid4().hex,
            status=DocumentStatus.READY,
            total_pages=5,
        )
        db.add(doc)
        await db.flush()

        chunk = DocumentChunk(
            id=uuid4(),
            tenant_id=tenant_id,
            document_id=doc.id,
            chunk_index=0,
            page_number=1,
            token_count=30,
            content=(
                "Präambel: Amazon Web Services (AWS) erbringt kritische Core Banking Cloud IaaS Dienste. "
                "KWG § 25b und DORA Art. 30 uneingeschränkte Prüfrechte und Zutrittsrechte werden garantiert. "
                "Kündigungsfrist beträgt 90 Tage. Unterauftragnehmer unterliegen Tier-4 Kaskadenregelungen (JC 2024 28)."
            ),
        )
        db.add(chunk)
        await db.commit()

        register = await dora_register_engine.generate_register_for_tenant(tenant_id, db)
        assert register.total_ict_contracts == 1
        entry = register.entries[0]
        assert "AWS" in entry.vendor_legal_name
        assert entry.criticality == "CRITICAL_IMPORTANT"
        assert entry.audit_rights_compliant is True
        assert entry.exit_notice_period_days == 90
        assert entry.subcontractor_depth == 4
        assert entry.remediation_status == "CLEAN"


@pytest.mark.asyncio
async def test_portfolio_batch_remediation_execution():
    """
    Verifies automated portfolio-wide contract batch remediation and mathematical risk containment index.
    """
    async with async_session_factory() as db:
        res = await dora_register_engine.execute_portfolio_batch_remediation(SIEMENS_TENANT_ID, db)

        assert res.tenant_id == SIEMENS_TENANT_ID
        assert res.total_contracts_processed >= 4
        assert res.total_clauses_synthesized >= 1
        assert res.pre_risk_portfolio_average > res.post_risk_portfolio_average
        assert res.risk_reduction_percentage > 50.0  # Significant risk reduction
        assert len(res.sha256_batch_seal) == 64

        for item in res.remediation_items:
            assert item.pre_remediation_risk_score > item.post_remediation_risk_score
            assert len(item.remediated_clause_types) >= 1
            assert "Nachtragsvereinbarung" in item.synthesized_amendment_title


def test_certified_dora_register_pdf_generation():
    """
    Verifies PyMuPDF generation of official 3-page DIN 5008 BaFin & ESA Information Register Dossier.
    """
    entries = dora_register_engine._generate_canonical_portfolio(SIEMENS_TENANT_ID)
    from datetime import datetime

    from app.schemas.dora_register import DoraInformationRegister
    register = DoraInformationRegister(
        tenant_id=SIEMENS_TENANT_ID,
        reporting_entity_name="Siemens Financial Services AG",
        reporting_date=datetime.now().date(),
        reporting_lei="529900T8BM49AURSDO55",
        total_ict_contracts=len(entries),
        critical_ict_contracts=len(entries),
        overall_compliance_rate=75.0,
        entries=entries,
        esa_template_version="ESA JC 2024 05 / DORA Art. 28(3)",
        sha256_register_seal=uuid4().hex + uuid4().hex,
    )

    pdf_path = dora_register_engine.generate_dora_register_pdf(
        register=register,
        signatory_name="Dr. Hannelore Graf, Leiterin Compliance",
    )

    assert pdf_path.exists()
    assert pdf_path.suffix == ".pdf"
    assert pdf_path.stat().st_size > 1500


def test_esa_standardized_json_export():
    """
    Verifies JSON export adhering to ESA JC 2024 05 electronic reporting taxonomy.
    """
    entries = dora_register_engine._generate_canonical_portfolio(SIEMENS_TENANT_ID)
    from datetime import datetime

    from app.schemas.dora_register import DoraInformationRegister
    register = DoraInformationRegister(
        tenant_id=SIEMENS_TENANT_ID,
        reporting_entity_name="Siemens AG Financial",
        reporting_date=datetime.now().date(),
        reporting_lei="529900T8BM49AURSDO55",
        total_ict_contracts=len(entries),
        critical_ict_contracts=3,
        overall_compliance_rate=50.0,
        entries=entries,
        esa_template_version="ESA JC 2024 05 / DORA Art. 28(3)",
        sha256_register_seal="test_seal_hash",
    )

    payload = dora_register_engine.export_esa_json(register)
    assert "dora_register_header" in payload
    assert "table_b_01_arrangements" in payload
    assert "table_b_04_subcontracting_exit" in payload
    assert len(payload["table_b_01_arrangements"]) == len(entries)


def test_rest_dora_register_endpoints():
    """
    Verifies REST endpoints:
    1. GET /api/v1/dora-register/register
    2. GET /api/v1/dora-register/export-json
    3. GET /api/v1/dora-register/export-pdf
    4. POST /api/v1/dora-register/batch-remediation
    """
    client = TestClient(app)
    headers = {"X-Tenant-ID": str(SIEMENS_TENANT_ID)}

    # 1. GET /register
    res = client.get("/api/v1/dora-register/register", headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert "entries" in data
    assert data["total_ict_contracts"] >= 1
    assert "sha256_register_seal" in data

    # 2. GET /export-json
    json_res = client.get("/api/v1/dora-register/export-json", headers=headers)
    assert json_res.status_code == 200
    assert "dora_register_header" in json_res.json()
    assert "attachment" in json_res.headers.get("content-disposition", "")

    # 3. GET /export-pdf
    pdf_res = client.get("/api/v1/dora-register/export-pdf", headers=headers)
    assert pdf_res.status_code == 200
    assert pdf_res.headers["content-type"] == "application/pdf"
    assert "BAFIN_DORA_INFORMATIONSREGISTER" in pdf_res.headers.get("content-disposition", "")
    assert len(pdf_res.content) > 1500

    # 4. POST /batch-remediation
    batch_res = client.post("/api/v1/dora-register/batch-remediation", headers=headers)
    assert batch_res.status_code == 200
    batch_data = batch_res.json()
    assert batch_data["total_contracts_processed"] >= 1
    assert batch_data["risk_reduction_percentage"] > 0.0
    assert "sha256_batch_seal" in batch_data

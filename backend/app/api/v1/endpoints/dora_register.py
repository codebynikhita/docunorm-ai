"""
DocuNorm AI — Day 40: DORA Art. 28(3) Register of Information & Portfolio Batch Remediation REST Endpoints.
Conforms to ESA Final Draft ITS (JC 2024 05 / EBA/ITS/2024/01) and BaFin Circular 10/2026 mandates.
"""

from typing import Annotated

from fastapi import APIRouter, Depends, Response
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_session
from app.core.tenant import SIEMENS_TENANT_ID, get_current_tenant_id
from app.schemas.dora_register import BatchRemediationResult, DoraInformationRegister
from app.services.dora_register_engine import dora_register_engine

router = APIRouter(prefix="/dora-register", tags=["DORA Register of Information & Batch Remediation"])


@router.get(
    "/register",
    response_model=DoraInformationRegister,
    summary="Get Statutory DORA Art. 28(3) Register of Information",
)
async def get_dora_information_register(
    db: Annotated[AsyncSession, Depends(get_session)],
) -> DoraInformationRegister:
    """
    Returns the complete statutory DORA Art. 28(3) Register of Information for the current tenant partition,
    including criticality assessments, LEI codes, subcontractor cascading depth, and audit compliance.
    """
    tenant_id = get_current_tenant_id() or SIEMENS_TENANT_ID
    return await dora_register_engine.generate_register_for_tenant(tenant_id, db)


@router.get(
    "/export-json",
    summary="Export ESA Standardized JSON Register of Information",
)
async def export_esa_register_json(
    db: Annotated[AsyncSession, Depends(get_session)],
) -> JSONResponse:
    """
    Exports the statutory Information Register formatted to the European Supervisory Authorities
    (EBA / EIOPA / ESMA) JC 2024 05 electronic reporting taxonomy.
    """
    tenant_id = get_current_tenant_id() or SIEMENS_TENANT_ID
    register = await dora_register_engine.generate_register_for_tenant(tenant_id, db)
    payload = dora_register_engine.export_esa_json(register)

    headers = {
        "Content-Disposition": f'attachment; filename="ESA_DORA_REGISTER_{register.reporting_lei}.json"',
    }
    return JSONResponse(content=payload, headers=headers)


@router.get(
    "/export-pdf",
    summary="Export Certified DIN 5008 BaFin Information Register Dossier PDF",
)
async def export_dora_register_pdf(
    db: Annotated[AsyncSession, Depends(get_session)],
    signatory_name: str = "Dr. Johannes von Stauffenberg, Leitender Compliance-Jurist",
) -> Response:
    """
    Generates and downloads an official 3-page DIN 5008 BaFin & ESA Information Register Dossier
    (Informationsregister gem. Art. 28 Abs. 3 DORA) with cryptographic SHA-256 seal.
    """
    tenant_id = get_current_tenant_id() or SIEMENS_TENANT_ID
    register = await dora_register_engine.generate_register_for_tenant(tenant_id, db)
    pdf_path = dora_register_engine.generate_dora_register_pdf(register, signatory_name=signatory_name)

    with open(pdf_path, "rb") as f:
        pdf_bytes = f.read()

    clean_filename = f"BAFIN_DORA_INFORMATIONSREGISTER_{register.reporting_lei}.pdf"
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{clean_filename}"'},
    )


@router.post(
    "/batch-remediation",
    response_model=BatchRemediationResult,
    summary="Execute Portfolio-Wide Automated Contract Remediation",
)
async def execute_portfolio_batch_remediation(
    db: Annotated[AsyncSession, Depends(get_session)],
) -> BatchRemediationResult:
    """
    Performs automated batch remediation across all deficient contracts in the tenant portfolio,
    synthesizing compliant covenants for DORA Art. 30, BaFin RS 10/2026, and GDPR Art. 28,
    and returning verified pre vs. post portfolio risk metrics.
    """
    tenant_id = get_current_tenant_id() or SIEMENS_TENANT_ID
    return await dora_register_engine.execute_portfolio_batch_remediation(tenant_id, db)

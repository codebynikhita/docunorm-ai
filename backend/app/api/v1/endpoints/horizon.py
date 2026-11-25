"""
DocuNorm AI — Day 39: RegTech Horizon Scanner & Contract Drift REST Endpoints.
Monitors statutory shifts across DORA RTS, BaFin Circulars, EU AI Act, and EDPB rulings,
evaluating enterprise contracts against forthcoming enforcement deadlines.
"""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.core.db import get_session
from app.core.tenant import get_current_tenant_id
from app.models.document import Document, DocumentChunk
from app.schemas.horizon import ContractDriftReport, RegulatoryUpdate
from app.services.horizon_scanner import horizon_scanner

router = APIRouter(prefix="/horizon", tags=["RegTech Horizon Scanner & Contract Drift"])


@router.get(
    "/updates",
    response_model=list[RegulatoryUpdate],
    summary="List Active European & German Regulatory Horizon Updates",
)
async def list_regulatory_updates(
    authority: str | None = Query(default=None, description="Filter by issuing authority (e.g. BAFIN, EBA, EDPB)"),
) -> list[RegulatoryUpdate]:
    """
    Returns active regulatory updates and countdown to statutory enforcement deadlines
    across DORA, KWG § 25b, BaFin Rundschreiben, EU AI Act, and EDPB sovereignty rulings.
    """
    updates = horizon_scanner.get_active_updates()
    if authority:
        authority_upper = authority.strip().upper()
        updates = [u for u in updates if u.issuing_authority.upper() == authority_upper]
    return updates


@router.get(
    "/documents/{document_id}/drift-analysis",
    response_model=ContractDriftReport,
    summary="Get Contract Drift Analysis for Document",
)
@router.post(
    "/documents/{document_id}/drift-analysis",
    response_model=ContractDriftReport,
    summary="Analyze Contract Drift for Document",
)
async def get_contract_drift_analysis(
    document_id: UUID,
    db: Annotated[AsyncSession, Depends(get_session)],
) -> ContractDriftReport:
    """
    Evaluates contract clauses against the upcoming regulatory horizon, identifying
    compliance gaps, calculating drift scores, and determining retrofitting action requirements.
    """
    tenant_id = get_current_tenant_id()
    stmt = select(Document).where(Document.id == document_id)
    if tenant_id:
        stmt = stmt.where(Document.tenant_id == tenant_id)

    doc_res = await db.execute(stmt)
    document = doc_res.scalar_one_or_none()

    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document '{document_id}' not found.",
        )

    chunk_stmt = select(DocumentChunk).where(DocumentChunk.document_id == document_id)
    if tenant_id:
        chunk_stmt = chunk_stmt.where(DocumentChunk.tenant_id == tenant_id)

    chunk_stmt = chunk_stmt.order_by(DocumentChunk.chunk_index.asc())
    chunk_res = await db.execute(chunk_stmt)
    chunks = chunk_res.scalars().all()

    chunk_dicts = [
        {
            "id": str(c.id),
            "content": c.content,
            "page_number": c.page_number,
            "bounding_box": c.bounding_box or [0.0, 0.0, 100.0, 50.0],
        }
        for c in chunks
    ]

    return horizon_scanner.audit_contract_drift(
        document_id=document.id,
        document_filename=document.filename,
        chunks=chunk_dicts,
    )


@router.get(
    "/documents/{document_id}/export-drift-pdf",
    summary="Export Certified DIN 5008 Contract Drift Legal Opinion PDF",
)
async def export_contract_drift_pdf(
    document_id: UUID,
    db: Annotated[AsyncSession, Depends(get_session)],
    signatory_name: str = "Dr. Johannes von Stauffenberg, Leitender Compliance-Jurist",
) -> Response:
    """
    Generates and downloads an official DIN 5008 Legal Expert Opinion PDF
    (Rechtsgutachten zur aufsichtsrechtlichen Vertragskonformität und Horizont-Drift)
    with cryptographic SHA-256 seal.
    """
    tenant_id = get_current_tenant_id()
    stmt = select(Document).where(Document.id == document_id)
    if tenant_id:
        stmt = stmt.where(Document.tenant_id == tenant_id)

    doc_res = await db.execute(stmt)
    document = doc_res.scalar_one_or_none()

    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document '{document_id}' not found.",
        )

    chunk_stmt = select(DocumentChunk).where(DocumentChunk.document_id == document_id)
    if tenant_id:
        chunk_stmt = chunk_stmt.where(DocumentChunk.tenant_id == tenant_id)

    chunk_stmt = chunk_stmt.order_by(DocumentChunk.chunk_index.asc())
    chunk_res = await db.execute(chunk_stmt)
    chunks = chunk_res.scalars().all()

    chunk_dicts = [
        {
            "id": str(c.id),
            "content": c.content,
            "page_number": c.page_number,
            "bounding_box": c.bounding_box or [0.0, 0.0, 100.0, 50.0],
        }
        for c in chunks
    ]

    report = horizon_scanner.audit_contract_drift(
        document_id=document.id,
        document_filename=document.filename,
        chunks=chunk_dicts,
    )

    pdf_path = horizon_scanner.generate_drift_report_pdf(
        document_filename=document.filename,
        report=report,
        signatory_name=signatory_name,
    )

    clean_filename = f"GUTACHTEN_VERTRAGSDRIFT_{document.filename.replace('.pdf', '')}.pdf"

    with open(pdf_path, "rb") as f:
        pdf_bytes = f.read()

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{clean_filename}"'},
    )

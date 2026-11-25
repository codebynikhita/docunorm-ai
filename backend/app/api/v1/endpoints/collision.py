"""
DocuNorm AI — Cross-Regulatory Conflict & Jurisdictional Incompatibility REST Endpoints.
Provides normative collision analysis, stateless reconciliation, and certified legal opinion PDF export.
"""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.core.db import get_session
from app.core.tenant import get_current_tenant_id
from app.models.document import Document, DocumentChunk
from app.schemas.collision import (
    ClauseReconcileRequest,
    ClauseReconcileResponse,
    DocumentConflictMatrix,
)
from app.services.collision_engine import collision_engine

router = APIRouter(prefix="/collision", tags=["Regulatory Conflict & Incompatibility Matrix"])


@router.post(
    "/reconcile-clause",
    response_model=ClauseReconcileResponse,
    summary="Stateless Clause Collision Audit & Statutory Reconciliation Synthesis",
)
async def reconcile_clause_endpoint(payload: ClauseReconcileRequest) -> ClauseReconcileResponse:
    """
    Evaluates a single clause snippet for multi-standard collisions (DORA vs. CLOUD Act vs. GDPR vs. KWG)
    and synthesizes authoritative reconciliation covenants.
    """
    return collision_engine.reconcile_clause(payload)


@router.get(
    "/documents/{document_id}/matrix",
    response_model=DocumentConflictMatrix,
    summary="Get Regulatory Conflict Matrix for Document",
)
@router.post(
    "/documents/{document_id}/matrix",
    response_model=DocumentConflictMatrix,
    summary="Analyze Regulatory Conflict Matrix for Document",
)
async def get_document_collision_matrix(
    document_id: UUID,
    db: Annotated[AsyncSession, Depends(get_session)],
) -> DocumentConflictMatrix:
    """
    Performs comprehensive cross-regulatory collision analysis on document chunks,
    detecting normative deadlocks between EU regulations and foreign statutes.
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

    return collision_engine.analyze_conflicts(
        document_id=document.id,
        document_filename=document.filename,
        chunks=chunk_dicts,
    )


@router.get(
    "/documents/{document_id}/export-matrix-pdf",
    summary="Export Certified DIN 5008 Conflict Matrix Legal Opinion PDF",
)
async def export_collision_matrix_pdf(
    document_id: UUID,
    db: Annotated[AsyncSession, Depends(get_session)],
    signatory_name: str = "Dr. Johannes von Stauffenberg, Leitender Compliance-Jurist",
) -> Response:
    """
    Generates and downloads an official DIN 5008 Legal Expert Opinion PDF
    (Rechtsgutachten zur aufsichtsrechtlichen Kollisionsprüfung) with cryptographic SHA-256 seal.
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

    matrix = collision_engine.analyze_conflicts(
        document_id=document.id,
        document_filename=document.filename,
        chunks=chunk_dicts,
    )

    pdf_path = collision_engine.generate_collision_matrix_pdf(
        document_filename=document.filename,
        matrix=matrix,
        signatory_name=signatory_name,
    )

    clean_filename = f"GUTACHTEN_KOLLISIONSPRUEFUNG_{document.filename.replace('.pdf', '')}.pdf"

    with open(pdf_path, "rb") as f:
        pdf_bytes = f.read()

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{clean_filename}"'},
    )

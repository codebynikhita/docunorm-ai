"""
DocuNorm AI — Day 41: AI Contract Negotiation Simulator REST Endpoints.
Simulates multi-turn legal arguments and redlines between Enterprise Legal Counsel
and ICT Vendor Counsel, producing BaFin-compliant compromise covenants.
"""

from uuid import UUID

from fastapi import APIRouter, HTTPException, Response, status

from app.schemas.negotiation_sim import NegotiationSession, NegotiationStepRequest
from app.services.negotiation_simulator import negotiation_simulator

router = APIRouter(prefix="/negotiation-sim", tags=["AI Negotiation Simulator & Stresstest"])


@router.post(
    "/simulate",
    response_model=NegotiationSession,
    summary="Simulate Multi-Turn Contract Negotiation Rounds",
)
async def simulate_contract_negotiation(payload: NegotiationStepRequest) -> NegotiationSession:
    """
    Executes an autonomous multi-turn negotiation simulation between Enterprise Legal Counsel
    and Vendor Legal Counsel across complex regulatory topics (DORA, BaFin RS 10/2026, CLOUD Act),
    generating redline arguments and an audit-safe compromise covenant.
    """
    return negotiation_simulator.simulate_negotiation(payload)


@router.get(
    "/sessions/{session_id}",
    response_model=NegotiationSession,
    summary="Get Negotiation Session Details",
)
async def get_negotiation_session(session_id: UUID) -> NegotiationSession:
    """
    Retrieves the negotiation session details, transcript rounds, and final reconciled clause.
    """
    session = negotiation_simulator.get_session(session_id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Negotiation session '{session_id}' not found.",
        )
    return session


@router.get(
    "/sessions/{session_id}/export-protocol-pdf",
    summary="Export Certified DIN 5008 Negotiation Protocol PDF",
)
async def export_negotiation_protocol_pdf(
    session_id: UUID,
    signatory_name: str = "Dr. Johannes von Stauffenberg, Leitender Compliance-Jurist",
) -> Response:
    """
    Generates and downloads an official 2-page DIN 5008 Negotiation Dossier & Audit Protocol PDF
    (Aufsichtsrechtliches Verhandlungsprotokoll & Nachweisdokument) with cryptographic SHA-256 seal.
    """
    session = negotiation_simulator.get_session(session_id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Negotiation session '{session_id}' not found.",
        )

    pdf_path = negotiation_simulator.generate_negotiation_protocol_pdf(session, signatory_name=signatory_name)

    with open(pdf_path, "rb") as f:
        pdf_bytes = f.read()

    clean_filename = f"VERHANDLUNGSPROTOKOLL_{session.session_id.hex[:8]}.pdf"
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{clean_filename}"'},
    )

"""
REST API Endpoints for Enterprise Supply Chain Portfolio Aggregation &
BAFA Annual Statutory Due Diligence Reporting (§ 10 Abs. 2 LkSG).
"""

from typing import Annotated

from fastapi import APIRouter, Depends, Query, Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.core.db import get_session
from app.models.tenant import Tenant
from app.models.user import User, UserRole
from app.schemas.portfolio import BafaAnnualReportSynthesis
from app.services.bafa_annual_report_exporter import generate_bafa_annual_report_pdf
from app.services.portfolio_aggregator import portfolio_aggregator

router = APIRouter(prefix="/portfolio", tags=["Enterprise Portfolio Governance"])


async def get_or_create_default_tenant_and_user(
    db: AsyncSession,
) -> tuple[Tenant, User]:
    """Helper to ensure a valid tenant exists for portfolio operations."""
    stmt_tenant = select(Tenant).limit(1)
    res_tenant = await db.execute(stmt_tenant)
    tenant = res_tenant.scalar_one_or_none()

    if not tenant:
        tenant = Tenant(
            name="Default Sovereign Enterprise",
            domain="sovereign.local",
            is_active=True,
        )
        db.add(tenant)
        await db.commit()
        await db.refresh(tenant)

    stmt_user = select(User).where(User.tenant_id == tenant.id).limit(1)
    res_user = await db.execute(stmt_user)
    user = res_user.scalar_one_or_none()

    if not user:
        user = User(
            email="compliance.director@sovereign.local",
            hashed_password="not_used_local_mode",
            full_name="Chief Compliance Officer",
            role=UserRole.ADMIN,
            tenant_id=tenant.id,
            is_active=True,
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)

    return tenant, user


@router.get(
    "/lksg-summary",
    response_model=BafaAnnualReportSynthesis,
    summary="Get Multi-Contract Supply Chain Portfolio Aggregation (§ 10 LkSG)",
)
@router.post(
    "/lksg-summary",
    response_model=BafaAnnualReportSynthesis,
    summary="Calculate Multi-Contract Supply Chain Portfolio Aggregation (§ 10 LkSG)",
)
async def get_portfolio_lksg_summary(
    db: Annotated[AsyncSession, Depends(get_session)],
    reporting_year: int = Query(2026, description="Fiscal reporting year under § 10 LkSG"),
) -> BafaAnnualReportSynthesis:
    """
    Aggregates supply chain compliance metrics across all supplier contracts:
    1. Overall LkSG compliance score and institutional rating (AAA/BBB/CCC).
    2. Quantitative HHI concentration risk index.
    3. Global jurisdiction hazard exposures (ITUC, CPI, Basel Annex VII).
    4. Active substantiated knowledge alerts and CAPA remediation progress.
    """
    tenant, _ = await get_or_create_default_tenant_and_user(db)
    return await portfolio_aggregator.aggregate_portfolio(
        db=db,
        tenant_id=tenant.id,
        reporting_year=reporting_year,
    )


@router.get(
    "/export-bafa-annual-report-pdf",
    summary="Download Official DIN 5008 Annual BAFA Due Diligence Report PDF (§ 10 Abs. 2 LkSG)",
)
@router.post(
    "/export-bafa-annual-report-pdf",
    summary="Export Official DIN 5008 Annual BAFA Due Diligence Report PDF (§ 10 Abs. 2 LkSG)",
)
async def export_bafa_annual_report_pdf(
    db: Annotated[AsyncSession, Depends(get_session)],
    company_name: str = Query("DocuNorm Sovereign Banking Group AG", description="Legal entity name"),
    reporting_year: int = Query(2026, description="Fiscal reporting year"),
) -> Response:
    """
    Generates and streams an official 3-page DIN 5008 Annual Corporate Due Diligence Report
    under § 10 Abs. 2 LkSG with cryptographic SHA-256 seal and Board Attestation.
    """
    tenant, _ = await get_or_create_default_tenant_and_user(db)
    synthesis = await portfolio_aggregator.aggregate_portfolio(
        db=db,
        tenant_id=tenant.id,
        reporting_year=reporting_year,
    )

    pdf_path = generate_bafa_annual_report_pdf(
        synthesis=synthesis,
        company_name=company_name,
    )

    with open(pdf_path, "rb") as f:
        pdf_bytes = f.read()

    clean_filename = f"BAFA_JAHRESBERICHT_{reporting_year}_LKSG_10.pdf"

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{clean_filename}"'},
    )

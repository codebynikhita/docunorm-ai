"""
DocuNorm AI — Multi-Tenant Management & RLS Isolation REST Endpoints.
Provides client tenant introspection, tenant provisioning, and live GDPR/BaFin isolation audit checks.
"""

from typing import Annotated

from fastapi import APIRouter, Depends, Header, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_session
from app.core.tenant import get_current_tenant_id, set_current_tenant_id
from app.schemas.tenant import TenantCreate, TenantIsolationAuditReport, TenantRead
from app.services.tenant_service import tenant_service

router = APIRouter(prefix="/tenants", tags=["Multi-Tenancy & Client Isolation"])


@router.get(
    "",
    response_model=list[TenantRead],
    summary="List All Enterprise Tenants with Aggregated Document Metrics",
)
async def list_enterprise_tenants(
    db: Annotated[AsyncSession, Depends(get_session)],
) -> list[TenantRead]:
    """
    Returns all registered enterprise client tenants (e.g. Siemens AG, Deutsche Bank, Allianz, BMW)
    with total document and chunk counts.
    """
    return await tenant_service.list_tenants(db)


@router.post(
    "",
    response_model=TenantRead,
    status_code=status.HTTP_201_CREATED,
    summary="Provision a New Enterprise Client Tenant",
)
async def create_enterprise_tenant(
    payload: TenantCreate,
    db: Annotated[AsyncSession, Depends(get_session)],
) -> TenantRead:
    """
    Provisions a new isolated tenant partition in accordance with GDPR Art. 32.
    """
    return await tenant_service.create_tenant(db, payload)


@router.get(
    "/current",
    response_model=TenantRead,
    summary="Introspect Currently Active Request Tenant Context",
)
async def get_current_tenant_context(
    db: Annotated[AsyncSession, Depends(get_session)],
    x_tenant_id: Annotated[str | None, Header(description="Enterprise Tenant UUID or Slug")] = None,
) -> TenantRead:
    """
    Returns the tenant resolved for the current request (from X-Tenant-ID header or session context).
    """
    tenant_id = get_current_tenant_id()
    if x_tenant_id:
        resolved = await tenant_service.get_tenant_by_id_or_slug(db, x_tenant_id)
        if resolved:
            tenant_id = resolved.id

    tenant = await tenant_service.get_tenant_by_id_or_slug(db, tenant_id)
    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Tenant '{tenant_id}' not found.",
        )

    all_tenants = await tenant_service.list_tenants(db)
    for t in all_tenants:
        if t.id == tenant.id:
            return t

    return TenantRead(
        id=tenant.id,
        name=tenant.name,
        slug=tenant.slug,
        created_at=tenant.created_at,
        updated_at=tenant.updated_at,
        document_count=0,
        chunk_count=0,
    )


@router.get(
    "/isolation-audit",
    response_model=TenantIsolationAuditReport,
    summary="Execute Live Multi-Tenant Boundary Penetration & Isolation Audit",
)
async def run_tenant_isolation_audit(
    db: Annotated[AsyncSession, Depends(get_session)],
    x_tenant_id: Annotated[str | None, Header(description="Enterprise Tenant UUID or Slug")] = None,
) -> TenantIsolationAuditReport:
    """
    Executes a forensic penetration verification on the active tenant:
    - Verifies active database RLS mode (PostgreSQL Row-Level Security vs Sovereign App Partitioning).
    - Proves 0 cross-tenant data leakage between partitioned clients.
    - Emits BaFin KWG § 25b & GDPR Art. 32 compliance certification seal.
    """
    active_tenant_id = get_current_tenant_id()
    if x_tenant_id:
        resolved = await tenant_service.get_tenant_by_id_or_slug(db, x_tenant_id)
        if resolved:
            active_tenant_id = resolved.id

    return await tenant_service.run_isolation_leakage_audit(db, active_tenant_id)


@router.post(
    "/{tenant_id_or_slug}/switch",
    response_model=TenantRead,
    summary="Switch Active Context Tenant for Testing / Administrative Audits",
)
async def switch_tenant_context(
    tenant_id_or_slug: str,
    db: Annotated[AsyncSession, Depends(get_session)],
) -> TenantRead:
    """
    Switches the thread/asyncio context to the designated tenant.
    """
    tenant = await tenant_service.get_tenant_by_id_or_slug(db, tenant_id_or_slug)
    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Tenant '{tenant_id_or_slug}' not found.",
        )
    set_current_tenant_id(tenant.id)

    all_tenants = await tenant_service.list_tenants(db)
    for t in all_tenants:
        if t.id == tenant.id:
            return t

    return TenantRead(
        id=tenant.id,
        name=tenant.name,
        slug=tenant.slug,
        created_at=tenant.created_at,
        updated_at=tenant.updated_at,
        document_count=0,
        chunk_count=0,
    )

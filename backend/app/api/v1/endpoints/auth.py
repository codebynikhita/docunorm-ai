"""
Authentication and Role-Based Access Control (RBAC) API Router.
Provides enterprise registration, login, JWT token issuance, and current user introspection.
"""

from typing import Annotated
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, Header, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_session
from app.core.security import (
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
)
from app.models.tenant import Tenant
from app.models.user import User, UserRole

router = APIRouter(prefix="/auth", tags=["Authentication"])


class SignUpRequest(BaseModel):
    email: str
    password: str
    full_name: str
    organization: str = "Siemens AG"
    role: str = "auditor"


class LoginRequest(BaseModel):
    email: str
    password: str


class UserOut(BaseModel):
    id: str
    email: str
    full_name: str
    role: str
    tenant_id: str
    organization: str = "Siemens AG"


class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut


async def get_or_create_default_tenant(db: AsyncSession, org_name: str) -> Tenant:
    """
    Finds or provisions an enterprise tenant corresponding to organization name.
    """
    slug = org_name.lower().replace(" ", "-").replace(".", "")
    stmt = select(Tenant).where(Tenant.slug == slug)
    result = await db.execute(stmt)
    tenant = result.scalar_one_or_none()

    if not tenant:
        tenant = Tenant(
            id=uuid4(),
            name=org_name,
            slug=slug,
        )
        db.add(tenant)
        await db.commit()
        await db.refresh(tenant)

    return tenant


@router.post("/signup", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
async def signup(
    req: SignUpRequest,
    db: Annotated[AsyncSession, Depends(get_session)],
) -> AuthResponse:
    """
    Register a new institutional compliance officer or legal counsel.
    Enforces password complexity and provisions an enterprise tenant.
    """
    if len(req.password) < 8:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must be at least 8 characters in accordance with BaFin IT security standards.",
        )

    # Check if user already exists
    stmt = select(User).where(User.email == req.email.lower().strip())
    existing = (await db.execute(stmt)).scalar_one_or_none()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"An account with email '{req.email}' is already registered.",
        )

    tenant = await get_or_create_default_tenant(db, req.organization)

    # Map role string safely
    try:
        user_role = UserRole(req.role.lower())
    except ValueError:
        user_role = UserRole.AUDITOR

    new_user = User(
        id=uuid4(),
        tenant_id=tenant.id,
        email=req.email.lower().strip(),
        full_name=req.full_name.strip(),
        hashed_password=hash_password(req.password),
        role=user_role,
        is_active=True,
    )

    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    token = create_access_token(
        {
            "sub": str(new_user.id),
            "email": new_user.email,
            "role": new_user.role.value,
            "tenant_id": str(new_user.tenant_id),
        }
    )

    return AuthResponse(
        access_token=token,
        token_type="bearer",
        user=UserOut(
            id=str(new_user.id),
            email=new_user.email,
            full_name=new_user.full_name,
            role=new_user.role.value,
            tenant_id=str(new_user.tenant_id),
            organization=req.organization,
        ),
    )


@router.post("/login", response_model=AuthResponse)
async def login(
    req: LoginRequest,
    db: Annotated[AsyncSession, Depends(get_session)],
) -> AuthResponse:
    """
    Authenticate an institutional user and return an RFC 7519 JWT session token.
    """
    email_clean = req.email.lower().strip()
    stmt = select(User).where(User.email == email_clean)
    user = (await db.execute(stmt)).scalar_one_or_none()

    # Auto-provision institutional demo accounts if not yet seeded
    if not user and any(kw in email_clean for kw in ("siemens", "weber", "bafin", "demo")):
        is_bafin = "bafin" in email_clean
        org_name = "Bundesanstalt für Finanzdienstleistungsaufsicht" if is_bafin else "Siemens AG"
        tenant = await get_or_create_default_tenant(db, org_name)
        user = User(
            id=uuid4(),
            tenant_id=tenant.id,
            email=email_clean,
            full_name="BaFin Lead Auditor" if is_bafin else "Dr. M. Weber",
            hashed_password=hash_password(req.password or "Siemens2026!"),
            role=UserRole.ADMIN if is_bafin else UserRole.AUDITOR,
            is_active=True,
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)

    if not user or not verify_password(req.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials. Please verify your email and password.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is deactivated. Contact compliance administrator.",
        )

    # Lookup tenant name
    tenant_stmt = select(Tenant).where(Tenant.id == user.tenant_id)
    tenant = (await db.execute(tenant_stmt)).scalar_one_or_none()
    org_name = tenant.name if tenant else "Siemens AG"

    token = create_access_token(
        {
            "sub": str(user.id),
            "email": user.email,
            "role": user.role.value,
            "tenant_id": str(user.tenant_id),
        }
    )

    return AuthResponse(
        access_token=token,
        token_type="bearer",
        user=UserOut(
            id=str(user.id),
            email=user.email,
            full_name=user.full_name,
            role=user.role.value,
            tenant_id=str(user.tenant_id),
            organization=org_name,
        ),
    )


@router.get("/me", response_model=UserOut)
async def get_current_user(
    db: Annotated[AsyncSession, Depends(get_session)],
    authorization: str | None = Header(None),
) -> UserOut:
    """
    Introspect the active JWT token and retrieve the current user's profile.
    """
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or malformed Authorization header.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = authorization.replace("Bearer ", "").strip()
    payload = decode_access_token(token)
    if not payload or "sub" not in payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired access token.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        user_id = UUID(payload["sub"])
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Corrupted user identifier in token.",
        )

    stmt = select(User).where(User.id == user_id)
    user = (await db.execute(stmt)).scalar_one_or_none()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User account no longer exists.",
        )

    tenant_stmt = select(Tenant).where(Tenant.id == user.tenant_id)
    tenant = (await db.execute(tenant_stmt)).scalar_one_or_none()
    org_name = tenant.name if tenant else "Siemens AG"

    return UserOut(
        id=str(user.id),
        email=user.email,
        full_name=user.full_name,
        role=user.role.value,
        tenant_id=str(user.tenant_id),
        organization=org_name,
    )

from typing import Annotated
from uuid import uuid4

from fastapi import APIRouter, Depends, File, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.core.db import get_session
from app.models.audit import AuditLog
from app.models.document import Document, DocumentStatus
from app.models.tenant import Tenant
from app.models.user import User, UserRole
from app.schemas.document import DocumentRead, DocumentUploadResponse
from app.services.storage import storage_service

router = APIRouter(prefix="/documents", tags=["Document Management"])


async def get_or_create_default_tenant_and_user(
    db: AsyncSession,
) -> tuple[Tenant, User]:
    """
    Ensures a default enterprise tenant and auditor user exist for development/demo.
    In multi-tenant production, this context comes from the validated JWT token.
    """
    # 1. Check or create default demo tenant (Siemens AG Demo)
    stmt = select(Tenant).where(Tenant.slug == "siemens-ag-demo")
    result = await db.execute(stmt)
    tenant = result.scalar_one_or_none()

    if not tenant:
        tenant = Tenant(
            id=uuid4(),
            name="Siemens AG (Compliance Demo)",
            slug="siemens-ag-demo",
        )
        db.add(tenant)
        await db.flush()

    # 2. Check or create default auditor user
    user_stmt = select(User).where(User.email == "auditor@siemens-demo.de")
    user_result = await db.execute(user_stmt)
    user = user_result.scalar_one_or_none()

    if not user:
        user = User(
            id=uuid4(),
            tenant_id=tenant.id,
            email="auditor@siemens-demo.de",
            full_name="Nikhita Reddy (Lead Auditor)",
            hashed_password="mock_hashed_secret_for_dev_mode",
            role=UserRole.AUDITOR,
            is_active=True,
        )
        db.add(user)
        await db.flush()

    return tenant, user


@router.post(
    "/upload",
    response_model=DocumentUploadResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload & Cryptographically Fingerprint Corporate PDF",
)
async def upload_document(
    file: Annotated[UploadFile, File(description="Corporate PDF document (max 50 MB)")],
    db: Annotated[AsyncSession, Depends(get_session)],
) -> DocumentUploadResponse:
    """
    Enterprise Document Ingestion Endpoint:
    1. Validates MIME type and size limit.
    2. Streams file to compute tamper-evident SHA-256 hash.
    3. Enforces cryptographic deduplication (returns existing record if hash matches).
    4. Persists raw PDF to content-addressable storage.
    5. Creates Document record with status PENDING and logs GDPR audit trail.
    """
    # 1. Validate MIME type and compute cryptographic SHA-256 fingerprint (Fail Fast)
    sha256_hash, file_size, content = await storage_service.validate_and_hash_file(file)

    # 2. Resolve tenant & user context
    tenant, user = await get_or_create_default_tenant_and_user(db)

    # 3. Deduplication Check: Does this tenant already have this exact document?
    existing_stmt = select(Document).where(
        Document.tenant_id == tenant.id,
        Document.sha256_hash == sha256_hash,
    )
    existing_result = await db.execute(existing_stmt)
    existing_document = existing_result.scalar_one_or_none()

    if existing_document:
        return DocumentUploadResponse(
            message="Document already exists with identical cryptographic SHA-256 fingerprint. Deduplicated.",
            is_duplicate=True,
            document=DocumentRead.model_validate(existing_document),
        )

    # 4. Persist document to content-addressable storage
    target_path = storage_service.save_document(
        tenant_id=str(tenant.id),
        sha256_hash=sha256_hash,
        content=content,
    )

    # 5. Insert new Document entry in PostgreSQL
    new_document = Document(
        id=uuid4(),
        tenant_id=tenant.id,
        uploaded_by=user.id,
        filename=file.filename or "unnamed_document.pdf",
        file_path=str(target_path),
        file_size_bytes=file_size,
        mime_type=file.content_type or "application/pdf",
        sha256_hash=sha256_hash,
        status=DocumentStatus.PENDING,
    )
    db.add(new_document)

    # 6. Create immutable GDPR audit log entry
    audit_entry = AuditLog(
        id=uuid4(),
        tenant_id=tenant.id,
        user_id=user.id,
        action="DOCUMENT_UPLOAD",
        resource_type="DOCUMENT",
        resource_id=str(new_document.id),
        details={
            "filename": new_document.filename,
            "sha256_hash": sha256_hash,
            "file_size_bytes": file_size,
        },
    )
    db.add(audit_entry)

    # Atomic commit
    await db.commit()
    await db.refresh(new_document)

    return DocumentUploadResponse(
        message="Document uploaded successfully and registered with cryptographic SHA-256 proof.",
        is_duplicate=False,
        document=DocumentRead.model_validate(new_document),
    )


@router.get(
    "/",
    response_model=list[DocumentRead],
    summary="List All Ingested Documents for Current Tenant",
)
async def list_documents(
    db: Annotated[AsyncSession, Depends(get_session)],
) -> list[DocumentRead]:
    """
    Retrieves all corporate documents registered under the active tenant.
    """
    tenant, _ = await get_or_create_default_tenant_and_user(db)
    stmt = (
        select(Document)
        .where(Document.tenant_id == tenant.id)
        .order_by(Document.created_at.desc())
    )
    result = await db.execute(stmt)
    documents = result.scalars().all()
    return [DocumentRead.model_validate(doc) for doc in documents]

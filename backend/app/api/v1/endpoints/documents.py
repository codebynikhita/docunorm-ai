from typing import Annotated
from uuid import UUID, uuid4
from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.core.db import get_session
from app.models.audit import AuditLog
from app.models.document import Document, DocumentChunk, DocumentStatus
from app.models.tenant import Tenant
from app.models.user import User, UserRole
from app.schemas.document import (
    AuditCitation,
    AuditRequest,
    AuditResponse,
    DocumentRead,
    DocumentUploadResponse,
    SearchQuery,
    SearchResponse,
    SearchResultChunk,
)
from app.services.auditor import (
    build_audit_prompt,
    generate_llm_audit_finding,
    parse_citations_from_response,
    translate_chunks_to_english,
)
from app.services.embedding import embedding_service
from app.services.parser import PDFParserService
from app.services.privacy import privacy_firewall
from app.services.storage import storage_service
from app.services.validator import validate_pdf_metadata

router = APIRouter(prefix="/documents", tags=["Document Management"])
pdf_parser = PDFParserService()


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
    summary="Upload, Fingerprint & Automatically Parse Corporate PDF",
)
async def upload_document(
    file: Annotated[UploadFile, File(description="Corporate PDF document (max 50 MB)")],
    db: Annotated[AsyncSession, Depends(get_session)],
) -> DocumentUploadResponse:
    """
    Enterprise Document Ingestion Pipeline:
    1. Validates filename and size via validate_pdf_metadata (Fail Fast).
    2. Streams file to compute cryptographic SHA-256 fingerprint.
    3. Enforces cryptographic deduplication (returns existing record if hash matches).
    4. Persists raw PDF to content-addressable storage.
    5. Structural parsing via PyMuPDF (extracts pages, paragraphs, bounding boxes).
    6. Persists document record and atomic chunks into PostgreSQL.
    7. Logs immutable GDPR audit trail.
    """
    filename = file.filename or "unnamed_document.pdf"

    # 1. Validate MIME type and compute cryptographic SHA-256 fingerprint
    sha256_hash, file_size, content = await storage_service.validate_and_hash_file(file)

    # Validate business rules using our validator service
    try:
        validate_pdf_metadata(filename=filename, file_size_bytes=file_size)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e

    # 2. Resolve tenant & user context
    tenant, user = await get_or_create_default_tenant_and_user(db)

    # 3. Deduplication Check
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

    # 5. Structural PDF Parsing (Extract text and bounding-box coordinates)
    parse_result = pdf_parser.parse_pdf(target_path)

    # 6. Insert new Document entry in PostgreSQL
    new_document = Document(
        id=uuid4(),
        tenant_id=tenant.id,
        uploaded_by=user.id,
        filename=filename,
        file_path=str(target_path),
        file_size_bytes=file_size,
        mime_type=file.content_type or "application/pdf",
        sha256_hash=sha256_hash,
        total_pages=parse_result.total_pages,
        status=DocumentStatus.READY,
    )
    db.add(new_document)

    # 7. Insert extracted chunks with page numbers, bounding boxes, and embeddings
    total_pii_masked = 0
    for block in parse_result.blocks:
        anonymized = privacy_firewall.anonymize_text(block.text)
        if anonymized.has_pii:
            total_pii_masked += len(anonymized.entities)

        # Generate 1024-dimensional dense semantic embedding vector
        vector = embedding_service.generate_embedding(anonymized.sanitized_text)

        chunk = DocumentChunk(
            id=uuid4(),
            document_id=new_document.id,
            tenant_id=tenant.id,
            chunk_index=block.block_index,
            page_number=block.page_number,
            bounding_box=block.bounding_box,
            content=anonymized.sanitized_text,
            raw_content_masked=anonymized.has_pii,
            token_count=len(anonymized.sanitized_text.split()),
            embedding=vector,
        )
        db.add(chunk)

    # 8. Create immutable GDPR audit log entry
    audit_entry = AuditLog(
        id=uuid4(),
        tenant_id=tenant.id,
        user_id=user.id,
        action="DOCUMENT_INGEST",
        resource_type="DOCUMENT",
        resource_id=str(new_document.id),
        details={
            "filename": new_document.filename,
            "sha256_hash": sha256_hash,
            "file_size_bytes": file_size,
            "total_pages": parse_result.total_pages,
            "chunks_extracted": len(parse_result.blocks),
            "pii_entities_neutralized": total_pii_masked,
        },
    )
    db.add(audit_entry)

    # Atomic transaction commit
    await db.commit()
    await db.refresh(new_document)

    return DocumentUploadResponse(
        message=(
            f"Document uploaded and parsed successfully. "
            f"Extracted {len(parse_result.blocks)} chunks across {parse_result.total_pages} pages."
        ),
        is_duplicate=False,
        document=DocumentRead.model_validate(new_document),
    )


@router.get(
    "",
    response_model=list[DocumentRead],
    include_in_schema=False,
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


@router.get(
    "/{document_id}/chunks",
    summary="Retrieve Extracted Chunks & Bounding Boxes for Document",
)
async def get_document_chunks(
    document_id: UUID,
    db: Annotated[AsyncSession, Depends(get_session)],
) -> list[dict]:
    """
    Retrieves all atomic text chunks for a document including page numbers
    and visual bounding-box coordinates for frontend citation overlays.
    """
    tenant, _ = await get_or_create_default_tenant_and_user(db)

    stmt = (
        select(DocumentChunk)
        .where(
            DocumentChunk.document_id == document_id,
            DocumentChunk.tenant_id == tenant.id,
        )
        .order_by(DocumentChunk.page_number.asc(), DocumentChunk.chunk_index.asc())
    )
    result = await db.execute(stmt)
    chunks = result.scalars().all()

    if not chunks:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No chunks found for document '{document_id}'.",
        )

    return [
        {
            "id": str(c.id),
            "chunk_index": c.chunk_index,
            "page_number": c.page_number,
            "bounding_box": c.bounding_box,
            "content": c.content,
            "token_count": c.token_count,
        }
        for c in chunks
    ]


@router.get(
    "/{document_id}/translated-chunks",
    summary="Retrieve Extracted Chunks with Dynamic English Translation",
)
async def get_translated_chunks(
    document_id: UUID,
    db: Annotated[AsyncSession, Depends(get_session)],
) -> list[dict]:
    """
    Retrieves all text chunks of any document translated to English
    for the Dual-View / English Dossier reader.
    """
    tenant, _ = await get_or_create_default_tenant_and_user(db)

    stmt = (
        select(DocumentChunk)
        .where(
            DocumentChunk.document_id == document_id,
            DocumentChunk.tenant_id == tenant.id,
        )
        .order_by(DocumentChunk.page_number.asc(), DocumentChunk.chunk_index.asc())
    )
    result = await db.execute(stmt)
    chunks = result.scalars().all()

    if not chunks:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No chunks found for document '{document_id}'.",
        )

    raw_chunks = [
        {
            "id": str(c.id),
            "chunk_index": c.chunk_index,
            "page_number": c.page_number,
            "bounding_box": c.bounding_box,
            "content": c.content,
            "token_count": c.token_count,
        }
        for c in chunks
    ]

    return await translate_chunks_to_english(raw_chunks)


@router.get(
    "/{document_id}/file",
    summary="Stream Raw PDF Binary for Interactive Canvas Rendering",
)
async def get_document_file(
    document_id: UUID,
    db: Annotated[AsyncSession, Depends(get_session)],
) -> FileResponse:
    """
    Streams raw PDF binary to the frontend PDF.js canvas renderer.
    """
    tenant, _ = await get_or_create_default_tenant_and_user(db)

    stmt = select(Document).where(
        Document.id == document_id,
        Document.tenant_id == tenant.id,
    )
    result = await db.execute(stmt)
    document = result.scalar_one_or_none()

    if not document or not document.file_path or not Path(document.file_path).exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document file not found for ID '{document_id}'.",
        )

    return FileResponse(
        path=document.file_path,
        media_type=document.mime_type or "application/pdf",
        filename=document.filename,
    )


@router.post(
    "/{document_id}/search",
    response_model=SearchResponse,
    summary="Semantic Vector Search Over Document Chunks (pgvector)",
)
async def search_document(
    document_id: UUID,
    payload: SearchQuery,
    db: Annotated[AsyncSession, Depends(get_session)],
) -> SearchResponse:
    """
    High-performance semantic vector search powered by pgvector:
    1. Converts natural language question into 1024-dim dense vector.
    2. Executes cosine distance query in PostgreSQL (<=> operator).
    3. Returns top-k matching chunks with similarity scores and visual bounding boxes.
    """
    tenant, _ = await get_or_create_default_tenant_and_user(db)

    # 1. Generate 1024-dimensional query vector
    query_vector = embedding_service.generate_embedding(payload.query)

    # 2. Query PostgreSQL pgvector with cosine distance
    distance_expr = DocumentChunk.embedding.cosine_distance(query_vector).label(
        "distance"
    )
    stmt = (
        select(DocumentChunk, distance_expr)
        .where(
            DocumentChunk.document_id == document_id,
            DocumentChunk.tenant_id == tenant.id,
            DocumentChunk.embedding.is_not(None),
        )
        .order_by(distance_expr.asc())
        .limit(payload.limit)
    )
    result = await db.execute(stmt)
    rows = result.all()

    matches: list[SearchResultChunk] = []
    for chunk, distance in rows:
        # Distance is in range [0, 2]. Cosine similarity = 1 - distance
        similarity = round(max(0.0, 1.0 - float(distance)), 4)
        matches.append(
            SearchResultChunk(
                chunk_id=chunk.id,
                document_id=chunk.document_id,
                page_number=chunk.page_number,
                bounding_box=chunk.bounding_box,
                content=chunk.content,
                similarity_score=similarity,
            )
        )

    return SearchResponse(
        query=payload.query,
        document_id=document_id,
        total_results=len(matches),
        results=matches,
    )


@router.post(
    "/{document_id}/audit",
    response_model=AuditResponse,
    summary="Execute Zero-Hallucination Regulatory Compliance Audit",
)
async def audit_document(
    document_id: UUID,
    payload: AuditRequest,
    db: Annotated[AsyncSession, Depends(get_session)],
) -> AuditResponse:
    """
    Executes a grounded regulatory compliance audit:
    1. Vector search in PostgreSQL for semantically relevant chunks.
    2. Builds anti-hallucination prompt citing [SOURCE_X].
    3. Synthesizes finding with exact page and visual bounding-box coordinates.
    4. Logs GDPR compliant audit trail.
    """
    tenant, user = await get_or_create_default_tenant_and_user(db)

    # 0. Self-healing: if document has 0 chunks, parse and ingest on-the-fly
    count_stmt = select(DocumentChunk).where(DocumentChunk.document_id == document_id)
    existing_chunks = (await db.execute(count_stmt)).scalars().all()

    if not existing_chunks:
        doc_stmt = select(Document).where(Document.id == document_id)
        target_doc = (await db.execute(doc_stmt)).scalar_one_or_none()
        if target_doc and target_doc.file_path and Path(target_doc.file_path).exists():
            parse_res = pdf_parser.parse_pdf(target_doc.file_path)
            for blk in parse_res.blocks:
                anon = privacy_firewall.anonymize_text(blk.text)
                vec = embedding_service.generate_embedding(anon.sanitized_text)
                c = DocumentChunk(
                    id=uuid4(),
                    document_id=target_doc.id,
                    tenant_id=tenant.id,
                    chunk_index=blk.block_index,
                    page_number=blk.page_number,
                    bounding_box=blk.bounding_box,
                    content=anon.sanitized_text,
                    raw_content_masked=anon.has_pii,
                    token_count=len(anon.sanitized_text.split()),
                    embedding=vec,
                )
                db.add(c)
            await db.flush()
    else:
        # Backfill any null embeddings
        for c in existing_chunks:
            if c.embedding is None:
                c.embedding = embedding_service.generate_embedding(c.content)
        await db.flush()

    # 1. Retrieve top matching chunks via pgvector
    query_vector = embedding_service.generate_embedding(payload.query)
    distance_expr = DocumentChunk.embedding.cosine_distance(query_vector).label("distance")

    stmt = (
        select(DocumentChunk, distance_expr)
        .where(
            DocumentChunk.document_id == document_id,
            DocumentChunk.tenant_id == tenant.id,
            DocumentChunk.embedding.is_not(None),
        )
        .order_by(distance_expr.asc())
        .limit(3)
    )
    result = await db.execute(stmt)
    rows = result.all()

    if not rows:
        return AuditResponse(
            document_id=document_id,
            query=payload.query,
            framework=payload.framework,
            status="INCONCLUSIVE",
            finding_summary="No relevant clauses found in the document for the specified query.",
            citations=[],
        )

    # 2. Prepare chunk mapping for auditor citations
    retrieved_chunks = []
    chunk_map: dict[str, dict] = {}

    for idx, (chunk, _) in enumerate(rows, start=1):
        source_key = f"SOURCE_{idx}"
        chunk_data = {
            "chunk_id": str(chunk.id),
            "page_number": chunk.page_number,
            "bounding_box": chunk.bounding_box or [50.0, 100.0, 500.0, 160.0],
            "content": chunk.content,
        }
        retrieved_chunks.append(chunk_data)
        chunk_map[source_key] = chunk_data

    # 3. Generate grounded regulatory LLM finding (Gemini 1.5 with deterministic fallback)
    finding_summary = await generate_llm_audit_finding(
        query=payload.query,
        retrieved_chunks=retrieved_chunks,
        framework=payload.framework,
    )

    # 4. Extract citations and bounding boxes
    parsed_citations = parse_citations_from_response(finding_summary, chunk_map)

    citations = [
        AuditCitation(
            source_tag=c["source_tag"],
            chunk_id=c.get("chunk_id"),
            page_number=c["page_number"],
            bounding_box=c["bounding_box"],
            content=c.get("content"),
        )
        for c in parsed_citations
    ]

    # 6. Log immutable GDPR audit record
    audit_entry = AuditLog(
        id=uuid4(),
        tenant_id=tenant.id,
        user_id=user.id,
        action="DOCUMENT_AUDITED",
        resource_type="DOCUMENT",
        resource_id=str(document_id),
        details={
            "query": payload.query,
            "framework": payload.framework,
            "citations_count": len(citations),
        },
    )
    db.add(audit_entry)
    await db.commit()

    return AuditResponse(
        document_id=document_id,
        query=payload.query,
        framework=payload.framework,
        status="COMPLIANT",
        finding_summary=finding_summary,
        citations=citations,
    )


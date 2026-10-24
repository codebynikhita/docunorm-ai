import json
import logging
from pathlib import Path
from uuid import UUID, uuid4

from redis.asyncio import Redis
from sqlalchemy import select

from app.core.config import get_settings
from app.core.db import async_session_factory
from app.models.audit import AuditLog
from app.models.document import Document, DocumentChunk, DocumentStatus
from app.services.embedding import embedding_service
from app.services.parser import PDFParserService
from app.services.privacy import privacy_firewall

logger = logging.getLogger(__name__)
settings = get_settings()
pdf_parser = PDFParserService()


def get_redis_client() -> Redis:
    """
    Acquire asynchronous Redis client connection using application settings.
    """
    return Redis(
        host=settings.REDIS_HOST,
        port=settings.REDIS_PORT,
        decode_responses=True,
    )


async def set_task_progress(
    document_id: UUID,
    status: str,
    progress: int,
    stage: str,
    error: str | None = None,
) -> None:
    """
    Record real-time document ingestion stage and percentage progress in Redis.
    Expires after 3600 seconds (1 hour).
    """
    try:
        redis = get_redis_client()
        payload = {
            "document_id": str(document_id),
            "status": status,
            "progress": progress,
            "stage": stage,
            "error": error,
        }
        await redis.set(f"doc:task:{document_id}", json.dumps(payload), ex=3600)
        await redis.aclose()
    except Exception as e:
        logger.warning(f"Could not persist task progress to Redis: {e}")


async def get_task_progress(document_id: UUID) -> dict[str, str | int | None]:
    """
    Retrieve real-time ingestion progress from Redis.
    Falls back to a default status if Redis key is missing.
    """
    try:
        redis = get_redis_client()
        raw = await redis.get(f"doc:task:{document_id}")
        await redis.aclose()
        if raw:
            return json.loads(raw)
    except Exception as e:
        logger.warning(f"Could not read task progress from Redis: {e}")

    return {
        "document_id": str(document_id),
        "status": "unknown",
        "progress": 0,
        "stage": "pending",
        "error": None,
    }


async def process_document_background(
    document_id: UUID,
    target_path: Path,
    tenant_id: UUID,
    user_id: UUID,
) -> None:
    """
    Asynchronous Enterprise Document Ingestion Task.
    Executes in background worker queue to prevent blocking the HTTP server thread:
    1. Extracts PDF structure and bounding boxes (millimeter coordinate ruler).
    2. Executes BDSG/GDPR Privacy Shield (Microsoft Presidio PII anonymization).
    3. Computes 1024-dimensional dense semantic vectors (pgvector).
    4. Records immutable German audit log and flips DocumentStatus to READY.
    """
    logger.info(f"🚀 [BackgroundTask] Starting background ingestion for document: {document_id}")
    await set_task_progress(document_id, "processing", 15, "parsing_pdf_geometry")

    try:
        # Step 1: Structural PDF Parsing
        parse_result = pdf_parser.parse_pdf(target_path)
        total_blocks = len(parse_result.blocks)
        logger.info(
            f"📄 [BackgroundTask] Extracted {total_blocks} blocks across {parse_result.total_pages} pages."
        )

        await set_task_progress(
            document_id,
            "processing",
            35,
            f"redacting_pii_across_{total_blocks}_paragraphs",
        )

        # Step 2: Anonymization & Embedding Vector Generation
        chunks_to_insert: list[DocumentChunk] = []
        total_pii_masked = 0

        for idx, block in enumerate(parse_result.blocks):
            # BDSG/GDPR Anonymization
            anonymized = privacy_firewall.anonymize_text(block.text)
            if anonymized.has_pii:
                total_pii_masked += len(anonymized.entities)

            # 1024-dim dense embedding
            vector = embedding_service.generate_embedding(anonymized.sanitized_text)

            chunk = DocumentChunk(
                id=uuid4(),
                document_id=document_id,
                tenant_id=tenant_id,
                chunk_index=block.block_index,
                page_number=block.page_number,
                bounding_box=block.bounding_box,
                content=anonymized.sanitized_text,
                raw_content_masked=anonymized.has_pii,
                token_count=len(anonymized.sanitized_text.split()),
                embedding=vector,
            )
            chunks_to_insert.append(chunk)

            # Update incremental progress every 10 blocks
            if idx % 10 == 0 or idx == total_blocks - 1:
                pct = int(35 + (idx / max(total_blocks, 1)) * 40)
                await set_task_progress(
                    document_id,
                    "processing",
                    pct,
                    f"embedding_paragraph_{idx + 1}_of_{total_blocks}",
                )

        await set_task_progress(document_id, "processing", 85, "persisting_to_pgvector")

        # Step 3: Database Persistence in dedicated session
        async with async_session_factory() as db:
            # Query document record
            doc_stmt = select(Document).where(Document.id == document_id)
            doc_res = await db.execute(doc_stmt)
            doc = doc_res.scalar_one_or_none()

            if doc:
                doc.total_pages = parse_result.total_pages
                doc.status = DocumentStatus.READY
                db.add(doc)

            # Insert chunks in batch
            for chunk in chunks_to_insert:
                db.add(chunk)

            # Create immutable GDPR audit record
            audit_entry = AuditLog(
                id=uuid4(),
                tenant_id=tenant_id,
                user_id=user_id,
                action="DOCUMENT_INGEST_ASYNC",
                resource_type="DOCUMENT",
                resource_id=str(document_id),
                details={
                    "total_pages": parse_result.total_pages,
                    "chunks_extracted": total_blocks,
                    "pii_entities_neutralized": total_pii_masked,
                    "mode": "async_background_task",
                },
            )
            db.add(audit_entry)

            await db.commit()

        await set_task_progress(document_id, "ready", 100, "ingestion_complete")
        logger.info(f"✅ [BackgroundTask] Successfully completed ingestion for document: {document_id}")

    except Exception as exc:
        logger.error(f"❌ [BackgroundTask] Failed ingestion for document {document_id}: {exc}", exc_info=True)
        await set_task_progress(
            document_id,
            "failed",
            0,
            "error_during_ingestion",
            error=str(exc),
        )
        async with async_session_factory() as db:
            doc_stmt = select(Document).where(Document.id == document_id)
            doc_res = await db.execute(doc_stmt)
            doc = doc_res.scalar_one_or_none()
            if doc:
                doc.status = DocumentStatus.FAILED
                db.add(doc)
                await db.commit()

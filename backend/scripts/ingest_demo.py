import asyncio
import os
import sys
from pathlib import Path

# Add backend directory to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.core.db import async_session_factory
from app.api.v1.endpoints.documents import get_or_create_default_tenant_and_user
from app.models.document import Document, DocumentChunk, DocumentStatus
from app.models.audit import AuditLog
from app.services.storage import storage_service
from app.services.validator import validate_pdf_metadata
from app.services.parser import PDFParserService
from app.services.privacy import privacy_firewall
from app.services.embedding import embedding_service
from uuid import uuid4
from sqlmodel import select

async def ingest_demo_file():
    pdf_path = "/Users/nikhitagp/.gemini/antigravity/scratch/docunorm-ai/Siemens_Master_IKT_Vertrag_2026.pdf"
    if not os.path.exists(pdf_path):
        print(f"File not found: {pdf_path}")
        return

    with open(pdf_path, "rb") as f:
        file_bytes = f.read()

    filename = "Siemens_Master_IKT_Vertrag_2026.pdf"
    
    async with async_session_factory() as db:
        tenant, user = await get_or_create_default_tenant_and_user(db)
        
        # Check if already ingested
        stmt = select(Document).where(Document.filename == filename, Document.tenant_id == tenant.id)
        result = await db.execute(stmt)
        existing = result.scalar_one_or_none()
        if existing:
            print(f"Document '{filename}' already exists in DB with ID: {existing.id}")
            return existing.id

        # Validate
        import hashlib
        sha256_hash = hashlib.sha256(file_bytes).hexdigest()
        file_path_obj = storage_service.save_document(
            tenant_id=tenant.id,
            sha256_hash=sha256_hash,
            content=file_bytes,
        )
        parser = PDFParserService()
        parse_result = parser.parse_pdf(file_path_obj)
        file_path = str(file_path_obj)

        new_doc = Document(
            id=uuid4(),
            tenant_id=tenant.id,
            uploaded_by=user.id,
            filename=filename,
            file_path=file_path,
            file_size_bytes=len(file_bytes),
            sha256_hash=sha256_hash,
            total_pages=parse_result.total_pages,
            status=DocumentStatus.READY,
        )
        db.add(new_doc)
        await db.flush()

        chunks_to_embed = []
        for idx, block in enumerate(parse_result.blocks):
            res = privacy_firewall.anonymize_text(block.text)
            chunk = DocumentChunk(
                id=uuid4(),
                document_id=new_doc.id,
                tenant_id=tenant.id,
                chunk_index=idx,
                page_number=block.page_number,
                bounding_box=block.bounding_box,
                content=res.sanitized_text,
                pii_masked=res.has_pii,
            )
            db.add(chunk)
            chunks_to_embed.append(chunk)

        # Generate vectors
        if chunks_to_embed:
            texts = [c.content for c in chunks_to_embed]
            vectors = [embedding_service.generate_embedding(t) for t in texts]
            for c, vec in zip(chunks_to_embed, vectors):
                c.embedding = vec

        await db.commit()
        print(f"Successfully ingested German Enterprise Demo '{filename}' with ID: {new_doc.id}")
        return new_doc.id

if __name__ == "__main__":
    asyncio.run(ingest_demo_file())

import asyncio
import json
import os
import re
from collections.abc import AsyncGenerator
from pathlib import Path
from uuid import UUID, uuid4

import httpx
from fastapi import Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.models.audit import AuditLog
from app.models.document import Document, DocumentChunk
from app.services.auditor import (
    build_audit_prompt,
    build_fallback_synthesis,
    parse_citations_from_response,
)
from app.services.embedding import embedding_service
from app.services.parser import PDFParserService
from app.services.privacy import privacy_firewall

pdf_parser = PDFParserService()


async def stream_audit_response(
    document_id: UUID,
    query: str,
    framework: str,
    lang: str,
    history: list[dict] | None,
    tenant_id: UUID,
    user_id: UUID,
    db: AsyncSession,
    request: Request | None = None,
) -> AsyncGenerator[str, None]:
    """
    Streams regulatory audit findings token-by-token via Server-Sent Events (SSE).
    Supports client-side AbortController cancellation via request.is_disconnected().
    Emits structured events:
      - 'status': retrieval and model readiness telemetry
      - 'token': real-time token/word payloads
      - 'citations': extracted [SOURCE_X] citations with page & bounding box data
      - 'done': full response aggregation, token count, and performance telemetry
      - 'aborted': early cancellation notification
    """
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
                    tenant_id=tenant_id,
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

    # 1. Retrieve top matching chunks via dense embeddings
    effective_search_query = query
    if history:
        past_user_queries = [h.get("text", "") for h in history if h.get("role") == "user" and h.get("text", "").strip()]
        if past_user_queries:
            last_query = past_user_queries[-1]
            q_tokens = query.lower().split()
            is_followup = (
                len(q_tokens) < 10
                or any(w in query.lower() for w in [
                    "and", "und", "what about", "wie steht", "gilt", "wer", "who", "cost", "kosten",
                    "strafe", "penalty", "support", "unterstützung", "migration", "frist", "period",
                    "zweite", "second", "erklär", "explain", "detail", "sub", "unterauftrag"
                ])
            )
            if is_followup:
                effective_search_query = f"{last_query} {query}"

    query_vector = embedding_service.generate_embedding(effective_search_query)

    is_sqlite = True
    try:
        bind = db.get_bind()
        if bind and bind.dialect.name != "sqlite":
            is_sqlite = False
    except Exception:
        is_sqlite = True

    if is_sqlite:
        stmt = (
            select(DocumentChunk)
            .where(
                DocumentChunk.document_id == document_id,
                DocumentChunk.tenant_id == tenant_id,
                DocumentChunk.embedding.is_not(None),
            )
        )
        result = await db.execute(stmt)
        all_chunks = result.scalars().all()
        scored_chunks = []
        for c in all_chunks:
            if c.embedding:
                try:
                    sim = embedding_service.cosine_similarity(query_vector, c.embedding)
                    scored_chunks.append((c, 1.0 - sim))
                except Exception:
                    continue
        scored_chunks.sort(key=lambda x: x[1])
        rows = scored_chunks[:8]
    else:
        distance_expr = DocumentChunk.embedding.cosine_distance(query_vector).label("distance")
        stmt = (
            select(DocumentChunk, distance_expr)
            .where(
                DocumentChunk.document_id == document_id,
                DocumentChunk.tenant_id == tenant_id,
                DocumentChunk.embedding.is_not(None),
            )
            .order_by(distance_expr.asc())
            .limit(8)
        )
        result = await db.execute(stmt)
        rows = result.all()

    if not rows:
        inconclusive_msg = (
            "Es wurden keine relevanten Vertragsklauseln zu Ihrer Anfrage gefunden."
            if lang == "DE"
            else "No relevant clauses found in the document for the specified query."
        )
        yield f"event: status\ndata: {json.dumps({'stage': 'empty', 'message': inconclusive_msg})}\n\n"
        yield f"event: token\ndata: {json.dumps({'token': inconclusive_msg})}\n\n"
        yield f"event: citations\ndata: {json.dumps({'citations': []})}\n\n"
        yield f"event: done\ndata: {json.dumps({'full_text': inconclusive_msg, 'tokens_count': 1, 'citations_count': 0})}\n\n"
        return

    # 2. Build retrieved chunks mapping for citations
    retrieved_chunks = []
    chunk_map: dict[str, dict] = {}
    seen_chunk_ids = set()

    for (chunk, _) in rows:
        if str(chunk.id) in seen_chunk_ids:
            continue
        seen_chunk_ids.add(str(chunk.id))
        source_key = f"SOURCE_{len(retrieved_chunks) + 1}"
        chunk_data = {
            "chunk_id": str(chunk.id),
            "page_number": chunk.page_number,
            "bounding_box": chunk.bounding_box or [50.0, 100.0, 500.0, 160.0],
            "content": chunk.content,
        }
        retrieved_chunks.append(chunk_data)
        chunk_map[source_key] = chunk_data

    # Contextual expansion: sibling chunks from the same page
    top_pages = {c["page_number"] for c in retrieved_chunks[:3]}
    if top_pages and len(retrieved_chunks) < 14:
        sibling_stmt = (
            select(DocumentChunk)
            .where(
                DocumentChunk.document_id == document_id,
                DocumentChunk.tenant_id == tenant_id,
                DocumentChunk.page_number.in_(top_pages),
            )
            .order_by(DocumentChunk.chunk_index.asc())
            .limit(25)
        )
        sibling_res = await db.execute(sibling_stmt)
        for sibling in sibling_res.scalars().all():
            if str(sibling.id) not in seen_chunk_ids and len(retrieved_chunks) < 14:
                seen_chunk_ids.add(str(sibling.id))
                source_key = f"SOURCE_{len(retrieved_chunks) + 1}"
                chunk_data = {
                    "chunk_id": str(sibling.id),
                    "page_number": sibling.page_number,
                    "bounding_box": sibling.bounding_box or [50.0, 100.0, 500.0, 160.0],
                    "content": sibling.content,
                }
                retrieved_chunks.append(chunk_data)
                chunk_map[source_key] = chunk_data

    # Emit initial retrieval status event
    yield f"event: status\ndata: {json.dumps({'stage': 'retrieved', 'chunks_count': len(retrieved_chunks), 'framework': framework})}\n\n"

    prompt = build_audit_prompt(query, retrieved_chunks, framework=framework, lang=lang, history=history)

    # 3. Stream tokens (Live Gemini SSE if key configured, otherwise Sovereign Token Streamer)
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        try:
            from app.core.config import get_settings
            settings = get_settings()
            api_key = getattr(settings, "GEMINI_API_KEY", None)
        except Exception:
            api_key = None

    accumulated_text = ""
    token_count = 0
    is_aborted = False

    streamed_successfully = False
    if api_key and api_key != "your_gemini_api_key_here":
        models_to_try = [
            os.getenv("GEMINI_MODEL", "gemini-2.5-flash"),
            "gemini-2.5-flash",
            "gemini-2.5-flash-lite",
            "gemini-1.5-flash",
        ]
        for model_name in models_to_try:
            if streamed_successfully:
                break
            try:
                stream_url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:streamGenerateContent?alt=sse&key={api_key}"
                payload = {
                    "contents": [{"parts": [{"text": prompt}]}],
                    "generationConfig": {
                        "temperature": 0.1,
                        "maxOutputTokens": 800,
                    },
                }
                async with httpx.AsyncClient(timeout=30.0) as client:
                    async with client.stream("POST", stream_url, json=payload) as response:
                        if response.status_code == 200:
                            async for line in response.aiter_lines():
                                # Check client cancellation on each chunk
                                if request and await request.is_disconnected():
                                    is_aborted = True
                                    yield f"event: aborted\ndata: {json.dumps({'reason': 'client_disconnected', 'tokens_count': token_count})}\n\n"
                                    break

                                if line.startswith("data: "):
                                    chunk_json_str = line[6:].strip()
                                    if not chunk_json_str:
                                        continue
                                    try:
                                        chunk_obj = json.loads(chunk_json_str)
                                        candidates = chunk_obj.get("candidates", [])
                                        if candidates:
                                            parts = candidates[0].get("content", {}).get("parts", [])
                                            for part in parts:
                                                token_text = part.get("text", "")
                                                if token_text:
                                                    accumulated_text += token_text
                                                    token_count += len(token_text.split()) or 1
                                                    yield f"event: token\ndata: {json.dumps({'token': token_text})}\n\n"
                                                    streamed_successfully = True
                                    except Exception:
                                        continue

                            if is_aborted:
                                break
            except Exception:
                continue

    # Fallback to Sovereign Token-Level Streamer if remote stream was empty or unconfigured
    if not streamed_successfully and not is_aborted:
        yield f"event: status\ndata: {json.dumps({'stage': 'sovereign_inference', 'engine': 'Sovereign-Forensic-Streamer'})}\n\n"
        fallback_text = build_fallback_synthesis(
            query,
            retrieved_chunks,
            framework=framework,
            lang=lang,
            history=history,
        )

        # Tokenize by words and punctuation to produce human-paced SSE streaming
        tokens = re.findall(r"\S+|\n+", fallback_text)
        for idx, tok in enumerate(tokens):
            if request and await request.is_disconnected():
                is_aborted = True
                yield f"event: aborted\ndata: {json.dumps({'reason': 'client_disconnected', 'tokens_count': token_count})}\n\n"
                break

            suffix = "" if (tok.startswith("\n") or idx == len(tokens) - 1) else " "
            chunk_token = tok + suffix
            accumulated_text += chunk_token
            token_count += 1

            yield f"event: token\ndata: {json.dumps({'token': chunk_token})}\n\n"
            # Natural human reading speed (12-18ms per token)
            await asyncio.sleep(0.016)

    # 4. Extract citations and emit completion telemetry
    citations = parse_citations_from_response(accumulated_text, chunk_map)
    yield f"event: citations\ndata: {json.dumps({'citations': citations})}\n\n"

    done_payload = {
        "full_text": accumulated_text,
        "tokens_count": token_count,
        "citations_count": len(citations),
        "aborted": is_aborted,
    }
    yield f"event: done\ndata: {json.dumps(done_payload)}\n\n"

    # 5. Log immutable GDPR audit record
    try:
        audit_entry = AuditLog(
            id=uuid4(),
            tenant_id=tenant_id,
            user_id=user_id,
            action="DOCUMENT_AUDITED_STREAM",
            resource_type="DOCUMENT",
            resource_id=str(document_id),
            details={
                "query": query,
                "framework": framework,
                "citations_count": len(citations),
                "tokens_count": token_count,
                "aborted": is_aborted,
            },
        )
        db.add(audit_entry)
        await db.commit()
    except Exception as log_err:
        print(f"Warning: Failed to persist streaming audit log: {log_err}")

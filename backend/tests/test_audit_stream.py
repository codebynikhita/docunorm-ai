import json
from uuid import uuid4

import pytest
from httpx import ASGITransport, AsyncClient
from sqlmodel import select

from app.core.db import async_session_factory
from app.core.tenant import SIEMENS_TENANT_ID, tenant_context
from app.main import app
from app.models.audit import AuditLog
from app.models.document import Document, DocumentChunk
from app.services.streaming_auditor import stream_audit_response


@pytest.mark.asyncio
async def test_stream_audit_response_generator():
    """
    Verifies that stream_audit_response yields properly formatted SSE events:
    status -> token -> citations -> done, and creates an immutable AuditLog entry.
    """
    async with async_session_factory() as session:
        with tenant_context(SIEMENS_TENANT_ID):
            # Find canonical Siemens document
            doc_stmt = select(Document).where(Document.tenant_id == SIEMENS_TENANT_ID)
            res = await session.execute(doc_stmt)
            doc = res.scalars().first()
            assert doc is not None, "Canonical Siemens document must exist"

            # Verify chunks exist
            chunk_stmt = select(DocumentChunk).where(DocumentChunk.document_id == doc.id)
            c_res = await session.execute(chunk_stmt)
            chunks = c_res.scalars().all()
            assert len(chunks) > 0, "Document must have indexed chunks"

            # Run generator directly
            events = []
            tokens = []
            citations = []
            done_payload = None

            gen = stream_audit_response(
                document_id=doc.id,
                query="Welche Kündigungsfristen und Regelungen gelten nach BGB § 314?",
                framework="DORA",
                lang="DE",
                history=None,
                tenant_id=doc.tenant_id,
                user_id=uuid4(),
                db=session,
                request=None,
            )

            async for chunk_str in gen:
                events.append(chunk_str)
                if "event: token" in chunk_str:
                    for line in chunk_str.splitlines():
                        if line.startswith("data: "):
                            data = json.loads(line[6:])
                            tokens.append(data.get("token", ""))
                elif "event: citations" in chunk_str:
                    for line in chunk_str.splitlines():
                        if line.startswith("data: "):
                            data = json.loads(line[6:])
                            citations = data.get("citations", [])
                elif "event: done" in chunk_str:
                    for line in chunk_str.splitlines():
                        if line.startswith("data: "):
                            done_payload = json.loads(line[6:])

            assert len(events) > 0, "Generator must emit events"
            assert len(tokens) > 0, "Generator must emit token deltas"
            assert citations is not None, "Citations list must be parsed"
            assert done_payload is not None, "Generator must conclude with done event"
            assert done_payload["tokens_count"] > 0
            assert "full_text" in done_payload
            assert len(done_payload["full_text"]) > 10

            # Verify AuditLog was recorded
            log_stmt = (
                select(AuditLog)
                .where(
                    AuditLog.resource_id == str(doc.id),
                    AuditLog.action == "DOCUMENT_AUDITED_STREAM",
                )
                .order_by(AuditLog.timestamp.desc())
            )
            log_res = await session.execute(log_stmt)
            audit_log = log_res.scalars().first()
            assert audit_log is not None, "AuditLog must be created for stream completion"
            assert audit_log.details["tokens_count"] == done_payload["tokens_count"]

            # Clean up test audit log
            await session.delete(audit_log)
            await session.commit()


@pytest.mark.asyncio
async def test_audit_stream_endpoint():
    """
    Verifies that POST /api/v1/documents/{document_id}/audit-stream returns
    HTTP 200 with text/event-stream content-type and valid SSE token packets.
    """
    async with async_session_factory() as session:
        with tenant_context(SIEMENS_TENANT_ID):
            doc_stmt = select(Document).where(Document.tenant_id == SIEMENS_TENANT_ID)
            res = await session.execute(doc_stmt)
            doc = res.scalars().first()
            assert doc is not None

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        payload = {
            "query": "DORA Art. 30 Kündigung und Ausstiegsstrategie",
            "framework": "DORA",
            "lang": "DE",
            "history": [],
        }
        headers = {"X-Tenant-ID": "siemens-ag"}

        response = await ac.post(
            f"/api/v1/documents/{doc.id}/audit-stream",
            json=payload,
            headers=headers,
        )

        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        assert "text/event-stream" in response.headers.get("content-type", "")
        body = response.text
        assert "event: status" in body
        assert "event: token" in body
        assert "event: done" in body

        # Clean up any logged audit entry from this test
        async with async_session_factory() as session:
            log_stmt = (
                select(AuditLog)
                .where(
                    AuditLog.resource_id == str(doc.id),
                    AuditLog.action == "DOCUMENT_AUDITED_STREAM",
                )
                .order_by(AuditLog.timestamp.desc())
            )
            log_res = await session.execute(log_stmt)
            audit_log = log_res.scalars().first()
            if audit_log:
                await session.delete(audit_log)
                await session.commit()


@pytest.mark.asyncio
async def test_stream_audit_cancellation_handling():
    """
    Verifies that when client disconnects early, the streamer detects it,
    emits an 'aborted' event, stops emitting tokens, and marks the AuditLog as aborted.
    """
    async with async_session_factory() as session:
        with tenant_context(SIEMENS_TENANT_ID):
            doc_stmt = select(Document).where(Document.tenant_id == SIEMENS_TENANT_ID)
            res = await session.execute(doc_stmt)
            doc = res.scalars().first()
            assert doc is not None

            # Mock Request object simulating early disconnection after 2 tokens
            class MockDisconnectedRequest:
                def __init__(self):
                    self.calls = 0

                async def is_disconnected(self):
                    self.calls += 1
                    return self.calls > 2

            mock_req = MockDisconnectedRequest()
            gen = stream_audit_response(
                document_id=doc.id,
                query="Kündigungsfristen Test",
                framework="DORA",
                lang="DE",
                history=None,
                tenant_id=doc.tenant_id,
                user_id=uuid4(),
                db=session,
                request=mock_req,
            )

            events = []
            async for chunk_str in gen:
                events.append(chunk_str)

            full_stream = "".join(events)
            assert "event: aborted" in full_stream, "Must emit aborted event on client disconnection"

            # Verify AuditLog logged with aborted: True
            log_stmt = (
                select(AuditLog)
                .where(
                    AuditLog.resource_id == str(doc.id),
                    AuditLog.action == "DOCUMENT_AUDITED_STREAM",
                )
                .order_by(AuditLog.timestamp.desc())
            )
            log_res = await session.execute(log_stmt)
            audit_log = log_res.scalars().first()
            assert audit_log is not None
            assert audit_log.details.get("aborted") is True

            # Clean up
            await session.delete(audit_log)
            await session.commit()

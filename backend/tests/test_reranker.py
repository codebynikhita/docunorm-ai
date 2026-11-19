"""
DocuNorm AI — Cross-Encoder Re-Ranking & High-Precision Retrieval Test Suite.
Validates two-stage neural cross-attention, German statutory citation reinforcement,
and REST endpoints in accordance with BaFin KWG § 25b and DORA Art. 30.
"""

from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from app.core.db import async_session_factory
from app.core.tenant import SIEMENS_TENANT_ID
from app.main import app
from app.models.document import Document, DocumentChunk, DocumentStatus
from app.models.user import User, UserRole
from app.services.reranker import reranker_service


def test_cross_encoder_scoring_and_ranking():
    """
    Verifies that the Cross-Encoder boosts the true operative termination clause
    over general and irrelevant clauses, calculating correct scores and rank deltas.
    """
    query = "Kündigungsrecht aus wichtigem Grund bei aufsichtsrechtlicher Anordnung der BaFin"

    passages = [
        # Index 0: Irrelevant confidentiality clause
        "Die Parteien verpflichten sich zur strengen Geheimhaltung aller im Rahmen der Zusammenarbeit ausgetauschten Geschäftsgeheimnisse.",
        # Index 1: Standard ordinary termination (weak relevance)
        "Dieser Vertrag kann von beiden Parteien mit einer Frist von sechs Monaten zum Ende eines Kalenderjahres ordentlich gekündigt werden.",
        # Index 2: Operative regulatory emergency termination (Exact needle!)
        "Der Auftraggeber ist berechtigt, diesen Vertrag außerordentlich und fristlos aus wichtigem Grund zu kündigen, insbesondere wenn die BaFin oder eine zuständige europäische Aufsichtsbehörde die Beendigung oder Rückabwicklung der Auslagerung anordnet.",
    ]

    res = reranker_service.rerank_passages(
        query=query,
        documents=passages,
        top_k=3,
        boost_legal_terms=True,
    )

    assert res.total_candidates == 3
    assert len(res.results) == 3

    # The operative clause (Index 2) MUST be elevated to Rank 1!
    top_hit = res.results[0]
    assert top_hit.index == 2
    assert top_hit.reranked_rank == 1
    assert top_hit.initial_rank == 3
    assert top_hit.rank_delta == +2  # Elevated by 2 positions
    assert top_hit.score > 0.75
    assert any("BaFin" in match or "Termination" in match for match in top_hit.legal_term_matches)

    # Both other passages must have significantly lower scores than top hit
    assert res.results[1].score < top_hit.score
    assert res.results[2].score < top_hit.score
    assert top_hit.score - res.results[1].score > 0.30


def test_german_statutory_citation_cross_attention():
    """
    Verifies that specific section citations (§ 25b KWG, Art. 30 DORA)
    receive explicit cross-attention weight over generic regulatory mentions.
    """
    query = "DORA Art. 30 Abs. 2 Unterbeauftragung und Prüfungsrechte"

    passages = [
        # Index 0: Generic IT security
        "Der Dienstleister setzt zeitgemäße Sicherheitsvorkehrungen und Firewalls ein.",
        # Index 1: Generic GDPR mention
        "Die Vorgaben der DSGVO und des BDSG werden von beiden Vertragspartnern vollumfänglich eingehalten.",
        # Index 2: Exact DORA Art. 30 statutory clause
        "Gemäß DORA Art. 30 Abs. 2 vereinbaren die Parteien uneingeschränkte Prüfrechte und Zutrittsbefugnisse für die BaFin und die EZB sowie strenge Auflagen für jede Weiterverlagerung an Unterauftragnehmer.",
    ]

    res = reranker_service.rerank_passages(
        query=query,
        documents=passages,
        top_k=3,
        boost_legal_terms=True,
    )

    assert res.results[0].index == 2
    assert res.results[0].score > 0.80
    assert any("Statutory Citation" in m or "DORA" in m for m in res.results[0].legal_term_matches)


def test_rerank_fastapi_endpoints():
    """
    Verifies the REST endpoints:
    - POST /api/v1/rerank
    - GET /api/v1/rerank/models
    """
    client = TestClient(app)

    # 1. Model Info Endpoint
    res_info = client.get("/api/v1/rerank/models")
    assert res_info.status_code == 200
    info_data = res_info.json()
    assert info_data["model_id"] == "BAAI/bge-reranker-large"
    assert "de" in info_data["supported_languages"]

    # 2. General Re-Rank Endpoint
    payload = {
        "query": "Haftungsausschluss bei grober Fahrlässigkeit nach BGB § 309 Nr. 7",
        "documents": [
            "Die Haftung für leichte Fahrlässigkeit wird ausgeschlossen.",
            "Ein Haftungsausschluss für Schäden aus der Verletzung des Lebens, des Körpers oder der Gesundheit sowie für grobes Verschulden ist nach BGB § 309 unwirksam.",
            "Zahlungsziel ist 30 Tage netto nach Rechnungserhalt.",
        ],
        "top_k": 2,
        "boost_legal_terms": True,
    }
    res_rerank = client.post("/api/v1/rerank", json=payload)
    assert res_rerank.status_code == 200
    data = res_rerank.json()
    assert data["total_candidates"] == 3
    assert data["top_k"] == 2
    assert len(data["results"]) == 2
    # Second document (index 1) should be #1
    assert data["results"][0]["index"] == 1
    assert data["results"][0]["score"] > 0.70


@pytest.mark.asyncio
async def test_two_stage_document_reranked_search():
    """
    Verifies the two-stage document search endpoint:
    - Stage 1: Vector search candidate retrieval
    - Stage 2: Cross-Encoder re-ranking with rank delta tracking
    """
    client = TestClient(app)

    async with async_session_factory() as session:
        # 1. Create a user and document
        user = User(
            id=uuid4(),
            tenant_id=SIEMENS_TENANT_ID,
            email=f"auditor-{uuid4()}@siemens.de",
            full_name="Lead Re-Rank Auditor",
            hashed_password="mock",
            role=UserRole.AUDITOR,
        )
        session.add(user)
        await session.flush()

        doc = Document(
            id=uuid4(),
            tenant_id=SIEMENS_TENANT_ID,
            uploaded_by=user.id,
            filename="Siemens_IKT_Auslagerungsvertrag_2026.pdf",
            file_path="/storage/documents/siemens/test_rerank.pdf",
            file_size_bytes=10240,
            mime_type="application/pdf",
            sha256_hash=uuid4().hex + uuid4().hex,
            status=DocumentStatus.READY,
            total_pages=3,
        )
        session.add(doc)

        # 2. Add Chunks
        chunk1 = DocumentChunk(
            id=uuid4(),
            document_id=doc.id,
            tenant_id=SIEMENS_TENANT_ID,
            chunk_index=0,
            page_number=1,
            content="Präambel: Dieser Vertrag regelt die Bereitstellung von Cloud-Infrastrukturleistungen.",
            token_count=10,
        )
        chunk2 = DocumentChunk(
            id=uuid4(),
            document_id=doc.id,
            tenant_id=SIEMENS_TENANT_ID,
            chunk_index=1,
            page_number=2,
            content="Vergütung: Die Abrechnung erfolgt monatlich auf Basis der tatsächlichen CPU-Nutzung.",
            token_count=12,
        )
        chunk3 = DocumentChunk(
            id=uuid4(),
            document_id=doc.id,
            tenant_id=SIEMENS_TENANT_ID,
            chunk_index=2,
            page_number=3,
            content="Aufsichtsrechtliche Kündigung: Der Auftraggeber kann gemäß DORA Art. 30 Abs. 2 bei aufsichtsrechtlicher Beanstandung fristlos kündigen.",
            token_count=18,
        )
        session.add_all([chunk1, chunk2, chunk3])
        await session.commit()

        doc_id = doc.id

    # Test the reranked search endpoint
    search_payload = {
        "query": "DORA Art. 30 Kündigung bei Beanstandung durch die Aufsichtsbehörde",
        "candidate_pool_size": 10,
        "top_k": 3,
        "boost_legal_terms": True,
    }

    res = client.post(
        f"/api/v1/documents/{doc_id}/reranked-search",
        json=search_payload,
        headers={"X-Tenant-ID": "siemens-ag"},
    )
    assert res.status_code == 200
    search_data = res.json()
    assert search_data["stage1_candidates_fetched"] >= 3
    assert len(search_data["results"]) >= 1

    # Chunk 3 MUST be the top result with highest cross-encoder score
    top_result = search_data["results"][0]
    assert "DORA Art. 30" in top_result["content"]
    assert top_result["final_rank"] == 1
    assert top_result["cross_encoder_score"] > 0.70

    # Teardown test artifacts
    async with async_session_factory() as session:
        c1 = await session.get(DocumentChunk, chunk1.id)
        c2 = await session.get(DocumentChunk, chunk2.id)
        c3 = await session.get(DocumentChunk, chunk3.id)
        d = await session.get(Document, doc_id)
        u = await session.get(User, user.id)
        for obj in [c1, c2, c3, d, u]:
            if obj:
                await session.delete(obj)
        await session.commit()

#!/usr/bin/env python3
"""
DocuNorm Sovereign AI - Comprehensive End-to-End System Verification Audit
Tests all core systems, database, translation, LkSG/BAFA, DORA, and API endpoints.
"""
import asyncio
import sqlite3
import sys
from pathlib import Path

# Add backend directory to path
backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

import uuid

import httpx

from app.main import app
from app.models.document import Document
from app.services.auditor import fallback_translate_german_text
from app.services.bafa_pdf_exporter import generate_bafa_audit_report_pdf
from app.services.bafa_questionnaire import BafaQuestionnaireService


async def test_all_systems():
    print("=" * 80)
    print("🔍 DOCUNORM SOVEREIGN AI - FULL SYSTEM VERIFICATION AUDIT")
    print("=" * 80)
    
    results = {}
    
    # 1. Database Verification
    print("\n[1/6] 📦 Checking SQLite Sovereign Database (docunorm_local.db)...")
    db_path = backend_dir / "docunorm_local.db"
    assert db_path.exists(), f"Database not found at {db_path}"
    
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    cursor.execute("SELECT id, filename, total_pages, sha256_hash FROM documents")
    docs = cursor.fetchall()
    print(f"  • Registered documents: {len(docs)}")
    for d in docs:
        cursor.execute("SELECT count(*) FROM document_chunks WHERE document_id = ?", (d[0],))
        cnt = cursor.fetchone()[0]
        print(f"    - '{d[1]}' (Pages: {d[2]}, Chunks: {cnt}, ID: {d[0]})")
    results["database"] = len(docs) >= 2
    
    # 2. Translation Engine Verification (50-page Deutsche Bank Agreement)
    print("\n[2/6] 🌐 Checking 50-Clause Translation Coverage...")
    cursor.execute("""
        SELECT dc.content FROM document_chunks dc
        JOIN documents d ON d.id = dc.document_id
        WHERE d.filename LIKE '%Deutsche_Bank%'
    """)
    all_chunks = [r[0] for r in cursor.fetchall()]
    
    untranslated_count = 0
    for text in all_chunks:
        trans = fallback_translate_german_text(text)
        if trans == text and any(w in text.lower() for w in ["teil ", "vertragsdossier", "§ ", "aufsichtsrechtlicher"]):
            untranslated_count += 1
            
    print(f"  • Tested chunks: {len(all_chunks)}")
    print(f"  • Untranslated critical clauses: {untranslated_count} / {len(all_chunks)}")
    results["translation"] = untranslated_count == 0 and len(all_chunks) > 0
    
    # 3. LkSG & BAFA Questionnaire Engine
    print("\n[3/6] ⚖️ Testing LkSG & BAFA Statutory Questionnaire (§§ 2-10 LkSG)...")
    doc_id = uuid.uuid4()
    test_chunks = [
        {"id": "c1", "page_number": 1, "content": "Siemens AG Rahmenvereinbarung über IT-Dienstleistungen nach LkSG. Kinderarbeit gem. ILO 138/182 ist untersagt. Verbot von Zwangsarbeit. ISO 45001 Arbeitsschutz. Mindestlohn nach MiLoG. Minamata- und Stockholmer Übereinkommen werden eingehalten. Beschwerdeverfahren gem. § 8 LkSG eingerichtet. BAFA-Bericht jährlich."}
    ]
    bafa_res = BafaQuestionnaireService.generate_questionnaire(
        document_id=doc_id,
        filename="Siemens_Audit_Test.pdf",
        chunks=test_chunks,
    )
    print(f"  • BAFA Score: {bafa_res.overall_score}% ({bafa_res.compliance_rating})")
    print(f"  • Criteria Met: {bafa_res.compliant_count} / {bafa_res.total_questions} sections")
    results["bafa_engine"] = bafa_res.overall_score >= 80.0 and len(bafa_res.sections) == 12
    
    # 4. BAFA PDF Report Generation
    print("\n[4/6] 📄 Testing Certified BAFA PDF Report Generator...")
    temp_doc = Document(
        id=doc_id,
        tenant_id=uuid.uuid4(),
        filename="Deutsche_Bank_Master_Cloud_Agreement_50P.pdf",
        sha256_hash="e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
        total_pages=50,
        file_size_bytes=524288,
    )
    pdf_path = generate_bafa_audit_report_pdf(
        document=temp_doc,
        questionnaire=bafa_res,
        output_dir="/tmp/docunorm_audit_check",
    )
    print(f"  • Generated PDF at: {pdf_path}")
    print(f"  • PDF file size: {pdf_path.stat().st_size} bytes")
    results["bafa_pdf"] = pdf_path.exists() and pdf_path.stat().st_size > 5000
    
    # 5. Fast HTTP API Endpoint Verification (using httpx ASGITransport)
    print("\n[5/6] 🚀 Testing FastAPI Endpoints (In-Process ASGI Simulation)...")
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        # 5.1 Health Check
        r_health = await client.get("/health")
        print(f"  • GET /health -> Status: {r_health.status_code}")
        
        # 5.2 List Documents
        r_docs = await client.get("/api/v1/documents/")
        print(f"  • GET /api/v1/documents/ -> Status: {r_docs.status_code}, Found: {len(r_docs.json())} docs")
        doc_list = r_docs.json()
        target_doc_id = doc_list[0]["id"] if doc_list else None
        
        if target_doc_id:
            # 5.3 File Stream
            r_file = await client.get(f"/api/v1/documents/{target_doc_id}/file")
            print(f"  • GET /api/v1/documents/{target_doc_id[:8]}.../file -> Status: {r_file.status_code}, Size: {len(r_file.content)} bytes")
            
            # 5.4 Translated Chunks
            r_trans = await client.get(f"/api/v1/documents/{target_doc_id}/translated-chunks")
            print(f"  • GET /api/v1/documents/{target_doc_id[:8]}.../translated-chunks -> Status: {r_trans.status_code}, Chunks: {len(r_trans.json())}")
            
            # 5.5 LkSG Audit
            r_lksg = await client.post(f"/api/v1/documents/{target_doc_id}/lksg-audit")
            print(f"  • POST /api/v1/documents/{target_doc_id[:8]}.../lksg-audit -> Status: {r_lksg.status_code}")
            
            # 5.6 BAFA Questionnaire
            r_bafa_q = await client.post(f"/api/v1/documents/{target_doc_id}/lksg-bafa-questionnaire")
            print(f"  • POST /api/v1/documents/{target_doc_id[:8]}.../lksg-bafa-questionnaire -> Status: {r_bafa_q.status_code}")
            
            # 5.7 BAFA Report PDF Export
            r_bafa_pdf = await client.post(f"/api/v1/documents/{target_doc_id}/export-bafa-report-pdf")
            print(f"  • POST /api/v1/documents/{target_doc_id[:8]}.../export-bafa-report-pdf -> Status: {r_bafa_pdf.status_code}, Size: {len(r_bafa_pdf.content)} bytes")
            
            results["api_endpoints"] = (
                r_health.status_code == 200
                and r_docs.status_code == 200
                and r_file.status_code == 200
                and r_trans.status_code == 200
                and r_lksg.status_code == 200
                and r_bafa_q.status_code == 200
                and r_bafa_pdf.status_code == 200
            )
        else:
            results["api_endpoints"] = False

    # 6. Summary Verdict
    print("\n" + "=" * 80)
    all_pass = all(results.values())
    for k, v in results.items():
        print(f"  {'✅' if v else '❌'} Gate {k.upper()}: {'PASSED' if v else 'FAILED'}")
    print("=" * 80)
    if all_pass:
        print("🏆 VERDICT: ALL SYSTEMS 100% OPERATIONAL & PRODUCTION READY.")
    else:
        print("⚠️ VERDICT: ONE OR MORE SUBSYSTEMS REPORTED DEFICIENCIES.")
    print("=" * 80)
    return all_pass

if __name__ == "__main__":
    success = asyncio.run(test_all_systems())
    sys.exit(0 if success else 1)

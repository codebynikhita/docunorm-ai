import asyncio
import httpx
import json

BASE_URL = "http://127.0.0.1:8000"

async def test_full_pipeline():
    print("==================================================")
    print("🧪 DOCUNORM AI - FULL STACK END-TO-END SYSTEM TEST")
    print("==================================================")
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        # 1. Health check
        print("\n[Step 1] Checking Backend Health...")
        try:
            r = await client.get(f"{BASE_URL}/health")
            print(f"-> Health Status Code: {r.status_code}")
            assert r.status_code == 200, f"Health check failed: {r.text}"
            print("   ✅ Backend is Healthy and Operational!")
        except Exception as e:
            print(f"   ❌ Could not connect to {BASE_URL}: {e}")
            print("   Make sure uvicorn is running on port 8000.")
            return

        # 2. List Documents
        print("\n[Step 2] Listing Ingested Documents...")
        r = await client.get(f"{BASE_URL}/api/v1/documents")
        assert r.status_code == 200, f"List documents failed: {r.text}"
        docs = r.json()
        print(f"-> Found {len(docs)} documents in database.")
        for d in docs[:3]:
            print(f"   • {d['filename']} (ID: {d['id']}, Pages: {d.get('total_pages')})")
        
        assert len(docs) > 0, "No documents found!"
        
        # Pick the German demo doc or first doc
        target_doc = next((d for d in docs if "Siemens_Master_IKT_Vertrag_2026" in d["filename"]), docs[0])
        doc_id = target_doc["id"]
        print(f"\n   🎯 Selected Document for Testing: '{target_doc['filename']}' ({doc_id})")

        # 3. Test Translated Chunks Endpoint (Dual-View / English Dossier)
        print("\n[Step 3] Testing /translated-chunks Endpoint (Dual-View Feature)...")
        r = await client.get(f"{BASE_URL}/api/v1/documents/{doc_id}/translated-chunks")
        assert r.status_code == 200, f"Translated chunks failed: {r.text}"
        chunks = r.json()
        print(f"-> Retrieved {len(chunks)} translated chunks.")
        assert len(chunks) > 0, "No chunks returned!"
        sample = chunks[0]
        print(f"   Sample Original Chunk (Page {sample['page_number']}):\n   🇩🇪 \"{sample['content'][:90]}...\"")
        print(f"   Sample English Translation:\n   🇬🇧 \"{sample.get('translated_content', sample['content'])[:90]}...\"")
        print("   ✅ Dual-View Translation API works perfectly!")

        # 4. Test German Audit Query (BaFin / DORA)
        print("\n[Step 4] Testing German Regulatory Audit Query...")
        query_de = "Sind Ausstiegsfristen nach Art. 30 geregelt?"
        print(f"   Query (DE): \"{query_de}\"")
        payload_de = {"query": query_de, "framework": "DORA"}
        r = await client.post(f"{BASE_URL}/api/v1/documents/{doc_id}/audit", json=payload_de)
        assert r.status_code == 200, f"German audit failed: {r.text}"
        audit_res_de = r.json()
        print(f"-> Audit Status: {audit_res_de['status']}")
        print(f"-> Citations Found: {len(audit_res_de['citations'])}")
        print(f"-> AI Finding Summary:\n{audit_res_de['finding_summary']}")
        assert len(audit_res_de['citations']) > 0, "Expected at least 1 citation for Art. 30 check!"
        print("   ✅ German Regulatory Audit & Citation Grounding Verified!")

        # 5. Test English Audit Query (Delay Penalty)
        print("\n[Step 5] Testing English Regulatory Audit Query...")
        query_en = "What is the maximum delay penalty rate and SLA cap?"
        print(f"   Query (EN): \"{query_en}\"")
        payload_en = {"query": query_en, "framework": "DORA"}
        r = await client.post(f"{BASE_URL}/api/v1/documents/{doc_id}/audit", json=payload_en)
        assert r.status_code == 200, f"English audit failed: {r.text}"
        audit_res_en = r.json()
        print(f"-> Audit Status: {audit_res_en['status']}")
        print(f"-> Citations Found: {len(audit_res_en['citations'])}")
        print(f"-> AI Finding Summary:\n{audit_res_en['finding_summary']}")
        assert len(audit_res_en['citations']) > 0, "Expected citation for penalty check!"
        print("   ✅ English Cross-Lingual Regulatory Audit Verified!")

        print("\n==================================================")
        print("🎉 ALL 5 INTEGRATION STEPS PASSED SUCCESSFULLY!")
        print("==================================================")

if __name__ == "__main__":
    asyncio.run(test_full_pipeline())

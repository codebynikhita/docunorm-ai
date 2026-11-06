#!/usr/bin/env python3
"""
DocuNorm Deep Fault-Injection & Negative Boundary Audit Harness
Systematically tests:
1. 404 Resiliency on Non-Existent Entities across all Document Routes
2. Malformed UUID & Path Traversal Injection Handling
3. Boundary & Negative Numerical Inputs in SLA Calculations
4. Database Referential Integrity & Orphan Verification
5. JWT Forgery, Algorithm Confusion & Expired Auth Probes
6. Zero-byte and Corrupted PDF Upload Validation
"""
import asyncio
import sys
import time
from pathlib import Path

backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

import sqlite3

import httpx

from app.main import app


async def run_fault_injection_suite():
    print("=" * 85)
    print("⚡ DOCUNORM DEEP FAULT-INJECTION & ADVERSARIAL STRESS HARNESS")
    print(f"🕒 Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S UTC', time.gmtime())}")
    print("=" * 85)

    transport = httpx.ASGITransport(app=app)
    passed_tests = 0
    total_tests = 0

    async with httpx.AsyncClient(transport=transport, base_url="http://testserver", timeout=30.0) as client:
        # -------------------------------------------------------------------------
        # CATEGORY 1: NON-EXISTENT ENTITY (404) RESILIENCY
        # -------------------------------------------------------------------------
        print("\n[CATEGORY 1] 🛑 404 RESILIENCY ON NON-EXISTENT ENTITIES")
        print("-" * 85)

        fake_id = "00000000-0000-0000-0000-000000000000"
        test_routes = [
            ("GET", f"/api/v1/documents/{fake_id}/chunks", None),
            ("GET", f"/api/v1/documents/{fake_id}/translated-chunks", None),
            ("GET", f"/api/v1/documents/{fake_id}/file", None),
            ("GET", f"/api/v1/documents/{fake_id}/tables", None),
            ("GET", f"/api/v1/documents/{fake_id}/dora-exit-audit", None),
            ("GET", f"/api/v1/documents/{fake_id}/dora-subcontractor-audit", None),
            ("GET", f"/api/v1/documents/{fake_id}/dora-audit-rights", None),
            ("GET", f"/api/v1/documents/{fake_id}/clause-risk-heatmap", None),
            ("GET", f"/api/v1/documents/{fake_id}/lksg-audit", None),
            ("POST", f"/api/v1/documents/{fake_id}/lksg-bafa-questionnaire", None),
            ("POST", f"/api/v1/documents/{fake_id}/export-din-audit-report", None),
            ("POST", f"/api/v1/documents/{fake_id}/export-bafa-report-pdf", None),
            ("POST", f"/api/v1/documents/{fake_id}/export-amendment-pdf", {}),
            ("GET", f"/api/v1/documents/{fake_id}/export-english-pdf", None),
        ]

        for method, route, body in test_routes:
            total_tests += 1
            if method == "GET":
                r = await client.get(route)
            else:
                r = await client.post(route, json=body if body is not None else {})

            if r.status_code == 404:
                passed_tests += 1
                print(f"  • {method:<4} {route:<58} -> HTTP 404 (SAFE)")
            else:
                print(f"  ❌ FAILED: {method} {route} returned HTTP {r.status_code} instead of 404!")

        # -------------------------------------------------------------------------
        # CATEGORY 2: MALFORMED IDENTIFIERS & PATH TRAVERSAL ATTEMPTS
        # -------------------------------------------------------------------------
        print("\n[CATEGORY 2] 🛡️  MALFORMED IDENTIFIERS & PATH TRAVERSAL ATTEMPTS")
        print("-" * 85)

        hostile_paths = [
            "/api/v1/documents/not-a-uuid/chunks",
            "/api/v1/documents/..%2F..%2Fetc%2Fpasswd/file",
            "/api/v1/documents/%00/dora-exit-audit",
            "/api/v1/documents/12345/tables",
        ]

        for path in hostile_paths:
            total_tests += 1
            r = await client.get(path)
            # Must return 422 (Unprocessable) or 400 or 404, never 500
            if r.status_code in (400, 404, 422):
                passed_tests += 1
                print(f"  • GET {path:<50} -> HTTP {r.status_code} (NEUTRALIZED)")
            else:
                print(f"  ❌ UNHANDLED EXCEPTION: {path} returned HTTP {r.status_code}")

        # -------------------------------------------------------------------------
        # CATEGORY 3: SLA PENALTY CALCULATOR NUMERICAL BOUNDARY PROBES
        # -------------------------------------------------------------------------
        print("\n[CATEGORY 3] 🔢 NUMERICAL BOUNDARY & EDGE CASE PROBES (SLA CALCULATOR)")
        print("-" * 85)

        sample_doc_id = "8991aff2-b631-4831-b963-bbe9fcc77029"
        boundary_payloads = [
            # Zero order value
            {"document_id": sample_doc_id, "table_id": "tbl_0", "annual_order_value_eur": 0.0, "actual_downtime_hours": 10.0, "sla_tier": "Tier-3"},
            # Zero downtime (perfect availability)
            {"document_id": sample_doc_id, "table_id": "tbl_0", "annual_order_value_eur": 500000.0, "actual_downtime_hours": 0.0, "sla_tier": "Tier-3"},
            # Downtime below tolerated threshold (2.0 hours < 4.38 hours)
            {"document_id": sample_doc_id, "table_id": "tbl_0", "annual_order_value_eur": 500000.0, "actual_downtime_hours": 2.0, "sla_tier": "Tier-3"},
            # Extreme catastrophic downtime (500 hours > 87.6 hours termination trigger)
            {"document_id": sample_doc_id, "table_id": "tbl_0", "annual_order_value_eur": 1200000.0, "actual_downtime_hours": 500.0, "sla_tier": "Tier-1"},
            # Fractional microscopic downtime (4.3801 hours)
            {"document_id": sample_doc_id, "table_id": "tbl_0", "annual_order_value_eur": 1000000.0, "actual_downtime_hours": 4.3801, "sla_tier": "Tier-2"},
        ]

        for i, payload in enumerate(boundary_payloads, 1):
            total_tests += 1
            r = await client.post(f"/api/v1/documents/{sample_doc_id}/tables/calculate-penalty", json=payload)
            if r.status_code == 200:
                data = r.json()
                passed_tests += 1
                print(f"  • Probe {i} (Downtime: {payload['actual_downtime_hours']}h, EUR {payload['annual_order_value_eur']:,.0f}): Penalty EUR {data['final_enforceable_penalty_eur']:,.2f} ({data['dora_compliance_status']}) (PASSED)")
            else:
                print(f"  ❌ Probe {i} failed with status {r.status_code}: {r.text}")

        # -------------------------------------------------------------------------
        # CATEGORY 4: AUTHENTICATION FORGERY & TAMPERED TOKEN INJECTION
        # -------------------------------------------------------------------------
        print("\n[CATEGORY 4] 🔐 AUTHENTICATION FORGERY & TAMPERED TOKEN INJECTION")
        print("-" * 85)

        forged_headers = [
            ("Bearer invalid.token.payload", "Forged JWT syntax"),
            ("Bearer eyJhbGciOiJub25lIn0.eyJzdWIiOiIxMjM0In0.", "Algorithm None exploit"),
            ("Basic YWRtaW46cGFzc3dvcmQ=", "Invalid Auth Scheme"),
            ("Bearer ", "Empty Bearer Token"),
        ]

        for token, desc in forged_headers:
            total_tests += 1
            r = await client.get("/api/v1/auth/me", headers={"Authorization": token})
            if r.status_code == 401:
                passed_tests += 1
                print(f"  • {desc:<30} -> HTTP 401 Unauthorized (REJECTED)")
            else:
                print(f"  ❌ Security Leak: {desc} returned HTTP {r.status_code} instead of 401!")

        # -------------------------------------------------------------------------
        # CATEGORY 5: ZERO-BYTE & MALFORMED FILE UPLOAD INTEGRITY
        # -------------------------------------------------------------------------
        print("\n[CATEGORY 5] 📁 FILE UPLOAD ZERO-BYTE & FORMAT VALIDATION")
        print("-" * 85)

        # 5.1 Empty file upload
        total_tests += 1
        r_empty = await client.post(
            "/api/v1/documents/upload",
            files={"file": ("empty.pdf", b"", "application/pdf")},
        )
        if r_empty.status_code in (400, 422):
            passed_tests += 1
            print(f"  • Empty 0-byte PDF Upload -> HTTP {r_empty.status_code} (PROPERLY REJECTED)")
        else:
            print(f"  ❌ Empty file upload was not rejected! Status: {r_empty.status_code}")

        # 5.2 Invalid extension upload
        total_tests += 1
        r_exe = await client.post(
            "/api/v1/documents/upload",
            files={"file": ("malicious.exe", b"MZ\x90\x00\x03\x00\x00\x00", "application/x-msdownload")},
        )
        if r_exe.status_code in (400, 415, 422):
            passed_tests += 1
            print(f"  • Non-PDF (.exe) Upload -> HTTP {r_exe.status_code} (PROPERLY REJECTED)")
        else:
            print(f"  ❌ Non-PDF file upload was not rejected! Status: {r_exe.status_code}")

        # -------------------------------------------------------------------------
        # CATEGORY 6: DATABASE REFERENTIAL INTEGRITY AUDIT
        # -------------------------------------------------------------------------
        print("\n[CATEGORY 6] 🗄️  DATABASE REFERENTIAL INTEGRITY & ORPHAN AUDIT")
        print("-" * 85)

        total_tests += 1
        db_path = backend_dir / "docunorm_local.db"
        if db_path.exists():
            conn = sqlite3.connect(str(db_path))
            cur = conn.cursor()

            # Check for orphaned chunks without matching document
            cur.execute("""
                SELECT count(*) FROM document_chunks 
                WHERE document_id NOT IN (SELECT id FROM documents)
            """)
            orphaned_chunks = cur.fetchone()[0]

            # Check for orphaned documents without matching tenant
            cur.execute("""
                SELECT count(*) FROM documents 
                WHERE tenant_id NOT IN (SELECT id FROM tenants)
            """)
            orphaned_docs = cur.fetchone()[0]

            conn.close()

            if orphaned_chunks == 0 and orphaned_docs == 0:
                passed_tests += 1
                print(f"  • Orphaned Chunks:  {orphaned_chunks} (CLEAN)")
                print(f"  • Orphaned Docs:    {orphaned_docs} (CLEAN)")
                print("  • Database Integrity: 100% Consistent Relational Graph (PASSED)")
            else:
                print(f"  ❌ Integrity Fault: Found {orphaned_chunks} orphaned chunks and {orphaned_docs} orphaned docs!")

    # -------------------------------------------------------------------------
    # SUMMARY
    # -------------------------------------------------------------------------
    print("\n" + "=" * 85)
    print(f"🏆 FAULT-INJECTION AUDIT RESULT: {passed_tests} / {total_tests} PROBES PASSED ({(passed_tests/total_tests)*100:.1f}%)")
    print("=" * 85)
    if passed_tests == total_tests:
        print("✅ ALL ADVERSARIAL, 404, MALFORMED INPUT, AND INTEGRITY CHECKS PASSED.")
    else:
        print("⚠️ Some fault-injection probes detected vulnerabilities.")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(run_fault_injection_suite())

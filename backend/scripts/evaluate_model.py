#!/usr/bin/env python3
"""
DocuNorm Sovereign AI - Multi-Dataset Regulatory Benchmark Suite
Runs automated regression testing across all 5 Regulatory Pillars:
- DORA Exit & Migration Strategy (Art. 30 Abs. 2)
- Sub-Outsourcing Cascading Risk (Art. 30 Abs. 3)
- BaFin & ECB Unrestricted Audit Rights (KWG § 25b)
- SLAs, Penalties & Liability Protection
- ZUGFeRD 2.3 / CEN 16931 E-Invoicing
"""
import asyncio
import json
import os
import sys
import time
from pathlib import Path
from dotenv import load_dotenv

# Ensure backend directory is in sys.path
backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))
load_dotenv(backend_dir / ".env", override=True)

from app.services.auditor import generate_llm_audit_finding


async def run_evaluation():
    benchmark_file = backend_dir / "data" / "training" / "test_benchmark.json"

    if not benchmark_file.exists():
        print(f"❌ Error: Benchmark dataset not found at: {benchmark_file}")
        return

    with open(benchmark_file, "r", encoding="utf-8") as f:
        benchmarks = json.load(f)

    passed = 0
    total = len(benchmarks)
    pillar_scores = {}

    print("=" * 75)
    print("🏛️  DOCUNORM SOVEREIGN AI - CONTINUOUS MULTI-DATASET BENCHMARK")
    print(f"📊 Running {total} Ground-Truth Test Cases Across All Regulatory Pillars")
    print("=" * 75)

    for idx, test in enumerate(benchmarks, 1):
        pillar = test.get("pillar", "General Compliance")
        if pillar not in pillar_scores:
            pillar_scores[pillar] = {"passed": 0, "total": 0}
        pillar_scores[pillar]["total"] += 1

        retrieved_chunk = [{"page_number": 1, "content": test["context"]}]

        start_t = time.time()
        response = await generate_llm_audit_finding(
            query=test["query"],
            retrieved_chunks=retrieved_chunk,
            framework="DORA",
            lang="DE"
        )
        duration_ms = (time.time() - start_t) * 1000

        # Verification Criteria:
        # 1. Exact Source Grounding
        has_citation = test["must_include_citation"] in response
        # 2. Key Statutory Terminology
        has_facts = any(fact.lower() in response.lower() for fact in test["must_mention"])
        # 3. Regulatory Status Verdict (KONFORM / DEFIZITÄR)
        has_status = test["expected_status"] in response

        if has_citation and has_facts and has_status:
            print(f"[{idx}/{total}] ✅ PASS | {test['id']} ({duration_ms:.0f}ms) -> Pillar: {pillar}")
            passed += 1
            pillar_scores[pillar]["passed"] += 1
        else:
            print(f"[{idx}/{total}] ❌ FAIL | {test['id']} -> Pillar: {pillar}")
            print(f"       Details: citation={has_citation}, facts={has_facts}, status={has_status}")
            print(f"       Response snippet: {response[:120]}...\n")

    overall_score = (passed / total) * 100 if total else 0
    print("\n" + "=" * 75)
    print("📈 REGULATORY PILLAR SCORECARD BREAKDOWN:")
    print("-" * 75)
    for p_name, p_data in pillar_scores.items():
        p_pct = (p_data["passed"] / p_data["total"]) * 100 if p_data["total"] else 0
        bar = "█" * int(p_pct // 10) + "░" * (10 - int(p_pct // 10))
        print(f"  • {p_name:<38} [{bar}] {p_pct:>5.1f}% ({p_data['passed']}/{p_data['total']})")

    print("-" * 75)
    print(f"🎯 OVERALL BENCHMARK ACCURACY: {overall_score:.1f}% ({passed}/{total} Passed)")
    if overall_score >= 90:
        print("🏆 VERDICT: Certified BaFin / DORA Compliance Audit Engine Ready for Production.")
    else:
        print("⚠️ VERDICT: Requires prompt tuning or rule refinement.")
    print("=" * 75)


if __name__ == "__main__":
    asyncio.run(run_evaluation())

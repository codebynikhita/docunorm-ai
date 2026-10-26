#!/usr/bin/env python3
"""
Test Live Gemini 2.0 Flash Inference with newly configured API Key
Run with: python scripts/test_live_inference.py
"""
import asyncio
import os
from pathlib import Path
from dotenv import load_dotenv

backend_dir = Path(__file__).resolve().parent.parent
load_dotenv(backend_dir / ".env", override=True)

from app.services.auditor import generate_llm_audit_finding

async def main():
    print("=" * 70)
    print("🚀 TESTING LIVE GEMINI 2.0 FLASH WITH ACTIVE API KEY")
    print("=" * 70)

    sample_chunk = [{
        "page_number": 3,
        "content": "§ 8 Abs. 2: Die Kündigungsfrist beträgt 60 Tage zum Monatsende mit 90 Tagen Migrationsbeistand."
    }]

    query = "Sind die Kündigungsfristen nach DORA Art. 30 zulässig?"
    print(f"📝 Query: {query}\n")

    response = await generate_llm_audit_finding(
        query=query,
        retrieved_chunks=sample_chunk,
        framework="DORA",
        lang="DE"
    )

    print("⚖️ MODEL RESPONSE:")
    print(response)
    print("=" * 70)

if __name__ == "__main__":
    asyncio.run(main())

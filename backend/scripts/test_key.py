#!/usr/bin/env python3
"""
Test script to diagnose Google Gemini Key / Token
Run with: python scripts/test_key.py
"""
import os
from pathlib import Path
from dotenv import load_dotenv
import httpx

backend_dir = Path(__file__).resolve().parent.parent
load_dotenv(backend_dir / ".env", override=True)

api_key = os.getenv("GEMINI_API_KEY")

print("=" * 60)
print(f"🔑 Loaded Key: {api_key[:12]}...{api_key[-6:] if api_key else ''}")
print("=" * 60)

# Test 1: Standard REST endpoint with query param
url_param = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"
print("\n1️⃣ Testing via URL query parameter (?key=...)...")
try:
    resp = httpx.get(url_param, timeout=10.0)
    print(f"   Status Code: {resp.status_code}")
    if resp.status_code == 200:
        print("   ✅ SUCCESS! Key is valid and active.")
    else:
        print(f"   Response: {resp.text[:250]}")
except Exception as e:
    print(f"   Network/Error: {e}")

# Test 2: Via X-goog-api-key header
print("\n2️⃣ Testing via Header ('X-goog-api-key')...")
try:
    resp = httpx.get("https://generativelanguage.googleapis.com/v1beta/models", headers={"X-goog-api-key": api_key}, timeout=10.0)
    print(f"   Status Code: {resp.status_code}")
    if resp.status_code == 200:
        print("   ✅ SUCCESS! Header authentication works.")
    else:
        print(f"   Response: {resp.text[:250]}")
except Exception as e:
    print(f"   Network/Error: {e}")

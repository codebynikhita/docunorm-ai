#!/usr/bin/env python3
"""
Inspect tunedModels endpoint via REST API
"""
import os
from pathlib import Path
from dotenv import load_dotenv
import httpx

backend_dir = Path(__file__).resolve().parent.parent
load_dotenv(backend_dir / ".env", override=True)
api_key = os.getenv("GEMINI_API_KEY")

url = f"https://generativelanguage.googleapis.com/v1beta/tunedModels?key={api_key}"
print(f"Testing GET {url}...")
try:
    resp = httpx.get(url, timeout=10.0)
    print("Status:", resp.status_code)
    print("Response:", resp.text)
except Exception as e:
    print("Error:", e)

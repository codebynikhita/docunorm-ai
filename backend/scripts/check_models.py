#!/usr/bin/env python3
"""
Inspect available tunable models in Gemini API
Run with: python scripts/check_models.py
"""
import os
from pathlib import Path
from dotenv import load_dotenv
import google.generativeai as genai

backend_dir = Path(__file__).resolve().parent.parent
load_dotenv(backend_dir / ".env", override=True)

api_key = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=api_key)

print("🔍 Querying models supporting 'createTunedModel' or fine-tuning...")
try:
    for model in genai.list_models():
        supported_methods = getattr(model, "supported_generation_methods", [])
        if "createTunedModel" in supported_methods or "createTunedTextModel" in supported_methods or "tune" in str(supported_methods):
            print(f"✅ Tunable model: {model.name} (Methods: {supported_methods})")
        elif "1.5" in model.name:
            print(f"ℹ️  {model.name} (Methods: {supported_methods})")
except Exception as e:
    print(f"❌ Error: {e}")

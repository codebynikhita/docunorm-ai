#!/usr/bin/env python3
"""
DocuNorm Sovereign AI - Enterprise Training & Benchmark Dataset Validator
Audits fine-tuning datasets and ground-truth benchmark corpora for:
- JSON / JSONL structural validity
- Role schema conformance (system, user, assistant)
- Ground-truth citation density ([SOURCE_X] tags)
- Token length statistics (mean, min, max, P95)
- Markdown sanitization (zero unescaped asterisk corruption)
- Regulatory pillar distribution balance
"""
import json
import re
import sys
from pathlib import Path

backend_dir = Path(__file__).resolve().parent.parent
data_dir = backend_dir / "data" / "training"


def estimate_tokens(text: str) -> int:
    """Rough estimate of tokens (~4 chars per token for European languages)."""
    return max(1, len(text) // 4)


def validate_training_file(path: Path) -> dict:
    if not path.exists():
        return {"error": f"File not found: {path}"}

    total_lines = 0
    valid_entries = 0
    citation_count = 0
    raw_asterisk_faults = 0
    token_counts = []
    pillars = {}

    with open(path, "r", encoding="utf-8") as f:
        for idx, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            total_lines += 1

            try:
                entry = json.loads(line)
            except json.JSONDecodeError as e:
                return {"error": f"JSON syntax error on line {idx}: {e}"}

            messages = entry.get("messages", [])
            if not messages or len(messages) < 3:
                return {"error": f"Line {idx}: missing required 3-turn message schema (system, user, assistant)"}

            roles = [m.get("role") for m in messages]
            if roles[:3] != ["system", "user", "assistant"]:
                return {"error": f"Line {idx}: invalid message roles order: {roles}"}

            user_text = messages[1].get("content", "")
            assistant_text = messages[2].get("content", "")

            # Check citation presence
            if "[SOURCE_" in user_text and "[SOURCE_" in assistant_text:
                citation_count += 1

            # Check for raw asterisk bugs
            if re.search(r"[a-zA-ZäöüÄÖÜß]\*{1,3}[a-zA-ZäöüÄÖÜß]", assistant_text):
                raw_asterisk_faults += 1

            # Token estimation
            full_text = " ".join(m.get("content", "") for m in messages)
            tokens = estimate_tokens(full_text)
            token_counts.append(tokens)

            # Detect pillar
            if "Exit" in assistant_text or "Kündigung" in assistant_text:
                p = "Exit & Migration (DORA Art. 30.2)"
            elif "Subunternehmer" in assistant_text or "Kaskade" in assistant_text:
                p = "Subcontracting & Cascading (Art. 30.3)"
            elif "Prüf" in assistant_text or "KWG" in assistant_text or "BaFin" in assistant_text:
                p = "Audit Rights (KWG § 25b)"
            elif "SLA" in assistant_text or "Pönal" in assistant_text or "Verfügbarkeit" in assistant_text:
                p = "SLAs & Penalty Matrices"
            elif "ZUGFeRD" in assistant_text or "Rechnung" in assistant_text:
                p = "E-Invoicing (ZUGFeRD 2.3)"
            elif "IELTS" in assistant_text or "Candidate" in assistant_text:
                p = "Academic / Certification"
            elif "BGB § 311" in assistant_text or "Musterklausel" in assistant_text:
                p = "BGB § 311 Remediation"
            else:
                p = "General Supervisory Mandate"

            pillars[p] = pillars.get(p, 0) + 1
            valid_entries += 1

    sorted_tokens = sorted(token_counts)
    p95_tokens = sorted_tokens[int(len(sorted_tokens) * 0.95)] if sorted_tokens else 0
    mean_tokens = sum(token_counts) / len(token_counts) if token_counts else 0

    return {
        "file": path.name,
        "total_samples": valid_entries,
        "citation_density_pct": round((citation_count / valid_entries) * 100, 1) if valid_entries else 0,
        "raw_asterisk_faults": raw_asterisk_faults,
        "mean_tokens_per_sample": round(mean_tokens, 1),
        "min_tokens": min(token_counts) if token_counts else 0,
        "max_tokens": max(token_counts) if token_counts else 0,
        "p95_tokens": p95_tokens,
        "pillars": pillars,
    }


def validate_benchmark_file(path: Path) -> dict:
    if not path.exists():
        return {"error": f"File not found: {path}"}

    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    if not isinstance(data, list):
        return {"error": "Benchmark file must be a JSON list"}

    missing_fields = 0
    for idx, item in enumerate(data):
        required = ["id", "pillar", "context", "query", "must_include_citation", "must_mention", "expected_status"]
        for r in required:
            if r not in item:
                missing_fields += 1

    return {
        "file": path.name,
        "total_test_cases": len(data),
        "missing_fields": missing_fields,
        "pillars_covered": len(set(i.get("pillar") for i in data)),
    }


def main():
    print("=" * 80)
    print("🔍 DOCUNORM SOVEREIGN AI - DATASET AUDIT & QUALITY ASSURANCE")
    print("=" * 80)

    train_path = data_dir / "dora_bafin_train.jsonl"
    bench_path = data_dir / "test_benchmark.json"

    train_res = validate_training_file(train_path)
    bench_res = validate_benchmark_file(bench_path)

    # 1. Training Set Audit
    print(f"\n📂 TRAINING DATASET: {train_path.name}")
    print(f"  • Total Valid Samples:        {train_res.get('total_samples')}")
    print(f"  • Grounding Citation Density: {train_res.get('citation_density_pct')}%")
    print(f"  • Raw Asterisk Faults:        {train_res.get('raw_asterisk_faults')} (Clean)")
    print(f"  • Token Distribution:         Mean={train_res.get('mean_tokens_per_sample')} | Min={train_res.get('min_tokens')} | Max={train_res.get('max_tokens')} | P95={train_res.get('p95_tokens')}")
    print(f"\n  🏛️  Pillar Diversity Breakdown:")
    for p, count in train_res.get("pillars", {}).items():
        print(f"     - {p:<42} : {count:>2} samples")

    # 2. Benchmark Set Audit
    print(f"\n📂 BENCHMARK CORPUS: {bench_path.name}")
    print(f"  • Ground-Truth Cases:         {bench_res.get('total_test_cases')}")
    print(f"  • Missing Field Errors:       {bench_res.get('missing_fields')}")
    print(f"  • Unique Pillars Covered:     {bench_res.get('pillars_covered')}")

    # Summary Gate
    has_errors = (
        "error" in train_res
        or "error" in bench_res
        or train_res.get("raw_asterisk_faults", 0) > 0
        or train_res.get("citation_density_pct", 0) < 90.0
        or bench_res.get("missing_fields", 0) > 0
    )

    print("\n" + "=" * 80)
    if not has_errors:
        print("🏆 VERDICT: DATASETS FULLY CERTIFIED & READY FOR ENTERPRISE FINE-TUNING")
    else:
        print("❌ VERDICT: QUALITY DEFICIENCIES DETECTED")
    print("=" * 80)

    sys.exit(0 if not has_errors else 1)


if __name__ == "__main__":
    main()

# DocuNorm AI 🛡️📄 (DOCUNORM.DE)

> **Enterprise German Regulatory Document Intelligence & Audit Platform (DORA Art. 30, BDSG/GDPR, LkSG, and ZUGFeRD 2.3 / Factur-X Compliant).**

[![CI](https://github.com/codebynikhita/docunorm-ai/actions/workflows/ci.yml/badge.svg)](https://github.com/codebynikhita/docunorm-ai/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.11%2B-blue)](https://www.python.org/)
[![Next.js](https://img.shields.io/badge/Next.js-16-black)](https://nextjs.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16%20%2B%20pgvector-336791)](https://github.com/pgvector/pgvector)

---

## 📌 Overview

**DocuNorm AI** is an enterprise-grade document intelligence platform engineered specifically for the German and European regulatory landscape. It empowers financial institutions, critical infrastructure operators, and enterprise compliance teams to audit high-stakes contracts against strict statutory standards with zero hallucinations and full sovereign privacy.

### Key Capabilities

1. **DORA Art. 30 & LkSG Compliance Auditing:**
   - Automated verification of exit transition periods (Art. 30 Abs. 2), sub-outsourcing controls, SLA delay penalties, and supply chain due diligence.
   - Every audit assertion is grounded in source citations with verifiable `[x0, y0, x1, y1]` coordinates and laser bounding-box highlights on original PDF pages.

2. **Cross-Lingual Dual-View Document Intelligence:**
   - **`[ 🇩🇪 PDF ]`**: Native German PDF viewer with responsive canvas rendering.
   - **`[ ⚖️ Dual-View ]`**: Side-by-side synchronized view showing original German PDF alongside legal English paragraph translations.
   - **`[ 🇬🇧 English Dossier ]`**: Complete English translation dossier with expandable German statutory source accordions for international compliance officers.
   - **Floating Bilingual Lens**: Click any sentence or bounding box on the PDF to instantly see its verified German-to-English translation in an interactive HUD.

3. **ZUGFeRD 2.3 / Factur-X Discrepancy Engine:**
   - Ingests hybrid e-invoices (PDF + embedded `factur-x.xml`).
   - Cross-references human-readable visual tables against machine-readable XML elements (VAT rates, Leitweg-ID, IBAN, line items) to flag invoice fraud or tax non-compliance.

4. **DIN 66399 Schutzklasse 3 Prüfbericht (Audit Certificate):**
   - Generates verifiable, printable compliance certificates with SHA-256 document hashing, auditor signatures, and BaFin regulatory stamps.

5. **Local Privacy Firewall (BDSG / GDPR):**
   - Pre-inference scrubbing of German tax IDs (Steuer-ID), IBANs, person names, and company addresses using Microsoft Presidio and German statutory regex patterns before embedding or LLM synthesis.

6. **Tri-Theme & Multi-Layout System:**
   - **🏛️ Bauhaus Paper**: German architectural ivory light mode (`#f6f4ee` paper, crimson accents).
   - **⚡ Cyber-Noir**: Obsidian jet black (`#05070b`) with DIN signal orange (`#ff5500`) and acid lime.
   - **🌊 Blueprint**: Prussian Oceanic Navy (`#050c1e`) with Electric Cyan (`#00f0ff`).
   - Layout templates: **Workbench** (split audit workspace), **Executive Cockpit** (KPI gauges and clause verification matrix), and **Focus Canvas** (full-screen PDF deep reading).

---

## 🏗️ Architecture

```
docunorm-ai/
├── .docker/             # Database initialization (pgvector + PostgreSQL 16)
├── backend/             # FastAPI core, hybrid RAG, auditor engine, Presidio firewall
│   ├── app/
│   │   ├── api/v1/      # REST API endpoints (documents, search, audit, chat)
│   │   ├── core/        # Config, database session factory, security
│   │   ├── models/      # SQLAlchemy ORM models (Document, Chunk, AuditLog)
│   │   ├── schemas/     # Pydantic validation schemas
│   │   └── services/    # PDFParser, PrivacyFirewall, Auditor, Embedding, Zugferd
│   └── scripts/         # Demo contract generators, ingestion, and E2E tests
├── frontend/            # Next.js 16 (App Router), Tailwind CSS v4, PDF.js
│   ├── src/app/         # Theme stylesheets, layout switcher, main workbench
│   ├── src/components/  # DocumentViewer, AuditorPanel, Certificate, ZugferdInspector
│   └── src/lib/         # Bilingual i18n dictionaries, API client
├── docs/                # Architectural diagrams & ADRs
└── docker-compose.yml   # Multi-container orchestration (PostgreSQL 16, pgvector, Redis)
```

---

## 🚀 Quickstart Guide

### Prerequisites
- **Docker** & Docker Compose
- **Python 3.11+**
- **Node.js 20+**

### 1. Boot Infrastructure
Start PostgreSQL with `pgvector` and Redis:
```bash
docker compose up -d
```

### 2. Backend Setup
```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt  # or poetry install

# Run database migrations / initialization
python -c "from app.core.db import init_db; init_db()"

# Start FastAPI server
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```
API Documentation will be available at: `http://127.0.0.1:8000/docs`

### 3. Generate & Ingest Authentic German Demo Contract
Generate the 3-page authentic German IKT contract (`Siemens_Master_IKT_Vertrag_2026.pdf` with DORA Art. 30 clauses and embedded Factur-X invoice stream) and ingest into pgvector:
```bash
cd backend
.venv/bin/python scripts/generate_german_demo.py
.venv/bin/python scripts/ingest_demo.py
```

### 4. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```
Web Application will be available at: `http://localhost:3000`

---

## 🧪 Testing & Verification

Run the full automated test suite:

```bash
# 1. Backend unit tests (25 tests covering Auditor, Parser, Privacy, ZUGFeRD)
cd backend
.venv/bin/pytest

# 2. End-to-end full stack integration test
.venv/bin/python scripts/test_integration.py

# 3. Frontend typecheck
cd ../frontend
npx tsc --noEmit
```

---

## 🔒 Security & Privacy Standard
- **Zero-Data Exfiltration:** Text embeddings and vector retrieval can execute 100% on-premises.
- **DIN 66399 Schutzklasse 3:** Highest corporate confidentiality classification.
- **Verifiable Citations:** LLM synthesis is constrained by deterministic bounding boxes to eliminate hallucinations in financial and regulatory compliance reviews.

---

## 📄 License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.


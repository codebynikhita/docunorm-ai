# DocuNorm AI 🛡️📄

> **Enterprise-grade, privacy-first document intelligence and regulatory audit platform (GDPR & EU AI Act compliant).**

[![CI](https://github.com/codebynikhita/docunorm-ai/actions/workflows/ci.yml/badge.svg)](https://github.com/codebynikhita/docunorm-ai/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.11%2B-blue)](https://www.python.org/)
[![Next.js](https://img.shields.io/badge/Next.js-15-black)](https://nextjs.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16%20%2B%20pgvector-336791)](https://github.com/pgvector/pgvector)

---

## 📌 Overview

DocuNorm AI is engineered for European enterprises requiring rigorous compliance (GDPR, EU AI Act, ZUGFeRD / XRechnung standards) when auditing complex corporate documents (contracts, financial balance sheets, and regulatory filings).

### Key Features
- **Local PII Redaction Firewall:** Pre-inference scrubbing of German tax IDs (Steuer-ID), IBANs, person names, and addresses via Microsoft Presidio & custom regex rules.
- **Hybrid Retrieval Engine:** Combines BM25 lexical keyword matching with dense multilingual embeddings (`BAAI/bge-m3`) and cross-encoder re-ranking (`BAAI/bge-reranker-large`).
- **Interactive Audit Workbench:** Next.js 15 dual-pane workspace featuring real-time token streaming and dynamic PDF.js bounding-box highlight citations.
- **Sovereign Infrastructure:** Single ACID-compliant PostgreSQL 16 database storing relational entities, audit logs, and dense vectors (`pgvector`).

---

## 🏗️ Architecture

See our [Architecture Decision Records (ADRs)](./docs/adr/) for detailed justifications of technical trade-offs.

```
docunorm-ai/
├── .docker/             # Database initialization and container manifests
├── backend/             # FastAPI asynchronous core, parsing pipeline, RAG engine
├── frontend/            # Next.js 15 App Router, Tailwind CSS, shadcn/ui, PDF.js
├── docs/                # Architectural diagrams, ADRs, compliance documentation
├── docker-compose.yml   # Multi-container orchestration (PostgreSQL + pgvector, Redis)
├── .env.example         # Environment template with documented defaults
└── README.md
```

---

## 🚀 Quickstart (Local Development)

### Prerequisites
- [Docker](https://docs.docker.com/get-docker/) & Docker Compose
- Python 3.11+
- Node.js 20+

### 1. Clone & Configure Environment
```bash
git clone https://github.com/codebynikhita/docunorm-ai.git
cd docunorm-ai
cp .env.example .env
```

### 2. Boot Core Infrastructure
Start PostgreSQL (with `pgvector` pre-installed) and Redis:
```bash
docker compose up -d
```

Verify service health:
```bash
docker compose ps
```

# ADR 0001: Selection of PostgreSQL 16 with `pgvector` for Relational & Vector Storage

## Status
Accepted

## Date
2026-10-17

## Context & Problem Statement
DocuNorm AI requires storage for:
1. Relational domain entities: Tenants, Users, Document metadata, Bounding-box annotations, and GDPR audit trails.
2. High-dimensional vector embeddings: Dense representations of document chunks generated via multilingual models (`BAAI/bge-m3`, 1024 dimensions).
3. Lexical search tokens: Keyword and German compound word matching (BM25 / Full-Text Search).

Modern architectures often introduce standalone vector databases (e.g., Pinecone, Chroma, Milvus, Qdrant). We must evaluate whether a dedicated vector database or an extended relational engine best aligns with European enterprise requirements (GDPR, data sovereignty, ACID transactions, operational overhead).

## Decision
We select **PostgreSQL 16 with the `pgvector` extension** as our unified primary database and vector store, backed by `Redis 7` for ephemeral task queuing and caching.

## Rationale & Benefits for European Enterprise
1. **ACID Transactions Across Relational & Vector Data:**
   When a document chunk is inserted, updated, or purged under GDPR "Right to be Forgotten" (Article 17), both the relational metadata (tenant ID, audit log, access permissions) and the vector embeddings are updated atomically within a single transaction. Standalone vector DBs require two-phase commits or eventual consistency, risking orphaned PII vectors.
2. **Data Sovereignty & On-Premises Compliance:**
   Most German enterprises (Mittelstand & DAX companies) forbid piping un-anonymized document vectors into US-hosted SaaS vector databases. PostgreSQL + pgvector can run entirely on-premise, inside sovereign European cloud infrastructure (Hetzner, Open Telekom Cloud), or in self-hosted Kubernetes clusters.
3. **Hybrid Search in a Single Query:**
   PostgreSQL natively supports lexical Full-Text Search (with German language dictionaries) alongside dense vector similarity search (cosine distance via HNSW / IVFFlat indexes). This enables Reciprocal Rank Fusion (RRF) directly in the database layer.
4. **Zero Extra Infrastructure Overhead:**
   Every mature engineering team already possesses PostgreSQL backup, replication, monitoring, and security tooling. Introducing a specialized vector DB increases operational burden with minimal latency benefit at our target scale.

## Consequences
- **Positive:**
  - Single source of truth for all structured and unstructured data.
  - Simplified backup, disaster recovery, and GDPR compliance audits.
  - Native indexing options: HNSW (Hierarchical Navigable Small World) for fast approximate nearest neighbor search.
- **Negative / Trade-offs:**
  - Extremely high vector dimensions (>2000) or massive scale (>100M vectors) require careful index memory tuning (`maintenance_work_mem`, `shared_buffers`). For `bge-m3` (1024 dimensions) and enterprise-scale audits (<1M chunks), performance is optimal.

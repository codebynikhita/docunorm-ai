-- ==============================================================================
-- DocuNorm AI: Database Initialization Script
-- Executed on container startup only when the data directory is clean
-- ==============================================================================

-- Enable pgvector extension for high-dimensional vector similarity search
CREATE EXTENSION IF NOT EXISTS vector;

-- Enable UUID extension for cryptographically sound primary keys
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Enable pg_trgm for fuzzy string matching / German compound keyword search
CREATE EXTENSION IF NOT EXISTS pg_trgm;

-- Apex PostgreSQL Initialization Script
-- Runs on first database creation (mounted to /docker-entrypoint-initdb.d/)

-- Enable pgvector extension for embedding similarity search
CREATE EXTENSION IF NOT EXISTS vector;

-- Enable pg_trgm for fuzzy text search (used by ticker lookups)
CREATE EXTENSION IF NOT EXISTS pg_trgm;

-- Enable uuid-ossp for UUID generation
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Verify extensions loaded
DO $$
BEGIN
    RAISE NOTICE 'Apex DB initialized — extensions: vector, pg_trgm, uuid-ossp';
END
$$;

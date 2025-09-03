-- Initialize database with extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- Create initial tables will be handled by Alembic migrations
-- This file is for database-level setup only

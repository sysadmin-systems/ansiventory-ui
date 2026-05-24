-- ==============================================================================
-- 01_extensions.sql
-- Extensões iniciais do banco de dados Ansiventory.
-- Executado automaticamente na criação do banco (uma única vez).
-- ==============================================================================

-- UUID como tipo de chave primária
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Funções criptográficas (pgcrypto)
CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- Pesquisa textual avançada
CREATE EXTENSION IF NOT EXISTS pg_trgm;

-- Estatísticas estendidas de queries (disponível no PG14+)
CREATE EXTENSION IF NOT EXISTS pg_stat_statements;

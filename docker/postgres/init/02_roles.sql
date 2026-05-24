-- ==============================================================================
-- 02_roles.sql
-- Criação de roles com privilégios separados por responsabilidade.
-- ==============================================================================

-- Role somente-leitura (relatórios, BI, etc.)
DO $$
BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'ansiventory_readonly') THEN
    CREATE ROLE ansiventory_readonly NOLOGIN;
  END IF;
END;
$$;

GRANT CONNECT ON DATABASE ansiventory TO ansiventory_readonly;
GRANT USAGE  ON SCHEMA public TO ansiventory_readonly;
ALTER DEFAULT PRIVILEGES IN SCHEMA public
  GRANT SELECT ON TABLES TO ansiventory_readonly;

-- Role de aplicação (sem DDL, apenas DML)
DO $$
BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'ansiventory_app') THEN
    CREATE ROLE ansiventory_app NOLOGIN;
  END IF;
END;
$$;

GRANT CONNECT ON DATABASE ansiventory TO ansiventory_app;
GRANT USAGE  ON SCHEMA public TO ansiventory_app;
ALTER DEFAULT PRIVILEGES IN SCHEMA public
  GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES    TO ansiventory_app;
ALTER DEFAULT PRIVILEGES IN SCHEMA public
  GRANT USAGE, SELECT ON SEQUENCES TO ansiventory_app;

-- Associa o usuário principal ao role de aplicação
GRANT ansiventory_app TO ansiventory;

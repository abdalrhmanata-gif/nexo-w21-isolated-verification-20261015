-- Hosted read-only catalog query pack.
-- This file contains SELECT statements only. On hosted Development, run each
-- statement individually through a separately verified project-scoped
-- read_only=true connection; stop after Query 1 if the role gate fails.
-- This file is executed by CI only against a disposable local PostgreSQL 17 stack.

-- Query 1: session identity and effective role attributes.
SELECT
  pg_catalog.current_database() AS database_name,
  current_user AS current_user,
  session_user AS session_user,
  pg_catalog.current_setting('server_version_num')::integer AS server_version_num,
  pg_catalog.current_setting('transaction_read_only')::boolean AS transaction_read_only,
  r.rolsuper,
  r.rolcreatedb,
  r.rolcreaterole,
  r.rolcanlogin,
  r.rolbypassrls,
  (SELECT pg_catalog.to_regclass('supabase_migrations.schema_migrations')::text)
    AS migration_ledger_relation
FROM pg_catalog.pg_roles AS r
WHERE r.rolname = current_user;

-- Query 2: relevant role attributes.
SELECT
  r.rolname,
  r.rolsuper,
  r.rolinherit,
  r.rolcreaterole,
  r.rolcreatedb,
  r.rolcanlogin,
  r.rolreplication,
  r.rolbypassrls
FROM pg_catalog.pg_roles AS r
WHERE r.rolname IN (
  'postgres',
  'supabase_admin',
  'supabase_read_only_user',
  'anon',
  'authenticated',
  'service_role'
)
ORDER BY r.rolname;

-- Query 3: relevant role membership. PostgreSQL 17 exposes inherit_option/set_option.
SELECT
  member.rolname AS member_role,
  granted.rolname AS granted_role,
  m.admin_option,
  m.inherit_option,
  m.set_option
FROM pg_catalog.pg_auth_members AS m
JOIN pg_catalog.pg_roles AS member ON member.oid = m.member
JOIN pg_catalog.pg_roles AS granted ON granted.oid = m.roleid
WHERE member.rolname IN (
        'postgres', 'supabase_admin', 'supabase_read_only_user',
        'anon', 'authenticated', 'service_role'
      )
   OR granted.rolname IN (
        'postgres', 'supabase_admin', 'supabase_read_only_user',
        'anon', 'authenticated', 'service_role'
      )
ORDER BY member.rolname, granted.rolname;

-- Query 4: built-in global function ACL defaults (separate from pg_default_acl).
SELECT
  creator.rolname AS creator_role,
  CASE WHEN acl.grantee = 0 THEN 'PUBLIC'
       ELSE pg_catalog.pg_get_userbyid(acl.grantee) END AS grantee,
  acl.privilege_type,
  acl.is_grantable
FROM pg_catalog.pg_roles AS creator
CROSS JOIN LATERAL pg_catalog.aclexplode(
  pg_catalog.acldefault('f', creator.oid)
) AS acl
WHERE creator.rolname IN ('postgres', 'supabase_admin')
ORDER BY creator.rolname, grantee, acl.privilege_type;

-- Query 5: explicit global and schema-specific default ACL overrides.
SELECT
  creator.rolname AS creator_role,
  COALESCE(n.nspname, '<global>') AS schema_name,
  d.defaclobjtype AS object_type,
  CASE WHEN acl.grantee = 0 THEN 'PUBLIC'
       ELSE grantee.rolname END AS grantee,
  acl.privilege_type,
  acl.is_grantable
FROM pg_catalog.pg_default_acl AS d
JOIN pg_catalog.pg_roles AS creator ON creator.oid = d.defaclrole
LEFT JOIN pg_catalog.pg_namespace AS n ON n.oid = d.defaclnamespace
CROSS JOIN LATERAL pg_catalog.aclexplode(d.defaclacl) AS acl
LEFT JOIN pg_catalog.pg_roles AS grantee ON grantee.oid = acl.grantee
WHERE creator.rolname IN ('postgres', 'supabase_admin')
ORDER BY creator.rolname, schema_name, d.defaclobjtype, grantee, acl.privilege_type;

-- Query 6: relevant user-defined routines and effective EXECUTE privileges.
SELECT
  n.nspname AS schema_name,
  p.proname AS routine_name,
  pg_catalog.pg_get_function_identity_arguments(p.oid) AS identity_arguments,
  p.prokind AS routine_kind,
  pg_catalog.pg_get_userbyid(p.proowner) AS owner_role,
  p.prosecdef AS security_definer,
  p.proconfig AS routine_settings,
  p.proacl::text AS stored_acl,
  pg_catalog.has_function_privilege('anon', p.oid, 'EXECUTE') AS anon_execute,
  pg_catalog.has_function_privilege('authenticated', p.oid, 'EXECUTE') AS authenticated_execute,
  pg_catalog.has_function_privilege('service_role', p.oid, 'EXECUTE') AS service_role_execute
FROM pg_catalog.pg_proc AS p
JOIN pg_catalog.pg_namespace AS n ON n.oid = p.pronamespace
WHERE p.prokind IN ('f', 'p')
  AND n.nspname NOT IN ('pg_catalog', 'information_schema')
  AND (
    n.nspname = 'public'
    OR pg_catalog.pg_get_userbyid(p.proowner) = 'supabase_admin'
    OR p.prosecdef
  )
ORDER BY n.nspname, p.proname, pg_catalog.pg_get_function_identity_arguments(p.oid);

-- Query 7: ledger table presence; hosted operators must stop if absent.
SELECT pg_catalog.to_regclass('supabase_migrations.schema_migrations')::text
  AS migration_ledger_relation;

-- Query 8: ledger contents. For a hosted run, execute only after Query 7
-- confirms the relation exists and Query 1 passed; compare versions/names
-- to the exact checked-in migration set and stop on any mismatch.
SELECT version, name
FROM supabase_migrations.schema_migrations
ORDER BY version;

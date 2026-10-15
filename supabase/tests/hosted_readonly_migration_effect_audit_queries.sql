-- ZAVQERA hosted migration-effect catalog audit. SELECT-only metadata; no application rows.
-- Run only through the scoped Supabase Management API read-only endpoint.

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
  pg_catalog.to_regclass('supabase_migrations.schema_migrations')::text AS migration_ledger_relation
FROM pg_catalog.pg_roles AS r
WHERE r.rolname = current_user;

SELECT
  expected.schema_name,
  expected.relation_name,
  c.oid IS NOT NULL AS relation_exists,
  c.relkind AS relation_kind,
  pg_catalog.pg_get_userbyid(c.relowner) AS owner_role,
  c.relrowsecurity AS row_level_security_enabled,
  c.relforcerowsecurity AS row_level_security_forced
FROM (VALUES
  ('public','agent_executions'),
  ('public','mission_authority_budgets'),
  ('public','mission_authority_budget_reservations'),
  ('public','ai_usage_reservations'),
  ('public','mission_approvals'),
  ('public','workspace_invitations')
) AS expected(schema_name, relation_name)
LEFT JOIN pg_catalog.pg_namespace AS n ON n.nspname = expected.schema_name
LEFT JOIN pg_catalog.pg_class AS c
  ON c.relnamespace = n.oid AND c.relname = expected.relation_name
ORDER BY expected.schema_name, expected.relation_name;

SELECT
  expected.table_name,
  expected.column_name,
  a.attnum IS NOT NULL AS column_exists,
  pg_catalog.format_type(a.atttypid, a.atttypmod) AS data_type,
  a.attnotnull AS not_null,
  pg_catalog.pg_get_expr(d.adbin, d.adrelid) AS default_expression
FROM (VALUES
  ('agent_executions','dispatch_claimed_at'),
  ('agent_executions','dispatch_claim_authority_hash'),
  ('agent_executions','dispatch_claim_request_hash'),
  ('agent_executions','dispatch_claim_budget_revision'),
  ('agent_executions','reconciliation_claimed_at'),
  ('agent_executions','reconciliation_lease_expires_at'),
  ('agent_executions','reconciliation_claim_token'),
  ('agent_executions','research_claimed_at'),
  ('agent_executions','research_claim_request_hash'),
  ('agent_executions','research_claim_authority_hash'),
  ('agent_executions','research_claim_mission_version'),
  ('agent_executions','provider_receipt'),
  ('mission_authority_budgets','authority_revision'),
  ('mission_authority_budgets','authority_hash'),
  ('mission_authority_budgets','actions_reserved'),
  ('mission_authority_budgets','actions_consumed'),
  ('mission_authority_budgets','spend_reserved'),
  ('mission_authority_budgets','spend_consumed'),
  ('mission_authority_budgets','max_spend'),
  ('mission_authority_budget_reservations','budget_id'),
  ('mission_authority_budget_reservations','execution_id'),
  ('mission_authority_budget_reservations','status'),
  ('mission_authority_budget_reservations','charged_spend'),
  ('mission_authority_budget_reservations','settlement_reason'),
  ('ai_usage_reservations','generation_kind'),
  ('ai_usage_reservations','request_hash')
) AS expected(table_name, column_name)
LEFT JOIN pg_catalog.pg_namespace AS n ON n.nspname = 'public'
LEFT JOIN pg_catalog.pg_class AS c
  ON c.relnamespace = n.oid AND c.relname = expected.table_name
LEFT JOIN pg_catalog.pg_attribute AS a
  ON a.attrelid = c.oid AND a.attname = expected.column_name
 AND a.attnum > 0 AND NOT a.attisdropped
LEFT JOIN pg_catalog.pg_attrdef AS d
  ON d.adrelid = a.attrelid AND d.adnum = a.attnum
ORDER BY expected.table_name, expected.column_name;

SELECT
  expected.table_name,
  expected.constraint_name,
  con.oid IS NOT NULL AS constraint_exists,
  con.contype AS constraint_type,
  pg_catalog.pg_get_constraintdef(con.oid, true) AS definition
FROM (VALUES
  ('mission_authority_budgets','mission_authority_budgets_valid_window'),
  ('mission_authority_budgets','mission_authority_budgets_per_action_within_total'),
  ('mission_authority_budgets','mission_authority_budgets_action_accounting'),
  ('mission_authority_budgets','mission_authority_budgets_spend_accounting'),
  ('mission_authority_budgets','mission_authority_budgets_scope_revision_unique'),
  ('agent_executions','agent_executions_dispatch_claim_consistency'),
  ('agent_executions','agent_executions_reconciliation_claim_consistency'),
  ('agent_executions','agent_executions_research_claim_consistency'),
  ('ai_usage_reservations','ai_usage_reservations_state_check'),
  ('ai_usage_reservations','ai_usage_reservations_generation_kind_check'),
  ('ai_usage_reservations','ai_usage_reservations_request_hash_check')
) AS expected(table_name, constraint_name)
LEFT JOIN pg_catalog.pg_namespace AS n ON n.nspname = 'public'
LEFT JOIN pg_catalog.pg_class AS c
  ON c.relnamespace = n.oid AND c.relname = expected.table_name
LEFT JOIN pg_catalog.pg_constraint AS con
  ON con.conrelid = c.oid AND con.conname = expected.constraint_name
ORDER BY expected.table_name, expected.constraint_name;

SELECT
  expected.index_name,
  ic.oid IS NOT NULL AS index_exists,
  t.oid::regclass::text AS indexed_table,
  pg_catalog.pg_get_indexdef(ic.oid) AS definition,
  i.indisunique AS is_unique,
  i.indisvalid AS is_valid
FROM (VALUES
  ('mission_authority_budgets_one_active_scope_idx'),
  ('mission_authority_budgets_expiry_idx'),
  ('mission_authority_budgets_mission_idx'),
  ('mission_authority_budget_reservations_budget_status_idx'),
  ('mission_authority_budget_reservations_execution_status_idx'),
  ('agent_executions_dispatch_claimed_idx'),
  ('agent_executions_reconciliation_lease_idx'),
  ('agent_executions_research_claimed_idx')
) AS expected(index_name)
LEFT JOIN pg_catalog.pg_class AS ic
  ON ic.relname = expected.index_name AND ic.relkind IN ('i','I')
 AND ic.relnamespace = (SELECT oid FROM pg_catalog.pg_namespace WHERE nspname = 'public')
LEFT JOIN pg_catalog.pg_index AS i ON i.indexrelid = ic.oid
LEFT JOIN pg_catalog.pg_class AS t ON t.oid = i.indrelid
ORDER BY expected.index_name;

SELECT
  expected.signature,
  expected.should_exist,
  p.oid IS NOT NULL AS exists_now,
  (p.oid IS NOT NULL) = expected.should_exist AS expectation_matches,
  n.nspname AS schema_name,
  p.prokind AS routine_kind,
  pg_catalog.pg_get_userbyid(p.proowner) AS owner_role,
  p.prosecdef AS security_definer,
  p.proconfig AS routine_settings,
  p.proacl::text AS stored_acl,
  CASE WHEN p.oid IS NULL THEN NULL ELSE pg_catalog.has_function_privilege('anon', p.oid, 'EXECUTE') END AS anon_execute,
  CASE WHEN p.oid IS NULL THEN NULL ELSE pg_catalog.has_function_privilege('authenticated', p.oid, 'EXECUTE') END AS authenticated_execute,
  CASE WHEN p.oid IS NULL THEN NULL ELSE pg_catalog.has_function_privilege('service_role', p.oid, 'EXECUTE') END AS service_role_execute
FROM (VALUES
  ('private.configure_mission_authority_budget(uuid,uuid,uuid,bigint,numeric,numeric,text,timestamptz,timestamptz)',true),
  ('public.configure_mission_authority_budget(uuid,uuid,uuid,bigint,numeric,numeric,text,timestamptz,timestamptz)',true),
  ('private.revoke_mission_authority_budget(uuid)',true),
  ('public.revoke_mission_authority_budget(uuid)',true),
  ('private.reserve_agent_execution_budget(uuid,uuid)',true),
  ('private.settle_agent_execution_budget(uuid,text,jsonb)',true),
  ('private.claim_agent_execution_dispatch(uuid)',true),
  ('public.claim_agent_execution_dispatch(uuid)',true),
  ('private.claim_agent_execution_reconciliation(uuid)',true),
  ('public.claim_agent_execution_reconciliation(uuid)',true),
  ('private.reconcile_agent_execution_outcome(uuid,uuid,text,jsonb,jsonb)',true),
  ('public.reconcile_agent_execution_outcome(uuid,uuid,text,jsonb,jsonb)',true),
  ('private.reconcile_stale_agent_execution(uuid)',true),
  ('public.reconcile_stale_agent_execution(uuid)',true),
  ('private.record_mission_event(uuid,text,jsonb)',true),
  ('public.record_mission_event(uuid,text,jsonb)',true),
  ('private.guard_external_execution_success_receipt()',true),
  ('private.complete_read_only_research_execution(uuid,uuid,text,jsonb,jsonb,text,text)',true),
  ('public.complete_read_only_research_execution(uuid,uuid,text,jsonb,jsonb,text,text)',true),
  ('private.complete_read_only_research_execution(uuid,text,jsonb,jsonb,text,text)',false),
  ('public.complete_read_only_research_execution(uuid,text,jsonb,jsonb,text,text)',false),
  ('private.claim_read_only_research_execution(uuid,uuid,text)',true),
  ('public.claim_read_only_research_execution(uuid,uuid,text)',true),
  ('private.reserve_ai_generation(text,text,text)',true),
  ('public.reserve_ai_generation(text,text,text)',true),
  ('private.reserve_ai_generation(text)',false),
  ('public.reserve_ai_generation(text)',false),
  ('private.consume_ai_generation(uuid)',true),
  ('private.release_ai_generation(uuid)',true),
  ('private.can_edit_workspace(uuid,uuid)',true),
  ('private.create_workspace_invitation(uuid,text,text,text,timestamptz)',true),
  ('public.create_workspace_invitation(uuid,text,text,text,timestamptz)',true),
  ('private.get_workspace_invitation(text)',true),
  ('public.get_workspace_invitation(text)',true),
  ('private.accept_workspace_invitation(text)',true),
  ('public.accept_workspace_invitation(text)',true),
  ('private.revoke_workspace_invitation(uuid)',true),
  ('public.revoke_workspace_invitation(uuid)',true),
  ('private.complete_agent_execution(uuid,text,jsonb,jsonb,text,text)',true),
  ('public.complete_agent_execution(uuid,text,jsonb,jsonb,text,text)',true)
) AS expected(signature, should_exist)
LEFT JOIN LATERAL (SELECT pg_catalog.to_regprocedure(expected.signature) AS oid) AS resolved ON true
LEFT JOIN pg_catalog.pg_proc AS p ON p.oid = resolved.oid
LEFT JOIN pg_catalog.pg_namespace AS n ON n.oid = p.pronamespace
ORDER BY expected.signature;

SELECT
  access.source_kind,
  access.grantee,
  access.privilege_type,
  access.is_grantable,
  access.effective_private_usage
FROM (
  SELECT
    'EFFECTIVE_ROLE'::text AS source_kind,
    r.rolname AS grantee,
    'USAGE'::text AS privilege_type,
    NULL::boolean AS is_grantable,
    pg_catalog.has_schema_privilege(r.rolname, 'private', 'USAGE') AS effective_private_usage
  FROM pg_catalog.pg_roles AS r
  WHERE r.rolname IN ('anon','authenticated','service_role')
  UNION ALL
  SELECT
    'STORED_ACL'::text,
    CASE WHEN a.grantee = 0 THEN 'PUBLIC' ELSE gr.rolname END,
    a.privilege_type,
    a.is_grantable,
    NULL::boolean
  FROM pg_catalog.pg_namespace AS n
  CROSS JOIN LATERAL pg_catalog.aclexplode(COALESCE(n.nspacl, pg_catalog.acldefault('n', n.nspowner))) AS a
  LEFT JOIN pg_catalog.pg_roles AS gr ON gr.oid = a.grantee
  WHERE n.nspname = 'private' AND a.privilege_type = 'USAGE'
) AS access
ORDER BY access.source_kind, access.grantee;

SELECT
  expected.trigger_name,
  t.oid IS NOT NULL AS trigger_exists,
  p.oid::regprocedure::text AS trigger_function,
  t.tgenabled AS trigger_enabled_state,
  pg_catalog.pg_get_triggerdef(t.oid, true) AS trigger_definition
FROM (VALUES ('agent_execution_success_receipt_guard')) AS expected(trigger_name)
LEFT JOIN pg_catalog.pg_class AS c ON c.oid = pg_catalog.to_regclass('public.agent_executions')
LEFT JOIN pg_catalog.pg_trigger AS t
  ON t.tgrelid = c.oid AND t.tgname = expected.trigger_name AND NOT t.tgisinternal
LEFT JOIN pg_catalog.pg_proc AS p ON p.oid = t.tgfoid;

SELECT
  n.nspname AS schema_name,
  p.oid::regprocedure::text AS signature,
  p.prosecdef AS security_definer,
  p.proconfig AS routine_settings,
  pg_catalog.pg_get_userbyid(p.proowner) AS owner_role,
  pg_catalog.pg_get_functiondef(p.oid) AS function_definition
FROM pg_catalog.pg_proc AS p
JOIN pg_catalog.pg_namespace AS n ON n.oid = p.pronamespace
WHERE n.nspname IN ('public','private')
  AND p.proname IN (
    'can_edit_workspace', 'record_mission_event', 'get_workspace_invitation',
    'create_workspace_invitation', 'accept_workspace_invitation', 'revoke_workspace_invitation',
    'reserve_ai_generation', 'complete_read_only_research_execution',
    'claim_agent_execution_dispatch', 'claim_agent_execution_reconciliation',
    'reconcile_agent_execution_outcome', 'claim_read_only_research_execution',
    'guard_external_execution_success_receipt', 'reconcile_stale_agent_execution'
  )
ORDER BY n.nspname, p.proname, p.oid::regprocedure::text;

SELECT
  acl_rows.source_kind,
  acl_rows.creator_role,
  acl_rows.schema_name,
  acl_rows.grantee,
  acl_rows.privilege_type,
  acl_rows.is_grantable
FROM (
  SELECT
    'BUILTIN_GLOBAL_BASELINE'::text AS source_kind,
    creator.rolname AS creator_role,
    '<global>'::text AS schema_name,
    CASE WHEN a.grantee = 0 THEN 'PUBLIC' ELSE pg_catalog.pg_get_userbyid(a.grantee) END AS grantee,
    a.privilege_type,
    a.is_grantable
  FROM pg_catalog.pg_roles AS creator
  CROSS JOIN LATERAL pg_catalog.aclexplode(pg_catalog.acldefault('f', creator.oid)) AS a
  WHERE creator.rolname IN ('postgres','supabase_admin')
  UNION ALL
  SELECT
    'EXPLICIT_DEFAULT_ACL'::text,
    creator.rolname,
    COALESCE(ns.nspname, '<global>'),
    CASE WHEN a.grantee = 0 THEN 'PUBLIC' ELSE gr.rolname END,
    a.privilege_type,
    a.is_grantable
  FROM pg_catalog.pg_default_acl AS d
  JOIN pg_catalog.pg_roles AS creator ON creator.oid = d.defaclrole
  LEFT JOIN pg_catalog.pg_namespace AS ns ON ns.oid = d.defaclnamespace
  CROSS JOIN LATERAL pg_catalog.aclexplode(d.defaclacl) AS a
  LEFT JOIN pg_catalog.pg_roles AS gr ON gr.oid = a.grantee
  WHERE creator.rolname IN ('postgres','supabase_admin')
    AND d.defaclobjtype = 'f'
    AND (d.defaclnamespace = 0 OR ns.nspname = 'public')
) AS acl_rows
ORDER BY creator_role, source_kind, schema_name, grantee, privilege_type;

-- Query 11: enumerate version/name pairs only; no SQL bodies or application rows.
SELECT
  version::text AS version,
  name::text AS name
FROM supabase_migrations.schema_migrations
ORDER BY version::text, name::text;

-- Query 12: W66 relation ACL, including effective grants and expanded stored ACL.
-- This is catalog metadata only; do not broaden this role into application-row reads.
SELECT
  'EFFECTIVE_PRIVILEGE'::text AS evidence_kind,
  t.schema_name,
  t.relation_name,
  t.owner_role,
  t.row_level_security_enabled,
  t.row_level_security_forced,
  roles.rolname AS grantee,
  privileges.privilege_type,
  pg_catalog.has_table_privilege(roles.oid, t.relation_oid, privileges.privilege_type) AS effective_privilege,
  NULL::boolean AS is_grantable,
  NULL::text AS grantor
FROM (
  SELECT c.oid AS relation_oid, n.nspname AS schema_name, c.relname AS relation_name,
    pg_catalog.pg_get_userbyid(c.relowner) AS owner_role, c.relowner AS owner_oid,
    c.relacl AS relation_acl, c.relrowsecurity AS row_level_security_enabled,
    c.relforcerowsecurity AS row_level_security_forced
  FROM pg_catalog.pg_class AS c
  JOIN pg_catalog.pg_namespace AS n ON n.oid = c.relnamespace
  WHERE n.nspname = 'public' AND c.relname = 'agent_executions' AND c.relkind IN ('r', 'p')
) AS t
CROSS JOIN pg_catalog.pg_roles AS roles
CROSS JOIN (VALUES ('SELECT'), ('INSERT'), ('UPDATE'), ('DELETE'), ('TRUNCATE'), ('REFERENCES'), ('TRIGGER'), ('MAINTAIN')) AS privileges(privilege_type)
WHERE roles.rolname IN ('anon', 'authenticated', 'service_role', 'postgres')
UNION ALL
SELECT
  'STORED_ACL'::text AS evidence_kind, t.schema_name, t.relation_name, t.owner_role,
  t.row_level_security_enabled, t.row_level_security_forced,
  CASE WHEN a.grantee = 0 THEN 'PUBLIC' ELSE grantee_role.rolname END AS grantee,
  a.privilege_type, NULL::boolean AS effective_privilege, a.is_grantable,
  pg_catalog.pg_get_userbyid(a.grantor) AS grantor
FROM (
  SELECT c.oid AS relation_oid, n.nspname AS schema_name, c.relname AS relation_name,
    pg_catalog.pg_get_userbyid(c.relowner) AS owner_role, c.relowner AS owner_oid,
    c.relacl AS relation_acl, c.relrowsecurity AS row_level_security_enabled,
    c.relforcerowsecurity AS row_level_security_forced
  FROM pg_catalog.pg_class AS c
  JOIN pg_catalog.pg_namespace AS n ON n.oid = c.relnamespace
  WHERE n.nspname = 'public' AND c.relname = 'agent_executions' AND c.relkind IN ('r', 'p')
) AS t
CROSS JOIN LATERAL pg_catalog.aclexplode(COALESCE(t.relation_acl, pg_catalog.acldefault('r', t.owner_oid))) AS a
LEFT JOIN pg_catalog.pg_roles AS grantee_role ON grantee_role.oid = a.grantee
ORDER BY evidence_kind, grantee, privilege_type;

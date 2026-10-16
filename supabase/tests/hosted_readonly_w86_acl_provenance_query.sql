-- W86 prerequisite: read-only privilege provenance probe.
-- Returns catalog metadata only; no writes, setting changes, or application rows.
-- Run with a verified read-only session before any owner-reviewed hosted proposal.
WITH RECURSIVE role_path (
  role_oid, role_name, depth, oid_path, inherits_all, member_role_name
) AS (
  SELECT r.oid, r.rolname, 0, ARRAY[r.oid]::oid[], true, NULL::text COLLATE "C"
    FROM pg_roles r
   WHERE r.rolname = 'service_role'
  UNION ALL
  SELECT parent.oid,
         parent.rolname,
         child.depth + 1,
         child.oid_path || parent.oid,
         child.inherits_all AND membership.inherit_option,
         child.role_name::text COLLATE "C"
    FROM role_path child
    JOIN pg_auth_members membership ON membership.member = child.role_oid
    JOIN pg_roles parent ON parent.oid = membership.roleid
   WHERE NOT parent.oid = ANY(child.oid_path)
),
target AS (
  SELECT to_regclass('public.agent_executions')::oid AS relid
)
SELECT jsonb_build_object(
  'probe_name', 'w86_acl_provenance_v1',
  'current_user', current_user,
  'session_user', session_user,
  'transaction_read_only', current_setting('transaction_read_only'),
  'relation', (
    SELECT CASE WHEN c.oid IS NULL THEN jsonb_build_object('exists', false)
                ELSE jsonb_build_object(
                  'exists', true,
                  'schema_name', n.nspname,
                  'relation_name', c.relname,
                  'owner_role', pg_get_userbyid(c.relowner),
                  'row_level_security_enabled', c.relrowsecurity,
                  'row_level_security_forced', c.relforcerowsecurity,
                  'stored_acl_is_null', c.relacl IS NULL)
           END
      FROM target t
      LEFT JOIN pg_class c ON c.oid = t.relid
      LEFT JOIN pg_namespace n ON n.oid = c.relnamespace
  ),
  'service_role_effective_privileges', (
    SELECT COALESCE(jsonb_object_agg(privilege_name,
      CASE WHEN t.relid IS NULL THEN NULL
           ELSE has_table_privilege('service_role', t.relid, privilege_name)
      END), '{}'::jsonb)
      FROM target t
      CROSS JOIN (VALUES
        ('SELECT'), ('INSERT'), ('UPDATE'), ('DELETE'),
        ('TRUNCATE'), ('REFERENCES'), ('TRIGGER'), ('MAINTAIN')
      ) AS privileges(privilege_name)
  ),
  'service_role_membership_paths', (
    SELECT COALESCE(jsonb_agg(jsonb_build_object(
      'role_name', rp.role_name,
      'depth', rp.depth,
      'member_of_role', rp.member_role_name,
      'all_edges_inherit', rp.inherits_all
    ) ORDER BY rp.depth, rp.role_name), '[]'::jsonb)
      FROM role_path rp
  ),
  'table_acl_entries', (
    SELECT COALESCE(jsonb_agg(jsonb_build_object(
      'grantee', CASE WHEN acl.grantee = 0 THEN 'PUBLIC' ELSE grantee_role.rolname END,
      'privilege_type', acl.privilege_type,
      'is_grantable', acl.is_grantable,
      'grantor', grantor_role.rolname
    ) ORDER BY COALESCE(grantee_role.rolname, 'PUBLIC'), acl.privilege_type), '[]'::jsonb)
      FROM target t
      JOIN pg_class c ON c.oid = t.relid
      CROSS JOIN LATERAL aclexplode(COALESCE(c.relacl, acldefault('r', c.relowner))) acl
      LEFT JOIN pg_roles grantee_role ON grantee_role.oid = acl.grantee
      LEFT JOIN pg_roles grantor_role ON grantor_role.oid = acl.grantor
  ),
  'column_acl_entries', (
    SELECT COALESCE(jsonb_agg(jsonb_build_object(
      'column_name', a.attname,
      'grantee', CASE WHEN acl.grantee = 0 THEN 'PUBLIC' ELSE grantee_role.rolname END,
      'privilege_type', acl.privilege_type,
      'is_grantable', acl.is_grantable,
      'grantor', grantor_role.rolname
    ) ORDER BY a.attnum, COALESCE(grantee_role.rolname, 'PUBLIC'), acl.privilege_type), '[]'::jsonb)
      FROM target t
      JOIN pg_attribute a ON a.attrelid = t.relid
      CROSS JOIN LATERAL aclexplode(a.attacl) acl
      LEFT JOIN pg_roles grantee_role ON grantee_role.oid = acl.grantee
      LEFT JOIN pg_roles grantor_role ON grantor_role.oid = acl.grantor
     WHERE a.attnum > 0 AND NOT a.attisdropped
  ),
  'service_role_inherited_table_acl_entries', (
    SELECT COALESCE(jsonb_agg(jsonb_build_object(
      'grantee_role', rp.role_name,
      'membership_depth', rp.depth,
      'all_membership_edges_inherit', rp.inherits_all,
      'privilege_type', acl.privilege_type,
      'is_grantable', acl.is_grantable,
      'grantor', grantor_role.rolname
    ) ORDER BY rp.depth, rp.role_name, acl.privilege_type), '[]'::jsonb)
      FROM role_path rp
      JOIN target t ON t.relid IS NOT NULL
      JOIN pg_class c ON c.oid = t.relid
      CROSS JOIN LATERAL aclexplode(COALESCE(c.relacl, acldefault('r', c.relowner))) acl
      LEFT JOIN pg_roles grantor_role ON grantor_role.oid = acl.grantor
     WHERE acl.grantee = rp.role_oid
       AND (rp.depth = 0 OR rp.inherits_all)
  ),
  'service_role_inherited_column_acl_entries', (
    SELECT COALESCE(jsonb_agg(jsonb_build_object(
      'column_name', a.attname,
      'grantee_role', rp.role_name,
      'membership_depth', rp.depth,
      'all_membership_edges_inherit', rp.inherits_all,
      'privilege_type', acl.privilege_type,
      'is_grantable', acl.is_grantable,
      'grantor', grantor_role.rolname
    ) ORDER BY a.attnum, rp.depth, rp.role_name, acl.privilege_type), '[]'::jsonb)
      FROM role_path rp
      JOIN target t ON t.relid IS NOT NULL
      JOIN pg_attribute a ON a.attrelid = t.relid
      CROSS JOIN LATERAL aclexplode(a.attacl) acl
      LEFT JOIN pg_roles grantor_role ON grantor_role.oid = acl.grantor
     WHERE a.attnum > 0 AND NOT a.attisdropped
       AND acl.grantee = rp.role_oid
       AND (rp.depth = 0 OR rp.inherits_all)
  )
) AS w86_acl_provenance;

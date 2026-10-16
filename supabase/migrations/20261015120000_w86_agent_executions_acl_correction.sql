-- W86: forward-only correction for the observed W66 table-ACL drift.
-- This migration restores the W65/W66 intended boundary:
--   * authenticated may SELECT history subject to RLS;
--   * anon and authenticated cannot mutate executions;
--   * service_role must use explicitly granted guarded RPCs, not the table.
-- It deliberately does not grant or revoke EXECUTE on any function.
-- Hosted application is blocked pending separate migration-history review and approval.

-- Do not silently claim a complete repair if service_role inherits ACLs from
-- another role. Revoking grants directly from service_role cannot remove those.
-- Inspect inherited parent-role ACLs first and stop before any mutation if found.
do $w86_inherited_acl_preflight$
declare
  inherited_entries text;
begin
  with recursive role_path (
    role_oid, role_name, depth, oid_path, inherits_all
  ) as (
    select r.oid, r.rolname, 0, array[r.oid]::oid[], true
      from pg_roles r
     where r.rolname = 'service_role'
    union all
    select parent.oid,
           parent.rolname,
           child.depth + 1,
           child.oid_path || parent.oid,
           child.inherits_all and membership.inherit_option
      from role_path child
      join pg_auth_members membership on membership.member = child.role_oid
      join pg_roles parent on parent.oid = membership.roleid
     where child.depth < 16
       and not parent.oid = any(child.oid_path)
  ),
  inherited_table_acl as (
    select rp.role_name,
           'table ' || acl.privilege_type as privilege_description
      from role_path rp
      join pg_class c on c.oid = 'public.agent_executions'::regclass
      cross join lateral aclexplode(coalesce(c.relacl, acldefault('r', c.relowner))) acl
     where rp.depth > 0
       and rp.inherits_all
       and acl.grantee = rp.role_oid
  ),
  inherited_column_acl as (
    select rp.role_name,
           format('column %I %s', a.attname, acl.privilege_type) as privilege_description
      from role_path rp
      join pg_attribute a on a.attrelid = 'public.agent_executions'::regclass
      cross join lateral aclexplode(a.attacl) acl
     where a.attnum > 0
       and not a.attisdropped
       and rp.depth > 0
       and rp.inherits_all
       and acl.grantee = rp.role_oid
  ),
  inherited_acl as (
    select role_name, privilege_description from inherited_table_acl
    union all
    select role_name, privilege_description from inherited_column_acl
  )
  select string_agg(
           format('%s via role %I', privilege_description, role_name),
           '; ' order by role_name, privilege_description
         )
    into inherited_entries
    from inherited_acl;

  if inherited_entries is not null then
    raise exception
      'W86 refused: service_role inherits agent_executions privileges from parent roles: %',
      inherited_entries;
  end if;
end
$w86_inherited_acl_preflight$;

revoke all privileges on table public.agent_executions
  from public, anon, authenticated, service_role;

-- Table-level REVOKE does not revoke column-level grants. Remove any such grants
-- too, so a legacy per-column ACL cannot bypass the table-level boundary.
do $w86$
declare
  column_names text;
begin
  select string_agg(format('%I', a.attname), ', ' order by a.attnum)
    into column_names
    from pg_attribute a
   where a.attrelid = 'public.agent_executions'::regclass
     and a.attnum > 0
     and not a.attisdropped;

  if column_names is not null then
    execute format(
      'revoke all privileges (%s) on table public.agent_executions from public, anon, authenticated, service_role',
      column_names
    );
  end if;
end
$w86$;

-- Re-establish the only direct table privilege intentionally retained for API roles.
grant select on table public.agent_executions to authenticated;

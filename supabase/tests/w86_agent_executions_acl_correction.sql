-- W86 regression: the forward correction restores the complete table/column ACL boundary.
-- Intended for the disposable PostgreSQL 17 replay only.
begin;
create extension if not exists pgtap;
select plan(22);

select ok(not has_table_privilege('service_role', 'public.agent_executions', 'SELECT'),
  'service_role cannot directly read execution rows');
select ok(not has_table_privilege('service_role', 'public.agent_executions', 'INSERT'),
  'service_role cannot directly insert execution rows');
select ok(not has_table_privilege('service_role', 'public.agent_executions', 'UPDATE'),
  'service_role cannot directly alter execution rows');
select ok(not has_table_privilege('service_role', 'public.agent_executions', 'DELETE'),
  'service_role cannot directly delete execution history');
select ok(not has_table_privilege('service_role', 'public.agent_executions', 'TRUNCATE'),
  'service_role cannot truncate execution history');
select ok(not has_table_privilege('service_role', 'public.agent_executions', 'REFERENCES'),
  'service_role cannot create direct foreign-key references');
select ok(not has_table_privilege('service_role', 'public.agent_executions', 'TRIGGER'),
  'service_role cannot attach direct triggers');
select ok(not has_table_privilege('service_role', 'public.agent_executions', 'MAINTAIN'),
  'PostgreSQL 17 MAINTAIN privilege is also denied');

select ok(not has_any_column_privilege('service_role', 'public.agent_executions', 'SELECT'),
  'service_role has no column-level SELECT bypass');
select ok(not has_any_column_privilege('service_role', 'public.agent_executions', 'INSERT'),
  'service_role has no column-level INSERT bypass');
select ok(not has_any_column_privilege('service_role', 'public.agent_executions', 'UPDATE'),
  'service_role has no column-level UPDATE bypass');
select ok(not has_any_column_privilege('service_role', 'public.agent_executions', 'REFERENCES'),
  'service_role has no column-level REFERENCES bypass');

select ok(not exists (
  select 1
    from pg_class c
    cross join lateral aclexplode(coalesce(c.relacl, acldefault('r', c.relowner))) a
   where c.oid = 'public.agent_executions'::regclass
     and (a.grantee = 0 or a.grantee = 'service_role'::regrole)
), 'stored table ACL has no PUBLIC or service_role privilege entries');

select ok(has_table_privilege('authenticated', 'public.agent_executions', 'SELECT'),
  'authenticated retains RLS-governed execution history reads');

select ok(
  not has_table_privilege('authenticated', 'public.agent_executions', 'INSERT')
  and not has_table_privilege('authenticated', 'public.agent_executions', 'UPDATE')
  and not has_table_privilege('authenticated', 'public.agent_executions', 'DELETE')
  and not has_table_privilege('authenticated', 'public.agent_executions', 'TRUNCATE')
  and not has_table_privilege('authenticated', 'public.agent_executions', 'REFERENCES')
  and not has_table_privilege('authenticated', 'public.agent_executions', 'TRIGGER')
  and not has_table_privilege('authenticated', 'public.agent_executions', 'MAINTAIN'),
  'authenticated receives no direct write or table-control privilege');

select ok(
  not has_table_privilege('anon', 'public.agent_executions', 'SELECT')
  and not has_table_privilege('anon', 'public.agent_executions', 'INSERT')
  and not has_table_privilege('anon', 'public.agent_executions', 'UPDATE')
  and not has_table_privilege('anon', 'public.agent_executions', 'DELETE')
  and not has_table_privilege('anon', 'public.agent_executions', 'TRUNCATE')
  and not has_table_privilege('anon', 'public.agent_executions', 'REFERENCES')
  and not has_table_privilege('anon', 'public.agent_executions', 'TRIGGER')
  and not has_table_privilege('anon', 'public.agent_executions', 'MAINTAIN'),
  'anon has no direct table privilege');

select ok(has_function_privilege('service_role',
  'public.complete_agent_execution(uuid,text,jsonb,jsonb,text,text)', 'EXECUTE'),
  'trusted service_role completion RPC remains executable');
select ok(has_function_privilege('service_role',
  'private.complete_agent_execution(uuid,text,jsonb,jsonb,text,text)', 'EXECUTE'),
  'private guarded completion implementation remains executable by the trusted worker');
select ok(not has_function_privilege('authenticated',
  'public.complete_agent_execution(uuid,text,jsonb,jsonb,text,text)', 'EXECUTE'),
  'authenticated cannot replace direct table access with trusted completion access');
select ok(not has_function_privilege('anon',
  'public.complete_agent_execution(uuid,text,jsonb,jsonb,text,text)', 'EXECUTE'),
  'anon cannot execute trusted completion');


select ok(not exists (
  with recursive role_path (
    role_oid, role_name, depth, oid_path, inherits_all, can_set_role, reachable_via_membership_options
  ) as (
    select r.oid, r.rolname, 0, array[r.oid]::oid[], true, true, true
      from pg_roles r
     where r.rolname = 'service_role'
    union all
    select parent.oid,
           parent.rolname,
           child.depth + 1,
           child.oid_path || parent.oid,
           child.inherits_all and membership.inherit_option,
           child.can_set_role and membership.set_option,
           (child.reachable_via_membership_options and membership.inherit_option)
             or (child.can_set_role and membership.set_option)
      from role_path child
      join pg_auth_members membership on membership.member = child.role_oid
      join pg_roles parent on parent.oid = membership.roleid
     where not parent.oid = any(child.oid_path)
  )
  select 1
    from role_path
   where depth > 0
     and role_name = 'authenticated'
     and reachable_via_membership_options
), 'service_role has no INHERIT or SET ROLE path to authenticated');

select ok(not exists (
  with recursive anon_role_path (
    role_oid, role_name, depth, oid_path, inherits_all, can_set_role, reachable_via_membership_options
  ) as (
    select r.oid, r.rolname, 0, array[r.oid]::oid[], true, true, true
      from pg_roles r
     where r.rolname = 'anon'
    union all
    select parent.oid,
           parent.rolname,
           child.depth + 1,
           child.oid_path || parent.oid,
           child.inherits_all and membership.inherit_option,
           child.can_set_role and membership.set_option,
           (child.reachable_via_membership_options and membership.inherit_option)
             or (child.can_set_role and membership.set_option)
      from anon_role_path child
      join pg_auth_members membership on membership.member = child.role_oid
      join pg_roles parent on parent.oid = membership.roleid
     where not parent.oid = any(child.oid_path)
  )
  select 1
    from anon_role_path
   where depth > 0
     and role_name = 'authenticated'
     and reachable_via_membership_options
), 'anon has no INHERIT or SET ROLE path to authenticated SELECT grant target');

select * from finish();
rollback;

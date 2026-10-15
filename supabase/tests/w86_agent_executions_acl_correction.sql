-- W86 regression: the forward correction restores the complete table/column ACL boundary.
-- Intended for the disposable PostgreSQL 17 replay only.
begin;
create extension if not exists pgtap;
select plan(20);

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

select * from finish();
rollback;

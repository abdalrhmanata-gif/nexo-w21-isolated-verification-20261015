-- W84: future functions created by postgres must not be executable by default.
-- Existing intended RPC grants must survive; this test creates only transaction-local probes.
begin;
create extension if not exists pgtap;
select plan(21);

select ok(exists (
  select 1 from pg_default_acl d
  where d.defaclrole = 'postgres'::regrole
    and d.defaclnamespace = 0
    and d.defaclobjtype = 'f'
), 'postgres has an explicit global function-default ACL override');

select ok(not exists (
  select 1
    from pg_default_acl d
    cross join lateral aclexplode(d.defaclacl) a
  where d.defaclrole = 'postgres'::regrole
    and d.defaclnamespace = 0
    and d.defaclobjtype = 'f'
    and a.privilege_type = 'EXECUTE'
    and a.grantee = 0
), 'future postgres-created functions do not grant EXECUTE to PUBLIC globally');

select ok(not exists (
  select 1
    from pg_default_acl d
    cross join lateral aclexplode(d.defaclacl) a
    left join pg_roles grantee_role on grantee_role.oid = a.grantee
  where d.defaclrole = 'postgres'::regrole
    and d.defaclnamespace = 0
    and d.defaclobjtype = 'f'
    and a.privilege_type = 'EXECUTE'
    and grantee_role.rolname = 'anon'
), 'future postgres-created functions have no global anon EXECUTE default');

select ok(not exists (
  select 1
    from pg_default_acl d
    cross join lateral aclexplode(d.defaclacl) a
    left join pg_roles grantee_role on grantee_role.oid = a.grantee
  where d.defaclrole = 'postgres'::regrole
    and d.defaclnamespace = 0
    and d.defaclobjtype = 'f'
    and a.privilege_type = 'EXECUTE'
    and grantee_role.rolname = 'authenticated'
), 'future postgres-created functions have no global authenticated EXECUTE default');

select ok(not exists (
  select 1
    from pg_default_acl d
    cross join lateral aclexplode(d.defaclacl) a
    left join pg_roles grantee_role on grantee_role.oid = a.grantee
  where d.defaclrole = 'postgres'::regrole
    and d.defaclnamespace = 0
    and d.defaclobjtype = 'f'
    and a.privilege_type = 'EXECUTE'
    and grantee_role.rolname = 'service_role'
), 'future postgres-created functions have no global service_role EXECUTE default');

select ok(not exists (
  select 1
    from pg_default_acl d
    cross join lateral aclexplode(d.defaclacl) a
  where d.defaclrole = 'postgres'::regrole
    and d.defaclnamespace = 'public'::regnamespace::oid
    and d.defaclobjtype = 'f'
    and a.privilege_type = 'EXECUTE'
    and a.grantee = 0
), 'public-schema function defaults do not reintroduce PUBLIC EXECUTE');

select ok(not exists (
  select 1
    from pg_default_acl d
    cross join lateral aclexplode(d.defaclacl) a
    left join pg_roles grantee_role on grantee_role.oid = a.grantee
  where d.defaclrole = 'postgres'::regrole
    and d.defaclnamespace = 'public'::regnamespace::oid
    and d.defaclobjtype = 'f'
    and a.privilege_type = 'EXECUTE'
    and grantee_role.rolname = 'anon'
), 'public-schema function defaults do not grant anon EXECUTE');

select ok(not exists (
  select 1
    from pg_default_acl d
    cross join lateral aclexplode(d.defaclacl) a
    left join pg_roles grantee_role on grantee_role.oid = a.grantee
  where d.defaclrole = 'postgres'::regrole
    and d.defaclnamespace = 'public'::regnamespace::oid
    and d.defaclobjtype = 'f'
    and a.privilege_type = 'EXECUTE'
    and grantee_role.rolname = 'authenticated'
), 'public-schema function defaults do not grant authenticated EXECUTE');

select ok(not exists (
  select 1
    from pg_default_acl d
    cross join lateral aclexplode(d.defaclacl) a
    left join pg_roles grantee_role on grantee_role.oid = a.grantee
  where d.defaclrole = 'postgres'::regrole
    and d.defaclnamespace = 'public'::regnamespace::oid
    and d.defaclobjtype = 'f'
    and a.privilege_type = 'EXECUTE'
    and grantee_role.rolname = 'service_role'
), 'public-schema function defaults do not grant service_role EXECUTE');

create function public.w84_default_acl_probe_public()
returns integer language sql immutable as $body$ select 1 $body$;

create function private.w84_default_acl_probe_private()
returns integer language sql immutable as $body$ select 1 $body$;

select ok(to_regprocedure('public.w84_default_acl_probe_public()') is not null,
  'public future-function probe was created');
select ok(to_regprocedure('private.w84_default_acl_probe_private()') is not null,
  'private future-function probe was created');

select ok(
  (select pg_get_userbyid(p.proowner) = 'postgres'
     from pg_proc p where p.oid = 'public.w84_default_acl_probe_public()'::regprocedure)
  and
  (select pg_get_userbyid(p.proowner) = 'postgres'
     from pg_proc p where p.oid = 'private.w84_default_acl_probe_private()'::regprocedure),
  'both probe functions are owned by the role whose defaults were hardened');

select ok(not has_function_privilege('anon', 'public.w84_default_acl_probe_public()', 'EXECUTE'),
  'anon cannot execute a new public function without an explicit grant');
select ok(not has_function_privilege('authenticated', 'public.w84_default_acl_probe_public()', 'EXECUTE'),
  'authenticated cannot execute a new public function without an explicit grant');
select ok(not has_function_privilege('service_role', 'public.w84_default_acl_probe_public()', 'EXECUTE'),
  'service_role cannot execute a new public function without an explicit grant');
select ok(not has_function_privilege('anon', 'private.w84_default_acl_probe_private()', 'EXECUTE'),
  'anon cannot execute a new private function without an explicit grant');
select ok(not has_function_privilege('authenticated', 'private.w84_default_acl_probe_private()', 'EXECUTE'),
  'authenticated cannot execute a new private function without an explicit grant');
select ok(not has_function_privilege('service_role', 'private.w84_default_acl_probe_private()', 'EXECUTE'),
  'service_role cannot execute a new private function without an explicit grant');

select ok(
  has_function_privilege('anon', 'public.get_workspace_invitation(text)', 'EXECUTE')
  and has_function_privilege('authenticated', 'public.get_workspace_invitation(text)', 'EXECUTE')
  and not has_function_privilege('service_role', 'public.get_workspace_invitation(text)', 'EXECUTE'),
  'the existing token-gated invitation GET ACL remains unchanged');
select ok(
  has_function_privilege('authenticated', 'public.get_ai_usage()', 'EXECUTE')
  and not has_function_privilege('anon', 'public.get_ai_usage()', 'EXECUTE'),
  'the existing authenticated quota RPC remains callable and anonymous access remains denied');
select ok(
  has_function_privilege('service_role', 'public.complete_read_only_research_execution(uuid,uuid,text,jsonb,jsonb,text,text)', 'EXECUTE')
  and not has_function_privilege('authenticated', 'public.complete_read_only_research_execution(uuid,uuid,text,jsonb,jsonb,text,text)', 'EXECUTE')
  and not has_function_privilege('anon', 'public.complete_read_only_research_execution(uuid,uuid,text,jsonb,jsonb,text,text)', 'EXECUTE'),
  'the existing trusted Research completion RPC grant remains intact');

select * from finish();
rollback;

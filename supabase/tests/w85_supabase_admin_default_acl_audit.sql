-- W85: audit function ACL defaults when supabase_admin is the actual creator.
-- Diagnostic coverage only: this file is run on disposable PostgreSQL 17.
-- No role impersonation is attempted; the temporary probe is rolled back.
begin;
create extension if not exists pgtap;
select plan(12);

select ok(
  current_user = 'supabase_admin' and session_user = 'supabase_admin',
  'the audit connects as the actual supabase_admin creator role');

select ok(to_regrole('supabase_admin') is not null,
  'the disposable Supabase role supabase_admin exists');

select ok(exists (
  select 1
    from aclexplode(acldefault('f', 'supabase_admin'::regrole)) a
   where a.grantee = 0 and a.privilege_type = 'EXECUTE'
), 'PostgreSQL built-in function defaults include PUBLIC EXECUTE for this creator');

select diag(format(
  'supabase_admin attributes: rolsuper=%s, rolcanlogin=%s, rolcreaterole=%s, rolbypassrls=%s; postgres member of supabase_admin=%s; public CREATE=%s; current_user=%s',
  (select rolsuper from pg_roles where rolname = 'supabase_admin'),
  (select rolcanlogin from pg_roles where rolname = 'supabase_admin'),
  (select rolcreaterole from pg_roles where rolname = 'supabase_admin'),
  (select rolbypassrls from pg_roles where rolname = 'supabase_admin'),
  pg_has_role('postgres', 'supabase_admin', 'MEMBER'),
  has_schema_privilege('supabase_admin', 'public', 'CREATE'),
  current_user
));

select ok(exists (
  select 1
    from pg_default_acl d
    cross join lateral aclexplode(d.defaclacl) a
    join pg_roles r on r.oid = a.grantee
   where d.defaclrole = 'supabase_admin'::regrole
     and d.defaclnamespace = 'public'::regnamespace
     and d.defaclobjtype = 'f'
     and a.privilege_type = 'EXECUTE'
     and r.rolname = 'anon'
), 'supabase_admin public-schema defaults explicitly include anon EXECUTE');

select ok(exists (
  select 1
    from pg_default_acl d
    cross join lateral aclexplode(d.defaclacl) a
    join pg_roles r on r.oid = a.grantee
   where d.defaclrole = 'supabase_admin'::regrole
     and d.defaclnamespace = 'public'::regnamespace
     and d.defaclobjtype = 'f'
     and a.privilege_type = 'EXECUTE'
     and r.rolname = 'authenticated'
), 'supabase_admin public-schema defaults explicitly include authenticated EXECUTE');

select ok(exists (
  select 1
    from pg_default_acl d
    cross join lateral aclexplode(d.defaclacl) a
    join pg_roles r on r.oid = a.grantee
   where d.defaclrole = 'supabase_admin'::regrole
     and d.defaclnamespace = 'public'::regnamespace
     and d.defaclobjtype = 'f'
     and a.privilege_type = 'EXECUTE'
     and r.rolname = 'service_role'
), 'supabase_admin public-schema defaults explicitly include service_role EXECUTE');

create function public.w85_supabase_admin_probe()
returns integer language sql immutable as $probe$ select 85 $probe$;

select ok(
  (select pg_get_userbyid(p.proowner) = 'supabase_admin'
     from pg_proc p where p.oid = 'public.w85_supabase_admin_probe()'::regprocedure),
  'the probe function is owned by the role that created it');

select ok(exists (
  select 1 from pg_proc p
  cross join lateral aclexplode(coalesce(p.proacl, acldefault('f', p.proowner))) a
  where p.oid = 'public.w85_supabase_admin_probe()'::regprocedure
    and a.grantee = 0 and a.privilege_type = 'EXECUTE'
), 'the supabase_admin-created public function has a direct PUBLIC EXECUTE ACL');

select ok(exists (
  select 1 from pg_proc p
  cross join lateral aclexplode(coalesce(p.proacl, acldefault('f', p.proowner))) a
  where p.oid = 'public.w85_supabase_admin_probe()'::regprocedure
    and a.grantee = 'anon'::regrole and a.privilege_type = 'EXECUTE'
), 'the supabase_admin-created public function directly grants anon EXECUTE');

select ok(exists (
  select 1 from pg_proc p
  cross join lateral aclexplode(coalesce(p.proacl, acldefault('f', p.proowner))) a
  where p.oid = 'public.w85_supabase_admin_probe()'::regprocedure
    and a.grantee = 'authenticated'::regrole and a.privilege_type = 'EXECUTE'
), 'the supabase_admin-created public function directly grants authenticated EXECUTE');

select ok(exists (
  select 1 from pg_proc p
  cross join lateral aclexplode(coalesce(p.proacl, acldefault('f', p.proowner))) a
  where p.oid = 'public.w85_supabase_admin_probe()'::regprocedure
    and a.grantee = 'service_role'::regrole and a.privilege_type = 'EXECUTE'
), 'the supabase_admin-created public function directly grants service_role EXECUTE');

select ok(
  has_function_privilege('anon', 'public.w85_supabase_admin_probe()', 'EXECUTE')
  and has_function_privilege('authenticated', 'public.w85_supabase_admin_probe()', 'EXECUTE')
  and has_function_privilege('service_role', 'public.w85_supabase_admin_probe()', 'EXECUTE'),
  'all three API roles can effectively execute the probe under these isolated defaults');

select * from finish();
rollback;

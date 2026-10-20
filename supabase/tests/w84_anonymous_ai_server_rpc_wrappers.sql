-- Narrow PostgREST surface for server-only anonymous quota operations.
begin;
create extension if not exists pgtap;

select plan(19);

select is((
  select count(*)::integer
    from pg_proc p join pg_namespace n on n.oid = p.pronamespace
   where n.nspname = 'public'
     and p.proname in ('reserve_anonymous_ai_generation',
                       'consume_anonymous_ai_generation',
                       'release_anonymous_ai_generation')
), 3, 'public server RPC surface has exactly three reviewed functions');

select is((
  select count(*)::integer
    from pg_proc p join pg_namespace n on n.oid = p.pronamespace
   where n.nspname = 'public'
     and p.proname in ('reserve_anonymous_ai_generation',
                       'consume_anonymous_ai_generation',
                       'release_anonymous_ai_generation')
     and p.prosecdef
), 3, 'all public wrappers use SECURITY DEFINER');

select is((
  select count(*)::integer
    from pg_proc p join pg_namespace n on n.oid = p.pronamespace
   where n.nspname = 'public'
     and p.proname in ('reserve_anonymous_ai_generation',
                       'consume_anonymous_ai_generation',
                       'release_anonymous_ai_generation')
     and p.proconfig @> array['search_path=pg_catalog, public']
), 3, 'all wrappers pin search_path to pg_catalog, public');

select is((
  select count(*)::integer
    from pg_proc p join pg_namespace n on n.oid = p.pronamespace
   where n.nspname = 'public'
     and p.proname in ('reserve_anonymous_ai_generation',
                       'consume_anonymous_ai_generation',
                       'release_anonymous_ai_generation')
     and (p.prosrc not like '%auth.uid()%' or p.prosrc not like '%auth.role()%')
), 0, 'all wrappers bind the request to service_role and no user uid');

select is(has_function_privilege('service_role', 'public.reserve_anonymous_ai_generation(text,text,uuid)', 'EXECUTE'), true, 'service_role can call reserve wrapper');
select is(has_function_privilege('service_role', 'public.consume_anonymous_ai_generation(uuid)', 'EXECUTE'), true, 'service_role can call consume wrapper');
select is(has_function_privilege('service_role', 'public.release_anonymous_ai_generation(uuid)', 'EXECUTE'), true, 'service_role can call release wrapper');

select is(has_function_privilege('anon', 'public.reserve_anonymous_ai_generation(text,text,uuid)', 'EXECUTE'), false, 'anon cannot call reserve wrapper');
select is(has_function_privilege('authenticated', 'public.reserve_anonymous_ai_generation(text,text,uuid)', 'EXECUTE'), false, 'authenticated cannot call reserve wrapper');
select is(has_function_privilege('anon', 'public.consume_anonymous_ai_generation(uuid)', 'EXECUTE'), false, 'anon cannot call consume wrapper');
select is(has_function_privilege('authenticated', 'public.consume_anonymous_ai_generation(uuid)', 'EXECUTE'), false, 'authenticated cannot call consume wrapper');
select is(has_function_privilege('anon', 'public.release_anonymous_ai_generation(uuid)', 'EXECUTE'), false, 'anon cannot call release wrapper');
select is(has_function_privilege('authenticated', 'public.release_anonymous_ai_generation(uuid)', 'EXECUTE'), false, 'authenticated cannot call release wrapper');

select is((
  select count(*)::integer
    from pg_proc p join pg_namespace n on n.oid = p.pronamespace
   where n.nspname = 'private'
     and p.proname in ('reserve_anonymous_ai_generation',
                       'consume_anonymous_ai_generation',
                       'release_anonymous_ai_generation')
), 3, 'private implementations remain present and separate from API wrappers');

select is((
  select count(*)::integer
    from pg_proc p join pg_namespace n on n.oid = p.pronamespace
   where n.nspname = 'private'
     and p.proname in ('reserve_anonymous_ai_generation',
                       'consume_anonymous_ai_generation',
                       'release_anonymous_ai_generation')
     and has_function_privilege('anon', p.oid, 'EXECUTE')
), 0, 'anon has no direct execution on private implementations');

select is((
  select count(*)::integer
    from pg_proc p join pg_namespace n on n.oid = p.pronamespace
   where n.nspname = 'private'
     and p.proname in ('reserve_anonymous_ai_generation',
                       'consume_anonymous_ai_generation',
                       'release_anonymous_ai_generation')
     and has_function_privilege('authenticated', p.oid, 'EXECUTE')
), 0, 'authenticated has no direct execution on private implementations');

select is((
  select count(*)::integer
    from pg_proc p join pg_namespace n on n.oid = p.pronamespace
   where n.nspname = 'public'
     and p.proname in ('reserve_anonymous_ai_generation',
                       'consume_anonymous_ai_generation',
                       'release_anonymous_ai_generation')
     and exists (
       select 1
         from aclexplode(coalesce(p.proacl, acldefault('f', p.proowner))) acl
        where acl.grantee not in (p.proowner, (select oid from pg_roles where rolname = 'service_role'))
          and acl.privilege_type = 'EXECUTE'
     )
), 0, 'wrappers have no direct EXECUTE grants beyond owner and service_role');

select is((
  select count(*)::integer
    from pg_proc p join pg_namespace n on n.oid = p.pronamespace
    join lateral aclexplode(coalesce(p.proacl, acldefault('f', p.proowner))) acl on true
   where n.nspname = 'public'
     and p.proname in ('reserve_anonymous_ai_generation',
                       'consume_anonymous_ai_generation',
                       'release_anonymous_ai_generation')
     and acl.grantee = (select oid from pg_roles where rolname = 'service_role')
     and acl.privilege_type = 'EXECUTE'
), 3, 'service_role is the only non-owner direct EXECUTE grantee');

select is((
  select count(*)::integer
    from pg_proc p join pg_namespace n on n.oid = p.pronamespace
   where n.nspname = 'public'
     and p.proname in ('reserve_anonymous_ai_generation',
                       'consume_anonymous_ai_generation',
                       'release_anonymous_ai_generation')
     and pg_get_userbyid(p.proowner) in ('anon', 'authenticated')
), 0, 'end-user roles do not own SECURITY DEFINER wrappers');

select * from finish();
rollback;

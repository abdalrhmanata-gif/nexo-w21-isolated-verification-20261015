-- W83/W80 read-only catalog reconciliation for an authorized operator.
-- This file performs SELECTs only. It never calls application RPCs.
-- Run with a pre-provisioned read-only libpq service alias, for example:
--   PGOPTIONS='-c default_transaction_read_only=on' psql -X \
--     'service=zavqera_dev_readonly' -v ON_ERROR_STOP=1 \
--     -f supabase/tests/w83_invitation_catalog_reconciliation.sql
-- Do not put connection strings, passwords, tokens, or row data in captured output.

\set ON_ERROR_STOP on
begin transaction read only;

\echo '=== Database identity metadata (verify this is the explicitly authorized environment) ==='
select current_database() as database_name,
       current_user as effective_user,
       session_user as login_user,
       current_setting('server_version_num') as server_version_num,
       current_setting('transaction_read_only') as transaction_read_only;

select current_setting('transaction_read_only') = 'on' as read_only_guard_confirmed \gset
\if :read_only_guard_confirmed
  \echo 'READ_ONLY_GUARD=CONFIRMED'
\else
  \echo 'READ_ONLY_GUARD=FAILED'
  \quit 3
\endif

\echo '=== Supabase migration ledger availability ==='
select to_regclass('supabase_migrations.schema_migrations') is not null as ledger_available \gset
\if :ledger_available
  select exists (
    select 1 from information_schema.columns
     where table_schema = 'supabase_migrations'
       and table_name = 'schema_migrations'
       and column_name = 'name'
  ) as ledger_has_name \gset
  \if :ledger_has_name
    \echo 'Ledger rows (version/name metadata only):'
    select version, name from supabase_migrations.schema_migrations order by version, name;
  \else
    \echo 'Ledger has no name column; versions only (migration-name reconciliation remains unresolved).'
    select version from supabase_migrations.schema_migrations order by version;
  \endif
\else
  \echo 'UNRESOLVED: supabase_migrations.schema_migrations is absent or not visible to this role.'
\endif

\echo '=== Relevant function inventory: signatures, owner, mode, volatility and configured search_path ==='
with targets(schema_name, function_name) as (
  values ('public','create_workspace_invitation'), ('public','get_workspace_invitation'),
         ('public','accept_workspace_invitation'), ('public','revoke_workspace_invitation'),
         ('private','create_workspace_invitation'), ('private','get_workspace_invitation'),
         ('private','accept_workspace_invitation'), ('private','revoke_workspace_invitation')
)
select n.nspname as schema_name,
       p.proname as function_name,
       p.oid::regprocedure as exact_signature,
       pg_get_userbyid(p.proowner) as owner,
       case when p.prosecdef then 'SECURITY DEFINER' else 'SECURITY INVOKER' end as security_mode,
       p.provolatile as volatility_code,
       p.proconfig as configured_settings,
       coalesce(array_to_string(p.proconfig, ', '), '(no function-level settings)') as settings_display
  from targets t
  join pg_namespace n on n.nspname = t.schema_name
  join pg_proc p on p.pronamespace = n.oid and p.proname = t.function_name
 order by n.nspname, p.proname, p.oid::regprocedure::text;

\echo '=== Function EXECUTE ACL entries, including PUBLIC and owner ==='
with targets(schema_name, function_name) as (
  values ('public','create_workspace_invitation'), ('public','get_workspace_invitation'),
         ('public','accept_workspace_invitation'), ('public','revoke_workspace_invitation'),
         ('private','create_workspace_invitation'), ('private','get_workspace_invitation'),
         ('private','accept_workspace_invitation'), ('private','revoke_workspace_invitation')
)
select n.nspname as schema_name,
       p.oid::regprocedure as exact_signature,
       case when a.grantee = 0 then 'PUBLIC' else gr.rolname end as grantee,
       owner_role.rolname as function_owner,
       a.privilege_type,
       a.is_grantable,
       case when a.grantee = p.proowner then 'owner (implicit/explicit)' else 'non-owner ACL' end as acl_class
  from targets t
  join pg_namespace n on n.nspname = t.schema_name
  join pg_proc p on p.pronamespace = n.oid and p.proname = t.function_name
  cross join lateral aclexplode(coalesce(p.proacl, acldefault('f', p.proowner))) a
  left join pg_roles gr on gr.oid = a.grantee
  join pg_roles owner_role on owner_role.oid = p.proowner
 where a.privilege_type = 'EXECUTE'
 order by n.nspname, p.oid::regprocedure::text, grantee;

\echo '=== Effective EXECUTE for expected and other login-capable roles ==='
with targets(schema_name, function_name) as (
  values ('public','create_workspace_invitation'), ('public','get_workspace_invitation'),
         ('public','accept_workspace_invitation'), ('public','revoke_workspace_invitation'),
         ('private','create_workspace_invitation'), ('private','get_workspace_invitation'),
         ('private','accept_workspace_invitation'), ('private','revoke_workspace_invitation')
), candidate_roles as (
  select rolname from pg_roles
   where rolname in ('anon','authenticated','service_role')
      or (rolcanlogin and rolname not like 'pg_%')
)
select n.nspname as schema_name,
       p.oid::regprocedure as exact_signature,
       r.rolname,
       has_function_privilege(r.rolname, p.oid, 'EXECUTE') as effective_execute,
       pg_has_role(r.rolname, p.proowner, 'USAGE') as has_owner_role_membership
  from targets t
  join pg_namespace n on n.nspname = t.schema_name
  join pg_proc p on p.pronamespace = n.oid and p.proname = t.function_name
 cross join candidate_roles r
 order by n.nspname, p.oid::regprocedure::text, r.rolname;

\echo '=== Schema USAGE ACL and effective USAGE for private ==='
select case when a.grantee = 0 then 'PUBLIC' else r.rolname end as grantee,
       a.privilege_type, a.is_grantable
  from pg_namespace n
  cross join lateral aclexplode(coalesce(n.nspacl, acldefault('n', n.nspowner))) a
  left join pg_roles r on r.oid = a.grantee
 where n.nspname = 'private' and a.privilege_type = 'USAGE'
 order by grantee;

select rolname,
       has_schema_privilege(rolname, 'private', 'USAGE') as effective_private_usage
  from pg_roles
 where rolname in ('anon','authenticated','service_role')
    or (rolcanlogin and rolname not like 'pg_%')
 order by rolname;

\echo '=== Role attributes for API roles and function owners ==='
select rolname, rolsuper, rolinherit, rolcreaterole, rolcreatedb, rolcanlogin, rolbypassrls
  from pg_roles
 where rolname in ('anon','authenticated','service_role','postgres','supabase_admin')
 order by rolname;

\echo '=== Role membership paths relevant to invitation privilege inheritance ==='
select member_role.rolname as member,
       granted_role.rolname as granted_role,
       m.admin_option,
       m.inherit_option,
       m.set_option
  from pg_auth_members m
  join pg_roles member_role on member_role.oid = m.member
  join pg_roles granted_role on granted_role.oid = m.roleid
 where member_role.rolname in ('anon','authenticated','service_role','postgres','supabase_admin')
    or granted_role.rolname in ('anon','authenticated','service_role','postgres','supabase_admin')
 order by member, granted_role;

\echo '=== Built-in function EXECUTE default ACL baseline (used when no global function default override exists) ==='
\echo 'Per-schema default ACL entries are added to the global/built-in baseline; a schema-level REVOKE cannot remove a global grant.'
select owner_role.rolname as object_creator,
       case when a.grantee = 0 then 'PUBLIC' else grantee_role.rolname end as grantee,
       a.privilege_type,
       a.is_grantable
  from pg_roles owner_role
  cross join lateral aclexplode(acldefault('f', owner_role.oid)) a
  left join pg_roles grantee_role on grantee_role.oid = a.grantee
 where owner_role.rolname in ('postgres','supabase_admin')
   and a.privilege_type = 'EXECUTE'
 order by owner_role.rolname, grantee;

\echo '=== Default ACL overrides that can affect future functions in public/private ==='
select owner_role.rolname as object_creator,
       case when d.defaclnamespace = 0 then '(global)' else ns.nspname end as schema_name,
       case d.defaclobjtype when 'f' then 'function' else d.defaclobjtype::text end as object_type,
       case when a.grantee = 0 then 'PUBLIC' else grantee_role.rolname end as grantee,
       a.privilege_type,
       a.is_grantable
  from pg_default_acl d
  join pg_roles owner_role on owner_role.oid = d.defaclrole
  left join pg_namespace ns on ns.oid = d.defaclnamespace
  cross join lateral aclexplode(d.defaclacl) a
  left join pg_roles grantee_role on grantee_role.oid = a.grantee
 where d.defaclobjtype = 'f'
   and (d.defaclnamespace = 0 or ns.nspname in ('public','private'))
 order by object_creator, schema_name, grantee, privilege_type;

\echo '=== Expected existing invitation ACLs after W83 and future-function defaults after W84 ==='
\echo 'Function inventory: exactly one overload per each of the eight names/signatures specified in W80.'
\echo 'Owner/security/search_path: postgres owner; private helpers SECURITY DEFINER; public GET SECURITY DEFINER; three public mutation wrappers SECURITY INVOKER; all configured search_path=pg_catalog, public.'
\echo 'Direct non-owner EXECUTE grantees: public create/accept/revoke and private create/accept/revoke = authenticated only; public/private GET = anon and authenticated only; no service_role or PUBLIC.'
\echo 'Effective role matrix is defined by unchanged supabase/tests/w80_invitation_helper_privileges.sql; expected service_role=false for all eight; anon private schema USAGE=false.'
\echo 'W84 expected for future functions created by postgres: global function default ACL omits PUBLIC, anon, authenticated, service_role; public-schema defaults omit PUBLIC and those API roles.'
\echo 'supabase_admin is a distinct function creator; its built-in/global and scoped default ACLs are reported separately and are not changed by W84. Owner-side review remains required.'
\echo 'Classify all other grants, memberships, owners, overloads, configuration or ledger gaps as unexpected/unknown and stop for review. This report is not an automated rollout approval.'

rollback;

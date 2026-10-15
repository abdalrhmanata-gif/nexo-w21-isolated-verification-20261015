-- W84 hardens default EXECUTE ACLs for future functions created by the migration owner.
-- Existing function ACLs are intentionally unchanged; each callable RPC must receive
-- explicit, reviewed GRANT EXECUTE statements in its defining migration.
-- Scope is role postgres only. supabase_admin defaults are separate and remain
-- owner-managed because this migration must not impersonate or rewrite that role.

alter default privileges for role postgres
  revoke execute on functions from public;

alter default privileges for role postgres
  revoke execute on functions from anon, authenticated, service_role;

-- Supabase's scoped public defaults may add these API-role grants back on top
-- of global defaults, so revoke them at that scope as well. Existing function
-- grants are not affected by ALTER DEFAULT PRIVILEGES.
alter default privileges for role postgres in schema public
  revoke execute on functions from public, anon, authenticated, service_role;

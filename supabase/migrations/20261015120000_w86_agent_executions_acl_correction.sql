-- W86: forward-only correction for the observed W66 table-ACL drift.
-- This migration restores the W65/W66 intended boundary:
--   * authenticated may SELECT history subject to RLS;
--   * anon and authenticated cannot mutate executions;
--   * service_role must use explicitly granted guarded RPCs, not the table.
-- It deliberately does not grant or revoke EXECUTE on any function.
-- Hosted application is blocked pending separate migration-history review and approval.

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

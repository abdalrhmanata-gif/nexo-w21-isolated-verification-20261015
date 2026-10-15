-- W83 repairs the invitation EXECUTE boundary without rewriting W44/W80 history.
-- The authenticated server client remains subject to the same JWT role grants;
-- service_role does not need these browser-facing invitation RPCs.

-- A clean local Supabase replay has direct service_role EXECUTE ACL entries on
-- these public RPCs, though the checked-in W44/W80 grants never add that role.
-- Remove only that direct grant from the four invitation entrypoints.
revoke execute on function public.create_workspace_invitation(uuid, text, text, text, timestamptz)
  from service_role;
revoke execute on function public.get_workspace_invitation(text)
  from service_role;
revoke execute on function public.accept_workspace_invitation(text)
  from service_role;
revoke execute on function public.revoke_workspace_invitation(uuid)
  from service_role;

-- Anonymous invitation lookup is deliberately token-gated. anon has no USAGE
-- on private, so this single public wrapper must cross the schema boundary as
-- its owner. The private helper validates the 64-character SHA-256 token and
-- returns only invitation metadata; it performs the existing expiry update.
-- Qualifying wi columns avoids W44's OUT parameter named `status` shadowing the
-- table column. Keep the helper's direct role ACL unchanged and keep its path
-- pinned; the wrapper adds no direct access to the private schema for anon.
create or replace function private.get_workspace_invitation(p_token_hash text)
returns table(
  id uuid,
  email text,
  role text,
  status text,
  expires_at timestamptz,
  created_at timestamptz
)
language plpgsql
security definer
set search_path = pg_catalog, public
as $function$
begin
  if p_token_hash is null or char_length(p_token_hash) <> 64 then
    raise exception 'INVALID_INVITATION_TOKEN' using errcode = '22023';
  end if;

  update public.workspace_invitations as wi
     set status = 'EXPIRED'
   where wi.token_hash = p_token_hash
     and wi.status = 'PENDING'
     and wi.expires_at <= timezone('utc', now());

  return query
  select wi.id, wi.email, wi.role, wi.status, wi.expires_at, wi.created_at
    from public.workspace_invitations as wi
   where wi.token_hash = p_token_hash
   limit 1;
end;
$function$;

-- Preserve the existing anon/authenticated EXECUTE ACL and postgres ownership;
-- change only the security mode needed to invoke the private helper securely.
create or replace function public.get_workspace_invitation(p_token_hash text)
returns table(
  id uuid,
  email text,
  role text,
  status text,
  expires_at timestamptz,
  created_at timestamptz
)
language sql
security definer
set search_path = pg_catalog, public
as $function$
  select * from private.get_workspace_invitation(p_token_hash);
$function$;

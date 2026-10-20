-- Expose only the three server-side anonymous quota operations through the
-- default PostgREST schema. Do not expose the private schema itself.
create or replace function public.reserve_anonymous_ai_generation(
  p_visitor_hash text,
  p_ip_hash text,
  p_request_id uuid
)
returns table (
  allowed boolean,
  reservation_id uuid,
  remaining integer,
  reason text
)
language plpgsql
security definer
set search_path = pg_catalog, public
as $function$
begin
  if coalesce(auth.role(), '') <> 'service_role' or auth.uid() is not null then
    raise exception using errcode = '42501', message = 'service_role_required';
  end if;
  return query
    select * from private.reserve_anonymous_ai_generation(p_visitor_hash, p_ip_hash, p_request_id);
end;
$function$;

create or replace function public.consume_anonymous_ai_generation(p_reservation_id uuid)
returns boolean
language plpgsql
security definer
set search_path = pg_catalog, public
as $function$
begin
  if coalesce(auth.role(), '') <> 'service_role' or auth.uid() is not null then
    raise exception using errcode = '42501', message = 'service_role_required';
  end if;
  return private.consume_anonymous_ai_generation(p_reservation_id);
end;
$function$;

create or replace function public.release_anonymous_ai_generation(p_reservation_id uuid)
returns boolean
language plpgsql
security definer
set search_path = pg_catalog, public
as $function$
begin
  if coalesce(auth.role(), '') <> 'service_role' or auth.uid() is not null then
    raise exception using errcode = '42501', message = 'service_role_required';
  end if;
  return private.release_anonymous_ai_generation(p_reservation_id);
end;
$function$;

revoke all on function public.reserve_anonymous_ai_generation(text, text, uuid)
  from public, anon, authenticated, service_role;
revoke all on function public.consume_anonymous_ai_generation(uuid)
  from public, anon, authenticated, service_role;
revoke all on function public.release_anonymous_ai_generation(uuid)
  from public, anon, authenticated, service_role;

grant execute on function public.reserve_anonymous_ai_generation(text, text, uuid) to service_role;
grant execute on function public.consume_anonymous_ai_generation(uuid) to service_role;
grant execute on function public.release_anonymous_ai_generation(uuid) to service_role;

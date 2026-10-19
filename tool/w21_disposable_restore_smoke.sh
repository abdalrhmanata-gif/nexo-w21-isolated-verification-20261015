#!/usr/bin/env bash
set -euo pipefail

# Allowlisted application-schema logical backup/restore smoke only.
# Excludes managed realtime/storage/vault schemas; the archive stays in the
# labeled W21 PostgreSQL container and is never uploaded. Not a full-DB or
# production backup and not an RPO/RTO rehearsal.
PROJECT_ID="zavqera-e2e-local"
EXPECTED_SENTINEL="$ZAVQERA_E2E_SUPABASE_WORKDIR/ZAVQERA_E2E_DISPOSABLE"
PROOF="$RUNNER_TEMP/W21_RESTORE_SMOKE_PROOF.txt"
RESTORE_DB="zavqera_restore_$GITHUB_RUN_ID"
DUMP_PATH="/tmp/$RESTORE_DB.dump"
DB_CONTAINER=""
DUMP_SHA256="not-created"
DUMP_BYTES="0"
SOURCE_RELATIONS="unknown"
RESTORE_RELATIONS="unknown"
SOURCE_EXTENSION_RELATIONS="unknown"
RESTORE_EXTENSION_RELATIONS="unknown"
SENTINEL_ID="w21-restore-$GITHUB_RUN_ID"
SENTINEL_PAYLOAD="zavqera-disposable-restore-smoke:$GITHUB_RUN_ID"
SENTINEL_CREATED="false"
SENTINEL_ROW_MATCHED="false"
FIXTURE_CLEANUP_REQUIRED="false"
FIXTURE_SEED_SUCCEEDED="false"
FIXTURE_ROW_MATCHED="false"
FIXTURE_REMOVED="false"
FIXTURE_USER_ID=""
FIXTURE_WORKSPACE_ID=""
FIXTURE_OBJECTIVE="w21-restore-objective-$GITHUB_RUN_ID"
FIXTURE_WORKSPACE_NAME="w21-restore-workspace-$GITHUB_RUN_ID"
FIXTURE_ACTION_ONE="w21-restore-action-one"
FIXTURE_ACTION_TWO="w21-restore-action-two"
SOURCE_FIXTURE_SIGNATURE="not-created"
RESTORE_FIXTURE_SIGNATURE="not-created"
FIXTURE_EXPECTED_SIGNATURE=""
RESTORE_PROFILE_TRIGGER_ENABLED="false"
RESTORE_TRIGGER_MODES_RESTORED="false"
SOURCE_SENTINEL_REMOVED="false"
RESTORE_OK="false"
RESTORE_DB_REMOVED="false"
DUMP_REMOVED="false"
CLEANUP_VERIFIED="false"

mkdir -p "$RUNNER_TEMP"

finish() {
  local original_status=$?
  local cleanup_status=0
  trap - EXIT
  set +e

  if [[ -n "$DB_CONTAINER" ]]; then
    docker exec --user postgres "$DB_CONTAINER" dropdb \
      --if-exists --force -U postgres "$RESTORE_DB" >/dev/null 2>&1
    local drop_status=$?
    docker exec --user postgres "$DB_CONTAINER" rm -f "$DUMP_PATH" >/dev/null 2>&1
    local rm_status=$?

    local sentinel_drop_status=0
    local remaining_sentinel="not-created"
    if [[ "$SENTINEL_CREATED" == "true" ]]; then
      docker exec --user postgres "$DB_CONTAINER" psql -Xv ON_ERROR_STOP=1 -U postgres -d postgres \
        -c "DROP TABLE IF EXISTS public.w21_restore_smoke_sentinel" >/dev/null 2>&1
      sentinel_drop_status=$?
      remaining_sentinel="$(docker exec --user postgres "$DB_CONTAINER" psql -XAt -U postgres -d postgres \
        -c "SELECT to_regclass('public.w21_restore_smoke_sentinel') IS NOT NULL" 2>/dev/null)"
      if [[ "$sentinel_drop_status" -eq 0 && "$remaining_sentinel" == "f" ]]; then
        SOURCE_SENTINEL_REMOVED="true"
      fi
    fi

    local fixture_delete_status=0
    local remaining_fixture="not-created"
    if [[ "$FIXTURE_CLEANUP_REQUIRED" == "true" ]]; then
      docker exec --user postgres "$DB_CONTAINER" psql -Xv ON_ERROR_STOP=1 -U postgres -d postgres \
        -c "DELETE FROM public.mission_actions WHERE mission_id IN (SELECT id FROM public.missions WHERE workspace_id = '$FIXTURE_WORKSPACE_ID'::uuid AND owner_id = '$FIXTURE_USER_ID'::uuid);
            DELETE FROM public.missions WHERE workspace_id = '$FIXTURE_WORKSPACE_ID'::uuid AND owner_id = '$FIXTURE_USER_ID'::uuid AND objective = '$FIXTURE_OBJECTIVE';
            DELETE FROM public.workspace_members WHERE workspace_id = '$FIXTURE_WORKSPACE_ID'::uuid AND user_id = '$FIXTURE_USER_ID'::uuid;
            DELETE FROM public.workspaces WHERE id = '$FIXTURE_WORKSPACE_ID'::uuid AND owner_id = '$FIXTURE_USER_ID'::uuid;
            DELETE FROM auth.users WHERE id = '$FIXTURE_USER_ID'::uuid" >/dev/null 2>&1
      fixture_delete_status=$?
      remaining_fixture="$(docker exec --user postgres "$DB_CONTAINER" psql -XAt -U postgres -d postgres \
        -c "SELECT (EXISTS (SELECT 1 FROM auth.users WHERE id = '$FIXTURE_USER_ID'::uuid)
                 OR EXISTS (SELECT 1 FROM public.profiles WHERE id = '$FIXTURE_USER_ID'::uuid)
                 OR EXISTS (SELECT 1 FROM public.workspaces WHERE id = '$FIXTURE_WORKSPACE_ID'::uuid)
                 OR EXISTS (SELECT 1 FROM public.workspace_members WHERE workspace_id = '$FIXTURE_WORKSPACE_ID'::uuid)
                 OR EXISTS (SELECT 1 FROM public.missions WHERE workspace_id = '$FIXTURE_WORKSPACE_ID'::uuid AND owner_id = '$FIXTURE_USER_ID'::uuid AND objective = '$FIXTURE_OBJECTIVE'))" 2>/dev/null)"
      if [[ "$fixture_delete_status" -eq 0 && "$remaining_fixture" == "f" ]]; then
        FIXTURE_REMOVED="true"
      fi
    fi

    local remaining_db="unknown"
    remaining_db="$(docker exec --user postgres "$DB_CONTAINER" psql -XAt -U postgres -d postgres \
      -c "SELECT EXISTS (SELECT 1 FROM pg_database WHERE datname = '$RESTORE_DB')" 2>/dev/null)"
    local remaining_dump="unknown"
    remaining_dump="$(docker exec --user postgres "$DB_CONTAINER" sh -c \
      "test ! -e '$DUMP_PATH' && printf absent || printf present" 2>/dev/null)"

    if [[ "$drop_status" -eq 0 && "$remaining_db" == "f" ]]; then RESTORE_DB_REMOVED="true"; fi
    if [[ "$rm_status" -eq 0 && "$remaining_dump" == "absent" ]]; then DUMP_REMOVED="true"; fi
    if [[ "$SENTINEL_CREATED" == "true" && "$SOURCE_SENTINEL_REMOVED" == "true" && "$RESTORE_DB_REMOVED" == "true" && "$DUMP_REMOVED" == "true" ]]; then
      if [[ "$FIXTURE_CLEANUP_REQUIRED" != "true" || "$FIXTURE_REMOVED" == "true" ]]; then
        CLEANUP_VERIFIED="true"
      fi
    fi
    [[ "$CLEANUP_VERIFIED" == "true" ]] || cleanup_status=1
  fi

  {
    echo "restore_smoke=$([[ "$original_status" -eq 0 && "$RESTORE_OK" == "true" && "$SENTINEL_ROW_MATCHED" == "true" && "$FIXTURE_SEED_SUCCEEDED" == "true" && "$FIXTURE_ROW_MATCHED" == "true" && "$RESTORE_PROFILE_TRIGGER_ENABLED" == "true" && "$RESTORE_TRIGGER_MODES_RESTORED" == "true" && "$CLEANUP_VERIFIED" == "true" ]] && printf PASS || printf FAIL)"
    echo "project_id=$PROJECT_ID"
    echo "source_database=postgres"
    echo "restore_database=$RESTORE_DB"
    echo "dump_sha256=$DUMP_SHA256"
    echo "dump_bytes=$DUMP_BYTES"
    echo "source_app_relation_count=$SOURCE_RELATIONS"
    echo "restored_app_relation_count=$RESTORE_RELATIONS"
    echo "source_extension_relation_count=$SOURCE_EXTENSION_RELATIONS"
    echo "restored_extension_relation_count=$RESTORE_EXTENSION_RELATIONS"
    echo "extension_membership_note=extension-owned members may be recreated by CREATE EXTENSION and are not compared as application relations"
    echo "sentinel_row_matched=$SENTINEL_ROW_MATCHED"
    echo "synthetic_fixture_seeded=$FIXTURE_SEED_SUCCEEDED"
    echo "synthetic_fixture_row_matched=$FIXTURE_ROW_MATCHED"
    echo "synthetic_fixture_removed=$FIXTURE_REMOVED"
    echo "restore_auth_profile_trigger_enabled=$RESTORE_PROFILE_TRIGGER_ENABLED"
    echo "restore_user_trigger_modes_restored=$RESTORE_TRIGGER_MODES_RESTORED"
    echo "source_sentinel_removed=$SOURCE_SENTINEL_REMOVED"
    echo "restore_database_removed=$RESTORE_DB_REMOVED"
    echo "dump_removed=$DUMP_REMOVED"
    echo "restore_cleanup_verified=$CLEANUP_VERIFIED"
  } > "$PROOF"
  cat "$PROOF"

  if [[ "$original_status" -ne 0 ]]; then exit "$original_status"; fi
  if [[ "$cleanup_status" -ne 0 || "$RESTORE_OK" != "true" || "$CLEANUP_VERIFIED" != "true" ]]; then exit 1; fi
  exit 0
}
trap finish EXIT

if [[ -z "$ZAVQERA_E2E_SUPABASE_WORKDIR" || ! -f "$EXPECTED_SENTINEL" ]]; then
  echo "Refusing restore smoke: explicit disposable W21 sentinel is missing." >&2
  exit 2
fi
if [[ "$(cat "$EXPECTED_SENTINEL")" != "$PROJECT_ID" ]]; then
  echo "Refusing restore smoke: disposable sentinel does not match expected project." >&2
  exit 2
fi
if [[ ! "$GITHUB_RUN_ID" =~ ^[0-9]+$ ]]; then
  echo "Refusing restore smoke: numeric CI run ID is required." >&2
  exit 2
fi

matching_containers="$(docker ps --filter "label=com.supabase.cli.project=$PROJECT_ID" --format '{{.ID}} {{.Names}}' |
  awk '$2 ~ /(^|_)db(_|$)/ { print $1 }')"
matching_count="$(printf '%s\n' "$matching_containers" | awk 'NF { count++ } END { print count + 0 }')"
if [[ "$matching_count" != "1" ]]; then
  echo "Refusing restore smoke: expected exactly one labeled disposable PostgreSQL container." >&2
  exit 2
fi
DB_CONTAINER="$(printf '%s\n' "$matching_containers" | awk 'NF { print; exit }')"
container_project="$(docker inspect --format '{{ index .Config.Labels "com.supabase.cli.project" }}' "$DB_CONTAINER")"
if [[ "$container_project" != "$PROJECT_ID" ]]; then
  echo "Refusing restore smoke: selected database container has a different project label." >&2
  exit 2
fi

docker exec --user postgres "$DB_CONTAINER" pg_isready -U postgres -d postgres >/dev/null

# Create a linked, non-secret synthetic user/workspace/mission/action fixture in
# this disposable source database. This tests application relationships on
# restore; it is not production data and must be removed in the EXIT trap.
sentinel_exists="$(docker exec --user postgres "$DB_CONTAINER" psql -XAt -U postgres -d postgres \
  -c "SELECT to_regclass('public.w21_restore_smoke_sentinel') IS NOT NULL")"
if [[ "$sentinel_exists" != "f" ]]; then
  echo "Refusing restore smoke: synthetic sentinel table already exists in source." >&2
  exit 2
fi
SENTINEL_CREATED="true"
docker exec --user postgres "$DB_CONTAINER" psql -Xv ON_ERROR_STOP=1 -U postgres -d postgres \
  -c "CREATE TABLE public.w21_restore_smoke_sentinel (id text PRIMARY KEY, payload text NOT NULL); INSERT INTO public.w21_restore_smoke_sentinel (id, payload) VALUES ('$SENTINEL_ID', '$SENTINEL_PAYLOAD')"

FIXTURE_USER_ID="$(docker exec --user postgres "$DB_CONTAINER" psql -XAt -U postgres -d postgres -c "SELECT gen_random_uuid()::text")"
FIXTURE_WORKSPACE_ID="$(docker exec --user postgres "$DB_CONTAINER" psql -XAt -U postgres -d postgres -c "SELECT gen_random_uuid()::text")"
UUID_RE='^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$'
if [[ ! "$FIXTURE_USER_ID" =~ $UUID_RE || ! "$FIXTURE_WORKSPACE_ID" =~ $UUID_RE ]]; then
  echo "Refusing restore smoke: synthetic fixture IDs were not valid UUIDs." >&2
  exit 2
fi
FIXTURE_EXPECTED_SIGNATURE="1|1|1|$FIXTURE_WORKSPACE_NAME|1|owner|1|$FIXTURE_OBJECTIVE|DRAFT|0:$FIXTURE_ACTION_ONE:PENDING,1:$FIXTURE_ACTION_TWO:PENDING"
FIXTURE_CLEANUP_REQUIRED="true"
docker exec -i --user postgres "$DB_CONTAINER" psql -Xv ON_ERROR_STOP=1 -U postgres -d postgres <<SQL
BEGIN;
SELECT pg_catalog.set_config('request.jwt.claim.sub', '$FIXTURE_USER_ID', true);
SELECT pg_catalog.set_config('request.jwt.claims', jsonb_build_object('sub', '$FIXTURE_USER_ID', 'role', 'authenticated')::text, true);
INSERT INTO auth.users (id) VALUES ('$FIXTURE_USER_ID');
INSERT INTO public.workspaces (id, owner_id, name)
VALUES ('$FIXTURE_WORKSPACE_ID'::uuid, '$FIXTURE_USER_ID'::uuid, '$FIXTURE_WORKSPACE_NAME');
INSERT INTO public.workspace_members (workspace_id, user_id, role)
VALUES ('$FIXTURE_WORKSPACE_ID'::uuid, '$FIXTURE_USER_ID'::uuid, 'owner');
SELECT id FROM public.create_mission_with_actions(
  '$FIXTURE_WORKSPACE_ID'::uuid,
  '$FIXTURE_OBJECTIVE',
  '["$FIXTURE_ACTION_ONE", "$FIXTURE_ACTION_TWO"]'::jsonb
);
COMMIT;
SQL
FIXTURE_SEED_SUCCEEDED="true"

# Create the archive only inside the explicitly labeled local test container.
docker exec --user postgres "$DB_CONTAINER" pg_dump \
  --format=custom --no-owner --no-acl \
  --schema=public \
  --schema=private \
  --schema=auth \
  --schema=extensions \
  --schema=supabase_migrations \
  --file="$DUMP_PATH" --dbname=postgres
docker exec --user postgres "$DB_CONTAINER" pg_restore --list "$DUMP_PATH" >/dev/null
DUMP_SHA256="$(docker exec --user postgres "$DB_CONTAINER" sha256sum "$DUMP_PATH" | awk '{print $1}')"
DUMP_BYTES="$(docker exec --user postgres "$DB_CONTAINER" stat -c '%s' "$DUMP_PATH")"
[[ "$DUMP_SHA256" =~ ^[0-9a-f]{64}$ ]]
[[ "$DUMP_BYTES" =~ ^[0-9]+$ && "$DUMP_BYTES" -gt 0 ]]

docker exec --user postgres "$DB_CONTAINER" createdb \
  --encoding=UTF8 --template=template0 --owner=postgres "$RESTORE_DB"
# template0 on this PostgreSQL image already initializes public; remove that
# empty default only in the disposable target so pg_restore can recreate it.
docker exec --user postgres "$DB_CONTAINER" psql -Xv ON_ERROR_STOP=1 -U postgres -d "$RESTORE_DB" \
  -c "DROP SCHEMA public CASCADE"
# Restore schema first. During data-only restore, disable user-defined triggers
# on restored table objects only. Keep PostgreSQL's internal RI/FK triggers
# enabled, so relational integrity remains enforced. Snapshot and restore each
# user-trigger mode exactly; this avoids trigger side effects requiring app JWTs
# or duplicate derived rows, without bypassing foreign-key checks.
docker exec --user postgres "$DB_CONTAINER" pg_restore \
  --schema-only --exit-on-error --no-owner --no-acl --dbname="$RESTORE_DB" "$DUMP_PATH"
docker exec -i --user postgres "$DB_CONTAINER" psql -Xv ON_ERROR_STOP=1 -U postgres -d "$RESTORE_DB" <<'SQL'
CREATE SCHEMA w21_restore_control;
CREATE TABLE w21_restore_control.trigger_state AS
SELECT n.nspname::text AS schema_name,
       c.relname::text AS table_name,
       t.tgname::text AS trigger_name,
       t.tgenabled::text AS enabled_mode
FROM pg_catalog.pg_trigger t
JOIN pg_catalog.pg_class c ON c.oid = t.tgrelid
JOIN pg_catalog.pg_namespace n ON n.oid = c.relnamespace
WHERE NOT t.tgisinternal
  AND c.relkind IN ('r', 'p')
  AND n.nspname IN ('public', 'private', 'auth', 'extensions', 'supabase_migrations');

DO $w21$
DECLARE r record;
BEGIN
  FOR r IN
    SELECT schema_name, table_name, trigger_name
    FROM w21_restore_control.trigger_state
    WHERE enabled_mode <> 'D'
  LOOP
    EXECUTE format('ALTER TABLE %I.%I DISABLE TRIGGER %I',
                   r.schema_name, r.table_name, r.trigger_name);
  END LOOP;
END
$w21$;
SQL
docker exec --user postgres "$DB_CONTAINER" pg_restore \
  --data-only --exit-on-error --no-owner --no-acl --dbname="$RESTORE_DB" "$DUMP_PATH"
docker exec -i --user postgres "$DB_CONTAINER" psql -Xv ON_ERROR_STOP=1 -U postgres -d "$RESTORE_DB" <<'SQL'
DO $w21$
DECLARE r record;
BEGIN
  FOR r IN
    SELECT schema_name, table_name, trigger_name, enabled_mode
    FROM w21_restore_control.trigger_state
  LOOP
    CASE r.enabled_mode
      WHEN 'O' THEN
        EXECUTE format('ALTER TABLE %I.%I ENABLE TRIGGER %I',
                       r.schema_name, r.table_name, r.trigger_name);
      WHEN 'R' THEN
        EXECUTE format('ALTER TABLE %I.%I ENABLE REPLICA TRIGGER %I',
                       r.schema_name, r.table_name, r.trigger_name);
      WHEN 'A' THEN
        EXECUTE format('ALTER TABLE %I.%I ENABLE ALWAYS TRIGGER %I',
                       r.schema_name, r.table_name, r.trigger_name);
      WHEN 'D' THEN
        NULL;
      ELSE
        RAISE EXCEPTION 'Unknown trigger mode % for %.%.%',
          r.enabled_mode, r.schema_name, r.table_name, r.trigger_name;
    END CASE;
  END LOOP;
END
$w21$;
DROP SCHEMA w21_restore_control CASCADE;
SQL
RESTORE_TRIGGER_MODES_RESTORED="true"
restore_profile_trigger_check="$(docker exec --user postgres "$DB_CONTAINER" psql -XAt -U postgres -d "$RESTORE_DB" \
  -c "SELECT EXISTS (SELECT 1 FROM pg_catalog.pg_trigger WHERE tgname = 'on_auth_user_created' AND tgrelid = 'auth.users'::regclass AND NOT tgisinternal AND tgenabled = 'O')")"
if [[ "$restore_profile_trigger_check" != "t" ]]; then
  echo "Restore smoke failed: auth user profile trigger was not restored enabled." >&2
  exit 1
fi
RESTORE_PROFILE_TRIGGER_ENABLED="true"

relation_query="SELECT count(*) FROM pg_catalog.pg_class c JOIN pg_catalog.pg_namespace n ON n.oid = c.relnamespace WHERE n.nspname IN ('public','private','auth','supabase_migrations') AND c.relkind IN ('r','p','v','m','S','f')"
extension_relation_query="SELECT count(*) FROM pg_catalog.pg_class c JOIN pg_catalog.pg_namespace n ON n.oid = c.relnamespace WHERE n.nspname = 'extensions' AND c.relkind IN ('r','p','v','m','S','f')"
SOURCE_RELATIONS="$(docker exec --user postgres "$DB_CONTAINER" psql -XAt -U postgres -d postgres -c "$relation_query")"
RESTORE_RELATIONS="$(docker exec --user postgres "$DB_CONTAINER" psql -XAt -U postgres -d "$RESTORE_DB" -c "$relation_query")"
SOURCE_EXTENSION_RELATIONS="$(docker exec --user postgres "$DB_CONTAINER" psql -XAt -U postgres -d postgres -c "$extension_relation_query")"
RESTORE_EXTENSION_RELATIONS="$(docker exec --user postgres "$DB_CONTAINER" psql -XAt -U postgres -d "$RESTORE_DB" -c "$extension_relation_query")"
[[ "$SOURCE_RELATIONS" =~ ^[0-9]+$ && "$RESTORE_RELATIONS" =~ ^[0-9]+$ ]]
[[ "$SOURCE_EXTENSION_RELATIONS" =~ ^[0-9]+$ && "$RESTORE_EXTENSION_RELATIONS" =~ ^[0-9]+$ ]]
[[ "$SOURCE_RELATIONS" == "$RESTORE_RELATIONS" ]]

for relation in \
  public.profiles \
  public.workspaces \
  public.missions \
  public.mission_actions \
  public.workspace_members \
  public.agent_executions \
  public.w21_restore_smoke_sentinel \
  auth.users \
  auth.identities \
  supabase_migrations.schema_migrations
do
  source_rows="$(docker exec --user postgres "$DB_CONTAINER" psql -XAt -U postgres -d postgres -c "SELECT count(*) FROM $relation")"
  restored_rows="$(docker exec --user postgres "$DB_CONTAINER" psql -XAt -U postgres -d "$RESTORE_DB" -c "SELECT count(*) FROM $relation")"
  if [[ ! "$source_rows" =~ ^[0-9]+$ || ! "$restored_rows" =~ ^[0-9]+$ || "$source_rows" != "$restored_rows" ]]; then
    echo "Restore smoke mismatch for $relation: source=$source_rows restored=$restored_rows" >&2
    exit 1
  fi
  printf 'restore_count_%s=%s\n' "$(printf '%s' "$relation" | tr '.' '_')" "$restored_rows"
done

source_sentinel="$(docker exec --user postgres "$DB_CONTAINER" psql -XAt -U postgres -d postgres \
  -c "SELECT id || '|' || payload FROM public.w21_restore_smoke_sentinel WHERE id = '$SENTINEL_ID'")"
restored_sentinel="$(docker exec --user postgres "$DB_CONTAINER" psql -XAt -U postgres -d "$RESTORE_DB" \
  -c "SELECT id || '|' || payload FROM public.w21_restore_smoke_sentinel WHERE id = '$SENTINEL_ID'")"
expected_sentinel="$SENTINEL_ID|$SENTINEL_PAYLOAD"
if [[ "$source_sentinel" != "$expected_sentinel" || "$restored_sentinel" != "$expected_sentinel" ]]; then
  echo "Synthetic sentinel mismatch: source='$source_sentinel' restored='$restored_sentinel'" >&2
  exit 1
fi
SENTINEL_ROW_MATCHED="true"
echo "sentinel_row_matched=true"

fixture_signature_query="SELECT concat(
  (SELECT count(*)::text FROM auth.users WHERE id = '$FIXTURE_USER_ID'::uuid), '|',
  (SELECT count(*)::text FROM public.profiles WHERE id = '$FIXTURE_USER_ID'::uuid), '|',
  (SELECT count(*)::text FROM public.workspaces WHERE id = '$FIXTURE_WORKSPACE_ID'::uuid AND owner_id = '$FIXTURE_USER_ID'::uuid), '|',
  coalesce((SELECT name FROM public.workspaces WHERE id = '$FIXTURE_WORKSPACE_ID'::uuid), '<missing>'), '|',
  (SELECT count(*)::text FROM public.workspace_members WHERE workspace_id = '$FIXTURE_WORKSPACE_ID'::uuid AND user_id = '$FIXTURE_USER_ID'::uuid), '|',
  coalesce((SELECT role::text FROM public.workspace_members WHERE workspace_id = '$FIXTURE_WORKSPACE_ID'::uuid AND user_id = '$FIXTURE_USER_ID'::uuid), '<missing>'), '|',
  (SELECT count(*)::text FROM public.missions WHERE workspace_id = '$FIXTURE_WORKSPACE_ID'::uuid AND owner_id = '$FIXTURE_USER_ID'::uuid AND objective = '$FIXTURE_OBJECTIVE'), '|',
  coalesce((SELECT status::text FROM public.missions WHERE workspace_id = '$FIXTURE_WORKSPACE_ID'::uuid AND owner_id = '$FIXTURE_USER_ID'::uuid AND objective = '$FIXTURE_OBJECTIVE'), '<missing>'), '|',
  coalesce((SELECT string_agg(a.position::text || ':' || a.title || ':' || a.status::text, ',' ORDER BY a.position)
            FROM public.mission_actions a JOIN public.missions m ON m.id = a.mission_id
            WHERE m.workspace_id = '$FIXTURE_WORKSPACE_ID'::uuid AND m.owner_id = '$FIXTURE_USER_ID'::uuid AND m.objective = '$FIXTURE_OBJECTIVE'), '<missing>')
)"
SOURCE_FIXTURE_SIGNATURE="$(docker exec --user postgres "$DB_CONTAINER" psql -XAt -U postgres -d postgres -c "$fixture_signature_query")"
RESTORE_FIXTURE_SIGNATURE="$(docker exec --user postgres "$DB_CONTAINER" psql -XAt -U postgres -d "$RESTORE_DB" -c "$fixture_signature_query")"
if [[ "$SOURCE_FIXTURE_SIGNATURE" != "$FIXTURE_EXPECTED_SIGNATURE" || "$RESTORE_FIXTURE_SIGNATURE" != "$FIXTURE_EXPECTED_SIGNATURE" || "$SOURCE_FIXTURE_SIGNATURE" != "$RESTORE_FIXTURE_SIGNATURE" ]]; then
  echo "Synthetic application fixture mismatch: source/restored signatures differ from the exact expected relationship fingerprint." >&2
  exit 1
fi
FIXTURE_ROW_MATCHED="true"
echo "synthetic_fixture_row_matched=true"

RESTORE_OK="true"
echo "Disposable logical backup/restore smoke passed; dump contents are not exported."

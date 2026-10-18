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

    local remaining_db="unknown"
    remaining_db="$(docker exec --user postgres "$DB_CONTAINER" psql -XAt -U postgres -d postgres \
      -c "SELECT EXISTS (SELECT 1 FROM pg_database WHERE datname = '$RESTORE_DB')" 2>/dev/null)"
    local remaining_dump="unknown"
    remaining_dump="$(docker exec --user postgres "$DB_CONTAINER" sh -c \
      "test ! -e '$DUMP_PATH' && printf absent || printf present" 2>/dev/null)"

    if [[ "$drop_status" -eq 0 && "$remaining_db" == "f" ]]; then RESTORE_DB_REMOVED="true"; fi
    if [[ "$rm_status" -eq 0 && "$remaining_dump" == "absent" ]]; then DUMP_REMOVED="true"; fi
    if [[ "$RESTORE_DB_REMOVED" == "true" && "$DUMP_REMOVED" == "true" ]]; then CLEANUP_VERIFIED="true"; fi
    [[ "$CLEANUP_VERIFIED" == "true" ]] || cleanup_status=1
  fi

  {
    echo "restore_smoke=$([[ "$original_status" -eq 0 && "$RESTORE_OK" == "true" && "$CLEANUP_VERIFIED" == "true" ]] && printf PASS || printf FAIL)"
    echo "project_id=$PROJECT_ID"
    echo "source_database=postgres"
    echo "restore_database=$RESTORE_DB"
    echo "dump_sha256=$DUMP_SHA256"
    echo "dump_bytes=$DUMP_BYTES"
    echo "source_app_relation_count=$SOURCE_RELATIONS"
    echo "restored_app_relation_count=$RESTORE_RELATIONS"
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
docker exec --user postgres "$DB_CONTAINER" pg_restore \
  --exit-on-error --no-owner --no-acl --dbname="$RESTORE_DB" "$DUMP_PATH"

relation_query="SELECT count(*) FROM pg_catalog.pg_class c JOIN pg_catalog.pg_namespace n ON n.oid = c.relnamespace WHERE n.nspname IN ('public','private','auth','extensions','supabase_migrations') AND c.relkind IN ('r','p','v','m','S','f')"
SOURCE_RELATIONS="$(docker exec --user postgres "$DB_CONTAINER" psql -XAt -U postgres -d postgres -c "$relation_query")"
RESTORE_RELATIONS="$(docker exec --user postgres "$DB_CONTAINER" psql -XAt -U postgres -d "$RESTORE_DB" -c "$relation_query")"
[[ "$SOURCE_RELATIONS" =~ ^[0-9]+$ && "$RESTORE_RELATIONS" =~ ^[0-9]+$ ]]
[[ "$SOURCE_RELATIONS" == "$RESTORE_RELATIONS" ]]

for relation in \
  public.profiles \
  public.workspaces \
  public.missions \
  public.mission_actions \
  public.agent_executions \
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

RESTORE_OK="true"
echo "Disposable logical backup/restore smoke passed; dump contents are not exported."
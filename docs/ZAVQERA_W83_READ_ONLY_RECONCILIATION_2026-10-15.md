# W83 Read-Only Schema Reconciliation Procedure

**Status:** Prepared for an authorized environment owner. This procedure has not connected to hosted Supabase. No hosted Development or Production state is inferred from the isolated CI database.

## Scope and source contract

The target is the eight invitation helper/wrapper functions named in `supabase/tests/w80_invitation_helper_privileges.sql`, plus the `private` schema ACL, role memberships, function default ACLs and Supabase migration ledger. Historical implementation sources are W44 (`20261008160000_w44_workspace_invitations.sql`, `20261008170000_w44_invitation_lifecycle.sql`), W46 (`20261008172000_w46_workspace_activity_audit.sql`), W80 (`20261013100000_w80_fail_closed_workspace_role_checks.sql`) and W83 (`20261015100000_w83_workspace_invitation_privilege_correction.sql`). W83 uses `CREATE OR REPLACE` for the two lookup functions and four direct service-role revocations. It does not change table/RLS state, ownership, schema grants, or migration ledger rows.

Expected state after replay through W83 and after an idempotent W83 reapplication is the same:

| Function | Expected non-owner EXECUTE grantees | Owner / security / path |
| --- | --- | --- |
| `public.create_workspace_invitation(uuid,text,text,text,timestamptz)` | `authenticated` | `postgres`, INVOKER, `pg_catalog, public` |
| `public.get_workspace_invitation(text)` | `anon`, `authenticated` | `postgres`, DEFINER, `pg_catalog, public` |
| `public.accept_workspace_invitation(text)` | `authenticated` | `postgres`, INVOKER, `pg_catalog, public` |
| `public.revoke_workspace_invitation(uuid)` | `authenticated` | `postgres`, INVOKER, `pg_catalog, public` |
| `private.create_workspace_invitation(uuid,text,text,text,timestamptz)` | `authenticated` | `postgres`, DEFINER, `pg_catalog, public` |
| `private.get_workspace_invitation(text)` | `anon`, `authenticated` | `postgres`, DEFINER, `pg_catalog, public` |
| `private.accept_workspace_invitation(text)` | `authenticated` | `postgres`, DEFINER, `pg_catalog, public` |
| `private.revoke_workspace_invitation(uuid)` | `authenticated` | `postgres`, DEFINER, `pg_catalog, public` |

There must be exactly one overload of each name/signature. No `PUBLIC` or `service_role` direct grant is expected. W80 further asserts effective role privileges and requires no `anon` USAGE on `private`; `anon`'s helper EXECUTE exception does not confer schema access. Function owners retain inherent owner rights and are reported separately from non-owner ACL entries. Reapplication should make no other catalog change.

Default function ACLs are a separate policy surface: they do not change grants on these existing function OIDs, but affect future functions created by the listed owners. Do not assume the checked-in W80 assertions cover those defaults. The disposable run below observed `service_role EXECUTE` in the default function ACL for `postgres` and `supabase_admin` in `public`; the origin and intended policy for any hosted environment are unknown. Record and review that output separately. It is not fixed by W83, and this task makes no default-privilege change.

## Authorized read-only procedure

1. The environment owner confirms which project is targeted from their trusted console/process and configures a libpq service alias such as `zavqera_dev_readonly` with a dedicated account that has only metadata/catalog read access. Do not place a URI/password/token on the command line, in shell history, or in output. Do not use a service-role credential. Do not use a linked Supabase CLI context.
2. From the repository root, run the checked-in catalog report with transaction-level read-only mode:

   ```sh
   PGOPTIONS='-c default_transaction_read_only=on' \
     psql -X 'service=zavqera_dev_readonly' -v ON_ERROR_STOP=1 \
     -f supabase/tests/w83_invitation_catalog_reconciliation.sql \
     > w83-development-catalog.txt 2>&1
   ```

   Use a separately named alias for any other environment. Review the effective database/login identities in the report and verify the selected project independently before retaining output. The report prints only database identity metadata, migration versions/names, role/ACL/function metadata, not application rows.
3. The SQL opens a read-only transaction and performs metadata `SELECT`s only. It does not call RPCs or functions under test, perform DML/DDL, or inspect invitation/user row contents. It reports ledger version/name when available (version only if the older ledger lacks a `name` column). A missing/inaccessible ledger is unresolved evidence, not an empty ledger.
4. Compare the ordered ledger to all checked-in migration timestamps/names using an offline copy of the report and repository migration manifest. For the relevant history, verify W44/W46/W80 predecessors and whether W83 is recorded. Do not infer applied state merely from the current function body.
5. Compare every function signature/count, owner, `prosecdef`, volatility, `proconfig`, direct ACL, effective EXECUTE, schema USAGE, role memberships and function default ACL output against the matrix above and the canonical W80 test. Classify each row as expected, unexpected, unknown or manual review. An extra overload, owner/membership path, PUBLIC/service-role ACL, anonymous private-schema USAGE, unexpected function setting, missing ledger evidence, or privilege that cannot be explained is a stop condition.
6. Preserve timestamped, access-controlled query output plus repository HEAD, migration manifest digest and independent project identity evidence. Redact no catalog fields silently; do not include connection configuration or user/application data.

## Dependencies, stop conditions and recovery limits

- **Dependencies:** authorized operator and environment owner; independently verified project target; read-only DB identity; catalog visibility; checked-out exact migration source and manifest; review of results by database security owner.
- **Preconditions:** PR/migration source reviewed; no pending migration application; no hosted credentials supplied to this task; output capture approved for metadata. This is a read-only preflight, not rollout approval.
- **Stop:** wrong or ambiguous project identity, read-only transaction not `on`, insufficient catalog visibility, ledger absent/inconsistent, any unexpected grant/membership/owner/signature/search path/overload, or query error. Do not try to repair ACLs or ledger in place.
- **Verification:** only the independent environment owner may subsequently propose a forward migration; first compare current ledger and all W83 preconditions, then obtain separate approval. After any separately approved change, repeat this report and run the unchanged W80 pgTAP regression on a disposable PG17 stack. This document itself authorizes no hosted operation.
- **Recovery:** W83 is forward-only; no down migration or safe automatic rollback is established. If a later authorized rollout partially fails, stop, preserve error and ledger/catalog evidence, determine committed state read-only, and have the owner review a forward repair or backup restoration. Do not delete ledger rows, restore old grants, or rerun blindly. Backup restoration may lose intervening writes.

## Evidence boundaries

The original isolated run at SHA `16b6c655f21c36b11757c827e36ff39494916b14` demonstrated a disposable PostgreSQL 17 replay of 88 checked-in migrations through W83 plus one explicitly disclosed local-only auth-trigger compatibility fixture, W44 17/17, W80 49/49, successful W83 reapplication, successful remainder replay and verified cleanup. Its [run](https://github.com/abdalrhmanata-gif/nexo-w21-isolated-verification-20261015/actions/runs/38734947527) and [artifact](https://github.com/abdalrhmanata-gif/nexo-w21-isolated-verification-20261015/actions/runs/38734947527/artifacts/11973300579) are repository-only evidence.

The paired verification revision is commit `8510654bd6da55394f5a13f64cfcfb06b0ad62c8`, run [38737023310](https://github.com/abdalrhmanata-gif/nexo-w21-isolated-verification-20261015/actions/runs/38737023310), artifact [11973343485](https://github.com/abdalrhmanata-gif/nexo-w21-isolated-verification-20261015/actions/runs/38737023310/artifacts/11973343485), artifact digest `sha256:717a30b6926606d4ce92201bc9e8dde621091babe966cd6b214b644e60552636`. It replayed 88 checked-in migration files plus the local-only compatibility fixture (89 ledger rows total), observed PostgreSQL `170011`, and recorded exact matching SHA-256 `fd22a28c084fcdbcfbed354fa2e2d31630aa42db0e08d22fe7dd2d0d51081844` for the two catalog snapshots. Before reapplication, W44 passed 17/17 and W80 49/49; after reapplication W44 passed 17/17 and W80 49/49; all four TAP exit codes were 0; W83 reapply and later replay were 0; cleanup verified zero containers/volumes. The snapshots show eight unique functions, postgres owner, expected security modes/paths, exact non-owner ACLs, no service_role function EXECUTE on those eight functions, and anon without private-schema USAGE. This does not remove the default-ACL caveat above. The artifact, not the earlier progress note, is the evidence source.

Neither run establishes hosted Development/Production parity, W66/W67/W81/W82 security, universal Mission Authority enforcement, provider guarantees, or launch readiness. Release remains **NO-GO**.


## Latest exact-SHA launch gate after W80/W81 wiring — 2026-10-15

The full [W21 Local Launch Gate run 38740599618](https://github.com/abdalrhmanata-gif/nexo-w21-isolated-verification-20261015/actions/runs/38740599618) passed on exact workflow/source/test SHA `77e4ca26157137dfcd3146a066f8503cd72c1c67` in the temporary verification repository. Artifacts: [W21 evidence/cleanup 11975193299](https://github.com/abdalrhmanata-gif/nexo-w21-isolated-verification-20261015/actions/runs/38740599618/artifacts/11975193299) and [browser diagnostics 11975083311](https://github.com/abdalrhmanata-gif/nexo-w21-isolated-verification-20261015/actions/runs/38740599618/artifacts/11975083311).

The workflow now explicitly copies and executes the unchanged W80 invitation privilege test and W81 read-only Research JIT claim test. W80 passed **49/49**, W81 passed its **23-test plan**, the W30 launch-gate test passed after adding a narrowly scoped assertion for the exact token-gated `public.get_workspace_invitation(text)` SECURITY DEFINER exception, the W82 quota/reservation test passed, and the remaining W66/W67/W63–W79 Mission Authority SQL regressions passed. The four ledger concurrency proofs, W72 fake-provider integration and browser E2E (**2 passed, 2.3m**) passed. Cleanup reports `supabase_stop_exit_code=0`, no remaining containers/volumes and `cleanup_verified=true`.

This updates the isolated evidence record only. It does not change the read-only nature of the operator procedure above, prove any hosted migration ledger or ACL state, or authorize W83 rollout. Authorized owners must still perform an independent, freshly identified, read-only metadata reconciliation before any separate migration review. The original `abdalrhmanata-gif/Nexo` repository remains untouched; PR #39 is OPEN/Draft/unmerged; Issue #23 is OPEN; provider adapters remain empty/fail-closed; release remains **NO-GO**.


## W84 future-function defaults — reconciliation follow-up, 2026-10-15

The read-only report now shows both PostgreSQL's built-in function ACL baseline and schema-specific pg_default_acl overrides, plus role attributes/membership paths for postgres and supabase_admin. In the isolated PG17 replay, the built-in baseline included PUBLIC EXECUTE for both creator roles; scoped public defaults also included API roles. This finding is metadata evidence from the disposable stack, not evidence about hosted Supabase.

W84 candidate 20261015110000_w84_postgres_function_default_acl_hardening.sql changes defaults only for future functions created by postgres; it does not mutate existing function ACLs and does not modify the separate supabase_admin defaults. Its 21-assertion test passed in the full W21 run; W80 isolated workflow [38748554496](https://github.com/abdalrhmanata-gif/nexo-w21-isolated-verification-20261015/actions/runs/38748554496) verified full migration replay through W84, test 21/21, successful W84 reapplication, and test 21/21 again. [Evidence 11980312862](https://github.com/abdalrhmanata-gif/nexo-w21-isolated-verification-20261015/actions/runs/38748554496/artifacts/11980312862).

The full W21 Local Launch Gate passed on SHA 7f28798b35f23787446194da3ff1804ece62e716: [run 38746026089](https://github.com/abdalrhmanata-gif/nexo-w21-isolated-verification-20261015/actions/runs/38746026089); the artifact records READ_ONLY_GUARD=CONFIRMED, database identity postgres/postgres, server version 170011, W83 and W84 ledger entries, default ACL baseline/overrides and verified cleanup. See [evidence/cleanup 11980335837](https://github.com/abdalrhmanata-gif/nexo-w21-isolated-verification-20261015/actions/runs/38746026089/artifacts/11980335837).

Still required before any rollout: an authorized owner must independently verify the hosted project identity and run this catalog report using a validated read-only connection; compare the hosted migration ledger/function ACLs/default ACLs/membership to repository expectations; explicitly classify supabase_admin defaults; stop on unexplained differences. W84 has not been applied to hosted Supabase, and this document authorizes no mutation. Launch remains NO-GO.

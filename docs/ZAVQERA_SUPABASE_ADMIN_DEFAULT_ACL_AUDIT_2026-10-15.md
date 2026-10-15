# ZAVQERA — supabase_admin Function Default ACL Audit (W85)

**Disposition: isolated diagnostic PASS; hosted-state verification NOT DONE; no privilege changes authorized or applied.**

## Exact evidence

- Verification repository: [nexo-w21-isolated-verification-20261015](https://github.com/abdalrhmanata-gif/nexo-w21-isolated-verification-20261015).
- Exact code/test SHA for the W85-enabled workflows: `eb723c68ef73f54758ddb37d34ec713ba9e9d4d5`.
- Dedicated PostgreSQL 17 isolated run: [W80 run 38755183112 — SUCCESS](https://github.com/abdalrhmanata-gif/nexo-w21-isolated-verification-20261015/actions/runs/38755183112).
- Captured evidence artifact: [11982114807](https://github.com/abdalrhmanata-gif/nexo-w21-isolated-verification-20261015/actions/runs/38755183112/artifacts/11982114807), SHA-256 `72473c9fa89f0290804de1c615e9151fcda331d31feae133a9e5038368cfd7e8`.
- Audit file: `supabase/tests/w85_supabase_admin_default_acl_audit.sql` (12 pgTAP assertions).
- The captured disposable database identifies PostgreSQL `170011` (PostgreSQL 17.11), login/effective role `supabase_admin`, and confirms W85's test session actually ran as that role.
- W85: **12 planned / 12 passed / 0 failed**. The isolated Supabase stack cleanup was verified.
- The same workflow replayed the checked-in migration chain through W84; W44 passed 17/17, W46 8/8, unchanged W80 passed 49/49 before and after W83 reapplication, and W84 passed 21/21 before and after reapplication.

## What W85 established on the isolated stack

1. The built-in function default ACL for creator role `supabase_admin` includes `PUBLIC EXECUTE`.
2. Its `public` schema function defaults explicitly include `EXECUTE` for `anon`, `authenticated`, and `service_role`.
3. A test-only function created while connected as `supabase_admin` was owned by that role. Its effective/direct EXECUTE ACL included `PUBLIC` and those three API roles.
4. The test session was connected directly as `supabase_admin`; the test no longer attempts `SET ROLE` from `postgres`.
5. The SQL test ends in `ROLLBACK`. It makes no lasting default-ACL change. The runner uses raw `psql -qAt` output so TAP assertions are counted accurately; the prior attempt had passed all SQL assertions but the aligned output caused a false-negative in the shell counter.

This is evidence of the local test image's role/default configuration only. It does not prove the same attributes, memberships, object ownership, or ACLs on any hosted Supabase project.

## Decision and required boundary

- **Do not add a migration that changes `supabase_admin` defaults based solely on this isolated result.**
- W84 continues to harden future functions created by `postgres`; it deliberately does not alter `supabase_admin` defaults.
- PostgreSQL documents that future-object defaults depend on the role that creates the object, and per-schema defaults are additive to global defaults. These changes do not affect existing function ACLs: [PostgreSQL 17 — ALTER DEFAULT PRIVILEGES](https://www.postgresql.org/docs/17/sql-alterdefaultprivileges.html).
- Supabase documents `supabase_admin` as an internal role for administrative tasks; dashboard SQL runs as `postgres`. Its hosted platform's ownership model differs from older/self-hosted configurations: [Supabase Postgres Roles](https://supabase.com/docs/guides/database/postgres/roles) · [Remove Superuser Access from Studio](https://supabase.com/docs/guides/self-hosting/remove-superuser-access).
- Before any future change, an authorized environment owner must independently identify the exact hosted project and run a read-only catalog/default-ACL/role-membership/ownership query. Stop on unknown or inconsistent ownership, role capabilities, or migration-ledger evidence. This note authorizes no hosted query or mutation.
- `TRUSTED_DISPATCH_ADAPTERS` remains empty and fail-closed. PR #39 remains Draft/open/unmerged, Issue #23 remains open, and release remains **NO-GO** until all production enforcement and provider evidence is independently closed.

## Exact-SHA full W21 result

The full [W21 Local Launch Gate run 38755183191 — SUCCESS](https://github.com/abdalrhmanata-gif/nexo-w21-isolated-verification-20261015/actions/runs/38755183191) completed on the same code/test SHA `eb723c68ef73f54758ddb37d34ec713ba9e9d4d5` used for W85. Its checks included:

- Disposable PostgreSQL 17 migration replay and launch-gate pgTAP.
- Read-only W83 catalog report with `READ_ONLY_GUARD=CONFIRMED`.
- Mission Authority and quota/workspace SQL regressions, including the separate W85 audit connected as `supabase_admin`.
- Four actual-ledger concurrency proofs and W72 persistent fake-provider integration.
- Browser E2E: **2 passed (2.7m)**.
- Disposable database cleanup: `supabase_stop_exit_code=0`, `remaining_containers=none`, `remaining_volumes=none`, `cleanup_verified=true`.

Artifacts:
- [W21 evidence and cleanup — artifact 11982878731](https://github.com/abdalrhmanata-gif/nexo-w21-isolated-verification-20261015/actions/runs/38755183191/artifacts/11982878731), SHA-256 `b9a380ea826b83b354fb3099d5cc9a3ba65cd6f4bc02ffbe51f168af22786f9c`.
- [Browser diagnostics — artifact 11982529470](https://github.com/abdalrhmanata-gif/nexo-w21-isolated-verification-20261015/actions/runs/38755183191/artifacts/11982529470), SHA-256 `7e69662880fd057c742054a597e7742835317d82063eb980c0b09179faca5474`.
- On that same SHA, [Web Unit 38755183119](https://github.com/abdalrhmanata-gif/nexo-w21-isolated-verification-20261015/actions/runs/38755183119) and [Flutter CI 38755183147](https://github.com/abdalrhmanata-gif/nexo-w21-isolated-verification-20261015/actions/runs/38755183147) also succeeded. The dedicated W85-enabled isolated PostgreSQL run is [38755183112](https://github.com/abdalrhmanata-gif/nexo-w21-isolated-verification-20261015/actions/runs/38755183112).

The W21 pass is disposable engineering evidence only. It does not prove hosted Supabase migration/ACL parity, universal production egress enforcement, deployed credential isolation, or real-provider idempotency/receipt/reconciliation guarantees.

## Current release posture

- `TRUSTED_DISPATCH_ADAPTERS` remains empty and fail-closed.
- Original Nexo PR #39 remains OPEN / Draft / UNMERGED at `9d752a59f0683ea7149633138dc85bb33cf9a41b`; Issue #23 remains OPEN.
- No hosted Supabase state, deployment, secret, billing, or DNS configuration was changed; no commit was pushed to the original Nexo repository.
- Launch remains **NO-GO** until the hosted parity audit and all production-wide Mission Authority/provider gates are independently closed.

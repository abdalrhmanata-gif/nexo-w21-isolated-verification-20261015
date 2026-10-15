# Hosted Read-only Migration-Effect Audit Review — 2026-10-15

**Decision: NO-GO for release.** This is a source-to-catalog review of the read-only evidence ZIP captured from ZAVQERA Development. No hosted database changes were made.

## Evidence identity

- Project ref: `mrwmmbytcymqgwvcoywd`; project name `ZAVQERA Development`; region `eu-west-1`.
- Captured: `2026-10-15T17:58:32.963985+00:00` UTC.
- Evidence ZIP SHA-256: `5294a52f2695a938a291f3317c379aadf060d9f0aa6c07f7a029ff7865035384`.
- Query-pack SHA-256: `7fbe8b65aeb75c446ca942277d0541de27de905e9b2172f304924e9029de6c62`.
- All 10 fixed queries completed; `transaction_read_only=true`; token not saved; no application rows queried.
- Caveat: the observed `supabase_read_only_user` has `rolbypassrls=true`. The evidence is bounded to the pinned catalog-only query pack and read-only endpoint; do not reuse it for application-data reads.
- Candidate comparison source: isolated-repo commit `51bc1a543a6c47267b9fc4e8fc0dbec3a8eef6f9`, branch `codex/w80-forward-correction-20261015`.

## Confirmed gaps

1. **Mission Authority budget schema missing.** `public.mission_authority_budgets` and `public.mission_authority_budget_reservations` are absent. All 26 expected columns are absent; 10/11 expected constraints and all 8 expected indexes are absent. The only matching AI reservation state constraint still allows `reserved`, `consumed`, `released` and not `unknown`.
2. **W71 stale-recovery behavior is old.** The captured `private.reconcile_stale_agent_execution(uuid)` marks an expired execution `UNKNOWN` without holding the associated external-effect budget reservation as `HELD_UNKNOWN`. The candidate W71 implementation locks the mission/execution/reservation/budget and preserves the ambiguous reservation.
3. **W75/W76 receipt invariant is absent.** The `agent_execution_success_receipt_guard` trigger and `private.guard_external_execution_success_receipt()` are absent.
4. **Signature drift is material.** The 40-signature check returned 23 mismatches: 19 expected candidate signatures are absent and 4 legacy signatures marked forbidden remain. The newer claim-bound research-completion signatures are absent while older variants remain.
5. **W80 fail-closed body/path is not reflected.** Hosted `private.can_edit_workspace(uuid,uuid)` has `search_path=public, private` and a body without `coalesce(..., false)`; the candidate W80 body uses `coalesce(..., false)` and pins `pg_catalog, public, private`. Existence alone is not parity.
6. **W82 identity binding is absent.** `generation_kind`/`request_hash` columns and the three-argument `reserve_ai_generation(text,text,text)` routines are missing. Legacy one-argument private/public functions remain and have effective EXECUTE for `authenticated` and `service_role`.
7. **W83 privilege correction is absent.** `public.get_workspace_invitation(text)` remains SECURITY INVOKER, not the candidate's SECURITY DEFINER token-gated wrapper. All four public invitation entrypoints retain effective `service_role` EXECUTE, which candidate W83 revokes. Do not blindly revoke anon access from the token-gated lookup; reconcile the intended design and grants together.
8. **W84 defaults are not reflected for postgres.** The observed explicit public-schema default ACL for creator `postgres` still grants EXECUTE to `anon`, `authenticated`, and `service_role`. The same API-role defaults remain under `supabase_admin`; W84 deliberately does not cover that role, so it remains a separate owner-policy decision.
9. **Private schema ACLs need narrow reconciliation.** Effective `USAGE` is true for `authenticated` and `service_role`, false for `anon`. `private.create_workspace_invitation(...)` has a null stored ACL (PostgreSQL default function ACL semantics), broader than the explicit narrow grants in the candidate. This is a catalog ACL finding, not evidence that a function was invoked.

## Audit limitations

- This ZIP checks that the migration ledger relation exists but does not enumerate ledger rows. Use the separate migration-history reconciliation evidence for the 89-local/74-hosted-ledger comparison and timestamp/name conflicts; the ledger/catalog join remains a prerequisite.
- Effective table privileges on `public.agent_executions` were not queried here. Therefore W66 direct `service_role` table-privilege hardening remains **unverified by this ZIP**.
- This is a snapshot at the timestamp above. It does not prove provider-side idempotency/reconciliation or the full runtime Mission Authority boundary.

## Safe next steps

1. Keep release **NO-GO** and `TRUSTED_DISPATCH_ADAPTERS = Object.freeze({})` empty/fail-closed.
2. Do not run hosted migrations or apply repair SQL yet. First reconcile historical ledger provenance; never infer a missing migration from its name alone.
3. Add a reviewed read-only check for W66 effective table ACLs and finish the ledger/catalog provenance comparison.
4. Draft any repair as a forward-only migration, test on disposable PostgreSQL 17, then seek separate approval before any hosted maintenance.

## Candidate-source references

- [W66](https://github.com/abdalrhmanata-gif/nexo-w21-isolated-verification-20261015/blob/51bc1a543a6c47267b9fc4e8fc0dbec3a8eef6f9/supabase/migrations/20261011160000_w66_service_role_table_privilege_hardening.sql)
- [W71](https://github.com/abdalrhmanata-gif/nexo-w21-isolated-verification-20261015/blob/51bc1a543a6c47267b9fc4e8fc0dbec3a8eef6f9/supabase/migrations/20261012070000_w71_expired_external_execution_budget_recovery.sql)
- [W75](https://github.com/abdalrhmanata-gif/nexo-w21-isolated-verification-20261015/blob/51bc1a543a6c47267b9fc4e8fc0dbec3a8eef6f9/supabase/migrations/20261012140000_w75_correlatable_provider_receipt.sql)
- [W76](https://github.com/abdalrhmanata-gif/nexo-w21-isolated-verification-20261015/blob/51bc1a543a6c47267b9fc4e8fc0dbec3a8eef6f9/supabase/migrations/20261012150000_w76_guard_external_success_on_insert.sql)
- [W80](https://github.com/abdalrhmanata-gif/nexo-w21-isolated-verification-20261015/blob/51bc1a543a6c47267b9fc4e8fc0dbec3a8eef6f9/supabase/migrations/20261013100000_w80_fail_closed_workspace_role_checks.sql)
- [W82](https://github.com/abdalrhmanata-gif/nexo-w21-isolated-verification-20261015/blob/51bc1a543a6c47267b9fc4e8fc0dbec3a8eef6f9/supabase/migrations/20261014130000_w82_ai_generation_reservation_identity.sql)
- [W83](https://github.com/abdalrhmanata-gif/nexo-w21-isolated-verification-20261015/blob/51bc1a543a6c47267b9fc4e8fc0dbec3a8eef6f9/supabase/migrations/20261015100000_w83_workspace_invitation_privilege_correction.sql)
- [W84](https://github.com/abdalrhmanata-gif/nexo-w21-isolated-verification-20261015/blob/51bc1a543a6c47267b9fc4e8fc0dbec3a8eef6f9/supabase/migrations/20261015110000_w84_postgres_function_default_acl_hardening.sql)
- [W21 isolated launch-gate run](https://github.com/abdalrhmanata-gif/nexo-w21-isolated-verification-20261015/actions/runs/38779082395) and [W80 isolated PostgreSQL 17 pgTAP run](https://github.com/abdalrhmanata-gif/nexo-w21-isolated-verification-20261015/actions/runs/38779442480) are local/disposable evidence only, not hosted parity proof.


## Post-capture tooling validation — 2026-10-15

After this report's 10-query hosted evidence was captured, the pinned effect pack was extended to 12 queries and both packs passed disposable PostgreSQL 17 smoke in W80 run 38786902560. The new pack hash is a7aba3461786dbb5854f71dc4f87b7e0498d12509add535ab3df4a7ec231a284. The offline comparison tool and its seven tests also passed.

This later local verification does not change the underlying hosted evidence above. Queries 11/12 still must be executed against Development via the explicit read-only endpoint before the current migration-ledger tuples and W66 ACL can be reviewed.

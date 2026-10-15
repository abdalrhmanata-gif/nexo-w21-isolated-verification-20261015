# ZAVQERA — Historical migration path recovery check (2026-10-15)

**Disposition: UNRESOLVED / RELEASE NO-GO.** This is a read-only source-availability check. It does not claim that the historical migrations never existed and does not authorize any database change.

## Scope

- Original repository searched: `abdalrhmanata-gif/Nexo`.
- Audit scope: exact historic migration paths implied by the 22 same-name/different-version ledger conflicts, plus all six hosted-only ledger names.
- Method: exact-path GitHub REST commit-history lookup under `supabase/migrations/` (page size 5) on (a) the repository default branch `main`, (b) branch `codex/w66-w82-dev-audit-refresh-20261014`, and (c) the active PR #39 branch `codex/mission-action-runtime-seam-test-20261014`, each explicitly passed as `sha`. Independently scanned the recursive migration trees of all 23 currently listed original-repository branch refs for the 22 historical timestamp-conflict filenames. The existing audit also scanned all 23 branch-tip trees for the six hosted-only filenames.
- Result checked on 2026-10-15: all 28 exact-path queries returned zero commit-history entries in each of the three queried history scopes (84 exact-path lookups, zero results); the 22 timestamp-conflict filenames were absent from all 23 current branch-tip trees; the six hosted-only names were also absent from all 23 current branch-tip trees.
- Scope limitation: path-history queries were not run independently on every one of the 23 refs; current tip absence does not exclude that a file once existed and was later deleted in another branch's history.
- Current W86 candidate branch in the isolated repository is `codex/w86-agent-executions-acl-correction-20261015`, tested SHA `8dbaa7cb27abbb15144f6b81f1bb8538dd2ce5be`. It contains one additional isolated candidate migration (W86). W86 is not part of the historical 89-file baseline used in the hosted ledger reconciliation and must not be counted as a previously deployed migration.

## Exact-path query results

Every entry below is the exact filename queried inside the original repository's migration directory. For each entry, the GitHub commit-history endpoint returned an empty list (0 commits).

### 22 same-name / different-version candidates

| Hosted ledger version | Migration name | Exact historical path |
|---|---|---|
| `20260924180025` | `w10_deletion_integrity_read_boundary` | `supabase/migrations/20260924180025_w10_deletion_integrity_read_boundary.sql` |
| `20260926060416` | `w16_audit_history_table_hardening` | `supabase/migrations/20260926060416_w16_audit_history_table_hardening.sql` |
| `20261004083051` | `w30_reconstruct_missing_w5_history_tables` | `supabase/migrations/20261004083051_w30_reconstruct_missing_w5_history_tables.sql` |
| `20261004074420` | `w30_server_only_quota_rls_deny_policy` | `supabase/migrations/20261004074420_w30_server_only_quota_rls_deny_policy.sql` |
| `20261005080648` | `w36_enable_pro_plan_identity` | `supabase/migrations/20261005080648_w36_enable_pro_plan_identity.sql` |
| `20261008142204` | `w41_seed_bounded_research_agent` | `supabase/migrations/20261008142204_w41_seed_bounded_research_agent.sql` |
| `20261008145424` | `w42_workspace_rpc_authorization_parity` | `supabase/migrations/20261008145424_w42_workspace_rpc_authorization_parity.sql` |
| `20261008145525` | `w43_bounded_agent_execution_runtime` | `supabase/migrations/20261008145525_w43_bounded_agent_execution_runtime.sql` |
| `20261008155642` | `w44_invitation_lifecycle` | `supabase/migrations/20261008155642_w44_invitation_lifecycle.sql` |
| `20261008160824` | `w45_workspace_member_management` | `supabase/migrations/20261008160824_w45_workspace_member_management.sql` |
| `20261008161617` | `w46_activity_security_hardening` | `supabase/migrations/20261008161617_w46_activity_security_hardening.sql` |
| `20261008161055` | `w46_workspace_activity_audit` | `supabase/migrations/20261008161055_w46_workspace_activity_audit.sql` |
| `20261009092613` | `w47_atomic_workspace_bootstrap` | `supabase/migrations/20261009092613_w47_atomic_workspace_bootstrap.sql` |
| `20261009093725` | `w48_seed_research_agent_for_new_workspaces` | `supabase/migrations/20261009093725_w48_seed_research_agent_for_new_workspaces.sql` |
| `20261009171718` | `w49_agent_execution_recovery` | `supabase/migrations/20261009171718_w49_agent_execution_recovery.sql` |
| `20260921180138` | `w4_table_privilege_hardening` | `supabase/migrations/20260921180138_w4_table_privilege_hardening.sql` |
| `20261009171722` | `w50_expired_execution_lease_fence` | `supabase/migrations/20261009171722_w50_expired_execution_lease_fence.sql` |
| `20261009185119` | `w51_member_rpc_wrapper_permissions` | `supabase/migrations/20261009185119_w51_member_rpc_wrapper_permissions.sql` |
| `20260924172730` | `w7_authoritative_action_mutation` | `supabase/migrations/20260924172730_w7_authoritative_action_mutation.sql` |
| `20260924173730` | `w8_lifecycle_integrity_provenance` | `supabase/migrations/20260924173730_w8_lifecycle_integrity_provenance.sql` |
| `20260924175412` | `w9_1_completed_outcome_guard` | `supabase/migrations/20260924175412_w9_1_completed_outcome_guard.sql` |
| `20260924174933` | `w9_verification_outcome_lifecycle` | `supabase/migrations/20260924174933_w9_verification_outcome_lifecycle.sql` |

### Six hosted-only ledger names

| Hosted ledger version | Migration name | Exact historical path |
|---|---|---|
| `20261007105825` | `expose_anonymous_ai_guard_rpc` | `supabase/migrations/20261007105825_expose_anonymous_ai_guard_rpc.sql` |
| `20261005053351` | `w35_plan_ai_allowances_5_50_300` | `supabase/migrations/20261005053351_w35_plan_ai_allowances_5_50_300.sql` |
| `20261008150359` | `w44_workspace_invitations_and_activity` | `supabase/migrations/20261008150359_w44_workspace_invitations_and_activity.sql` |
| `20261008161103` | `w46_invitation_activity_bindings` | `supabase/migrations/20261008161103_w46_invitation_activity_bindings.sql` |
| `20260921180227` | `w4_harden_profile_trigger_search_path` | `supabase/migrations/20260921180227_w4_harden_profile_trigger_search_path.sql` |
| `20260924171437` | `w6_authoritative_mission_mutation_and_concurrency` | `supabase/migrations/20260924171437_w6_authoritative_mission_mutation_and_concurrency.sql` |

## Interpretation

The three checked Git history scopes (`main`, `codex/w66-w82-dev-audit-refresh-20261014`, and `codex/mission-action-runtime-seam-test-20261014`) did not produce the exact SQL at any of these paths, and none of the exact filenames is present at any of the 23 current branch tips. This is an availability result for the scopes checked, not proof that a file never existed. Branch histories beyond these three refs were not all queried path-by-path. Possible sources outside this search remain: a developer's local Git object database or reflog, a deleted/private branch, CI artifacts, a deployment bundle, a reviewed release archive, or a backup of the migration directory.

A similarly named current source file is not an acceptable substitute for the original SQL. The hosted ledger records version and name, not SQL checksums. Do not change the ledger, re-create historic versions from current source, or run an inferred replay.

## Required next action

1. Preserve the current 12-query evidence ZIP and its hashes.
2. Search any authoritative local clone, deleted-branch/reflog backups, CI artifacts, deployment bundle, and release archives for these 28 exact filenames or historical blobs.
3. If recovered, SHA-256 hash each SQL file and associate it with a commit/artifact identity; compare full SQL and ordered effects against the current source migration.
4. For each path, classify as `EXACT`, `EQUIVALENT_EFFECT_BUT_DIFFERENT_SQL`, or `UNRESOLVED`, with evidence. Do not infer equality from name alone.
5. If historic SQL cannot be recovered, maintain `UNKNOWN` provenance and base any future fix on a fresh read-only catalog/effect map plus explicit owner-reviewed forward migration. Keep separate from any migration-ledger repair decision.

## Guardrails

No hosted database or migration ledger was written. No migration was applied. The original repository and its PR #39/Issue #23 remain untouched by this path-history query. The W86 PR is an isolated Draft review only and does not close history reconciliation.

**Release stays NO-GO.**

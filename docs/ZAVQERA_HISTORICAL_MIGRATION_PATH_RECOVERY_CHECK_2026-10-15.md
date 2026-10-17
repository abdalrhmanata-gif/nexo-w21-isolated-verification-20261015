# ZAVQERA — Historical migration path recovery check (2026-10-15)

**Disposition: UNRESOLVED / RELEASE NO-GO.** This is a read-only source-availability check. It does not claim that the historical migrations never existed and does not authorize any database change.

## Scope

- Original repository searched: `abdalrhmanata-gif/Nexo`.
- Audit scope: exact historic migration paths implied by the 22 same-name/different-version ledger conflicts, plus all six hosted-only ledger names.
- Method: for each of the 28 historical exact paths listed below, queried GitHub's commits endpoint with `path=supabase/migrations/<filename>.sql` and `sha=<branch>` independently on **all 23 currently visible original-repository branch refs**. Each query used `per_page=1`, which is sufficient to distinguish an empty path history from at least one commit. Also inspected the recursive migration trees at all 23 branch tips.
- Result checked on 2026-10-15: **28 paths × 23 current branch refs = 644 branch-scoped exact-path history lookups; all returned empty lists, with zero commits and zero API/tool errors.** The 22 timestamp-conflict filenames and the six hosted-only filenames were also absent from the 23 current branch-tip migration trees.
- Scope limitation: the search is complete for the 28 exact paths within the 23 branch refs listed in the branch-tip snapshot appended below. It cannot inspect unlisted/deleted/private refs, users' local Git object databases and reflogs, CI/deployment artifacts not exposed by GitHub's repository API, or release archives stored elsewhere.
- Current W86 candidate branch in the isolated repository is `codex/w86-agent-executions-acl-correction-20261015`. The full disposable PostgreSQL 17.11 workflow passed on SHA `24af5583113e606bf8ec80f179cca0854073abac`; the W86 SQL blob remains `f870dd83a82c27057bf24390c254713d3fe29182`. W86 is one new isolated candidate migration and is not part of the historical 89-file baseline used in the hosted ledger reconciliation; do not count it as a previously deployed migration.

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

## All-branch exact-path history sweep — 2026-10-15

The same-name/different-timestamp paths and the six hosted-only paths were each queried against all current refs. For every exact path, the branch-specific endpoint returned an empty list.

| Scope | Exact paths | Branch refs | Lookups | Commits found | API/tool errors |
|---|---:|---:|---:|---:|---:|
| Same-name / timestamp-conflict paths | 22 | 23 | 506 | 0 | 0 |
| Hosted-only ledger paths | 6 | 23 | 138 | 0 | 0 |
| **Total unique path/ref pairs** | **28** | **23** | **644** | **0** | **0** |

The previous targeted review of `main`, the audit branch, and active PR #39 branch had reported 84 lookups; those are overlapping checks, not additional unique pairs beyond the 644 above. All currently listed refs were included in the full sweep.

**Consequence:** exact historical SQL for the 22 hosted timestamp paths and six hosted-only paths is **not available from path history on any of these 23 refs**. Do not mark an old migration as identical to a current differently timestamped file. Seek a local clone/reflog, CI artifact, deployment bundle, reviewed release archive, backup, or another authoritative owner-held source.

### Branch-tip snapshot used for the 23-ref sweep

The exact branch heads used in this run were:

| Branch ref | Head SHA |
|---|---|
| `abdalrhmanata-gif-import-nexo-v1-9` | `9219518b853a4125721b4292067840a685c7e74a` |
| `abdalrhmanata-gif-netlify-alternative-deployment` | `bc7dd99ad49a580392b8b64fd165cc2802be9c59` |
| `agent-origin-main-clean-2df7` | `1de719f9cd1f4b15f22efc7e880c9374056a8c79` |
| `codex/egress-gateway-auth-staging-20261015` | `b184b91540c80be8a07b455bddaeca9080fad4f0` |
| `codex/mission-action-runtime-seam-test-20261014` | `9d752a59f0683ea7149633138dc85bb33cf9a41b` |
| `codex/w66-w82-dev-audit-refresh-20261014` | `5aea5611bbb975b971a9c7f7947d4c47b1cb438b` |
| `codex/w80-pgtap-verification-20261014` | `0c56de7c84d41c43f77d86e84dea67f2d88f6ec7` |
| `codex/w80-sql-privilege-fix-20261014` | `2e7dcccf9679ecc78f2b522064a4b121135645c4` |
| `codex/w80-sql-review-base-20261014` | `5e2094fd27c7de60496729956af562651de93137` |
| `codex/w80-workflow-enablement-20261014` | `81ef820d160bfef04edbbab181fc562de203f7fa` |
| `codex/zavqera-windows-path-guards` | `5c1d093d6b2c33c41e5446d10f2c5ed8256be996` |
| `followthrough-action-loop` | `0e1daf921e72d248962d68d9cf29af26591ca166` |
| `main` | `f64a87addb25a7455c6acde446b81bb3427d43cc` |
| `zavqera/ai-planner-integration` | `5e2094fd27c7de60496729956af562651de93137` |
| `zavqera/alternative-web-deployment` | `46dc6029f084fb000ba511478d6e8aec3eb532b3` |
| `zavqera/controlled-adapter-ci-validation` | `96a6803b69dbe62e886bfe04fc4fee5c818e9565` |
| `zavqera/first-user-validation-execution-kit` | `9402265722126333bdb684e5bd4fc0e4aff9a001` |
| `zavqera/integrate-origin-main-clean` | `bb095b716c29d4c13e83d5c817bf2676d127d61a` |
| `zavqera/netlify-preview-candidate` | `1c4e4b37f7378443ec1faaea169b1279469ceaa7` |
| `zavqera/next-phase-first-user-validation` | `ff567e524c8358148922c8780674c16e2be67020` |
| `zavqera/openai-responses-integration` | `45d335e4c8a7a6b9627795e51fcb73fdde453f43` |
| `zavqera/public-preview-deployment` | `6f66b3b3c317fa7787753a8668c84ab8a076b959` |
| `zavqera/web-technical-validation-ci` | `c61536c08014712877cefb9cfe8a4fdfc7bd7de1` |

**Disposition stays UNKNOWN / NO-GO.** These results establish only that the exact paths cannot be recovered from the current visible refs. They do not establish whether their DDL effects are present or absent in the hosted database.

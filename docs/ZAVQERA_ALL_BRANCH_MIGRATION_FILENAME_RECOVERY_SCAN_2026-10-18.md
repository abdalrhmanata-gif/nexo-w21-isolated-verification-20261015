# ZAVQERA — All-branch migration filename recovery sweep (2026-10-18)

**Disposition: bounded GitHub branch-tip scan complete; deployed SQL-byte provenance still UNKNOWN; release NO-GO.**

## Purpose and method

This pass followed the 2026-10-17 owner-review update. It queried the recursive Git tree for every branch tip returned by GitHub for both the original `abdalrhmanata-gif/Nexo` repository and the isolated verification repository. Every tree response was complete (`truncated=false`). Each tree was checked for the exact 28 hosted-side migration filenames listed below. The scan was read-only.

## Results

- Original repository: **23/23 branch tips** scanned.
- Isolated verification repository: **4/4 branch tips** scanned.
- Total: **27/27 branch tips**, all recursive trees untruncated.
- Exact hosted-side filename hits among all 28 candidates: **0**.
- The audited source commit `fbbcb080904acd88aad83a082803f627859026e2` has **89 SQL migration files**; all 89 source-side migration filenames in the 95-row register are present in that source tree.
- Within that source tree, 46 of the 74 ledger rows have matching version/name paths. The 22 conflicting hosted-version paths and six hosted-only paths are absent from the 27 branch-tip snapshots.
- No file or ledger entry was changed by the scan.

### Branch-tip evidence

| Repository | Branch | Head SHA | Tree entries | Truncated | Hits / 28 |
|---|---|---|---:|---|---:|
| Original Nexo | `abdalrhmanata-gif-import-nexo-v1-9` | `9219518b853a4125721b4292067840a685c7e74a` | 97 | no | 0 |
| Original Nexo | `abdalrhmanata-gif-netlify-alternative-deployment` | `bc7dd99ad49a580392b8b64fd165cc2802be9c59` | 199 | no | 0 |
| Original Nexo | `agent-origin-main-clean-2df7` | `1de719f9cd1f4b15f22efc7e880c9374056a8c79` | 196 | no | 0 |
| Original Nexo | `codex/egress-gateway-auth-staging-20261015` | `b184b91540c80be8a07b455bddaeca9080fad4f0` | 504 | no | 0 |
| Original Nexo | `codex/mission-action-runtime-seam-test-20261014` | `9d752a59f0683ea7149633138dc85bb33cf9a41b` | 507 | no | 0 |
| Original Nexo | `codex/w66-w82-dev-audit-refresh-20261014` | `5aea5611bbb975b971a9c7f7947d4c47b1cb438b` | 490 | no | 0 |
| Original Nexo | `codex/w80-pgtap-verification-20261014` | `0c56de7c84d41c43f77d86e84dea67f2d88f6ec7` | 493 | no | 0 |
| Original Nexo | `codex/w80-sql-privilege-fix-20261014` | `2e7dcccf9679ecc78f2b522064a4b121135645c4` | 491 | no | 0 |
| Original Nexo | `codex/w80-sql-review-base-20261014` | `5e2094fd27c7de60496729956af562651de93137` | 490 | no | 0 |
| Original Nexo | `codex/w80-workflow-enablement-20261014` | `81ef820d160bfef04edbbab181fc562de203f7fa` | 106 | no | 0 |
| Original Nexo | `codex/zavqera-windows-path-guards` | `5c1d093d6b2c33c41e5446d10f2c5ed8256be996` | 479 | no | 0 |
| Original Nexo | `followthrough-action-loop` | `0e1daf921e72d248962d68d9cf29af26591ca166` | 103 | no | 0 |
| Original Nexo | `main` | `f64a87addb25a7455c6acde446b81bb3427d43cc` | 105 | no | 0 |
| Original Nexo | `zavqera/ai-planner-integration` | `1b02272a7281b2e9ebf9020cd21a8ac9de3e577e` | 508 | no | 0 |
| Original Nexo | `zavqera/alternative-web-deployment` | `46dc6029f084fb000ba511478d6e8aec3eb532b3` | 258 | no | 0 |
| Original Nexo | `zavqera/controlled-adapter-ci-validation` | `96a6803b69dbe62e886bfe04fc4fee5c818e9565` | 250 | no | 0 |
| Original Nexo | `zavqera/first-user-validation-execution-kit` | `9402265722126333bdb684e5bd4fc0e4aff9a001` | 195 | no | 0 |
| Original Nexo | `zavqera/integrate-origin-main-clean` | `bb095b716c29d4c13e83d5c817bf2676d127d61a` | 196 | no | 0 |
| Original Nexo | `zavqera/netlify-preview-candidate` | `1c4e4b37f7378443ec1faaea169b1279469ceaa7` | 318 | no | 0 |
| Original Nexo | `zavqera/next-phase-first-user-validation` | `ff567e524c8358148922c8780674c16e2be67020` | 194 | no | 0 |
| Original Nexo | `zavqera/openai-responses-integration` | `45d335e4c8a7a6b9627795e51fcb73fdde453f43` | 113 | no | 0 |
| Original Nexo | `zavqera/public-preview-deployment` | `6f66b3b3c317fa7787753a8668c84ab8a076b959` | 198 | no | 0 |
| Original Nexo | `zavqera/web-technical-validation-ci` | `c61536c08014712877cefb9cfe8a4fdfc7bd7de1` | 196 | no | 0 |
| Isolated audit | `codex/migration-ledger-provenance-20261015` | `5f90815d1b5d0ff798e5ff82ce038133677e9e98` | 549 | no | 0 |
| Isolated audit | `codex/mission-action-runtime-seam-test-20261014` | `ec16dc5de69805cadccd1653984802768b22f3f5` | 509 | no | 0 |
| Isolated audit | `codex/w80-forward-correction-20261015` | `b0068d7f677c56fb45f9752b3679497159eabd93` | 530 | no | 0 |
| Isolated audit | `codex/w86-agent-executions-acl-correction-20261015` | `0dc44842f9eaa25d0f34628b1c5c3de0741b41cf` | 536 | no | 0 |

## The 28 exact hosted-side filename candidates checked

### 22 same-name / different-version hosted entries

`20260921180138_w4_table_privilege_hardening.sql`  
`20261004083051_w30_reconstruct_missing_w5_history_tables.sql`  
`20260924172730_w7_authoritative_action_mutation.sql`  
`20260924173730_w8_lifecycle_integrity_provenance.sql`  
`20260924174933_w9_verification_outcome_lifecycle.sql`  
`20260924175412_w9_1_completed_outcome_guard.sql`  
`20260924180025_w10_deletion_integrity_read_boundary.sql`  
`20260926060416_w16_audit_history_table_hardening.sql`  
`20261004074420_w30_server_only_quota_rls_deny_policy.sql`  
`20261005080648_w36_enable_pro_plan_identity.sql`  
`20261008142204_w41_seed_bounded_research_agent.sql`  
`20261008145424_w42_workspace_rpc_authorization_parity.sql`  
`20261008145525_w43_bounded_agent_execution_runtime.sql`  
`20261008155642_w44_invitation_lifecycle.sql`  
`20261008160824_w45_workspace_member_management.sql`  
`20261008161055_w46_workspace_activity_audit.sql`  
`20261008161617_w46_activity_security_hardening.sql`  
`20261009092613_w47_atomic_workspace_bootstrap.sql`  
`20261009093725_w48_seed_research_agent_for_new_workspaces.sql`  
`20261009171718_w49_agent_execution_recovery.sql`  
`20261009171722_w50_expired_execution_lease_fence.sql`  
`20261009185119_w51_member_rpc_wrapper_permissions.sql`

### 6 hosted-only entries

`20261007105825_expose_anonymous_ai_guard_rpc.sql`  
`20261005053351_w35_plan_ai_allowances_5_50_300.sql`  
`20261008150359_w44_workspace_invitations_and_activity.sql`  
`20261008161103_w46_invitation_activity_bindings.sql`  
`20260921180227_w4_harden_profile_trigger_search_path.sql`  
`20260924171437_w6_authoritative_mission_mutation_and_concurrency.sql`

## Relevant historical clue — source file first surfaced as an addition

GitHub history for source-side file `supabase/migrations/20260921180052_w4_table_privilege_hardening.sql` identifies commit [`772f011624c199adc021a61d039a4cf13e9a3740`](https://github.com/abdalrhmanata-gif/nexo-w21-isolated-verification-20261015/commit/772f011624c199adc021a61d039a4cf13e9a3740), dated **2026-09-25 21:11:21 UTC**, where that source file is marked **added**. The commit message is `merge: stage ZAVQERA integration without historical artifact`. This reinforces that the current source-side text does not itself supply the missing historical deployment proof. It does not prove which SQL was executed on Development.

## Limits and disposition

This is a snapshot sweep of the 27 branch tips visible from GitHub on 2026-10-18. It does **not** enumerate every historical commit object, deleted/unreachable branch, fork, private/external repository, workstation clone, or deployment/backup archive. A file absent from branch tips is not evidence that it was never executed.

For all 22 conflicting and six hosted-only entries:
- Keep owner review pending and deployed SQL digests/deployment record URIs blank unless trusted evidence is recovered.
- Do not generate SQL from inference, rewrite the hosted migration ledger, or declare exact-byte equivalence from matching names/timestamps/schema.
- Continue searching authoritative deployment/audit exports and backups. If unrecoverable, record `UNKNOWN_BLOCKING` and plan a separately reviewed re-baselining path.
- Keep `hosted_write_authorized=false`, `TRUSTED_DISPATCH_ADAPTERS` empty/fail-closed, PR #1/#2 open/draft/unmerged, and release **NO-GO**.

No database connection, SQL execution, hosted write, migration, deployment, secret change, billing/DNS change, or PR merge was part of this scan.

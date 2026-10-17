# ZAVQERA — Expanded historical migration-source recovery check (2026-10-17)

**Disposition: historical SQL provenance remains UNKNOWN / release NO-GO.** This document records a wider offline/public-GitHub search. It does not reconstruct SQL and does not authorize changes to any hosted database.

## 1. Scope of this pass

### Current branch-head tree scan

Repository: \`abdalrhmanata-gif/Nexo\`

- Fetched the repository's 23 visible branch refs and scanned each branch-head Git tree recursively.
- All 23 tree responses returned successfully with \`truncated=false\`.
- Counted SQL files directly under \`supabase/migrations\`, then matched the migration suffix independently of its numeric timestamp. This is wider than searching for only the exact hosted filename.
- Result: the 22 known same-name/version conflicts were present on relevant branch heads only under the currently checked-in/source-side timestamp. None of the 22 hosted timestamp filenames was found in the 23 current branch-head trees.
- Result: none of the six hosted-only migration names was found in any scanned current branch-head tree. Similar names were not treated as equivalent.

### Commit-history follow-up

For all 22 current source migration paths, requested GitHub commit history scoped to \`zavqera/ai-planner-integration\`:

- 21 paths returned one reachable introducing/changed commit each.
- \`20261009170000_w50_expired_execution_lease_fence.sql\` returned two commits, both modifying the current source-side path.
- The historic base migration paths W4 table privilege hardening, W7, W8, W9, W9.1 and W10 point to commit \`772f011624c199adc021a61d039a4cf13e9a3740\`, whose message is **“merge: stage ZAVQERA integration without historical artifact”**. In that commit these files are marked \`added\`, not as a recoverable rename from a historic timestamp path.
- The parent of that commit, \`fcac980c9909c1a083007ed120d4742584fbcb4e\`, contains zero files under \`supabase/migrations\`.
- Prior provenance notes also recorded 644 exact historic-path/ref checks (28 filenames × 23 visible refs) with zero commits returned. This exact-path search is historical supporting evidence; it did not by itself establish file equivalence.

### GitHub Actions artifact search

- Inspected run metadata pages 1–20 from \`abdalrhmanata-gif/Nexo\`: 2,000 run records, spanning approximately \`2026-10-17T04:41:56Z\` through \`2026-10-12T10:37:25Z\`. The API reported 10,590 total workflow runs during this search, so this was a bounded 2,000-run window, not the full archive.
- Filtered the returned records for W21 Local Launch Gate, W25 Isolated PostgreSQL Atomic Fence and W80-style workflow labels where present.
- Checked representative W21 artifact inventories from 2026-10-12 through 2026-10-15. They contained only the small \`zavqera-w21-evidence\` (326–328 bytes) and \`zavqera-w21-browser-diagnostics\` (661–743 bytes) artifacts. Representative W21 runs checked: \`38247173973\`, \`38248625444\`, \`38280173757\`, \`38285709683\`, \`38629459754\`, \`38683741782\`, \`38701020891\`, and \`38713041690\`.
- Three recent W25 run inventories checked (\`39003340849\`, \`39003517132\`, \`39003536576\`) had no artifacts.
- No historic SQL source archive was identified in these checked artifact inventories. Run logs/artifact metadata are not a substitute for the original migration SQL bytes.
- This search does not inspect every artifact for all 10,590 runs and does not rule out private/local/deleted repositories, external deployment bundles, user-machine Git objects/reflogs, or backups.

## 2. The unresolved version conflicts

The hosted ledger has these versions; the checked-in source has the following different versions. No hosted-version path was recovered in the visible branch-head scan.

| Migration name | Checked-in source version | Hosted ledger version |
|---|---:|---:|
| \`w10_deletion_integrity_read_boundary\` | \`20260924220000\` | \`20260924180025\` |
| \`w16_audit_history_table_hardening\` | \`20260926100000\` | \`20260926060416\` |
| \`w30_reconstruct_missing_w5_history_tables\` | \`20260924165500\` | \`20261004083051\` |
| \`w30_server_only_quota_rls_deny_policy\` | \`20261004080000\` | \`20261004074420\` |
| \`w36_enable_pro_plan_identity\` | \`20261005080400\` | \`20261005080648\` |
| \`w41_seed_bounded_research_agent\` | \`20261008150000\` | \`20261008142204\` |
| \`w42_workspace_rpc_authorization_parity\` | \`20261008152000\` | \`20261008145424\` |
| \`w43_bounded_agent_execution_runtime\` | \`20261008152500\` | \`20261008145525\` |
| \`w44_invitation_lifecycle\` | \`20261008170000\` | \`20261008155642\` |
| \`w45_workspace_member_management\` | \`20261008171000\` | \`20261008160824\` |
| \`w46_activity_security_hardening\` | \`20261008173000\` | \`20261008161617\` |
| \`w46_workspace_activity_audit\` | \`20261008172000\` | \`20261008161055\` |
| \`w47_atomic_workspace_bootstrap\` | \`20261009120000\` | \`20261009092613\` |
| \`w48_seed_research_agent_for_new_workspaces\` | \`20261009140000\` | \`20261009093725\` |
| \`w49_agent_execution_recovery\` | \`20261009150000\` | \`20261009171718\` |
| \`w4_table_privilege_hardening\` | \`20260921180052\` | \`20260921180138\` |
| \`w50_expired_execution_lease_fence\` | \`20261009170000\` | \`20261009171722\` |
| \`w51_member_rpc_wrapper_permissions\` | \`20261009183000\` | \`20261009185119\` |
| \`w7_authoritative_action_mutation\` | \`20260924190000\` | \`20260924172730\` |
| \`w8_lifecycle_integrity_provenance\` | \`20260924200000\` | \`20260924173730\` |
| \`w9_1_completed_outcome_guard\` | \`20260924211000\` | \`20260924175412\` |
| \`w9_verification_outcome_lifecycle\` | \`20260924210000\` | \`20260924174933\` |

## 3. Six hosted-only migration names not present in the checked-in source names

No matching suffix/file name for these six was found in any of the 23 visible branch-head migration trees:

| Hosted version | Hosted migration name |
|---:|---|
| \`20260921180227\` | \`w4_harden_profile_trigger_search_path\` |
| \`20260924171437\` | \`w6_authoritative_mission_mutation_and_concurrency\` |
| \`20261005053351\` | \`w35_plan_ai_allowances_5_50_300\` |
| \`20261007105825\` | \`expose_anonymous_ai_guard_rpc\` |
| \`20261008150359\` | \`w44_workspace_invitations_and_activity\` |
| \`20261008161103\` | \`w46_invitation_activity_bindings\` |

A similarly named source migration, such as \`w6_authoritative_mission_mutation\`, must not be assumed to contain the SQL that was deployed under \`w6_authoritative_mission_mutation_and_concurrency\`.

## 4. What can and cannot be concluded

**Supported conclusion:** this expanded public branch-head and bounded Actions-artifact check recovered no authoritative historical SQL bytes for the 22 version conflicts or six hosted-only names.

**Not supported:** that the historical SQL never existed, that the checked-in source bytes equal deployed bytes, that the changes are semantically equivalent, or that the hosted ledger can be rewritten to match source.

The valid classification for all unresolved historical bytes remains \`UNKNOWN\`. Recovery paths still worth checking include owner-controlled local clones and Git reflogs/objects, backup snapshots, deployment bundles, CI caches or archives not represented by the sampled artifacts, and any source repository maintained by a database owner. Any recovered SQL must be tied to a trusted provenance chain and deployment identity before being classified as authoritative.

## 5. Mandatory disposition

- Keep \`hosted_write_authorized=false\`.
- Do not apply W86 or any other migration to hosted Development or Main/Production.
- Do not manually repair or rewrite \`supabase_migrations.schema_migrations\`.
- Do not reconstruct old SQL from current code or adjacent migration files.
- Require independent database-owner review, authoritative source recovery, isolated revalidation and separate explicit authorization before any future hosted change.

**Result: SOURCE RECOVERY NOT ACHIEVED. RELEASE NO-GO.**

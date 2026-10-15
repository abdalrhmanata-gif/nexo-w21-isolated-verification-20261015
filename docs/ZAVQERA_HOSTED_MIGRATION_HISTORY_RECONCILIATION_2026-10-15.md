# ZAVQERA — Hosted Migration History Reconciliation (2026-10-15)

**Decision: BLOCKED / RELEASE NO-GO.** This is a read-only evidence reconciliation. No migration ledger rows were edited, no DDL/DML was run, no deployment occurred, and no hosted database was changed.

## Evidence identity

- Project: ZAVQERA Development; ref mrwmmbytcymqgwvcoywd; region eu-west-1.
- Observed at UTC: 2026-10-15T17:18:09.104812+00:00.
- Endpoint: Supabase Management API /database/query/read-only.
- Gate: current_user = supabase_read_only_user; transaction_read_only = true; server_version_num = 170006.
- Query pack SHA-256: 2462ff5f494b1acc6dd75e8290aa9eeb4fda4e4899a590e697d3c5a0be5790d2.
- Captured evidence ZIP SHA-256: dfc507963929356f9cbdeacc343a564dcd647addf17bd811d3543ff2a2237c36.
- Evidence ZIP contained eight query responses and the summary; no access token was saved in that output.

## Exact comparison

| Measure | Count |
|---|---:|
| Current checked-in migrations | 89 |
| Hosted migration ledger rows | 74 |
| Exact version + name matches | 46 |
| Same migration name, different timestamp | 22 |
| Local names absent from hosted ledger by exact name | 21 |
| Hosted names absent from current source by exact name | 6 |
| Current local tuples absent from ledger | 43 |
| Hosted tuples absent from current source | 28 |

A same-name/timestamp match is only a candidate lineage mapping. The hosted ledger contains version/name metadata, not the historical SQL bytes or a checksum. No mismatch may be resolved by changing timestamps or inserting/deleting ledger rows without recovering the deployed source and comparing effects.

## 22 same-name timestamp differences

| Name | Current local version | Hosted ledger version |
|---|---:|---:|
| w10_deletion_integrity_read_boundary | 20260924220000 | 20260924180025 |
| w16_audit_history_table_hardening | 20260926100000 | 20260926060416 |
| w30_reconstruct_missing_w5_history_tables | 20260924165500 | 20261004083051 |
| w30_server_only_quota_rls_deny_policy | 20261004080000 | 20261004074420 |
| w36_enable_pro_plan_identity | 20261005080400 | 20261005080648 |
| w41_seed_bounded_research_agent | 20261008150000 | 20261008142204 |
| w42_workspace_rpc_authorization_parity | 20261008152000 | 20261008145424 |
| w43_bounded_agent_execution_runtime | 20261008152500 | 20261008145525 |
| w44_invitation_lifecycle | 20261008170000 | 20261008155642 |
| w45_workspace_member_management | 20261008171000 | 20261008160824 |
| w46_activity_security_hardening | 20261008173000 | 20261008161617 |
| w46_workspace_activity_audit | 20261008172000 | 20261008161055 |
| w47_atomic_workspace_bootstrap | 20261009120000 | 20261009092613 |
| w48_seed_research_agent_for_new_workspaces | 20261009140000 | 20261009093725 |
| w49_agent_execution_recovery | 20261009150000 | 20261009171718 |
| w4_table_privilege_hardening | 20260921180052 | 20260921180138 |
| w50_expired_execution_lease_fence | 20261009170000 | 20261009171722 |
| w51_member_rpc_wrapper_permissions | 20261009183000 | 20261009185119 |
| w7_authoritative_action_mutation | 20260924190000 | 20260924172730 |
| w8_lifecycle_integrity_provenance | 20260924200000 | 20260924173730 |
| w9_1_completed_outcome_guard | 20260924211000 | 20260924175412 |
| w9_verification_outcome_lifecycle | 20260924210000 | 20260924174933 |

## 21 local names with no same-name hosted row

| Local version | Local name |
|---:|---|
| 20261008160000 | w44_workspace_invitations |
| 20260921180053 | w5_audit_history_replay_baseline |
| 20261011160000 | w66_service_role_table_privilege_hardening |
| 20261011165000 | w67_legacy_research_rpc_privilege_hardening |
| 20261011170000 | w68_persistent_authority_budget_reservations |
| 20261011180000 | w69_one_time_jit_dispatch_claim |
| 20260924170000 | w6_authoritative_mission_mutation |
| 20261011190000 | w70_durable_unknown_outcome_reconciliation |
| 20261012070000 | w71_expired_external_execution_budget_recovery |
| 20261012120000 | w73_trusted_system_mission_events |
| 20261012130000 | w74_reconciliation_claim_freshness |
| 20261012140000 | w75_correlatable_provider_receipt |
| 20261012150000 | w76_guard_external_success_on_insert |
| 20261012160000 | w77_read_only_research_payload_bounds |
| 20261012170000 | w78_bind_research_history_to_execution |
| 20261012180000 | w79_trusted_research_completion |
| 20261013100000 | w80_fail_closed_workspace_role_checks |
| 20261014110000 | w81_read_only_research_jit_claim |
| 20261014130000 | w82_ai_generation_reservation_identity |
| 20261015100000 | w83_workspace_invitation_privilege_correction |
| 20261015110000 | w84_postgres_function_default_acl_hardening |

The W44, W6 and W5 files need special historical-source checks. The 18 candidate files W66–W71 and W73–W84 are not found in the current hosted ledger by exact version/name; the ledger alone does not prove every corresponding effect is absent, so check schema effects independently.

## 6 hosted ledger names with no same-name local file

| Hosted version | Hosted name |
|---:|---|
| 20261007105825 | expose_anonymous_ai_guard_rpc |
| 20261005053351 | w35_plan_ai_allowances_5_50_300 |
| 20261008150359 | w44_workspace_invitations_and_activity |
| 20261008161103 | w46_invitation_activity_bindings |
| 20260921180227 | w4_harden_profile_trigger_search_path |
| 20260924171437 | w6_authoritative_mission_mutation_and_concurrency |

Recover the exact historical migration from the branch/commit/artifact that was deployed. Candidate relationships by naming similarity are not proof of identical SQL.

## Independently observed catalog mismatches

1. **W80:** private.can_edit_workspace(uuid, uuid) is SECURITY DEFINER and has configured search_path public, private. Current checked-in W80 specifies pg_catalog, public, private. This is confirmed catalog/source drift; exploitability is not inferred from this alone.
2. **W82:** hosted public.reserve_ai_generation(text) and private.reserve_ai_generation(text) remain the old single-argument signatures. The current W82 source defines a three-argument identity-bound contract. The catalog reports effective service_role EXECUTE on the old signatures.
3. **W83:** public.get_workspace_invitation(text) is SECURITY INVOKER in the captured catalog, while current W83 expects SECURITY DEFINER. All four public invitation wrappers (create/get/accept/revoke) show effective service_role EXECUTE; W83 candidate explicitly revokes the direct service_role grant.
4. **Private invitation helper:** private.create_workspace_invitation has a NULL stored ACL and the function-privilege probe reports effective execution for anon/authenticated/service_role. This query pack did not capture effective USAGE on schema private, so reachability and impact are not established. Run the dedicated W83 schema-usage check before classification.
5. **W84 default ACL:** the captured built-in global baseline grants function EXECUTE to PUBLIC for creator roles postgres and supabase_admin. The explicit public-schema function default ACLs report EXECUTE to anon, authenticated and service_role for both creators. W84 hardens postgres-created future functions only; it explicitly leaves supabase_admin defaults owner-managed. A separate database/platform owner decision is required.
6. **W66 relation privileges:** the eight-query pack did not include direct table ACL inventory. The effect of W66 must be rechecked with a dedicated read-only relation-ACL query; do not infer its current state solely from this pack.

The queries surfaced 87 non-system routines, several role-membership paths and 276 default-ACL rows. The highlighted findings are not a substitute for reviewing every function owner, security mode, ACL, effective privilege, schema USAGE, membership and default ACL.

## Safe action sequence

1. Keep Release NO-GO. Preserve the evidence. Do not run hosted db push, migration repair, direct edits to supabase_migrations.schema_migrations, or hosted replays.
2. Recover and content-hash historical SQL for all 22 timestamp conflicts and 6 hosted-only names. Diff those SQL files against the current branch; record exact, equivalent-but-different, or unresolved.
3. Build an effect matrix for each local-only candidate and every historical mismatch. Query table/column/index/constraint/function existence and definitions, grants, memberships, search_path and default ACLs using a verified read-only session. Specifically add table ACL probes for W66 and schema USAGE probes for W83.
4. Separate history reconciliation from security repair. Do not fake historical rows or change versions to force a match.
5. Only after the history and effect matrix is complete, prepare the smallest forward-only repair migration(s), without applying them to hosted projects.
6. Replay the reconstructed source on disposable PostgreSQL 17, run the unchanged W21 and W80/W82/W83/W84 tests, and capture exact SHA, artifacts and cleanup proof.
7. Have an authorized database/platform owner review supabase_admin default ACL policy plus all SECURITY DEFINER routines. Any future hosted migration requires a separate explicit approval; Main/Production is out of scope here.

## Release and repository guardrails

Original abdalrhmanata-gif/Nexo was not changed. Do not merge PR #39; keep it open/Draft. Keep Issue #23 open. Keep TRUSTED_DISPATCH_ADAPTERS empty/fail-closed. Hosted Development and Main/Production remain unmodified by this reconciliation.

**Final disposition: BLOCKED / NO-GO.** The next deliverable is a source-backed historical migration manifest and effect matrix. Ledger repair before that would risk marking security changes applied without evidence or replaying DDL against live state.


## Follow-up pack extension — 2026-10-15 (not yet executed)

The historical mapping above remains tied to the earlier captured 74-row ledger. The later 10-query effect capture identified selected schema and routine gaps but did not enumerate current ledger version/name pairs or directly inspect effective/stored ACLs on `public.agent_executions`. The updated pinned pack adds query 11 (ledger version/name only) and query 12 (effective table privileges plus expanded stored ACL). New pack SHA-256: `a7aba3461786dbb5854f71dc4f87b7e0498d12509add535ab3df4a7ec231a284`.

This 12-query version awaits isolated CI/disposable PostgreSQL 17 verification and a fresh user-executed read-only capture. Do not reuse the prior 74-row count as an assumption; compare the new ledger response with the checked-in files row-by-row. No ledger repair or hosted migration is authorized.


## Expanded source-recovery check — 2026-10-15

The six hosted-only names listed above were checked against every current branch ref in abdalrhmanata-gif/Nexo (23 refs; duplicate head commits deduplicated for tree inspection). None appears in a current branch-tip migration tree. Exact-path GitHub commit-history queries also returned zero commits for those paths. This makes the recovery issue more concrete: the current visible branch tips do not contain those files, and the current path histories do not offer recoverable source.

This is not proof the migrations never existed in a private/deleted/local commit or deployment artifact. Keep their effects UNKNOWN until exact historical SQL or equivalent trusted provenance is recovered. Do not recreate these migrations from their names.



## Fresh 12-query ledger and W66 ACL evidence — 2026-10-15 18:45 UTC

New uploaded evidence ZIP SHA-256: `fff6f88aca42c73dc691ead099e969f3cfc911fea5504ce1291b6e04ae0320f6`; query-pack SHA-256: `a7aba3461786dbb5854f71dc4f87b7e0498d12509add535ab3df4a7ec231a284`. The 12-query capture reports the same 74 hosted ledger rows in the earlier 8-query reconciliation and adds current row details plus W66 table ACL effects.

Reconciliation counts are internally consistent: 89 source migrations; 74 hosted rows; 46 exact tuples; 22 same-name/timestamp conflicts; 43 source tuples absent from the hosted exact tuple set; 28 hosted tuples absent from the source exact tuple set; 21 source names absent by exact name; six hosted names absent by exact name.

Most important new result: `service_role` still has all eight queried effective privileges and explicit stored ACL privileges on `public.agent_executions`, including INSERT, UPDATE, DELETE and TRUNCATE. This directly disagrees with W66’s checked-in `REVOKE ALL PRIVILEGES` effect. Treat as a critical security blocker; do not patch the hosted database or migration ledger without historical/source reconciliation, a reviewed forward-only candidate and separate owner approval.

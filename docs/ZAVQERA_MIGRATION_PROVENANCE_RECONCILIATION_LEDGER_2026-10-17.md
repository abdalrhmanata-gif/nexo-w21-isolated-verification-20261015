# ZAVQERA — migration provenance reconciliation ledger (2026-10-17)

**Status: INCOMPLETE / INDEPENDENT OWNER REVIEW REQUIRED / RELEASE NO-GO.** This ledger reconciles the exact version/name metadata in the captured hosted ledger against the reviewed source migration inventory. It does not prove deployed SQL-byte equality and does not authorize hosted changes.

## Evidence identity

- Hosted capture: `20261017T151516202599Z.zip`
- Hosted capture SHA-256: `9cee349552ddc4daf3a30c109ac570963313d35915b11308130916cb4773d79d`
- Capture time (UTC): `2026-10-17T15:15:16.204988+00:00`
- Project: `ZAVQERA Development` (`mrwmmbytcymqgwvcoywd`), region `eu-west-1`
- PostgreSQL: `server_version_num=170006` (17.6)
- Reported source checkout HEAD: `fbbcb080904acd88aad83a082803f627859026e2`
- Source migration manifest SHA-256: `0d05ab7285edc975084ddbc595d1af7d2dd0752cc27e94d8fe0549170419be38`
- Query-pack SHA-256: `a7aba3461786dbb5854f71dc4f87b7e0498d12509add535ab3df4a7ec231a284`
- Query 13 SHA-256: `806c1fbc1842860387dea71cdcefc6d02edf8e4f23ad1aa07ece96c1a1a8312b`

## Source manifest line-ending reconciliation — 2026-10-17

The recorded manifest discrepancy was investigated without changing any migration SQL:

- Captured raw-checkout manifest SHA-256: `0d05ab7285edc975084ddbc595d1af7d2dd0752cc27e94d8fe0549170419be38`.
- The reproducible Linux/LF checkout manifest was `555db007d0c25ee7bf6ed4f983766eea1dde170a7ef5d0e12cc710d5838c7094`.
- GitHub resolves the reported source HEAD `fbbcb080904acd88aad83a082803f627859026e2` in this isolated audit repository, and that tree contains 89 migration files. Comparing that commit to the current audit branch showed no changed paths under `supabase/migrations`.
- The isolated W80 pre-database test verified that the captured digest matches the simulated CRLF checkout manifest and differs from the LF checkout manifest. This identifies a checkout line-ending representation difference; it does not prove the historical SQL bytes executed by Supabase.
- The reviewer now emits both the raw working-tree manifest and a separate LF-normalized manifest so future captures can be compared across Windows/Linux checkout settings. The normalized manifest SHA-256 for the 89 current source files is `555db007d0c25ee7bf6ed4f983766eea1dde170a7ef5d0e12cc710d5838c7094`, independently reconstructed from the exact-SHA W80 artifact's 89-file SHA list. The existing ZIP remains unchanged and its original raw manifest value is preserved.

**Limit:** only the local-source manifest representation has been reconciled. Historical deployed SQL bytes and deployment provenance remain unverified; the 46 exact version/name metadata matches stay `UNKNOWN`, all owner reviews remain `PENDING`, and release remains NO-GO.

## Reconciliation totals

| Measure | Count | Interpretation |
|---|---:|---|
| Source migration files | 89 | The source inventory used by the offline reviewer |
| Hosted migration ledger rows | 74 | Query 11 read-only metadata |
| Exact version/name metadata matches | 46 | Classification remains `UNKNOWN` for SQL bytes |
| Same-name / different-version conflicts | 22 | `NAME_VERSION_CONFLICT` |
| Source tuples absent from hosted exact tuples | 43 | Includes 22 conflict source tuples + 21 source-only tuples |
| Hosted tuples absent from source exact tuples | 28 | Includes 22 conflict hosted tuples + 6 hosted-only tuples |
| Source-only tuples excluding conflicts | 21 | `SOURCE_NOT_IN_LEDGER` |
| Hosted-only tuples excluding conflicts | 6 | `HOSTED_ONLY_SOURCE_UNKNOWN` |
| Reconciliation units | 95 | 46 metadata matches + 22 conflicts + 21 source-only + 6 hosted-only |

**Count rule:** the 43 source-unmatched and 28 hosted-unmatched totals overlap the 22 version conflicts. Do not add these aggregate counts as disjoint groups.

## Complete row ledger

Each row is pending independent review. `UNKNOWN` means the version/name metadata can align but authoritative source SQL bytes and deployment evidence have not been linked. No item is classified `EXACT_SOURCE_BYTES_VERIFIED`.

| ID | Source version | Source name | Hosted version | Hosted name | Metadata relation | Classification | Source SQL SHA-256 in review output | Owner review |
|---|---|---|---|---|---|---|---|---|
| ZMR-001 | 20260921175955 | w4_core_tables_and_indexes | 20260921175955 | w4_core_tables_and_indexes | EXACT_VERSION_NAME_TUPLE | UNKNOWN | UNKNOWN — not emitted per-file in the review JSON | PENDING |
| ZMR-002 | 20260921180001 | w4_timestamp_triggers | 20260921180001 | w4_timestamp_triggers | EXACT_VERSION_NAME_TUPLE | UNKNOWN | UNKNOWN — not emitted per-file in the review JSON | PENDING |
| ZMR-003 | 20260921180006 | w4_profile_auth_trigger | 20260921180006 | w4_profile_auth_trigger | EXACT_VERSION_NAME_TUPLE | UNKNOWN | UNKNOWN — not emitted per-file in the review JSON | PENDING |
| ZMR-004 | 20260921180015 | w4_profiles_and_workspaces_rls | 20260921180015 | w4_profiles_and_workspaces_rls | EXACT_VERSION_NAME_TUPLE | UNKNOWN | UNKNOWN — not emitted per-file in the review JSON | PENDING |
| ZMR-005 | 20260921180021 | w4_missions_rls | 20260921180021 | w4_missions_rls | EXACT_VERSION_NAME_TUPLE | UNKNOWN | UNKNOWN — not emitted per-file in the review JSON | PENDING |
| ZMR-006 | 20260921180030 | w4_mission_actions_rls | 20260921180030 | w4_mission_actions_rls | EXACT_VERSION_NAME_TUPLE | UNKNOWN | UNKNOWN — not emitted per-file in the review JSON | PENDING |
| ZMR-007 | 20260921180044 | w4_auth_trigger_privilege_hardening | 20260921180044 | w4_auth_trigger_privilege_hardening | EXACT_VERSION_NAME_TUPLE | UNKNOWN | UNKNOWN — not emitted per-file in the review JSON | PENDING |
| ZMR-008 | 20260921180052 | w4_table_privilege_hardening | 20260921180138 | w4_table_privilege_hardening | SAME_NAME_DIFFERENT_VERSION | NAME_VERSION_CONFLICT | 43b8aeac20e00ce8170f5064a8622a66f7cee58c6cc25d4ff0afeb59b83ed044 | PENDING |
| ZMR-009 | 20260921180053 | w5_audit_history_replay_baseline | — | — | SOURCE_TUPLE_ABSENT_FROM_HOSTED_LEDGER | SOURCE_NOT_IN_LEDGER | 00ac604863ffec7b7b14f4a402ebe59da40c50b10d444b3a736b389a35a48410 | PENDING |
| ZMR-010 | 20260924165026 | w5_verification_outcome_audit_tables | 20260924165026 | w5_verification_outcome_audit_tables | EXACT_VERSION_NAME_TUPLE | UNKNOWN | UNKNOWN — not emitted per-file in the review JSON | PENDING |
| ZMR-011 | 20260924165031 | w5_server_only_verification_outcome_access | 20260924165031 | w5_server_only_verification_outcome_access | EXACT_VERSION_NAME_TUPLE | UNKNOWN | UNKNOWN — not emitted per-file in the review JSON | PENDING |
| ZMR-012 | 20260924165042 | w5_verification_command_boundary | 20260924165042 | w5_verification_command_boundary | EXACT_VERSION_NAME_TUPLE | UNKNOWN | UNKNOWN — not emitted per-file in the review JSON | PENDING |
| ZMR-013 | 20260924165050 | w5_verified_outcome_commit_boundary | 20260924165050 | w5_verified_outcome_commit_boundary | EXACT_VERSION_NAME_TUPLE | UNKNOWN | UNKNOWN — not emitted per-file in the review JSON | PENDING |
| ZMR-014 | 20260924165056 | w5_append_only_history_hardening | 20260924165056 | w5_append_only_history_hardening | EXACT_VERSION_NAME_TUPLE | UNKNOWN | UNKNOWN — not emitted per-file in the review JSON | PENDING |
| ZMR-015 | 20260924165500 | w30_reconstruct_missing_w5_history_tables | 20261004083051 | w30_reconstruct_missing_w5_history_tables | SAME_NAME_DIFFERENT_VERSION | NAME_VERSION_CONFLICT | 9535d37eca3016aef22d4ae46ab9bf6b66260eab4e8a16da646168f67254ac78 | PENDING |
| ZMR-016 | 20260924170000 | w6_authoritative_mission_mutation | — | — | SOURCE_TUPLE_ABSENT_FROM_HOSTED_LEDGER | SOURCE_NOT_IN_LEDGER | 287a5b74c3cbb0955fe3e4492599508af769bc91e575db49d8c3a5e6950de957 | PENDING |
| ZMR-017 | 20260924180454 | w11_performance_rls_optimization | 20260924180454 | w11_performance_rls_optimization | EXACT_VERSION_NAME_TUPLE | UNKNOWN | UNKNOWN — not emitted per-file in the review JSON | PENDING |
| ZMR-018 | 20260924190000 | w7_authoritative_action_mutation | 20260924172730 | w7_authoritative_action_mutation | SAME_NAME_DIFFERENT_VERSION | NAME_VERSION_CONFLICT | b10e159fc0a2bdb22bfb5ddfdffb1d7ea54b901dc6bc7622ddd4e5f6f0689877 | PENDING |
| ZMR-019 | 20260924200000 | w8_lifecycle_integrity_provenance | 20260924173730 | w8_lifecycle_integrity_provenance | SAME_NAME_DIFFERENT_VERSION | NAME_VERSION_CONFLICT | 345618a321263fce57549eb1846ef6a0dd086be0e941cc3f41146a2a138ccef0 | PENDING |
| ZMR-020 | 20260924210000 | w9_verification_outcome_lifecycle | 20260924174933 | w9_verification_outcome_lifecycle | SAME_NAME_DIFFERENT_VERSION | NAME_VERSION_CONFLICT | 6daf32a69e6f600fff4eb5ca3bf6f3843d74e0f59354a5f01cce6e8123e7dbd6 | PENDING |
| ZMR-021 | 20260924211000 | w9_1_completed_outcome_guard | 20260924175412 | w9_1_completed_outcome_guard | SAME_NAME_DIFFERENT_VERSION | NAME_VERSION_CONFLICT | ce6293c13f946ae6180fdef269238c60ceed5a7dc51e96d0b27ee9f2b54fe688 | PENDING |
| ZMR-022 | 20260924220000 | w10_deletion_integrity_read_boundary | 20260924180025 | w10_deletion_integrity_read_boundary | SAME_NAME_DIFFERENT_VERSION | NAME_VERSION_CONFLICT | f1feed7c1cbd8603e3eefcb50ba2daf146f9a5490e477b2a3cca2d2407e9d795 | PENDING |
| ZMR-023 | 20260926100000 | w16_audit_history_table_hardening | 20260926060416 | w16_audit_history_table_hardening | SAME_NAME_DIFFERENT_VERSION | NAME_VERSION_CONFLICT | ba566c0ae365fd82a826503bf6d8db3cec29fbf8930fe93dea0df8bd2118af92 | PENDING |
| ZMR-024 | 20260929182538 | w18_action_follow_up_persistence | 20260929182538 | w18_action_follow_up_persistence | EXACT_VERSION_NAME_TUPLE | UNKNOWN | UNKNOWN — not emitted per-file in the review JSON | PENDING |
| ZMR-025 | 20261001081755 | w20_cancelled_action_completion_semantics | 20261001081755 | w20_cancelled_action_completion_semantics | EXACT_VERSION_NAME_TUPLE | UNKNOWN | UNKNOWN — not emitted per-file in the review JSON | PENDING |
| ZMR-026 | 20261001091146 | w21_authoritative_completion_integrity | 20261001091146 | w21_authoritative_completion_integrity | EXACT_VERSION_NAME_TUPLE | UNKNOWN | UNKNOWN — not emitted per-file in the review JSON | PENDING |
| ZMR-027 | 20261001184951 | w22_ai_usage_quota_and_reservations | 20261001184951 | w22_ai_usage_quota_and_reservations | EXACT_VERSION_NAME_TUPLE | UNKNOWN | UNKNOWN — not emitted per-file in the review JSON | PENDING |
| ZMR-028 | 20261001185058 | w22_ai_usage_privilege_hardening | 20261001185058 | w22_ai_usage_privilege_hardening | EXACT_VERSION_NAME_TUPLE | UNKNOWN | UNKNOWN — not emitted per-file in the review JSON | PENDING |
| ZMR-029 | 20261002114358 | w26_atomic_mission_creation | 20261002114358 | w26_atomic_mission_creation | EXACT_VERSION_NAME_TUPLE | UNKNOWN | UNKNOWN — not emitted per-file in the review JSON | PENDING |
| ZMR-030 | 20261002172509 | w27_ai_usage_search_path_hardening | 20261002172509 | w27_ai_usage_search_path_hardening | EXACT_VERSION_NAME_TUPLE | UNKNOWN | UNKNOWN — not emitted per-file in the review JSON | PENDING |
| ZMR-031 | 20261002192325 | w28_all_definer_search_path_hardening | 20261002192325 | w28_all_definer_search_path_hardening | EXACT_VERSION_NAME_TUPLE | UNKNOWN | UNKNOWN — not emitted per-file in the review JSON | PENDING |
| ZMR-032 | 20261003170104 | w29_fix_ai_usage_period_conflict | 20261003170104 | w29_fix_ai_usage_period_conflict | EXACT_VERSION_NAME_TUPLE | UNKNOWN | UNKNOWN — not emitted per-file in the review JSON | PENDING |
| ZMR-033 | 20261004080000 | w30_server_only_quota_rls_deny_policy | 20261004074420 | w30_server_only_quota_rls_deny_policy | SAME_NAME_DIFFERENT_VERSION | NAME_VERSION_CONFLICT | 9380442b56d45494a2715f8f992630e1e6c07edd2c052325c10b8d7f59acc118 | PENDING |
| ZMR-034 | 20261004150738 | w31_mission_transition_serialization | 20261004150738 | w31_mission_transition_serialization | EXACT_VERSION_NAME_TUPLE | UNKNOWN | UNKNOWN — not emitted per-file in the review JSON | PENDING |
| ZMR-035 | 20261004180528 | w32_move_rpc_definers_to_private | 20261004180528 | w32_move_rpc_definers_to_private | EXACT_VERSION_NAME_TUPLE | UNKNOWN | UNKNOWN — not emitted per-file in the review JSON | PENDING |
| ZMR-036 | 20261004191348 | w33_free_ai_limit_five | 20261004191348 | w33_free_ai_limit_five | EXACT_VERSION_NAME_TUPLE | UNKNOWN | UNKNOWN — not emitted per-file in the review JSON | PENDING |
| ZMR-037 | 20261004191431 | w34_plan_quota_constraints | 20261004191431 | w34_plan_quota_constraints | EXACT_VERSION_NAME_TUPLE | UNKNOWN | UNKNOWN — not emitted per-file in the review JSON | PENDING |
| ZMR-038 | 20261005080400 | w36_enable_pro_plan_identity | 20261005080648 | w36_enable_pro_plan_identity | SAME_NAME_DIFFERENT_VERSION | NAME_VERSION_CONFLICT | 7f5beb84a016495175d769844cef19c829e90f72de7c717a17864c05b2f6916f | PENDING |
| ZMR-039 | 20261006120927 | anonymous_ai_plan_guard | 20261006120927 | anonymous_ai_plan_guard | EXACT_VERSION_NAME_TUPLE | UNKNOWN | UNKNOWN — not emitted per-file in the review JSON | PENDING |
| ZMR-040 | 20261008133407 | grant_authenticated_execute_record_mission_event | 20261008133407 | grant_authenticated_execute_record_mission_event | EXACT_VERSION_NAME_TUPLE | UNKNOWN | UNKNOWN — not emitted per-file in the review JSON | PENDING |
| ZMR-041 | 20261008133915 | w37_move_record_mission_event_to_private | 20261008133915 | w37_move_record_mission_event_to_private | EXACT_VERSION_NAME_TUPLE | UNKNOWN | UNKNOWN — not emitted per-file in the review JSON | PENDING |
| ZMR-042 | 20261008141939 | w38_business_collaboration_approvals_agents | 20261008141939 | w38_business_collaboration_approvals_agents | EXACT_VERSION_NAME_TUPLE | UNKNOWN | UNKNOWN — not emitted per-file in the review JSON | PENDING |
| ZMR-043 | 20261008142004 | w39_workspace_membership_policy_execution | 20261008142004 | w39_workspace_membership_policy_execution | EXACT_VERSION_NAME_TUPLE | UNKNOWN | UNKNOWN — not emitted per-file in the review JSON | PENDING |
| ZMR-044 | 20261008142018 | w40_approval_gate_and_collaborative_verification | 20261008142018 | w40_approval_gate_and_collaborative_verification | EXACT_VERSION_NAME_TUPLE | UNKNOWN | UNKNOWN — not emitted per-file in the review JSON | PENDING |
| ZMR-045 | 20261008150000 | w41_seed_bounded_research_agent | 20261008142204 | w41_seed_bounded_research_agent | SAME_NAME_DIFFERENT_VERSION | NAME_VERSION_CONFLICT | c3c932cc4702019c4dcb6b2f7cc6dfbc9ceabcc30e1dcc4da8f80d34ae9614d1 | PENDING |
| ZMR-046 | 20261008152000 | w42_workspace_rpc_authorization_parity | 20261008145424 | w42_workspace_rpc_authorization_parity | SAME_NAME_DIFFERENT_VERSION | NAME_VERSION_CONFLICT | 6ca4026f51e91fc0fc8d614f07bca8809bb29f7d74840ecf8981c593a332f257 | PENDING |
| ZMR-047 | 20261008152500 | w43_bounded_agent_execution_runtime | 20261008145525 | w43_bounded_agent_execution_runtime | SAME_NAME_DIFFERENT_VERSION | NAME_VERSION_CONFLICT | bf340fde73bb680fc1f24db1f36ea369843f93b2b63e5e97738854a4803ee45a | PENDING |
| ZMR-048 | 20261008160000 | w44_workspace_invitations | — | — | SOURCE_TUPLE_ABSENT_FROM_HOSTED_LEDGER | SOURCE_NOT_IN_LEDGER | 4be788b212346cd8e65cc8e5dfa731d6f81c3805e2af877ec96a9e3001f915ee | PENDING |
| ZMR-049 | 20261008170000 | w44_invitation_lifecycle | 20261008155642 | w44_invitation_lifecycle | SAME_NAME_DIFFERENT_VERSION | NAME_VERSION_CONFLICT | a9990920524af42840d9238cb718294efce7083d4852f280d04dac71aae15850 | PENDING |
| ZMR-050 | 20261008171000 | w45_workspace_member_management | 20261008160824 | w45_workspace_member_management | SAME_NAME_DIFFERENT_VERSION | NAME_VERSION_CONFLICT | 8036e1ac1c58c726b626a3b0aa5673a2eacef2531a85a53e55b37c2419d09199 | PENDING |
| ZMR-051 | 20261008172000 | w46_workspace_activity_audit | 20261008161055 | w46_workspace_activity_audit | SAME_NAME_DIFFERENT_VERSION | NAME_VERSION_CONFLICT | 599fc9746a3137e4cd67edf3cb4c3e0655197726b4794a4eb27dbfd2078d2c94 | PENDING |
| ZMR-052 | 20261008173000 | w46_activity_security_hardening | 20261008161617 | w46_activity_security_hardening | SAME_NAME_DIFFERENT_VERSION | NAME_VERSION_CONFLICT | 4a2c3d09fceb9fabfee0b2c00a555ecfb374e1e62bd790c4eeb45200c284fa15 | PENDING |
| ZMR-053 | 20261009120000 | w47_atomic_workspace_bootstrap | 20261009092613 | w47_atomic_workspace_bootstrap | SAME_NAME_DIFFERENT_VERSION | NAME_VERSION_CONFLICT | 31818b1aa9ad79eb84ede0757eafc760c5b391d88dad6da5611a414eaf5c05f6 | PENDING |
| ZMR-054 | 20261009140000 | w48_seed_research_agent_for_new_workspaces | 20261009093725 | w48_seed_research_agent_for_new_workspaces | SAME_NAME_DIFFERENT_VERSION | NAME_VERSION_CONFLICT | 95af01bd2bf92e317803f97da5b1167c3acc734ca255d8a21c147893384244a3 | PENDING |
| ZMR-055 | 20261009150000 | w49_agent_execution_recovery | 20261009171718 | w49_agent_execution_recovery | SAME_NAME_DIFFERENT_VERSION | NAME_VERSION_CONFLICT | f18e9c218aaea778a0f7687cd38ee5927a72a0d4a9269637ead58c07ecc16754 | PENDING |
| ZMR-056 | 20261009170000 | w50_expired_execution_lease_fence | 20261009171722 | w50_expired_execution_lease_fence | SAME_NAME_DIFFERENT_VERSION | NAME_VERSION_CONFLICT | 15103d5636cd52b4935eb400e380135e695f276d629c01c3c9734e7938013d38 | PENDING |
| ZMR-057 | 20261009183000 | w51_member_rpc_wrapper_permissions | 20261009185119 | w51_member_rpc_wrapper_permissions | SAME_NAME_DIFFERENT_VERSION | NAME_VERSION_CONFLICT | 714d22d5f5f37fcbdf311d3bf8850b9b89b45d8a19dc588ec3f3594c30a31a7f | PENDING |
| ZMR-058 | 20261010101000 | w52_foreign_key_indexes | 20261010101000 | w52_foreign_key_indexes | EXACT_VERSION_NAME_TUPLE | UNKNOWN | UNKNOWN — not emitted per-file in the review JSON | PENDING |
| ZMR-059 | 20261010101707 | w53_rls_initplan_optimization | 20261010101707 | w53_rls_initplan_optimization | EXACT_VERSION_NAME_TUPLE | UNKNOWN | UNKNOWN — not emitted per-file in the review JSON | PENDING |
| ZMR-060 | 20261010110505 | w54_workspace_policy_consolidation | 20261010110505 | w54_workspace_policy_consolidation | EXACT_VERSION_NAME_TUPLE | UNKNOWN | UNKNOWN — not emitted per-file in the review JSON | PENDING |
| ZMR-061 | 20261010110509 | w55_product_growth_signals | 20261010110509 | w55_product_growth_signals | EXACT_VERSION_NAME_TUPLE | UNKNOWN | UNKNOWN — not emitted per-file in the review JSON | PENDING |
| ZMR-062 | 20261010125620 | w56_agent_execution_duplicate_dispatch_guard | 20261010125620 | w56_agent_execution_duplicate_dispatch_guard | EXACT_VERSION_NAME_TUPLE | UNKNOWN | UNKNOWN — not emitted per-file in the review JSON | PENDING |
| ZMR-063 | 20261010164000 | w57_exact_agent_approval_binding | 20261010164000 | w57_exact_agent_approval_binding | EXACT_VERSION_NAME_TUPLE | UNKNOWN | UNKNOWN — not emitted per-file in the review JSON | PENDING |
| ZMR-064 | 20261010180000 | w58_retry_replay_and_consumption_tombstone | 20261010180000 | w58_retry_replay_and_consumption_tombstone | EXACT_VERSION_NAME_TUPLE | UNKNOWN | UNKNOWN — not emitted per-file in the review JSON | PENDING |
| ZMR-065 | 20261010181500 | w59_bind_expiry_into_approval_scope | 20261010181500 | w59_bind_expiry_into_approval_scope | EXACT_VERSION_NAME_TUPLE | UNKNOWN | UNKNOWN — not emitted per-file in the review JSON | PENDING |
| ZMR-066 | 20261010183000 | w60_start_idempotency_request_binding | 20261010183000 | w60_start_idempotency_request_binding | EXACT_VERSION_NAME_TUPLE | UNKNOWN | UNKNOWN — not emitted per-file in the review JSON | PENDING |
| ZMR-067 | 20261010190000 | w61_safe_approval_payload_shape | 20261010190000 | w61_safe_approval_payload_shape | EXACT_VERSION_NAME_TUPLE | UNKNOWN | UNKNOWN — not emitted per-file in the review JSON | PENDING |
| ZMR-068 | 20261011100000 | w62_redact_pii_field_names | 20261011100000 | w62_redact_pii_field_names | EXACT_VERSION_NAME_TUPLE | UNKNOWN | UNKNOWN — not emitted per-file in the review JSON | PENDING |
| ZMR-069 | 20261011130000 | w63_trusted_execution_completion | 20261011130000 | w63_trusted_execution_completion | EXACT_VERSION_NAME_TUPLE | UNKNOWN | UNKNOWN — not emitted per-file in the review JSON | PENDING |
| ZMR-070 | 20261011140000 | w64_read_only_research_completion | 20261011140000 | w64_read_only_research_completion | EXACT_VERSION_NAME_TUPLE | UNKNOWN | UNKNOWN — not emitted per-file in the review JSON | PENDING |
| ZMR-071 | 20261011150000 | w65_agent_execution_table_write_boundary | 20261011150000 | w65_agent_execution_table_write_boundary | EXACT_VERSION_NAME_TUPLE | UNKNOWN | UNKNOWN — not emitted per-file in the review JSON | PENDING |
| ZMR-072 | 20261011160000 | w66_service_role_table_privilege_hardening | — | — | SOURCE_TUPLE_ABSENT_FROM_HOSTED_LEDGER | SOURCE_NOT_IN_LEDGER | b33df4d724eac552ffacdfd8986c724581f846cd42dd25bb19f6edd8e9875b4c | PENDING |
| ZMR-073 | 20261011165000 | w67_legacy_research_rpc_privilege_hardening | — | — | SOURCE_TUPLE_ABSENT_FROM_HOSTED_LEDGER | SOURCE_NOT_IN_LEDGER | a0814297c305bdf787fb2d57537dde6192e3031e4dc70e87daafd8db72bbe012 | PENDING |
| ZMR-074 | 20261011170000 | w68_persistent_authority_budget_reservations | — | — | SOURCE_TUPLE_ABSENT_FROM_HOSTED_LEDGER | SOURCE_NOT_IN_LEDGER | 67259e0ce35f2f94d7f06554f2dd91fe23a4ade01536dcd55e044dc441ed53d7 | PENDING |
| ZMR-075 | 20261011180000 | w69_one_time_jit_dispatch_claim | — | — | SOURCE_TUPLE_ABSENT_FROM_HOSTED_LEDGER | SOURCE_NOT_IN_LEDGER | 239253ba998b54959f97f6403203f67ac3b04c5fc20636f2903f09f5746daee3 | PENDING |
| ZMR-076 | 20261011190000 | w70_durable_unknown_outcome_reconciliation | — | — | SOURCE_TUPLE_ABSENT_FROM_HOSTED_LEDGER | SOURCE_NOT_IN_LEDGER | ee683f868c335b991ae2a508ea3bb6cc6609f8361c2c130770ac66c0a0038448 | PENDING |
| ZMR-077 | 20261012070000 | w71_expired_external_execution_budget_recovery | — | — | SOURCE_TUPLE_ABSENT_FROM_HOSTED_LEDGER | SOURCE_NOT_IN_LEDGER | f2a5d8201c0b31c836e43fe4d3ee700497eb62016ad52332263d163ae3862e22 | PENDING |
| ZMR-078 | 20261012120000 | w73_trusted_system_mission_events | — | — | SOURCE_TUPLE_ABSENT_FROM_HOSTED_LEDGER | SOURCE_NOT_IN_LEDGER | 71238ba9471f9b7e2323c96e74e16ee273516e6d2b252e789241aa5f6b7ea857 | PENDING |
| ZMR-079 | 20261012130000 | w74_reconciliation_claim_freshness | — | — | SOURCE_TUPLE_ABSENT_FROM_HOSTED_LEDGER | SOURCE_NOT_IN_LEDGER | 2c21227b2368477e84fbfbbd0f9fdca5a5af0c8afc194a9612a6a72d0bd24632 | PENDING |
| ZMR-080 | 20261012140000 | w75_correlatable_provider_receipt | — | — | SOURCE_TUPLE_ABSENT_FROM_HOSTED_LEDGER | SOURCE_NOT_IN_LEDGER | efd571d3a8ee63f746f7a3ba4941c08c6ce1a8b898f53416d4d064fd31ed197d | PENDING |
| ZMR-081 | 20261012150000 | w76_guard_external_success_on_insert | — | — | SOURCE_TUPLE_ABSENT_FROM_HOSTED_LEDGER | SOURCE_NOT_IN_LEDGER | e831c1604b025b41713e2089b037e958355d1a72482467843db49d1bb35a55b5 | PENDING |
| ZMR-082 | 20261012160000 | w77_read_only_research_payload_bounds | — | — | SOURCE_TUPLE_ABSENT_FROM_HOSTED_LEDGER | SOURCE_NOT_IN_LEDGER | f5a0b2be93784966d734d420b3f124168f46b0b31c85cd18609fd59812682cd4 | PENDING |
| ZMR-083 | 20261012170000 | w78_bind_research_history_to_execution | — | — | SOURCE_TUPLE_ABSENT_FROM_HOSTED_LEDGER | SOURCE_NOT_IN_LEDGER | 5d93928d1b407016c73f1ac5f1ca737ccde313fd9fa85ef29b098e0fcad2032b | PENDING |
| ZMR-084 | 20261012180000 | w79_trusted_research_completion | — | — | SOURCE_TUPLE_ABSENT_FROM_HOSTED_LEDGER | SOURCE_NOT_IN_LEDGER | 5e20732f8d8b436b200002dbe6a1c02f62e1cbd8b47195b18a2d405141355d5b | PENDING |
| ZMR-085 | 20261013100000 | w80_fail_closed_workspace_role_checks | — | — | SOURCE_TUPLE_ABSENT_FROM_HOSTED_LEDGER | SOURCE_NOT_IN_LEDGER | 7e608c19e15ad53fcd79df8555ae1c51dd832c343263bc10b2d36dc229bc2ed7 | PENDING |
| ZMR-086 | 20261014110000 | w81_read_only_research_jit_claim | — | — | SOURCE_TUPLE_ABSENT_FROM_HOSTED_LEDGER | SOURCE_NOT_IN_LEDGER | 6164478666ac98c9d089f501804d16b35631d8ada68da1c846b547b32fc31d7f | PENDING |
| ZMR-087 | 20261014130000 | w82_ai_generation_reservation_identity | — | — | SOURCE_TUPLE_ABSENT_FROM_HOSTED_LEDGER | SOURCE_NOT_IN_LEDGER | 7aed50cb7c556da2154de9d1d87a3f992447c3a07007dba27a338de90ca0dda3 | PENDING |
| ZMR-088 | 20261015100000 | w83_workspace_invitation_privilege_correction | — | — | SOURCE_TUPLE_ABSENT_FROM_HOSTED_LEDGER | SOURCE_NOT_IN_LEDGER | 2848fa39b70d4818b5298a53c14506a38595ce406272eecbfc560a46d8b19cd5 | PENDING |
| ZMR-089 | 20261015110000 | w84_postgres_function_default_acl_hardening | — | — | SOURCE_TUPLE_ABSENT_FROM_HOSTED_LEDGER | SOURCE_NOT_IN_LEDGER | 62a1872cd2da4d3f4f8d461574a1948d4df03f0f8f9b09456f6d5b5de8faebf8 | PENDING |
| ZMR-090 | — | — | 20261007105825 | expose_anonymous_ai_guard_rpc | HOSTED_TUPLE_ABSENT_FROM_SOURCE | HOSTED_ONLY_SOURCE_UNKNOWN | UNKNOWN | PENDING |
| ZMR-091 | — | — | 20261005053351 | w35_plan_ai_allowances_5_50_300 | HOSTED_TUPLE_ABSENT_FROM_SOURCE | HOSTED_ONLY_SOURCE_UNKNOWN | UNKNOWN | PENDING |
| ZMR-092 | — | — | 20261008150359 | w44_workspace_invitations_and_activity | HOSTED_TUPLE_ABSENT_FROM_SOURCE | HOSTED_ONLY_SOURCE_UNKNOWN | UNKNOWN | PENDING |
| ZMR-093 | — | — | 20261008161103 | w46_invitation_activity_bindings | HOSTED_TUPLE_ABSENT_FROM_SOURCE | HOSTED_ONLY_SOURCE_UNKNOWN | UNKNOWN | PENDING |
| ZMR-094 | — | — | 20260921180227 | w4_harden_profile_trigger_search_path | HOSTED_TUPLE_ABSENT_FROM_SOURCE | HOSTED_ONLY_SOURCE_UNKNOWN | UNKNOWN | PENDING |
| ZMR-095 | — | — | 20260924171437 | w6_authoritative_mission_mutation_and_concurrency | HOSTED_TUPLE_ABSENT_FROM_SOURCE | HOSTED_ONLY_SOURCE_UNKNOWN | UNKNOWN | PENDING |

## Interpretation and unresolved evidence

- The hosted migration ledger stores only version/name metadata. Therefore a 46-row exact version/name tuple match is **not** proof that the SQL executed on the hosted project matches the checked-in SQL.
- Per-file source SHA-256 is present here for the 43 source tuples absent from the hosted exact-tuple set because the offline reviewer emitted those hashes. For the 46 metadata-match rows, this review artifact did not emit each file hash separately; they remain `UNKNOWN` per-row while the aggregate manifest above is pinned.
- Hosted SQL SHA-256 and a trusted per-deployment SQL evidence reference remain `UNKNOWN` for all hosted rows.
- `source_checkout_head_reported` is the local HEAD value recorded by the offline reviewer; it was not resolvable as a public `Nexo` commit during this continuation. Do not claim public commit verification on the basis of that value alone.
- The six hosted-only names and 22 version conflicts remain unresolved; do not infer historical equivalence from similar names or timestamps.

## Release gates

1. Recover source SQL bytes and trusted deployment provenance for all unresolved rows, including the 22 conflicts and six hosted-only names. Keep unresolved rows `UNKNOWN`.
2. Obtain independent database-owner review of direct `service_role` grants, missing budget/claim schema, missing trigger/index/constraints, legacy callable routines/`SECURITY DEFINER`, private-schema USAGE, and default EXECUTE ACLs.
3. Only after those gates, prepare a dependency-aware forward-only candidate and validate it in disposable PostgreSQL 17 with exact catalogue assertions, negative controls, repeat-apply/idempotency checks, and verified cleanup.
4. No W86 or other migration may be applied to hosted Development or Main/Production without a separate written authorization naming the exact target/change set/operator/window/recovery plan and confirmed restorable backup.

`hosted_write_authorized=false`. `TRUSTED_DISPATCH_ADAPTERS` remains empty/fail-closed. This ledger generation performed no hosted write, migration, deployment, secret change, or PR merge.
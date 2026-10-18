"""Static syntax guard for the isolated W86 owner-path test helper in CI."""
from __future__ import annotations

import re
import subprocess
import textwrap
import unittest
from pathlib import Path


WORKFLOW = (
    Path(__file__).resolve().parents[1]
    / ".github"
    / "workflows"
    / "zavqera-w80-isolated-pgtap.yml"
)
START_MARKER = "          # Exercise both ways to obtain table-owner authority (SET ROLE and INHERIT)."
EXPECTED_FINAL_GATE = 'if [ "${regression_status}" -ne 0 ] || [ "${later_status}" -ne 0 ] || [ "${w84_status}" -ne 0 ] || [ "${w85_status}" -ne 0 ] || [ "${w86_status}" -ne 0 ] || [ "${query_pack_status}" -ne 0 ] || [ "${w86_authenticated_parent_guard_status}" -ne 0 ] || [ "${anon_authenticated_guard_status:-1}" -ne 0 ] || [ "${untrusted_parent_acl_guard_status:-1}" -ne 0 ] || [ "${owner_path_guard_status}" -ne 0 ] || [ "${untrusted_owner_guard_status:-1}" -ne 0 ] || [ "${mixed_path_no_mutation_status:-1}" -ne 0 ]; then exit 1; fi'
END_MARKER = EXPECTED_FINAL_GATE


class W86OwnerPathWorkflowSyntaxTests(unittest.TestCase):
    def test_anon_to_authenticated_guard_covers_inherit_set_and_mixed_paths(self):
        workflow = WORKFLOW.read_text(encoding="utf-8")
        start_marker = "          # Negative control: W86 must reject any anon-to-authenticated path before it grants SELECT."
        end_marker = "          # Exercise both ways to obtain table-owner authority (SET ROLE and INHERIT)."
        self.assertIn(start_marker, workflow)
        self.assertIn(end_marker, workflow)
        start = workflow.index(start_marker)
        end = workflow.index(end_marker, start)
        helper = textwrap.dedent(workflow[start:end])
        result = subprocess.run(
            ["bash", "-n"], input=helper, text=True, capture_output=True, check=False
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('run_anon_authenticated_parent_negative_control inherit "INHERIT TRUE, SET FALSE"', helper)
        self.assertIn('run_anon_authenticated_parent_negative_control set "INHERIT FALSE, SET TRUE"', helper)
        self.assertIn('run_anon_authenticated_parent_negative_control mixed "MIXED SET ROLE THEN INHERIT"', helper)
        self.assertIn("W86_ANON_AUTH_${kind^^}_REACHABILITY_PASS", helper)
        self.assertIn("W86_ANON_AUTH_${kind^^}_NO_MUTATION_PASS", helper)
        self.assertIn("W86 refused: anon can reach authenticated via a parent role path", helper)
        self.assertIn('echo "expected_w86_pgtap_assertions=25"', workflow)
        self.assertIn("REVOKE authenticated FROM anon", helper)
        self.assertIn(r"DO \$cleanup_anon_auth\$", workflow)
        self.assertIn("anon_authenticated_guard_status=1", helper)
        self.assertIn('[ "${anon_authenticated_guard_status:-1}" -ne 0 ]', workflow)


    def test_untrusted_roles_cannot_own_or_reach_execution_table_owner(self):
        workflow = WORKFLOW.read_text(encoding="utf-8")
        start_marker = "          # Negative controls: neither untrusted API role may own the execution table."
        end_marker = "          # Exercise both ways to obtain table-owner authority (SET ROLE and INHERIT)."
        self.assertIn(start_marker, workflow)
        self.assertIn(end_marker, workflow)
        start = workflow.index(start_marker)
        end = workflow.index(end_marker, start)
        helper = textwrap.dedent(workflow[start:end])
        result = subprocess.run(
            ["bash", "-n"], input=helper, text=True, capture_output=True, check=False
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("run_untrusted_owner_negative_control anon", helper)
        self.assertIn("run_untrusted_owner_negative_control authenticated", helper)
        self.assertIn("ALTER TABLE public.agent_executions OWNER TO ${owner_role}", helper)
        self.assertIn("W86 refused: anon/authenticated can own or reach owner of public.agent_executions", helper)
        self.assertIn('before_state="$(docker exec', helper)
        self.assertIn('[ "${before_state}" != "${after_state}" ]', helper)
        self.assertIn("REVOKE CREATE ON SCHEMA public FROM ${owner_role}", helper)
        self.assertIn("W86_AFTER_UNTRUSTED_OWNER_${owner_role^^}_CLEANUP", helper)
        self.assertIn("GRANT SELECT (%I) ON TABLE public.agent_executions TO %I", helper)
        self.assertIn("supabase/tests/w86_agent_executions_acl_correction.sql 25", helper)
        self.assertIn("run_untrusted_owner_mixed_path_negative_control", helper)
        self.assertIn("GRANT ${intermediate_role} TO authenticated WITH INHERIT FALSE, SET TRUE;", helper)
        self.assertIn("GRANT ${owner_role} TO ${intermediate_role} WITH INHERIT TRUE, SET FALSE;", helper)
        self.assertIn("W86_UNTRUSTED_OWNER_MIXED_PATH_REACHABILITY_PASS", helper)
        self.assertIn("W86_UNTRUSTED_OWNER_MIXED_PATH_NO_MUTATION_PASS", helper)
        self.assertIn("REVOKE ${intermediate_role} FROM authenticated", helper)
        self.assertIn("W86_AFTER_UNTRUSTED_OWNER_MIXED_PATH_CLEANUP", helper)
        self.assertIn("untrusted_owner_guard_status=1", workflow)
        self.assertIn('[ "${untrusted_owner_guard_status:-1}" -ne 0 ]', workflow)
        self.assertIn('echo "expected_w86_pgtap_assertions=25"', workflow)

    def test_untrusted_api_role_parent_acl_guard_covers_all_reachability_modes(self):
        workflow = WORKFLOW.read_text(encoding="utf-8")
        start_marker = "          # Negative control: W86 must refuse reachable parent-role table/column ACLs for anon/authenticated before any mutation."
        end_marker = "          # Exercise both ways to obtain table-owner authority (SET ROLE and INHERIT)."
        self.assertIn(start_marker, workflow)
        self.assertIn(end_marker, workflow)
        start = workflow.index(start_marker)
        end = workflow.index(end_marker, start)
        helper = textwrap.dedent(workflow[start:end])
        result = subprocess.run(
            ["bash", "-n"], input=helper, text=True, capture_output=True, check=False
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        for call in (
            "run_untrusted_parent_acl_negative_control anon inherit table",
            "run_untrusted_parent_acl_negative_control anon set table",
            "run_untrusted_parent_acl_negative_control anon mixed table",
            "run_untrusted_parent_acl_negative_control authenticated inherit table",
            "run_untrusted_parent_acl_negative_control authenticated set table",
            "run_untrusted_parent_acl_negative_control authenticated mixed table",
            "run_untrusted_parent_acl_negative_control anon inherit column",
            "run_untrusted_parent_acl_negative_control anon set column",
            "run_untrusted_parent_acl_negative_control anon mixed column",
            "run_untrusted_parent_acl_negative_control authenticated inherit column",
            "run_untrusted_parent_acl_negative_control authenticated set column",
            "run_untrusted_parent_acl_negative_control authenticated mixed column",
        ):
            self.assertIn(call, helper)
        self.assertIn("W86_UNTRUSTED_PARENT_ACL_${root_role^^}_${kind^^}_${acl_kind^^}_NO_MUTATION_PASS", helper)
        self.assertIn("W86 refused: anon/authenticated can obtain agent_executions privileges via parent roles", helper)
        self.assertIn("untrusted_parent_acl_guard_status=1", helper)
        self.assertIn('[ "${untrusted_parent_acl_guard_status:-1}" -ne 0 ]', workflow)
        self.assertIn("supabase/tests/w86_agent_executions_acl_correction.sql 25", helper)

    def test_owner_path_helper_is_valid_bash_and_covers_both_membership_modes(self):
        workflow = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn(START_MARKER, workflow, "W86 owner-path test helper is missing")
        self.assertIn(END_MARKER, workflow, "W80 final gate is missing")
        self.assertIn(EXPECTED_FINAL_GATE, workflow, "W80 final gate must account for every required negative-control status")
        self.assertIn('mixed_path_no_mutation_status="${mixed_no_mutation_status}"', workflow)
        self.assertIn('echo "mixed_path_no_mutation_status=${mixed_path_no_mutation_status}" >> "${RUNNER_TEMP}/W80_EVIDENCE.txt"', workflow)
        self.assertIn('[ "${mixed_path_no_mutation_status:-1}" -ne 0 ]', workflow)
        start = workflow.index(START_MARKER)
        end = workflow.index(END_MARKER, start)
        helper = textwrap.dedent(workflow[start:end])

        result = subprocess.run(
            ["bash", "-n"],
            input=helper,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('run_owner_path_negative_control role "INHERIT FALSE, SET TRUE"', helper)
        self.assertIn('run_owner_path_negative_control inherit "INHERIT TRUE, SET FALSE"', helper)
        self.assertIn("GRANT CREATE ON SCHEMA public TO ${role_name}", helper)
        self.assertIn("REVOKE CREATE ON SCHEMA public FROM ${role_name}", helper)
        self.assertIn("W86_OWNER_${kind^^}_NO_MUTATION_PASS", helper)
        self.assertIn("owner_path_guard_status=1", helper)

    def test_owner_guard_covers_mixed_set_role_then_inherit_path(self):
        workflow = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn('run_owner_path_negative_control mixed "MIXED SET ROLE THEN INHERIT"', workflow)
        self.assertIn("GRANT w86_acl_owner_mixed_intermediate_probe TO service_role WITH INHERIT FALSE, SET TRUE;", workflow)
        self.assertIn("GRANT ${role_name} TO w86_acl_owner_mixed_intermediate_probe WITH INHERIT TRUE, SET FALSE;", workflow)
        self.assertIn("W86_OWNER_MIXED_PATH_REACHABILITY_PASS", workflow)
        self.assertIn("pg_has_role('service_role', 'w86_acl_owner_mixed_intermediate_probe', 'SET')", workflow)
        self.assertIn("has_table_privilege('service_role', 'public.agent_executions', 'DELETE')", workflow)
        self.assertIn("REVOKE w86_acl_owner_mixed_intermediate_probe FROM service_role", workflow)
        self.assertIn("REVOKE ALL PRIVILEGES ON TABLE public.agent_executions FROM service_role", workflow)
        self.assertIn("w86_owner_mixed_path_reachability_exit_code", workflow)
        self.assertIn("W86_OWNER_MIXED_GUARD_REACHABILITY_CHECK.txt", workflow)

    def test_final_gate_fails_closed_on_missing_or_failed_mixed_path_check(self):
        workflow = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn(EXPECTED_FINAL_GATE, workflow)
        self.assertIn('mixed_path_no_mutation_status="${mixed_no_mutation_status}"', workflow)
        self.assertIn('echo "mixed_path_no_mutation_status=${mixed_path_no_mutation_status}" >> "${RUNNER_TEMP}/W80_EVIDENCE.txt"', workflow)
        self.assertIn('[ "${mixed_path_no_mutation_status:-1}" -ne 0 ]', workflow)

    def test_w86_read_only_acl_probe_covers_mixed_set_role_then_inherit_path(self):
        workflow = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn("CREATE ROLE w86_acl_probe_grandparent NOLOGIN", workflow)
        self.assertIn("GRANT w86_acl_probe_grandparent TO w86_acl_probe_parent WITH INHERIT TRUE, SET FALSE", workflow)
        self.assertIn("reachable_via_membership_options", workflow)
        self.assertIn("W86_ACL_PROVENANCE_MIXED_PATH_ACL_PASS", workflow)
        self.assertIn("W86_MIXED_PATH_GUARD_PASS", workflow)
        self.assertIn("GRANT DELETE ON TABLE public.agent_executions TO service_role", workflow)
        self.assertIn("W86_MIXED_PATH_NO_MUTATION_PASS", workflow)
        self.assertIn("w86_mixed_path_no_mutation_exit_code", workflow)

    def test_pgtap_contract_covers_explicit_column_acl_cleanup(self):
        root = Path(__file__).resolve().parents[1]
        sql_path = root / "supabase" / "tests" / "w86_agent_executions_acl_correction.sql"
        sql = sql_path.read_text(encoding="utf-8")
        workflow = WORKFLOW.read_text(encoding="utf-8")

        plans = re.findall(r"(?mi)^\s*select\s+plan\((\d+)\);", sql)
        assertions = re.findall(r"(?mi)^\s*select\s+ok\s*\(", sql)
        self.assertEqual(["25"], plans)
        self.assertEqual(25, len(assertions), "pgTAP plan must match the actual assertion count")
        self.assertIn("no stored column ACLs remain for PUBLIC, anon, authenticated, or service_role", sql)
        self.assertIn(
            "acl.grantee in (\n       0,\n       'anon'::regrole,\n       'authenticated'::regrole,\n       'service_role'::regrole",
            sql,
        )

        # The disposable drift fixture must seed direct API-role column grants
        # so the runtime pgTAP assertion proves W86 actually removes them.
        self.assertIn("'grant select (%I) on table public.agent_executions to anon'", workflow)
        self.assertIn("'grant update (%I) on table public.agent_executions to authenticated'", workflow)
        self.assertIn("acl.grantee = 'anon'::regrole", workflow)
        self.assertIn("acl.grantee = 'authenticated'::regrole", workflow)
        self.assertIn('echo "expected_w86_pgtap_assertions=25"', workflow)
        invocations = re.findall(
            r"run_pgtap[^\n]*w86_agent_executions_acl_correction\.sql\s+(\d+)",
            workflow,
        )
        self.assertTrue(invocations, "workflow must invoke the W86 pgTAP test")
        self.assertEqual(
            {"25"},
            set(invocations),
            "every W86 workflow invocation must expect 25 assertions",
        )


if __name__ == "__main__":
    unittest.main()

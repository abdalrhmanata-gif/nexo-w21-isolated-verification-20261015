"""Static syntax guard for the isolated W86 owner-path test helper in CI."""
from __future__ import annotations

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
END_MARKER = '          if [ "${regression_status}" -ne 0 ] || [ "${later_status}" -ne 0 ] || [ "${w84_status}" -ne 0 ] || [ "${w85_status}" -ne 0 ] || [ "${w86_status}" -ne 0 ] || [ "${query_pack_status}" -ne 0 ] || [ "${w86_authenticated_parent_guard_status}" -ne 0 ] || [ "${owner_path_guard_status}" -ne 0 ]; then exit 1; fi'


class W86OwnerPathWorkflowSyntaxTests(unittest.TestCase):
    def test_owner_path_helper_is_valid_bash_and_covers_both_membership_modes(self):
        workflow = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn(START_MARKER, workflow, "W86 owner-path test helper is missing")
        self.assertIn(END_MARKER, workflow, "W80 final gate is missing")
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

    def test_w86_read_only_acl_probe_covers_mixed_set_role_then_inherit_path(self):
        workflow = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn("CREATE ROLE w86_acl_probe_grandparent NOLOGIN", workflow)
        self.assertIn("GRANT w86_acl_probe_grandparent TO w86_acl_probe_parent WITH INHERIT TRUE, SET FALSE", workflow)
        self.assertIn("reachable_via_membership_options", workflow)
        self.assertIn("W86_ACL_PROVENANCE_MIXED_PATH_ACL_PASS", workflow)
        self.assertIn("W86_MIXED_PATH_GUARD_PASS", workflow)


if __name__ == "__main__":
    unittest.main()

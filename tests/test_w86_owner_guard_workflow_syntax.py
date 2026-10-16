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
        self.assertIn("W86_OWNER_${kind^^}_NO_MUTATION_PASS", helper)
        self.assertIn("owner_path_guard_status=1", helper)


if __name__ == "__main__":
    unittest.main()

import unittest
from pathlib import Path

from tools.classify_launch_checklist_changes import is_checklist_only


WORKFLOW = Path(__file__).resolve().parents[1] / ".github" / "workflows" / "flutter.yml"


class LaunchChecklistWorkflowClassificationTests(unittest.TestCase):
    def test_checklist_validator_tests_and_handoff_use_fast_path(self):
        self.assertTrue(
            is_checklist_only(
                [
                    "docs/ZAVQERA_LAUNCH_READINESS_CHECKLIST_2026-10-18.md",
                    "tools/validate_launch_checklist.py",
                    "tests/test_launch_checklist.py",
                    "docs/ZAVQERA_CONTINUATION_HANDOFF_2026-10-15.md",
                ]
            )
        )

    def test_application_or_unknown_paths_keep_full_validation(self):
        for changed in (
            "apps/web/app/page.tsx",
            "pubspec.yaml",
            "supabase/migrations/example.sql",
            "tool/verify_project.sh",
            "docs/another-document.md",
        ):
            with self.subTest(changed=changed):
                self.assertFalse(is_checklist_only(["tools/validate_launch_checklist.py", changed]))

    def test_empty_change_set_fails_closed_to_full_validation(self):
        self.assertFalse(is_checklist_only([]))

    def test_windows_separators_are_normalized(self):
        self.assertTrue(is_checklist_only([r"tools\validate_launch_checklist.py"]))

    def test_embedded_newline_cannot_hide_an_unrecognized_path(self):
        self.assertFalse(
            is_checklist_only(
                ["tools/validate_launch_checklist.py\napps/web/app/page.tsx"]
            )
        )

    def test_existing_required_workflow_runs_fast_checks_and_keeps_full_path(self):
        workflow = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn('branches: ["**"]', workflow)
        self.assertRegex(workflow, r"(?m)^\s+pull_request:\s*$")
        self.assertIn("classify-changes:", workflow)
        self.assertIn("needs: classify-changes", workflow)
        self.assertIn("if: always()", workflow)
        self.assertIn("python3 tools/validate_launch_checklist.py", workflow)
        self.assertIn("python3 -m unittest tests/test_launch_checklist.py tests/test_launch_checklist_workflow.py -v", workflow)
        self.assertIn('git diff --check "$DIFF_BASE...$DIFF_HEAD"', workflow)
        for full_validation_step in (
            "Setup Flutter",
            "Verify ZAVQERA MVP",
            "Install web dependencies",
            "Run controlled-adapter tests",
            "Run web tests",
            "Typecheck web app",
        ):
            step = workflow.split(f"- name: {full_validation_step}", 1)[1].split("\n      - name:", 1)[0]
            self.assertIn("needs.classify-changes.outputs.checklist_only != 'true'", step)


if __name__ == "__main__":
    unittest.main()

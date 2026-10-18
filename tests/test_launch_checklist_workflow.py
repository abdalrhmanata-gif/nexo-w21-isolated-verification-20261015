import unittest
from pathlib import Path

from tools.classify_launch_checklist_changes import is_checklist_only, parse_change_records


WORKFLOW = Path(__file__).resolve().parents[1] / ".github" / "workflows" / "flutter.yml"


def change(status, path, old_mode="100644", new_mode="100644"):
    return (status, old_mode, new_mode, path)


def raw_record(status, path, old_mode="100644", new_mode="100644"):
    return f":{old_mode} {new_mode} {'a' * 40} {'b' * 40} {status}\0{path}\0".encode()


class LaunchChecklistWorkflowClassificationTests(unittest.TestCase):
    def test_checklist_validator_tests_and_handoff_use_fast_path(self):
        self.assertTrue(
            is_checklist_only(
                [
                    change("M", "docs/ZAVQERA_LAUNCH_READINESS_CHECKLIST_2026-10-18.md"),
                    change("M", "tools/validate_launch_checklist.py"),
                    change("M", "tests/test_launch_checklist.py"),
                    change("M", "docs/ZAVQERA_CONTINUATION_HANDOFF_2026-10-15.md"),
                ]
            )
        )

    def test_application_or_unknown_paths_keep_full_validation(self):
        for changed in (
            "apps/web/app/page.tsx",
            "apps/web/package-lock.json",
            "pubspec.lock",
            "netlify.toml",
            "supabase/tests/w80_invitation_helper_privileges.sql",
            "pubspec.yaml",
            "supabase/migrations/example.sql",
            "apps/web/lib/mission-authority/trusted-worker-http.mjs",
            ".github/workflows/zavqera-w21-e2e.yml",
            "tool/verify_project.sh",
            "docs/another-document.md",
        ):
            with self.subTest(changed=changed):
                self.assertFalse(is_checklist_only([change("M", "tools/validate_launch_checklist.py"), change("M", changed)]))

    def test_empty_change_set_fails_closed_to_full_validation(self):
        self.assertFalse(is_checklist_only([]))

    def test_added_exact_allowlisted_checklist_file_is_safe(self):
        self.assertTrue(is_checklist_only([change("A", "tests/test_launch_checklist.py", "000000")]))

    def test_deletions_and_renames_use_full_validation(self):
        self.assertFalse(is_checklist_only([change("D", "tests/test_launch_checklist.py", new_mode="000000")]))
        self.assertFalse(
            is_checklist_only(
                [
                    change("D", "docs/ZAVQERA_LAUNCH_READINESS_CHECKLIST_2026-10-18.md", new_mode="000000"),
                    change("A", "docs/ZAVQERA_CONTINUATION_HANDOFF_2026-10-15.md", "000000"),
                ]
            )
        )

    def test_workflow_edits_case_variants_and_unrecognized_status_use_full_validation(self):
        self.assertFalse(is_checklist_only([change("M", ".github/workflows/flutter.yml")]))
        self.assertFalse(is_checklist_only([change("M", "tools/classify_launch_checklist_changes.py")]))
        self.assertFalse(is_checklist_only([change("M", "Tools/validate_launch_checklist.py")]))
        self.assertFalse(is_checklist_only([change("R100", "tools/validate_launch_checklist.py")]))

    def test_windows_separators_are_normalized(self):
        self.assertTrue(is_checklist_only([change("M", r"tools\validate_launch_checklist.py")]))

    def test_embedded_newline_cannot_hide_an_unrecognized_path(self):
        self.assertFalse(
            is_checklist_only(
                [change("M", "tools/validate_launch_checklist.py\napps/web/app/page.tsx")]
            )
        )

    def test_missing_or_malformed_path_data_fails_closed(self):
        self.assertFalse(is_checklist_only(parse_change_records(b"")))
        record = raw_record("M", "tools/validate_launch_checklist.py")
        self.assertFalse(is_checklist_only(parse_change_records(record[:-1])))
        self.assertFalse(is_checklist_only(parse_change_records(record + b"A\0")))
        self.assertFalse(is_checklist_only(parse_change_records(raw_record("M", "bad-\xff-path"))))
        self.assertFalse(is_checklist_only(parse_change_records(b":invalid 100644 bad hash M\0tools/validate_launch_checklist.py\0")))

    def test_symlink_or_executable_mode_changes_use_full_validation(self):
        self.assertFalse(is_checklist_only([change("M", "tools/validate_launch_checklist.py", new_mode="120000")]))
        self.assertFalse(is_checklist_only([change("M", "tests/test_launch_checklist.py", new_mode="100755")]))

    def test_existing_required_workflow_runs_fast_checks_and_keeps_full_path(self):
        workflow = WORKFLOW.read_text(encoding="utf-8")
        push_trigger = workflow.split("\non:", 1)[1].split("\npermissions:", 1)[0]
        self.assertRegex(
            push_trigger,
            r'(?ms)^  push:\s*\n    branches: \["\*\*", "!codex/launch-readiness-gates-20261018"\]\s*\n  pull_request:\s*$'
        )
        self.assertIn("classify-changes:", workflow)
        self.assertIn("needs: classify-changes", workflow)
        self.assertIn("if: always()", workflow)
        self.assertIn("set -euo pipefail", workflow)
        self.assertIn("git diff --raw --no-renames -z", workflow)
        self.assertIn("python3 tools/validate_launch_checklist.py", workflow)
        self.assertIn("python3 -m unittest tests/test_launch_checklist.py tests/test_launch_checklist_workflow.py -v", workflow)
        self.assertIn('git diff --check "$DIFF_BASE...$DIFF_HEAD"', workflow)
        fast_step = workflow.split("- name: Run launch checklist validator and regression tests", 1)[1].split("\n      - name:", 1)[0]
        self.assertIn("set -euo pipefail", fast_step)
        self.assertLess(fast_step.index("python3 tools/validate_launch_checklist.py"), fast_step.index("python3 -m unittest"))
        self.assertLess(fast_step.index("python3 -m unittest"), fast_step.index("git diff --check"))
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

    def test_launch_branch_push_is_excluded_but_its_pr_keeps_full_verification(self):
        workflow = WORKFLOW.read_text(encoding="utf-8")
        triggers = workflow.split("\non:", 1)[1].split("\npermissions:", 1)[0]
        self.assertIn('branches: ["**", "!codex/launch-readiness-gates-20261018"]', triggers)
        self.assertRegex(triggers, r"(?m)^  pull_request:\s*$")
        self.assertNotIn("branches-ignore", triggers)
        self.assertNotRegex(triggers, r"(?m)^\s+types:\s*\[.*\]\s*$")

        verify = workflow.split("\n  verify:", 1)[1].split("\njobs:", 1)[0]
        self.assertIn("needs: classify-changes", verify)
        self.assertIn("if: always()", verify)
        self.assertIn("needs.classify-changes.result != 'success' || needs.classify-changes.outputs.checklist_only != 'true'", verify)


if __name__ == "__main__":
    unittest.main()

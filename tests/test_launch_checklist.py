import unittest
from pathlib import Path

from tools.validate_launch_checklist import validate_checklist


CHECKLIST = Path(__file__).resolve().parents[1] / "docs" / "ZAVQERA_LAUNCH_READINESS_CHECKLIST_2026-10-18.md"


class LaunchChecklistValidatorTests(unittest.TestCase):
    def setUp(self):
        self.text = CHECKLIST.read_text(encoding="utf-8")

    def test_current_checklist_has_complete_gate_records(self):
        self.assertEqual(validate_checklist(self.text), [])

    def test_rejects_unknown_status(self):
        mutated = self.text.replace("**Status:** BLOCKED", "**Status:** MAYBE", 1)
        self.assertTrue(any("invalid status" in error for error in validate_checklist(mutated)))

    def test_rejects_missing_full_source_sha(self):
        mutated = self.text.replace(
            "**Evidence / exact source SHA:** W86/W80 run `39136888615`, SHA `e123ead90684b64a9809ad6d4ba7b8ddcb155155`, W86 25/25 and W80 49/49, artifact `12140396685` (disposable PostgreSQL 17.11 only). Recovery smoke run `39139497594`, SHA `dcffaf1a138b1ddfee596fbdc0c76081272ce985`, artifact `12141246974`. Current review checkout HEAD `61208ffcdb3a6154aa616cdd152b78221bbeaca6` has uncommitted changes; it is not a tested release candidate.",
            "**Evidence / exact source SHA:** Old test result with no resolvable source commit.",
            1,
        )
        self.assertTrue(any("full 40-character source SHA" in error for error in validate_checklist(mutated)))

    def test_rejects_missing_owner_or_reviewer(self):
        mutated = self.text.replace("Application security owner / independent security reviewer", "Application security owner", 1)
        self.assertTrue(any("owner and independent reviewer" in error for error in validate_checklist(mutated)))

    def test_rejects_missing_stop_condition(self):
        mutated = self.text.replace("**Stop condition:** Candidate SHA is missing, dirty, differs from CI evidence, or an artifact cannot be matched to it.", "**Stop condition:**", 1)
        self.assertTrue(any("Gate A: missing Stop condition" in error for error in validate_checklist(mutated)))

    def test_rejects_duplicate_gate(self):
        duplicate = self.text.split("### Gate B", 1)[0] + self.text[self.text.index("### Gate A"):self.text.index("### Gate B")] + "### Gate B" + self.text.split("### Gate B", 1)[1]
        self.assertTrue(any("duplicate Gate A" in error for error in validate_checklist(duplicate)))

    def test_requires_explicit_release_decision(self):
        mutated = self.text.replace("## Release decision: NO-GO", "## Release decision: MAYBE", 1)
        errors = validate_checklist(mutated)
        self.assertTrue(any("release decision must be explicitly GO or NO-GO" in error for error in errors))

    def test_na_requires_owner_approval(self):
        mutated = self.text.replace("**Status:** BLOCKED", "**Status:** N/A", 1)
        errors = validate_checklist(mutated)
        self.assertTrue(any("N/A lacks explicit owner/reviewer approval" in error for error in errors))

    def test_pass_cannot_reuse_evidence_from_an_older_sha(self):
        candidate = "f" * 40
        mutated = self.text.replace(
            "**Release candidate SHA:** NONE (current checkout is dirty; no release candidate selected)",
            f"**Release candidate SHA:** {candidate}",
            1,
        ).replace("**Status:** BLOCKED", "**Status:** PASS", 1)
        errors = validate_checklist(mutated)
        self.assertTrue(any("does not identify the current candidate SHA" in error for error in errors))

    def test_disposable_test_evidence_cannot_satisfy_hosted_gate(self):
        candidate = "e123ead90684b64a9809ad6d4ba7b8ddcb155155"
        mutated = self.text.replace(
            "**Release candidate SHA:** NONE (current checkout is dirty; no release candidate selected)",
            f"**Release candidate SHA:** {candidate}",
            1,
        )
        gate_d_start = mutated.index("### Gate D")
        gate_e_start = mutated.index("### Gate E")
        gate_d = mutated[gate_d_start:gate_e_start].replace("**Status:** BLOCKED", "**Status:** PASS", 1)
        gate_d = gate_d.replace(
            "No fresh 13-query hosted capture is recorded here.",
            "No fresh 13-query hosted capture is recorded here. scope=exact_candidate_ci",
            1,
        )
        mutated = mutated[:gate_d_start] + gate_d + mutated[gate_e_start:]
        errors = validate_checklist(mutated)
        self.assertTrue(any("does not claim required scope=HOSTED_READ_ONLY_CAPTURE" in error for error in errors))

    def test_go_requires_all_mandatory_gates_to_pass(self):
        mutated = self.text.replace("## Release decision: NO-GO", "## Release decision: GO", 1)
        self.assertTrue(any("GO requires every mandatory gate" in error for error in validate_checklist(mutated)))

    def test_missing_required_scope_fails(self):
        mutated = self.text.replace("**Required evidence scope:** EXACT_CANDIDATE_CI", "**Required evidence scope:** LOCAL_TESTS_ONLY", 1)
        self.assertTrue(any("invalid required evidence scope" in error for error in validate_checklist(mutated)))

    def test_pass_and_na_require_owner_and_independent_review_claims(self):
        candidate = "e123ead90684b64a9809ad6d4ba7b8ddcb155155"
        for status, approval_record in (
            ("PASS", "**Accountable owner / independent reviewer:** Release owner / independent release reviewer."),
            ("N/A", "**Accountable owner / independent reviewer:** N/A approved by Release Owner; independent review by Security Reviewer."),
        ):
            with self.subTest(status=status):
                mutated = self.text.replace(
                    "**Release candidate SHA:** NONE (current checkout is dirty; no release candidate selected)",
                    f"**Release candidate SHA:** {candidate}",
                    1,
                )
                start, end = mutated.index("### Gate A"), mutated.index("### Gate B")
                gate_a = mutated[start:end].replace("**Status:** BLOCKED", f"**Status:** {status}", 1)
                gate_a = gate_a.replace(
                    "Current review checkout HEAD `61208ffcdb3a6154aa616cdd152b78221bbeaca6` has uncommitted changes; it is not a tested release candidate.",
                    "Current review checkout is not release proof. scope=exact_candidate_ci",
                    1,
                )
                gate_a = gate_a.replace(
                    "**Accountable owner / independent reviewer:** Release owner / independent release reviewer (named assignment pending).",
                    approval_record,
                    1,
                )
                mutated = mutated[:start] + gate_a + mutated[end:]
                errors = validate_checklist(mutated)
                self.assertTrue(any("lacks independent_review=pass" in error for error in errors), errors)
                self.assertTrue(any("lacks owner_approval=pass" in error for error in errors), errors)

    def test_blank_exit_condition_and_closure_action_fail(self):
        for field in ("Exit condition", "Closure action", "Required evidence scope"):
            with self.subTest(field=field):
                line = next(line for line in self.text.splitlines() if line.startswith(f"- **{field}:**"))
                mutated = self.text.replace(line, f"- **{field}:**", 1)
                errors = validate_checklist(mutated)
                self.assertTrue(any(f"Gate A: missing {field}" in error for error in errors), errors)


if __name__ == "__main__":
    unittest.main()

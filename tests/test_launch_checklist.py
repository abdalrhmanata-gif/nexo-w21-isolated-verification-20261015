import re
import unittest
from pathlib import Path

from tools.validate_launch_checklist import validate_checklist


CHECKLIST = Path(__file__).resolve().parents[1] / "docs" / "ZAVQERA_LAUNCH_READINESS_CHECKLIST_2026-10-18.md"


def select_candidate(text, candidate):
    return re.sub(
        r"(?m)^\*\*Release candidate SHA:\*\*.*$",
        f"**Release candidate SHA:** {candidate}",
        text,
        count=1,
    )


def replace_gate_field(text, gate_id, field, value):
    start = text.index(f"### Gate {gate_id} —")
    end = text.find("\n### Gate ", start + 1)
    if end == -1:
        end = len(text)
    gate = text[start:end]
    pattern = re.compile(rf"(?m)^- \*\*{re.escape(field)}:\*\*.*$")
    replaced, count = pattern.subn(f"- **{field}:** {value}", gate, count=1)
    if count != 1:
        raise AssertionError(f"Gate {gate_id} must contain exactly one {field} field")
    return text[:start] + replaced + text[end:]


class LaunchChecklistValidatorTests(unittest.TestCase):
    def setUp(self):
        self.text = CHECKLIST.read_text(encoding="utf-8")

    def test_current_checklist_has_complete_gate_records(self):
        self.assertEqual(validate_checklist(self.text), [])

    def test_rejects_unknown_status(self):
        mutated = self.text.replace("**Status:** BLOCKED", "**Status:** MAYBE", 1)
        self.assertTrue(any("invalid status" in error for error in validate_checklist(mutated)))

    def test_rejects_missing_full_source_sha(self):
        mutated = replace_gate_field(
            self.text, "A", "Evidence / exact source SHA", "Old test result with no resolvable source commit."
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
        self.assertTrue(any("exactly one explicit GO or NO-GO" in error for error in errors))

    def test_na_requires_owner_approval(self):
        mutated = self.text.replace("**Status:** BLOCKED", "**Status:** N/A", 1)
        errors = validate_checklist(mutated)
        self.assertTrue(any("evidence lacks owner_approval=PASS by an accountable person/team" in error for error in errors))

    def test_pass_cannot_reuse_evidence_from_an_older_sha(self):
        candidate = "f" * 40
        mutated = select_candidate(self.text, candidate).replace("**Status:** BLOCKED", "**Status:** PASS", 1)
        errors = validate_checklist(mutated)
        self.assertTrue(any("must bind candidate_sha" in error for error in errors))

    def test_tested_sha_must_equal_candidate_even_when_candidate_is_also_mentioned(self):
        candidate = "f" * 40
        mutated = select_candidate(self.text, candidate)
        start, end = mutated.index("### Gate A"), mutated.index("### Gate B")
        gate_a = mutated[start:end].replace("**Status:** BLOCKED", "**Status:** PASS", 1)
        gate_a = replace_gate_field(
            gate_a,
            "A",
            "Evidence / exact source SHA",
            f"candidate_sha={candidate}; tested_sha=e123ead90684b64a9809ad6d4ba7b8ddcb155155; scope=exact_candidate_ci; owner_approval=PASS by Alice; independent_review=PASS by Bob; artifact `12140396685`.",
        )
        gate_a = replace_gate_field(
            gate_a,
            "A",
            "Accountable owner / independent reviewer",
            "Alice (release owner) / Bob (independent reviewer).",
        )
        mutated = mutated[:start] + gate_a + mutated[end:]
        errors = validate_checklist(mutated)
        self.assertTrue(any("tested_sha differs from the selected release candidate" in error for error in errors))

    def test_pass_requires_tested_sha_even_when_candidate_sha_is_claimed(self):
        candidate = "f" * 40
        mutated = select_candidate(self.text, candidate)
        start, end = mutated.index("### Gate A"), mutated.index("### Gate B")
        gate_a = mutated[start:end].replace("**Status:** BLOCKED", "**Status:** PASS", 1)
        gate_a = replace_gate_field(
            gate_a,
            "A",
            "Evidence / exact source SHA",
            f"candidate_sha={candidate}; scope=exact_candidate_ci; owner_approval=PASS by Alice; independent_review=PASS by Bob",
        )
        gate_a = replace_gate_field(
            gate_a,
            "A",
            "Accountable owner / independent reviewer",
            "Alice (release owner) / Bob (independent reviewer).",
        )
        mutated = mutated[:start] + gate_a + mutated[end:]
        errors = validate_checklist(mutated)
        self.assertTrue(any("must include exactly one tested_sha claim" in error for error in errors), errors)

    def test_approvals_must_match_their_named_roles(self):
        candidate = "e" * 40
        mutated = select_candidate(self.text, candidate)
        start, end = mutated.index("### Gate A"), mutated.index("### Gate B")
        gate_a = mutated[start:end].replace("**Status:** BLOCKED", "**Status:** PASS", 1)
        gate_a = replace_gate_field(
            gate_a,
            "A",
            "Evidence / exact source SHA",
            f"candidate_sha={candidate}; tested_sha={candidate}; scope=exact_candidate_ci; owner_approval=PASS by Bob; independent_review=PASS by Alice",
        )
        gate_a = replace_gate_field(
            gate_a,
            "A",
            "Accountable owner / independent reviewer",
            "Alice (release owner) / Bob (independent reviewer).",
        )
        mutated = mutated[:start] + gate_a + mutated[end:]
        errors = validate_checklist(mutated)
        self.assertTrue(any("owner_approval approver must exactly match the named owner" in error for error in errors), errors)
        self.assertTrue(any("independent_review approver must exactly match the named independent reviewer" in error for error in errors), errors)

    def test_owner_and_independent_reviewer_must_be_different_identities(self):
        candidate = "e" * 40
        mutated = select_candidate(self.text, candidate)
        start, end = mutated.index("### Gate A"), mutated.index("### Gate B")
        gate_a = mutated[start:end].replace("**Status:** BLOCKED", "**Status:** PASS", 1)
        gate_a = replace_gate_field(
            gate_a,
            "A",
            "Evidence / exact source SHA",
            f"candidate_sha={candidate}; tested_sha={candidate}; scope=exact_candidate_ci; owner_approval=PASS by Alice; independent_review=PASS by Alice",
        )
        gate_a = replace_gate_field(
            gate_a,
            "A",
            "Accountable owner / independent reviewer",
            "Alice (release owner) / Alice (independent reviewer).",
        )
        mutated = mutated[:start] + gate_a + mutated[end:]
        errors = validate_checklist(mutated)
        self.assertTrue(any("owner and independent reviewer must be different identities" in error for error in errors), errors)

    def test_owner_reviewer_separator_must_be_unambiguous(self):
        candidate = "e" * 40
        mutated = select_candidate(self.text, candidate)
        start, end = mutated.index("### Gate A"), mutated.index("### Gate B")
        gate_a = mutated[start:end].replace("**Status:** BLOCKED", "**Status:** PASS", 1)
        gate_a = replace_gate_field(
            gate_a,
            "A",
            "Evidence / exact source SHA",
            f"candidate_sha={candidate}; tested_sha={candidate}; scope=exact_candidate_ci; owner_approval=PASS by Alice; independent_review=PASS by Bob / Alice",
        )
        gate_a = replace_gate_field(
            gate_a,
            "A",
            "Accountable owner / independent reviewer",
            "Alice (release owner) / Bob (independent reviewer) / Alice.",
        )
        mutated = mutated[:start] + gate_a + mutated[end:]
        errors = validate_checklist(mutated)
        self.assertTrue(any("exactly one ' / ' separator" in error for error in errors), errors)

    def test_unrecognized_parenthetical_cannot_hide_an_identity(self):
        candidate = "e" * 40
        mutated = select_candidate(self.text, candidate)
        start, end = mutated.index("### Gate A"), mutated.index("### Gate B")
        gate_a = mutated[start:end].replace("**Status:** BLOCKED", "**Status:** PASS", 1)
        gate_a = replace_gate_field(
            gate_a,
            "A",
            "Evidence / exact source SHA",
            f"candidate_sha={candidate}; tested_sha={candidate}; scope=exact_candidate_ci; owner_approval=PASS by Alice; independent_review=PASS by Bob",
        )
        gate_a = replace_gate_field(
            gate_a,
            "A",
            "Accountable owner / independent reviewer",
            "Alice (release owner) / Bob (Alice).",
        )
        mutated = mutated[:start] + gate_a + mutated[end:]
        errors = validate_checklist(mutated)
        self.assertTrue(any("independent_review approver must exactly match the named independent reviewer" in error for error in errors), errors)

    def test_approver_must_not_match_only_a_substring_of_owner_identity(self):
        candidate = "e" * 40
        mutated = select_candidate(self.text, candidate)
        start, end = mutated.index("### Gate A"), mutated.index("### Gate B")
        gate_a = mutated[start:end].replace("**Status:** BLOCKED", "**Status:** PASS", 1)
        gate_a = replace_gate_field(
            gate_a,
            "A",
            "Evidence / exact source SHA",
            f"candidate_sha={candidate}; tested_sha={candidate}; scope=exact_candidate_ci; owner_approval=PASS by Alice; independent_review=PASS by Bob",
        )
        gate_a = replace_gate_field(
            gate_a,
            "A",
            "Accountable owner / independent reviewer",
            "Malice (release owner) / Bob (independent reviewer).",
        )
        mutated = mutated[:start] + gate_a + mutated[end:]
        errors = validate_checklist(mutated)
        self.assertTrue(any("owner_approval approver must exactly match the named owner" in error for error in errors), errors)

    def test_disposable_test_evidence_cannot_satisfy_hosted_gate(self):
        candidate = "e123ead90684b64a9809ad6d4ba7b8ddcb155155"
        mutated = select_candidate(self.text, candidate)
        gate_d = replace_gate_field(mutated, "D", "Status", "PASS")
        gate_d = replace_gate_field(
            gate_d,
            "D",
            "Evidence / exact source SHA",
            f"candidate_sha={candidate}; tested_sha={candidate}; scope=hosted_read_only_capture_and_review; owner_approval=PASS by Alice; independent_review=PASS by Bob.",
        )
        gate_d = replace_gate_field(
            gate_d,
            "D",
            "Accountable owner / independent reviewer",
            "Alice (authorized Development database owner) / Bob (independent database-platform reviewer).",
        )
        errors = validate_checklist(gate_d)
        self.assertTrue(any("does not claim required scope=HOSTED_READ_ONLY_CAPTURE" in error for error in errors))

    def test_production_scope_rejects_explicitly_disposable_evidence(self):
        candidate = "e123ead90684b64a9809ad6d4ba7b8ddcb155155"
        mutated = select_candidate(self.text, candidate)
        gate_d = replace_gate_field(mutated, "D", "Status", "PASS")
        gate_d = replace_gate_field(
            gate_d,
            "D",
            "Evidence / exact source SHA",
            f"not a fresh hosted capture; candidate_sha={candidate}; tested_sha={candidate}; scope=hosted_read_only_capture; owner_approval=PASS by Alice; independent_review=PASS by Bob.",
        )
        gate_d = replace_gate_field(
            gate_d,
            "D",
            "Accountable owner / independent reviewer",
            "Alice (authorized Development database owner) / Bob (independent database-platform reviewer).",
        )
        self.assertTrue(any("explicitly disclaims required scope=HOSTED_READ_ONLY_CAPTURE" in error for error in validate_checklist(gate_d)))

    def test_synthetic_ci_logical_restore_smoke_cannot_satisfy_application_backup_restore(self):
        candidate = "e123ead90684b64a9809ad6d4ba7b8ddcb155155"
        mutated = select_candidate(self.text, candidate)
        gate_g = replace_gate_field(mutated, "G", "Status", "PASS")
        gate_g = replace_gate_field(
            gate_g,
            "G",
            "Evidence / exact source SHA",
            f"candidate_sha={candidate}; tested_sha={candidate}; scope=application_backup_restore; owner_approval=PASS by Alice; independent_review=PASS by Bob; synthetic CI logical-restore smoke.",
        )
        gate_g = replace_gate_field(
            gate_g,
            "G",
            "Accountable owner / independent reviewer",
            "Alice (backup/recovery owner) / Bob (independent recovery reviewer).",
        )
        errors = validate_checklist(gate_g)
        self.assertTrue(
            any("explicitly disclaims required scope=APPLICATION_BACKUP_RESTORE" in error for error in errors),
            errors,
        )

    def test_scope_prefix_does_not_satisfy_a_different_scope(self):
        candidate = "e123ead90684b64a9809ad6d4ba7b8ddcb155155"
        mutated = select_candidate(self.text, candidate)
        gate_d = replace_gate_field(mutated, "D", "Status", "PASS")
        gate_d = replace_gate_field(
            gate_d,
            "D",
            "Evidence / exact source SHA",
            f"candidate_sha={candidate}; tested_sha={candidate}; scope=hosted_read_only_capture_and_review; owner_approval=PASS by Alice; independent_review=PASS by Bob.",
        )
        gate_d = replace_gate_field(
            gate_d,
            "D",
            "Accountable owner / independent reviewer",
            "Alice (authorized Development database owner) / Bob (independent database-platform reviewer).",
        )
        errors = validate_checklist(gate_d)
        self.assertTrue(any("does not claim required scope=HOSTED_READ_ONLY_CAPTURE" in error for error in errors))

    def test_conflicting_duplicate_claims_fail_closed(self):
        candidate = "e" * 40
        stale = "f" * 40
        mutated = select_candidate(self.text, candidate)
        start, end = mutated.index("### Gate A"), mutated.index("### Gate B")
        gate_a = mutated[start:end].replace("**Status:** BLOCKED", "**Status:** PASS", 1)
        gate_a = replace_gate_field(
            gate_a,
            "A",
            "Evidence / exact source SHA",
            f"candidate_sha={candidate}; candidate_sha={stale}; tested_sha={candidate}; tested_sha=bad; scope=exact_candidate_ci; scope=runtime_security_review; owner_approval=PASS by Alice; owner_approval=PASS by Alice; independent_review=PASS by Bob",
        ).replace(
            "**Accountable owner / independent reviewer:** Release owner / independent release reviewer (named assignment pending).",
            "**Accountable owner / independent reviewer:** Alice (release owner) / Bob (independent reviewer).", 1,
        )
        mutated = mutated[:start] + gate_a + mutated[end:]
        errors = validate_checklist(mutated)
        self.assertTrue(any("must bind candidate_sha" in error for error in errors), errors)
        self.assertTrue(any("does not claim required scope=EXACT_CANDIDATE_CI" in error for error in errors), errors)
        self.assertTrue(any("malformed tested_sha" in error for error in errors), errors)
        self.assertTrue(any("lacks owner_approval=PASS" in error for error in errors), errors)

    def test_well_formed_candidate_bound_claims_are_accepted(self):
        candidate = "e" * 40
        mutated = select_candidate(self.text, candidate)
        start, end = mutated.index("### Gate A"), mutated.index("### Gate B")
        gate_a = mutated[start:end].replace("**Status:** BLOCKED", "**Status:** PASS", 1)
        gate_a = replace_gate_field(
            gate_a,
            "A",
            "Evidence / exact source SHA",
            f"candidate_sha={candidate}; tested_sha={candidate}; scope=exact_candidate_ci; owner_approval=PASS by Alice; independent_review=PASS by Bob",
        ).replace(
            "**Accountable owner / independent reviewer:** Release owner / independent release reviewer (named assignment pending).",
            "**Accountable owner / independent reviewer:** Alice (release owner) / Bob (independent reviewer).", 1,
        )
        mutated = mutated[:start] + gate_a + mutated[end:]
        self.assertFalse(any(error.startswith("Gate A:") for error in validate_checklist(mutated)))

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
            ("N/A", "**Accountable owner / independent reviewer:** Alice (release owner) / Bob (independent release reviewer)."),
        ):
            with self.subTest(status=status):
                mutated = select_candidate(self.text, candidate)
                start, end = mutated.index("### Gate A"), mutated.index("### Gate B")
                gate_a = mutated[start:end].replace("**Status:** BLOCKED", f"**Status:** {status}", 1)
                gate_a = replace_gate_field(
                    gate_a,
                    "A",
                    "Evidence / exact source SHA",
                    f"candidate_sha={candidate}; tested_sha={candidate}; scope=exact_candidate_ci",
                )
                gate_a = gate_a.replace(
                    "**Accountable owner / independent reviewer:** Release owner / independent release reviewer (named assignment pending).",
                    approval_record if status == "N/A" else "**Accountable owner / independent reviewer:** Alice (release owner) / Bob (independent release reviewer).",
                    1,
                )
                mutated = mutated[:start] + gate_a + mutated[end:]
                errors = validate_checklist(mutated)
                self.assertTrue(any("lacks independent_review=PASS by an accountable person/team" in error for error in errors), errors)
                self.assertTrue(any("lacks owner_approval=PASS by an accountable person/team" in error for error in errors), errors)

    def test_blank_exit_condition_and_closure_action_fail(self):
        for field in ("Exit condition", "Closure action", "Required evidence scope"):
            with self.subTest(field=field):
                line = next(line for line in self.text.splitlines() if line.startswith(f"- **{field}:**"))
                mutated = self.text.replace(line, f"- **{field}:**", 1)
                errors = validate_checklist(mutated)
                self.assertTrue(any(f"Gate A: missing {field}" in error for error in errors), errors)


if __name__ == "__main__":
    unittest.main()

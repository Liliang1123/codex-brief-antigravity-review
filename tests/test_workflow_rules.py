import importlib.util
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load_validator():
    path = ROOT / "scripts" / "validate_templates.py"
    spec = importlib.util.spec_from_file_location("validate_templates", path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class WorkflowRulesTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.validator = load_validator()
        cls.skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        cls.handoff = (ROOT / "references" / "handoff-contract.md").read_text(encoding="utf-8")
        cls.review = (ROOT / "references" / "review-template.md").read_text(encoding="utf-8")

    def test_description_targets_prompt_and_evidence_review(self):
        description = self.skill.split("---", 2)[1]
        self.assertIn("task prompts", description)
        self.assertIn("diff", description)
        self.assertNotIn("breaking down implementation/task/step/batch", description)

    def test_standalone_path_does_not_require_handoff(self):
        self.assertIn("Standalone Lightweight", self.skill)
        section = self.skill.split("## Standalone Lightweight", 1)[1].split("## ", 1)[0]
        self.assertIn("does not require", section)
        self.assertIn("Handoff Contract", section)

    def test_review_and_fix_returns_to_change_gate(self):
        self.assertIn("Review and fix", self.skill)
        self.assertIn("openspec-superpower-change", self.skill)

    def test_canonical_contract_lives_only_in_status(self):
        self.assertIn("canonical", self.handoff)
        self.assertIn("docs/agent-collab/<change-id>/status.md", self.handoff)
        self.assertIn("must not embed", self.handoff)

    def test_attempt_specific_artifacts_preserve_review_history(self):
        self.assertIn("attempt-<AA>", self.skill)
        self.assertIn("same batch", self.skill)
        self.assertIn("needs-fix", self.skill)

    def test_fail_and_blocked_must_reenter_review(self):
        self.assertIn("FAIL", self.review)
        self.assertIn("needs-fix", self.review)
        self.assertIn("resume_condition", self.review)
        self.assertIn("must be reviewed again", self.review)

    def test_complete_contract_requires_review_and_final_verification(self):
        data = self.validator.extract_handoff_contract(self.handoff, "handoff")
        data.update(
            lifecycle_state="complete",
            last_review_result="blocked",
            final_verification="pending",
            final_review_result="pending",
            next_owner="user",
        )
        with self.assertRaisesRegex(AssertionError, "complete"):
            self.validator.validate_handoff_contract(data, "invalid-complete")

    def test_fallback_scalar_parser_handles_yaml_booleans_and_null(self):
        self.assertIs(self.validator.parse_scalar("true"), True)
        self.assertIs(self.validator.parse_scalar("false"), False)
        self.assertIsNone(self.validator.parse_scalar("null"))

    def test_fail_transition_requires_new_attempt_on_same_batch(self):
        before = self.validator.extract_handoff_contract(self.handoff, "handoff")
        before.update(lifecycle_state="ready-for-review", last_review_result="not-run")
        after = dict(before)
        after.update(
            lifecycle_state="needs-fix",
            last_review_result="fail",
            attempt=before["attempt"],
            contract_revision=before["contract_revision"] + 1,
            next_owner="codex-brief-antigravity-review",
        )
        with self.assertRaisesRegex(AssertionError, "attempt"):
            self.validator.validate_transition(before, after, "invalid-fail")

    def test_final_batch_pass_hands_back_to_router(self):
        before = self.validator.extract_handoff_contract(self.handoff, "handoff")
        before.update(
            lifecycle_state="ready-for-review",
            current_batch=before["planned_batches"],
            last_review_result="not-run",
        )
        after = dict(before)
        after.update(
            lifecycle_state="awaiting-final-verification",
            last_review_result="pass",
            contract_revision=before["contract_revision"] + 1,
            next_owner="openspec-superpower-change",
        )
        self.validator.validate_transition(before, after, "final-pass")

    def test_execution_contract_rejects_unapproved_proposal_mode(self):
        data = self.validator.extract_handoff_contract(self.handoff, "handoff")
        data.update(
            mode="openspec-proposal",
            approval_status="proposed",
            executor="codex",
            governor="openspec-superpower-change",
        )
        with self.assertRaisesRegex(AssertionError, "execution contract"):
            self.validator.validate_handoff_contract(data, "proposal")

    def test_regular_transition_cannot_change_batch_attempt_or_owner(self):
        before = self.validator.extract_handoff_contract(self.handoff, "handoff")
        after = dict(before)
        after.update(
            lifecycle_state="ready-for-execution",
            current_batch=before["current_batch"] + 1,
            attempt=99,
            next_owner="user",
            contract_revision=before["contract_revision"] + 1,
        )
        with self.assertRaisesRegex(AssertionError, "same batch and attempt|next_owner"):
            self.validator.validate_transition(before, after, "illegal-jump")

    def test_blocked_contract_requires_blocked_review_result(self):
        data = self.validator.extract_handoff_contract(self.handoff, "handoff")
        data.update(
            lifecycle_state="blocked",
            last_review_result="pass",
            blocked_reason="dependency unavailable",
            blocker_owner="dependency",
            resume_condition="dependency restored",
            next_owner="user",
        )
        with self.assertRaisesRegex(AssertionError, "blocked review"):
            self.validator.validate_handoff_contract(data, "blocked-pass")

    def test_compact_contract_still_requires_typed_evidence_fields(self):
        data = self.validator.extract_handoff_contract(self.handoff, "handoff")
        data.update(
            risk_profile="compact",
            step_critical="pytest",
            final_critical="pytest",
            stop_conditions="none",
            verification_strategy="run tests",
        )
        with self.assertRaisesRegex(AssertionError, "list|mapping"):
            self.validator.validate_handoff_contract(data, "untyped-compact")

    def test_complete_state_is_terminal(self):
        before = self.validator.extract_handoff_contract(self.handoff, "handoff")
        before.update(
            lifecycle_state="complete",
            current_batch=before["planned_batches"],
            last_review_result="pass",
            final_review_result="pass",
            final_verification="pass",
            next_owner="user",
        )
        after = dict(before)
        after.update(attempt=2, contract_revision=before["contract_revision"] + 1)
        with self.assertRaisesRegex(AssertionError, "terminal"):
            self.validator.validate_transition(before, after, "mutate-complete")

    def test_change_id_must_be_path_safe_slug(self):
        data = self.validator.extract_handoff_contract(self.handoff, "handoff")
        data["change_id"] = "../escape"
        with self.assertRaisesRegex(AssertionError, "change_id"):
            self.validator.validate_handoff_contract(data, "unsafe-change-id")

    def test_brief_uses_execution_revision_and_review_uses_current_revision(self):
        brief = (ROOT / "references" / "brief-template.md").read_text(encoding="utf-8")
        self.assertIn("ready-for-execution", brief)
        self.assertIn("Execution revision", self.review)
        self.assertIn("Review revision", self.review)

    def test_final_gate_failure_can_return_to_fix_with_new_attempt(self):
        before = self.validator.extract_handoff_contract(self.handoff, "handoff")
        before.update(
            lifecycle_state="awaiting-final-verification",
            current_batch=before["planned_batches"],
            last_review_result="pass",
            next_owner="openspec-superpower-change",
        )
        after = dict(before)
        after.update(
            lifecycle_state="needs-fix",
            attempt=before["attempt"] + 1,
            contract_revision=before["contract_revision"] + 1,
            last_review_result="fail",
            final_review_result="fail",
            next_owner="openspec-superpower-change",
        )
        self.validator.validate_transition(before, after, "final-gate-fix")

    def test_validator_honors_target_directory(self):
        missing = ROOT / "tests" / "definitely-missing-skill"
        result = subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "validate_templates.py"), str(missing)],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertNotEqual(0, result.returncode)
        self.assertIn(str(missing), result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()

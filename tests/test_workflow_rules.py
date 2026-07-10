import importlib.util
import hashlib
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def artifact(path: str) -> dict[str, str]:
    return {"path": path, "sha256": "a" * 64}


def evidence_manifest(
    role: str,
    result: str,
    change_id: str = "add-example-change",
    current_batch: int = 1,
    attempt: int = 1,
    contract_revision: int = 1,
    canonical_sha256: str = "b" * 64,
) -> str:
    return (
        "<!-- COOP_EVIDENCE_MANIFEST_START -->\n"
        "```yaml\n"
        "evidence_schema_version: 1\n"
        f"evidence_role: {role}\n"
        f"evidence_result: {result}\n"
        f"change_id: {change_id}\n"
        f"current_batch: {current_batch}\n"
        f"attempt: {attempt}\n"
        f"contract_revision: {contract_revision}\n"
        f"canonical_sha256: {canonical_sha256}\n"
        "```\n"
        "<!-- COOP_EVIDENCE_MANIFEST_END -->\n"
    )


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
        for expected in (
            "non-state-changing", "read-only", "does not request fixes",
            "final completion", "valid Handoff Contract", "file edits",
            "workflow/template changes",
        ):
            self.assertIn(expected, description)
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

    def test_preflight_uses_pass_or_blocked_without_batch_review_substitution(self):
        brief = (ROOT / "references" / "brief-template.md").read_text(encoding="utf-8")
        self.assertIn("结果：PASS / BLOCKED", brief)
        self.assertNotIn("结果：PASS / FAIL / BLOCKED", brief)
        self.assertIn("Preflight uses only `PASS`/`BLOCKED`", self.skill)
        self.assertIn("不能充当 `batch-review`", self.review)

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

    def test_handoff_schema_has_evidence_bound_v3_fields(self):
        for expected in (
            "schema_version: 3",
            "attempt_report_artifact:",
            "last_review_artifact:",
            "final_verification_artifact:",
            "final_review_artifact:",
        ):
            self.assertIn(expected, self.handoff)

    def test_fallback_scalar_parser_handles_yaml_booleans_and_null(self):
        self.assertIs(self.validator.parse_scalar("true"), True)
        self.assertIs(self.validator.parse_scalar("false"), False)
        self.assertIsNone(self.validator.parse_scalar("null"))

    def test_fail_transition_requires_new_attempt_on_same_batch(self):
        before = self.validator.extract_handoff_contract(self.handoff, "handoff")
        before.update(
            lifecycle_state="ready-for-review",
            last_review_result="not-run",
            attempt_report_artifact=artifact("docs/agent-collab/change/report.md"),
        )
        after = dict(before)
        after.update(
            lifecycle_state="needs-fix",
            last_review_result="fail",
            last_review_artifact=artifact("docs/review/fail.md"),
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
            attempt_report_artifact=artifact("docs/agent-collab/change/report.md"),
        )
        after = dict(before)
        after.update(
            lifecycle_state="awaiting-final-verification",
            last_review_result="pass",
            last_review_artifact=artifact("docs/review/batch.md"),
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
        with self.assertRaisesRegex(AssertionError, "blocked|tuple"):
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
            attempt_report_artifact=artifact("docs/agent-collab/change/report.md"),
            last_review_artifact=artifact("docs/review/batch.md"),
            final_verification_artifact=artifact("docs/agent-collab/change/final-verification.md"),
            final_review_artifact=artifact("docs/review/final.md"),
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
        before = self._awaiting_contract("pass")
        after = dict(before)
        after.update(
            lifecycle_state="needs-fix",
            attempt=before["attempt"] + 1,
            contract_revision=before["contract_revision"] + 1,
            final_review_result="fail",
            final_review_artifact=artifact("docs/review/final-fail.md"),
            next_owner="openspec-superpower-change",
        )
        self.validator.validate_transition(before, after, "final-gate-fix")

    def test_all_external_profiles_require_nonblank_critical_commands(self):
        data = self.validator.extract_handoff_contract(self.handoff, "handoff")
        data.update(risk_profile="compact", step_critical=[], final_critical=[])
        with self.assertRaisesRegex(AssertionError, "step_critical|final_critical"):
            self.validator.validate_handoff_contract(data, "empty-critical")

        data = self.validator.extract_handoff_contract(self.handoff, "handoff")
        data.update(step_critical=["   "], final_critical=["\t"])
        with self.assertRaisesRegex(AssertionError, "non-blank"):
            self.validator.validate_handoff_contract(data, "blank-critical")

    def test_blank_stop_and_blocker_values_are_rejected(self):
        data = self.validator.extract_handoff_contract(self.handoff, "handoff")
        data["stop_conditions"] = [" "]
        with self.assertRaisesRegex(AssertionError, "stop_conditions"):
            self.validator.validate_handoff_contract(data, "blank-stop")

        data = self.validator.extract_handoff_contract(self.handoff, "handoff")
        data.update(
            lifecycle_state="blocked",
            last_review_result="blocked",
            last_review_artifact=artifact("docs/review/blocked.md"),
            attempt_report_artifact=artifact("docs/agent-collab/change/report-abort.md"),
            blocked_reason=" ",
            blocker_owner="dependency",
            resume_condition="\t",
            next_owner="user",
        )
        with self.assertRaisesRegex(AssertionError, "blocked_reason|resume_condition"):
            self.validator.validate_handoff_contract(data, "blank-blocker")

    def test_boolean_is_not_a_positive_integer(self):
        for key in ("current_batch", "planned_batches", "attempt", "contract_revision"):
            data = self.validator.extract_handoff_contract(self.handoff, "handoff")
            data[key] = True
            with self.subTest(key=key):
                with self.assertRaisesRegex(AssertionError, "positive integer"):
                    self.validator.validate_handoff_contract(data, f"bool-{key}")

    def test_readonly_fields_must_match_exactly_without_duplicates(self):
        base = self.validator.extract_handoff_contract(self.handoff, "handoff")
        for readonly in (
            list(base["readonly_fields"]) + ["attempt"],
            list(base["readonly_fields"]) + [base["readonly_fields"][0]],
            list(base["readonly_fields"])[1:],
        ):
            data = dict(base)
            data["readonly_fields"] = readonly
            with self.subTest(readonly=readonly):
                with self.assertRaisesRegex(AssertionError, "readonly_fields"):
                    self.validator.validate_handoff_contract(data, "readonly-mismatch")

    def test_result_and_artifact_fields_are_strictly_paired(self):
        data = self.validator.extract_handoff_contract(self.handoff, "handoff")
        data["last_review_artifact"] = artifact("docs/review/unexpected.md")
        with self.assertRaisesRegex(AssertionError, "last_review_artifact"):
            self.validator.validate_handoff_contract(data, "unexpected-review-artifact")

        data = self._awaiting_contract("pass")
        data["final_verification_artifact"] = None
        with self.assertRaisesRegex(AssertionError, "final_verification_artifact"):
            self.validator.validate_handoff_contract(data, "missing-final-evidence")

    def test_artifact_reference_must_be_safe_relative_path_and_sha256(self):
        data = self.validator.extract_handoff_contract(self.handoff, "handoff")
        data.update(
            lifecycle_state="ready-for-brief",
            current_batch=2,
            contract_revision=4,
            last_review_result="pass",
            last_review_artifact={"path": "../escape", "sha256": "x"},
        )
        with self.assertRaisesRegex(AssertionError, "artifact|sha256|relative"):
            self.validator.validate_handoff_contract(data, "unsafe-artifact")

    def test_runtime_artifact_validation_checks_file_size_and_hash(self):
        data = self.validator.extract_handoff_contract(self.handoff, "handoff")
        data.update(
            lifecycle_state="ready-for-brief",
            current_batch=2,
            contract_revision=4,
            last_review_result="pass",
            last_review_artifact=artifact("docs/review/batch.md"),
        )
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            review = root / "docs" / "review" / "batch.md"
            review.parent.mkdir(parents=True)
            review.write_text(evidence_manifest("batch-review", "pass"), encoding="utf-8")
            data["last_review_artifact"]["sha256"] = hashlib.sha256(review.read_bytes()).hexdigest()
            self.validator.validate_evidence_artifacts(data, root, "runtime")
            data["last_review_artifact"]["sha256"] = "0" * 64
            with self.assertRaisesRegex(AssertionError, "sha256"):
                self.validator.validate_evidence_artifacts(data, root, "runtime")

    def _awaiting_contract(self, verification: str = "pending") -> dict:
        data = self.validator.extract_handoff_contract(self.handoff, "handoff")
        data.update(
            lifecycle_state="awaiting-final-verification",
            current_batch=data["planned_batches"],
            last_review_result="pass",
            attempt_report_artifact=artifact("docs/agent-collab/change/report.md"),
            last_review_artifact=artifact("docs/review/batch.md"),
            final_verification=verification,
            final_verification_artifact=(
                artifact("docs/agent-collab/change/final-verification.md")
                if verification != "pending" else None
            ),
            final_review_result="pending",
            final_review_artifact=None,
            next_owner="openspec-superpower-change",
        )
        return data

    def test_final_verification_pass_can_be_persisted_before_final_review(self):
        before = self._awaiting_contract()
        after = self._awaiting_contract("pass")
        after["contract_revision"] = before["contract_revision"] + 1
        self.validator.validate_transition(before, after, "persist-final-verification")

    def test_complete_requires_persisted_verification_and_all_artifacts(self):
        before = self._awaiting_contract()
        after = self._awaiting_contract("pass")
        after.update(
            lifecycle_state="complete",
            final_review_result="pass",
            final_review_artifact=artifact("docs/review/final.md"),
            next_owner="user",
            contract_revision=before["contract_revision"] + 1,
        )
        with self.assertRaisesRegex(AssertionError, "persisted final verification"):
            self.validator.validate_transition(before, after, "atomic-complete")

        before = self._awaiting_contract("pass")
        after = dict(before)
        after.update(
            lifecycle_state="complete",
            final_review_result="pass",
            final_review_artifact=artifact("docs/review/final.md"),
            next_owner="user",
            contract_revision=before["contract_revision"] + 1,
        )
        self.validator.validate_transition(before, after, "evidenced-complete")

    def test_batch_blocked_cannot_resume_directly_to_review(self):
        before = self.validator.extract_handoff_contract(self.handoff, "handoff")
        before.update(
            lifecycle_state="blocked",
            last_review_result="blocked",
            attempt_report_artifact=artifact("docs/agent-collab/change/abort.md"),
            last_review_artifact=artifact("docs/review/blocked.md"),
            blocked_reason="dependency unavailable",
            blocker_owner="dependency",
            resume_condition="dependency restored",
            next_owner="user",
        )
        after = dict(before)
        after.update(
            lifecycle_state="ready-for-review",
            last_review_result="not-run",
            last_review_artifact=None,
            blocked_reason=None,
            blocker_owner="none",
            resume_condition=None,
            next_owner="codex-brief-antigravity-review",
            attempt=before["attempt"] + 1,
            contract_revision=before["contract_revision"] + 1,
        )
        with self.assertRaisesRegex(AssertionError, "invalid lifecycle transition"):
            self.validator.validate_transition(before, after, "skip-report")

    def test_needs_fix_accepts_batch_and_each_final_failure_stage(self):
        batch = self.validator.extract_handoff_contract(self.handoff, "handoff")
        batch.update(
            lifecycle_state="needs-fix",
            last_review_result="fail",
            attempt_report_artifact=artifact("docs/agent-collab/change/report.md"),
            last_review_artifact=artifact("docs/review/batch-fail.md"),
        )
        self.validator.validate_handoff_contract(batch, "batch-fail")

        verification = self._awaiting_contract()
        verification.update(
            lifecycle_state="needs-fix",
            final_verification="fail",
            final_verification_artifact=artifact("docs/agent-collab/change/final-verification-fail.md"),
        )
        self.validator.validate_handoff_contract(verification, "verification-fail")

        review = self._awaiting_contract("pass")
        review.update(
            lifecycle_state="needs-fix",
            final_review_result="fail",
            final_review_artifact=artifact("docs/review/final-fail.md"),
        )
        self.validator.validate_handoff_contract(review, "final-review-fail")

    def test_blocked_accepts_batch_and_each_final_block_stage(self):
        common = {
            "lifecycle_state": "blocked",
            "blocked_reason": "dependency unavailable",
            "blocker_owner": "dependency",
            "resume_condition": "dependency restored",
            "next_owner": "user",
        }
        batch = self.validator.extract_handoff_contract(self.handoff, "handoff")
        batch.update(
            **common,
            last_review_result="blocked",
            attempt_report_artifact=artifact("docs/agent-collab/change/abort.md"),
            last_review_artifact=artifact("docs/review/batch-blocked.md"),
        )
        self.validator.validate_handoff_contract(batch, "batch-blocked")

        verification = self._awaiting_contract()
        verification.update(
            **common,
            final_verification="blocked",
            final_verification_artifact=artifact("docs/agent-collab/change/final-verification-blocked.md"),
        )
        self.validator.validate_handoff_contract(verification, "verification-blocked")

        review = self._awaiting_contract("pass")
        review.update(
            **common,
            final_review_result="blocked",
            final_review_artifact=artifact("docs/review/final-blocked.md"),
        )
        self.validator.validate_handoff_contract(review, "final-review-blocked")

    def test_preflight_blocked_does_not_require_an_attempt_report(self):
        data = self.validator.extract_handoff_contract(self.handoff, "handoff")
        data.update(
            lifecycle_state="blocked",
            last_review_result="blocked",
            last_review_artifact=artifact("docs/review/preflight-blocked.md"),
            blocked_reason="brief has an unauthorized git step",
            blocker_owner="codex-brief-antigravity-review",
            resume_condition="brief revised and preflight rerun",
            next_owner="codex-brief-antigravity-review",
        )
        self.assertIsNone(data["attempt_report_artifact"])
        self.validator.validate_handoff_contract(data, "preflight-blocked")

    def test_final_review_blocked_resume_preserves_verification_evidence(self):
        before = self._awaiting_contract("pass")
        before.update(
            lifecycle_state="blocked",
            final_review_result="blocked",
            final_review_artifact=artifact("docs/review/final-blocked.md"),
            blocked_reason="reviewer unavailable",
            blocker_owner="dependency",
            resume_condition="reviewer available",
            next_owner="user",
        )
        after = dict(before)
        after.update(
            lifecycle_state="awaiting-final-verification",
            final_review_result="pending",
            final_review_artifact=None,
            blocked_reason=None,
            blocker_owner="none",
            resume_condition=None,
            next_owner="openspec-superpower-change",
            contract_revision=before["contract_revision"] + 1,
        )
        self.validator.validate_transition(before, after, "resume-final-review")

        replaced = dict(after)
        replaced["attempt_report_artifact"] = artifact("docs/agent-collab/change/replacement-report.md")
        replaced["last_review_artifact"] = artifact("docs/review/replacement-batch.md")
        with self.assertRaisesRegex(AssertionError, "cannot rewrite"):
            self.validator.validate_transition(before, replaced, "resume-final-review-rewrite")

    def test_runtime_artifact_validation_rejects_missing_empty_and_symlink_escape(self):
        data = self.validator.extract_handoff_contract(self.handoff, "handoff")
        data.update(
            lifecycle_state="ready-for-brief",
            current_batch=2,
            contract_revision=4,
            last_review_result="pass",
            attempt_report_artifact=artifact("docs/agent-collab/change/report.md"),
            last_review_artifact=artifact("docs/review/batch.md"),
        )
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            root = base / "root"
            root.mkdir()
            with self.assertRaisesRegex(AssertionError, "exist and be non-empty"):
                self.validator.validate_evidence_artifacts(data, root, "missing")

            report = root / "docs" / "agent-collab" / "change" / "report.md"
            review = root / "docs" / "review" / "batch.md"
            report.parent.mkdir(parents=True)
            review.parent.mkdir(parents=True)
            report.write_text(evidence_manifest("attempt-report", "pass"), encoding="utf-8")
            review.write_text("", encoding="utf-8")
            data["attempt_report_artifact"]["sha256"] = hashlib.sha256(report.read_bytes()).hexdigest()
            with self.assertRaisesRegex(AssertionError, "exist and be non-empty"):
                self.validator.validate_evidence_artifacts(data, root, "empty")

            outside = base / "outside.md"
            outside.write_text("outside\n", encoding="utf-8")
            review.unlink()
            review.symlink_to(outside)
            data["last_review_artifact"]["sha256"] = hashlib.sha256(outside.read_bytes()).hexdigest()
            with self.assertRaisesRegex(AssertionError, "outside artifact root"):
                self.validator.validate_evidence_artifacts(data, root, "symlink")

    def test_nonfinal_batch_promotion_requires_review_pass_and_keeps_decision_evidence(self):
        before = self.validator.extract_handoff_contract(self.handoff, "handoff")
        before.update(
            lifecycle_state="ready-for-review",
            attempt_report_artifact=artifact("docs/agent-collab/change/report.md"),
            next_owner="codex-brief-antigravity-review",
        )
        after = dict(before)
        after.update(
            lifecycle_state="ready-for-brief",
            current_batch=before["current_batch"] + 1,
            attempt=1,
            contract_revision=before["contract_revision"] + 1,
            attempt_report_artifact=None,
            last_review_result="not-run",
            last_review_artifact=None,
            next_owner="codex-brief-antigravity-review",
        )
        with self.assertRaisesRegex(AssertionError, "Review PASS|review evidence"):
            self.validator.validate_transition(before, after, "promote-without-review")

    def test_batch_decision_cannot_replace_the_report_that_was_reviewed(self):
        before = self.validator.extract_handoff_contract(self.handoff, "handoff")
        before.update(
            lifecycle_state="ready-for-review",
            current_batch=before["planned_batches"],
            attempt_report_artifact=artifact("docs/agent-collab/change/original-report.md"),
            next_owner="codex-brief-antigravity-review",
        )
        after = dict(before)
        after.update(
            lifecycle_state="awaiting-final-verification",
            contract_revision=before["contract_revision"] + 1,
            attempt_report_artifact=artifact("docs/agent-collab/change/replacement-report.md"),
            last_review_result="pass",
            last_review_artifact=artifact("docs/review/batch-pass.md"),
            next_owner="openspec-superpower-change",
        )
        with self.assertRaisesRegex(AssertionError, "attempt_report_artifact|reviewed Report"):
            self.validator.validate_transition(before, after, "replace-reviewed-report")

    def test_final_review_cannot_start_in_the_revision_that_first_persists_verification_pass(self):
        before = self._awaiting_contract()
        after = dict(before)
        after.update(
            lifecycle_state="blocked",
            contract_revision=before["contract_revision"] + 1,
            final_verification="pass",
            final_verification_artifact=artifact("docs/agent-collab/change/final-verification.md"),
            final_review_result="blocked",
            final_review_artifact=artifact("docs/review/final-review-blocked.md"),
            blocked_reason="reviewer unavailable",
            blocker_owner="dependency",
            resume_condition="reviewer available",
            next_owner="user",
        )
        with self.assertRaisesRegex(AssertionError, "persisted final verification|final Review"):
            self.validator.validate_transition(before, after, "atomic-final-verification-and-review")

    def test_blocked_self_transition_cannot_change_gate_tuple_or_evidence(self):
        before = self.validator.extract_handoff_contract(self.handoff, "handoff")
        before.update(
            lifecycle_state="blocked",
            current_batch=before["planned_batches"],
            attempt_report_artifact=artifact("docs/agent-collab/change/report-abort.md"),
            last_review_result="blocked",
            last_review_artifact=artifact("docs/review/batch-blocked.md"),
            blocked_reason="batch dependency unavailable",
            blocker_owner="dependency",
            resume_condition="batch dependency restored",
            next_owner="user",
        )
        after = dict(before)
        after.update(
            contract_revision=before["contract_revision"] + 1,
            last_review_result="pass",
            last_review_artifact=artifact("docs/review/fabricated-batch-pass.md"),
            final_verification="pass",
            final_verification_artifact=artifact("docs/agent-collab/change/fabricated-final-verification.md"),
            final_review_result="blocked",
            final_review_artifact=artifact("docs/review/final-review-blocked.md"),
            blocked_reason="final reviewer unavailable",
            resume_condition="final reviewer available",
        )
        with self.assertRaisesRegex(AssertionError, "blocked self-transition|result tuple|evidence"):
            self.validator.validate_transition(before, after, "rewrite-blocked-stage")

    def test_runtime_complete_snapshot_rejects_reused_artifact_with_mismatched_role_and_result(self):
        data = self.validator.extract_handoff_contract(self.handoff, "handoff")
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            evidence = root / "evidence.md"
            evidence.write_text(
                "# Review Result: FAIL\nNo verification commands were run.\n",
                encoding="utf-8",
            )
            shared_ref = {
                "path": "evidence.md",
                "sha256": hashlib.sha256(evidence.read_bytes()).hexdigest(),
            }
            data.update(
                lifecycle_state="complete",
                current_batch=data["planned_batches"],
                attempt_report_artifact=dict(shared_ref),
                last_review_result="pass",
                last_review_artifact=dict(shared_ref),
                final_verification="pass",
                final_verification_artifact=dict(shared_ref),
                final_review_result="pass",
                final_review_artifact=dict(shared_ref),
                next_owner="user",
            )
            with self.assertRaisesRegex(AssertionError, "artifact|evidence|result|role|distinct"):
                self.validator.validate_handoff_contract(data, "mixed-complete")
                self.validator.validate_evidence_artifacts(data, root, "mixed-complete")

    def test_runtime_evidence_manifest_binds_artifact_role_and_result(self):
        data = self.validator.extract_handoff_contract(self.handoff, "handoff")
        data.update(
            lifecycle_state="complete",
            current_batch=data["planned_batches"],
            contract_revision=5,
            last_review_result="pass",
            final_verification="pass",
            final_review_result="pass",
            next_owner="user",
        )
        specs = {
            "attempt_report_artifact": ("attempt-report.md", "attempt-report", "pass", 1),
            "last_review_artifact": ("batch-review.md", "batch-review", "pass", 2),
            "final_verification_artifact": ("final-verification.md", "final-verification", "pass", 3),
            "final_review_artifact": ("final-review.md", "final-review", "fail", 4),
        }
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for key, (path, role, result, revision) in specs.items():
                target = root / path
                target.write_text(
                    evidence_manifest(role, result, current_batch=2, contract_revision=revision),
                    encoding="utf-8",
                )
                data[key] = {"path": path, "sha256": hashlib.sha256(target.read_bytes()).hexdigest()}
            self.validator.validate_handoff_contract(data, "distinct-complete")
            with self.assertRaisesRegex(AssertionError, "evidence result"):
                self.validator.validate_evidence_artifacts(data, root, "distinct-complete")

    def test_timeout_audit_can_bind_report_and_review_without_other_role_reuse(self):
        data = self.validator.extract_handoff_contract(self.handoff, "handoff")
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            timeout = root / "timeout-audit.md"
            timeout.write_text(evidence_manifest("timeout-audit", "blocked"), encoding="utf-8")
            ref = {"path": timeout.name, "sha256": hashlib.sha256(timeout.read_bytes()).hexdigest()}
            data.update(
                lifecycle_state="blocked",
                contract_revision=2,
                attempt_report_artifact=dict(ref),
                last_review_result="blocked",
                last_review_artifact=dict(ref),
                blocked_reason="external agent timed out",
                blocker_owner="external-agent",
                resume_condition="timeout audit resolved",
                next_owner="codex-brief-antigravity-review",
            )
            self.validator.validate_handoff_contract(data, "timeout")
            self.validator.validate_evidence_artifacts(data, root, "timeout")

        conflicting = dict(data)
        conflicting["last_review_artifact"] = dict(data["last_review_artifact"])
        conflicting["last_review_artifact"]["sha256"] = "c" * 64
        with self.assertRaisesRegex(AssertionError, "distinct by role"):
            self.validator.validate_handoff_contract(conflicting, "timeout-conflict")

    def test_complete_rejects_preflight_review_as_batch_review_evidence(self):
        data = self.validator.extract_handoff_contract(self.handoff, "handoff")
        data.update(
            lifecycle_state="complete",
            current_batch=data["planned_batches"],
            contract_revision=5,
            last_review_result="pass",
            final_verification="pass",
            final_review_result="pass",
            next_owner="user",
        )
        specs = {
            "attempt_report_artifact": ("attempt.md", "attempt-report", "pass", 1),
            "last_review_artifact": ("preflight.md", "preflight-review", "pass", 2),
            "final_verification_artifact": ("verification.md", "final-verification", "pass", 3),
            "final_review_artifact": ("final-review.md", "final-review", "pass", 4),
        }
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for key, (path, role, result, revision) in specs.items():
                target = root / path
                target.write_text(
                    evidence_manifest(role, result, current_batch=2, contract_revision=revision),
                    encoding="utf-8",
                )
                data[key] = {"path": path, "sha256": hashlib.sha256(target.read_bytes()).hexdigest()}
            self.validator.validate_handoff_contract(data, "preflight-as-batch")
            with self.assertRaisesRegex(AssertionError, "evidence role|batch-review"):
                self.validator.validate_evidence_artifacts(data, root, "preflight-as-batch")

    def test_timeout_audit_is_blocked_only_and_cannot_satisfy_complete(self):
        data = self.validator.extract_handoff_contract(self.handoff, "handoff")
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            timeout = root / "timeout.md"
            timeout.write_text(evidence_manifest("timeout-audit", "pass"), encoding="utf-8")
            shared = {"path": timeout.name, "sha256": hashlib.sha256(timeout.read_bytes()).hexdigest()}
            data.update(
                lifecycle_state="complete",
                current_batch=data["planned_batches"],
                attempt_report_artifact=dict(shared),
                last_review_result="pass",
                last_review_artifact=dict(shared),
                final_verification="pass",
                final_verification_artifact=artifact("verification.md"),
                final_review_result="pass",
                final_review_artifact=artifact("final-review.md"),
                next_owner="user",
            )
            with self.assertRaisesRegex(AssertionError, "timeout-audit|distinct|blocked"):
                self.validator.validate_handoff_contract(data, "timeout-complete")

    def test_runtime_rejects_stale_batch_and_attempt_evidence(self):
        data = self._awaiting_contract()
        data.update(attempt=9, contract_revision=10)
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            specs = {
                "attempt_report_artifact": ("report.md", "attempt-report", 1),
                "last_review_artifact": ("review.md", "batch-review", 2),
            }
            for key, (path, role, revision) in specs.items():
                target = root / path
                target.write_text(
                    evidence_manifest(role, "pass", current_batch=1, attempt=1, contract_revision=revision),
                    encoding="utf-8",
                )
                data[key] = {"path": path, "sha256": hashlib.sha256(target.read_bytes()).hexdigest()}
            with self.assertRaisesRegex(AssertionError, "required batch|required attempt"):
                self.validator.validate_evidence_artifacts(data, root, "stale-evidence")

    def test_runtime_complete_requires_and_validates_previous_status(self):
        previous = self._awaiting_contract("pass")
        previous["contract_revision"] = 4
        current = dict(previous)
        current.update(
            lifecycle_state="complete",
            contract_revision=5,
            final_review_result="pass",
            final_review_artifact=artifact("final-review.md"),
            next_owner="user",
        )
        previous_bytes = b"canonical previous status revision 4\n"
        previous_sha = hashlib.sha256(previous_bytes).hexdigest()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            specs = {
                "attempt_report_artifact": ("report.md", "attempt-report", "pass", 1, "b" * 64),
                "last_review_artifact": ("batch-review.md", "batch-review", "pass", 2, "c" * 64),
                "final_verification_artifact": ("verification.md", "final-verification", "pass", 3, "d" * 64),
                "final_review_artifact": ("final-review.md", "final-review", "pass", 4, previous_sha),
            }
            for key, (path, role, result, revision, source_sha) in specs.items():
                target = root / path
                target.write_text(
                    evidence_manifest(
                        role,
                        result,
                        current_batch=2,
                        contract_revision=revision,
                        canonical_sha256=source_sha,
                    ),
                    encoding="utf-8",
                )
                current[key] = {"path": path, "sha256": hashlib.sha256(target.read_bytes()).hexdigest()}
            previous.update(
                attempt_report_artifact=current["attempt_report_artifact"],
                last_review_artifact=current["last_review_artifact"],
                final_verification_artifact=current["final_verification_artifact"],
            )
            with self.assertRaisesRegex(AssertionError, "requires previous canonical status"):
                self.validator.validate_evidence_artifacts(current, root, "complete-without-history")
            self.validator.validate_evidence_artifacts(
                current,
                root,
                "complete-with-history",
                previous=previous,
                previous_status_sha256=previous_sha,
            )

    def test_previous_status_binds_nonfinal_promotion_to_reviewed_attempt(self):
        previous = self.validator.extract_handoff_contract(self.handoff, "handoff")
        previous.update(
            lifecycle_state="ready-for-review",
            attempt=3,
            contract_revision=3,
            attempt_report_artifact=artifact("report.md"),
            next_owner="codex-brief-antigravity-review",
        )
        current = dict(previous)
        current.update(
            lifecycle_state="ready-for-brief",
            current_batch=2,
            attempt=1,
            contract_revision=4,
            last_review_result="pass",
            last_review_artifact=artifact("review.md"),
            next_owner="codex-brief-antigravity-review",
        )
        previous_sha = hashlib.sha256(b"reviewed attempt 3 status\n").hexdigest()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            report = root / "report.md"
            review = root / "review.md"
            report.write_text(
                evidence_manifest("attempt-report", "pass", attempt=2, contract_revision=1),
                encoding="utf-8",
            )
            review.write_text(
                evidence_manifest(
                    "batch-review",
                    "pass",
                    attempt=2,
                    contract_revision=3,
                    canonical_sha256=previous_sha,
                ),
                encoding="utf-8",
            )
            report_ref = {"path": report.name, "sha256": hashlib.sha256(report.read_bytes()).hexdigest()}
            review_ref = {"path": review.name, "sha256": hashlib.sha256(review.read_bytes()).hexdigest()}
            previous["attempt_report_artifact"] = report_ref
            current["attempt_report_artifact"] = report_ref
            current["last_review_artifact"] = review_ref
            with self.assertRaisesRegex(AssertionError, "wrong source attempt"):
                self.validator.validate_evidence_artifacts(
                    current,
                    root,
                    "wrong-attempt-promotion",
                    previous=previous,
                    previous_status_sha256=previous_sha,
                )

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

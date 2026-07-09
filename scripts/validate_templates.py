#!/usr/bin/env python3
"""Validate brief/review templates and the shared Handoff lifecycle."""
from __future__ import annotations

import re
import sys
from pathlib import Path

try:
    import yaml
except ModuleNotFoundError:  # The supported subset has a dependency-free fallback.
    yaml = None


START = "<!-- COOP_HANDOFF_CONTRACT_START -->"
END = "<!-- COOP_HANDOFF_CONTRACT_END -->"
SCHEMA_VERSION = 2
RISK_PROFILES = {"compact", "standard", "strict"}
BATCH_PROFILES = {"single", "cohesive", "staged"}
BUSINESS_ACCEPTANCE = {"required", "optional", "not-applicable"}
MODES = {
    "review-only", "discovery-first", "openspec-proposal",
    "approved-implementation", "direct-change", "self-evolution",
}
APPROVAL_STATUSES = {"not-required", "proposed", "approved", "blocked"}
EXECUTORS = {"codex", "external-agent"}
GOVERNORS = {"openspec-superpower-change", "codex-brief-antigravity-review"}
NEXT_OWNERS = {
    "openspec-superpower-change", "codex-brief-antigravity-review",
    "external-agent", "user",
}
LIFECYCLE_STATES = {
    "ready-for-brief", "ready-for-execution", "ready-for-review",
    "needs-fix", "blocked", "awaiting-final-verification", "complete",
}
REVIEW_RESULTS = {"not-run", "pass", "fail", "blocked"}
FINAL_VERIFICATION_RESULTS = {"pending", "pass", "fail", "blocked"}
FINAL_REVIEW_RESULTS = {"pending", "pass", "fail", "blocked"}
BLOCKER_OWNERS = {
    "none", "openspec-superpower-change", "codex-brief-antigravity-review",
    "external-agent", "user", "dependency",
}
ALLOWED_TRANSITIONS = {
    "ready-for-brief": {"ready-for-execution", "blocked"},
    "ready-for-execution": {"ready-for-review", "blocked"},
    "ready-for-review": {
        "needs-fix", "blocked", "ready-for-brief",
        "awaiting-final-verification",
    },
    "needs-fix": {"ready-for-execution", "blocked"},
    "blocked": {
        "ready-for-brief", "ready-for-execution", "ready-for-review",
        "needs-fix", "blocked",
    },
    "awaiting-final-verification": {"complete", "needs-fix", "blocked"},
    "complete": set(),
}
IMMUTABLE_FIELDS = {
    "schema_version", "change_id", "mode", "approval_status", "risk_profile",
    "batch_profile", "planned_batches", "executor", "governor",
    "step_critical", "final_critical", "business_acceptance",
    "stop_conditions", "verification_strategy", "readonly_fields",
}


def parse_scalar(value: str):
    value = value.strip()
    if (value.startswith('"') and value.endswith('"')) or (
        value.startswith("'") and value.endswith("'")
    ):
        return value[1:-1]
    lowered = value.lower()
    if lowered in {"true", "false"}:
        return lowered == "true"
    if lowered in {"null", "~"}:
        return None
    if re.fullmatch(r"-?\d+", value):
        return int(value)
    return value


def simple_yaml_load(text: str) -> dict:
    result: dict = {}
    current_key: str | None = None
    for raw in text.splitlines():
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        indent = len(raw) - len(raw.lstrip(" "))
        line = raw.strip()
        if indent == 0 and not line.startswith("- "):
            if ":" not in line:
                continue
            key, value = line.split(":", 1)
            key = key.strip()
            if value.strip():
                result[key] = parse_scalar(value)
                current_key = None
            else:
                result[key] = {}
                current_key = key
        elif indent == 2 and current_key and line.startswith("- "):
            if not isinstance(result[current_key], list):
                result[current_key] = []
            result[current_key].append(parse_scalar(line[2:]))
        elif indent == 2 and current_key and ":" in line:
            if not isinstance(result[current_key], dict):
                result[current_key] = {}
            key, value = line.split(":", 1)
            result[current_key][key.strip()] = parse_scalar(value)
    return result


def yaml_load(text: str):
    return yaml.safe_load(text) if yaml is not None else simple_yaml_load(text)


def read(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise AssertionError(f"missing required file: {path}") from exc


def require(text: str, needle: str, label: str) -> None:
    if needle not in text:
        raise AssertionError(f"{label}: missing required text: {needle!r}")


def extract_handoff_contract(text: str, label: str) -> dict:
    if text.count(START) != 1 or text.count(END) != 1:
        raise AssertionError(f"{label}: handoff contract must have exactly one marker block")
    body = text.split(START, 1)[1].split(END, 1)[0].strip()
    if body.startswith("```yaml"):
        body = body.removeprefix("```yaml").strip()
    if body.endswith("```"):
        body = body[:-3].strip()
    data = yaml_load(body)
    if not isinstance(data, dict):
        raise AssertionError(f"{label}: handoff contract must be a YAML mapping")
    return data


def _require_positive_int(data: dict, key: str, label: str) -> None:
    if not isinstance(data[key], int) or data[key] < 1:
        raise AssertionError(f"{label}: {key} must be a positive integer")


def validate_handoff_contract(data: dict, label: str) -> None:
    required = {
        "schema_version", "change_id", "mode", "approval_status",
        "risk_profile", "batch_profile", "current_batch", "planned_batches",
        "attempt", "contract_revision", "lifecycle_state",
        "last_review_result", "blocked_reason", "blocker_owner",
        "resume_condition", "final_verification", "final_review_result",
        "executor", "governor",
        "next_owner", "step_critical", "final_critical",
        "business_acceptance", "stop_conditions", "verification_strategy",
        "readonly_fields",
    }
    missing = sorted(required - set(data))
    if missing:
        raise AssertionError(f"{label}: missing contract fields: {missing}")
    if data["schema_version"] != SCHEMA_VERSION:
        raise AssertionError(f"{label}: schema_version must be {SCHEMA_VERSION}")
    enums = {
        "mode": MODES,
        "approval_status": APPROVAL_STATUSES,
        "risk_profile": RISK_PROFILES,
        "batch_profile": BATCH_PROFILES,
        "executor": EXECUTORS,
        "governor": GOVERNORS,
        "next_owner": NEXT_OWNERS,
        "lifecycle_state": LIFECYCLE_STATES,
        "last_review_result": REVIEW_RESULTS,
        "blocker_owner": BLOCKER_OWNERS,
        "final_verification": FINAL_VERIFICATION_RESULTS,
        "final_review_result": FINAL_REVIEW_RESULTS,
    }
    for key, allowed in enums.items():
        if data[key] not in allowed:
            raise AssertionError(f"{label}: invalid {key}")
    for key in ("current_batch", "planned_batches", "attempt", "contract_revision"):
        _require_positive_int(data, key, label)
    if data["current_batch"] > data["planned_batches"]:
        raise AssertionError(f"{label}: current_batch must not exceed planned_batches")
    if not isinstance(data["change_id"], str) or not re.fullmatch(
        r"[a-z0-9]+(?:-[a-z0-9]+)*", data["change_id"]
    ):
        raise AssertionError(f"{label}: change_id must be a path-safe kebab-case slug")
    if data["executor"] != "external-agent" or data["governor"] != "codex-brief-antigravity-review":
        raise AssertionError(f"{label}: execution contract requires external-agent executor and brief governor")
    if data["mode"] not in {"approved-implementation", "direct-change", "self-evolution"}:
        raise AssertionError(f"{label}: execution contract has invalid mode")
    if data["mode"] in {"approved-implementation", "self-evolution"} and data["approval_status"] != "approved":
        raise AssertionError(f"{label}: execution contract must be approved")
    if data["mode"] == "direct-change" and data["approval_status"] not in {"not-required", "approved"}:
        raise AssertionError(f"{label}: direct-change execution contract has invalid approval")
    acceptance = data["business_acceptance"]
    if not isinstance(acceptance, dict):
        raise AssertionError(f"{label}: business_acceptance must be a mapping")
    for key in ("unit", "pipeline", "api", "real_business"):
        if acceptance.get(key) not in BUSINESS_ACCEPTANCE:
            raise AssertionError(f"{label}: invalid business_acceptance.{key}")
    for key in ("step_critical", "final_critical"):
        if not isinstance(data[key], list) or not all(isinstance(item, str) for item in data[key]):
            raise AssertionError(f"{label}: {key} must be a string list")
        if data["risk_profile"] in {"standard", "strict"} and not data[key]:
            raise AssertionError(f"{label}: {key} must be a non-empty string list")
    if not isinstance(data["stop_conditions"], list) or not data["stop_conditions"] or not all(
        isinstance(item, str) for item in data["stop_conditions"]
    ):
        raise AssertionError(f"{label}: stop_conditions must be a non-empty string list")
    strategy = data["verification_strategy"]
    if not isinstance(strategy, dict) or not all(
        isinstance(strategy.get(key), str) and strategy[key]
        for key in ("step", "final")
    ):
        raise AssertionError(f"{label}: verification_strategy must be a step/final string mapping")
    readonly = data["readonly_fields"]
    expected_readonly = IMMUTABLE_FIELDS
    if not isinstance(readonly, list) or not expected_readonly.issubset(readonly):
        raise AssertionError(f"{label}: readonly_fields is incomplete")

    state = data["lifecycle_state"]
    expected_owners = {
        "ready-for-brief": {"codex-brief-antigravity-review"},
        "ready-for-execution": {"external-agent"},
        "ready-for-review": {"codex-brief-antigravity-review"},
        "needs-fix": {"codex-brief-antigravity-review", "openspec-superpower-change"},
        "blocked": NEXT_OWNERS,
        "awaiting-final-verification": {"openspec-superpower-change"},
        "complete": {"user"},
    }
    if data["next_owner"] not in expected_owners[state]:
        raise AssertionError(f"{label}: invalid next_owner for {state}")
    if state != "blocked" and any(
        data[key] not in {None, "none"}
        for key in ("blocked_reason", "blocker_owner", "resume_condition")
    ):
        raise AssertionError(f"{label}: non-blocked state must clear blocker fields")
    if state in {"ready-for-execution", "ready-for-review"} and data["last_review_result"] != "not-run":
        raise AssertionError(f"{label}: active attempt requires last_review_result not-run")
    if state in {"ready-for-brief", "ready-for-execution", "ready-for-review"} and (
        data["final_verification"] != "pending" or data["final_review_result"] != "pending"
    ):
        raise AssertionError(f"{label}: pre-final states require pending final gates")
    if state == "needs-fix" and data["last_review_result"] != "fail":
        raise AssertionError(f"{label}: needs-fix requires fail review")
    if state == "blocked":
        if data["last_review_result"] != "blocked":
            raise AssertionError(f"{label}: blocked review result is required")
        if data["blocker_owner"] == "none" or data["blocked_reason"] in {None, "none"}:
            raise AssertionError(f"{label}: blocked requires blocker owner and reason")
        if data["resume_condition"] in {None, "none"}:
            raise AssertionError(f"{label}: blocked requires resume_condition")
    if state == "awaiting-final-verification":
        if data["current_batch"] != data["planned_batches"]:
            raise AssertionError(f"{label}: awaiting-final-verification requires final batch")
        if (
            data["last_review_result"] != "pass"
            or data["final_verification"] != "pending"
            or data["final_review_result"] != "pending"
        ):
            raise AssertionError(f"{label}: awaiting-final-verification requires batch review pass and pending final gates")
        if data["next_owner"] != "openspec-superpower-change":
            raise AssertionError(f"{label}: awaiting-final-verification must return to router")
    if state == "complete":
        if data["current_batch"] != data["planned_batches"]:
            raise AssertionError(f"{label}: complete requires final batch")
        if (
            data["last_review_result"] != "pass"
            or data["final_verification"] != "pass"
            or data["final_review_result"] != "pass"
        ):
            raise AssertionError(f"{label}: complete requires batch review, final review, and final verification pass")
        if data["next_owner"] != "user":
            raise AssertionError(f"{label}: complete requires next_owner user")
    elif data["final_verification"] == "pass" or data["final_review_result"] == "pass":
        raise AssertionError(f"{label}: final pass results are valid only when complete")


def validate_transition(before: dict, after: dict, label: str) -> None:
    validate_handoff_contract(before, f"{label}:before")
    validate_handoff_contract(after, f"{label}:after")
    if before["lifecycle_state"] == "complete":
        raise AssertionError(f"{label}: complete is terminal")
    for key in IMMUTABLE_FIELDS:
        if before[key] != after[key]:
            raise AssertionError(f"{label}: readonly field changed: {key}")
    if after["contract_revision"] != before["contract_revision"] + 1:
        raise AssertionError(f"{label}: contract_revision must increment by one")
    current_state = before["lifecycle_state"]
    next_state = after["lifecycle_state"]
    if next_state not in ALLOWED_TRANSITIONS[current_state]:
        raise AssertionError(f"{label}: invalid lifecycle transition")
    special_attempt_transitions = {
        ("ready-for-review", "needs-fix"),
        ("ready-for-review", "ready-for-brief"),
        ("awaiting-final-verification", "needs-fix"),
    }
    if current_state == "blocked" and next_state != "blocked":
        special_attempt_transitions.add((current_state, next_state))
    if (current_state, next_state) not in special_attempt_transitions:
        if after["current_batch"] != before["current_batch"] or after["attempt"] != before["attempt"]:
            raise AssertionError(f"{label}: transition must keep the same batch and attempt")
    if next_state in {"needs-fix", "blocked"} and after["current_batch"] != before["current_batch"]:
        raise AssertionError(f"{label}: FAIL/BLOCKED must stay on the same batch")
    if next_state == "needs-fix":
        if after["attempt"] != before["attempt"] + 1:
            raise AssertionError(f"{label}: FAIL must increment attempt")
        if after["last_review_result"] != "fail":
            raise AssertionError(f"{label}: needs-fix requires fail review")
    if current_state == "blocked" and next_state != "blocked":
        if after["current_batch"] != before["current_batch"]:
            raise AssertionError(f"{label}: resumed work must stay on the same batch")
        if after["attempt"] != before["attempt"] + 1:
            raise AssertionError(f"{label}: resumed work must use a fresh attempt")
    if current_state == "ready-for-review" and next_state == "ready-for-brief":
        if before["current_batch"] >= before["planned_batches"]:
            raise AssertionError(f"{label}: final PASS must hand back to router")
        if after["current_batch"] != before["current_batch"] + 1 or after["attempt"] != 1:
            raise AssertionError(f"{label}: non-final PASS must advance one batch and reset attempt")
        if after["last_review_result"] != "pass":
            raise AssertionError(f"{label}: batch advance requires Review PASS")
    if next_state == "awaiting-final-verification":
        if before["current_batch"] != before["planned_batches"]:
            raise AssertionError(f"{label}: only final batch can hand back")
        if after["current_batch"] != before["current_batch"]:
            raise AssertionError(f"{label}: final handback keeps the same batch")


def validate_frontmatter(skill: str) -> None:
    if not skill.startswith("---\n"):
        raise AssertionError("SKILL.md: missing YAML frontmatter")
    parts = skill.split("---\n", 2)
    keys = [
        line.split(":", 1)[0].strip()
        for line in parts[1].splitlines()
        if line.strip() and not line.startswith(" ") and ":" in line
    ]
    if keys != ["name", "description"]:
        raise AssertionError(f"SKILL.md: frontmatter keys must be name, description only; got {keys}")


def main(argv: list[str] | None = None) -> int:
    argv = sys.argv if argv is None else argv
    root = Path(argv[1]).resolve() if len(argv) > 1 else Path.cwd().resolve()
    print(f"[i] Validating project layout in: {root}")
    for directory in ("agents", "references", "scripts"):
        if not (root / directory).is_dir():
            raise AssertionError(f"missing directory: {root / directory}")

    skill = read(root / "SKILL.md")
    metadata = yaml_load(read(root / "agents" / "openai.yaml"))
    validate_frontmatter(skill)
    interface = metadata.get("interface") if isinstance(metadata, dict) else None
    if not isinstance(interface, dict):
        raise AssertionError("agents/openai.yaml: missing interface mapping")
    for field in ("display_name", "short_description", "default_prompt"):
        if field not in interface:
            raise AssertionError(f"agents/openai.yaml: missing interface.{field}")
    if "$codex-brief-antigravity-review" not in str(interface["default_prompt"]):
        raise AssertionError("agents/openai.yaml: default_prompt must mention the skill")
    if metadata.get("policy", {}).get("allow_implicit_invocation") is not True:
        raise AssertionError("agents/openai.yaml: implicit invocation must remain enabled")

    required_templates = {
        "brief-template.md": (
            "Canonical Handoff Contract", "attempt-<AA>", "contract_revision",
            "函数级变更地图", "业务验收标准", "外部 Agent 不得修改 canonical",
        ),
        "report-template.md": (
            "Execution Report", "Attempt <AA>", "Canonical status path",
            "建议状态", "外部 Agent 不得直接编辑 canonical",
        ),
        "review-template.md": (
            "# Review Result: PASS / FAIL / BLOCKED", "Required State Transition",
            "needs-fix", "resume_condition", "must be reviewed again",
            "awaiting-final-verification",
        ),
        "agy-dispatch-template.md": (
            "attempt-<AA>", "Canonical status", "不得修改 canonical status",
        ),
        "timeout-audit-template.md": (
            "Attempt <AA>", "resume_condition", "fresh Review",
        ),
    }
    for filename, needles in required_templates.items():
        text = read(root / "references" / filename)
        for needle in needles:
            require(text, needle, filename)

    for needle in (
        "Standalone Lightweight", "Handed-off External Execution",
        "Review and fix", "attempt-<AA>", "same batch", "needs-fix",
        "awaiting-final-verification", "openspec-superpower-change",
        "temporary structured backup", "Major Self-Evolution",
    ):
        require(skill, needle, "SKILL.md")

    handoff_text = read(root / "references" / "handoff-contract.md")
    contract = extract_handoff_contract(handoff_text, "handoff-contract.md")
    validate_handoff_contract(contract, "handoff-contract.md")
    require(handoff_text, "must not embed another mutable block", "handoff-contract.md")
    print("[✓] Validation succeeded: templates and lifecycle are compliant")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except AssertionError as exc:
        print(f"Validation failed: {exc}", file=sys.stderr)
        raise SystemExit(1)

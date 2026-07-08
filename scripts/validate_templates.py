#!/usr/bin/env python3
import os
import sys
try:
    import yaml
except ModuleNotFoundError:  # pragma: no cover - exercised when PyYAML is absent
    yaml = None

START = "<!-- COOP_HANDOFF_CONTRACT_START -->"
END = "<!-- COOP_HANDOFF_CONTRACT_END -->"
RISK_PROFILES = {"compact", "standard", "strict"}
BATCH_PROFILES = {"single", "cohesive", "staged"}
BUSINESS_ACCEPTANCE = {"required", "optional", "not-applicable"}
MODES = {
    "review-only",
    "discovery-first",
    "openspec-proposal",
    "approved-implementation",
    "direct-change",
    "self-evolution",
}
APPROVAL_STATUSES = {"not-required", "proposed", "approved", "blocked"}
EXECUTORS = {"codex", "external-agent"}
GOVERNORS = {"codex", "codex-brief-antigravity-review"}
NEXT_OWNERS = {"codex", "codex-brief-antigravity-review", "external-agent", "user"}

def parse_scalar(value):
    value = value.strip()
    if (value.startswith('"') and value.endswith('"')) or (value.startswith("'") and value.endswith("'")):
        return value[1:-1]
    if value.isdigit():
        return int(value)
    return value

def simple_yaml_load(text):
    result = {}
    current_key = None
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

def yaml_load(text):
    if yaml is not None:
        return yaml.safe_load(text)
    return simple_yaml_load(text)

def check_file_exists(filepath):
    if not os.path.exists(filepath):
        print(f"[-] Error: File not found -> {filepath}")
        return False
    print(f"[+] Found: {filepath}")
    return True

def extract_handoff_contract(text, label):
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

def validate_handoff_contract(data, label):
    required = {
        "schema_version", "change_id", "mode", "approval_status", "risk_profile",
        "batch_profile", "current_batch", "planned_batches", "executor",
        "governor", "next_owner", "step_critical", "final_critical",
        "business_acceptance", "stop_conditions", "verification_strategy",
    }
    missing = sorted(required - set(data))
    if missing:
        raise AssertionError(f"{label}: missing contract fields: {missing}")
    if data["mode"] not in MODES:
        raise AssertionError(f"{label}: invalid mode")
    if data["approval_status"] not in APPROVAL_STATUSES:
        raise AssertionError(f"{label}: invalid approval_status")
    if data["risk_profile"] not in RISK_PROFILES:
        raise AssertionError(f"{label}: invalid risk_profile")
    if data["batch_profile"] not in BATCH_PROFILES:
        raise AssertionError(f"{label}: invalid batch_profile")
    if data["executor"] not in EXECUTORS:
        raise AssertionError(f"{label}: invalid executor")
    if data["governor"] not in GOVERNORS:
        raise AssertionError(f"{label}: invalid governor")
    if data["next_owner"] not in NEXT_OWNERS:
        raise AssertionError(f"{label}: invalid next_owner")
    if int(data["current_batch"]) < 1 or int(data["current_batch"]) > int(data["planned_batches"]):
        raise AssertionError(f"{label}: current_batch must be between 1 and planned_batches")
    acceptance = data["business_acceptance"]
    for key in ("unit", "pipeline", "api", "real_business"):
        if key not in acceptance:
            raise AssertionError(f"{label}: missing business_acceptance.{key}")
        if acceptance[key] not in BUSINESS_ACCEPTANCE:
            raise AssertionError(f"{label}: invalid business_acceptance.{key}")
    if data["risk_profile"] in {"standard", "strict"}:
        for key in ("step_critical", "final_critical"):
            if not isinstance(data[key], list) or not data[key] or not all(isinstance(item, str) for item in data[key]):
                raise AssertionError(f"{label}: {key} must be a non-empty string list")

def main():
    project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    print(f"[i] Validating project layout in: {project_dir}")

    # 1. Check folder structures
    required_dirs = ["agents", "references", "scripts"]
    for d in required_dirs:
        dir_path = os.path.join(project_dir, d)
        if not os.path.isdir(dir_path):
            print(f"[-] Error: Missing directory -> {dir_path}")
            sys.exit(1)
        print(f"[+] Directory exists: {d}/")

    # 2. Check metadata configs
    skill_md = os.path.join(project_dir, "SKILL.md")
    openai_yaml = os.path.join(project_dir, "agents/openai.yaml")

    if not check_file_exists(skill_md) or not check_file_exists(openai_yaml):
        sys.exit(1)

    # Validate SKILL.md frontmatter
    try:
        with open(skill_md, "r", encoding="utf-8") as f:
            content = f.read()
            if not content.startswith("---"):
                print("[-] Error: SKILL.md does not start with YAML frontmatter ---")
                sys.exit(1)
            parts = content.split("---")
            if len(parts) < 3:
                print("[-] Error: SKILL.md has invalid frontmatter blocks")
                sys.exit(1)
            frontmatter = yaml_load(parts[1])
            print(f"[+] SKILL.md Frontmatter validated. Skill Name: {frontmatter.get('name')}")
    except Exception as e:
        print(f"[-] Error parsing SKILL.md frontmatter: {e}")
        sys.exit(1)

    # Validate openai.yaml
    try:
        with open(openai_yaml, "r", encoding="utf-8") as f:
            meta = yaml_load(f.read())
            interface = meta.get("interface") if isinstance(meta, dict) else None
            if not isinstance(interface, dict):
                raise AssertionError("missing interface mapping")
            required_interface = {"display_name", "short_description", "default_prompt"}
            missing_interface = sorted(required_interface - set(interface))
            if missing_interface:
                raise AssertionError(f"missing interface fields: {missing_interface}")
            if "$codex-brief-antigravity-review" not in str(interface["default_prompt"]):
                raise AssertionError("default_prompt must explicitly mention the skill")
            policy = meta.get("policy", {})
            if policy.get("allow_implicit_invocation", True) is not True:
                raise AssertionError("implicit invocation must remain enabled")
            print(f"[+] agents/openai.yaml validated. Display Name: {interface['display_name']}")
            for required_text in [
                "temporary structured backup",
                "remove temporary backups",
                "Long-term history is managed",
            ]:
                if required_text not in content:
                    raise AssertionError(f"SKILL.md missing backup lifecycle text: {required_text}")
    except Exception as e:
        print(f"[-] Error parsing agents/openai.yaml: {e}")
        sys.exit(1)

    # 3. Check reference templates
    required_templates = [
        "brief-template.md",
        "report-template.md",
        "review-template.md",
        "agy-dispatch-template.md",
        "timeout-audit-template.md",
        "handoff-contract.md"
    ]
    for tmpl in required_templates:
        tmpl_path = os.path.join(project_dir, "references", tmpl)
        if not check_file_exists(tmpl_path):
            sys.exit(1)

    # 4. Check specific contents in timeout-audit-template.md
    timeout_path = os.path.join(project_dir, "references", "timeout-audit-template.md")
    try:
        with open(timeout_path, "r", encoding="utf-8") as f:
            timeout_content = f.read()
        required_sections = [
            "文档类型：Timeout Audit",
            "## 结论",
            "## Review 范围",
            "## 验证记录",
            "## 后续门禁"
        ]
        for sec in required_sections:
            if sec not in timeout_content:
                print(f"[-] Error: timeout-audit-template.md is missing required section '{sec}'")
                sys.exit(1)
        print("[+] timeout-audit-template.md content validated.")
    except Exception as e:
        print(f"[-] Error checking timeout-audit-template.md contents: {e}")
        sys.exit(1)


    # 5. Check audit hardening content in core templates
    template_requirements = {
        "brief-template.md": [
            "Handoff Contract",
            "compact / standard / strict",
            "函数级变更地图",
            "数据合同",
            "不变量与错误矩阵",
            "TDD 与生产 wiring",
            "## 5. Git / 工作区硬约束",
            "## 10. 业务验收标准",
            "## 11. Key Assertions",
            "## 12. 阻塞处理",
            "pytest 通过不能替代业务链路通过",
            "备份仅用于失败回滚",
            "历史版本通过 `/Users/elvis/file/develop/opensource/openspec-superpower-change`",
        ],
        "report-template.md": [
            "PASS / FAIL / BLOCKED",
            "Handoff Contract Fingerprint",
            "## Git / 工作区状态",
            "## Evidence",
            "### Commands",
            "### Artifacts",
            "### Key Assertions",
            "## 业务验收分层",
            "## 子问题覆盖矩阵",
        ],
        "review-template.md": [
            "# Review Result: PASS / FAIL / BLOCKED",
            "Contract Consensus",
            "## Summary",
            "## Findings",
            "## Required Fixes",
            "## Verification",
            "## Final Decision",
            "Brief 要求 server/API/真实业务回归，而 Report 只有 pytest 证据",
        ],
    }
    for tmpl, needles in template_requirements.items():
        path = os.path.join(project_dir, "references", tmpl)
        with open(path, "r", encoding="utf-8") as f:
            text = f.read()
        for needle in needles:
            if needle not in text:
                print(f"[-] Error: {tmpl} is missing required audit text {needle!r}")
                sys.exit(1)
        print(f"[+] {tmpl} audit hardening content validated.")

    # 6. Check Handoff Contract schema and role boundaries
    handoff_path = os.path.join(project_dir, "references", "handoff-contract.md")
    with open(handoff_path, "r", encoding="utf-8") as f:
        handoff_text = f.read()
    validate_handoff_contract(extract_handoff_contract(handoff_text, "handoff-contract.md"), "handoff-contract.md")
    for needle in [
        "Do not invent or overwrite `mode`, `approval_status`, or `risk_profile`",
        "Unit tests do not imply API/server/business-chain success",
        "current_batch",
        "planned_batches",
    ]:
        if needle not in handoff_text:
            print(f"[-] Error: handoff-contract.md is missing required text {needle!r}")
            sys.exit(1)
    print("[+] handoff-contract.md schema and boundary content validated.")

    print("\n[✓] Validation Succeeded: The skill structure is fully complete and compliant!")

if __name__ == "__main__":
    main()

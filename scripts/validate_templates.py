#!/usr/bin/env python3
import os
import sys
import yaml

def check_file_exists(filepath):
    if not os.path.exists(filepath):
        print(f"[-] Error: File not found -> {filepath}")
        return False
    print(f"[+] Found: {filepath}")
    return True

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
            frontmatter = yaml.safe_load(parts[1])
            print(f"[+] SKILL.md Frontmatter validated. Skill Name: {frontmatter.get('name')}")
    except Exception as e:
        print(f"[-] Error parsing SKILL.md frontmatter: {e}")
        sys.exit(1)

    # Validate openai.yaml
    try:
        with open(openai_yaml, "r", encoding="utf-8") as f:
            meta = yaml.safe_load(f)
            print(f"[+] agents/openai.yaml validated. Display Name: {meta.get('display_name')}")
    except Exception as e:
        print(f"[-] Error parsing agents/openai.yaml: {e}")
        sys.exit(1)

    # 3. Check reference templates
    required_templates = [
        "brief-template.md",
        "report-template.md",
        "review-template.md",
        "agy-dispatch-template.md",
        "timeout-audit-template.md"
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
            "## 5. Git / 工作区硬约束",
            "## 10. 业务验收标准",
            "## 11. Key Assertions",
            "## 12. 阻塞处理",
            "pytest 通过不能替代业务链路通过",
        ],
        "report-template.md": [
            "PASS / FAIL / BLOCKED",
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

    print("\n[✓] Validation Succeeded: The skill structure is fully complete and compliant!")

if __name__ == "__main__":
    main()

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

    print("\n[✓] Validation Succeeded: The skill structure is fully complete and compliant!")

if __name__ == "__main__":
    main()

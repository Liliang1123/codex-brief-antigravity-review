# AGENTS.md

## Project positioning

`codex-brief-antigravity-review` is an open-source, reusable Codex skill designed to govern the collaboration between planning-focused orchestrators (like Codex) and execution-focused command-line agents (like Antigravity CLI).

## Required behavior for agents

- Read `SKILL.md` before changing this project.
- Do not modify files in `references/` or `agents/` without updating `SKILL.md` or explaining the changes.
- Test the templates for formatting consistency before completing changes.
- Never execute `git add` or `git commit` on behalf of the user. Leave the staging and committing to the human reviewer.
- Ensure any self-evolution changes to this skill do not bypass or weaken the quality control loop (Brief -> Dispatch -> Report -> Review).

## Validation

Run the following checklist before finalizing changes:
1. Ensure all Mermaid diagram syntaxes inside `SKILL.md` or templates are valid.
2. Confirm the YAML frontmatter in `SKILL.md` contains accurate name, description, and trigger mappings.
3. Validate that `agents/openai.yaml` matches the configurations defined in `SKILL.md`.

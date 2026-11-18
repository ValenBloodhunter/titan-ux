---
name: titan-verify
description: "Run full-stack static anti-slop/a11y/perf checks, route-graph analysis, build checks, and headless Playwright QA. Usage: /titan-verify [url-or-path]"
---

# `/titan-verify`

Resolve the Titan-UX base directory (first try the checkout root containing `../../SKILL.md`, then `../titan-ux/`, `~/.gemini/config/skills/titan-ux/`, `~/.gemini/antigravity/skills/titan-ux/`, `~/.claude/skills/titan-ux/`, `~/.codex/skills/titan-ux/`, `~/.agents/skills/titan-ux/`, `~/.cursor/skills/titan-ux/`), read **only** `## Command I` in `references/command_playbooks.md` plus its permitted references, and execute it for `$ARGUMENTS`.

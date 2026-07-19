# BUILD_STATUS — MultiAgents-Powerhouse (Meta)

Tracks the shipping status of MultiAgents-Powerhouse itself: skills, MCPs, infrastructure, and documentation.

> **Rule:** Only update this file on `main` after a PR is merged — never on a feature branch.

---

## Layer 1 — Infrastructure & Workflow Setup

- [x] Define repo structure (mcps/ + skills/)
- [x] Write root CLAUDE.md with auto-routing and hard rules
- [x] Create `.internal/.claude/agents/` — PM Tech Lead, Research Engineer, Dev Engineer, QA Engineer
- [x] Create `.internal/.claude/skills/powerhouse-software-team/SKILL.md` — unified /pst command
- [x] Create `.internal/.claude/hooks/warn-missing-specs.sh` — advisory spec-gate hook (check-gstack.sh removed in repo cleanup — external-install gate dropped)
- [x] Write TECH_SPEC.md for investment-brain (required before Layer 1 of that sub-project)

---

## Layer 2 — Skills: Core Shipping

- [x] `Powerhouse-Claud-Project-Setup-Kit` — shipped
- [x] `Powerhouse-Prompt-Optimizer` — shipped
- [x] `Powerhouse-Resume-Specialist` — shipped
- [x] `Powerhouse-software-team` — shipped (CLI target)
- [x] `Powerhouse-software-team` — monorepo improvements (--project flag, CWD detection) merged back

---

## Layer 3 — MCP Servers: Core Shipping

- [x] `market-intelligence` — shipped (US/India/Canada markets)
- [x] `investment-brain` — Layer 1 (Types & Config) complete
- [x] `investment-brain` — Layer 2 (Services) complete
- [x] `investment-brain` — Layer 3 (Scorer + Deal-breaker) complete
- [x] `investment-brain` — Layer 4 (Paper Trading) complete
- [x] `investment-brain` — Layer 5 (MCP Bridge + Prompt Builder) complete
- [x] `investment-brain` — Layer 6 (CLI) complete
- [x] `investment-brain` — Layer 7 (Integration & Polish) complete

---

## Layer 4 — Documentation

- [x] Root README.md — restructured with CLI / Multi-Target / MCP sections
- [x] `skills/README.md` — CLI vs multi-target labels added
- [x] `skills/Powerhouse-software-team/README.md` — monorepo usage guide added
- [x] `mcps/market-intelligence/` — TECH_SPEC.md written retrospectively
- [x] GitHub releases — v1.0 tag for market-intelligence

---

## Layer 5 — Distribution & Discovery

- [x] GitHub topics set (mcp, claude, ai-tools, finance, skills)
- [x] `skills/` installable from GitHub raw URL documented
- [x] `mcps/` installable via uvx / pip documented
- [x] Demo GIF or screenshot in root README

---

## Layer 6 — Merger: development-protocols → MultiAgents-Powerhouse

- [x] Phase 1: Create directory structure (cli/, templates/, .agents/)
- [x] Phase 1: Copy CLI scripts from development-protocols (cli.js, init.js, apply.js)
- [x] Phase 1: Copy templates (workflow, stacks/expo, addons/firebase/stripe/opencode-ai)
- [x] Phase 1: Create .agents/ as cross-tool alias (OpenCode, Kimi, Cursor compatible)
- [x] Phase 2: Add advisor.md agent from development-protocols
- [x] Phase 2: Copy CI/CD and Husky templates
- [x] Phase 2: Copy session tracking scripts (save.sh, restore.sh)
- [x] Phase 3: Update package.json (rename to MultiAgents-Powerhouse, bin entry, keywords)
- [x] Phase 3: Update CLI branding (cli.js, init.js, apply.js)
- [x] Phase 4: Update README.md with unified docs (CLI + agent pipeline + multi-tool)
- [x] Phase 4: Create TECH_SPEC.md for the merger
- [x] Phase 5: Test CLI commands (init, apply) — manual testing in temp directory
- [x] Phase 5: Test /powerhouse skill commands — verify no regressions

---

## Layer 7 — Powerhouse Software Team (PST) Compliance

- [x] PST compliance audit (6 gaps identified)
- [x] `.internal/.powerhouse/lib/` scripts (detect-project.sh, pst-status.sh, pst-next.sh)
- [x] `.internal/.claude/commands/` — 7 PST slash commands (pst-status through pst-next)
- [x] `.internal/.claude/settings.json` — 3 hooks registered (spec-gate, branch-name, commit-msg); gstack hook removed in repo cleanup
- [x] `.internal/.opencode/commands/follow-ticket.md` — dispatcher command
- [x] `templates/workflow/` — opencode.json, settings.json, follow-ticket.md
- [x] AGENTS.md monorepo status conflict fixed
- [x] PR #6 merged: `feature/powerhouse/L7-pst-compliance`

---

## Layer 8 — Multi-Model Architecture (OpenCode Go Plan)

- [x] 6 agent definitions (`.opencode/agents/`) — zero hardcoded models
- [x] Base `opencode.json` — no model fields (survives model deprecation)
- [x] `opencode.go.json` — Go plan overlay with per-agent model routing
- [x] Templates for new installs (templates/workflow/)
- [x] AGENTS.md — documents Go plan activation and quota table
- [x] PR #7 merged: `feature/powerhouse/L8-model-routing`

### Model Routing

See `opencode.go.json` for specific model assignments and `AGENTS.md` for the routing rationale.

### Activate

```bash
cp opencode.go.json opencode.json
```

---

## Notes

- `market-intelligence` is exempt from spec-gate (shipped before spec discipline was established)
- Branch naming: `feature/{subproject}/L{N}-{description}` — sub-project + layer both visible (e.g. `feature/powerhouse/L1-branch-convention`)
- Recovery: `git diff main...HEAD --stat` + this file = full context after session reset


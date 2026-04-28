# BUILD_STATUS — Claude-Powerhouse (Meta)

Tracks the shipping status of Claude-Powerhouse itself: skills, MCPs, infrastructure, and documentation.

> **Rule:** Only update this file on `main` after a PR is merged — never on a feature branch.

---

## Layer 1 — Infrastructure & Workflow Setup

- [x] Define repo structure (mcps/ + skills/)
- [x] Write root CLAUDE.md with auto-routing and hard rules
- [x] Create `.claude/agents/` — PM Tech Lead, Research Engineer, Dev Engineer, QA Engineer
- [x] Create `.claude/skills/powerhouse/SKILL.md` — unified /powerhouse command
- [x] Create `.claude/hooks/check-gstack.sh` — gstack install gate
- [x] Create `.claude/hooks/warn-missing-specs.sh` — advisory spec-gate hook
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

## Notes

- `market-intelligence` is exempt from spec-gate (shipped before spec discipline was established)
- Branch naming: `feature/{subproject}/L{N}-{description}` — sub-project + layer both visible (e.g. `feature/powerhouse/L1-branch-convention`)
- Recovery: `git diff main...HEAD --stat` + this file = full context after session reset

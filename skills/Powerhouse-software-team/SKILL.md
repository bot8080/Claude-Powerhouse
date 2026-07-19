---
name: powerhouse-software-team
description: |
  Full AI software development team — PM plans, Dev builds, QA reviews.
  Use this skill when the user wants to build software with a structured pipeline, needs a PM → Dev → QA workflow, asks for spec-first development, layer-gated builds, or mentions wanting an AI dev team. Triggers include: "build me a feature", "set up a dev team pipeline", "plan then build then review", "spec-first development", "layered build order", "I need PM Dev QA agents", "agent pipeline for software", or any mention of structured software development with role separation. Also trigger when the user asks for ticket-based development, build status tracking, or context recovery across sessions.
  Spec-first, layer-gated, 7-point QA validation, context recovery.
  Commands: /pst status, /pst plan, /pst build, /pst review, /pst branch, /pst pr, /pst next
compatibility: claude-code, opencode, kimi-code
---

# Powerhouse Software Team

## Overview

Run a complete AI software development team: PM plans, Dev builds, QA reviews — all gated by spec documents and a strict layer build order.

**Core principle:** No code without a spec. No Layer N without Layer N-1 complete.

**Target:** Claude Code, OpenCode, Kimi Code. Works in both single-project repos and monorepos.

---

## The Three Anchor Documents

Write these **before any code**. They are contracts, not documentation:

| Document | Purpose |
|----------|---------|
| TECH_SPEC.md | Data contract — schemas, collections, service signatures |
| SCREEN_SPEC.md | UX contract — every screen in ASCII or wireframe |
| BUILD_STATUS.md | Progress tracker — checkboxes per layer, updated after every merge |

**Hard rule:** No spec = STOP. Write the spec first, then plan the ticket.

---

## Layered Build Order

Enforce N-1 before N. Typical full-stack app stack:

| Layer | Name | What goes here |
|-------|------|----------------|
| 1 | Types & Constants | Interfaces, enums, color tokens, config |
| 2 | Services | Data access — CRUD, auth, storage |
| 3 | Context & Hooks | State management, business logic |
| 4 | Base Components | Reusable UI primitives |
| 5 | Screens / Pages | Full route implementations |
| 6 | Backend Functions | Cloud functions, webhooks, scheduled jobs |
| 7 | Integration & Polish | Wire together, performance, real data |

Adapt layer names and count to your stack. The gate rule is universal.

---

## Agent Pipeline (every feature)

```
PM Tech Lead → [Research?] → Dev Engineer → QA Engineer → Human Approve → Merge
```

| Agent | Responsibility |
|-------|---------------|
| PM Tech Lead | Plans ticket, enforces N-1 gate, defines scope + out-of-scope |
| Research Engineer | Investigates new APIs/integrations — skip for standard CRUD |
| Dev Engineer | Implements ticket exactly — no more, no less |
| QA Engineer | Validates against TECH_SPEC + SCREEN_SPEC schemas |

Create agent files at `.claude/agents/` — one markdown file per agent with role, trigger, and output format.

**Step 5b — Browser verification (web projects only):** After code review, the QA Engineer uses `/browse` to verify the built UI in a real browser:
- Console — no JS errors after page load
- Critical UI elements present
- Main user flow works end-to-end
- Layout holds at mobile + desktop

Skip this step for mobile apps, CLIs, and backend-only features.

---

## Monorepo Support

If your project is a monorepo with multiple sub-projects, scope all commands to the active sub-project.

**Sub-project detection (in order):**
1. User passes `--project <name>` explicitly → use it
2. CWD is inside a sub-project directory → infer from path
3. CWD is repo root → show root-level BUILD_STATUS.md
4. Ambiguous → ask once: "Which sub-project?"

**Implementation:**

```python
def detect_project(args: list, cwd: str, root_path: str) -> str:
    if "--project" in args:
        idx = args.index("--project")
        return args[idx + 1]
    rel = os.path.relpath(cwd, root_path)
    parts = rel.split(os.sep)
    if parts[0] in ("mcps", "skills") and len(parts) >= 2:
        return parts[1]
    return "root"
```

---

## Unified Command: /pst

| Sub-command | Action |
|-------------|--------|
| `status [--project <name>]` | Read BUILD_STATUS, current layer + next unchecked task |
| `plan [feature]` | Invoke PM Tech Lead → structured ticket |
| `build` | Invoke Dev Engineer → implement current ticket |
| `review` | Invoke QA Engineer → validate changes |
| `branch [name]` | Create `feature/{subproject}/L{N}-{name}` |
| `pr` | Type-check → rebase → push → create PR |
| `next` | Find first unchecked item across all sub-projects |

---

## Auto-Routing

| User says | Action |
|-----------|--------|
| "build X", "create X", "add X" | PM Tech Lead ticket first |
| "review", "check", "QA" | QA Engineer |
| "done", "merge", "PR" | Finish-feature flow |
| "status", "what's next" | Read BUILD_STATUS |
| "research X", "how does X work" | Research Engineer |

---

## Session Hygiene & Context Recovery

- BUILD_STATUS.md updates on `main` only, not feature branches
- Fresh session after each merge
- 4 git commands for full context: `git branch` + `git diff main...HEAD --stat` + `git diff main...HEAD` + `git status`
- Branch naming: `feature/{subproject}/L{N}-{name}`

---

## New Project Setup

1. Write TECH_SPEC.md, SCREEN_SPEC.md, BUILD_STATUS.md
2. Write CLAUDE.md with auto-routing
3. Create `.claude/agents/` (pm, dev, qa, research)
4. Create `.claude/skills/[project]/SKILL.md` with `/pst` commands
5. Start Layer 1

---
name: software-team
description: Use when starting or structuring any complex software project with AI — establishes a full team workflow with spec-first anchor documents, enforced layered build order, PM → Dev → QA agent pipeline, and a unified project command skill
---

# Software Team

## Overview

Run a complete AI software development team: PM plans, Dev builds, QA reviews — all gated by spec documents and a strict layer build order.

**Core principle:** No code without a spec. No Layer N without Layer N-1 complete.

---

## The Three Anchor Documents

Write these **before any code**. They are contracts, not documentation:

| Document | Purpose |
|----------|---------|
| `TECH_SPEC.md` | Data contract — schemas, collections, service signatures |
| `SCREEN_SPEC.md` | UX contract — every screen in ASCII or wireframe |
| `BUILD_STATUS.md` | Progress tracker — checkboxes per layer, updated after every merge |

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
PM Tech Lead → [Research] → Dev Engineer → QA Engineer → Human Approve → Merge
```

| Agent | Responsibility |
|-------|---------------|
| PM Tech Lead | Plans ticket, enforces N-1 gate, defines scope + out-of-scope |
| Research Engineer | Investigates new APIs/integrations — skip for standard CRUD |
| Dev Engineer | Implements ticket exactly — no more, no less |
| QA Engineer | Validates against TECH_SPEC + SCREEN_SPEC schemas |

Create agent files at `.claude/agents/` — one markdown file per agent with role, trigger, and output format.

**Step 5b — Browser verification (web projects only):** After code review, the QA Engineer uses `/gstack` to verify the built UI in a real browser:
- `$B console` — no JS errors after page load
- `$B is visible ".key-element"` — critical UI elements present
- `$B goto → fill → click → snapshot` — main user flow works end-to-end
- `$B responsive /tmp/check` — layout holds at mobile + desktop

Skip this step for mobile apps, CLIs, and backend-only features.

---

## Unified Command Skill

Create a project-level skill (e.g. `/myapp`) with these sub-commands:

| Sub-command | Action |
|-------------|--------|
| `status` | Read BUILD_STATUS, show current layer + next unchecked task |
| `plan [feature]` | Invoke PM Tech Lead → produce structured ticket |
| `build` | Invoke Dev Engineer → implement current ticket |
| `review` | Invoke QA Engineer → validate changes |
| `branch [name]` | Create `feature/L{N}-{name}` branch from develop |
| `pr` | Type-check → sync develop → create PR with standard template |
| `next` | Find first unchecked item in BUILD_STATUS |

Route all user intent through this single entry point — never ask users which agent to call.

---

## Auto-Routing (put in CLAUDE.md)

| User says | Automatic action |
|-----------|-----------------|
| "build X", "create X", "add X" | PM Tech Lead ticket first |
| "review", "check", "QA" | QA Engineer |
| "done", "merge", "PR" | Finish-feature flow |
| "status", "what's next" | Read BUILD_STATUS, suggest next task |
| "research X", "how does X work" | Research Engineer |

Never ask "which agent should I use?" — route automatically.

---

## Session Hygiene

- `BUILD_STATUS.md` updates on `develop` only — never on feature branches (prevents recurring merge conflicts)
- Start a fresh session after each merged PR (preserves token budget)
- Use Claude's persistent memory system for cross-session project context
- Branch naming: `feature/L{N}-{name}` — layer number visible in the branch name

## Context Recovery (chat cleared mid-work)

If a session is cleared before a PR is merged, git state is the recovery source — not chat history. Run these four commands at the start of the next session:

```bash
git branch --show-current          # what feature you were building
git diff develop...HEAD --stat     # all files changed in this branch
git diff develop...HEAD            # full diff of everything built so far
git status                         # any uncommitted work still in progress
```

Combined with `BUILD_STATUS.md` (what layers are fully done), these four commands give complete context: what the feature is, what was already implemented, and what still needs to be written. No need to start over — resume from exactly where the session stopped.

---

## New Project Setup Checklist

1. Write `TECH_SPEC.md` — all schemas, service signatures, build layer map
2. Write `SCREEN_SPEC.md` — ASCII spec for every screen before any UI work
3. Create `BUILD_STATUS.md` — all items unchecked, grouped by layer
4. Write `CLAUDE.md` — hard rules, auto-routing table, tech stack, agent pipeline
5. Create `.claude/agents/` — pm-tech-lead.md, dev-engineer.md, qa-engineer.md, research-engineer.md
6. Create `.claude/skills/[project]/SKILL.md` — unified command skill with all sub-commands
7. Start Layer 1. Never skip ahead.

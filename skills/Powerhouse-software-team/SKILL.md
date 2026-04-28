# Software Team

## Overview

Run a complete AI software development team: PM plans, Dev builds, QA reviews — all gated by spec documents and a strict layer build order.

**Core principle:** No code without a spec. No Layer N without Layer N-1 complete.

**Target:** Claude Code (CLI). Works in both single-project repos and monorepos.

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
3. CWD is repo root → show root-level `BUILD_STATUS.md`
4. Ambiguous → ask once: "Which sub-project?"

**Implementation:**

```python
# Sub-project detection logic
import os
import re

def detect_project(args: list, cwd: str, root_path: str) -> str:
    # 1. Check --project flag
    if "--project" in args:
        idx = args.index("--project")
        return args[idx + 1]

    # 2. Infer from CWD
    rel = os.path.relpath(cwd, root_path)
    parts = rel.split(os.sep)

    # Check if inside mcps/ or skills/
    if parts[0] in ("mcps", "skills") and len(parts) >= 2:
        return parts[1]  # e.g., "investment-brain"

    # 3. Default to root
    return "root"
```

**Per sub-project anchor docs:** Each sub-project gets its own `TECH_SPEC.md` and `BUILD_STATUS.md` inside its directory. Agents are shared at the repo root (`.claude/agents/`).

**Root `BUILD_STATUS.md`:** Track the monorepo's meta-work (which sub-projects are shipped, docs done, distribution ready) separately from each sub-project's layer checklist.

---

## Unified Command Skill

Create a project-level skill (e.g. `/myapp`) with these sub-commands:

| Sub-command | Action |
|-------------|--------|
| `status [--project <name>]` | Read BUILD_STATUS, show current layer + next unchecked task |
| `plan [feature]` | Invoke PM Tech Lead → produce structured ticket |
| `build` | Invoke Dev Engineer → implement current ticket |
| `review` | Invoke QA Engineer → validate changes |
| `branch [name]` | Create `feature/{subproject}/L{N}-{name}` branch from main |
| `pr` | Type-check → sync main → create PR with standard template |
| `next` | Find first unchecked item in BUILD_STATUS (all sub-projects) |

Route all user intent through this single entry point — never ask users which agent to call.

Add project-specific scaffolding sub-commands (e.g., `setup`, `seed`, `reset-db`) to this same skill — centralizing all project operations in one entry point.

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

- `BUILD_STATUS.md` updates on `main` only — never on feature branches (prevents recurring merge conflicts)
- Start a fresh session after each merged PR (preserves token budget)
- Use Claude's persistent memory system for cross-session project context
- Branch naming: `feature/{subproject}/L{N}-{name}` — sub-project + layer both visible in branch name

---

## Context Recovery (chat cleared mid-work)

If a session is cleared before a PR is merged, git state is the recovery source — not chat history. Run these four commands at the start of the next session:

```bash
git branch --show-current          # what feature you were building
git diff main...HEAD --stat        # all files changed in this branch
git diff main...HEAD               # full diff of everything built so far
git status                         # any uncommitted work still in progress
```

Combined with `BUILD_STATUS.md` (what layers are fully done), these four commands give complete context: what the feature is, what was already implemented, and what still needs to be written. No need to start over — resume from exactly where the session stopped.

---

## Persistence Model

Three layers, each with a distinct job. They complement — not duplicate — each other.

| Layer | Where | Stores | Lifetime |
|-------|-------|--------|----------|
| **Memory files** | `~/.claude/projects/<hash>/memory/` | *Why* — decisions, constraints, locked choices | Cross-session |
| **BUILD_STATUS.md** | Repo root or sub-project dir | *What* — which layers are done, what's in progress | Updated after each merge |
| **Git** | Branch + commits | *How* — the actual implementation | Permanent |

**Rule of thumb:** If you'd need to explain it to a new agent every session, it belongs in memory. If it tracks progress, it belongs in BUILD_STATUS. If it's code, it belongs in git.

### Lock a decision

When a design choice is settled and should not be re-litigated, write it to a memory file with a lock flag:

```markdown
---
name: Auth Strategy
description: Chosen auth approach — read before any auth work
type: project
---

Chosen: JWT with refresh tokens stored in httpOnly cookies.

**DO NOT re-brainstorm this.** Decision locked after L1 implementation.
Why: compliance requirement — session tokens must be httpOnly.
```

Agents recovering from a cleared session will read this and skip straight to implementing — no re-debate.

### Memory file format (Claude Code)

```markdown
---
name: <short name>
description: <one-line trigger — when should an agent read this?>
type: project | user | feedback | reference
---

<content — lead with the fact, then Why: and How to apply: lines>
```

Keep a `MEMORY.md` index in the same folder. One line per entry: `- [Title](file.md) — one-line hook`.

---

## New Project Setup Checklist

### Single-project repo
1. Write `TECH_SPEC.md` — all schemas, service signatures, build layer map
2. Write `SCREEN_SPEC.md` — ASCII spec for every screen before any UI work
3. Create `BUILD_STATUS.md` — all items unchecked, grouped by layer
4. Write `CLAUDE.md` — hard rules, auto-routing table, tech stack, agent pipeline
5. Create `.claude/agents/` — pm-tech-lead.md, dev-engineer.md, qa-engineer.md, research-engineer.md
6. Create `.claude/skills/[project]/SKILL.md` — unified command skill with all sub-commands
7. Start Layer 1. Branch naming: `feature/{project}/L{N}-{name}`. Never skip ahead.

### Monorepo
1. Write root `CLAUDE.md` — auto-routing, hard rules, agent pipeline reference, CLI/web split
2. Create root `BUILD_STATUS.md` — tracks meta-work (skills shipped, MCPs shipped, docs done)
3. Create `.claude/agents/` at repo root — shared across all sub-projects
4. Create `.claude/skills/[project]/SKILL.md` — unified command with `--project` flag support
5. For each active sub-project: write `TECH_SPEC.md` + `BUILD_STATUS.md` inside its directory
6. Start Layer 1 of the first sub-project. Never skip ahead.

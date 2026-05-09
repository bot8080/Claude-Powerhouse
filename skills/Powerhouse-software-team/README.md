# Powerhouse Software Team

> **[CLI only]** — This skill runs in **Claude Code** (terminal). Not available on Claude.ai web.

A **complete AI software development team** — PM plans, Dev builds, QA reviews, all in one structured workflow.

AI projects often collapse into chaos: no specs, no build order, agents doing whatever they want. This skill enforces a **spec-first discipline** with hard gates between build layers and a four-agent pipeline that keeps every feature accountable.

---

## At a Glance

```
User Request
     │
     ▼
┌─────────────────┐
│  @advisor       │  Quick help, brainstorming (anytime)
│  "ask advisor"  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  /pst plan      │  PM Tech Lead writes ticket
│                 │  → TECH_SPEC.md + structured ticket
└────────┬────────┘
         │
    ┌────┴────┐
    ▼         ▼
┌────────┐ ┌──────────┐
│Dev Eng │ │ Research │
│(simple)│ │(complex) │
└───┬────┘ └────┬─────┘
    │           │
    ▼           ▼
┌─────────────────┐
│  /pst build     │  Implements exactly the ticket scope
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  /pst review    │  QA Engineer validates
│                 │  7-point checklist:
│                 │  1. Spec match  5. Types/lint
│                 │  2. Scope       6. Smoke test
│                 │  3. Quality     7. Browser (UI)
│                 │  4. Criteria
└────────┬────────┘
         │
         ▼
    Human Approve → Merge
```

---

## Where This Skill Lives

When active, this skill instructs the AI to create and maintain these files in your project:

| File | Purpose |
|------|---------|
| `TECH_SPEC.md` | Data contract — schemas, service signatures |
| `SCREEN_SPEC.md` | UX contract — every screen before any UI code |
| `BUILD_STATUS.md` | Checked-off progress tracker per layer |
| `.claude/agents/pm-tech-lead.md` | PM agent behavior |
| `.claude/agents/research-engineer.md` | Research agent behavior |
| `.claude/agents/dev-engineer.md` | Dev agent behavior |
| `.claude/agents/qa-engineer.md` | QA agent behavior |
| `.claude/skills/[project]/SKILL.md` | Unified `/projectname` command skill |

---

## Commands (Claude Code)

Type these inside a **Claude Code** session:

| Command | When | What happens |
|---------|------|-------------|
| `/pst status` | Start of session | Shows current layer + first unchecked task |
| `/pst plan "feature"` | Before any code | PM writes TECH_SPEC + structured ticket |
| `/pst build` | After ticket done | Dev Engineer implements (or dispatches to OpenCode) |
| `/pst review` | After build complete | QA Engineer runs 7-point validation |
| `/pst branch name` | Starting new feature | Creates `feature/{project}/L{N}-{name}` |
| `/pst pr` | Ready to ship | Type-check → rebase → push → create PR |
| `/pst next` | Lost or stuck | Finds first unchecked task across all sub-projects |

---

## 7-Layer Build Order

Layer N cannot start until Layer N-1 is fully checked off and merged to `main`:

| Layer | Name | What it contains |
|-------|------|-----------------|
| 1 | Types & Constants | Interfaces, enums, config, color tokens |
| 2 | Services | CRUD, auth, API clients, storage |
| 3 | Context & Hooks | State management, business logic |
| 4 | Base Components | UI primitives — buttons, inputs, cards |
| 5 | Screens / Pages | Full route implementations |
| 6 | Backend Functions | Cloud functions, webhooks, scheduled jobs |
| 7 | Integration & Polish | Wire everything together, perf, real data |

**Example:** If you're at Layer 3, all interfaces (Layer 1) and services (Layer 2) must already exist on `main`.

---

## Agent Roles

| Agent | Trigger | Job |
|-------|---------|-----|
| **@advisor** | `@advisor` or "ask advisor" | Ad-hoc help, brainstorming, quick questions |
| **PM Tech Lead** | `/pst plan` or "build X" | Ticket creation, spec-gate + layer-gate checks |
| **Research Engineer** | "research X" or "how does X work" | API/library investigation (skipped for standard CRUD) |
| **Dev Engineer** | `/pst build` or "implement X" | Scoped implementation — no more, no less than ticket |
| **QA Engineer** | `/pst review` or "QA" | 7-point validation: spec, scope, quality, criteria, syntax, smoke, browser |
| **OpenCode Dispatcher** | "dispatch to opencode" | Routes mechanical work to free model |

---

## Monorepo Support

Works in both single-project repos and monorepos with multiple sub-projects (e.g., `mcps/`, `skills/`).

### Auto-Detection

The skill detects the active sub-project in this order:
1. **Explicit flag:** `--project investment-brain` → use that sub-project
2. **CWD inference:** Running inside `mcps/investment-brain/` → auto-detect "investment-brain"
3. **Root fallback:** Running from repo root → show root-level BUILD_STATUS.md

### Examples

```
/pst status                            → root BUILD_STATUS.md
/pst plan "add auth"                   → plans for project detected from CWD
/pst plan --project investment-brain   → plans for investment-brain specifically
```

### Project Structure

```
repo/
├── BUILD_STATUS.md          # Root meta-work tracker
├── TECH_SPEC.md            # Root-level spec (if needed)
├── mcps/
│   ├── market-intelligence/
│   │   ├── BUILD_STATUS.md # Per-sub-project tracking
│   │   └── TECH_SPEC.md
│   └── investment-brain/
│       ├── BUILD_STATUS.md
│       └── TECH_SPEC.md
├── skills/
│   └── Powerhouse-software-team/
│       └── ...
```

---

## Session Recovery

After session clear or context loss, restore full state with 4 commands:

```bash
git branch --show-current          # Where am I?
git diff main...HEAD --stat        # What changed?
git diff main...HEAD               # Full diff
git status                         # Uncommitted work?
```

Then read `BUILD_STATUS.md` for the next task.

---

## Installation

### In This Repo (Automatic)

Skills under `.claude/skills/` activate automatically when working in this repo. No install needed.

### In Your Own Project

To use this skill and agent workflow in a separate project:

1. Clone this repo for reference
2. Copy the agent definitions from `.claude/agents/` or `.opencode/agents/` to your project
3. Copy `AGENTS.md`, `opencode.json`, and the `.claude/` directory structure
4. Install the skill in Claude Code: copy `Powerhouse-software-team.skill` to your project's `.claude/skills/`

### For Claude.ai Web (Read Only)

Download the `.skill` file and upload to Claude.ai → Settings → Skills. Note: this skill only shows the docs — the `/pst` commands only work in Claude Code.

- [Powerhouse-software-team.skill](./Powerhouse-software-team.skill)

---

## Related

| Resource | Purpose |
|----------|---------|
| [All Skills](../README.md) | Browse all 4 skills + install guide |
| [Project Setup Kit](../Powerhouse-Claud-Project-Setup-Kit/) | Set up project knowledge base |
| [Root README](../../README.md) | Full repo documentation |
| [Quick Start](../../docs/QUICKSTART.md) | 5-minute setup guide |

---

*Part of the [MultiAgents-Powerhouse](../../README.md) suite.*

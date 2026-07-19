# Claude-Powerhouse — OpenCode Session Brief

Monorepo with two outputs: MCP servers (`mcps/`) and Skills (`skills/`).
Active sub-projects: `market-intelligence` (shipped), `investment-brain` (in development).

---

## Session Start Protocol

Run these at the start of every session — silently, before responding:

```bash
git branch --show-current
git diff main...HEAD --stat
git status
```

Then read `BUILD_STATUS.md` (root) and `mcps/investment-brain/BUILD_STATUS.md`.
Report to the user: current branch, first unchecked task, and any uncommitted work.

---

## Current State

All repo-level tasks from BUILD_STATUS.md are **complete**.
Active development continues on sub-projects.

### investment-brain — `mcps/investment-brain/`
**All 7 layers complete.** Every item checked off.

### market-intelligence — `mcps/market-intelligence/`
**Shipped.** 8 tools, US/India/Canada markets.

### Repo-level tasks
All Layer 1-8 items in root BUILD_STATUS.md are **complete**:
- Layer 1: Infrastructure & workflow setup ✅
- Layer 2: Skills core shipping ✅
- Layer 3: MCP servers core shipping ✅
- Layer 4: Documentation ✅
- Layer 5: Distribution & discovery ✅
- Layer 6: Merger (development-protocols → Claude-Powerhouse) ✅
- Layer 7: PST compliance ✅
- Layer 8: Multi-model architecture ✅

Next: ongoing feature development on sub-projects.

---

## Auto-Routing — follow without asking

| User says | Do this |
|---|---|
| "build X", "create X", "add X", "implement X" | Activate PM Tech Lead (read `.opencode/agents/pm-tech-lead.md`) |
| "plan X", "design X", "architect X" | Activate PM Tech Lead |
| "review", "check", "QA", "test" | Activate QA Engineer (read `.opencode/agents/qa-engineer.md`) |
| "research X", "how does X work", "investigate X" | Activate Research Engineer (read `.opencode/agents/research-engineer.md`) |
| "build" / "code it" (after a ticket exists) | Activate Dev Engineer (read `.opencode/agents/dev-engineer.md`) |
| "done", "merge", "PR", "ship" | Run: type-check → sync main → create PR |
| "status", "what's next", "where are we" | Read `BUILD_STATUS.md`, report first unchecked task |

**Rule:** Never ask which agent to use. Route silently and immediately.

---

## Pipeline (every feature)

```
PM Tech Lead → [Research Engineer?] → Dev Engineer → QA Engineer → Human Approve → Merge
```

Skip Research Engineer for standard CRUD/config. Use it for new APIs, unfamiliar libraries, or third-party integrations.

When activating a role, **read the agent file first** — it contains the full behavior definition.

---

## Layer Gate

Layer N cannot start until Layer N-1 is merged to `main`. Current layers:

| # | Name | Contents |
|---|---|---|
| 1 | Types & Constants | Interfaces, enums, config |
| 2 | Services | CRUD, auth, API clients |
| 3 | Context & Hooks | State, business logic |
| 4 | Base Components | UI primitives (skip for CLI/backend) |
| 5 | Screens / Pages | Full routes |
| 6 | Backend Functions | Cloud functions, webhooks |
| 7 | Integration & Polish | Wire up, performance, real data |

---

## Spec Gate

Before touching any source file, confirm both exist:
- `TECH_SPEC.md` — schemas and service signatures
- `BUILD_STATUS.md` — layer checklist

If missing: warn the user and suggest writing the spec first. Do not silently skip.
Exception: `market-intelligence` is exempt (already shipped without specs).

---

## Branch Naming

`feature/L{N}-{description}` — layer number must be visible in the branch name.
`BUILD_STATUS.md` updates go to `main` only — never on a feature branch.

---

## Context Recovery (after session clear)

```bash
git branch --show-current
git diff main...HEAD --stat
git diff main...HEAD
git status
```

These four commands + `BUILD_STATUS.md` fully restore context.

---

## Available Skills

Skills live in `skills/` and `~/.claude/skills/`. Use the `skill` tool to load them.

| Skill | Purpose |
|---|---|
| `software-team` | Full PM→Dev→QA pipeline |
| `Powerhouse-Claude-Project-Setup-Kit` | Project setup and knowledge-base auditing |
| `Powerhouse-Prompt-Optimizer` | Prompt engineering |
| `Powerhouse-Resume-Specialist` | DOCX resume formatting |

---

## Multi-Model Architecture (OpenCode Go Plan)

### Config Files

| File | Purpose |
|---|---|
| `opencode.json` | Base config — **no hardcoded models**, falls back to user default |
| `opencode.go.json` | Go plan overlay — per-agent model routing (optional, manual activation) |

### Why Route by Role?

Each role has different demands. Routing lets you match model capability to workload:
- **Planning / Architecture** → Strong reasoning. Used by PM Tech Lead, Advisor.
- **Complex implementation** → Balanced power. Used by Dev Engineer.
- **Mechanical / high-volume** → Fast and cheap. Used by Worker-Mechanical.
- **Validation / testing** → Thorough. Used by QA Engineer.
- **Investigation** → Research-capable. Used by Research Engineer.

### Activate

```bash
cp opencode.go.json opencode.json
```

### Model Discontinuation Safety

- **Zero hardcoded models in base `opencode.json`** — survives any model deprecation
- Agent definitions (`.opencode/agents/*.md`) contain **no `model:` field** — tool-agnostic
- Model routing lives only in config files
- If Go plan unavailable, falls back to your default model

> Specific model IDs are in `opencode.go.json` — check there for what the Go plan activates.

<!-- AGENTS.md — Universal project instructions for AI coding agents -->

# AGENTS.md — Development Workflow

## Pre-Flight Branch Validation

Before ANY planning or implementation, ALWAYS run this checklist:

1. `git branch --show-current` — identify current branch type
2. Classify the task:
   - **Feature work** (code, components, screens) → `feature/*` branch
   - **Meta/workflow/config** → `chore/*` branch
   - **Documentation-only** → `docs/*` branch
   - **Release** → `release/*` branch
   - **Hotfix** → `hotfix/*` branch (from main)
3. If current branch type doesn't match task type → STOP and propose change.
4. Check sync state: if behind origin/main >10 commits, suggest merge.

## Agent Pipeline

Every feature follows: PM Tech Lead → Dev Engineer → QA Engineer → Human Approve → Merge

| Agent | Job |
|-------|-----|
| PM Tech Lead | Plans features, enforces build order, produces scoped tickets |
| Dev Engineer | Implements exactly what ticket says |
| QA Engineer | Validates against specs + conventions |
| Advisor | Research, architecture, cost analysis (@advisor) |

## Session Start

When starting a new conversation:
1. Run `session-tracking/restore.sh` to restore previous session state
2. Read `docs/CONVENTIONS.md` and `docs/ARCHITECTURE.md`
3. Run `git branch --show-current`, validate branch type
4. Display current branch, sync status, and suggest next task

## Session End

Before finishing a chat session:
1. Run `session-tracking/save.sh` to persist session state
2. This saves current branch, commit, and modified files

## Build Order (Layered Architecture)

1. **Foundation** — Types, constants, utilities
2. **Services** — API/backend service layer
3. **Context & Hooks** — State management, custom hooks
4. **Components** — Reusable UI components
5. **Screens** — Full screen implementations
6. **Backend Functions** — Serverless/cloud functions
7. **Infrastructure** — CI/CD, security rules, config
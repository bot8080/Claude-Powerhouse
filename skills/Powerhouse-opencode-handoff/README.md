# OpenCode Handoff

> **Target:** Claude Code (CLI) only.

A Powerhouse skill that hands off mechanical coding tasks from Claude Code to **OpenCode + MiniMax M2 (free tier)** — saving Claude tokens for planning and review.

> [!NOTE]
> Claude Code is excellent at judgement work — planning, architecture, code review. It's wasteful to spend Opus tokens on boilerplate renames, well-spec'd CRUD, or docstring passes. This skill routes that work to OpenCode running MiniMax M2 (free on OpenRouter), keeps each dispatch in an isolated git worktree, and pulls the diff back through your existing QA Engineer for review.

---

## The Challenges This Solves

| Before ❌ | The Powerhouse Solution ✅ | The Result 🚀 |
| :--- | :--- | :--- |
| • Opus tokens spent on mechanical refactors and docstrings<br>• No way to share planning context with another agent<br>• Risk of agents stepping on each other's edits<br>• Free models go off-script without strict scoping | • PM Tech Lead writes one ticket; both CC and OC consume it<br>• Each dispatch runs in a dedicated git worktree<br>• OpenCode reads your `CLAUDE.md` automatically (no duplicate config)<br>• A custom OC slash command (`/follow-ticket`) pins behavior to In-Scope only<br>• QA Engineer reviews the diff in CC before merge | • **Token Savings**: routine work runs free on MiniMax M2<br>• **Zero Conflicts**: worktree isolation per dispatch<br>• **Reviewable Output**: every dispatch is a tracked branch you can read<br>• **Auditable**: append-only `dispatch-log.md` with timing + AC results |

---

## How It Works

```
Claude Code  ──plan──►  ticket file  ──dispatch──►  OpenCode (MiniMax M2)
   (Opus)                    │                          │
      ▲                      ▼                          ▼
      │              .powerhouse/tickets/        .powerhouse/wt/{id}/
      │                                                 │
      └────────────review (Sonnet 4.6) ◄────diff────────┘
```

1. **Plan** in Claude Code — the PM Tech Lead writes a ticket to `.powerhouse/tickets/{id}.md`.
2. **Classify** — the skill scores the task on spec-clarity, mechanical-ness, and blast-radius. Score ≥ 7/9 ⇒ recommend dispatch.
3. **Dispatch** — `git worktree add .powerhouse/wt/{id}`, then `opencode run --model openrouter/minimax/minimax-m2:free --file <ticket>`.
4. **Verify** — diff the worktree, ensure OC stayed inside `files_to_touch`.
5. **Review** in Claude Code — the QA Engineer runs its full checklist on the diff. PASS ⇒ merge worktree to the feature branch.

---

## Installation

### 1. Install OpenCode

```bash
curl -fsSL https://opencode.ai/install | bash
opencode --version
```

### 2. Auth with OpenRouter

```bash
opencode auth login
# Select: OpenRouter
# Paste your OpenRouter API key (https://openrouter.ai/keys)
```

> Free MiniMax M2 access is included with any OpenRouter account. No payment needed for the free tier.

### 3. Verify the model works

```bash
opencode run --model openrouter/minimax/minimax-m2:free "print 'hello' in python"
```

You should see a one-line Python snippet printed.

### 4. The skill itself

Skills under `.claude/skills/` and `skills/` activate automatically when working in this repo. Nothing to install.

---

## Usage

### Auto-suggest mode (default)

Just describe a task. The skill scores it and either suggests dispatch or keeps it in CC.

> *"Rename `getCwd` to `getCurrentWorkingDirectory` across the repo."*

→ Skill responds: *"Score 8/9 — recommend dispatch. Reason: pure rename across known files, low blast radius. Say `/dispatch` to proceed."*

### Explicit dispatch

> *"Send this to opencode"* / *"/dispatch"* / *"minimax this"*

→ Skill writes the ticket, runs the dispatcher, surfaces the diff for review.

### Classify only (no action)

> *"Is this opencode-able? — `add a 4-pillar score breakdown to the scoring engine`"*

→ Skill scores and explains; doesn't write or run anything.

---

## Cost & Quota Notes

**Free tier (OpenRouter `minimax-m2:free`):**
- ~20 requests per minute
- ~200 requests per day (shared across all OpenRouter free models on your account)
- 204k context window
- Tool calling supported

A single OC dispatch typically uses 5–30 model requests depending on how many tool calls (read/edit) the task needs. The skill's quota guard:

- Warns when fewer than ~30 RPD are estimated remaining.
- Refuses dispatches with fewer than ~10 RPD and offers to (a) switch to paid `minimax-m2` ($0.255/M input, $1/M output), (b) wait for daily reset, or (c) keep the task in Claude Code.

**Cost comparison (1M tokens output):**

| Model | Input $/M | Output $/M |
|---|---|---|
| Claude Opus 4.7 | ~$15 | ~$75 |
| Claude Sonnet 4.6 | ~$3 | ~$15 |
| MiniMax M2 (paid) | $0.255 | $1 |
| MiniMax M2:free | $0 | $0 |

For a routine 5k-token coding task, dispatch saves ~$0.40 vs Opus and ~$0.08 vs Sonnet — small per task, but compounds quickly across a development session.

---

## What This Skill Creates In Your Repo

| Path | Purpose |
|---|---|
| `.powerhouse/tickets/{id}.md` | One per dispatch — both CC and OC read this |
| `.powerhouse/tickets/SCHEMA.md` | Frontmatter contract |
| `.powerhouse/wt/{id}/` | Per-dispatch git worktree (auto-cleaned on success) |
| `.powerhouse/dispatches/{id}.ndjson` | Raw OC output (NDJSON events) |
| `.powerhouse/dispatch-log.md` | Append-only audit log |
| `.opencode/commands/follow-ticket.md` | OC slash command pinning behavior |
| `.claude/agents/opencode-dispatcher.md` | CC-side dispatcher agent |

`CLAUDE.md` is **not duplicated** — OpenCode reads it automatically as a fallback for `AGENTS.md` (per opencode.ai/docs/rules), so your existing project rules apply to both agents.

---

## Trigger Phrases

The skill activates on:

- *"Send this to opencode"*, *"let opencode handle this"*, *"use opencode"*
- *"/dispatch"*, *"/handoff"*, *"opencode handoff"*
- *"Minimax this"*, *"run this with minimax"*
- *"Save tokens on this task"*, *"offload this"*, *"give this to opencode"*
- Any *"build X"* / *"create X"* / *"implement X"* — the skill silently scores it and suggests dispatch when score ≥ 7.

---

## Hard Rules

- Never dispatch without an approved ticket on disk.
- Always surface the dispatch score and let the user confirm.
- Never merge a worktree where OC touched files outside `files_to_touch`.
- Never silently fall back to a paid model when the free tier hits its limit.
- Never run OC in the main working tree — always use `git worktree add`.

---

## Troubleshooting

| Error | Cause | Fix |
|-------|-------|-----|
| `opencode: command not found` | OpenCode not installed | `curl -fsSL https://opencode.ai/install \| bash` |
| OpenRouter auth failed (401) | API key missing/expired | `opencode auth login` → paste key from [openrouter.ai/keys](https://openrouter.ai/keys) |
| Worktree conflict | Stale dispatch not cleaned | `git worktree prune` + `rm -rf .powerhouse/wt/*` |
| Dispatch score < 7 | Task not mechanical enough | Keep task in Claude Code — don't force dispatch |
| Free tier limit (200/day) | Hit daily quota | Wait for UTC reset, or switch to paid `minimax-m2` model |
| OpenCode ignores files_to_touch | Missing `follow-ticket.md` command | Ensure `.opencode/commands/follow-ticket.md` exists in repo |
| OpenCode can't find AGENTS.md | Not in repo root | Create `AGENTS.md` (or run `npx powerhouse apply`) |

---

## Contents

- `SKILL.md` — full skill instructions (mode detection, classifier, dispatch flow)
- `references/dispatch-protocol.md` — the exact ticket → OC → diff → review contract
- `references/quota-and-fallback.md` — OpenRouter free-tier limits and paid-fallback math
- `Powerhouse-opencode-handoff.skill` — the installable distributable

---

*Part of the [Claude-Powerhouse](../../README.md) suite. Pairs with [Powerhouse-software-team](../pst-software-team/) (PM/Dev/QA pipeline) and `/pst` (unified command).*


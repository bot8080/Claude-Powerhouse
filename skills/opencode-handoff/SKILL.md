---
name: opencode-handoff
description: >
  Use this skill to hand off mechanical coding work from Claude Code to OpenCode (an open-source CLI agent
  from SST) running the free MiniMax M2 model on OpenRouter — saving Claude tokens for planning and review.
  Triggers include: "send to opencode", "let opencode handle this", "use opencode", "open code this for me",
  "/dispatch", "/handoff", "minimax this", "save tokens", "offload this task", "opencode handoff",
  "give this to opencode", "run this with minimax", or whenever the user asks Claude Code to delegate
  a code-execution task to a cheaper external agent. Also activates when Claude Code wants to suggest
  a handoff because the task profile is mechanical, well-specified, and low blast-radius. Each dispatch
  runs in a dedicated git worktree under .powerhouse/wt/, follows a PM-style ticket, and is reviewed
  back in Claude Code by the QA Engineer. Pairs with the existing PM Tech Lead, Dev Engineer, and
  QA Engineer agents in .claude/agents/.
---

# OpenCode Handoff

## Overview

This skill turns Claude Code into the **planner + reviewer** and OpenCode + MiniMax M2 into the **executor** for coding tasks that don't need Claude's judgement. It's the token-saving lane of the Powerhouse pipeline.

**Core idea.** Claude Code (Opus) plans and reviews. OpenCode (free MiniMax M2) writes the code. Each dispatch runs in an isolated git worktree so concurrent work in your main tree is never at risk.

**Target:** Claude Code (CLI) only.

**Hard rule.** Never dispatch without (a) an approved PM Tech Lead ticket, (b) a confirmed `dispatch_score`, and (c) a clean worktree. The user must approve the dispatch every time — this skill auto-suggests, it does not auto-route.

---

## Why this exists

Claude Code burns Opus tokens on mechanical work — boilerplate, renames, well-spec'd CRUD, repetitive edits. That work doesn't need Opus judgement. OpenCode + MiniMax M2 is purpose-built for it:

- 10B activated / 230B total params, 204k context window
- Strong on SWE-Bench Verified, Multi-SWE-Bench, Terminal-Bench
- Free on OpenRouter (`minimax-m2:free`) at ~20 RPM / ~200 RPD
- Tool-use and reasoning supported
- **Reads your existing `CLAUDE.md` automatically** as a fallback for `AGENTS.md` — no duplicate config

**Token-spend split:**

| Phase | Runs in | Model |
|---|---|---|
| Plan / spec / ticket | Claude Code | Opus 4.7 (or Sonnet 4.6) |
| Code execution | OpenCode | `openrouter/minimax/minimax-m2:free` |
| Code review / QA | Claude Code | Sonnet 4.6 |
| Architecture / research | Claude Code | Opus 4.7 + WebSearch |

---

## Mode detection

When the skill activates, decide which mode the user is in. Detect, then branch.

| User signal | Mode |
|---|---|
| "send X to opencode", "/dispatch", "minimax this" | **DISPATCH** — already approved a ticket, just run it |
| "plan and dispatch X", "build X with opencode" | **PLAN-THEN-DISPATCH** — write ticket first, then dispatch |
| "review the opencode work", "QA the dispatch" | **REVIEW** — pull diff back into CC, run QA Engineer |
| "should I send this to opencode?", "is this opencode-able?" | **CLASSIFY** — score it, recommend, don't act |
| Any "build X" / "create X" / "implement X" with no dispatch hint | **CLASSIFY-FIRST** — silently score; if score ≥ 7, *suggest* dispatch in the response |

If the user's intent is ambiguous, ask one clarifying question before branching.

---

## Auto-suggest classifier

Before recommending dispatch, score the task on three axes (each 0–3):

**Spec clarity.** Are inputs/outputs/files/acceptance criteria explicit? Does a TECH_SPEC reference exist?
- 3 = full ticket already written, every field filled
- 2 = clear ask, files known, criteria implicit
- 1 = directional, files unclear
- 0 = vague intent

**Mechanical-ness.** Boilerplate, rename, repetitive edit, well-known pattern → high. Novel API, debugging an unknown failure, architecture decision → low.
- 3 = pure transformation (rename, docstring, format)
- 2 = standard CRUD with clear pattern in codebase
- 1 = some judgement needed
- 0 = high-judgement / novel

**Blast radius (inverted).** Smaller blast = safer to dispatch.
- 3 = one file
- 2 = 2–4 files in one module
- 1 = cross-module
- 0 = cross-cutting / public API change

**Score** = `spec_clarity + mechanical_ness + (3 - blast_radius_raw)` where `blast_radius_raw` is the inverted score above (so just sum the three).

| Score | Action |
|---|---|
| **≥ 7** | Suggest dispatch — print the score, the reasoning, and ask for confirmation |
| **4–6** | Borderline — show the score and ask the user to choose: dispatch or stay in CC |
| **< 4** | Keep in CC — print "score X/9, keeping this in Claude Code (reason: …)" |

**Always print the score breakdown.** The user must be able to see *why* you recommend a dispatch and override it.

---

## DISPATCH mode — full flow

Run these steps in order. Use Bash. Never skip a check.

### 1. Pre-flight checks

```bash
# Confirm OpenCode is installed and authed
command -v opencode || { echo "OpenCode not installed. Run: curl -fsSL https://opencode.ai/install | bash"; exit 1; }
opencode auth list 2>&1 | grep -q openrouter || echo "WARN: OpenRouter not authed. Run: opencode auth login"

# Confirm we are in a git repo and the working tree is clean enough
git rev-parse --is-inside-work-tree >/dev/null || { echo "Not a git repo"; exit 1; }
git diff --quiet || echo "WARN: uncommitted changes in main worktree (won't affect dispatch but commit them when convenient)"
```

### 2. Confirm ticket

The ticket lives at `.powerhouse/tickets/{id}.md` and follows the schema in `.powerhouse/tickets/SCHEMA.md`. Validate that:

- `id`, `branch`, `files_to_touch`, `dispatch_score`, `model`, `status` are all present in the frontmatter
- `dispatch_score >= 7` (or the user explicitly overrode it for a 4–6 score)
- `status: planned`

If any check fails, halt and tell the user what's missing.

### 3. Spawn the dedicated worktree

```bash
TICKET_ID="L2-auth-svc-9f3a"          # from the ticket frontmatter
BRANCH="feature/L2-auth-svc"          # from the ticket frontmatter
WT=".powerhouse/wt/${TICKET_ID}"

# Create the branch if it doesn't exist
git show-ref --verify --quiet "refs/heads/${BRANCH}" || git branch "${BRANCH}" main

# Add the worktree (fails fast if path exists)
git worktree add "${WT}" "${BRANCH}"
```

Why a worktree: it's the only way to run OC concurrently with CC without file conflicts. Each dispatch is its own filesystem checkout of the feature branch. CC's working tree is never touched.

### 4. Run OpenCode

```bash
cd "${WT}"

opencode run \
  --model openrouter/minimax/minimax-m2:free \
  --format json \
  --quiet \
  --file ".powerhouse/tickets/${TICKET_ID}.md" \
  "/follow-ticket .powerhouse/tickets/${TICKET_ID}.md" \
  > ".powerhouse/dispatches/${TICKET_ID}.ndjson" 2>&1
```

The `/follow-ticket` slash command (defined in `.opencode/commands/follow-ticket.md`) pins OC to a single behavior: read the ticket, obey In Scope / Out of Scope / Files to Touch, emit a structured JSON completion report, stop.

Use `run_in_background: true` for the Bash call so the user can keep working in CC while OC runs. Watch the ndjson with `tail -f` if you need to surface progress.

### 5. Capture and validate the diff

```bash
# What did OC change?
git -C "${WT}" status --porcelain
git -C "${WT}" diff --stat

# Did OC stay inside files_to_touch?
git -C "${WT}" diff --name-only HEAD | sort > /tmp/oc_changed.txt
# Compare against the ticket's files_to_touch list (parse YAML frontmatter)
```

If OC touched files **outside** `files_to_touch`, halt and surface the violation. Do not merge. The user decides whether to re-dispatch with a revised ticket or accept manually.

### 6. Append to the dispatch log

Append one row to `.powerhouse/dispatch-log.md`:

```markdown
| 2026-04-27T18:32Z | L2-auth-svc-9f3a | minimax-m2:free | 4m12s | files_changed=3, ac_pass=4/4, off_scope=0 | OK |
```

### 7. Hand off to REVIEW mode

Print exactly:

> **Dispatch complete.** Ticket `{id}` ran in `{wt_path}`. {N} files changed, {M} acceptance criteria reported satisfied by OC. Ready for QA Engineer review — say `/powerhouse review` or "review the dispatch".

---

## REVIEW mode

1. Load `.claude/agents/qa-engineer.md` — run its full checklist against the worktree.
2. Read the OC completion JSON from `.powerhouse/dispatches/{id}.ndjson`. Compare OC's self-reported `ac_status` against the ticket's acceptance criteria.
3. Run any project-specific syntax/test commands listed in `CLAUDE.md` (e.g. `python -m py_compile src/...`).
4. Produce a PASS/FAIL report. On PASS: merge the worktree into the feature branch and remove it. On FAIL: leave the worktree intact, report issues, ask whether to re-dispatch a fix-up ticket or have CC patch directly.

Merge command:

```bash
# In the main repo, fast-forward the feature branch from the worktree's tip
git fetch . "${BRANCH}:${BRANCH}"   # no-op if same; handles edge cases
git worktree remove "${WT}"          # clean up the worktree dir
```

---

## CLASSIFY mode

User asks "is this opencode-able?" without committing to a dispatch. Score the task using the classifier above, print the score breakdown, and stop. Do not write a ticket. Do not spawn anything.

Output template:

```
Score: 8/9 — recommend OpenCode dispatch.
  Spec clarity:   3/3 — files explicit, AC clear
  Mechanical:     3/3 — pure rename across the codebase
  Blast radius:   2/3 (one module, ~6 files)
Reason to dispatch: This is mechanical and well-bounded; CC's judgement isn't needed. Estimated CC tokens saved: ~8k.
Recommendation: Say "/dispatch" or "send to opencode" to proceed. I'll write the ticket first and ask you to approve before running.
```

---

## Quota guard (OpenRouter free tier)

OpenRouter free models share **~200 requests per day** and **~20 RPM** across the account. A single OC dispatch can use 5–30 model requests depending on tool use.

Before any dispatch:

1. Inspect the last 24h of `.powerhouse/dispatch-log.md` and roughly count requests.
2. If estimated remaining < 30 RPD, **warn** the user.
3. If estimated remaining < 10 RPD, **refuse** the dispatch and offer:
   - Switch to paid `minimax-m2` ($0.255/M input, $1/M output) — ~50× cheaper than Opus and very capable.
   - Wait for the daily reset.
   - Run the ticket in CC anyway.

The user always chooses. Never silently switch models.

See `references/quota-and-fallback.md` for the cost math.

---

## Routing rules (auto-suggest)

Apply these rules when the user describes a coding task without explicitly invoking dispatch:

| Task profile | Recommendation |
|---|---|
| Rename/format/docstring across known files | **Suggest dispatch** — score will be ≥7 |
| Standard CRUD against a documented schema | **Suggest dispatch** if TECH_SPEC exists |
| Bug fix with a known reproducer + isolated module | **Suggest dispatch** |
| Bug fix where root cause is unknown | **Keep in CC** — investigate first, then maybe dispatch the patch |
| New API integration / unfamiliar library | **Keep in CC + Research Engineer** |
| Cross-cutting refactor touching many modules | **Keep in CC** — too high blast radius for OC |
| Architecture decision / interface design | **Keep in CC** — judgement work |
| Performance tuning / debugging | **Keep in CC** until cause is known |

Never override the user. They can always say "do it in CC anyway" or "just dispatch it".

---

## Files this skill creates / depends on

| Path | Role |
|---|---|
| `.powerhouse/tickets/{id}.md` | The ticket — both CC and OC read this |
| `.powerhouse/tickets/SCHEMA.md` | Frontmatter contract |
| `.powerhouse/wt/{id}/` | Per-dispatch git worktree |
| `.powerhouse/dispatches/{id}.ndjson` | Raw OC output (NDJSON events) |
| `.powerhouse/dispatch-log.md` | Append-only audit log |
| `.opencode/commands/follow-ticket.md` | Pins OC to ticket-following behavior |
| `.claude/agents/opencode-dispatcher.md` | The CC-side dispatcher agent (worktree, run, diff, hand-off) |
| `CLAUDE.md` | OC reads this automatically as fallback for AGENTS.md — keep it accurate |

---

## Risks & mitigations

| Risk | Mitigation |
|---|---|
| OC touches files outside `files_to_touch` | Diff check before merge; refuse merge on violation |
| OC introduces a subtle bug | QA Engineer runs full checklist + smoke tests in CC |
| Free tier exhausts mid-session | Quota guard refuses dispatches when <10 RPD remain |
| Worktrees pile up | Clean on success; `/powerhouse status` should surface orphans |
| User confused which model is doing what | Every dispatch prints a banner: `→ OpenCode + minimax-m2:free, ticket {id}, worktree {path}` |
| OC reasoning loss between turns | Single-shot only — no `--continue`. Split big tickets into smaller ones at plan time |

---

## Hard rules

- Never dispatch without an approved ticket on disk.
- Never auto-route — always surface the score and let the user confirm.
- Never merge a worktree where OC touched files outside `files_to_touch`.
- Never silently fall back to a paid model when the free tier hits its limit.
- Never run OC in the main working tree — always use `git worktree add`.
- Always print which model is running for which phase.

---

## See also

- `references/dispatch-protocol.md` — the exact ticket → OC → diff → review contract
- `references/quota-and-fallback.md` — OpenRouter free-tier limits and paid fallback math
- `.claude/agents/opencode-dispatcher.md` — the dispatcher agent definition
- `.opencode/commands/follow-ticket.md` — the OC slash command that pins behavior

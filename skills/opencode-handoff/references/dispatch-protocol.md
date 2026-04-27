# Dispatch Protocol

The exact contract between Claude Code (planner + reviewer) and OpenCode (executor).

---

## 1. Ticket schema

Every ticket lives at `.powerhouse/tickets/{id}.md` with this YAML frontmatter:

```yaml
---
id: L2-auth-svc-9f3a              # required — {layer}-{slug}-{shortid}
layer: 2                          # required — matches CLAUDE.md layer table
sub_project: investment-brain     # required — root | market-intelligence | investment-brain | …
branch: feature/L2-auth-svc       # required — feature/L{N}-{slug}
dispatch_score: 8                 # required — total 0..9 from the classifier
score_breakdown:                  # required — for audit
  spec_clarity: 3
  mechanical: 3
  blast_radius_inverted: 2
model: openrouter/minimax/minimax-m2:free   # required — fully qualified
status: planned                   # required — planned | dispatched | reviewing | merged | failed
files_to_touch:                   # required — exhaustive list, OC may NOT touch others
  - src/services/auth.py
  - tests/services/test_auth.py
created_at: 2026-04-27T18:32:00Z
created_by: claude-code           # claude-code | human
---
```

The body uses the standard PM Tech Lead format (Goal / In Scope / Out of Scope / Acceptance Criteria / Files to Touch / Spec References).

---

## 2. The OC slash command

`.opencode/commands/follow-ticket.md` is a single-purpose command. It is invoked by the dispatcher as:

```bash
opencode run \
  --model openrouter/minimax/minimax-m2:free \
  --format json \
  --quiet \
  --file ".powerhouse/tickets/${TICKET_ID}.md" \
  "/follow-ticket .powerhouse/tickets/${TICKET_ID}.md"
```

The command body instructs OC to:

1. Read the attached ticket file.
2. Implement only what's in **In Scope**.
3. Touch only the files listed under **Files to Touch**.
4. Make every **Acceptance Criterion** verifiable.
5. When done, print a final JSON line:
   ```json
   {"type": "completion", "files_changed": [...], "ac_status": [{"criterion": "...", "status": "pass|fail|n/a"}], "notes": "..."}
   ```
6. Stop. Do not start a new task.

---

## 3. Dispatch sequence

```
[CC]  ticket → write → .powerhouse/tickets/{id}.md
[CC]  git worktree add .powerhouse/wt/{id} {branch}
[CC]  opencode run --file .powerhouse/tickets/{id}.md /follow-ticket … > .powerhouse/dispatches/{id}.ndjson
[OC]  read ticket → edit files → emit completion JSON
[CC]  parse completion JSON
[CC]  git -C .powerhouse/wt/{id} diff --name-only HEAD
[CC]  validate: changed files ⊆ files_to_touch
[CC]  append to .powerhouse/dispatch-log.md
[CC]  hand off to REVIEW mode
```

---

## 4. Validation gates (CC enforces)

After OC finishes, CC must verify before any merge:

| Gate | Check | On failure |
|---|---|---|
| **File list** | `git diff --name-only` ⊆ `files_to_touch` | Halt; report extra files; do not merge |
| **AC self-report** | OC's `ac_status` lists every ticket AC | Halt; ask OC to re-run with the missing AC |
| **Syntax** | `python -m py_compile` for MCPs (per CLAUDE.md) | Halt; surface the syntax error to user |
| **Smoke** | Project-specific smoke test from CLAUDE.md | Halt; QA Engineer decides |

If any gate fails, the worktree is **left intact** for the user to inspect. The dispatcher does not auto-cleanup on failure.

---

## 5. Merge protocol

On QA PASS:

```bash
git -C .powerhouse/wt/{id} log --oneline -5    # confirm OC committed (or commit pending changes)
git -C .powerhouse/wt/{id} status               # should be clean
git worktree remove .powerhouse/wt/{id}         # branch tip is preserved
# back in main worktree:
git fetch . feature/L2-auth-svc:feature/L2-auth-svc   # no-op if branch already current
git checkout feature/L2-auth-svc                       # if you want to push or PR
```

The feature branch is the single source of truth — the worktree dir is just a temporary checkout location.

---

## 6. Failure modes & recovery

| Failure | Recovery |
|---|---|
| OC writes files outside `files_to_touch` | User reviews diff manually; either revise ticket and re-dispatch, or accept manually with a note in `dispatch-log.md` |
| OC times out (no completion JSON) | Worktree stays; user inspects `.powerhouse/dispatches/{id}.ndjson` for partial progress; can resume in CC or write a fix-up ticket |
| OC reports `ac_status: fail` for some criteria | QA Engineer reviews; usually a fix-up ticket with the failed criteria as the new In Scope |
| Worktree creation fails (path exists) | Either the dispatch is already running (check process), or a previous orphan — user removes manually with `git worktree remove --force` |
| Free-tier 429 rate limit hit mid-run | Capture the partial state; offer paid fallback or retry after the rate-limit window resets |

---

## 7. Cleanup on success

```bash
# Triggered after QA PASS
git worktree remove .powerhouse/wt/{id}
# Update ticket status
sed -i 's/^status: dispatched$/status: merged/' .powerhouse/tickets/{id}.md
# Append final row to dispatch-log.md
```

The ticket file is **kept** — it's the audit record of what was built.

---

## 8. What OC sees vs. what CC sees

OpenCode running in `.powerhouse/wt/{id}` sees:

- The full repo at the feature-branch tip
- `CLAUDE.md` (read automatically as fallback for `AGENTS.md`)
- The ticket file passed via `--file`
- The `/follow-ticket` slash command body

OC does **not** see:

- `.claude/agents/*.md` — those are CC-only agent definitions
- Any state from the parent CC session
- Other dispatches running in parallel

This isolation is intentional. Each dispatch is a hermetic execution.

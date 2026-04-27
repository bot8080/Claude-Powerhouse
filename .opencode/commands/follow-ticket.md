---
description: Follow a Powerhouse ticket exactly. Read the ticket file passed as the argument, implement only what's In Scope, touch only Files to Touch, verify each Acceptance Criterion, and emit a structured completion JSON before stopping.
agent: build
model: openrouter/minimax/minimax-m2:free
---

# /follow-ticket

You are running inside a dedicated git worktree at `.powerhouse/wt/{id}/`. Claude Code planned this ticket. Your job is to execute it precisely.

## Inputs

- `$ARGUMENTS` — path to the ticket file, relative to the worktree root (e.g. `.powerhouse/tickets/L2-auth-svc-9f3a.md`)
- The ticket file itself, also attached via `--file` for direct read access
- The repo's `CLAUDE.md` (you should read it for project conventions — it is the canonical project instructions for both Claude Code and OpenCode)

## What you must do

1. **Read the ticket.** Parse the YAML frontmatter and the body. Note especially:
   - `files_to_touch:` — these are the **only** files you may create or edit
   - **Goal**, **In Scope**, **Out of Scope**, **Acceptance Criteria** in the body
2. **Read CLAUDE.md** for project conventions (try/except wrapping, no print() in libraries, naming, layered build order, etc.)
3. **Read each file in `files_to_touch`** if it already exists, so your edits are coherent.
4. **Implement only what is In Scope.** Do not add features. Do not refactor unrelated code. Do not "improve" things that aren't broken. Do not touch files outside `files_to_touch` — not even for a one-line "while I'm here" cleanup.
5. **Verify each Acceptance Criterion** is satisfied by your changes. Be honest — if you can't verify one, mark it `n/a` or `fail` in your completion JSON.
6. **Emit the completion JSON** as the final output. Then stop.

## Hard rules

- **Never** edit a file not listed in `files_to_touch`.
- **Never** create a new file not listed in `files_to_touch`.
- **Never** delete a file unless deletion is explicitly stated in the ticket body.
- **Never** run destructive git commands (`reset --hard`, `clean -f`, branch deletion).
- **Never** make a commit unless the ticket explicitly tells you to. The Claude Code dispatcher handles commits and merging.
- **Never** start a follow-up task. Stop after the completion JSON.

## Completion JSON format (mandatory final output)

The very last line you print must be a single line of JSON:

```json
{"type": "completion", "ticket_id": "<id from frontmatter>", "files_changed": ["<path1>", "<path2>"], "ac_status": [{"criterion": "<criterion text>", "status": "pass|fail|n/a", "evidence": "<short note>"}], "out_of_scope_skipped": ["<thing you noticed but didn't do>"], "notes": "<any caveats>"}
```

Field rules:
- `files_changed` — actual paths you wrote to (verify with your tools), must be a subset of `files_to_touch`.
- `ac_status` — one entry per Acceptance Criterion in the ticket body, in the same order.
- `out_of_scope_skipped` — things you noticed (bugs, code smells, missing tests) but did **not** fix because they were out of scope. This helps Claude Code decide if a follow-up ticket is needed.
- `notes` — anything else the reviewer needs to know (e.g. "tests pre-existing for this file already cover the new code path").

## What if the ticket is unclear?

If the ticket is genuinely ambiguous (e.g. an acceptance criterion contradicts the In Scope list, or a required file is missing from `files_to_touch`), do **not** guess. Emit a completion JSON with `ac_status` entries marked `n/a` and a `notes` field explaining the ambiguity. Make zero file edits. Stop. Claude Code will revise the ticket and re-dispatch.

Better to do nothing than to do the wrong thing — Claude Code is paying for the QA review and the merge gate. Ambiguity is a "send it back" signal, not a "make a judgement call" signal.

---
name: opencode-handoff
description: >
  Use this skill to hand off mechanical coding work from Claude Code to OpenCode running
  the free MiniMax M2 model — saving Claude tokens for planning and review.
  Triggers: "send to opencode", "dispatch", "/dispatch", "minimax this", "opencode handoff",
  "let opencode handle this", "offload this task", "run this with opencode".
---

# OpenCode Handoff

**Claude Code plans + reviews. OpenCode executes. `dispatch.sh` handles everything in between.**

---

## Two commands

### `/dispatch <description>`

1. Ask PM Tech Lead to write a ticket for the task (simplified 4-field format — see `SCHEMA.md`)
2. Confirm the ticket looks right, then run:
   ```bash
   bash .powerhouse/dispatch.sh .powerhouse/tickets/<id>.md
   ```
3. Wait for the script to finish. It handles worktree, OC invocation, diff check, and logging.
4. On **hard failure** (OC not installed, auth missing, zero changes, non-zero exit): the script prints Dev Engineer fallback instructions — say "Dev Engineer: pick up ticket `<path>`"
5. On **soft failure** (files touched outside scope): the script prints options — choose 1/2/3

### `/dispatch-review`

Load `.claude/agents/qa-engineer.md` and run a full QA pass against the worktree at `.powerhouse/wt/<id>/`. On PASS, merge and remove the worktree. On FAIL, prompt user to re-dispatch a fix-up ticket or have Dev Engineer patch directly.

---

## Should I dispatch this?

Judge in one line: *Is this mechanical, well-bounded, and do I know exactly which files to touch?*

- **Yes** → write the ticket and dispatch
- **Borderline** → say the score aloud and ask the user to choose
- **No** → keep in Claude Code, no mention of dispatch needed

Don't print a 3-axis breakdown for clear cases. Only show reasoning when it's genuinely borderline.

---

## First time setup

Run once: `bash .powerhouse/setup.sh`

This verifies opencode is installed, OpenRouter is authed, and all required files are present.

---

## Pipeline position

```
PM Tech Lead → dispatch.sh (OpenCode) → QA Engineer → Human Approve → Merge
                      ↓ hard fail
               Dev Engineer → QA Engineer → Human Approve → Merge
```

Dev Engineer always uses the **original ticket** and a **fresh worktree** — never OC's partial work.

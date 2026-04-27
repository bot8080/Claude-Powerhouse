# /powerhouse

Unified command skill for Claude-Powerhouse. Routes all development intent through a single entry point.

---

## Sub-Commands

### `status [--project <name>]`

Show the current build state.

1. Detect active sub-project (CWD → explicit flag → prompt if ambiguous)
2. Read `BUILD_STATUS.md` for that sub-project (or root if at repo root)
3. Print:
   - Current layer number and name
   - Last completed task (most recent ✅)
   - Next unchecked task (first `- [ ]`)
   - Count of remaining tasks in current layer
4. If `BUILD_STATUS.md` is missing, say: "No BUILD_STATUS.md found. Run `/powerhouse plan` to set up the project."

---

### `plan [feature description]`

Invoke PM Tech Lead to create a structured ticket.

1. Load `.claude/agents/pm-tech-lead.md`
2. Detect active sub-project
3. Check spec gate (TECH_SPEC.md + BUILD_STATUS.md exist)
4. Check layer gate (previous layer fully checked)
5. Produce ticket using PM Tech Lead output format
6. Wait for human approval before proceeding

---

### `build`

Invoke Dev Engineer to implement the current approved ticket.

1. Confirm an approved ticket exists in the conversation
2. Load `.claude/agents/dev-engineer.md`
3. Run pre-flight checks (branch, spec)
4. Implement the ticket
5. Report files changed + acceptance criteria met
6. Hand off to QA with "Ready for QA Engineer review."

---

### `review`

Invoke QA Engineer to validate the current implementation.

1. Load `.claude/agents/qa-engineer.md`
2. Run full QA checklist
3. Produce QA report
4. On PASS: instruct user to merge, then run `/powerhouse pr`
5. On FAIL: return issues to Dev Engineer

---

### `branch [name]`

Create a properly named feature branch.

1. Detect active sub-project (CWD or --project flag)
2. Detect current layer number from sub-project `BUILD_STATUS.md`
3. Map sub-project to key: `investment-brain` | `market-intelligence` | `powerhouse`
4. Run: `git checkout -b feature/{subproject}/L{N}-{name}`
5. Confirm branch created and checked out

Example: `/powerhouse branch installable` from inside `mcps/investment-brain/` on Layer 7
→ creates `feature/investment-brain/L7-installable`

---

### `pr`

Prepare and create a pull request.

1. Run syntax/type checks for the active sub-project
2. `git fetch origin main && git rebase origin/main`
3. `git push -u origin <current-branch>`
4. Create PR with this template:

```
## Summary
- [what this ticket implemented]
- [layer number and name]

## Acceptance Criteria
- [ ] [from the ticket]

## QA
- Result: PASS
- Smoke test: ✅

## BUILD_STATUS update
After merge, check off: [task name] in BUILD_STATUS.md on main.
```

---

### `next`

Find the next unchecked task across all active sub-projects.

1. Read root `BUILD_STATUS.md`
2. Read `mcps/market-intelligence/BUILD_STATUS.md` if it exists
3. Read `mcps/investment-brain/BUILD_STATUS.md` if it exists
4. Print the first unchecked `- [ ]` item from each, with sub-project label
5. Suggest: "Run `/powerhouse plan [task]` to start the next ticket."

---

## Sub-Project Detection Logic

```
1. User passes --project <name>        → use it
2. CWD contains "market-intelligence"  → project = market-intelligence
3. CWD contains "investment-brain"     → project = investment-brain
4. CWD is repo root                    → show root BUILD_STATUS.md
5. Ambiguous                           → ask: "Which project? (market-intelligence / investment-brain / root)"
```

---

## Hard Rules

- Never skip the PM Tech Lead ticket step for any feature work
- Never merge without a QA PASS report
- Never update BUILD_STATUS.md on a feature branch — only on main after merge
- Never ask the user "which agent should I use?" — route automatically

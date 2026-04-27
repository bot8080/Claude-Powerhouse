# Ticket Schema

Every ticket under `.powerhouse/tickets/{id}.md` must conform to this schema.

Both Claude Code (planner + reviewer) and OpenCode (executor) parse this. Keep it stable.

---

## Filename

`{id}.md` where `id = {layer}-{slug}-{shortid}` and `shortid` is 4 hex chars.

Examples: `L2-auth-svc-9f3a.md`, `L1-types-config-c0a3.md`

---

## YAML Frontmatter

```yaml
---
id: L2-auth-svc-9f3a
layer: 2
sub_project: investment-brain        # root | market-intelligence | investment-brain | <new>
branch: feature/L2-auth-svc          # feature/L{N}-{slug}
dispatch_score: 8                    # 0..9, total from classifier
score_breakdown:
  spec_clarity: 3                    # 0..3
  mechanical: 3                      # 0..3
  blast_radius_inverted: 2           # 0..3 (3 = lowest blast)
model: openrouter/minimax/minimax-m2:free
status: planned                      # planned | dispatched | reviewing | merged | failed
files_to_touch:
  - src/services/auth.py
  - tests/services/test_auth.py
created_at: 2026-04-27T18:32:00Z
created_by: claude-code              # claude-code | human
---
```

### Field rules

| Field | Required | Notes |
|---|---|---|
| `id` | yes | Must match filename stem |
| `layer` | yes | Integer 1..7, matches CLAUDE.md layer table |
| `sub_project` | yes | Use `root` for monorepo-level work |
| `branch` | yes | Always `feature/L{N}-{slug}` |
| `dispatch_score` | yes | 0..9 |
| `score_breakdown` | yes | All three sub-scores must be present |
| `model` | yes | Fully qualified `provider/model` for OpenCode |
| `status` | yes | Lifecycle state |
| `files_to_touch` | yes | Exhaustive list — OC may not touch others |
| `created_at` | yes | ISO 8601 UTC |
| `created_by` | yes | Audit field |

---

## Body

After the closing `---`, write the standard PM Tech Lead ticket body:

```markdown
## Ticket: <short name>

**Layer:** N — <Layer Name>
**Sub-project:** <name>
**Branch:** feature/L{N}-<short-name>

### Goal
<One sentence: what this ticket accomplishes>

### In Scope
- <bullet list of exactly what must be built>

### Out of Scope
- <bullet list of what is explicitly NOT included>

### Acceptance Criteria
- [ ] <testable criterion 1>
- [ ] <testable criterion 2>

### Files to Touch
- <file path> — <what changes>

### Spec References
- TECH_SPEC.md § <section>
- CLAUDE.md § <section>
```

The body is identical to the existing `.claude/agents/pm-tech-lead.md` output format. The frontmatter is the only addition.

---

## Lifecycle

```
planned ──► dispatched ──► reviewing ──► merged
   │             │              │
   │             ▼              ▼
   └──────► failed (any time, with reason in dispatch-log.md)
```

State transitions are written by:
- `planned` — PM Tech Lead writes the ticket
- `dispatched` — opencode-dispatcher agent at start of OC run
- `reviewing` — QA Engineer at start of review
- `merged` — opencode-dispatcher agent on QA PASS
- `failed` — anyone, with a row in dispatch-log.md

---

## Validation

The dispatcher refuses to run a ticket if:

- Any required field is missing or empty
- `id` doesn't match filename
- `dispatch_score < 4` (always reject)
- `dispatch_score in 4..6` and no human override note in the body
- `status != planned` at dispatch time (a ticket can only be dispatched once)
- `files_to_touch` is empty

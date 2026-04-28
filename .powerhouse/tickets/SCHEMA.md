# Ticket Schema

Every ticket under `.powerhouse/tickets/{id}.md` must conform to this schema.

Both Claude Code (planner + reviewer) and OpenCode (executor) read this. Keep it stable.

---

## Filename

`{id}.md` where `id = {slug}-{timestamp}` — slug is a short kebab-case description, timestamp is Unix seconds (last 6 digits).

Examples: `auth-svc-239f3a.md`, `rsi-indicator-c0a312.md`

---

## YAML Frontmatter

```yaml
---
id: auth-svc-239f3a
branch: feature/investment-brain/auth-svc
files_to_touch:
  - src/services/auth.py
  - tests/services/test_auth.py
acceptance_criteria:
  - Auth token is returned on valid login
  - Invalid credentials return 401
---
```

### Field rules

| Field | Required | Notes |
|---|---|---|
| `id` | yes | Must match filename stem |
| `branch` | yes | `feature/{subproject}/{slug}` — must exist before dispatch |
| `files_to_touch` | yes | Exhaustive list — OC may not touch files outside this list |
| `acceptance_criteria` | yes | Testable, one criterion per line — QA Engineer checks each one |

---

## Body

After the closing `---`, write the ticket body:

```markdown
## Goal
<One sentence: what this ticket accomplishes>

## In Scope
- <bullet: exactly what must be built>

## Out of Scope
- <bullet: explicitly excluded>

## Notes
<Any context OC needs: patterns to follow, gotchas, relevant CLAUDE.md sections>
```

---

## Dispatch rules

`dispatch.sh` refuses to run if:

- Any required frontmatter field is missing or empty
- `files_to_touch` is empty
- The branch does not exist in git
- A worktree for this id already exists under `.powerhouse/wt/`

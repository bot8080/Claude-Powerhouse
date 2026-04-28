---
id: L1-warn-missing-specs-a3f2
layer: 1
sub_project: root
branch: feature/powerhouse/L1-warn-missing-specs
dispatch_score: 9
score_breakdown:
  spec_clarity: 3
  mechanical: 3
  blast_radius_inverted: 3
model: openrouter/minimax/minimax-m2:free
status: planned
files_to_touch:
  - .claude/hooks/warn-missing-specs.sh
created_at: 2026-04-27T00:00:00Z
created_by: claude-code
---

## Ticket: warn-missing-specs advisory hook

**Layer:** 1 — Infrastructure & Workflow Setup  
**Sub-project:** root (powerhouse meta)  
**Branch:** feature/powerhouse/L1-warn-missing-specs

### Goal

Create a pre-tool-use hook that warns (but does not block) when Claude is about to edit source files in a sub-project that is missing `TECH_SPEC.md` or `BUILD_STATUS.md`.

### In Scope

- `.claude/hooks/warn-missing-specs.sh` — bash script that:
  1. Reads `CLAUDE_TOOL_INPUT` (the JSON payload Claude Code passes to hooks)
  2. Extracts the file path being edited (the `file_path` field for Write/Edit tools)
  3. Detects which sub-project the file belongs to by checking for `mcps/` or `skills/` prefix
  4. Resolves the sub-project root (e.g. `mcps/investment-brain/`)
  5. Checks whether both `TECH_SPEC.md` and `BUILD_STATUS.md` exist in that root
  6. If either is missing, prints a warning to stderr: `[spec-gate] WARNING: <subproject> is missing <file> — consider writing the spec first.`
  7. Always exits 0 (advisory only, never blocks)
  8. Skips the check when:
     - The file being edited IS `TECH_SPEC.md` or `BUILD_STATUS.md`
     - The file is in the repo root (no sub-project prefix)
     - The file is in `.claude/`, `.powerhouse/`, or `skills/`

### Out of Scope

- Blocking / non-zero exit on missing specs (advisory only per CLAUDE.md)
- Checking any sub-projects other than those under `mcps/`
- Modifying `settings.json` (the hook registration is already in the hook file as a comment)
- Unit tests

### Acceptance Criteria

- [ ] Script is executable (`chmod +x`) and has a `#!/usr/bin/env bash` shebang
- [ ] Editing a file under `mcps/some-project/` with a missing `TECH_SPEC.md` prints the warning to stderr
- [ ] Editing a file under `mcps/some-project/` when both spec files exist produces no output
- [ ] Editing `TECH_SPEC.md` itself produces no output (skip condition)
- [ ] Script always exits 0 regardless of any condition
- [ ] `market-intelligence` sub-project is explicitly exempted (comment explains why: shipped before spec discipline)

### Files to Touch

- `.claude/hooks/warn-missing-specs.sh` — new file, bash hook script

### Spec References

- CLAUDE.md § Spec Gate (Advisory)
- CLAUDE.md § MCP Servers — market-intelligence (exempt note)

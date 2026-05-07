# TECH_SPEC.md — Claude-Powerhouse Merger

**Version:** 1.0.0  
**Date:** 2026-05-06  
**Status:** Implementation

---

## Overview

Merger of `development-protocols` (project scaffolding CLI + templates) into `Claude-Powerhouse` (spec-first, layer-gated agent pipeline) to create a unified development workflow tool.

---

## CLI Commands Schema

### `npx powerhouse init [name]`

**Purpose:** Interactive project scaffolding with stack + addon selection.

**Arguments:**
- `name` (optional): Project name. If omitted, prompts interactively.
- `.` : Create in current directory.

**Flow:**
1. Prompt for project name (if not provided)
2. List available stacks from `templates/stacks/*/stack.json`
3. User selects stack
4. Prompt for addons:
   - Backend: None / Firebase / Supabase
   - Payments: No / Stripe
   - AI Workflow: None / OpenCode
5. Copy `templates/workflow/` with `{{VAR}}` interpolation
6. Copy `templates/stacks/{selected}/` (raw files)
7. Copy `templates/addons/{selected}/` (if chosen)
8. Run `INSTALL_CMD` from stack.json

**Variables (from stack.json):**
```typescript
{
  PKG_MANAGER: string;      // "npm" | "yarn" | "pnpm"
  TYPECHECK_CMD: string;    // e.g., "npx tsc --noEmit"
  LINT_CMD: string;         // e.g., "npm run lint"
  TEST_CMD: string;         // e.g., "npm test"
  START_CMD: string;        // e.g., "npx expo start"
  INSTALL_CMD: string;      // e.g., "npm install --legacy-peer-deps"
  NODE_VERSION: string;     // e.g., "20"
  STACK: string;            // e.g., "Expo (React Native)"
  LANGUAGE: string;         // e.g., "TypeScript"
}
```

---

### `npx powerhouse apply`

**Purpose:** Add workflow conventions to existing project (non-destructive).

**Files Copied:**
- `AGENTS.md`, `QUICKSTART.md`, `CLAUDE.md`, `opencode.json`
- `.claude/`, `.github/`, `.husky/`, `docs/`, `session-tracking/`

**Rules:**
- Skips existing files (no overwrites)
- Skips `.template` extension files
- Never touches source code

---

## Template Structure Contract

### `stack.json` Schema

```typescript
{
  name: string;              // Display name
  language: string;          // "TypeScript" | "JavaScript" | ...
  variables: {
    PKG_MANAGER: string;
    TYPECHECK_CMD: string;
    LINT_CMD: string;
    TEST_CMD: string;
    START_CMD: string;
    INSTALL_CMD: string;
    INSTALL_FLAGS?: string;
    NODE_VERSION: string;
    STACK: string;
    LANGUAGE: string;
  };
  hooks?: {
    pre_commit?: string[];   // Commands to run before commit
  };
}
```

### Addon Contract

Each addon directory must be self-contained:
- `README.md` or `SETUP.md` — Installation + configuration guide
- Source files — Copied as-is to project root
- No variable interpolation (addons are raw copies)

---

## Agent Pipeline Signatures

### PM Tech Lead

**Input:** Feature description  
**Output:** Ticket file at `.powerhouse/tickets/{id}.md`

```markdown
---
id: {slug}-{hash}
branch: feature/{subproject}/L{N}-{slug}
files_to_touch:
  - path/to/file.ts
acceptance_criteria:
  - Criterion 1
  - Criterion 2
dispatch_score: 0-9
---

## Goal
[One sentence]

## In Scope
[Bullet list]

## Out of Scope
[Bullet list]

## Notes
[Context, patterns, gotchas]
```

### Dev Engineer

**Pre-flight:**
1. Confirm ticket exists
2. Confirm branch: `feature/{subproject}/L{N}-{name}`
3. Verify against `TECH_SPEC.md` schemas

**Rules:**
- Implement ticket exactly — no scope creep
- All external calls `try/except` wrapped
- No `print()` in library code
- No hard-coded credentials/paths
- Docstrings on all new functions

### QA Engineer

**7-Point Checklist:**
1. Spec compliance — schemas match `TECH_SPEC.md`
2. Scope compliance — matches In Scope, nothing from Out of Scope
3. Code quality — error handling, no secrets, no `print()`
4. Acceptance criteria — each criterion verifiable
5. Syntax check — `python -m py_compile` or `tsc --noEmit`
6. Smoke test — quick live test
7. Browser verification (web only) — no JS errors, key elements visible

**Output:** PASS/FAIL report

---

## Layer Map (This Merger)

| Layer | Task | Files |
|-------|------|-------|
| 1 | Directory structure | `cli/`, `templates/`, `.agents/` |
| 2 | CLI scripts | `cli/cli.js`, `cli/init.js`, `cli/apply.js` |
| 3 | Templates | `templates/workflow/`, `templates/stacks/`, `templates/addons/` |
| 4 | Agent definitions | `.claude/agents/advisor.md`, `.agents/agents/` |
| 5 | Config files | `package.json`, `opencode.json` |
| 6 | Documentation | `README.md`, `TECH_SPEC.md` |
| 7 | Testing | CLI test, skill test |

---

## Service Interfaces

### Stack Discovery

```typescript
function listStacks(): string[] {
  // Read templates/stacks/ directories
  // Filter for those with stack.json
  // Return directory names
}
```

### Variable Interpolation

```typescript
function copyDir(
  src: string,
  dest: string,
  replacements: Record<string, string>,
  stripTemplateExt: boolean
): void {
  // Recursive copy
  // Replace {{VAR}} tokens
  // Strip .template extension if flag set
}
```

### Sub-Project Detection

```typescript
function detectProject(): string {
  // 1. --project <name> flag → use it
  // 2. CWD contains "market-intelligence" → "market-intelligence"
  // 3. CWD contains "investment-brain" → "investment-brain"
  // 4. CWD is repo root → "root"
  // 5. Ambiguous → prompt user
}
```

---

## Error Handling

| Error | Handling |
|-------|----------|
| Missing `templates/` | Exit with "Reinstall claude-powerhouse" |
| Missing `stack.json` | Exit with "Stack not found or missing stack.json" |
| Directory exists (init) | Exit with "Directory already exists" |
| No `package.json` (apply) | Proceed — works on non-NPM projects too |
| Install fails | Log warning, suggest manual install |

---

## Testing Strategy

### CLI Tests

```bash
# Help command
node cli/cli.js --help

# Init (dry run in temp dir)
cd C:\Users\abhik\AppData\Local\Temp\opencode
node F:\Projects\Claude-Powerhouse\cli\init.js test-app

# Apply (on existing project)
cd F:\Projects\Claude-Powerhouse
node cli/apply.js
```

### Skill Tests

```bash
# In Claude Code
/pst status
/pst next
/pst branch test-feature
```

---

## Migration Notes

### From development-protocols

- Package renamed: `development-protocols` → `claude-powerhouse`
- CLI renamed: `development-protocols` → `powerhouse`
- Templates moved: `scripts/` → `cli/`
- Added: `.agents/` directory for cross-tool compatibility

### From Powerhouse

- No breaking changes
- Added: CLI scaffolding commands
- Added: `.agents/` alias
- Added: `advisor.md` agent

---

## Unknowns / Risks

| Risk | Mitigation |
|------|------------|
| Template variable conflicts | Test init in temp directory before committing |
| Agent definition conflicts | Keep Powerhouse versions, only add `advisor.md` |
| CLI path issues | Test `npx powerhouse` locally before publishing |
| Session tracking duplication | Document both methods as complementary |

---

## Success Criteria

- [ ] `npx powerhouse init my-app` scaffolds Expo project
- [ ] `npx powerhouse apply` adds conventions to existing project
- [ ] `/pst status` shows correct layer + next task
- [ ] `/pst plan/build/review` pipeline works end-to-end
- [ ] `@advisor` is available for ad-hoc help
- [ ] All 7 layers of both MCP servers remain functional
- [ ] CI/CD + Husky hooks work in scaffolded projects
- [ ] Session tracking (shell + git) documented and tested


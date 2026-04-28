---
id: powerhouse-techspec-372710
branch: feature/powerhouse/meta-techspec
files_to_touch:
  - TECH_SPEC.md
acceptance_criteria:
  - TECH_SPEC.md exists at repo root covering the powerhouse meta-project
  - Agents section documents all 5 agent roles, trigger phrases, and output contracts
  - Skills section documents all 5 current skills with target (CLI/Web/Both) and trigger
  - Dispatch pipeline section documents dispatch.sh inputs/outputs and failure modes
  - Hooks section documents warn-missing-specs.sh and check-gstack.sh behavior
---

## Goal

Write a root `TECH_SPEC.md` for the Claude-Powerhouse meta-project (the infra layer: agents, skills, hooks, dispatch pipeline) so we enforce on ourselves the same spec discipline we require of sub-projects.

## In Scope

- Document all 5 agents in `.claude/agents/` — role, trigger phrases, input, output format
- Document all 5 skills in `skills/` — name, target (CLI/Web/Both), trigger, what it produces
- Document the dispatch pipeline — `dispatch.sh` inputs, outputs, hard/soft failure modes, worktree lifecycle
- Document hooks — what each hook checks, when it fires, what it blocks/warns

## Out of Scope

- No changes to agent files or skill files
- No new agents or skills
- No changes to dispatch.sh or setup.sh
- No SCREEN_SPEC (CLI/backend project — no UI)

## Notes

- Follow the same format as `mcps/investment-brain/TECH_SPEC.md` (module map table + data models)
- The "data models" equivalent here is the ticket schema (from `.powerhouse/tickets/SCHEMA.md`) and the dispatch log format
- Dispatch score ≥ 7 — good OpenCode candidate (mechanical doc-writing, bounded to one file)

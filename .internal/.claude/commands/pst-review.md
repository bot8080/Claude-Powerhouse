---
name: pst-review
description: Invoke QA Engineer to validate changes against specs
---
Load `.internal/.claude/agents/qa-engineer.md` and activate the QA Engineer agent.

Run the 7-point checklist:
1. Spec compliance — schemas match TECH_SPEC.md
2. Scope compliance — no out-of-scope code
3. Code quality — error handling, no secrets
4. Acceptance criteria — each criterion verifiable
5. Syntax check — run project type checker
6. Smoke test — quick live test
7. Browser verification (web projects only)

Output: PASS/FAIL report.

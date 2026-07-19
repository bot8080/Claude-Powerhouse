---
name: pst-plan
description: Invoke PM Tech Lead to produce a structured ticket for a feature
---
Load `.internal/.claude/agents/pm-tech-lead.md` and activate the PM Tech Lead agent for the given feature description.

Steps:
1. Check spec gate (TECH_SPEC.md + BUILD_STATUS.md exist)
2. Check layer gate (N-1 is complete)
3. Produce structured ticket at `.internal/.powerhouse/tickets/{id}.md`
4. Print ticket summary with branch name and dispatch recommendation

---
name: pst-build
description: Invoke Dev Engineer to implement the current ticket
---
Load `.internal/.claude/agents/dev-engineer.md` and activate the Dev Engineer agent.

Pre-flight:
1. Confirm a ticket exists in `.internal/.powerhouse/tickets/`
2. Confirm correct branch (`feature/{subproject}/L{N}-{name}`)
3. Read TECH_SPEC.md for schema compliance

Then implement the ticket exactly, no scope creep.

---
name: follow-ticket
description: Execute a PST ticket — implement acceptance criteria, no scope creep
---
Load the ticket from `.internal/.powerhouse/tickets/<id>.md` and implement exactly:

1. Read files_to_touch list
2. Read TECH_SPEC.md for the active sub-project
3. Implement each acceptance criterion — no scope creep
4. All external calls: try/except wrapped
5. No print() in library code
6. No hard-coded credentials or paths
7. Docstrings on all new functions

When done: write results to dispatch log and exit.
Output format: list of files changed + acceptance criteria confirmed.

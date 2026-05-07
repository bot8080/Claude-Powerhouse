---
name: pst-pr
description: Type-check, rebase, push, and create a PR
---
Finish-feature flow:
1. Run type-checker for the active sub-project
2. Sync main: `git fetch origin main && git rebase origin/main`
3. Push: `git push -u origin HEAD`
4. Create PR using `gh pr create` with standard template

Do not update BUILD_STATUS.md — that happens on main after merge.

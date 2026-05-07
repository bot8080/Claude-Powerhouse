---
name: pst-next
description: Find first unchecked item across all sub-projects
---
Scan all BUILD_STATUS.md files (root + mcps/*/) and report the first unchecked task across all projects.

Use `.powerhouse/lib/pst-next.sh` for the full scan.

Then suggest the next action: plan it, build it, or move to a different project.

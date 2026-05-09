---
name: pst-status
description: Show current layer and next unchecked task from BUILD_STATUS.md
---
Read `BUILD_STATUS.md` for the active sub-project and report:
1. Current layer
2. First unchecked task
3. Any uncommitted work

Use `.powerhouse/lib/pst-status.sh` with optional `--project <name>` to scope to a sub-project.

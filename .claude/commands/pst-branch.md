---
name: pst-branch
description: Create a feature branch following the project naming convention
---
Create a new feature branch from `main` following: `feature/{subproject}/L{N}-{name}`

Usage: `/pst branch <name>`

Steps:
1. Determine active sub-project (via CWD or --project)
2. Determine next layer number from BUILD_STATUS.md
3. Run: `git checkout main && git pull && git checkout -b feature/{subproject}/L{N}-{name}`

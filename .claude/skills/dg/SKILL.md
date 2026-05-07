# Skill: dg — Project Command Center

Unified entry point for the development workflow.

## /dg or /dg status

Show current project status and suggest next task.

1. Run `git branch --show-current`
2. Run `git rev-list --left-right --count origin/main...HEAD`
3. Run `git status --porcelain | measure | % { $_.Lines }` for dirty file count
4. Summarize: branch, behind/ahead, dirty files

## /dg plan [feature]

Produce a structured ticket for the next feature:
1. Read `docs/CONVENTIONS.md`
2. Read `docs/ARCHITECTURE.md`
3. Produce: title, acceptance criteria, files to create/modify, dependencies

## /dg branch [type] [name]

Create a properly named branch:
- `feature/<name>` — features
- `chore/<name>` — config, meta
- `docs/<name>` — documentation
- `release/v<version>` — releases (from main)
- `hotfix/v<version>` — hotfixes (from main)

## /dg review

Review current changes:
1. Run `git diff --stat`
2. Run `git diff`
3. Check: type errors, lint errors, convention violations

## /dg pr

Create a pull request:
1. Run `{{TYPECHECK_CMD}}`
2. Run `{{TEST_CMD}}`
3. Create PR with `gh pr create`

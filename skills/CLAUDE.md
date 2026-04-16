# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Repo Is

A collection of Claude AI skills — `.skill` files that extend Claude's behavior in Claude.ai. Skills are installed by users via **Settings → Skills** and trigger automatically based on natural language matching.

## Skill File Structure

Each skill lives in its own folder:

```
skill-name/
  skill-name.skill   ← the installable skill file
  README.md          ← user-facing documentation
```

The `.skill` file format:
- YAML frontmatter block (`---`) with `name:` and `description:` fields
- The `description:` field is the trigger — Claude reads it to decide when to activate the skill
- Body is markdown: the actual instructions Claude follows when the skill activates

## Adding a New Skill

1. Create `skill-name/skill-name.skill` with YAML frontmatter + markdown instructions
2. Create `skill-name/README.md` explaining what it does, how to install, and usage examples
3. Add a row to the skills table in the root `README.md`

## Key Authoring Conventions

- The `description:` in the frontmatter determines when the skill fires — make it exhaustive with trigger phrases, synonyms, and intent patterns
- Skill instructions should be self-contained — assume no other context is available
- Follow the `ai-project-setup-kit` pattern: detect context first, then branch into modes
- Skills that involve file output should use `present_files` and save to `/mnt/user-data/outputs/`

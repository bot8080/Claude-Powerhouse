---
name: Powerhouse-Claud-Project-Setup-Kit
description: >
  Use this skill whenever the user wants to CREATE a new AI project from scratch OR IMPROVE/audit an existing project's knowledge base and instruction files. Triggers include: "create a new project for X", "help me set up a project", "build a knowledge base for my project", "improve my project instructions", "audit my knowledge base files", "my project files are getting messy", "simplify my project", "restructure my project docs", "my AI instructions are too complex", "refresh my knowledge base", or any mention of wanting better project organization for AI assistants. Always use this skill when the user is thinking about project setup, project instructions (system prompts), or knowledge base files — even if they don't use those exact words.
---

# Powerhouse Claud Project Setup Kit v2

A skill for creating new Claude projects or auditing and improving existing ones.

Goal: projects that work reliably across many conversations without bloating Claude's context window.

---

## Core Design Principles

These override all other guidance in this skill. When in doubt, return here.

1. **Instructions are a finite resource.** Every word in project_instructions.md consumes tokens in every conversation. Keep project instructions concise and focused on essential information — general context, key guidelines, and Claude's role. Reserve task-specific instructions for the chat itself.

2. **Right altitude, not maximum altitude.** Two failure modes exist: overly rigid/brittle instructions vs. overly vague ones. The sweet spot is specific enough to guide behavior effectively, yet flexible enough to apply heuristics. Prefer explaining the *why* over prescribing the exact *how*.

3. **Claude Projects use RAG automatically.** Knowledge base files are retrieved based on relevance to the conversation. Do NOT hardcode routing maps with trigger keywords for each file — this wastes instruction tokens and goes stale. Make each knowledge file clearly titled and well-structured so the retriever finds it. Only add routing hints if testing proves the retriever consistently misses a file.

4. **Test, then iterate.** A project that looks perfect on paper may fail in practice. The project is not done until tested with real prompts.

---

## Detecting the Mode

- **Mode 1 — CREATE**: User wants a new Claude project for a specific goal/domain
- **Mode 2 — IMPROVE**: User wants to audit/improve an existing project

If unclear, ask: "Are you starting a new project from scratch, or improving an existing one?"

---

## Mode 1: Create New Project

### Step 1 — Understand the Goal

Ask the user:
1. What is the project for?
2. Who will use it? (just them, a team, end users?)
3. What specific tasks or workflows should Claude handle?
4. Any hard constraints (things Claude must always or never do)?
5. How much domain knowledge do they already have?

### Step 2 — Research (Calibrated to Need)

Research depth should match the gap between what the user knows and what the project needs.

**If the user is a domain expert** (they built the workflow, they know the terminology):
Do 3–5 targeted searches to fill specific gaps, verify current best practices, and check for anything they might have missed. Ask what gaps they want filled.

**If the user is exploring a new domain:**
Do thorough research (8–12 searches) across these categories:

| Category | Example query pattern |
|---|---|
| Domain overview | "[domain] best practices 2025" |
| Workflows | "how to structure [task type]" |
| Common failures | "[domain] mistakes to avoid" |
| Templates/frameworks | "[domain] framework checklist" |

**Research quality rules:**
- Prefer primary sources: official docs, standards, expert guides
- Synthesize across sources — note where experts agree vs. disagree
- Flag outdated content and search for current alternatives
- Do not pad research with low-value searches to hit a count

### Step 3 — Draft the Plan

Present a plan before writing any files:

```
PROJECT PLAN: [Project Name]

Purpose: [1-2 sentence summary]

Files to create:
1. project_instructions.md — [brief description]
2. [topic].md — [what it covers and why it's a separate file]

Key design decisions:
- [Decision 1 and rationale]
- [Decision 2 and rationale]

Estimated instruction size: short / medium / long
  (short = <500 words, medium = 500-1000, long = 1000+)
  Target: as short as possible while covering essentials

Approve this plan before I write the files?
```

Wait for user approval before proceeding.

### Step 4 — Write the Files

#### project_instructions.md

Use only sections that are relevant — skip empty ones:

```markdown
# [Project Name]

## Role
[1-2 sentences: what Claude is and who it serves]

## Context
[Brief background the user would otherwise repeat every conversation.
Include: tech stack, audience, constraints, domain-specific terms.]

## How to Respond
[Behavioral guidance: tone, length, format preferences.
Focus on the 3-5 most important behaviors.
Explain WHY each matters so Claude can generalize.]

## Hard Constraints
[Only genuine dealbreakers. 3-7 items max.
If you are listing more than 7, most are not hard constraints.]

## Workflows
[Only for specific multi-step processes.
Omit entirely for general-purpose projects.]
```

**Sizing guidance:**
- Target: under 800 words (~1,000 tokens)
- If instructions exceed 1,200 words, something is over-specified
- Test: read them aloud. If you are skimming, Claude will too.

**What belongs where:**

| Content type | Location |
|---|---|
| How Claude should behave (applies every conversation) | project_instructions.md |
| Reference material Claude looks up when relevant | Knowledge file (loaded via RAG) |
| Task-specific details, one-off requests | The chat itself |
| Things that change week to week | The chat, not instructions |

#### Knowledge files ([topic].md)

```markdown
# [Clear, Descriptive Title]

## Overview
[What this document covers and when it is useful — helps RAG retrieval]

## [Main Content Sections]
[Clear headers for scanability]

## Quick Reference
[Tables, checklists, or summaries — optional]
```

**File design rules:**
- Each file covers a coherent topic (closely related things can share a file)
- Use descriptive filenames: `celpip_speaking_rubric.md` not `knowledge_1.md`
- Every file should be independently useful — do not require reading another file first
- Keep files under 400 lines unless content genuinely demands more

### Step 5 — Quality Check

Before saving, verify against these criteria:

1. **Token budget**: Under 800 words? If not, what can move to knowledge files or be cut?
2. **Redundancy**: Does anything in instructions duplicate knowledge file content?
3. **Brittleness**: Are there rigid rules that break on edge cases? Rewrite as principles.
4. **Colleague test**: Would a smart human colleague understand the project without 5 follow-up questions?
5. **Ignoring test**: Which instructions would Claude follow from common sense anyway? Cut those.

### Step 6 — Deliver with Testing Guidance

Save all files to `/mnt/user-data/outputs/` and present using `present_files`.

Provide:
- File count and what each covers
- Estimated token cost (word count and rough token estimate)

Then provide 3–5 test prompts the user should try inside their new project:

```
TEST YOUR PROJECT:

Try these prompts in a new conversation inside your project:

1. [Core use case]
2. [Edge case or constraint]
3. [Knowledge file retrieval test]
4. [Specific behavior rule test]

If any produce unexpected results, share the output and we can refine.
```

This step is not optional. A project that has not been tested is a guess.

---

## Mode 2: Improve Existing Project

### Step 1 — Audit All Available Files

Read every knowledge base file and instruction file. Build a picture of:

- Total files and their topics
- Approximate length of each file and the instructions
- Overlap between files
- Outdated or vague sections
- Structural issues (poor headers, mixed topics, walls of text)
- Instruction bloat (redundant rules, contradictions, over-specification)
- Misplaced content (things in instructions that belong in knowledge files, or vice versa)

### Step 2 — Targeted Research

Research only what the audit reveals needs updating:

- **Accuracy check**: Has existing advice been superseded? Search "[topic] best practices [current year]"
- **Gap fill**: For thin sections, search for depth
- **Tooling updates**: If the project references specific tools, verify they are still current

Skip categories where existing content is solid and current.

### Step 3 — Present the Improvement Plan

```
PROJECT AUDIT REPORT

Files Reviewed: [N files]
Total instruction size: [word count] words (~[token estimate] tokens)

Issues Found:
1. [File/section] — [Issue and impact]
2. [File/section] — [Issue and impact]

Proposed Actions:
- Simplify: [what and why]
- Remove Redundancy: [what and where]
- Restructure: [what and how]
- Merge: [which files and why]
- Refresh: [what needs updating]

Estimated result:
- Files before: [N] -> Files after: [N]
- Instruction size: [before] words -> [after] words
- Key improvements: [2-3 bullet points]

Shall I proceed?
```

Wait for user approval.

### Step 4 — Rewrite the Files

Apply approved improvements:

- **Simplification**: Cut rules Claude follows from common sense. Replace paragraph-form rules with concise statements. Remove duplicates within and across files.
- **Redundancy removal**: If two files cover the same concept, keep it in the most relevant file. Add a one-line cross-reference only if truly needed.
- **Restructuring**: Add clear headers. Group related concepts. Move quick-reference material to file bottoms.

### Step 5 — Deliver with Migration Guide

Save all improved files to `/mnt/user-data/outputs/` and present using `present_files`.

Provide a file-by-file action plan:

```
FILES READY — Here's what to do:

1. project_instructions.md
   -> ACTION: REPLACE
   -> Why: [specific reason]

2. [filename].md
   -> ACTION: REPLACE / DELETE / ADD NEW / KEEP
   -> Why: [specific reason]

How to apply:
Step 1 — Open your Claude Project settings
Step 2 — Delete any files marked DELETE
Step 3 — Upload all files marked REPLACE or ADD NEW
Step 4 — Paste project_instructions.md into the custom instructions field

Summary:
- Files: [N before] -> [N after]
- Instruction size: [before] -> [after] words
- Key improvements: [2-3 items]
```

Then provide 3–5 test prompts (same format as Mode 1 Step 6).

---

## Anti-Patterns Reference

See `references/anti-patterns.md` for a full list of failure modes and how to avoid them. Check this before finalizing any project output.

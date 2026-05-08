# Powerhouse Prompt Optimizer v2

> **[CLI + Web]** — Works in Claude Code and Claude.ai

Transform basic instructions into professional-grade prompts using **Anthropic's latest 2025 heuristics.**

> [!IMPORTANT]
> Returns **only** the improved prompt — no preamble, no commentary. Copy-paste into any model.

---

## Before → After

**Your input:**
> "Write a function to sort users by activity"

**What you get back:**

```markdown
You are a senior TypeScript engineer specializing in performance-optimized data structures.

<context>
User activity dashboard with 10,000+ rows. Data arrives as array of user objects
with lastActiveAt (ISO string | null) and activityScore (number | null) fields.
</context>

<task>
Write a type-safe sort function that orders users by:
1. activityScore descending (highest first)
2. lastActiveAt descending (most recent first) as tiebreaker
3. Null values sort to the end
</task>

<constraints>
- O(n log n) time complexity maximum
- Pure function (no mutations)
- Handle edge cases: empty array, all nulls, mixed nulls
- Include Jest tests for all edge cases
</constraints>
```

---

## What It Fixes

| Before ❌ | After ✅ |
|-----------|---------|
| "Write a login function" | Full spec with role + context + constraints + output format |
| "Make it fast" | `O(n log n) max` |
| "Handle errors" | Specific error types and response shapes |
| No user count | "10,000+ rows" → Claude tailors solution |
| No output format | "Return code + tests + explanation" |

---

## How to Use

**Trigger phrases — say any of these:**
- *"Improve this prompt: [your text]"*
- *"Optimize these instructions for an API call"*
- *"Make this prompt follow Anthropic's methodology"*
- *"Clean up this system prompt"*

**Best for:**
- Vague one-liners → full specifications
- Missing context → proper constraints
- Hallucination-prone prompts → hard guardrails
- Any instruction going to Claude, GPT, Gemini, or open-source models

---

## Installation

**Claude.ai web:**
1. Download [Powerhouse-Prompt-Optimizer.skill](./Powerhouse-Prompt-Optimizer.skill)
2. Go to [Claude.ai](https://claude.ai) → **Settings** → **Skills**
3. Click **Install Skill** and upload the file

**Claude Code:** Skills in `.claude/skills/` activate automatically when working in this repo.

---

## Contents

- `SKILL.md` — Core optimization logic and heuristics
- `references/prompt-types.md` — System vs User vs API prompt guidelines
- `Powerhouse-Prompt-Optimizer.skill` — Installable distributable

---

## Related

| Skill | Purpose |
|-------|---------|
| [Project Setup Kit](../Powerhouse-Claud-Project-Setup-Kit/) | Set up project knowledge base |
| [Software Team](../Powerhouse-software-team/) | Full PM→Dev→QA pipeline |

---

*Part of the [Claude-Powerhouse](../../README.md) suite.*

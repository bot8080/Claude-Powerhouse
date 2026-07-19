# Powerhouse Claude Project Setup Kit

> **You are here:** Home → Skills → Project Setup Kit
>
> **[CLI + Web]** — Works in Claude Code and Claude.ai

A professional-grade **AI Workspace Architect** — creates new Claude projects from scratch or audits and improves existing ones.

> [!TIP]
> Use when:
> - Your CLAUDE.md feels bloated (>2000 words)
> - Claude ignores uploaded knowledge base files
> - Agents give inconsistent answers
> - You want a new professional-grade assistant

---

## Before → After

**Before (bloated instructions, 2500+ words):**

```
You are a helpful assistant for my financial analysis project.
Here are all the rules:
1. Always check the market data first
2. Never give investment advice
3. Use the files in /knowledge for reference
4. If unsure, ask the user
5. Be professional but friendly
... [20+ more rules, many contradictory]
```

**After (principles-based, ~180 words):**

```
## Role
You are a financial analysis assistant. Your job is to:
1. Fetch and interpret market data
2. Present analysis clearly with sources
3. Never give licensed investment advice

## Principles
- Data-first: Always ground answers in fetched data, never speculate
- Transparent: Show your work — users trust reasoning they can verify
- Conservative: When data is missing, say "I don't have that data" rather than estimating

## Knowledge Base
Files in /knowledge/ are your source of truth.
Cite them like: [knowledge:valuation-methods.md]

## Output Format
For analysis requests:
1. Summary (2-3 sentences)
2. Data table (if applicable)
3. Methodology (which files/data you used)
4. Confidence level (high/medium/low + why)
```

---

## Key Features

| Feature | What It Does | Result |
|---------|--------------|--------|
| **Principles-Based** | Replaces rigid rules with flexible heuristics | Claude generalizes better |
| **Audit & Refine** | Deep analysis of existing instruction files | Roots out redundancy, contradictions |
| **RAG Optimization** | Structures knowledge base files for retrieval | Maximum accuracy on first try |
| **Token Efficiency** | Targets sub-800 word "gold standard" | Saves context window for actual work |

---

## How to Use

**Trigger phrases:**
- *"Help me set up a new project for [domain]"*
- *"Audit my current project instructions — they're getting messy"*
- *"Build a professional knowledge base for my coding project"*
- *"My Claude keeps ignoring the knowledge base — fix it"*

**What happens:**

1. **Context Detection** — Skill asks: new project or existing?
2. **New Projects:**
   - Asks about domain, use cases, tone
   - Generates `CLAUDE.md` + knowledge base structure
   - RAG-optimized file organization

3. **Existing Projects:**
   - Reads current `CLAUDE.md` / `AGENTS.md`
   - Identifies: redundancy, contradictions, token bloat
   - Produces: refined version + migration notes

---

## Installation

**Claude.ai web:**
1. Download [Powerhouse-Claude-Project-Setup-Kit.skill](./Powerhouse-Claude-Project-Setup-Kit.skill)
2. Go to [Claude.ai](https://claude.ai) → **Settings** → **Skills**
3. Click **Install Skill** and upload the file

**Claude Code:** copy this folder into your project's `.claude/skills/` directory.

---

## Contents

- `SKILL.md` — Core intelligence and instruction set
- `references/anti-patterns.md` — Common project-building mistakes
- `Powerhouse-Claude-Project-Setup-Kit.skill` — Installable distributable

---

## Related

| Resource | Purpose |
|----------|---------|
| [All Skills](../README.md) | Browse all 4 skills + install guide |
| [Prompt Optimizer](../Powerhouse-Prompt-Optimizer/) | Optimize individual prompts |
| [Software Team](../Powerhouse-software-team/) | Full PM→Dev→QA pipeline |
| [Root README](../../README.md) | Full repo documentation |

---

*Part of the [Claude-Powerhouse](../../README.md) suite.*

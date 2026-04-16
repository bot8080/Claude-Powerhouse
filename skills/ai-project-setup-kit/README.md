# claude-project-setup-kit

A skill for Claude AI that helps you **create new AI projects from scratch** and **audit and improve existing ones**.

> Not affiliated with or endorsed by Anthropic.

---

## What are Claude Projects?

Claude Projects is a feature in Claude.ai that lets you create a persistent, customized AI assistant for a specific purpose — like a CELPIP tutor, a customer support bot, a coding assistant, or a research helper.

Each project has two components:

**1. Project Instructions (System Prompt)**
A set of rules and behaviors that Claude follows every time someone chats inside the project. This is where you define the AI's role, tone, response format, and what it should always or never do.

**2. Knowledge Base Files**
Documents you upload to the project that Claude can reference during conversations. These can contain domain knowledge, templates, checklists, workflows, terminology — anything Claude needs to give accurate, specialized responses.

### Why Claude Projects are powerful

| Without a Project | With a Well-Built Project |
|---|---|
| Claude has no memory of your context | Claude always knows your domain, rules, and preferences |
| You repeat instructions every session | Instructions are permanent and consistent |
| Generic responses | Responses tailored to your specific use case |
| No domain knowledge | Claude references your uploaded knowledge files |
| Inconsistent tone and format | Consistent behavior every time |

### Where Claude Projects are used

- **Personal productivity** — A writing coach, study buddy, or daily planner tuned to your style
- **Language learning** — IELTS / CELPIP / TOEFL prep assistant with exam-specific knowledge
- **Customer support** — A support bot trained on your product docs and tone guidelines
- **Team knowledge base** — A shared assistant that knows your company's processes and terminology
- **Coding assistant** — A dev helper that knows your stack, coding standards, and project structure
- **Research assistant** — A domain expert loaded with papers, frameworks, and methodologies
- **Content creation** — A writing assistant that knows your brand voice, audience, and content rules

---

## The problem this skill solves

Setting up a Claude Project well is harder than it looks:

- **Poorly written instructions** produce inconsistent Claude behavior — rules get ignored, tone drifts, knowledge files go unused
- **Bad knowledge base structure** means Claude picks the wrong file or misses relevant content entirely
- **No routing map** means Claude doesn't know which file to consult for which task
- **Instruction bloat** — projects accumulate rules over time that become contradictory or redundant
- **Outdated knowledge files** — content that was accurate when written becomes stale

Most users end up with a project that works okay at first but degrades over time as files grow and instructions pile up. This skill fixes that — both at creation time and during ongoing maintenance.

---

## How to use it

The skill auto-detects your context the moment it triggers — no manual setup needed.

### Running inside a Claude Project (with files uploaded)
Just say "improve my project" — the skill detects your files and starts the audit immediately.

### Running inside a Claude Project (no files yet)
The skill will prompt you to upload your knowledge base files first, then retry.

### Running outside any project (general Claude chat)
The skill shows a menu:

```
1. 🆕 Create a new Claude Project from scratch
2. 🔧 Improve an existing Claude Project
```

- Reply **1** → skill walks you through creating everything from scratch
- Reply **2** → skill tells you exactly how to open your project and run the audit from there

---

## What it does

This skill operates in two modes:

### Mode 1 — Create
Set up a brand new Claude project from scratch:
- Asks 4 focused questions about your goal, audience, and constraints
- Conducts deep web research (7-category structured search) before writing anything
- Drafts a project plan and waits for your approval
- Writes `project_instructions.md` + all knowledge base files
- Automatically applies prompt engineering best practices to `project_instructions.md` before delivery

### Mode 2 — Improve
Audit and improve an existing Claude project:
- Reads all uploaded knowledge base files and instruction files in your project
- Identifies overlap, bloat, structural issues, and missing routing rules
- Runs fresh web research to verify and fill gaps
- Presents a detailed audit report and waits for your approval
- Rewrites and consolidates files, applies prompt engineering pass
- Delivers a **file-by-file handoff walkthrough** — tells you exactly which files to REPLACE, DELETE, ADD, or KEEP in your Claude Project settings

---

## Prompt Engineering — Built In

The skill automatically applies Anthropic's prompt engineering methodology to every `project_instructions.md` it produces or edits:

- Role assignment
- Explicit task statements with positive framing
- XML structure for multi-section files
- Knowledge file routing clarity
- Output format specification
- Hard constraints surfacing

No separate prompt-improver skill required — the logic is fully integrated.

---

## Who should use this skill

| You are... | How this skill helps |
|---|---|
| Setting up your first Claude Project | Creates all files from scratch with research-backed content |
| Frustrated that Claude ignores your knowledge files | Adds a proper routing map so Claude always picks the right file |
| Finding your project instructions are getting messy | Audits, simplifies, and restructures everything |
| Maintaining a team project | Ensures instructions are clear enough for consistent behavior across users |
| Building a project for someone else | Delivers professional, well-structured files ready to hand off |
| Noticing Claude's responses have become generic over time | Refreshes knowledge files with current best practices |

---

## Installation

1. Download `ai-project-setup-kit.skill` from this repo
2. Open [Claude.ai](https://claude.ai)
3. Go to **Settings → Skills**
4. Click **Install Skill** and upload the `.skill` file
5. The skill is now available in all your Claude chats

---

## Usage

Just talk to Claude naturally. The skill triggers automatically on phrases like:

- "create a new project for X"
- "help me set up a knowledge base"
- "my project files are getting messy"
- "audit my project instructions"
- "improve my Claude project setup"
- "my AI instructions are too complex"

---

## Requirements

- Claude.ai account (Free, Pro, or Team)
- Skills feature enabled in your account

---

## What gets delivered

**Mode 1 (Create):**
- `project_instructions.md` — prompt-optimized system prompt for your project
- `knowledge_[topic].md` — one focused file per domain topic

**Mode 2 (Improve):**
- Updated versions of all existing files
- File-by-file instructions on what to replace, delete, or keep
- Before/after summary with size reduction estimate

---

## License

MIT — see [LICENSE](./LICENSE)

---

## Contributing

Issues and PRs welcome. If you improve the skill or find edge cases it handles poorly, open an issue describing the input and what went wrong.

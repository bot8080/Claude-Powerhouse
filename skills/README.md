# MultiAgents-Powerhouse Skills

A personal collection of AI skills — reusable, installable, and open source.

> Not affiliated with or endorsed by Anthropic.

---

## What Are Skills?

Skills are instruction files that extend Claude's behavior for specific tasks. Once installed, they trigger automatically based on what you ask — no manual setup per conversation.

Think of them as plugins for Claude.

---

## Which Skill Should I Use?

| I want to... | Use this skill | Target |
|--------------|----------------|--------|
| Build a complex app with PM/Dev/QA pipeline | [Software Team](./Powerhouse-software-team/) | [CLI] |
| Set up a project knowledge base | [Project Setup Kit](./Powerhouse-Claud-Project-Setup-Kit/) | [Both] |
| Improve a vague prompt | [Prompt Optimizer](./Powerhouse-Prompt-Optimizer/) | [Both] |
| Format a professional resume | [Resume Specialist](./Powerhouse-Resume-Specialist/) | [Both] |

> **[CLI]** = Claude Code terminal only. **[Both]** = Claude Code + Claude.ai web.

---

## Skills in Detail

| Skill | Target | Description |
|-------|--------|-------------|
| [Powerhouse-software-team](./Powerhouse-software-team/) | [CLI] | Complete AI dev team — spec-first, 7-layer build order, PM → Dev → QA pipeline. |
| [Powerhouse-Claud-Project-Setup-Kit](./Powerhouse-Claud-Project-Setup-Kit/) | [Both] | AI Workspace Architect — project setup, structure auditing. |
| [Powerhouse-Prompt-Optimizer](./Powerhouse-Prompt-Optimizer/) | [Both] | Expert prompt engineering using Anthropic 2025 heuristics. |
| [Powerhouse-Resume-Specialist](./Powerhouse-Resume-Specialist/) | [Both] | Premium DOCX formatting and ATS optimization. |

---

## Quick Start

### Claude Code Users

Skills under `.claude/skills/` activate automatically when working in this repo. No install needed — just type trigger phrases.

### Claude.ai Web Users

1. Download the `.skill` file from the skill's folder
2. Go to [Claude.ai](https://claude.ai) → **Settings** → **Skills**
3. Click **Install Skill** and upload the file
4. The skill is now active in all your Claude chats

---

## How Skills Work

Each skill has:
- A **trigger description** — Claude reads this to decide when to use the skill
- **Instructions** — what Claude should do when the skill activates
- Optionally: **knowledge files, scripts, or reference docs** bundled inside

Skills activate automatically when your request matches the trigger — no need to mention the skill by name.

---

## Requirements

- Claude.ai account (Free, Pro, or Team)
- Skills feature enabled in your account

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| Skill not triggering | Use exact trigger phrases from skill's README |
| "Invalid skill file" | Make sure you downloaded `.skill` file, not `SKILL.md` |
| CLI skill in Claude.ai | Check the `[CLI]` vs `[Both]` badge — CLI-only skills need Claude Code |
| Wrong output | Skill might conflict with another installed skill — disable others temporarily |
| Download link broken | Use raw URL: `https://raw.githubusercontent.com/bot8080/MultiAgents-Powerhouse/main/skills/{name}/{name}.skill` |

---

## Contributing

PRs and issues welcome. To add a new skill:

1. Create `skill-name/SKILL.md` with YAML frontmatter + instructions
2. Create `skill-name/skill-name.skill` (the installable file)
3. Create `skill-name/README.md` explaining what it does
4. Add a row to the skills table above
5. Open a PR

---

## License

MIT — see [LICENSE](./LICENSE)

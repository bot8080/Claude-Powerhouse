# claude-skills

A personal collection of Claude AI skills — reusable, installable, and open source.

> Not affiliated with or endorsed by Anthropic.

---

## What are Claude Skills?

Claude Skills are instruction files (`.skill`) that extend Claude's behavior for specific tasks. Once installed in Claude.ai, they trigger automatically based on what you ask — no manual setup needed per conversation.

Think of them as plugins for Claude: each skill teaches Claude how to handle a specific domain or workflow better than it would by default.

---

## Skills in this repo

| Skill | Description | Install |
|---|---|---|
| [ai-project-setup-kit](./ai-project-setup-kit/) | Create and improve Claude Projects — auto-detects context, shows guided menu when run outside a project, starts audit immediately when run inside a project with files | [Download](./ai-project-setup-kit/ai-project-setup-kit.skill) |
| [prompt-improver](./prompt-improver/) | Rewrites any prompt using Anthropic's prompt engineering methodology — returns the improved prompt immediately, no commentary | [Download](./prompt-improver/prompt-improver.skill) |

---

## How to install a skill

1. Download the `.skill` file from the skill's folder
2. Open [Claude.ai](https://claude.ai)
3. Go to **Settings → Skills**
4. Click **Install Skill** and upload the `.skill` file
5. The skill is now active in all your Claude chats

---

## How skills work

Each skill has:
- A **trigger description** — Claude reads this to decide when to use the skill
- **Instructions** — what Claude should do when the skill activates
- Optionally: **knowledge files, scripts, or reference docs** bundled inside

Skills activate automatically when your request matches the trigger — you don't need to mention the skill by name.

---

## Requirements

- Claude.ai account (Free, Pro, or Team)
- Skills feature enabled in your account

---

## Contributing

Found a bug or want to improve a skill? PRs and issues are welcome.

If you want to submit your own skill:
- Follow the folder structure: `skill-name/SKILL.md` + `skill-name/skill-name.skill`
- Include a `README.md` inside the skill folder explaining what it does
- Open a PR with a short description of what the skill does and when it triggers

---

## License

MIT — see [LICENSE](./LICENSE)

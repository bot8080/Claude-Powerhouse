# Claude-Powerhouse Skills

Four installable skills that extend Claude's behavior. Install once — they trigger automatically from what you ask.

> Personal open-source project. Not affiliated with or endorsed by Anthropic.

## Pick your skill

| I want to... | Skill | Works in |
|--------------|-------|----------|
| Build software with a structured PM→Dev→QA pipeline | [Software Team](./Powerhouse-software-team/) | Claude Code |
| Set up or audit a Claude project's instructions and knowledge base | [Project Setup Kit](./Powerhouse-Claude-Project-Setup-Kit/) | Claude Code + Claude.ai |
| Turn a vague prompt into a professional specification | [Prompt Optimizer](./Powerhouse-Prompt-Optimizer/) | Claude Code + Claude.ai |
| Format an ATS-safe DOCX resume | [Resume Specialist](./Powerhouse-Resume-Specialist/) | Claude Code + Claude.ai |

Each skill's folder has a README with examples and trigger phrases, plus the installable `.skill` file.

### Trigger phrases

Each skill fires automatically when your request matches its trigger. Try these:

| Skill | Try saying |
|-------|------------|
| Software Team | "Build me a feature using the PM→Dev→QA pipeline" or `/pst plan` |
| Project Setup Kit | "Help me set up a Claude project" or "audit my knowledge base" |
| Prompt Optimizer | "Improve this prompt" (then paste your prompt) |
| Resume Specialist | "Format my resume as a DOCX" (then paste your content) |

## Install

**Claude.ai web:**

1. Download the `.skill` file from the skill's folder ([direct links below](#direct-download-links))
2. [Claude.ai](https://claude.ai) → **Settings** → **Skills** → **Install Skill** → upload the file
3. Ask normally — the skill activates when your request matches its trigger

**Claude Code (your own project):**

Copy the skill's folder into your project's `.claude/skills/` directory. The Software Team skill also pairs with agent definitions — see [its README](./Powerhouse-software-team/#installation).

### Direct download links

| Skill | Download |
|-------|----------|
| Software Team | [Powerhouse-software-team.skill](./Powerhouse-software-team/Powerhouse-software-team.skill) |
| Project Setup Kit | [Powerhouse-Claude-Project-Setup-Kit.skill](./Powerhouse-Claude-Project-Setup-Kit/Powerhouse-Claude-Project-Setup-Kit.skill) |
| Prompt Optimizer | [Powerhouse-Prompt-Optimizer.skill](./Powerhouse-Prompt-Optimizer/Powerhouse-Prompt-Optimizer.skill) |
| Resume Specialist | [Powerhouse-Resume-Specialist.skill](./Powerhouse-Resume-Specialist/Powerhouse-Resume-Specialist.skill) |

## Troubleshooting

| Problem | Fix |
|---------|-----|
| Skill not triggering | Use a trigger phrase from the skill's README |
| "Invalid skill file" | Upload the `.skill` file, not `SKILL.md` |
| `/pst` commands don't work in Claude.ai | Software Team is Claude Code-only; the web upload is reference-only |
| Download link broken | Use the raw URL: `https://raw.githubusercontent.com/bot8080/Claude-Powerhouse/main/skills/{name}/{name}.skill` |

More in [docs/TROUBLESHOOTING.md](../docs/TROUBLESHOOTING.md).

## Contributing a skill

1. Create `skills/<Name>/SKILL.md` — YAML frontmatter (`name:` lowercase-kebab, `description:` = the activation trigger, make it exhaustive) + markdown instructions
2. Zip it as `skills/<Name>/<Name>.skill` with the folder name inside matching the frontmatter `name`
3. Add a `README.md` with examples, and a row to the tables here and in the root README
4. Open a PR

## License

MIT — see [LICENSE](../LICENSE)

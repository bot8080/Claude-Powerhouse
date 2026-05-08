# Claude-Powerhouse

**Full-stack development workflow with AI agents** — project scaffolding + spec-first pipeline + financial MCPs in one repo.

---

## Choose Your Path

| I want to... | Go to |
|---|---|
| **Build an app with AI agents** | [docs/QUICKSTART.md](./docs/QUICKSTART.md) (5 min) |
| **Browse AI skills for Claude** | [skills/README.md](./skills/README.md) |
| **Get financial data in Claude Desktop** | [mcps/README.md](./mcps/README.md) |
| **See all commands at a glance** | [docs/CHEATSHEET.md](./docs/CHEATSHEET.md) |
| **Fix a problem** | [docs/TROUBLESHOOTING.md](./docs/TROUBLESHOOTING.md) |

---

## 30-Second Quick Start

```bash
# New project
npx powerhouse init my-app
cd my-app
claude                    # start Claude Code
/pst plan "user auth"    # PM writes a ticket
/pst build                # Dev implements
/pst review               # QA validates

# Or add to existing project
npx powerhouse apply
```

---

## What's in This Repo?

### CLI — Project Scaffolding

`npx powerhouse init` scaffolds new projects (Expo, React, Next.js) with AI workflow built in. `npx powerhouse apply` adds conventions to existing projects without touching source code.

### Skills — AI Agents for Claude

5 installable skills that extend Claude's behavior:

| Skill | Target | One-line summary |
|---|---|---|
| [Software Team](./skills/Powerhouse-software-team/) | CLI | PM → Dev → QA pipeline with spec-first discipline |
| [OpenCode Handoff](./skills/Powerhouse-opencode-handoff/) | CLI | Dispatch mechanical work to free models |
| [Project Setup Kit](./skills/Powerhouse-Claud-Project-Setup-Kit/) | Both | Audit and set up project knowledge bases |
| [Prompt Optimizer](./skills/Powerhouse-Prompt-Optimizer/) | Both | Fix vague prompts using Anthropic heuristics |
| [Resume Specialist](./skills/Powerhouse-Resume-Specialist/) | Both | ATS-optimized DOCX resume formatting |

**Full details:** [skills/README.md](./skills/README.md) — install instructions, which skill for which job, troubleshooting

### MCP Servers — Financial Intelligence

2 servers that connect Claude to real-time financial data:

| Server | Markets | Best for |
|---|---|---|
| [market-intelligence](./mcps/market-intelligence/) | US, India, Canada | Real-time stock data, technicals, scoring |
| [investment-brain](./mcps/investment-brain/) | US, India, Canada | Auto-scoring, paper trading, portfolio tracking |

**Full details:** [mcps/README.md](./mcps/README.md) — quick start, Claude Desktop config, which server you need

---

## Installation

```bash
git clone https://github.com/bot8080/Claude-Powerhouse.git
cd Claude-Powerhouse
npm install
npm link                    # makes `powerhouse` available globally
```

**Prerequisites:**

| Tool | Required For | Install |
|---|---|---|
| Node.js 20+ | CLI scaffolding | [nodejs.org](https://nodejs.org) |
| Claude Code | `/pst` commands | [docs.anthropic.com](https://docs.anthropic.com/en/docs/claude-code) |
| uv (optional) | MCP servers | [astral.sh/uv](https://astral.sh/uv) |
| Python 3.10+ (optional) | investment-brain | [python.org](https://python.org) |

---

## Project Structure

```
Claude-Powerhouse/
├── cli/                    # npx powerhouse (init, apply)
├── templates/              # Stack + addon templates
├── skills/                 # 5 AI skills for Claude
│   ├── Powerhouse-software-team/
│   ├── Powerhouse-opencode-handoff/
│   ├── Powerhouse-Claud-Project-Setup-Kit/
│   ├── Powerhouse-Prompt-Optimizer/
│   └── Powerhouse-Resume-Specialist/
├── mcps/                   # 2 MCP servers
│   ├── market-intelligence/
│   └── investment-brain/
├── docs/                   # Guides
│   ├── QUICKSTART.md
│   ├── CHEATSHEET.md
│   └── TROUBLESHOOTING.md
└── .opencode/agents/       # Agent definitions (6 roles)
```

---

## Development Workflow

This repo uses its own software-team pipeline:

```
/pst plan → [Research?] → /pst build → /pst review → Human Approve → Merge
```

| Command | What it does |
|---|---|
| `/pst status` | Current layer + next task |
| `/pst plan [feature]` | PM writes ticket |
| `/pst build` | Dev implements |
| `/pst review` | QA validates |
| `/pst branch [name]` | Create feature branch |
| `/pst pr` | Push + create PR |
| `/pst next` | First unchecked task |

See [BUILD_STATUS.md](./BUILD_STATUS.md) for current progress.

---

## License

MIT — see [LICENSE](./LICENSE).

> Financial data is for informational purposes only. Always verify before making investment decisions.
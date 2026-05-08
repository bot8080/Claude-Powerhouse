# MultiAgents-Powerhouse

> **Source-only monorepo.** Nothing here is published to npm or PyPI. Clone this repo to use any component.

AI development tooling built around a structured PM→Dev→QA workflow.
The Software Team skill is the centrepiece — enforces spec-first discipline across all agents.
Works in Claude Code; pairs with OpenCode's multi-model routing for free-tier parallel execution.
Everything else (MCP financial servers, agent definitions, CLI scaffolding) is modular — take what fits.

---

## Pick What You Need

| I want to… | Start here |
|---|---|
| Add structured PM→Dev→QA workflow to my project | [Software Team Skill](#1-ai-skills-skills) |
| Use OpenCode with different models per agent role | [Multi-Model Routing](#multi-model-routing-opencode) |
| Pull real-time financial data into Claude | [MCP Servers](#2-mcp-servers-mcps) |
| Scaffold a new AI project from scratch | [CLI Tool](#4-cli-tool-cli) |

---

## What's in This Repo

### 1. AI Skills (`skills/`)

4 installable skills that extend Claude's behavior:

| Skill | Target | Purpose |
|---|---|---|
| [Software Team](./skills/Powerhouse-software-team/) | CLI | PM→Dev→QA pipeline with spec-first discipline |
| [Project Setup Kit](./skills/Powerhouse-Claud-Project-Setup-Kit/) | Both | Project knowledge base setup |
| [Prompt Optimizer](./skills/Powerhouse-Prompt-Optimizer/) | Both | Prompt engineering with Anthropic heuristics |
| [Resume Specialist](./skills/Powerhouse-Resume-Specialist/) | Both | ATS-optimized DOCX resume formatting |

**Install:** Download `.skill` file → Claude.ai Settings → Skills → Upload

> **OpenCode users:** pair the Software Team skill with [Multi-Model Routing](#multi-model-routing-opencode) below — each agent role runs on a different free model.

---

## Multi-Model Routing (OpenCode)

If you use [OpenCode](https://opencode.ai) with the Go API plan (~$10/mo), activate per-agent model routing — each role runs on a model optimized for its workload:

| Agent | Model | Best For |
|---|---|---|
| PM Tech Lead | `kimi-k2-0711` | Planning, specs |
| Dev Engineer | `deepseek-v4-pro` | Complex implementation |
| Worker-Mechanical | `deepseek-v4-flash` | High-volume mechanical work |
| QA Engineer | `qwen3.6-plus` | Validation, testing |
| Research Engineer | `qwen3.5-plus` | API research |
| Advisor | `kimi-k2-0711` | Architecture, strategy |

**Activate:**
```bash
cp opencode.go.json opencode.json
```

> The base `opencode.json` has no hardcoded models — falls back to your default if you skip this.

---

### 2. MCP Servers (`mcps/`)

2 financial data servers for Claude Desktop:

| Server | Markets | Purpose |
|---|---|---|
| [market-intelligence](./mcps/market-intelligence/) | US, India, Canada | Real-time stock data, technicals, scoring |
| [investment-brain](./mcps/investment-brain/) | US, India, Canada | Auto-scoring, paper trading, portfolio tracking |

**Install:** Clone repo → `cd mcps/...` → `uv sync` → `uv run`

### 3. Agent Definitions (`.opencode/agents/`)

6 specialized agent roles for spec-first development:

| Agent | File | Purpose |
|---|---|---|
| PM Tech Lead | `pm-tech-lead.md` | Plans features, writes specs, reviews architecture |
| Dev Engineer | `dev-engineer.md` | Implements from approved specs |
| Worker-Mechanical | `worker-mechanical.md` | High-volume mechanical tasks |
| QA Engineer | `qa-engineer.md` | Tests, validates, finds bugs |
| Research Engineer | `research-engineer.md` | Investigates unfamiliar APIs |
| Advisor | `advisor.md` | Architecture, strategy, guidance |

These agent definitions are tool-agnostic — they work with any AI coding tool that reads project instruction files (OpenCode, Kimi Code, Cursor, Windsurf, GitHub Copilot, and others).

**Use in your own project:** Run `powerhouse apply` to copy agents to your project, or clone this repo and manually copy `.opencode/agents/` and `.claude/agents/`.

### 4. CLI Tool (`cli/`)

> **Status:** Local-only utility, not published to npm.

Local scaffolding utility for bootstrapping projects with the agent pipeline:

```bash
powerhouse init my-app    # Scaffold new project with agent pipeline
powerhouse apply          # Add workflow to existing project
```

**Install:** `git clone` → `npm link`

> **`powerhouse` vs `/pst`:** `powerhouse init/apply` is a one-time project bootstrapper — run it once to scaffold or wire up a project. `/pst` commands (`/pst plan`, `/pst build`, `/pst review`) are Claude Code slash commands for the ongoing development workflow inside any project — no installation required.

---

## Cross-Tool Compatibility

| Tool | How to Use These Agents |
|---|---|
| **OpenCode** | Native — reads `opencode.json` + `.opencode/agents/` |
| **Claude Code** | Reference — reads `AGENTS.md` conventions + `.claude/agents/` |
| **Kimi Code** | Reads `${KIMI_AGENTS_MD}` or `.agents/` alias |
| **Cursor** | Alongside `.cursor/rules/` |
| **Windsurf** | Alongside `.windsurfrules` |
| **GitHub Copilot** | Alongside `.github/copilot-instructions.md` |

The `.agents/` directory is a cross-tool alias — any tool that reads project files can access agent definitions from there.

---

## Quick Start

```bash
# 1. Clone the repo
git clone https://github.com/bot8080/MultiAgents-Powerhouse.git
cd MultiAgents-Powerhouse

# 2. Use any component independently:
#    - Install a skill: download .skill file from skills/ and upload to Claude.ai
#    - Run an MCP: cd mcps/market-intelligence && uv sync && uv run market-intelligence
#    - Use agents: open with OpenCode or Claude Code — agent definitions load automatically

# 3. Activate multi-model routing for OpenCode (optional)
cp opencode.go.json opencode.json
opencode
```

---

## Documentation

| Guide | Purpose |
|---|---|
| [docs/QUICKSTART.md](./docs/QUICKSTART.md) | 5-minute setup for each component |
| [docs/CHEATSHEET.md](./docs/CHEATSHEET.md) | All commands on one page |
| [docs/TROUBLESHOOTING.md](./docs/TROUBLESHOOTING.md) | Common errors and fixes |
| [AGENTS.md](./AGENTS.md) | Session brief + auto-routing rules |
| [BUILD_STATUS.md](./BUILD_STATUS.md) | Current development progress |

---

## Project Structure

```
MultiAgents-Powerhouse/
├── .opencode/
│   ├── agents/              # 6 agent definitions (tool-agnostic)
│   └── commands/            # OpenCode slash commands
├── skills/                   # 4 AI skills for Claude
│   ├── Powerhouse-software-team/
│   ├── Powerhouse-Claud-Project-Setup-Kit/
│   ├── Powerhouse-Prompt-Optimizer/
│   └── Powerhouse-Resume-Specialist/
├── mcps/                     # 2 MCP servers
│   ├── market-intelligence/
│   └── investment-brain/
├── cli/                      # Local scaffolding tool
├── docs/                     # Guides
├── templates/                # Project templates
├── opencode.json             # Base config (no hardcoded models)
├── opencode.go.json          # Per-agent model routing overlay
└── AGENTS.md                 # Session brief + conventions
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

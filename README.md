# MultiAgents-Powerhouse

> **Source-only monorepo.** Nothing here is published to npm or PyPI. Clone this repo to use any component.

A personal collection of AI tools in one monorepo: Claude skills, MCP servers, agent definitions, and a CLI scaffold. Works with Claude Code, Claude.ai, Claude Desktop, and OpenCode.

---

## What's in This Repo

### 1. AI Skills (`skills/`)

5 installable skills that extend Claude's behavior:

| Skill | Target | Purpose |
|---|---|---|
| [Software Team](./skills/Powerhouse-software-team/) | CLI | PM→Dev→QA pipeline with spec-first discipline |
| [OpenCode Handoff](./skills/Powerhouse-opencode-handoff/) | CLI | Dispatch mechanical work to free models |
| [Project Setup Kit](./skills/Powerhouse-Claud-Project-Setup-Kit/) | Both | Project knowledge base setup |
| [Prompt Optimizer](./skills/Powerhouse-Prompt-Optimizer/) | Both | Prompt engineering with Anthropic heuristics |
| [Resume Specialist](./skills/Powerhouse-Resume-Specialist/) | Both | ATS-optimized DOCX resume formatting |

**Install:** Download `.skill` file → Claude.ai Settings → Skills → Upload

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

#### Model Routing (OpenCode)

Each agent role is wired to a different model based on workload. Activate with:

```bash
cp opencode.go.json opencode.json
```

| Agent | Model | Best For |
|---|---|---|
| PM Tech Lead | `kimi-k2-0711` | Planning, architecture, specs |
| Dev Engineer | `deepseek-v4-pro` | Complex implementation |
| Worker-Mechanical | `deepseek-v4-flash` | High-volume mechanical work |
| QA Engineer | `qwen3.6-plus` | Validation, testing |
| Research Engineer | `qwen3.5-plus` | API research, investigation |
| Advisor | `kimi-k2-0711` | Architecture, strategy |

> The base `opencode.json` contains zero hardcoded models — it falls back to your default if you skip this step.

### 4. CLI Tool (`cli/`)

> **Status:** Local-only utility, not published to npm.

Local scaffolding utility for bootstrapping projects with the agent pipeline:

```bash
powerhouse init my-app    # Scaffold new project with agent pipeline
powerhouse apply          # Add workflow to existing project
```

**Install:** `git clone` → `npm link`

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
├── skills/                   # 5 AI skills for Claude
│   ├── Powerhouse-software-team/
│   ├── Powerhouse-opencode-handoff/
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

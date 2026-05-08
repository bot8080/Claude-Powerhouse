# MultiAgents-Powerhouse

> **Source-only monorepo.** Nothing here is published to npm or PyPI. Clone this repo to use any component.

A multi-model AI agent framework for spec-first software development. Built primarily for **OpenCode** with cross-tool compatibility (Claude Code, Kimi, Cursor, Windsurf, and others).

---

## Core Philosophy: Multi-Model Agent Routing

Different agent roles use different AI models based on their workload. This maximizes quality where it matters and minimizes cost where it doesn't.

| Agent | Model | Quota (req/5hr) | Best For |
|---|---|---|---|
| PM Tech Lead | `kimi-k2-0711` | 1,150 | Planning, architecture, specs |
| Dev Engineer | `deepseek-v4-pro` | 3,450 | Complex implementation |
| Worker-Mechanical | `deepseek-v4-flash` | 31,650 | High-volume mechanical work |
| QA Engineer | `qwen3.6-plus` | 3,300 | Validation, testing |
| Research Engineer | `qwen3.5-plus` | 10,200 | API research, investigation |
| Advisor | `kimi-k2-0711` | 1,150 | Architecture, strategy |

**Activate:**
```bash
cp opencode.go.json opencode.json
```

> **Note:** This is configuration-based routing. OpenCode reads per-agent model assignments from `opencode.json`. The base config (`opencode.json`) contains zero hardcoded models — it survives any model deprecation by falling back to your default.

---

## What's in This Repo

### 1. Agent Definitions (`.opencode/agents/`)

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

### 2. AI Skills (`skills/`)

5 installable skills that extend Claude's behavior:

| Skill | Target | Purpose |
|---|---|---|
| [Software Team](./skills/Powerhouse-software-team/) | CLI | PM→Dev→QA pipeline with spec-first discipline |
| [OpenCode Handoff](./skills/Powerhouse-opencode-handoff/) | CLI | Dispatch mechanical work to free models |
| [Project Setup Kit](./skills/Powerhouse-Claud-Project-Setup-Kit/) | Both | Project knowledge base setup |
| [Prompt Optimizer](./skills/Powerhouse-Prompt-Optimizer/) | Both | Prompt engineering with Anthropic heuristics |
| [Resume Specialist](./skills/Powerhouse-Resume-Specialist/) | Both | ATS-optimized DOCX resume formatting |

**Install:** Download `.skill` file → Claude.ai Settings → Skills → Upload

### 3. MCP Servers (`mcps/`)

2 financial data servers for Claude Desktop:

| Server | Markets | Purpose |
|---|---|---|
| [market-intelligence](./mcps/market-intelligence/) | US, India, Canada | Real-time stock data, technicals, scoring |
| [investment-brain](./mcps/investment-brain/) | US, India, Canada | Auto-scoring, paper trading, portfolio tracking |

**Install:** Clone repo → `cd mcps/...` → `uv sync` → `uv run`

### 4. CLI Tool (`cli/`)

Local scaffolding utility (not published to npm):

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

# 2. Activate multi-model routing (optional)
cp opencode.go.json opencode.json

# 3. Start coding with OpenCode
opencode

# Or use Claude Code (reads AGENTS.md conventions)
claude
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
├── opencode.go.json          # Go plan overlay (per-agent routing)
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

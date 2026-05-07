# Claude-Powerhouse

**Full-stack development workflow** — project scaffolding + spec-first agent pipeline in one tool.

Transforms AI coding agents into a structured, professional engineering team with:
- 🏗️ **Project scaffolding** — Expo, React, Next.js stacks with Firebase/Stripe addons
- 📋 **Spec-first discipline** — TECH_SPEC + BUILD_STATUS gates before any code
- 🤖 **Multi-agent pipeline** — PM → Research → Dev → QA with automatic routing
- 🔧 **CLI + Skills** — `npx powerhouse` for scaffolding, `/powerhouse` for execution
- 🌍 **Cross-tool compatible** — Works with Claude Code, OpenCode, Kimi Code, Cursor, Windsurf, +15 more

---

## Quick Start

> **Prerequisites:** Node.js 20+, Claude Code (CLI) for `/powerhouse` commands

```bash
# Scaffold a new project with interactive setup
npx powerhouse init my-app

# Or add workflow conventions to existing project (non-destructive)
npx powerhouse apply

# Then use the agent pipeline in Claude Code
/powerhouse status
/powerhouse plan "user auth"
/powerhouse build
/powerhouse review

# Need help? Ask @advisor anything
```

---

## Features

| Category | Feature | Description |
|----------|---------|-------------|
| **Scaffolding** | `npx powerhouse init` | Interactive project generator with stack + addon selection |
| **Retrofit** | `npx powerhouse apply` | Adds conventions to existing projects (non-destructive) |
| **Stacks** | Expo, React, Next.js | Production-ready templates with ESLint, Prettier, Jest, Husky |
| **Addons** | Firebase, Stripe, OpenCode AI | Auth, payments, multi-agent workflow — checkbox install |
| **Agent Pipeline** | PM → Dev → QA | Spec-first, layer-gated, 7-point QA validation |
| **Cross-Tool** | AGENTS.md + Skills | Works with 15+ AI coding tools |
| **MCP Servers** | market-intelligence, investment-brain | Financial data + analysis engines |
| **Skills** | software-team, opencode-handoff, etc. | Reusable AI workflows |

---

## CLI Commands (Scaffolding)

```bash
# Show all commands
npx powerhouse --help

# Create new project (interactive — prompts for name if omitted)
npx powerhouse init
npx powerhouse init my-app

# Create in current directory
npx powerhouse init .

# Add workflow conventions to existing project
# Copies: AGENTS.md, .claude/, .github/, .husky/, docs/, session-tracking/
# Never overwrites existing files or touches source code
npx powerhouse apply
```

**During `init`, you'll select:**
1. **Stack**: Expo (React Native), React, Next.js, Vue, Svelte
2. **Backend**: None / Firebase / Supabase
3. **Payments**: No / Stripe
4. **AI Workflow**: None / OpenCode AI

---

## Skill Commands (Execution)

> **These are Claude Code slash commands** — type them in a Claude Code session, not your terminal.

| Command | What it does |
|---|---|
| `/powerhouse status` | Current layer + next unchecked task |
| `/powerhouse plan [feature]` | PM Tech Lead produces a structured ticket |
| `/powerhouse build` | Dev Engineer implements (or OpenCode dispatch if mechanical) |
| `/powerhouse review` | QA Engineer full 7-point validation |
| `/powerhouse branch [name]` | Creates `feature/{subproject}/L{N}-{name}` |
| `/powerhouse pr` | Type-check → rebase → push → create PR |
| `/powerhouse next` | First unchecked task across all sub-projects |

---

## Project Structure

```
Claude-Powerhouse/
├── cli/                           # NPM-distributed CLI
│   ├── cli.js                     # Entry: init | apply | --help
│   ├── init.js                    # Project scaffolder
│   └── apply.js                   # Workflow retrofit
├── templates/
│   ├── workflow/                  # Universal conventions (AGENTS.md, CI/CD, Husky)
│   ├── stacks/
│   │   └── expo/                  # Expo + TypeScript + Expo Router
│   └── addons/
│       ├── firebase/              # Auth, Firestore, Storage, Cloud Functions
│       ├── stripe/                # Payment screens + webhooks
│       └── opencode-ai/           # Multi-agent AI workflow
├── .claude/
│   ├── agents/                    # PM, Dev, QA, Research, Advisor, Dispatcher
│   ├── skills/powerhouse/         # /powerhouse unified command
│   └── hooks/                     # Spec-gate + gstack hooks
├── .agents/                       # Cross-tool alias (OpenCode, Kimi, Cursor)
│   ├── agents/                    # Agent definitions
│   └── skills/                    # Skills for non-Claude tools
├── mcps/
│   ├── market-intelligence/       # Financial intelligence (shipped)
│   └── investment-brain/          # AI analysis engine (dev)
└── skills/
    ├── Powerhouse-software-team/  # Full PM→Dev→QA pipeline
    ├── Powerhouse-opencode-handoff/  # OpenCode dispatch
    └── ...
```

---

## Multi-Tool Compatibility

| Tool | AGENTS.md | Skills | Notes |
|------|-----------|--------|-------|
| **OpenCode** | ✅ Native | ✅ `.claude/skills/` or `.agents/skills/` | Primary file |
| **Kimi Code** | ✅ Native | ✅ `.claude/skills/` or `.agents/skills/` | Uses `${KIMI_AGENTS_MD}` |
| **Cursor** | ✅ Native | ✅ `.cursor/rules/` + skills | Alongside MDC rules |
| **Windsurf** | ✅ Native | ✅ | Alongside `.windsurfrules` |
| **GitHub Copilot** | ✅ Native | ✅ | Alongside `.github/copilot-instructions.md` |
| **Claude Code** | ⚠️ Reference | ✅ `.claude/skills/` | Use CLAUDE.md (reference AGENTS.md) |
| **Aider** | ✅ Native | ✅ | Alongside `.aider.conf.yml` |
| **Gemini CLI** | ✅ Native | ✅ | Alongside `GEMINI.md` |

**The `.agents/` directory** is a cross-tool alias — any tool that reads project files can access agent definitions and skills from there.

---

## 7-Layer Build Order

Layer N cannot start until Layer N-1 is fully checked off and merged to `main`:

| Layer | Name | Contents |
|-------|------|----------|
| 1 | Types & Constants | Interfaces, enums, color tokens, config |
| 2 | Services | Data access — CRUD, auth, storage |
| 3 | Context & Hooks | State management, business logic |
| 4 | Base Components | Reusable UI primitives (skip for CLI/backend) |
| 5 | Screens / Pages | Full route implementations |
| 6 | Backend Functions | Cloud functions, webhooks, scheduled jobs |
| 7 | Integration & Polish | Wire together, performance, real data |

---

## Agent Pipeline

Every feature flows through a fixed pipeline with automatic routing:

```
User → @advisor (ad-hoc help, anytime)
   ↓ (formal ticket)
/powerhouse plan "feature"
   ↓
PM Tech Lead → writes ticket with scope + acceptance criteria
   ↓ (optional, for unfamiliar APIs)
Research Engineer → investigates, produces findings doc
   ↓
/powerhouse build
   ↓
Dev Engineer → implements ticket exactly (or OpenCode dispatch if score >= 7)
   ↓
/powerhouse review
   ↓
QA Engineer → 7-point validation → PASS/FAIL
   ↓
Human approves → merge to main → update BUILD_STATUS.md
```

### Agent Roles

| Agent | Trigger | Responsibility |
|-------|---------|----------------|
| **@advisor** | `@advisor` or "ask advisor" | Ad-hoc help, brainstorming, quick questions |
| **PM Tech Lead** | "build X", "plan X", "create X" | Ticket creation, spec-gate + layer-gate checks, dispatch scoring |
| **Research Engineer** | "research X", "how does X work" | API/library investigation (skipped for standard CRUD) |
| **Dev Engineer** | "build", "implement", "code it" | Scoped implementation — no more, no less than the ticket |
| **QA Engineer** | "review", "QA", "check", "test" | 7-point validation: spec, scope, quality, criteria, syntax, smoke, browser |
| **OpenCode Dispatcher** | "dispatch", "send to opencode" | Mechanical work (score >= 7) → OpenCode + MiniMax M2 (free) in isolated worktree |

---

## MCP Servers

> **Target: Claude Desktop + Claude Code (CLI)**
> Install via `claude_desktop_config.json` or as a Claude Code MCP.

### Market-Intelligence (shipped)

Real-time financial intelligence across US (NASDAQ/NYSE), India (NSE/BSE), and Canada (TSX).

**8 tools:** multi-market ticker resolution, full company profiles, technical analysis (RSI/MACD/ADX/Bollinger), 4-pillar scoring, insider/institutional activity, FII/DII flows, Nifty valuation, US macro data.

```
$ uvx market-intelligence
> get_scoring_data("NVDA")
{
  "symbol": "NVDA",
  "total_score": 82,
  "verdict_suggestion": "BUY",
  "pillar_scores": {
    "valuation": {"score": 23, "reason": "PE=65.2, PEG=1.2"},
    "quality": {"score": 22, "reason": "ROE=65%, Insider=4.2%"},
    "momentum": {"score": 22, "reason": "above 50/200DMA, RSI=58"},
    "risk": {"score": 15, "beta": 1.68}
  },
  "piotroski_f_score": {"score": 8, "verdict": "strong"}
}
```

**Claude Desktop config:**
```json
{
  "mcpServers": {
    "market-intelligence": {
      "command": "uv",
      "args": ["run", "--directory", "C:\\path\\to\\Claude-Powerhouse\\mcps\\market-intelligence", "market-intelligence"]
    }
  }
}
```

[Full documentation →](./mcps/market-intelligence/README.md)

---

### Investment-Brain (in development)

Local Python engine that pre-computes analysis and generates minimal Claude prompts (~20–50 tokens). Claude only formats the output.

Scoring: Fundamental 35 / Technical 35 / Smart Money 30. 9-rule deal-breaker check runs before scoring.

```bash
cd mcps/investment-brain
pip install -r requirements.txt
python main.py analyze TSM
```

[Full documentation →](./mcps/investment-brain/README.md)

---

### Powerhouse Stack — Running Both Together

For the full experience, run `market-intelligence` as the data layer and `investment-brain` as the analysis engine on top of it.

**Step 1 — Start market-intelligence:**
```bash
cd mcps/market-intelligence
uv sync
# Keep this terminal open (or add to Claude Desktop config below)
uv run market-intelligence
```

**Step 2 — Wire investment-brain to it:**

Mac / Linux:
```bash
export MARKET_INTELLIGENCE_CMD="uv run --directory /path/to/Claude-Powerhouse/mcps/market-intelligence market-intelligence"
```

Windows (PowerShell):
```powershell
$env:MARKET_INTELLIGENCE_CMD = "uv run --directory C:\path\to\Claude-Powerhouse\mcps\market-intelligence market-intelligence"
```

**Step 3 — Analyze:**
```bash
cd mcps/investment-brain
pip install -r requirements.txt
python main.py analyze TSM
```

**Step 4 (optional) — Claude Desktop config for both MCPs:**
```json
{
  "mcpServers": {
    "market-intelligence": {
      "command": "uv",
      "args": ["run", "--directory", "C:\\path\\to\\mcps\\market-intelligence", "market-intelligence"]
    },
    "investment-brain": {
      "command": "python",
      "args": ["C:\\path\\to\\mcps\\investment-brain\\mcp_wrapper.py"]
    }
  }
}
```

When both MCPs are registered, Claude Desktop can call `analyze_stock`, `screen_stocks`, `paper_trade`, and `portfolio_review` as tools directly — no copy-pasting required.

---

## Skills

> Each skill states its target. Install in the matching environment.

| Skill | Target | Purpose |
|---|---|---|
| [Software Team](./skills/Powerhouse-software-team/) | **CLI only** | Full AI dev team — PM plans, Dev builds, QA reviews. Spec-first, layer-gated, four-agent pipeline. |
| [OpenCode Handoff](./skills/Powerhouse-opencode-handoff/) | **CLI only** | Hand off mechanical coding tasks to OpenCode + MiniMax M2 (free). CC plans + reviews; OC executes in an isolated git worktree. Auto-suggests when the task profile is mechanical. |
| [Project Setup Kit](./skills/Powerhouse-Claud-Project-Setup-Kit/) | **CLI + Web** | AI Workspace Architect — project setup, structure auditing, CLAUDE.md generation. |
| [Prompt Optimizer](./skills/Powerhouse-Prompt-Optimizer/) | **CLI + Web** | Expert-grade prompt engineering using the latest heuristics. |
| [Resume Specialist](./skills/Powerhouse-Resume-Specialist/) | **CLI + Web** | Premium DOCX formatting and ATS optimization. |

### Installing Web Skills (Claude.ai)
1. Download the `.skill` file from the skill's folder.
2. Open **Claude.ai → Settings → Skills**.
3. Click **Install Skill** and upload the file.

### Installing CLI Skills (Claude Code)
Skills in `.claude/skills/` activate automatically when you work in this repo. No manual install needed.

---

## Development Workflow

This repo runs its own software-team pipeline. Every feature follows:

```
PM Tech Lead → [Research?] → Dev Engineer → QA Engineer → Human Approve → Merge
```

Use the `/powerhouse` command for all development operations:

| Command | What it does |
|---|---|
| `/powerhouse status` | Current layer + next unchecked task |
| `/powerhouse plan [feature]` | PM Tech Lead produces a ticket |
| `/powerhouse build` | Dev Engineer implements the ticket |
| `/powerhouse review` | QA Engineer validates the changes |
| `/powerhouse branch [name]` | Creates `feature/L{N}-[name]` |
| `/powerhouse pr` | Type-check → rebase → create PR |
| `/powerhouse next` | First unchecked task across all sub-projects |

See [BUILD_STATUS.md](./BUILD_STATUS.md) for current progress.

---

## Getting Started

### Prerequisites

| Tool | Required For | Install |
|------|-------------|---------|
| **Node.js 20+** | CLI scaffolding (`npx powerhouse`) | [nodejs.org](https://nodejs.org) |
| **Claude Code** | `/powerhouse` skill commands | [docs.anthropic.com](https://docs.anthropic.com/en/docs/claude-code) |
| **uv** (optional) | Running MCP servers via `uvx` | [astral.sh/uv](https://astral.sh/uv) |
| **Python 3.10+** (optional) | `investment-brain` engine | [python.org](https://python.org) |
| **gstack** (optional) | Browser automation in skills | [github.com/garrytan/gstack](https://github.com/garrytan/gstack) |

### Clone & Install

```bash
git clone https://github.com/bot8080/Claude-Powerhouse.git
cd Claude-Powerhouse
npm install
npm link                    # makes `powerhouse` available globally
```

### Install gstack (optional — for workflow skills)

```bash
git clone --depth 1 https://github.com/garrytan/gstack.git ~/.claude/skills/gstack
cd ~/.claude/skills/gstack && ./setup --team
```

---

## Installing MCP Servers

### Via uvx (recommended)

```bash
uvx market-intelligence
```

### Via pip

```bash
pip install git+https://github.com/bot8080/Claude-Powerhouse.git#subdirectory=mcps/market-intelligence
```

---

## Installing Skills

### From GitHub (raw URL)

For any skill in this repo, use the raw URL directly:

```bash
# Upload to Claude.ai via Settings → Skills → Install Skill
# Use the raw URL: https://raw.githubusercontent.com/bot8080/Claude-Powerhouse/main/skills/<skill-name>/SKILL.md
```

### Example: Powerhouse-software-team skill

1. Go to: `https://raw.githubusercontent.com/bot8080/Claude-Powerhouse/main/skills/Powerhouse-software-team/SKILL.md`
2. Copy the content
3. Claude.ai → Settings → Skills → Install Skill → Paste

---

## License

MIT — see [LICENSE](./LICENSE).

> Financial data is for informational purposes only. Always verify before making investment decisions.

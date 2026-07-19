# MultiAgents-Powerhouse

> **Source-only monorepo.** Nothing is published to npm or PyPI. Clone this repo to use any component.

Two products built together: **financial MCP servers** and **AI development workflow skills**.

- **MCP servers** (market-intelligence + investment-brain) — real Python code, real stock data
- **Skills** (Software Team, Project Setup Kit, Prompt Optimizer, Resume Specialist) — installable in Claude
- **Agent definitions** — spec-first development roles for OpenCode and Claude Code (maintainer tooling in `.internal/`)

---

## What This Is NOT

| Not this | Because |
|----------|---------|
| An npm package | Nothing published. Source-only. |
| A marketplace | Skills are `.skill` files — manual download + upload. |
| Universal agent system | Setup varies per tool. Not "works everywhere out of the box." |
| A framework | It's a monorepo. Use what fits, ignore the rest. |

---

## Quick Start

### Option 1: Financial Analysis via MCP

Use real stock data in Claude Desktop. Clone → install → done.

```bash
git clone https://github.com/bot8080/MultiAgents-Powerhouse.git
cd MultiAgents-Powerhouse

# Terminal 1 — start data server
cd mcps/market-intelligence
uv sync
uv run market-intelligence

# Terminal 2 — analyze
cd mcps/investment-brain
pip install -r requirements.txt
python main.py analyze NVDA
```

See [Product 1: MCP Servers](#product-1-mcp-servers) below for all 8 tools.

### Option 2: AI Development Workflow

Add structured PM→Dev→QA pipeline to your project. Works in Claude Code or Claude.ai web.

**Claude Code users** (terminal):
```
/pst plan "feature"   → PM writes ticket
/pst build            → Dev implements
/pst review           → QA validates
```

**Claude.ai web users** (download skill file):
1. Download the `.skill` file from `skills/Powerhouse-software-team/`
2. Claude.ai → Settings → Skills → Install Skill
3. Say "set up an AI dev team" in any chat

See [Product 2: AI Skills](#product-2-ai-workflow-skills) below for all 4 skills.

### Option 3: Reference (maintainers)

For developers extending this repository, see the hidden `.internal/` folder which contains agent definitions, CLI scaffolding, templates, and internal configuration. These files are not required for using the MCP servers or the public skills.

---

## Stats

| Component | Count | Notes |
|-----------|-------|-------|
| MCP servers | 2 | market-intelligence + investment-brain |
| AI skills | 4 | Software Team, Project Setup Kit, Prompt Optimizer, Resume Specialist |
| Agent definitions | 7 | PM Lead, Dev, QA, Research (shared) + Advisor, Mechanical (OpenCode), Dispatcher (Claude Code) |
| Python files (MCPs) | 25+ | Across both servers |
| Markets covered | 3 | US, India (NSE/BSE), Canada (TSX) |
| MCP tools | 8 | Per market-intelligence server |

---

## Product 1: MCP Financial Servers

Financial intelligence servers for Claude Desktop. Real data, real code. Clone and run.

| Server | Markets | What it does | Status |
|--------|---------|--------------|--------|
| [market-intelligence](./mcps/market-intelligence/) | US, India, Canada | 8 tools: stock data, technicals, scoring, FII/DII flows | Shipped |
| [investment-brain](./mcps/investment-brain/) | US, India, Canada | Auto-scoring, screener, portfolio tracker, paper trading | Shipped |

### market-intelligence Tools

| Tool | Returns | Example |
|------|---------|---------|
| `resolve_tickers` | Clean Yahoo Finance symbols | `"Apple"` → `"AAPL"` |
| `get_full_profile` | Price, PE, ROE, margins, growth, analyst targets, risk | One call = 8 sections |
| `get_batch_profiles` | Full profiles for up to 20 stocks in 1 call | Avoids the 112-call problem |
| `get_technicals` | RSI, MACD, ADX, Bollinger, stop loss | Signal + numbers |
| `get_scoring_data` | 4-pillar score (V+Q+M+R, 100pts) + verdict | BUY / HOLD / SELL |

### investment-brain Commands

```bash
python main.py analyze NVDA                    # Full analysis + Claude prompt
python main.py screen --pe-max 25 --roe-min 15 # Filter + rank by criteria
python main.py paper-buy TSM 10 175 --stop-loss 158    # Virtual buy
python main.py portfolio                                 # Holdings + P&L
```

**Install:**

```bash
git clone https://github.com/bot8080/MultiAgents-Powerhouse.git
cd MultiAgents-Powerhouse/mcps/market-intelligence
uv sync && uv run market-intelligence   # keep terminal open
```

Configure Claude Desktop to use the server — see [mcps/README.md](./mcps/README.md) for full setup.

---

## Product 2: AI Workflow Skills

Installable skills that extend Claude's behavior. Manual download required.

| Skill | Target | What it does | When to Use |
|-------|--------|--------------|-------------|
| [Software Team](./skills/Powerhouse-software-team/) | CLI | PM→Dev→QA pipeline with spec-first discipline | Building complex apps with structured development |
| [Project Setup Kit](./skills/Powerhouse-Claud-Project-Setup-Kit/) | Both | Project knowledge base setup and audit | Starting a new project or auditing existing code |
| [Prompt Optimizer](./skills/Powerhouse-Prompt-Optimizer/) | Both | Prompt engineering using Anthropic 2025 heuristics | Fixing vague or ineffective prompts |
| [Resume Specialist](./skills/Powerhouse-Resume-Specialist/) | Both | ATS-optimized DOCX resume formatting | Formatting professional resumes |

> **CLI** = Claude Code terminal. **Both** = Claude Code + Claude.ai web.

**Install:**

1. Download the `.skill` file from the skill's folder
2. Claude.ai → Settings → Skills → Install Skill — upload the file
3. The skill triggers automatically based on what you ask

See [skills/README.md](./skills/README.md) for troubleshooting.

---

## Real-World Scenarios

### Scenario 1: Analyze a Stock in Claude

**Your team:**

1. **market-intelligence MCP** — fetch live stock data
2. **investment-brain** — score, screen, build portfolio prompt
3. **Claude** — format output into Summary Card

**Result:** Full investment analysis using live data. ~90% fewer Claude tokens vs. manual research.

---

### Scenario 2: Build a Feature with Structured Team

**Your team:**

1. **PM Tech Lead** — writes TECH_SPEC.md, enforces layer gates
2. **Research Engineer** — investigates unfamiliar APIs (auto-triggered)
3. **Dev Engineer** — implements the ticket scope
4. **QA Engineer** — 7-point validation before human approve

**Result:** Spec-first delivery with quality gates at every layer.

---

### Scenario 3: Portfolio Review with Paper Trading

**Your team:**

1. **investment-brain** — pull portfolio holdings + scores
2. **investment-brain** — compare vs. benchmarks
3. **Claude** — format into readable report

**Result:** Full portfolio review in seconds. Paper trade new positions before committing real capital.

---

## Design Principles

1. **Source-only** — nothing published to npm or PyPI. Clone and use directly.
2. **Deliverable-focused** — real code, real data, measurable outcomes. Not generic prompts.
3. **Spec-first discipline** — no code without a spec. No Layer N without Layer N-1 complete.
4. **Honest about scope** — MCP servers work. Skills need manual install. CLI is local-only.
5. **Tool-agnostic agents** — agent definitions are markdown files. They work wherever your AI tool reads instruction files.

---

## Contributing

PRs welcome. The fastest path to a merged PR is **one change at a time**.

**Always welcome as a PR:**

- New MCP tool or market coverage
- New skill or improved existing skill
- Bug fixes in MCP server or skill code
- Documentation improvements

**Start a discussion first:**

- New directories or structural changes
- Multi-file changes across the repo
- New integration formats or platforms

See [.internal/BUILD_STATUS.md](./.internal/BUILD_STATUS.md) for current progress.

---

## Project Structure

```
MultiAgents-Powerhouse/
├── mcps/                          # MCP financial servers
│   ├── market-intelligence/       # US/India/Canada stock data (8 tools)
│   └── investment-brain/          # Scoring, screening, portfolio (7 layers)
├── skills/                        # AI workflow skills
│   ├── Powerhouse-software-team/  # PM→Dev→QA pipeline [CLI]
│   ├── Powerhouse-Claud-Project-Setup-Kit/  # Project setup
│   ├── Powerhouse-Prompt-Optimizer/        # Prompt engineering
│   └── Powerhouse-Resume-Specialist/       # DOCX resume
├── docs/                          # Quickstart, cheatsheet, troubleshooting
├── .internal/                     # Maintainer-only files
│   ├── .opencode/agents/          # 6 agent definitions (OpenCode)
│   ├── .claude/agents/            # 5 agent definitions (Claude Code)
│   ├── .claude/commands/          # PST slash commands
│   ├── .powerhouse/               # /pst ticket + dispatch runtime
│   ├── cli/                       # Local scaffolding (not on npm)
│   ├── templates/                 # Project templates
│   ├── opencode.json              # Base config (no hardcoded models)
│   ├── opencode.go.json           # Go plan overlay (per-agent routing)
│   ├── AGENTS.md                  # Session brief + auto-routing rules
│   └── BUILD_STATUS.md            # Development progress tracker
```

---

## Documentation

| Guide | What it covers |
|-------|---------------|
| [docs/QUICKSTART.md](./docs/QUICKSTART.md) | 5-minute setup for MCPs + skills |
| [docs/CHEATSHEET.md](./docs/CHEATSHEET.md) | All commands on one page |
| [docs/TROUBLESHOOTING.md](./docs/TROUBLESHOOTING.md) | Common errors and fixes |
| [.internal/AGENTS.md](./.internal/AGENTS.md) | Session protocol, agent pipeline, layer gates (maintainer) |
| [.internal/BUILD_STATUS.md](./.internal/BUILD_STATUS.md) | Development progress tracker (maintainer) |
| [mcps/README.md](./mcps/README.md) | MCP servers overview + install |
| [skills/README.md](./skills/README.md) | AI skills overview + install |

---

## License

MIT — see [LICENSE](./LICENSE).

> Financial data is for informational purposes only. Always verify before making investment decisions.
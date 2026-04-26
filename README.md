# Claude-Powerhouse

A professional-grade collection of **MCP Servers** and **Claude Skills** that transform Claude from a chat assistant into a structured, spec-driven development powerhouse.

---

## What's Inside

```
Claude-Powerhouse/
├── mcps/                              # MCP Servers — Claude Desktop + Claude Code
│   ├── market-intelligence/           # US/India/CA financial intelligence (shipped)
│   └── investment-brain/              # AI-driven analysis engine (in development)
├── skills/                            # Skills — Claude.ai Web + Claude Code CLI
│   ├── software-team/                 # [CLI] Full PM→Dev→QA pipeline
│   ├── Powerhouse-Claud-Project-Setup-Kit/   # [Both] AI Workspace Architect
│   ├── Powerhouse-Prompt-Optimizer/   # [Both] Expert prompt engineering
│   └── Powerhouse-Resume-Specialist/  # [Both] DOCX + ATS optimization
└── .claude/
    ├── agents/                        # PM / Research / Dev / QA agent definitions
    ├── skills/powerhouse/             # /powerhouse unified command skill
    └── hooks/                         # Gstack gate + spec advisory hooks
```

> **Target labels matter.** Each skill lists `[CLI]`, `[Web]`, or `[Both]` — install in the right environment or it won't activate.

---

## MCP Servers

> **Target: Claude Desktop + Claude Code (CLI)**
> Install via `claude_desktop_config.json` or as a Claude Code MCP.

### Market-Intelligence (shipped)

Real-time financial intelligence across US (NASDAQ/NYSE), India (NSE/BSE), and Canada (TSX).

**8 tools:** multi-market ticker resolution, full company profiles, technical analysis (RSI/MACD/ADX/Bollinger), 4-pillar scoring, insider/institutional activity, FII/DII flows, Nifty valuation, US macro data.

```bash
cd mcps/market-intelligence
uv sync
uv run market-intelligence
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

---

## Skills

> Each skill states its target. Install in the matching environment.

| Skill | Target | Purpose |
|---|---|---|
| [Software Team](./skills/software-team/) | **CLI only** | Full AI dev team — PM plans, Dev builds, QA reviews. Spec-first, layer-gated, four-agent pipeline. |
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

```bash
git clone https://github.com/bot8080/claude-powerhouse.git
cd Claude-Powerhouse

# Install gstack (required for Claude Code workflow skills)
git clone --depth 1 https://github.com/garrytan/gstack.git ~/.claude/skills/gstack
cd ~/.claude/skills/gstack && ./setup --team
```

---

## License

MIT — see [LICENSE](./LICENSE).

> Financial data is for informational purposes only. Always verify before making investment decisions.

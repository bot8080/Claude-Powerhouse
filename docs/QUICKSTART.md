# Quick Start — MultiAgents-Powerhouse in 5 Minutes

> Pick the path below that matches your situation.

---

## Option A: Financial Analysis via MCP

**Goal:** Analyze stocks using market-intelligence + investment-brain.

```bash
# Clone the repo
git clone https://github.com/bot8080/MultiAgents-Powerhouse.git
cd MultiAgents-Powerhouse

# Terminal 1 — Start data server
cd mcps/market-intelligence
uv sync
uv run market-intelligence

# Terminal 2 — Run analysis
cd mcps/investment-brain
pip install -r requirements.txt
python main.py analyze NVDA
```

**All 8 MCP tools:**

| Tool | What you get |
|------|--------------|
| `resolve_tickers("Apple")` | → `AAPL` (handles US/India/Canada) |
| `get_full_profile("NVDA")` | Price, PE, ROE, margins, growth, risk |
| `get_batch_profiles(...)` | Up to 20 stocks in 1 call |
| `get_technicals("NVDA")` | RSI, MACD, ADX, Bollinger, stop loss |
| `get_scoring_data("NVDA")` | BUY/HOLD/SELL (V+Q+M+R) |
| `get_institutional_activity("NVDA")` | Insider trades, holders |
| `get_fii_dii_flows()` | India FII/DII flows |
| `get_nifty_valuation()` | Nifty 50 P/E zone |

**Register in Claude Desktop:**

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

**Next step:** Read [market-intelligence docs](../mcps/market-intelligence/README.md) for all tool details.

---

## Option B: Install Skills in Claude.ai

**Goal:** Add Powerhouse skills to Claude.ai web.

| Skill | File | What it does |
|-------|------|--------------|
| Software Team | [.skill](../skills/Powerhouse-software-team/Powerhouse-software-team.skill) | PM→Dev→QA pipeline |
| Prompt Optimizer | [.skill](../skills/Powerhouse-Prompt-Optimizer/Powerhouse-Prompt-Optimizer.skill) | Fix vague prompts |
| Project Setup Kit | [.skill](../skills/Powerhouse-Claud-Project-Setup-Kit/Powerhouse-Claud-Project-Setup-Kit.skill) | Audit knowledge base |
| Resume Specialist | [.skill](../skills/Powerhouse-Resume-Specialist/Powerhouse-Resume-Specialist.skill) | Format DOCX resumes |

**Install steps:**

1. Download the `.skill` file from the links above
2. Go to [Claude.ai](https://claude.ai) → **Settings** → **Skills**
3. Click **Install Skill** and upload the file

**Next step:** Start a chat and say the trigger phrase from each skill's README.

---

## Option C: Use Agent Definitions in Your Project

**Goal:** Add structured agent roles to any AI coding tool.

### OpenCode (auto-load)

Agents in `.opencode/agents/` load automatically when opening this repo in OpenCode. Copy them to your project if you want them elsewhere.

### Claude Code

Agents in `.claude/agents/` auto-activate when working in this repo. For your own project, copy the agent files to `~/.claude/agents/`.

| Agent | File |
|-------|------|
| PM Tech Lead | `pm-tech-lead.md` |
| Dev Engineer | `dev-engineer.md` |
| QA Engineer | `qa-engineer.md` |
| Research Engineer | `research-engineer.md` |
| Worker-Mechanical | `worker-mechanical.md` |
| Advisor | `advisor.md` |

**Next step:** Read [AGENTS.md](../AGENTS.md) for the full auto-routing rules.

---

## What Next?

| You just did... | Read next |
|----------------|-----------|
| Set up MCP servers | [market-intelligence README](../mcps/market-intelligence/README.md) |
| Installed skills | [skills/README.md](../skills/README.md) |
| Copied agents | [AGENTS.md](../AGENTS.md) — session protocol |

## Need Help?

- [Cheat Sheet](./CHEATSHEET.md) — one-page command reference
- [Troubleshooting](./TROUBLESHOOTING.md) — common errors and fixes
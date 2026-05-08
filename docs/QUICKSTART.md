# Quick Start — MultiAgents-Powerhouse in 5 Minutes

> Pick the path below that matches your situation.

---

## Option A: Start a New Project

**Goal:** Scaffold a new app with the full agent pipeline.

> **Note:** Not on npm. Requires `npm link` from the cloned repo first.

```bash
# From your clone of MultiAgents-Powerhouse:
npm link
# Then in any directory:
powerhouse init my-app
```

You'll be prompted to choose:
- **Stack:** Expo (React Native)
- **Backend:** None / Firebase / Supabase
- **Payments:** No / Stripe
- **AI Workflow:** None / OpenCode AI

**What you get:**
- Production-ready project with ESLint, Prettier, Jest, Husky
- `AGENTS.md` + `.claude/` with PM/Dev/QA agents
- `BUILD_STATUS.md` layer tracker
- `/pst` commands ready to use

**Next step:** `cd my-app` → run `claude` → type `/pst status`

---

## Option B: Add to Existing Project

**Goal:** Add workflow conventions without touching your source code.

> **Note:** Not on npm. Requires `npm link` from the cloned repo first (same as Option A).

```bash
powerhouse apply
```

**What changes:**
- Adds `AGENTS.md`, `.claude/`, `.github/`, `.husky/`, `docs/`, `session-tracking/`
- Never overwrites your existing files
- 100% non-destructive

**Next step:** `claude` → `/pst status`

---

## Option C: Use Skills in Claude.ai (No CLI)

**Goal:** Install Powerhouse skills in Claude.ai web.

| Skill | Install | What it does |
|-------|---------|--------------|
| Software Team | [Download .skill](../skills/Powerhouse-software-team/Powerhouse-software-team.skill) | PM/Dev/QA pipeline |
| Prompt Optimizer | [Download .skill](../skills/Powerhouse-Prompt-Optimizer/Powerhouse-Prompt-Optimizer.skill) | Fix vague prompts |
| Project Setup Kit | [Download .skill](../skills/Powerhouse-Claud-Project-Setup-Kit/Powerhouse-Claud-Project-Setup-Kit.skill) | Audit knowledge base |
| Resume Specialist | [Download .skill](../skills/Powerhouse-Resume-Specialist/Powerhouse-Resume-Specialist.skill) | Format DOCX resumes |

**Install steps:**
1. Download the `.skill` file
2. Go to [Claude.ai](https://claude.ai) → **Settings** → **Skills**
3. Click **Install Skill** and upload the file

**Next step:** Start a chat and say the trigger phrase from each skill's README.

---

## Option D: Financial Analysis via MCP

**Goal:** Analyze stocks using market-intelligence + investment-brain.

```bash
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

**Next step:** Register both in Claude Desktop for tool-calling:

```json
{
  "mcpServers": {
    "market-intelligence": { "command": "uv", "args": ["run", "--directory", "C:\\path\\to\\mcps\\market-intelligence", "market-intelligence"] },
    "investment-brain": { "command": "python", "args": ["C:\\path\\to\\mcps\\investment-brain\\mcp_wrapper.py"] }
  }
}
```

---

## What Next?

| You just did... | Read next |
|----------------|-----------|
| `npx powerhouse init` | [Powerhouse-software-team README](../skills/Powerhouse-software-team/README.md) — how to use `/pst` |
| `npx powerhouse apply` | [BUILD_STATUS.md](../BUILD_STATUS.md) — current layer progress |
| Installed web skills | [skills/README.md](../skills/README.md) — all skill details |
| Set up MCP servers | [market-intelligence README](../mcps/market-intelligence/README.md) — full tool docs |

## Need Help?

- [Cheat Sheet](./CHEATSHEET.md) — one-page command reference
- [Troubleshooting](./TROUBLESHOOTING.md) — common errors and fixes

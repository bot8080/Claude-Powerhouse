# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Repo Is

A monorepo with two components:
1. **`mcps/`** — MCP servers that give Claude real-time financial data tools
2. **`skills/`** — `.skill` files that extend Claude.ai's behavior (installed via Settings → Skills)

---

## MCP Servers (`mcps/`)

### market-intelligence

Financial intelligence server across US (NASDAQ/NYSE), India (NSE/BSE), and Canada (TSX). Built with FastMCP + yfinance.

**Commands:**
```bash
cd mcps/market-intelligence
uv sync                        # Install dependencies
uv run market-intelligence     # Run server

# Syntax-check all source files
python -m py_compile src/market_intelligence/*.py

# Quick live test
uv run python -c "from market_intelligence.resolver import resolve_tickers_impl; import json; print(json.dumps(resolve_tickers_impl(['AAPL']), indent=2))"
```

**Architecture:**
```
src/market_intelligence/
  server.py      — FastMCP entry point; all @mcp.tool registrations
  resolver.py    — Dynamic ticker resolution (.NS/.TO/.BO/.L suffixes, no static maps)
  profile.py     — get_full_profile (1 yf.Ticker.info call → 8 sections) + get_batch_profiles (ThreadPoolExecutor)
  technicals.py  — RSI, MACD, ADX, ATR, Bollinger, MFI, OBV, SMA 50/200 via ta library
  india.py       — FII/DII flows (nsepython) + Nifty 50 P/E zone (nsetools, yfinance fallback)
  activity.py    — Insider trades, institutional holders, upgrades/downgrades, earnings calendar
  scoring.py     — 4-pillar score: Valuation + Quality + Momentum + Risk (25pts each, 100 total)
  macro.py       — US macro data
```

**Key conventions:**
- All yfinance fields accessed via `.get()` — never crash on missing keys
- All external calls wrapped in `try/except` — return `{"error": "..."}` dicts, never raise
- `time.sleep(0.3)` between yfinance calls in batch mode
- `ta` library indicators require 50+ data points minimum
- `resolve_tickers` must NEVER append words like "India", "stock", or "NSE" to queries

**Claude Desktop config** (`%APPDATA%\Claude\claude_desktop_config.json`):
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

**Typical call order:** `resolve_tickers` → `get_batch_profiles` → `get_technicals` → `get_institutional_activity` → `get_scoring_data`. For India macro: `get_nifty_valuation` + `get_fii_dii_flows`.

---

### investment-brain (in development)

Local Python engine that pre-computes analysis and generates minimal Claude prompts (~20–50 tokens vs ~3,500). Claude only formats output.

**Commands:**
```bash
cd mcps/investment-brain
pip install -r requirements.txt
python main.py analyze TSM
python main.py screen --pe-max 25 --roe-min 15 --sector Semis
python main.py paper-buy TSM 10 175.50 --stop-loss 158 --target 210
python main.py portfolio
```

**Architecture:**
```
config.py          — Settings, thresholds, rules
mcp_bridge.py      — JSON-RPC client for market-intelligence MCP
data_fetcher.py    — MCP primary, yfinance fallback
deal_breaker.py    — 9-rule disqualification checker
scorer.py          — 35/35/30 scoring engine (Fundamental/Technical/Smart Money)
portfolio_db.py    — SQLite portfolio/watchlist/history
paper_trading.py   — Virtual ledger with rule enforcement
prompt_builder.py  — Claude prompt generator
main.py            — CLI entry point
```

Scoring: Fundamental 35 / Technical 35 / Smart Money 30. Deal-breaker checks run before scoring. Output is a copy-pasteable prompt block + JSON for Claude.

---

## Skills (`skills/`)

Each skill lives in `skills/<skill-name>/` with a `.skill` file and `README.md`.

**`.skill` file format:**
- YAML frontmatter: `name:` and `description:` fields
- The `description:` is the activation trigger — make it exhaustive with synonyms and intent patterns
- Body: markdown instructions Claude follows when activated
- Skills must be self-contained — assume no external context

**Adding a skill:**
1. Create `skills/<name>/<name>.skill` with YAML frontmatter + markdown instructions
2. Create `skills/<name>/README.md`
3. Add a row to the skills table in the root `README.md` and `skills/README.md`

**Current skills:**
| Skill | Purpose |
|---|---|
| `Powerhouse-Claud-Project-Setup-Kit` | AI Workspace Architect for project setup and auditing |
| `Powerhouse-Prompt-Optimizer` | Expert prompt engineering using latest heuristics |
| `Powerhouse-Resume-Specialist` | DOCX formatting + ATS optimization |

**Authoring pattern:** detect context first, then branch into modes (see `Powerhouse-Claud-Project-Setup-Kit` as the reference implementation). Skills that produce file output should save to `/mnt/user-data/outputs/`.

---

## gstack

gstack provides a headless browser and a suite of workflow skills. Install it globally before doing any work in this repo:

```bash
git clone --depth 1 https://github.com/garrytan/gstack.git ~/.claude/skills/gstack
cd ~/.claude/skills/gstack && ./setup --team
```

Verify: `test -d ~/.claude/skills/gstack/bin && echo "GSTACK_OK" || echo "GSTACK_MISSING"`

**Web browsing rule:** Always use `/browse` from gstack for all web browsing tasks. Never use `mcp__claude-in-chrome__*` tools.

**Available skills:**

| Skill | Purpose |
|---|---|
| `/browse` | Headless browser — use for ALL web browsing |
| `/office-hours` | Office hours facilitation |
| `/plan-ceo-review` | CEO review of plans |
| `/plan-eng-review` | Engineering review of plans |
| `/plan-design-review` | Design review of plans |
| `/design-consultation` | Design consultation |
| `/design-shotgun` | Rapid design exploration |
| `/design-html` | HTML design generation |
| `/review` | Code review |
| `/ship` | Ship a feature end-to-end |
| `/land-and-deploy` | Land and deploy changes |
| `/canary` | Canary deployment |
| `/benchmark` | Performance benchmarking |
| `/connect-chrome` | Connect to Chrome browser |
| `/qa` | Full QA pass |
| `/qa-only` | QA without other steps |
| `/design-review` | Design review |
| `/setup-browser-cookies` | Set up browser cookies |
| `/setup-deploy` | Configure deployment |
| `/setup-gbrain` | Set up gbrain |
| `/retro` | Retrospective |
| `/investigate` | Investigate an issue |
| `/document-release` | Document a release |
| `/codex` | Codex skill |
| `/cso` | CSO workflow |
| `/autoplan` | Automatic planning |
| `/plan-devex-review` | DevEx review of plans |
| `/devex-review` | Developer experience review |
| `/careful` | Careful/conservative mode |
| `/freeze` | Freeze changes |
| `/guard` | Guard mode |
| `/unfreeze` | Unfreeze changes |
| `/gstack-upgrade` | Upgrade gstack |
| `/learn` | Learning workflow |

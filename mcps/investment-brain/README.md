# Investment Brain

> **You are here:** Home → MCP Servers → investment-brain

**Local Python engine that does all the heavy lifting** — data fetching, scoring, screening, portfolio tracking, paper trading. Claude only formats the output.

**Result: ~80% less Claude token usage per analysis.**

---

## What It Does

| Feature | Description |
|---------|-------------|
| **Stock Analyzer** | Fetches data via MCP or yfinance, scores 35/35/30, outputs Claude-ready prompt |
| **Screener** | Filters universe by criteria, ranks by score, outputs batch prompt |
| **Portfolio Tracker** | SQLite-backed holdings with sector allocation, P&L, risk flags |
| **Paper Trading** | Virtual ledger with rule enforcement (position limits, stop losses) |
| **Prompt Builder** | Generates minimal prompts (20-50 tokens) + structured JSON for Claude |
| **Web UI** | FastAPI dashboard at `:8000` — analyze, screen, paper trade from a browser |
| **MCP Server** | Exposes investment-brain itself as an MCP tool for Claude Desktop / Claude Code |

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│  YOUR LOCAL MACHINE                                         │
│                                                             │
│  ┌─────────────────┐      ┌─────────────────────────────┐  │
│  │ Claude Desktop  │◄────►│  market-intelligence MCP    │  │
│  │                 │      │  (running via uv)           │  │
│  └─────────────────┘      └─────────────────────────────┘  │
│           ▲                            │                    │
│           │ You paste minimal prompt   │ MCP data          │
│           │ (20-50 tokens)             ▼                    │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  python main.py analyze TSM                         │   │
│  │  ↓                                                  │   │
│  │  • Fetches via MCP or yfinance                      │   │
│  │  • Scores: Fund 35 / Tech 35 / SM 30                │   │
│  │  • Checks 9 deal-breakers                           │   │
│  │  • Builds minimal prompt + JSON                     │   │
│  │  • You copy-paste into Claude                       │   │
│  └─────────────────────────────────────────────────────┘   │
│                            │                                │
│                            │ Optional: deploy to server    │
│                            ▼                                │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  SERVER (any Linux/Mac/Windows)                     │   │
│  │  • Web UI for portfolio tracking (:8000)            │   │
│  │  • yfinance for autonomous data                     │   │
│  │  • Sync SQLite DB via export/import                 │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

---

## Quick Start

### 1. Install

```bash
cd mcps/investment-brain
pip install -r requirements.txt
```

### 2. Configure MCP (optional)

Set the `MARKET_INTELLIGENCE_CMD` environment variable to point at your running `market-intelligence` MCP server. If unset, investment-brain falls back to yfinance only.

**Mac / Linux:**
```bash
export MARKET_INTELLIGENCE_CMD="uv run --directory /path/to/MultiAgents-Powerhouse/mcps/market-intelligence market-intelligence"
```

**Windows (PowerShell):**
```powershell
$env:MARKET_INTELLIGENCE_CMD = "uv run --directory C:\path\to\MultiAgents-Powerhouse\mcps\market-intelligence market-intelligence"
```

**Windows (Command Prompt):**
```cmd
set MARKET_INTELLIGENCE_CMD=uv run --directory C:\path\to\MultiAgents-Powerhouse\mcps\market-intelligence market-intelligence
```

Add the export to your shell profile (`.bashrc`, `.zshrc`, PowerShell `$PROFILE`) to make it permanent.

### 3. Analyze a Stock

```bash
python main.py analyze TSM
```

Output:
```
🔍 Analyzing TSM...

📊 Scores: Fund 28/35 | Tech 30/35 | SM 24/30
   Total: 82/100 | Verdict: BUY
   Account: TFSA | Stop Loss: $158.00

📋 Copy this entire block into Claude:
============================================================
Format this stock data into a Summary Card per my rules...
[JSON payload]
============================================================
```

### 4. Run Screener

```bash
python main.py screen --pe-max 25 --roe-min 15
python main.py screen --pe-max 25 --roe-min 15 --sector Technology AAPL MSFT NVDA TSM ASML
```

### 5. Paper Trade

```bash
python main.py paper-buy TSM 10 175.50 --stop-loss 158 --target 210
python main.py paper-sell TSM 10 185.00 --reason "Target hit"
```

### 6. Portfolio Review

```bash
python main.py portfolio
```

### 7. Web UI (optional)

```bash
python -m uvicorn web_app:app --host 0.0.0.0 --port 8000
```

Then open `http://localhost:8000` in a browser.

---

## Commands

| Command | Description |
|---------|-------------|
| `analyze <ticker> [--market US\|CA\|IN]` | Full analysis + Claude prompt |
| `screen [tickers...] [--pe-max N] [--roe-min N] [--sector NAME]` | Filter + rank stocks |
| `portfolio` | Review holdings + generate prompt |
| `paper-buy <t> <shares> <price> [--stop-loss] [--target]` | Virtual buy with rule checks |
| `paper-sell <t> <shares> <price> [--reason]` | Virtual sell |
| `watchlist` | Show watchlist |
| `history` | Show decision log |
| `export [--file PATH]` | Backup to JSON |
| `import <file>` | Restore from JSON |

---

## Token Savings

| Task | Claude alone | Python + Claude | Savings |
|------|-------------|-----------------|---------|
| Single stock analysis | ~3,500 tokens | ~400 tokens | **88%** |
| Portfolio review (20 holdings) | ~8,000 tokens | ~600 tokens | **92%** |
| Screener (10 stocks) | ~5,000 tokens | ~500 tokens | **90%** |
| Paper trade ticket | ~1,000 tokens | ~200 tokens | **80%** |

**Why:** Python does data fetching, scoring, and structuring. Claude only formats.

---

## Deploy to a Server

```bash
# On any server with Python 3.10+
git clone <repo>
cd mcps/investment-brain
pip install -r requirements.txt

# Run web UI
python -m uvicorn web_app:app --host 0.0.0.0 --port 8000

# Or just CLI via SSH
python main.py analyze TSM
```

---

## File Structure

```
mcps/investment-brain/
├── config.py              # Settings, thresholds, rules, env-var wiring
├── mcp_bridge.py          # CLIENT: connects investment-brain → market-intelligence MCP
├── mcp_wrapper.py         # SERVER: exposes investment-brain as MCP server for Claude
├── data_fetcher.py        # MCP primary, yfinance fallback
├── deal_breaker.py        # 9-rule disqualification checker
├── scorer.py              # 35/35/30 scoring engine
├── portfolio_db.py        # SQLite portfolio/watchlist/history
├── paper_trading.py       # Virtual ledger with rules
├── prompt_builder.py      # Claude prompt generator
├── web_app.py             # FastAPI dashboard (browser UI + REST API)
├── main.py                # CLI entry point
├── requirements.txt       # Pinned dependencies
└── data/                  # SQLite DB (auto-created on first run)
    └── portfolio.db
```

---

## Troubleshooting

| Error | Likely Cause | Fix |
|-------|-------------|-----|
| `MARKET_INTELLIGENCE_CMD` not found | Env var not set | `$env:MARKET_INTELLIGENCE_CMD = "uv run --directory C:\path\to\mcps\market-intelligence market-intelligence"` |
| `MCP connection failed` | market-intelligence not running | Start `uv run market-intelligence` in separate terminal |
| `yfinance rate limit` | Too many requests | Wait 1 hour, or set `MARKET_INTELLIGENCE_CMD` to use MCP data layer |
| `SQLite database is locked` | Another process using DB | Close other terminals. Export first: `python main.py export`, then delete `data/portfolio.db` |
| Web UI not loading | Port 8000 in use | `python -m uvicorn web_app:app --port 8001` |
| `No module named 'yfinance'` | Dependencies not installed | `pip install -r requirements.txt` |

---

## Related

| Resource | Purpose |
|----------|---------|
| [All MCP Servers](../README.md) | Browse both servers + install guide |
| [market-intelligence](../market-intelligence/) | Data layer — investment-brain calls this |
| [Root README](../../README.md) | Full repo documentation |
| [Quick Start](../../docs/QUICKSTART.md) | 5-minute setup guide |

---

*Not licensed financial advice.*

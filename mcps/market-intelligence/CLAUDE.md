# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

`market-intelligence` — MCP server for investment analysis across US, Indian, and Canadian markets. Built with FastMCP + yfinance. 8 tools total.

## Commands

```bash
# Install dependencies
uv sync

# Run the server (for testing)
uv run market-intelligence

# Syntax check all source files
python -m py_compile src/market_intelligence/*.py

# Quick live test
uv run python -c "from market_intelligence.resolver import resolve_tickers_impl; import json; print(json.dumps(resolve_tickers_impl(['AAPL']), indent=2))"
```

## Architecture

```
src/market_intelligence/
  server.py      — FastMCP entry point, all 8 @mcp.tool registrations
  resolver.py    — Dynamic ticker resolution (no static maps), handles .NS/.TO/.BO/.L suffixes
  profile.py     — get_full_profile (1 yf.Ticker.info call → 8 sections) + get_batch_profiles (ThreadPoolExecutor)
  technicals.py  — RSI, MACD, ADX, ATR, Bollinger, MFI, OBV, SMA 50/200 via ta library
  india.py       — FII/DII flows (nsepython) + Nifty 50 P/E zone (nsetools, yfinance fallback)
  activity.py    — Insider trades, institutional holders, upgrades/downgrades, earnings calendar (yfinance)
  scoring.py     — 4-pillar score: Valuation + Quality + Momentum + Risk (25pts each, 100 total)
```

## Tools

| Tool | Markets | Description |
|------|---------|-------------|
| `resolve_tickers` | All | Resolve names → clean symbols. Call FIRST. |
| `get_full_profile` | All | All metrics in 1 call (price, valuation, quality, growth, analyst, risk, dividends) |
| `get_batch_profiles` | All | Full profiles for multiple stocks in 1 MCP call |
| `get_technicals` | All | RSI, MACD, ADX, ATR, Bollinger, stop loss suggestion |
| `get_institutional_activity` | US, Canada | Insider trades, institutional holders, upgrades/downgrades |
| `get_fii_dii_flows` | India only | FII/DII daily flows + sentiment signal |
| `get_nifty_valuation` | India only | Nifty 50 P/E zone (Excellent → Bubble) |
| `get_scoring_data` | All | 4-pillar score + deal-breaker checks + verdict (BUY/HOLD/SELL) |

## Key Conventions

- All yfinance fields accessed via `.get()` — never crash on missing keys
- All external calls wrapped in `try/except` — return `{"error": "..."}` dicts, never raise
- `time.sleep(0.3)` between yfinance calls in batch mode
- `ta` library indicators require 50+ data points minimum
- `resolve_tickers` NEVER appends words like "India", "stock", "NSE" to queries

## Claude Desktop Config

```json
{
  "mcpServers": {
    "market-intelligence": {
      "command": "uv",
      "args": ["run", "--directory", "C:\\path\\to\\MultiAgents-Powerhouse\\mcps\\market-intelligence", "market-intelligence"]
    }
  }
}
```

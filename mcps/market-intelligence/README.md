# 📈 market-intelligence

MCP server for financial intelligence across US, Indian, and Canadian markets. 8 tools, built with FastMCP + yfinance.

## Market Coverage

| Tool | US | India | Canada |
|------|----|-------|--------|
| `resolve_tickers` | ✅ | ✅ | ✅ |
| `get_full_profile` | ✅ | ✅ | ✅ |
| `get_batch_profiles` | ✅ | ✅ | ✅ |
| `get_technicals` | ✅ | ✅ | ✅ |
| `get_institutional_activity` | ✅ | ⚠️ earnings only | ✅ |
| `get_fii_dii_flows` | ❌ | ✅ | ❌ |
| `get_nifty_valuation` | ❌ | ✅ | ❌ |
| `get_scoring_data` | ✅ | ✅ | ✅ |

⚠️ Insider/holder data not available for Indian stocks via Yahoo Finance — use `get_fii_dii_flows` instead.

## Tools

| Tool | Description |
|------|-------------|
| `resolve_tickers` | Resolve company names or partial tickers → clean Yahoo Finance symbols. Handles `.NS` (India NSE), `.BO` (India BSE), `.TO` (Canada), `.L` (London). Always call this first. |
| `get_full_profile` | All metrics in 1 call: price, valuation (PE/PEG/P/B/EV), quality (ROE/margins/cashflow/debt), growth, analyst targets, risk (beta/short interest), dividends, business description |
| `get_batch_profiles` | Full profiles for up to 20 stocks in 1 MCP call using parallel fetching. Solves the 14-ticker × 8-metric = 112 call problem |
| `get_technicals` | RSI(14), MACD, ADX(14), ATR(14), Bollinger Bands, MFI(14), OBV, SMA 50/200, Golden/Death Cross, overall signal, suggested stop loss |
| `get_institutional_activity` | Insider buy/sell transactions, top institutional holders + % change, mutual fund holders, analyst upgrades/downgrades, earnings calendar |
| `get_fii_dii_flows` | NSE India FII/DII daily buy/sell/net flows + rolling totals + sentiment signal |
| `get_nifty_valuation` | Nifty 50 P/E, P/B, dividend yield + valuation zone (Excellent/Good/Fair/Expensive/Bubble) |
| `get_scoring_data` | 4-pillar score: Valuation + Quality + Momentum + Risk (25pts each, 100 total). Deal-breaker checks. Verdict: BUY/HOLD/SELL |

## Installation

```bash
pip install uv   # if not already installed
git clone https://github.com/[YOUR-USERNAME]/Claude-Powerhouse.git
cd Claude-Powerhouse/mcps/market-intelligence
uv sync
```

## Running

```bash
uv run market-intelligence
```

## Claude Desktop Config

Add to `%APPDATA%\Claude\claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "market-intelligence": {
      "command": "uv",
      "args": [
        "run",
        "--directory",
        "C:\\path\\to\\Claude-Powerhouse\\mcps\\market-intelligence",
        "market-intelligence"
      ]
    }
  }
}
```

## Typical Workflow

```
1. resolve_tickers(["Bharat Electronics", "NVDA", "SHOP"])
   → ["BEL.NS", "NVDA", "SHOP.TO"]

2. get_batch_profiles(["BEL.NS", "NVDA", "SHOP.TO"])
   → all metrics in 1 MCP call

3. get_technicals("NVDA")
   → RSI, MACD, ADX, stop loss

4. get_institutional_activity("NVDA")
   → insider trades, institutional holders, upgrades

5. get_scoring_data("NVDA")
   → V+Q+M+R score, verdict, deal-breaker check

# India macro overlay
6. get_nifty_valuation()  +  get_fii_dii_flows()
```

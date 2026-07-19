# market-intelligence MCP

> **You are here:** Home → MCP Servers → market-intelligence

> **For:** Investors, analysts, Claude Desktop users who need real-time financial data

MCP server for financial intelligence across **US, Indian, and Canadian markets.** 9 tools, built with FastMCP + yfinance.

---

## Market Coverage

| Tool | US (NASDAQ/NYSE) | India (NSE/BSE) | Canada (TSX) |
|------|-----------------|-----------------|--------------|
| `resolve_tickers` | ✅ | ✅ | ✅ |
| `get_full_profile` | ✅ | ✅ | ✅ |
| `get_batch_profiles` | ✅ | ✅ | ✅ |
| `get_technicals` | ✅ | ✅ | ✅ |
| `get_institutional_activity` | ✅ | ⚠️ earnings only | ✅ |
| `get_fii_dii_flows` | ❌ | ✅ | ❌ |
| `get_nifty_valuation` | ❌ | ✅ | ❌ |
| `get_scoring_data` | ✅ | ✅ | ✅ |
| `get_us_macro` | ✅ | context | context |

**Not for:** Crypto, forex, real-time trading (data delayed 15-20 min via Yahoo Finance).

`get_us_macro` returns US macro indicators (VIX, yield curve, DXY, S&P 500 trend) — relevant as macro context before analysing any stock globally.

---

## Tools

| Tool | What It Returns | Example |
|------|----------------|---------|
| `resolve_tickers(["Apple", "TSM"])` | Clean Yahoo Finance symbols | `["AAPL", "TSM"]` |
| `get_full_profile("NVDA")` | All metrics in 1 call: price, PE/PEG, ROE, margins, growth, analyst targets, risk, dividends, business description | 9 sections per call |
| `get_batch_profiles(["NVDA", "TSM"])` | Full profiles for up to 20 stocks in 1 MCP call | Replaces many individual profile calls |
| `get_technicals("NVDA")` | RSI, MACD, ADX, Bollinger Bands, MFI, SMA 50/200, stop loss suggestion | Signal + numbers |
| `get_institutional_activity("NVDA")` | Insider trades, institutional holders, mutual fund holders, analyst upgrades/downgrades, earnings calendar | Full picture |
| `get_fii_dii_flows()` | India FII/DII daily buy/sell/net flows + sentiment signal | India macro |
| `get_nifty_valuation()` | Nifty 50 P/E, P/B, dividend yield + valuation zone | India macro |
| `get_scoring_data("NVDA")` | 4-pillar score (V+Q+M+R, 100 total) + deal-breaker checks + BUY/HOLD/SELL verdict | Final answer |
| `get_us_macro()` | VIX, 10Y-3M yield curve, DXY, S&P 500 200DMA + macro sentiment summary | US macro overlay |

---

## Example Session (Full Workflow)

**Step 1 — Resolve tickers:**
```
resolve_tickers(["Bharat Electronics", "NVDA", "SHOP"])
→ ["BEL.NS", "NVDA", "SHOP.TO"]
```

**Step 2 — Get profiles in 1 call:**
```
get_batch_profiles(["BEL.NS", "NVDA", "SHOP.TO"])
→ All PE, ROE, margins, growth, analyst targets for 3 stocks
```

**Step 3 — Technical analysis:**
```
get_technicals("NVDA")
→ RSI=58, MACD bullish, above 50/200 DMA, stop loss: $118
```

**Step 4 — Insider activity:**
```
get_institutional_activity("NVDA")
→ 3 insider buys last quarter, top holder: Vanguard (8.2%)
```

**Step 5 — Final scoring:**
```
get_scoring_data("NVDA")
→ Total: 82/100 (Valuation: 23, Quality: 22, Momentum: 22, Risk: 15)
→ Verdict: BUY
```

**Step 6 — India macro overlay:**
```
get_nifty_valuation() + get_fii_dii_flows()
→ Nifty P/E: 22.5 (Good zone)
→ FII: +$450M (bullish signal)
```

---

## Installation

```bash
pip install uv   # if not already installed
git clone https://github.com/bot8080/Claude-Powerhouse.git
cd Claude-Powerhouse/mcps/market-intelligence
uv sync
```

## Running

```bash
uv run market-intelligence
```

Keep this terminal open. Use tools from Claude Desktop or another terminal.

---

## Claude Desktop Config

Config file location:
- **Mac:** `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows:** `%APPDATA%\Claude\claude_desktop_config.json`
- **Linux:** `~/.config/Claude/claude_desktop_config.json`

Add to the config file:

```json
{
  "mcpServers": {
    "market-intelligence": {
      "command": "uv",
      "args": [
        "run",
        "--directory",
        "/path/to/Claude-Powerhouse/mcps/market-intelligence",
        "market-intelligence"
      ]
    }
  }
}
```

On Windows, use backslash paths (`C:\\path\\to\\...`). Restart Claude Desktop after editing.

---

## Troubleshooting

| Error | Likely Cause | Fix |
|-------|-------------|-----|
| `MCP tool call failed` | Server not running | Start `uv run market-intelligence` in separate terminal |
| `resolve_tickers` empty | Yahoo Finance API down | Wait 2-3 min, retry. Check [status](https://status.yahoo.com/) |
| Missing fields for Indian stocks | Yahoo Finance limitation | Use `get_fii_dii_flows` instead of insider data |
| Rate limit errors | Too many rapid calls | Use `get_batch_profiles` instead of individual calls (built-in 0.3s delay) |
| Incorrect ticker resolution | Missing exchange suffix | Add `.NS` for NSE, `.TO` for TSX, `.BO` for BSE |

---

## Related

| Resource | Purpose |
|----------|---------|
| [All MCP Servers](../README.md) | Browse both servers + install guide |
| [investment-brain](../investment-brain/) | Uses this as data layer for auto-scoring |
| [Root README](../../README.md) | Full repo documentation |
| [Troubleshooting](../../docs/TROUBLESHOOTING.md) | Common errors and fixes |

---

*Part of the [Claude-Powerhouse](../../README.md) suite. Data for informational purposes only — verify before investing.*

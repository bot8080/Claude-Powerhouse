# TECH_SPEC.md — market-intelligence

> Retrospective spec documenting the shipped implementation.

## Project Overview

**Purpose:** MCP server for investment analysis across US, Indian, and Canadian markets.  
**Tech Stack:** Python, FastMCP, yfinance, nsepython, nsetools, ta.  
**Markets Supported:** US (NYSE/NASDAQ), India (NSE/BSE), Canada (TSX), UK (LSE).  
**Tools:** 8 MCP tools total.

---

## Architecture

```
src/market_intelligence/
  server.py      — FastMCP entry point, 8 @mcp.tool registrations
  resolver.py    — Dynamic ticker resolution
  profile.py     — get_full_profile + get_batch_profiles
  technicals.py  — RSI, MACD, ADX, ATR, Bollinger, MFI, OBV, SMA
  india.py       — FII/DII flows, Nifty valuation
  activity.py    — Insider trades, institutional holders
  scoring.py     — 4-pillar score, Piotroski, Short Squeeze
  macro.py       — US macro overlay (VIX, yield curve, DXY)
```

### Dependencies

- `fastmcp` — MCP protocol
- `yfinance` — Yahoo Finance data
- `nsepython` — India FII/DII flows
- `nsetools` — Nifty 50 valuations
- `ta` — Technical indicators
- `pandas` — Data handling

---

## Ticker Suffix Convention

| Market | Suffix | Example |
|--------|-------|---------|
| US NYSE/NASDAQ | (none) | `NVDA` |
| India NSE | `.NS` | `BEL.NS` |
| India BSE | `.BO` | `BEL.BO` |
| Canada TSX | `.TO` | `SHOP.TO` |
| UK LSE | `.L` | `BP.L` |

`resolve_tickers` tool handles dynamic resolution — never manually append suffixes.

---

## Tools

### 1. resolve_tickers

```python
@tool
def resolve_tickers(queries: list[str]) -> dict:
```

**Purpose:** Resolve company names or partial tickers to exact Yahoo Finance symbols.  
**Input:** List of company names or partial tickers.  
**Output:**
```json
{
  "resolved": [{"query": "Apple", "symbol": "AAPL", "name": "Apple Inc."}],
  "ambiguous": [],
  "failed": []
}
```

**Notes:**
- Handles `.NS`, `.TO`, `.BO`, `.L` suffixes automatically
- Never adds "India", "stock", "NSE" to queries

---

### 2. get_full_profile

```python
@tool
def get_full_profile(symbol: str) -> dict:
```

**Purpose:** Comprehensive stock profile in one call.  
**Input:** Clean symbol (e.g., `NVDA`, `BEL.NS`, `SHOP.TO`).  
**Output:** 8 sections:
- **price** — current price, volume, avg_volume, market_cap
- **valuation** — pe_trailing, peg_ratio, pb, ps, ev_ebitda, dividend_yield
- **quality** — roe, roa, debt_to_equity, current_ratio, profit_margin
- **growth** — revenue, earnings, revenue_growth, earnings_growth
- **analyst** — target_mean, target_high, target_low, count, recommendation
- **risk** — beta, short_pct, insider_pct
- **dividends** — dividend_rate, ex_dividend_date, payout_ratio
- **earnings_quality** — fcf_to_ni_ratio, accruals_ratio, rating

---

### 3. get_batch_profiles

```python
@tool
def get_batch_profiles(symbols: list[str]) -> dict:
```

**Purpose:** Full profiles for multiple stocks in one MCP call.  
**Input:** List of symbols (max 20 recommended).  
**Output:**
```json
{
  "profiles": [...],
  "errors": [...],
  "counts": {"total": N, "success": M, "failed": K}
}
```

**Notes:** Uses ThreadPoolExecutor for parallel fetching.

---

### 4. get_technicals

```python
@tool
def get_technicals(symbol: str, period: str = "1y") -> dict:
```

**Purpose:** Technical indicators server-side.  
**Input:** Symbol, period (`1mo`, `3mo`, `6mo`, `1y`, `2y`, `5y`).  
**Output:**
- **trend** — sma_50, sma_200, above_50dma, above_200dma, golden_cross, death_cross
- **momentum** — rsi_14, macd, macd_signal, macd_bullish
- **strength** — adx_14, adx_interpretation
- **volatility** — atr_14, bollinger_upper, bollinger_lower, bollinger_position
- **volume** — obv, obv_trend, mfi_14
- **signals** — overall_signal
- **stop_loss** — suggested stop (price - 2×ATR)

**Notes:** Requires 50+ data points. Returns error if insufficient.

---

### 5. get_institutional_activity

```python
@tool
def get_institutional_activity(symbol: str) -> dict:
```

**Purpose:** Institutional activity for US/Canada stocks.  
**Output:**
- **insider_transactions** — last 5 buys/sells with shares, date, transaction_type
- **top_holders** — holder name, shares, % held, change
- **mutual_fund_holders** — count and top 5
- **analyst_upgrades_downgrades** — firm, rating_old, rating_new, target, date
- **earnings_calendar** — next date, eps_estimate
- **summary** — aggregate sentiment

**Notes:** India uses `get_fii_dii_flows` instead.

---

### 6. get_fii_dii_flows

```python
@tool
def get_fii_dii_flows(days: int = 20) -> dict:
```

**Purpose:** FII/DII daily flow data for India.  
**Input:** Days of history (default 20).  
**Output:**
- **fii** — daily buy, sell, net, cumulative
- **dii** — daily buy, sell, net, cumulative
- **net** — combined FII + DII
- **signal** — "DII absorbing FII selling", etc.

**Notes:** India market only. Data via nsepython.

---

### 7. get_nifty_valuation

```python
@tool
def get_nifty_valuation() -> dict:
```

**Purpose:** Nifty 50 index valuation zones.  
**Output:**
- **pe** — current P/E ratio
- **pb** — price-to-book
- **dividend_yield**
- **year_high**, **year_low**
- **zone** — Excellent (<18) | Good (18-22) | Fair (22-25) | Expensive (25-28) | Bubble (>28)
- **action** — buy/hold/sell recommendation for Nifty

**Notes:** Data via nsetools with yfinance fallback.

---

### 8. get_us_macro

```python
@tool
def get_us_macro() -> dict:
```

**Purpose:** US macro overlay.  
**Output:**
- **vix** — value, change_1d, zone (calm/elevated/crisis), signal
- **yield_curve** — rate_10y, rate_3m, spread, shape (normal/flattening/inverted)
- **dxy** — value, change_30d_pct, trend
- **sp500** — price, sma_200, trend, signal
- **macro_summary** — single-line signal

**Notes:** Call before analyzing US/Canada stocks.

---

## Scoring System

### 4-Pillar Score (100 points)

| Pillar | Max Points | Criteria |
|--------|----------|---------|
| Valuation | 25 | PE + PEG ratio |
| Quality | 25 | ROE + Insider % + moat |
| Momentum | 25 | SMA, RSI, MACD, ADX |
| Risk (Beta) | 25 | Beta 0.8-1.2 = 25pts |

### Modifiers

| Modifier | Adjustment |
|---------|-----------|
| Earnings Quality (excellent) | +3 |
| Earnings Quality (good) | +1 |
| Earnings Quality (warning) | -2 |
| Earnings Quality (poor) | -4 |
| Earnings Quality (red_flag) | -8 |
| Piotroski F-Score ≥8 | +5 |
| Piotroski F-Score ≤4 | -5 |

### Deal-Breakers

- `current_ratio < 0.5` → BLOCK
- `debt_to_equity > 500` → BLOCK
- No revenue + no earnings → BLOCK

### Piotroski F-Score (0-9)

9-point financial health check:
- **Profitability (4pts):** ROA > 0, CFO > 0, ROA improving, accrual quality
- **Leverage (3pts):** Leverage decreasing, current ratio improving, no new shares
- **Efficiency (2pts):** Gross margin improving, asset turnover improving

**Verdict:** 8-9 = Strong | 5-7 = Average | 0-4 = Weak

### Short Squeeze Detector (0-5)

Criteria:
- Short % > 10% → +1
- Short % > 20% → +1 (extra)
- Days-to-cover > 5 → +1
- Relative volume > 1.5x → +1
- RSI in 50-70 → +1

**Verdict:** ≥4 = High | ≥2 = Moderate | <2 = Low

### Final Verdict

| Score | Verdict |
|-------|--------|
| ≥80 | BUY |
| ≥65 | BUY/HOLD |
| ≥50 | HOLD |
| ≥35 | HOLD/SELL |
| <35 | SELL |

---

## Error Handling

- All yfinance fields accessed via `.get()` — never crash on missing keys
- All external calls wrapped in `try/except` — return `{"error": "..."}`
- `time.sleep(0.3)` between yfinance calls in batch mode

---

## Usage

```bash
# Install
uv sync

# Run server
uv run market-analyst-mcp
```

### Claude Desktop Config

```json
{
  "mcpServers": {
    "market-analyst": {
      "command": "uv",
      "args": ["run", "--directory", "path/to/market-intelligence", "market-analyst-mcp"]
    }
  }
}
```

---

## Notes

- `market-intelligence` was shipped before spec discipline was established — this is a retrospective write-up.
- All tools work without API keys — yfinance provides all data for free.
- 8 tools cover the full investment analysis workflow: resolve → profile → technicals → score → verdict.
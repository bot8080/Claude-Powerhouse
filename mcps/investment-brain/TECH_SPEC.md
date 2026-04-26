# TECH_SPEC — investment-brain

Pre-compute financial analysis locally and hand Claude a 20–50 token prompt. Claude formats output only — no research, no scoring, no tool calls during the conversation.

**Data pipeline:** `market-intelligence MCP` → `DataFetcher` → `DealBreaker` → `Scorer` → `PromptBuilder` → Claude

---

## Module Map

| Module | File | Status |
|---|---|---|
| Config & Thresholds | `config.py` | Done |
| MCP Bridge | `mcp_bridge.py` | Done |
| Data Fetcher | `data_fetcher.py` | Done |
| Deal-Breaker | `deal_breaker.py` | Done (3 rules need manual check) |
| Scoring Engine | `scorer.py` | Done |
| Portfolio DB | `portfolio_db.py` | Done |
| Paper Trading | `paper_trading.py` | Done |
| Prompt Builder | `prompt_builder.py` | Done |
| CLI | `main.py` | Done |
| Web App | `web_app.py` | Stub — not yet implemented |

---

## Data Models

### StockData (dict — passed between all modules)
```python
{
  "symbol": str,                   # canonical ticker (e.g. "TSM", "RELIANCE.NS")
  "market": str,                   # "US" | "CA" | "IN"
  "timestamp": str,                # ISO 8601
  "profile": {
    "identity": {
      "name": str,
      "sector": str,
      "industry": str,
      "market_cap": float | None,
      "exchange": str,
    },
    "price": {
      "current": float,
      "fifty_two_week_low": float | None,
      "fifty_two_week_high": float | None,
    },
    "valuation": {
      "pe_trailing": float | None,
      "pe": float | None,          # alias for pe_trailing
      "peg_ratio": float | None,
      "ev_ebitda": float | None,
    },
    "quality": {
      "roe": float | None,         # decimal (0.15 = 15%)
      "operating_margin": float | None,
      "debt_to_equity": float | None,
      "current_ratio": float | None,
      "free_cashflow": float | None,
    },
    "growth": {
      "revenue_growth": float | None,
      "earnings_growth": float | None,
    },
    "dividends": {
      "yield": float | None,       # percent (2.5 = 2.5%)
      "payout_ratio": float | None,
    },
    "risk": {
      "insider_pct": float | None,
      "institution_pct": float | None,
      "short_pct_float": float | None,
      "short_ratio": float | None,
      "overall_risk": float | None,
      "beta": float | None,
    },
    "analyst": {
      "target_mean": float | None,
      "recommendation": str,       # "buy" | "hold" | "sell" | ""
    },
  },
  "technicals": {
    "trend": {
      "above_200dma": bool,
      "above_50dma": bool,
      "golden_cross": bool,
      "death_cross": bool,
    },
    "momentum": {
      "rsi_14": float | None,
      "macd_bullish": bool,
    },
    "volatility": {
      "atr_pct": float | None,
      "bb_pct_b": float | None,
    },
    "strength": {
      "adx_14": float | None,
      "trend_direction": str,      # "bullish" | "bearish" | "neutral"
    },
    "volume": {
      "obv_trend": str,            # "rising" | "falling" | "flat"
      "mfi_14": float | None,
      "volume_vs_avg_20d": float | None,
    },
  },
  "institutional": {
    "insider_transactions": {
      "net_sell": float | None,    # total $ sold in 90d
    },
  },
  # MCP alternate structure (also supported)
  "mcp_scoring": {
    "raw_profile": dict,
    "raw_technicals": dict,
  },
  "blocked": bool,                 # MCP auto-blocked this ticker
  "deal_breakers": list[str],      # MCP-level deal-breaker labels
}
```

### ScoreResult (dict — output of `scorer.score_stock()`)
```python
{
  "fundamentals": {
    "score": int,                  # 0–35
    "max": 35,
    "breakdown": {
      "valuation": int,            # 0–12
      "quality": int,              # 0–13
      "growth": int,               # 0–5
      "dividends": int,            # 0–5
    },
    "raw": dict,                   # raw metric values used in scoring
  },
  "technicals": {
    "score": int,                  # 0–35
    "max": 35,
    "breakdown": {
      "trend": int,                # 0–10
      "momentum": int,             # 0–10
      "volatility": int,           # 0–5
      "strength_volume": int,      # 0–10
    },
    "raw": dict,
  },
  "smart_money": {
    "score": int,                  # 0–30
    "max": 30,
    "breakdown": {
      "insider": int,              # 0–8
      "institutional": int,        # 0–7
      "short_interest": int,       # 0–5
      "analyst": int,              # 0–5
      "governance": int,           # 0–5
    },
    "raw": dict,
    "note": str,                   # "Indian stock: limited institutional data" if applicable
  },
  "total": int,                    # 0–100
  "verdict": str,                  # "BUY" | "BUY-HOLD" | "HOLD" | "WAIT" | "SELL"
  "account": str,                  # "TFSA" | "RRSP" | "Direct MF"
  "stop_loss": float,
  "price_zones": {
    "excellent": float,
    "good": float,
    "fair": float,
    "expensive": float,
    "current": float,
  },
  "moat": str,                     # "wide" | "narrow" | "none"
}
```

### DealBreakerResult (dict — output of `deal_breaker.check_deal_breakers()`)
```python
{
  "blocked": bool,
  "reasons": list[str],            # human-readable block reasons
  "evidence": list[str],           # supporting metric values
  "needs_manual_check": list[str], # rules that can't be auto-checked
}
```

### PortfolioPosition (SQLite row — `portfolio` table)
```python
{
  "ticker": str,                   # PRIMARY KEY
  "name": str,
  "sector": str,
  "market": str,                   # "US" | "CA" | "IN"
  "account": str,                  # "TFSA" | "RRSP" | "Direct MF"
  "price": float,                  # current price
  "cost": float,                   # average cost basis
  "shares": float,
  "fund_score": int,
  "tech_score": int,
  "sm_score": int,
  "verdict": str,
  "flags": str,                    # JSON-encoded list[str]
  "notes": str,
  "stop_loss": float,
  "added": str,                    # ISO date
  "updated": str,
}
```

### PaperTradeResult (dict — output of `PaperTradingEngine.buy()` / `.sell()`)
```python
# Buy
{
  "success": bool,
  "ticker": str,
  "shares": float,
  "entry": float,
  "cost": float,
  "stop_loss": float,
  "warnings": list[str],
  "errors": list[str],
}

# Sell
{
  "success": bool,
  "ticker": str,
  "shares": float,
  "exit": float,
  "pnl_dollar": float,
  "pnl_pct": float,
  "errors": list[str],
}
```

---

## Service Signatures

### config.py
```python
# Constants (not functions — imported directly)
MCP_SERVER_CMD: str
DEFAULT_MARKET: str                    # "US" | "CA" | "IN"
ACCOUNT_MAP: dict[str, str]
FUNDAMENTALS_MAX: int                  # 35
TECHNICALS_MAX: int                    # 35
SMART_MONEY_MAX: int                   # 30
DEAL_BREAKERS: dict[str, float]        # thresholds (see below)
SECTOR_OVERRIDES: dict[str, dict]
PAPER_STARTING_CASH: float             # 50000.0
PAPER_MAX_POSITION_PCT: float          # 10.0
PAPER_MAX_SECTOR_PCT: float            # 30.0
PAPER_MIN_CASH_PCT: float              # 10.0
PAPER_MAX_POSITIONS: int               # 25
```

### data_fetcher.py
```python
class DataFetcher:
    def __enter__(self) -> "DataFetcher": ...
    def __exit__(self, *args): ...
    def resolve_ticker(self, query: str) -> Optional[str]: ...
    def get_stock_data(self, symbol: str, market: str = DEFAULT_MARKET) -> Optional[dict]: ...
    def close(self): ...
```

### deal_breaker.py
```python
def check_deal_breakers(data: dict) -> dict:
    """Returns DealBreakerResult. Never raises."""
```

### scorer.py
```python
def score_stock(data: dict, sector: str = "", moat: str = "none") -> dict:
    """Returns ScoreResult. Never raises."""
```

### portfolio_db.py
```python
class PortfolioDB:
    def get_portfolio(self) -> list[dict]: ...
    def get_watchlist(self) -> list[dict]: ...
    def get_history(self) -> list[dict]: ...
    def add_screener_results(self, results: list[dict], criteria: str) -> None: ...
    def get_all_data(self) -> dict: ...
    def import_all_data(self, data: dict) -> None: ...
```

### paper_trading.py
```python
class PaperTradingEngine:
    def __init__(self, db: PortfolioDB): ...
    def buy(self, ticker: str, shares: float, entry: float, sector: str,
            account: str, stop_loss: Optional[float], target: Optional[float]) -> dict: ...
    def sell(self, ticker: str, shares: float, exit_price: float, reason: str) -> dict: ...
    def get_cash(self) -> float: ...
    def get_total_value(self) -> float: ...
```

### prompt_builder.py
```python
class PromptBuilder:
    SYSTEM_HINT: str

    @classmethod
    def build_single_stock(cls, data: dict, scores: dict,
                           news: list[str] = None, bear_case: str = "",
                           macro: dict = None) -> str: ...

    @classmethod
    def build_batch(cls, items: list[dict]) -> str: ...

    @classmethod
    def build_portfolio_review(cls, holdings: list[dict], sector_alloc: list[dict],
                               flags: list[dict], actions: list[dict],
                               paper_summary: Optional[dict] = None) -> str: ...

    @classmethod
    def build_screener(cls, results: list[dict], criteria: str,
                       universe_size: int) -> str: ...

    @classmethod
    def build_paper_trade_ticket(cls, trade_result: dict,
                                 portfolio_impact: dict) -> str: ...

    @classmethod
    def build_dashboard_json(cls, data: dict, scores: dict) -> str: ...
```

---

## Scoring Rubric

### Fundamentals (35 pts)

| Sub-pillar | Max | Key Metrics | Notes |
|---|---|---|---|
| Valuation | 12 | P/E, PEG, EV/EBITDA | Sector overrides: REIT skips P/E → uses P/FFO |
| Quality | 13 | ROE, Op. Margin, D/E, Current Ratio, FCF | FCF positive = +4pts |
| Growth | 5 | Revenue growth YoY, Earnings growth YoY | >15% rev + earnings > rev = 5pts |
| Dividends | 5 | Yield 2–6%, Payout <60% | REITs: dividend_weight=2.0 |

**Scale reference:**
- P/E green ≤ 20, yellow ≤ 35
- ROE green ≥ 15%, yellow ≥ 8%
- Op. Margin green ≥ 20%, yellow ≥ 10%
- D/E green ≤ 50, yellow ≤ 200, red > 500

### Technicals (35 pts)

| Sub-pillar | Max | Key Metrics |
|---|---|---|
| Trend | 10 | Above 200DMA, above 50DMA, golden/death cross |
| Momentum | 10 | RSI 14, MACD bullish |
| Volatility | 5 | ATR%, Bollinger %B |
| Strength + Volume | 10 | ADX 14, OBV trend, MFI 14 |

**RSI zones:** oversold <30, neutral 45–65, overbought >70

### Smart Money (30 pts)

| Sub-pillar | Max | Key Metrics |
|---|---|---|
| Insider ownership | 8 | >10% = max |
| Institutional ownership | 7 | 60–85% = max (>85% = crowded = 3pts) |
| Short interest | 5 | <3% float = max |
| Analyst consensus | 5 | Buy rating = 5, Hold = 3, Sell = 1 |
| Governance risk | 5 | Overall risk score 1–3 = max |

**India market:** Smart Money defaults to 15/30 neutral (limited public data).

### Verdict Thresholds

| Score | Verdict |
|---|---|
| ≥ 80 | BUY |
| ≥ 65 | BUY-HOLD |
| ≥ 50 | HOLD |
| ≥ 35 | WAIT |
| < 35 | SELL |

**Moat override:** wide moat +2pts fundamentals, no moat -2pts.

---

## Deal-Breaker Rules (any single trigger = BLOCKED)

| # | Rule | Threshold | Auto-check? |
|---|---|---|---|
| 1 | Current ratio too low | < 0.5 | Yes |
| 2 | Debt/Equity extreme | > 500% | Yes |
| 3 | Sustained negative FCF | 2+ years | Partial (current FCF only) |
| 4 | Insider selling > $50M in 90d | $50M net sell | Yes |
| 5 | Promoter pledge (India) | > 50% pledged | Yes (config) |
| 6 | QoE Ratio (CFO/NI) < 0.7 | 2+ years | **Manual check required** |
| 7 | Altman Z-Score < 1.81 | Bankruptcy zone | **Manual check required** |
| 8 | Accounting red flags / auditor qualification | Any | **Manual check required** |
| 9 | Active regulatory action (SEC/SEBI) | Any | **Manual check required** |

Rules 6–9 are flagged in `needs_manual_check` list in the DealBreakerResult — never silently skipped.

---

## Sector Overrides

| Sector | Modification |
|---|---|
| Banks | Skip Altman Z, use CET1, P/E range 8–18 |
| Insurance | Skip Altman Z, use combined ratio, P/E range 10–20 |
| REIT | Skip P/E, use P/FFO, dividend_weight=2.0 |
| Energy | pe_weight=0.5, ev_ebitda_weight=1.5 |
| Commodities | pe_weight=0.5, ev_ebitda_weight=1.5 |

---

## Paper Trading Rules

| Rule | Value |
|---|---|
| Starting cash | $50,000 |
| Max position size | 10% of portfolio |
| Max sector allocation | 30% of portfolio |
| Min cash reserve | 10% at all times |
| Max positions | 25 |
| Default stop loss | 10% below entry |

---

## CLI Commands

```bash
python main.py analyze <TICKER> [--market US|CA|IN]
python main.py screen [--pe-max N] [--roe-min N] [--sector NAME] [TICKER...]
python main.py portfolio
python main.py paper-buy <TICKER> <SHARES> <PRICE> [--sector] [--account] [--stop-loss] [--target]
python main.py paper-sell <TICKER> <SHARES> <PRICE> [--reason]
python main.py watchlist
python main.py history
python main.py export [--file PATH]
python main.py import <FILE>
```

---

## Prompt Output Format

The prompt block Claude receives looks like this:

```
Format this stock data into a Summary Card per my rules.
Rules: Fundamentals 35, Technicals 35, Smart Money 30. Traffic lights.
One verdict. One action line with price and stop loss.
3 news bullets. 3 top risks. Decision log last.
No prose paragraphs. Tables only.

```json
{
  "mode": "format_single",
  "ticker": "TSM",
  "name": "Taiwan Semiconductor",
  "fund_score": 28, "fund_max": 35,
  "tech_score": 24, "tech_max": 35,
  "sm_score": 21, "sm_max": 30,
  "total_score": 73,
  "verdict": "BUY-HOLD",
  "stop_loss": 158.40,
  "price_zones": {"excellent": 149, "good": 162, "fair": 179, "expensive": 196, "current": 172},
  ...
}
```

Total payload to Claude: ~40 tokens (instruction) + ~300 tokens (JSON). Claude outputs ~800 tokens of formatted analysis.

---

## Build Layer Map

| Layer | Name | Modules | Status |
|---|---|---|---|
| 1 | Types & Constants | `config.py` | Done |
| 2 | Services | `mcp_bridge.py`, `data_fetcher.py` | Done |
| 3 | Intelligence | `deal_breaker.py`, `scorer.py` | Done |
| 4 | Storage | `portfolio_db.py`, `paper_trading.py` | Done |
| 5 | Output | `prompt_builder.py` | Done |
| 6 | CLI | `main.py` | Done |
| 7 | Integration & Polish | Wire together, real-data tests, requirements, docs | In progress |

---

## Open Items (Layer 7)

- [ ] `web_app.py` — stub only, not yet implemented
- [ ] `requirements.txt` — verify all deps are pinned
- [ ] End-to-end test with live market data (MCP connected)
- [ ] End-to-end test with yfinance fallback only
- [ ] `MCP_SERVER_CMD` in `config.py` hard-codes a Windows path — make env-var driven
- [ ] Deal-breaker rules 6–9 (manual check) — explore partial automation via market-intelligence scoring data
- [ ] `mcp_wrapper.py` — verify role and remove if redundant
- [ ] Screener universe — replace hardcoded default 10 tickers with configurable list

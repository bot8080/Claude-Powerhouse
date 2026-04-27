# BUILD_STATUS — investment-brain

> Update on `main` only after each PR merges.

---

## Layer 1 — Types & Constants
- [x] `config.py` — thresholds, scoring weights, paper trading rules, sector overrides

## Layer 2 — Services
- [x] `mcp_bridge.py` — JSON-RPC client for market-intelligence MCP
- [x] `data_fetcher.py` — MCP primary + yfinance fallback, US/CA/IN markets

## Layer 3 — Intelligence
- [x] `deal_breaker.py` — 9-rule checker (6 auto, 3 flagged for manual review)
- [x] `scorer.py` — full 35/35/30 rubric, sector overrides, moat adjustment, verdict

## Layer 4 — Storage
- [x] `portfolio_db.py` — SQLite: portfolio, watchlist, screener results, history
- [x] `paper_trading.py` — virtual ledger with position/sector/cash rules

## Layer 5 — Output
- [x] `prompt_builder.py` — 5 prompt modes: single, batch, portfolio, screener, paper trade ticket

## Layer 6 — CLI
- [x] `main.py` — 10 commands: analyze, screen, portfolio, paper-buy, paper-sell, watchlist, history, export, import

## Layer 7 — Integration & Polish
- [x] `MCP_SERVER_CMD` in `config.py` — env-var `MARKET_INTELLIGENCE_CMD` (L7a)
- [x] `requirements.txt` — all deps pinned, `requests` removed (L7a)
- [x] `mcp_wrapper.py` — kept: server-side MCP wrapper (distinct from client-side `mcp_bridge.py`) (L7a)
- [x] End-to-end test: analyze AAPL with MCP live (L7b)
- [x] End-to-end test: analyze AAPL with yfinance fallback only (L7b)
- [x] Screener universe — `SCREENER_UNIVERSE` list in `config.py` (L7a)
- [x] `web_app.py` — FastAPI + HTML dashboard, full API routes (L7a)
- [x] Deal-breaker rules 6–9 — explore partial automation (Altman Z via financials data)
- [x] `README.md` — update install + usage docs (env-var setup, correct folder name, mcp_wrapper) (L7b)
- [x] Combined "Powerhouse Stack" install guide (market-intelligence + investment-brain together) (L7b)
